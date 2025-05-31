"""
ESP32 MicroPython TV-B-Gone firmware.
Author: Ned Konz (ned@nedkonz.com)
20 May 2025
License: Public Domain
Thanks to Mitch Altman for the TV-B-Gone idea.
"""

import sys
import os
import gc
from time import sleep_ms
from esp32 import RMT, wake_on_ext1, WAKEUP_ANY_HIGH, WAKEUP_ALL_LOW
from machine import Pin, deepsleep, reset_cause
from micropython import const

from config import *
from leds import shine, sleep_leds
from codes import CODES
from capture import capture_all_codes


# Configurable constants
SCALE_FACTOR = const(3)  # Scale factor for pulse durations
CARRIER_FREQ = const(38_000)  # Carrier frequency in Hz
DUTY_CYCLE = const(25)  # Duty cycle as a percentage. 10 to 50% is typical.

IDLE_LEVEL = int(not ACTIVE_LEVEL)  # Inverted active level


output_pin = Pin(OUTPUT_PIN, Pin.OUT, value=IDLE_LEVEL, drive=Pin.DRIVE_3, hold=False)
button_pin = Pin(BUTTON_PIN, Pin.IN, BUTTON_PULL, hold=False)

# 1MHz/SCALE_FACTOR channel resolution (80MHz clock)
rmt = RMT(0, pin=output_pin, clock_div=80 * SCALE_FACTOR, idle_level=IDLE_LEVEL,
          tx_carrier=(CARRIER_FREQ, DUTY_CYCLE, ACTIVE_LEVEL))


def load_captured_codes():
    """Load every captured code from CAPTURE_DIRECTORY and add to CODES"""
    try:
        filenames = os.listdir(CAPTURE_DIRECTORY)
        for filename in filenames:
            print(f"Loading {filename}")
            with open(f"{CAPTURE_DIRECTORY}/{filename}", "r") as f:
                code_text = f.read()
            code = eval(code_text)
            CODES.append(code)
    except OSError:
        return False
    except Exception as e:
        print(f"Error loading captured codes: {e}")
        return False
    return True


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


def sleep():
    """Prepare the system for deep sleep."""
    print("Preparing for deep sleep...")
    shine(BLACK)
    if INPUT_POWER_PIN is not None:
        input_power_pin = Pin(INPUT_POWER_PIN, Pin.OUT, value=0, hold=True)
    sleep_leds()
    button_pin.init(Pin.IN, BUTTON_PULL, hold=True)
    if BUTTON_ACTIVE_LEVEL:
        wake_on_ext1([button_pin], WAKEUP_ANY_HIGH)
    else:
        wake_on_ext1([button_pin], WAKEUP_ALL_LOW)
    deepsleep()  # Deep sleep until button wakes


def wake():
    """Wake up from deep sleep."""
    print(f"Waking up cause={reset_cause()}")
    if INPUT_POWER_PIN is not None:
        input_power_pin = Pin(INPUT_POWER_PIN, Pin.OUT, value=0, hold=False)
    shine(GREEN, 500)


# Main program
# Run from boot.py
try:
    wake()
    load_captured_codes()

    if check_codes():
        print(f"Codes are valid. Ready to output to pin {OUTPUT_PIN}.")
        send_all_codes(CODES)

    if INPUT_PIN is not None:
        print("Hit Ctrl-C to capture codes")
        sleep_ms(3_000)

    sleep()

except KeyboardInterrupt:
    if INPUT_PIN is not None:
        capture_all_codes()
    sleep()

except Exception as e:
    print(f"Error: {e} {sys.exc_info()[0]}")
    shine(RED)
