import time
import esp32
from machine import Pin
from signals import CODES
from neopixel import NeoPixel

OUTPUT_PIN = 1  # GPIO pin to send the signal, active high
BUTTON_PIN = 0 # BOOT button, active low
RGB_LED_PIN = 48 # RGB LED pin

# 1MHz channel resolution (80MHz clock)
rmt = esp32.RMT(0, pin=Pin(1), clock_div=80, idle_level=0)

def send_code(code: tuple):
    rgb_led[0] = (255, 0, 0)  # Set to red
    rgb_led.write()
    rmt.write_pulses(code, data=True)
    rgb_led[0] = (0, 0, 0)  # Set to black
    rgb_led.write()


def send_all_codes(codes: tuple):
    for code in codes:
        send_code(code)
        time.sleep_ms(100)


def main_loop():
    # Initialize the RGB LED
    rgb_led = NeoPixel(Pin(RGB_LED_PIN), 1)
    rgb_led[0] = (0, 255, 0)  # Set to green
    rgb_led.write()

    # Initialize the button
    button = Pin(BUTTON_PIN, Pin.IN, Pin.PULL_UP)

    while True:
        if not button.value():  # Button pressed (active low)
            send_all_codes(CODES)

main_loop()