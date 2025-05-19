#!/usr/bin/env python3
import csv
import os
import argparse

# Configurable settings
TIMING_VARIATION_PCT = 25  # Default allowable variation in timing (percentage)

# Define IR protocols based on irmpSelectMain15Protocols.h from IRMP GitHub repository
# Format: (protocol_name, carrier_frequency, pulse_1, pause_1, pulse_0, pause_0, header_pulse, header_pause, address_bits, command_bits, stop_bit, lsb_first, flags)
# All times in microseconds
IR_PROTOCOLS = [
    # Protocol name, carrier, pulse1, pause1, pulse0, pause0, header_pulse, header_pause, address_bits, command_bits, stop_bit, lsb_first, flags
    ("SIRCS", 40000, 1200, 600, 600, 600, 2400, 600, 12, 12, False, False, None),  # Corrected SIRCS (Sony) values
    ("NEC", 38000, 560, 1690, 560, 560, 9000, 4500, 16, 16, True, True, None),
    ("APPLE", 38000, 560, 1690, 560, 560, 9000, 4500, 8, 16, True, False, None),
    ("SAMSUNG", 38000, 550, 1650, 550, 550, 4500, 4500, 16, 16, True, True, None),
    ("MATSUSHITA", 36000, 400, 1200, 400, 400, 3500, 3500, 12, 12, True, False, None),
    ("KASEIKYO", 37000, 500, 1500, 500, 500, 3400, 1700, 16, 16, True, False, None),
    ("RECS80", 38000, 158, 7432, 158, 4902, 0, 0, 4, 6, False, False, None),
    ("RC5", 36000, 889, 889, 889, 889, 889, 889, 5, 6, False, False, "RC5"),
    ("DENON", 38000, 275, 1900, 275, 775, 0, 0, 5, 10, False, False, None),
    ("RC6", 36000, 444, 444, 444, 444, 2666, 889, 8, 8, True, True, "RC6"),
    ("SAMSUNG32", 38000, 500, 1500, 500, 500, 4500, 4500, 16, 16, True, True, None),
    ("RECS80EXT", 38000, 158, 7432, 158, 4902, 0, 0, 4, 6, False, False, None),
    # ("NUBERT", 38000, 340, 1700, 340, 680, 0, 0, 0, 10, False, False, None),
    # ("BANG_OLUFSEN", 38000, 200, 3125, 200, 9375, 0, 0, 16, 8, False, False, None),
    # ("GRUNDIG", 38000, 528, 528, 528, 1056, 6336, 3168, 0, 8, True, False, None),
    # added protocols
    # ("THOMSON", 36000, 500, 1500, 500, 500, 8000, 2500, 8, 8, True, True, None),
    ("NEC16", 38000, 560, 1690, 560, 560, 9000, 4500, 8, 8, True, True, None),
]


def calculate_variation(measured, reference):
    """Calculate the percentage variation between measured and reference values"""
    if reference == 0:
        return float('inf')  # Avoid division by zero
    return (measured - reference) / reference * 100  # Return signed variation


def match_protocol(pulse_min, pulse_max, pause_min, pause_max, header_pulse=None, header_pause=None):
    """Match timing values to known IR protocols, allowing configurable variation"""
    matches = []
    variations = {}

    for protocol in IR_PROTOCOLS:
        name, _, pulse1, pause1, pulse0, pause0, hp, hpa, _, _, _, _, _ = protocol

        # Check if pulse and pause ranges overlap with protocol values (allowing configured variation)
        variation_factor = TIMING_VARIATION_PCT / 100.0

        pulse1_min = pulse1 * (1 - variation_factor)
        pulse1_max = pulse1 * (1 + variation_factor)
        pause1_min = pause1 * (1 - variation_factor)
        pause1_max = pause1 * (1 + variation_factor)
        pulse0_min = pulse0 * (1 - variation_factor)
        pulse0_max = pulse0 * (1 + variation_factor)
        pause0_min = pause0 * (1 - variation_factor)
        pause0_max = pulse0 * (1 + variation_factor)

        # Check for pulse/pause pattern matches
        pulse_match = False
        pause_match = False

        # Check if our measured pulse range overlaps with either pulse0 or pulse1 range
        if (pulse_min <= pulse1_max and pulse_max >= pulse1_min) or (pulse_min <= pulse0_max and pulse_max >= pulse0_min):
            pulse_match = True

        # Check if our measured pause range overlaps with either pause0 or pause1 range
        if (pause_min <= pause1_max and pause_max >= pause1_min) or (pause_min <= pause0_max and pause_max >= pause0_min):
            pause_match = True

        # If both pulse and pause match, check header if provided
        if pulse_match and pause_match:
            header_match = True
            header_pulse_variation = None
            header_pause_variation = None

            # If header values are provided, check them too
            if header_pulse is not None and header_pause is not None and hp > 0 and hpa > 0:
                hp_min = hp * (1 - variation_factor)
                hp_max = hp * (1 + variation_factor)
                hpa_min = hpa * (1 - variation_factor)
                hpa_max = hpa * (1 + variation_factor)

                if not (header_pulse >= hp_min and header_pulse <= hp_max and
                        header_pause >= hpa_min and header_pause <= hpa_max):
                    header_match = False
                else:
                    # Calculate actual variations for header pulse and pause
                    header_pulse_variation = calculate_variation(
                        header_pulse, hp)
                    header_pause_variation = calculate_variation(
                        header_pause, hpa)

            if header_match:
                matches.append(name)

                # Calculate average variation
                avg_variation = None
                if header_pulse_variation is not None and header_pause_variation is not None:
                    avg_variation = (abs(header_pulse_variation) +
                                     abs(header_pause_variation)) / 2

                variations[name] = {
                    'header_pulse_variation': header_pulse_variation,
                    'header_pause_variation': header_pause_variation,
                    'avg_header_variation': avg_variation
                }

    return matches, variations


