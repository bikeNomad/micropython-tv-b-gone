"""
Pin definitions for XIAO ESP32-C6 module from Seeed Studio.
"""
from machine import Pin
from time import sleep_ms

# Pins on board edge
PIN_D0 = 0
PIN_D1 = 1
PIN_D2 = 2
PIN_D3 = 21
PIN_D4 = 22
PIN_D5 = 23
PIN_D6 = 16
PIN_D7 = 17
PIN_D8 = 19
PIN_D9 = 20
PIN_D10 = 18

# Other pins
PIN_BOOT = 9 # Boot switch, active low (pulled up by HW)
PIN_RF_SWITCH = 14 # pull high for UFL output
PIN_RF_SWITCH_POWER = 3 # pull low to turn on RF switch
PIN_USER_LED = 15 # pull low to turn on LED
USER_LED_ACTIVE_LEVEL = 0

RF_SWITCH_PIN = Pin(PIN_RF_SWITCH, Pin.IN) # internal (pulled low by default)
RF_SWITCH_POWER_PIN = Pin(PIN_RF_SWITCH_POWER, Pin.IN) # off (pulled high)

def enable_wifi_antenna(enabled: bool = True, external: bool = False):
    if enabled:
        RF_SWITCH_POWER_PIN.init(mode=Pin.OUT, value=0)
        sleep_ms(100)
        RF_SWITCH_PIN.init(mode=Pin.OUT, value=external)
    else:
        RF_SWITCH_POWER_PIN.init(mode=Pin.IN, pull=None)
        RF_SWITCH_PIN.init(mode=Pin.IN, pull=None)

        