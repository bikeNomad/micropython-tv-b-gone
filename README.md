# MicroPython TV-B-Gone clone
## Introduction
This is a MicroPython implementation of the TV-B-Gone project.
The TV-B-Gone (by Mitch Altman) is a universal remote control that can turn off most televisions.
Unfortunately, the existing implementations (for the ATTiny microcontrollers) have very outdated code databases and don't work with many modern TVs.
This project is designed to work with the ESP32 microcontroller and a recent version of MicroPython (I used v1.25.0).
I wanted to use the ESP32 because its RMT peripheral allows for simple and well controlled modulated IR signal generation.
## Workflow
I didn't want to spend lots of time editing codes, so I bought a [very cheap IR universal remote control from Amazon](https://www.amazon.com/dp/B0D6GFNFJY).
I asked Google Gemini to tell me the top 10 brands of modern TVs and collected the power-toggle codes for every code given in my universal remote manual for the 10 brands, using an IR receiver module connected to my Saleae Logic 8 logic analyzer.
Saleae's automation API and Python helped me automate the collection process.
Then I had Cody write a Python script that could read the CSV files produced by the Saleae logic analyzer and convert them into a format that could be used by the ESP32. Along the way I also had it identify the IR protocols, and also produce hex representations of the codes for recognized protocols, to allow me to eliminate duplicate codes.
## TV Brands Supported
The following brands are supported:
  - Samsung
  - LG
  - TCL
  - Hisense
  - Sony
  - Vizio
  - Panasonic
  - Philips
  - Sharp
  - Toshiba
## Code structure
The representation of each of the codes in `firmware/codes.py` is a tuple with periods in microseconds. Each code may have an optional name as a string as the first member of the tuple.
I used the universal remote's own code numbers as the names.
This should make it easy to collect your own codes (see Peter Hinch's [MicroPython IR library](https://github.com/peterhinch/micropython_ir/tree/master)
## Configuration
See the top of `firmware/main.py` for the configuration options.
### Circuit-related configuration
  - `OUTPUT_PIN` is the GPIO pin used for the IR LED.
  - `IDLE_LEVEL` is the idle level of the output pin. This should be 0 (low) for most circuits, but some circuits may require a high idle level.
  - `ACTIVE_LEVEL` should be the inverse of `IDLE_LEVEL`. This is the level that the output pin will be set to when the IR LED is active.
  - `BUTTON_PIN` is the GPIO pin used for the button. I used GPIO 0, because it was connected to the `BOOT` button on my development board.
  - `BUTTON_ACTIVE_LEVEL` is the level that the button pin will be set to when the button is pressed. I used 0 (low) for my circuit, but some circuits may require a high level.
  - `BUTTON_PULL` is the pull-up or pull-down setting to use for the button pin. I used `Pin.PULL_UP` for my circuit, but some circuits may require a different pull-up or pull-down resistor. If you don't need to pull this pin, use `Pin.PULL_NONE`.
  - `RGB_LED_PIN` is the GPIO pin used for the RGB LED. I used GPIO 48, because it was connected to the onboard RGB LED on my development board. If you don't have an RGB LED, you can set this to `None` to disable the RGB LED.
  - `DUTY_CYCLE` is the duty cycle to use for the IR LED.
  This is the percentage of time that the IR LED will be on during the 38kHz pulses.
  I used 25% for my circuit, but numbers from 10% to 50% should work. 25% is a good starting point.
## Transmitter Circuit design
You will need a 940nm IR LED and a simple one-transistor driver circuit to drive the LED.
See Peter Hinch's explanation [here](https://github.com/peterhinch/micropython_ir/blob/master/TRANSMITTER.md).
Although Peter's examples show an NPN BJT transistor, 
I used a VN2225 N-channel MOSFET transistor because that's what I had on hand, but any logic-level N-channel MOSFET should work.
The IR LED's cathode is connected to the drain of the transistor,
and its anode is connected in series with a current limiting resistor whose other end is connected to +5V.
The MOSFET's source is connected to ground, and its gate is connected to the GPIO pin used for the IR LED.
The value of the current limiting resistor depends on the power supply voltage and the IR LED's maximum pulse current rating.
I used a high-power IR LED with a maximum pulse current rating of 1A (SFH4248Z), so I used a 33 ohm resistor to produce 100mA current pulses.
## Files in this repository
  - `analyze_signal.py`: Analyzes a recorded IR signal and prints the results.
  - `capture_saleae.py`: Captures IR signals using Saleae Logic 2 and saves the data to a CSV file.
  - `firmware/codes.py`: IR codes for the ESP32.
  - `firmware/main.py`: Main firmware file.
  - `good/`: CSV files of good (non-duplicated) IR codes captured using the Saleae Logic.
  - `good_py/`: Good IR codes captured using the Saleae Logic, converted to Python format.
  - `prompt_captures.py`: A script to capture IR codes using the Saleae and save them to CSV files.
  - `README.md`: This file.