def bits_to_hex(bits):
    """Convert a list of bits to a hex string"""
    if not bits:
        return "0x0"
    
    # Pad to multiple of 4 bits
    padded_bits = bits + [0] * (4 - len(bits) % 4 if len(bits) % 4 else 0)
    
    # Convert to hex
    hex_str = "0x"
    for i in range(0, len(padded_bits), 4):
        nibble = 0
        for j in range(4):
            if i + j < len(bits):  # Only use actual bits, not padding
                nibble |= (bits[i + j] << (3 - j))  # MSB first
        hex_str += format(nibble, 'x')
    
    return hex_str

def extract_bits_from_first_repetition(packet):
    """Extract bits from the first repetition based on pause durations"""
    # If no header or timing info, return empty list
    if (packet['header_pulse'] is None or 
        packet['min_pause_us'] == 'N/A' or 
        packet['max_pause_us'] == 'N/A'):
        return []
    
    # Get the original CSV data for this packet
    with open(packet['csv_file'], 'r') as f:
        reader = csv.reader(f)
        rows = list(reader)
    
    # Find the packet boundaries
    start_time = packet['start_time']
    
    # Find the start index in the CSV data
    start_idx = None
    for i, row in enumerate(rows):
        if len(row) >= 2:
            try:
                time = float(row[0])
                if time == start_time:
                    start_idx = i
                    break
            except ValueError:
                continue
    
    if start_idx is None:
        return []  # Can't find the start
    
    # Find the end of the first repetition
    end_idx = len(rows)
    for i in range(start_idx + 1, len(rows)):
        if len(rows[i]) >= 2:
            try:
                time_diff = float(rows[i][0]) - float(rows[i-1][0])
                if time_diff > 0.01:  # Gap > 10ms indicates end of repetition
                    end_idx = i
                    break
            except ValueError:
                continue
    
    # Extract the timing values for the first repetition
    times = []
    states = []
    
    for i in range(start_idx, end_idx):
        if len(rows[i]) >= 2:
            try:
                times.append(float(rows[i][0]))
                states.append(int(rows[i][1]))
            except ValueError:
                continue
    
    # Skip if too short
    if len(times) < 4:
        return []
    
    # Calculate durations
    durations = []
    for i in range(1, len(times)):
        durations.append((times[i] - times[i-1]) * 1_000_000)  # Convert to microseconds
    
    # Skip header if present
    start_idx = 0
    if packet['header_pulse'] is not None:
        start_idx = 2  # Skip header pulse and pause
    
    # Extract bits based on pause durations
    bits = []
    threshold = (packet['min_pause_us'] + packet['max_pause_us']) / 2
    
    for i in range(start_idx, len(durations) - 1, 2):
        if i + 1 < len(durations):
            pause = durations[i + 1]
            if pause > threshold:
                bits.append(1)
            else:
                bits.append(0)
    
    return bits

