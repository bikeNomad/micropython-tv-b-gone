from time import sleep_us
from esp32 import RMT
from machine import Pin
from signals import CODES
from neopixel import NeoPixel
from micropython import const
import gc

OUTPUT_PIN = 1  # GPIO pin to send the signal, active high
BUTTON_PIN = 0  # BOOT button, active low
RGB_LED_PIN = 48  # RGB LED pin

BLUE = const((0, 0, 255))
BLACK = const((0, 0, 0))
RED = const((255, 0, 0))
SCALE_FACTOR = const(3)
CARRIER_FREQ = const(38000)
DUTY_CYCLE = const(25)

IDLE_LEVEL = const(0)
ACTIVE_LEVEL = const(1)

# 1MHz channel resolution (80MHz clock)
rmt = RMT(0, pin=Pin(1), clock_div=80 * SCALE_FACTOR, idle_level=IDLE_LEVEL,
          tx_carrier=(CARRIER_FREQ, DUTY_CYCLE, ACTIVE_LEVEL))
rgb_led = NeoPixel(Pin(RGB_LED_PIN), 1)


def shine(color: tuple):
    rgb_led[0] = color
    rgb_led.write()


def send_code(code: tuple):
    shine(BLUE)
    # scale each pulse by SCALE_FACTOR
    scaled = [round(p / SCALE_FACTOR) for p in code]
    if len(scaled) % 2 == 1:
        scaled.append(RMT.PULSE_MAX)
    rmt.write_pulses(scaled, True)
    gc.collect()
    shine(BLACK)
    return sum(scaled) * SCALE_FACTOR


def send_all_codes(codes: tuple):
    print(f"Sending {len(codes)} codes...")
    duration = 0
    for code in codes:
        duration += send_code(code)
    print(f"Total duration: {duration / 1_000_000} s")


def main_loop():
    # Initialize the button
    button = Pin(BUTTON_PIN, Pin.IN, Pin.PULL_UP)

    while True:
        if not button.value():  # Button pressed (active low)
            send_all_codes(CODES)


# check all the numbers in CODES to ensure that none are > RMT.PULSE_MAX
def check_codes():
    max_pulse = 0
    max_period = RMT.PULSE_MAX * SCALE_FACTOR
    retval = True
    for i, code in enumerate(CODES):
        for pulse in code:
            max_pulse = max(pulse, max_pulse)
            if pulse > max_period:
                print(
                    f"code {i}: Pulse {pulse} exceeds {max_period}")
                retval = False
    print(f"Max pulse: {max_pulse}, max delay = {max_period}")
    return retval

try:
    if check_codes():
        print("Codes are valid")
        main_loop()
except Exception as e:
    print(f"Error: {e}")
    shine(RED)
