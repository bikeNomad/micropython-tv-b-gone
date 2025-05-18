#!/usr/bin/env python3
from saleae import automation
import os
import os.path

IN_CHANNEL=2
EXPORT_NAME = "digital.csv"

def capture_ir_data(filename):
    # Connect to the running Logic 2 Application on port `10430`.
    # Alternatively you can use automation.Manager.launch() to launch a new Logic 2 process - see
    # the API documentation for more details.
    # Using the `with` statement will automatically call manager.close() when exiting the scope. If you
    # want to use `automation.Manager` outside of a `with` block, you will need to call `manager.close()` manually.
    with automation.Manager.connect(port=10430) as manager:

        # Configure the capturing device to record on digital channels 0, 1, 2, and 3,
        # with a sampling rate of 10 MSa/s, and a logic level of 3.3V.
        # The settings chosen here will depend on your device's capabilities and what
        # you can configure in the Logic 2 UI.
        device_configuration = automation.LogicDeviceConfiguration(
            enabled_digital_channels=[IN_CHANNEL],
            digital_sample_rate=1_000_000,
            digital_threshold_volts=3.3,
        )

        capture_configuration = automation.CaptureConfiguration(
            capture_mode=automation.DigitalTriggerCaptureMode(
                trigger_type=automation.DigitalTriggerType.FALLING,
                trigger_channel_index=IN_CHANNEL,
                after_trigger_seconds=0.5
            )
        )

        # Start a capture - the capture will be automatically closed when leaving the `with` block
        with manager.start_capture(
                device_configuration=device_configuration,
                capture_configuration=capture_configuration) as capture:

            # Wait until the capture has finished
            capture.wait()

            output_dir = os.path.join(os.getcwd(), 'captures')
            os.makedirs(output_dir, exist_ok=True)

            # Export raw digital data to EXPORT_NAME
            capture.export_raw_data_csv(directory=output_dir, digital_channels=[IN_CHANNEL])
            # rename EXPORT_NAME to the command line arguments
            os.rename(os.path.join(output_dir, EXPORT_NAME), os.path.join(output_dir, filename + ".csv"))

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Capture IR data using Saleae Logic 2.")
    parser.add_argument("filename", type=str, help="The name of the file to save the captured data as.")
    args = parser.parse_args()

    capture_ir_data(args.filename)