def analyze_signal(csv_file):
    # Load the CSV file
    times = []
    states = []
    with open(csv_file, 'r') as f:
        reader = csv.reader(f)
        for row in reader:
            if len(row) >= 2:
                if row[0].startswith("Time") or float(row[0]) < 0:
                    continue
                times.append(float(row[0]))
                states.append(int(row[1]))

    # Calculate time differences
    time_diffs = [0]
    for i in range(1, len(times)):
        time_diffs.append(times[i] - times[i-1])

    # Find packet boundaries (gaps > 100ms)
    packet_starts = []
    for i in range(1, len(times)):
        if time_diffs[i] > 0.1 and states[i] == 0:
            packet_starts.append(i)

    # Add the first packet start if it's not already included
    if 0 not in packet_starts and states[0] == 0:
        packet_starts = [0] + packet_starts

    # Process each packet
    results = []
    for i, start_idx in enumerate(packet_starts):
        end_idx = packet_starts[i +
                                1] if i < len(packet_starts)-1 else len(times)

        packet_times = times[start_idx:end_idx]
        packet_states = states[start_idx:end_idx]

        # Skip if packet is too small
        if len(packet_times) < 4:  # Need at least 2 bits (4 records)
            continue

        # Get the start time of the packet
        start_time = packet_times[0]

        # Find repetition boundaries within the packet (gaps > 10ms but < 100ms)
        repetition_starts = [0]  # Always include the start of the packet
        for j in range(1, len(packet_times)):
            if packet_states[j] == 0 and packet_times[j] - packet_times[j-1] > 0.01 and packet_times[j] - packet_times[j-1] < 0.1:
                repetition_starts.append(j)

        # Calculate repetition spacings
        repetition_spacings = []
        for j in range(1, len(repetition_starts)):
            prev_end_idx = repetition_starts[j] - 1
            spacing = packet_times[repetition_starts[j]] - packet_times[prev_end_idx]
            repetition_spacings.append(spacing * 1_000_000)  # Convert to microseconds

        first_header_pulse = None
        first_header_pause = None

        # Process each repetition to extract bits
        all_repetition_bits = []
        for j, rep_start_idx in enumerate(repetition_starts):
            rep_end_idx = repetition_starts[j+1] if j+1 < len(repetition_starts) else len(packet_times)

            rep_times = packet_times[rep_start_idx:rep_end_idx]
            rep_states = packet_states[rep_start_idx:rep_end_idx]

            # Check for header (first pulse and pause if they're significantly longer)
            header_pulse = None
            header_pause = None
            if len(rep_times) >= 4:
                first_pulse = (rep_times[1] - rep_times[0]) * 1_000_000
                first_pause = (rep_times[2] - rep_times[1]) * 1_000_000

                # Look at subsequent pulses to determine if this is a header
                other_pulses = []
                for k in range(2, len(rep_times)-1, 2):
                    if k+1 < len(rep_times) and rep_states[k] == 0 and rep_states[k+1] == 1:
                        other_pulses.append(
                            (rep_times[k+1] - rep_times[k]) * 1_000_000)

                if other_pulses and (first_pulse > 2 * min(other_pulses) or first_pause > 2 * min(other_pulses)):
                    header_pulse = first_pulse
                    header_pause = first_pause

            # Group into bits (each bit is a 0 followed by a 1)
            bits = []
            start_k = 0 if header_pulse is None else 2  # Skip header if present

            for k in range(start_k, len(rep_times)-1, 2):
                if k+1 < len(rep_times) and rep_states[k] == 0 and rep_states[k+1] == 1:
                    pulse_time = rep_times[k+1] - rep_times[k]

                    # Only calculate pause time if we're not at the end of the repetition
                    # and the next state is 0 (start of next bit)
                    if k+2 < len(rep_times) and rep_states[k+2] == 0:
                        pause_time = rep_times[k+2] - rep_times[k+1]
                    else:
                        pause_time = None  # Mark as no pause (end of repetition)

                    bits.append((pulse_time, pause_time))

            all_repetition_bits.append(bits)

            # Store the first header pulse and pause times
            if j == 0 and header_pulse is not None:
                first_header_pulse = header_pulse
                first_header_pause = header_pause

        # For statistics and protocol matching, only use the first repetition
        first_rep_bits = all_repetition_bits[0] if all_repetition_bits else []

        # Bit statistics for the first repetition only
        if first_rep_bits:
            # Only include valid pauses (not None and not 0)
            first_rep_pulses = [bit[0] * 1_000_000 for bit in first_rep_bits]  # Convert to microseconds
            first_rep_pauses = [bit[1] * 1_000_000 for bit in first_rep_bits if bit[1] is not None]  # Convert to microseconds

            min_pulse = min(first_rep_pulses) if first_rep_pulses else 'N/A'
            max_pulse = max(first_rep_pulses) if first_rep_pulses else 'N/A'
            min_pause = min(first_rep_pauses) if first_rep_pauses else 'N/A'
            max_pause = max(first_rep_pauses) if first_rep_pauses else 'N/A'

            # Try to identify protocol using only the first repetition
            possible_protocols = []
            protocol_variations = {}
            if isinstance(min_pulse, float) and isinstance(max_pulse, float) and \
               isinstance(min_pause, float) and isinstance(max_pause, float):
                possible_protocols, protocol_variations = match_protocol(
                    min_pulse, max_pulse, min_pause, max_pause, first_header_pulse, first_header_pause
                )
        else:
            min_pulse = max_pulse = min_pause = max_pause = 'N/A'
            possible_protocols = []
            protocol_variations = {}

        # Calculate total bits across all repetitions (for display only)
        total_bits = sum(len(bits) for bits in all_repetition_bits)

        results.append({
            'csv_file': csv_file,  # Store the CSV filename
            'packet': i+1,
            'start_time': start_time,
            'repetitions': len(repetition_starts),
            'repetition_spacings': repetition_spacings,
            'header_pulse': first_header_pulse,
            'header_pause': first_header_pause,
            'total_bits': total_bits,
            'first_rep_bits': len(first_rep_bits),
            'bits_per_repetition': [len(bits) for bits in all_repetition_bits],
            'min_pulse_us': min_pulse,  # First repetition only
            'max_pulse_us': max_pulse,  # First repetition only
            'min_pause_us': min_pause,  # First repetition only
            'max_pause_us': max_pause,  # First repetition only
            'possible_protocols': possible_protocols,
            'protocol_variations': protocol_variations
        })

    return results


