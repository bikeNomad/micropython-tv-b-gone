from machine import Pin

# Configurable constants
# RMT output pin configuration
OUTPUT_PIN = 1  # GPIO pin to send the signal, active high
ACTIVE_LEVEL = 1    # OUTPUT_PIN state to turn on the LED

# Button configuration
BUTTON_PIN = 0  # BOOT button, active low (pulled up by hardware)
BUTTON_ACTIVE_LEVEL = 0  # Active low (0V)
BUTTON_PULL = None # or Pin.PULL_UP or Pin.PULL_DOWN depending on your hardware

# optional RGB LED configuration
RGB_LED_PIN = 48  # RGB LED pin (optional, None to disable)

# RGB LED colors
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)

CAPTURE_DIRECTORY = "/captured"

# optional input pin configuration for capturing IR signals
INPUT_PIN = 2  # GPIO pin for input (optional, None to disable)
INPUT_ACTIVE_LEVEL = 0  # Active low (0V)
