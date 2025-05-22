from machine import Pin, deepsleep
from esp32 import wake_on_ext1, WAKEUP_ALL_LOW 
from time import sleep_ms

BUTTON_PIN = 2  # must be RTC-capable pin.
LED_PIN = 15 # XIAO ESP32-C6 User LED pin, active LOW

sleep_ms(3000) # wait for button to be released

button = Pin(BUTTON_PIN, Pin.IN, Pin.PULL_UP)
led = Pin(LED_PIN, Pin.OUT, value=1)  # active low

def blink_led(period_ms):
    led.value(0)  # turn on LED
    sleep_ms(period_ms)
    led.value(1)  # turn off LED

blink_led(500)

if button.value() == 1:
    wake_on_ext1([button], WAKEUP_ALL_LOW)
    deepsleep()
else:
    print("Button is pressed. Not going to sleep.")
    while True:
        sleep_ms(100)
        blink_led(100)