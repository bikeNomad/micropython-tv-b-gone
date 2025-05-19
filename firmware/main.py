"""
ESP32 MicroPython TV-B-Gone firmware.
Author: Ned Konz (ned@nedkonz.com)
19 May 2025
License: Public Domain
Thanks to Mitch Altman for the TV-B-Gone idea.
"""

import sys
import gc
import time
from esp32 import RMT
from machine import Pin
from codes import CODES
from neopixel import NeoPixel
from micropython import const


# Configurable constants
# RMT output pin configuration
OUTPUT_PIN = const(1)  # GPIO pin to send the signal, active high
IDLE_LEVEL = const(0)
ACTIVE_LEVEL = const(1)

# Button configuration
BUTTON_PIN = const(0)  # BOOT button, active low
BUTTON_ACTIVE_LEVEL = const(0)  # Active low (0V)
BUTTON_PULL = Pin.PULL_UP

# optional RGB LED configuration
RGB_LED_PIN = const(48)  # RGB LED pin (optional, None to disable)

# RGB LED colors
BLACK = const((0, 0, 0))
BLUE = const((0, 0, 255))
RED = const((255, 0, 0))
GREEN = const((0, 255, 0))

SCALE_FACTOR = const(3)  # Scale factor for pulse durations
CARRIER_FREQ = const(38000)  # Carrier frequency in Hz
DUTY_CYCLE = const(25)  # Duty cycle as a percentage. 10 to 50% is typical.


# 1MHz channel resolution (80MHz clock)
rmt = RMT(0, pin=Pin(1), clock_div=80 * SCALE_FACTOR, idle_level=IDLE_LEVEL,
          tx_carrier=(CARRIER_FREQ, DUTY_CYCLE, ACTIVE_LEVEL))

rgb_led = NeoPixel(Pin(RGB_LED_PIN), 1) if RGB_LED_PIN is not None else None


def shine(color: tuple, period: int = 0):
    """Set the RGB LED to a specified color.
    Args:
        color (tuple): An RGB color tuple representing the LED color to display.
                       Each color component should be in the range 0-255.
        period (int): Optional. The duration in milliseconds to display the color.
    """
    if rgb_led is not None:
        rgb_led[0] = color
        rgb_led.write()
        if period > 0:
            time.sleep_ms(period)
            rgb_led[0] = BLACK
            rgb_led.write()


def send_code(code: tuple):
    """Send a single sequence of pulses to the RMT peripheral.
    Args:
        code (tuple): A tuple containing the pulse durations in microseconds.
                      The first element can be a string representing the name of the code.
    Returns:
        int: The total duration of the code in microseconds.
    """
    name = "unknown"
    if isinstance(code[0], str):
        name = code[0]
        code = code[1:]
    print(f"Sending {name} code")
    shine(BLUE, 50)
    # scale each pulse by SCALE_FACTOR
    scaled = [round(p / SCALE_FACTOR) for p in code]
    if len(scaled) % 2 == 1:
        scaled.append(RMT.PULSE_MAX)
    rmt.write_pulses(scaled, True)
    gc.collect()
    return sum(scaled) * SCALE_FACTOR


def send_all_codes(codes: tuple):
    """Send a sequence of codes to the RMT peripheral.
    Args:
        codes (tuple): A tuple containing tuples of pulse durations in microseconds.
                       Each tuple can optionally start with a string representing the name of the code.
    """
    print(f"Sending {len(codes)} codes...")
    duration = 0
    for code in codes:
        duration += send_code(code)
    print(f"Total duration: {duration / 1_000_000} s")


def main_loop():
    """Main loop. Waits for a button press to send all codes."""
    button = Pin(BUTTON_PIN, Pin.IN, BUTTON_PULL)

    while True:
        if button.value() == BUTTON_ACTIVE_LEVEL:  # Button pressed (active low)
            send_all_codes(CODES)


def check_codes():
    """Check all the pulse durations in CODES to ensure
    that none are > RMT.PULSE_MAX when scaled by SCALE_FACTOR.
    Returns:
        bool: True if all codes are valid, False otherwise.
    """
    max_pulse = 0
    max_period = RMT.PULSE_MAX * SCALE_FACTOR
    retval = True
    for i, code in enumerate(CODES):
        name = f"{i}"
        if isinstance(code[0], str):
            name = code[0]
            code = code[1:]
        for pulse in code:
            max_pulse = max(pulse, max_pulse)
            if pulse > max_period:
                print(f"code {name}: Pulse {pulse} exceeds {max_period}")
                retval = False
    print(f"Max pulse: {max_pulse}, max delay = {max_period}")
    return retval


# Run from boot.py
try:
    shine(GREEN, 500)

    if check_codes():
        print(f"Codes are valid. Ready to output to pin {OUTPUT_PIN}.")
        main_loop()
except Exception as e:
    print(f"Error: {e} {sys.exc_info()[0]}")
    shine(RED)
