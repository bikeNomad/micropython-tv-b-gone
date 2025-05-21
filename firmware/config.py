import sys
from machine import Pin

# Configurable constants
# RMT output pin configuration
OUTPUT_PIN = 1  # GPIO pin to send the signal, active high
ACTIVE_LEVEL = 1    # OUTPUT_PIN state to turn on the LED

# Button configuration
BUTTON_PIN = 0  # BOOT button, active low (pulled up by hardware)
BUTTON_ACTIVE_LEVEL = 0  # Active low (0V)
BUTTON_PULL = None  # or Pin.PULL_UP or Pin.PULL_DOWN depending on your hardware

# optional RGB LED configuration
RGB_LED_PIN = None  # RGB LED pin (optional, None to disable)
RGB_LED_POWER_PIN = None  # RGB LED power pin (optional, None to disable)

# optional monochrome LED configuration
USER_LED_PIN = None  # Monochrome User LED pin (optional, None to disable)
USER_LED_ACTIVE_LEVEL = 0  # Active low (0V)

# RGB LED colors
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)

# Directory to store .py files containing captured IR codes
CAPTURE_DIRECTORY = "/captured"

# optional input pin configuration for capturing IR signals
INPUT_PIN = None  # GPIO pin for input (optional, None to disable)
INPUT_ACTIVE_LEVEL = 0  # Active low (0V)
# GPIO pin to power the IR receiver (optional, None to disable)
INPUT_POWER_PIN = None

# Change USE_XIAO_ESP32C6 to False if you have an ESP32-C6 that is not a XIAO ESP32-C6
USE_XIAO_ESP32C6 = True
try:
    if USE_XIAO_ESP32C6 and 'ESP32C6' in sys.implementation._machine:
        print("Configuring for XIAO ESP32-C6")
        from xiao_esp32c6 import PIN_D0, PIN_D1, PIN_D2, PIN_USER_LED, PIN_D3
        OUTPUT_PIN = PIN_D0
        INPUT_PIN = PIN_D1
        BUTTON_PIN = PIN_D2
        BUTTON_PULL = Pin.PULL_UP
        INPUT_POWER_PIN = PIN_D3
        USER_LED_PIN = PIN_USER_LED
        USER_LED_ACTIVE_LEVEL = 0
except Exception as e:
    sys.print_exception(e)

# Configuration for Unexpected Maker TinyS3
# Change USE_UM_TINYS3 to False if you have a TinyS3 but don't want these settings.
USE_UM_TINYS3 = True
try:
    if USE_UM_TINYS3 and 'TinyS3' in sys.implementation._machine:
        print("Configuring for UM TinyS3")
        from tinys3 import RGB_DATA, RGB_PWR
        OUTPUT_PIN = 1
        INPUT_PIN = 2
        BUTTON_PIN = 3
        BUTTON_PULL = Pin.PULL_UP
        INPUT_POWER_PIN = 4
        RGB_LED_PIN = RGB_DATA
        RGB_LED_POWER_PIN = RGB_PWR
except Exception as e:
    sys.print_exception(e)
