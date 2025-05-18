import csv


def analyze_signal(csv_file):
    # Load the CSV file
    times = []
    states = []
    with open(csv_file, 'r') as f:
        reader = csv.reader(f)
        for row in reader:
            if len(row) >= 2:
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
    for i in range(len(packet_starts)):
        start_idx = packet_starts[i]
        end_idx = packet_starts[i+1] if i < len(packet_starts)-1 else len(times)
        
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
        
        # Process each repetition to extract bits
        all_repetition_bits = []
        for j in range(len(repetition_starts)):
            rep_start_idx = repetition_starts[j]
            rep_end_idx = repetition_starts[j+1] if j+1 < len(repetition_starts) else len(packet_times)
            
            rep_times = packet_times[rep_start_idx:rep_end_idx]
            rep_states = packet_states[rep_start_idx:rep_end_idx]
            
            # Group into bits (each bit is a 0 followed by a 1)
            bits = []
            for k in range(0, len(rep_times)-1, 2):
                if k+1 < len(rep_times) and rep_states[k] == 0 and rep_states[k+1] == 1:
                    pulse_time = rep_times[k+1] - rep_times[k]
                    
                    # Only calculate pause time if we're not at the end of the repetition
                    # and the next state is 0 (start of next bit)
                    if k+2 < len(rep_times) and rep_states[k+2] == 0:
                        pause_time = rep_times[k+2] - rep_times[k+1]
                    else:
                        pause_time = None  # Mark as no pause (end of repetition)
                    
                    bits.append((pulse_time, pulse_time))
            
            all_repetition_bits.append(bits)
        
        # Combine all bits from all repetitions for overall statistics
        all_bits = []
        for rep_bits in all_repetition_bits:
            all_bits.extend(rep_bits)
        
        if not all_bits:
            continue
            
        # First bit timing
        first_bit_pulse = all_bits[0][0] * 1_000_000  # Convert to microseconds
        first_bit_pause = all_bits[0][1] * 1_000_000 if all_bits[0][1] is not None else 'N/A'  # Convert to microseconds
        
        # Other bits statistics
        other_bits = all_bits[1:]
        if other_bits:
            # Only include valid pauses (not None and not 0)
            other_pulses = [bit[0] * 1_000_000 for bit in other_bits]  # Convert to microseconds
            other_pauses = [bit[1] * 1_000_000 for bit in other_bits if bit[1] is not None]  # Convert to microseconds
            
            min_pulse = min(other_pulses) if other_pulses else 'N/A'
            max_pulse = max(other_pulses) if other_pulses else 'N/A'
            min_pause = min(other_pauses) if other_pauses else 'N/A'
            max_pause = max(other_pauses) if other_pauses else 'N/A'
        else:
            min_pulse = max_pulse = min_pause = max_pause = 'N/A'
        
        results.append({
            'packet': i+1,
            'start_time': start_time,
            'repetitions': len(repetition_starts),
            'repetition_spacings': repetition_spacings,
            'first_bit_pulse_us': first_bit_pulse,
            'first_bit_pause_us': first_bit_pause,
            'total_bits': len(all_bits),
            'bits_per_repetition': [len(bits) for bits in all_repetition_bits],
            'min_other_pulse_us': min_pulse,
            'max_other_pulse_us': max_pulse,
            'min_other_pause_us': min_pause,
            'max_other_pause_us': max_pause
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


def main():
    csv_file = 'digital.csv'
    results = analyze_signal(csv_file)
    
    print(f"Found {len(results)} packets in the signal")
    print("-" * 100)
    
    for packet in results:
        print(f"Packet {packet['packet']} (start time: {packet['start_time']:.6f}s):")
        
        # Print repetition information
        if packet['repetitions'] > 1:
            print(f"  Repetitions: {packet['repetitions']}")
            
            # Format repetition spacings without trailing zeros
            spacings_formatted = [format_us(spacing).rstrip('µs') for spacing in packet['repetition_spacings']]
            print(f"  Repetition spacings: {spacings_formatted}µs")
            
            print(f"  Bits per repetition: {packet['bits_per_repetition']}")
        
        print(f"  First bit: Pulse = {format_us(packet['first_bit_pulse_us'])}, "
              f"Pause = {format_us(packet['first_bit_pause_us'])}")
        
        print(f"  Total bits: {packet['total_bits']}")
        
        print(f"  Other bits: Pulse (min={format_us(packet['min_other_pulse_us'])}, "
              f"max={format_us(packet['max_other_pulse_us'])}), "
              f"Pause (min={format_us(packet['min_other_pause_us'])}, "
              f"max={format_us(packet['max_other_pause_us'])})")
        
        print("-" * 100)


if __name__ == "__main__":
    main()
