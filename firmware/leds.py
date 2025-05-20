"""
LED control for an optional RGB LED and/or an optional monochrome LED.
"""

from time import sleep_ms
from neopixel import NeoPixel
from machine import Pin

from config import RGB_LED_PIN, USER_LED_PIN, USER_LED_ACTIVE_LEVEL, BLACK

rgb_led = NeoPixel(Pin(RGB_LED_PIN), 1) if RGB_LED_PIN is not None else None
user_led = Pin(USER_LED_PIN, Pin.OUT,
               level=not USER_LED_ACTIVE_LEVEL) if USER_LED_PIN is not None else None


def shine(color: tuple, period: int = 0):
    """
    Set the RGB LED to a specified color.
    And/or flash the USER_LED if color is not BLACK.
    Args:
        color (tuple): An RGB color tuple representing the LED color to display.
                       Each color component should be in the range 0-255.
        period (int): Optional. The duration in milliseconds to display the color.
    """
    if rgb_led is not None:
        rgb_led[0] = color
        rgb_led.write()

    if user_led is not None:
        if color != BLACK:
            user_led.value(USER_LED_ACTIVE_LEVEL)
        else:
            user_led.value(not USER_LED_ACTIVE_LEVEL)

    if period > 0:
        sleep_ms(period)

        if user_led is not None:
            user_led.value(not USER_LED_ACTIVE_LEVEL)

        if rgb_led is not None:
            rgb_led[0] = BLACK
            rgb_led.write()