def format_us(value):
    """Format microsecond values without trailing decimal zeros"""
    if isinstance(value, float):
        # Convert to integer if it's a whole number
        if value.is_integer():
            return f"{int(value)}µs"
        else:
            # Otherwise round to 1 decimal place
            return f"{value:.1f}".rstrip('0').rstrip('.') + "µs"
    return f"{value}"


def format_variation(value):
    """Format variation percentage with sign"""
    if value is None:
        return "N/A"
    return f"{value:+.1f}%".replace(".0%", "%")  # Remove trailing zeros


def main():
    # Set up command line argument parsing
    parser = argparse.ArgumentParser(description='Analyze IR signal from CSV file')
    parser.add_argument('csv_file', nargs='?', default='digital.csv', help='CSV file containing IR signal data')
    parser.add_argument('--variation', '-v', type=int, default=25, 
                        help='Allowable timing variation percentage (default: 25%%)')
    parser.add_argument('--unknown', '-u', action='store_true', 
                        help='Show only packets with unidentified protocols')
    parser.add_argument('--output', '-o', type=str, 
                        help='Output file for recognized packets as Python array')
    parser.add_argument('--hex', '-x', action='store_true',
                        help='Print filename and hex representation of first repetition')
    args = parser.parse_args()
    
    # Set the global timing variation percentage
    global TIMING_VARIATION_PCT
    TIMING_VARIATION_PCT = args.variation
    
    # Analyze the signal
    results = analyze_signal(args.csv_file)
    
    # If --hex option is specified, print filename and hex representation
    if args.hex:
        for packet in results:
            if packet['possible_protocols']:
                # Extract bits from the first repetition
                bits = extract_bits_from_first_repetition(packet)
                hex_value = bits_to_hex(bits)
                protocol = packet['possible_protocols'][0]
                print(f"{args.csv_file}\t{hex_value}")
        return
    
    # Print results
    print(f"Found {len(results)} packets in the signal (max allowed variation: {TIMING_VARIATION_PCT}%)")
    print("-" * 100)
    
    # Count identified and unidentified packets
    identified_count = sum(1 for packet in results if packet['possible_protocols'])
    unidentified_count = len(results) - identified_count
    
    # Filter results if --unknown flag is set
    display_results = results
    if args.unknown:
        display_results = [packet for packet in results if not packet['possible_protocols']]
        if not display_results:
            print("No unidentified packets found.")
            return
        print(f"Showing only unidentified packets ({unidentified_count} of {len(results)})")
        print("-" * 100)
    
    for packet in display_results:
        print(f"Packet {packet['packet']} (start time: {packet['start_time']:.6f}s):")
        
        # Print protocol information if available
        if packet['possible_protocols']:
            print(f"  Possible protocols: {', '.join(packet['possible_protocols'])}")
            
            # Format protocol variations for better readability
            formatted_variations = {}
            for protocol, variation in packet['protocol_variations'].items():
                formatted_variations[protocol] = {
                    'header_pulse': format_variation(variation['header_pulse_variation']),
                    'header_pause': format_variation(variation['header_pause_variation']),
                    'avg': format_variation(variation['avg_header_variation'])
                }
            print(f"  Protocol variations: {formatted_variations}")
        else:
            print("  Protocol: UNKNOWN")
        
        # Print header information if available
        if packet['header_pulse'] is not None and packet['header_pause'] is not None:
            print(f"  Header: Pulse = {format_us(packet['header_pulse'])}, "
                  f"Pause = {format_us(packet['header_pause'])}")
        
        # Print repetition information
        if packet['repetitions'] > 1:
            print(f"  Repetitions: {packet['repetitions']}")
            
            # Format repetition spacings without trailing zeros
            spacings_formatted = [format_us(spacing).rstrip('µs') for spacing in packet['repetition_spacings']]
            print(f"  Repetition spacings: {spacings_formatted}µs")
            
            print(f"  Bits per repetition: {packet['bits_per_repetition']}")
        
        print(f"  First repetition bits: {packet['first_rep_bits']}")
        print(f"  Total bits: {packet['total_bits']}")
        print(f"  First repetition timing: Pulse (min={format_us(packet['min_pulse_us'])}, "
              f"max={format_us(packet['max_pulse_us'])}), "
              f"Pause (min={format_us(packet['min_pause_us'])}, "
              f"max={format_us(packet['max_pause_us'])})")
        
        print("-" * 100)
    
    # Output recognized packets to a Python file if requested
    if args.output:
        # Filter for recognized packets
        recognized_packets = [packet for packet in results if packet['possible_protocols']]
        
        if not recognized_packets:
            print(f"No recognized packets to write to {args.output}")
            return
        
        # Extract the raw timing data for each packet
        packet_timings = []
        
        for packet in recognized_packets:
            # Get the original CSV data for this packet
            with open(args.csv_file, 'r') as f:
                reader = csv.reader(f)
                rows = list(reader)
            
            # Find the packet boundaries
            packet_idx = packet['packet']  # 1-based index as shown in output
            start_time = packet['start_time']
            
            # Find the start and end indices in the CSV data
            start_idx = None
            end_idx = None
            
            for i, row in enumerate(rows):
                if len(row) >= 2:
                    try:
                        time = float(row[0])
                        if time == start_time:
                            start_idx = i
                            break
                    except ValueError:
                        continue
            
            if start_idx is None:
                continue  # Skip if we can't find the start
            
            # Find the end of the packet (next packet start or end of file)
            end_idx = len(rows)
            for i in range(start_idx + 1, len(rows)):
                if len(rows[i]) >= 2:
                    try:
                        time_diff = float(rows[i][0]) - float(rows[i-1][0])
                        if time_diff > 0.1 and int(rows[i][1]) == 0:
                            end_idx = i
                            break
                    except ValueError:
                        continue
            
            # Extract the timing values
            packet_times = []
            packet_states = []
            
            for i in range(start_idx, end_idx):
                if len(rows[i]) >= 2:
                    try:
                        packet_times.append(float(rows[i][0]))
                        packet_states.append(int(rows[i][1]))
                    except ValueError:
                        continue
            
            # Convert to microsecond durations
            durations = []
            for i in range(1, len(packet_times)):
                duration = int((packet_times[i] - packet_times[i-1]) * 1_000_000)  # Convert to microseconds
                durations.append(duration)
            
            # Add the protocol name as a comment
            protocol_name = packet['possible_protocols'][0] if packet['possible_protocols'] else "UNKNOWN"
            
            # Store as (packet_idx, start_time, protocol_name, durations)
            packet_timings.append((packet_idx, start_time, protocol_name, durations))
        
        # Write to the output file
        with open(args.output, 'w') as f:
            basename, _ = os.path.splitext(os.path.basename(args.csv_file))
            f.write(f"# Recognized IR packets extracted from CSV file {args.csv_file}\n")
            f.write("# Format: list of (basename, pulse_duration, pause_duration, ...)\n")
            f.write("# All durations in microseconds\n\n")
            f.write("recognized_packets = [\n")

            for packet_idx, start_time, protocol_name, durations in packet_timings:
                f.write(
                    f"    # Packet {packet_idx} (start time: {start_time:.6f}s) - {protocol_name} protocol\n")
                f.write(f"    {tuple([basename] + durations[:-1])},\n")

            f.write("]\n")

        print(
            f"Wrote {len(packet_timings)} recognized packets to {args.output}")


if __name__ == "__main__":
    main()
