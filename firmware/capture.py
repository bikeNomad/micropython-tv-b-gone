"""Script to allow IR code capture using a GPIO pin."""
import os
from time import ticks_us, ticks_diff, sleep_ms
from array import array
from machine import Pin
from micropython import const

from config import INPUT_PIN, INPUT_ACTIVE_LEVEL, CAPTURE_DIRECTORY

MAX_GAP_US = const(100_000_000)  # 100ms gap to end capture
MAX_EDGES = const(100)  # Maximum number of edges to capture
MIN_EDGES = const(4)

input_pin = Pin(INPUT_PIN, Pin.IN)
times = None
edge = 0  # Current edge number, index into times
last_time = 0   # Last edge time
done = False  # Flag to indicate if capture is done


def _pin_callback(_):
    """Callback function to handle pin state changes."""
    global edge, last_time, done
    t = ticks_us()
    if edge == 0:
        last_time = t
        times[0] = t
        return
    if ticks_diff(t, last_time) > MAX_GAP_US:
        done = True
        return
    last_time = t
    if edge < MAX_EDGES:
        times[edge] = t
        edge += 1
    else:
        done = True


def capture_ir_code(filename, name="captured"):
    """Capture IR codes from a GPIO pin and save them to a file
    as a Python tuple named `code`

    Args:
        filename (str): The name of the file to save the captured codes.
        name (str, optional): An optional name for the captured code. Defaults to "captured".
    Returns:
        True if capture is successful, False otherwise.
    """
    global edge, last_time, done, times

    input_pin.irq(handler=None)

    # Verify that pin is not at INPUT_ACTIVE_LEVEL
    if input_pin.value() == INPUT_ACTIVE_LEVEL:
        print(
            f"Error: pin {INPUT_PIN} is already at level {INPUT_ACTIVE_LEVEL}")
        return False

    edge = 0
    last_time = 0
    done = False
    times = array("i", (0 for _ in range(MAX_EDGES)))  # Reset the times array
    input_pin.irq(handler=_pin_callback,
                  trigger=Pin.IRQ_RISING | Pin.IRQ_FALLING)

    # wait for first edge
    while edge == 0:
        sleep_ms(100)

    while not done:
        now = ticks_us()
        if last_time != 0 and ticks_diff(now, last_time) > MAX_GAP_US:
            break
        sleep_ms(100)

    input_pin.irq(handler=None)

    # check for overrun
    if edge >= MAX_EDGES:
        print("Error: Capture overrun")
        return False

    # check for minimum edges
    if edge < MIN_EDGES:
        print("Error: Capture too short")
        return False

    # add name to codes
    codes = [name]

    # Convert the times array to a list of pulse durations
    for i in range(1, edge):
        codes.append(times[i] - times[i-1])

    # Save the captured code to a file
    try:
        with open(filename, 'w') as f:
            f.write(f"# {name}\ncode = ")
            f.write(str(tuple(codes)))
            print(f"Captured code saved to {filename}")
    except OSError as e:
        print(f"Error writing to file: {e}")
        return False

    return True


def capture_all_codes():
    """
    Loop:
        Prompt the user for the next capture name
        Quit upon q or Ctrl-C
        Capture the code and save it to a file in the CAPTURE_DIRECTORY.
    """
    try:
        os.mkdir(CAPTURE_DIRECTORY)
    except OSError:
        pass

    existing_files = [f for f in os.listdir(CAPTURE_DIRECTORY) if f.endswith(".py")]
    num_files = len(existing_files)

    # Capture codes until the user interrupts
    try:
        while True:
            # prompt for name
            name = input("Enter a name for the next capture (q to quit): ")
            name = name.strip()
            if name.lower() == "q":
                break
            if name == "":
                name = f"code_{num_files}"
            fname = f"{name}.py"
            # check for duplicates
            if fname in existing_files:
                print(
                    f"Error: file {fname} already exists. Please choose a different name.")
                continue
            filename = f"{CAPTURE_DIRECTORY}/{fname}"
            if capture_ir_code(filename, name):
                print(f"Captured {repr(name)} to {filename}")
                num_files += 1
                existing_files.append(fname)
    except KeyboardInterrupt:
        print("Capture interrupted by user.")

    print(f"Files in {CAPTURE_DIRECTORY}: {existing_files}")

capture_all_codes()
