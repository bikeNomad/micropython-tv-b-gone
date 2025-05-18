import csv

# Define all IR protocols from IRMP GitHub repository
# Format: (protocol_name, carrier_frequency, pulse_1, pause_1, pulse_0, pause_0, header_pulse, header_pause, address_bits, command_bits, stop_bit, lsb_first, flags)
# All times in microseconds
IR_PROTOCOLS = [
    # Protocol name, carrier, pulse1, pause1, pulse0, pause0, header_pulse, header_pause, address_bits, command_bits, stop_bit, lsb_first, flags
    ("SIRCS", 40000, 1200, 600, 600, 600, 2400, 600, 12, 12, False, False, None),
    ("NEC", 38000, 560, 1690, 560, 560, 9000, 4500, 16, 16, True, True, None),
    ("SAMSUNG", 38000, 550, 1650, 550, 550, 4500, 4500, 16, 16, True, True, None),
    ("MATSUSHITA", 36000, 400, 1200, 400, 400, 3500, 3500, 12, 12, True, False, None),
    ("KASEIKYO", 37000, 500, 1500, 500, 500, 3400, 1700, 16, 16, True, False, None),
    ("RECS80", 38000, 158, 7432, 158, 4902, 0, 0, 4, 6, False, False, None),
    ("RC5", 36000, 889, 889, 889, 889, 889, 889, 5, 6, False, False, "RC5"),
    ("DENON", 38000, 275, 1900, 275, 775, 0, 0, 5, 10, False, False, None),
    ("RC6", 36000, 444, 444, 444, 444, 2666, 889, 8, 8, True, True, "RC6"),
    ("SAMSUNG32", 38000, 500, 1500, 500, 500, 4500, 4500, 16, 16, True, True, None),
    ("APPLE", 38000, 560, 1690, 560, 560, 9000, 4500, 8, 16, True, False, None),
    ("RECS80EXT", 38000, 158, 7432, 158, 4902, 0, 0, 4, 6, False, False, None),
    ("NUBERT", 38000, 340, 1700, 340, 680, 0, 0, 0, 10, False, False, None),
    ("BANG_OLUFSEN", 38000, 200, 3125, 200, 9375, 0, 0, 16, 8, False, False, None),
    ("GRUNDIG", 38000, 528, 528, 528, 1056, 6336, 3168, 0, 8, True, False, None),
    ("NOKIA", 38000, 500, 1500, 500, 500, 8000, 2500, 8, 8, True, True, None),
    ("SIEMENS", 36000, 275, 854, 275, 1708, 275, 854, 0, 10, False, False, None),
    ("JVC", 38000, 525, 1725, 525, 525, 9000, 4500, 16, 16, True, False, None),
    ("THOMSON", 36000, 500, 1500, 500, 500, 8000, 2500, 8, 8, True, True, None),
    ("NIKON", 38000, 500, 1500, 500, 3500, 2000, 6500, 0, 2, False, False, None),
    ("NETBOX", 38000, 560, 1690, 560, 560, 9000, 4500, 16, 16, True, True, None),
    ("ORTEK", 38000, 560, 1690, 560, 560, 9000, 4500, 16, 16, True, True, None),
    ("TELEFUNKEN", 38000, 750, 1150, 750, 400, 750, 1150, 0, 15, False, False, None),
    ("FDC", 38000, 550, 1600, 550, 550, 5000, 5000, 16, 16, True, False, None),
    ("RCCAR", 36000, 400, 400, 400, 800, 400, 400, 0, 16, True, True, None),
    ("RC6A", 36000, 444, 444, 444, 444, 2666, 889, 8, 16, True, True, "RC6A"),
    ("KATHREIN", 38000, 568, 1675, 568, 568, 9000, 4500, 4, 12, True, True, None),
    ("LEGO", 38000, 158, 7432, 158, 4902, 0, 0, 4, 6, False, False, None),
    ("IRMP16", 38000, 500, 1500, 500, 500, 9000, 4500, 0, 16, True, True, None),
    ("BOSE", 38000, 500, 1500, 500, 500, 1000, 1500, 8, 8, False, True, None),
    ("A1TVBOX", 38000, 560, 1690, 560, 560, 9000, 4500, 16, 16, True, True, None),
    ("ROOMBA", 38000, 500, 1500, 500, 500, 3000, 1000, 8, 8, False, False, None),
    ("RCMM32", 36000, 166, 166, 166, 166, 166, 166, 12, 12, False, False, "RCMM32"),
    ("RCMM24", 36000, 166, 166, 166, 166, 166, 166, 8, 12, False, False, "RCMM24"),
    ("RCMM12", 36000, 166, 166, 166, 166, 166, 166, 0, 12, False, False, "RCMM12"),
    ("SPEAKER", 38000, 550, 1650, 550, 550, 4500, 4500, 4, 12, False, True, None),
    ("LGAIR", 38000, 550, 1500, 550, 550, 8000, 4000, 8, 16, False, True, None),
    ("SAMSUNG48", 38000, 550, 1500, 550, 550, 4500, 4500, 16, 32, True, True, None),
    ("MERLIN", 38000, 550, 1500, 550, 550, 5000, 5000, 9, 16, True, True, None),
    ("PENTAX", 38000, 500, 1500, 500, 3500, 2000, 6500, 0, 6, False, False, None),
    ("FAN", 38000, 500, 1500, 500, 3500, 3000, 3000, 8, 8, False, False, None),
    ("S100", 40000, 550, 550, 550, 1650, 4400, 4400, 6, 6, False, False, None),
    ("ACP24", 38000, 560, 1690, 560, 560, 9000, 4500, 16, 8, True, True, None),
    ("TECHNICS", 37000, 500, 1500, 500, 500, 3500, 1750, 16, 8, True, False, None),
    ("PANASONIC", 38000, 500, 1500, 500, 500, 3500, 1750, 16, 32, True, False, None),
    ("MITSU_HEAVY", 38000, 400, 1200, 400, 400, 3200, 1600, 16, 16, True, False, None),
    ("VINCENT", 38000, 550, 1550, 550, 550, 5000, 5000, 16, 16, True, False, None),
    ("SAMSUNGAH", 38000, 500, 1500, 500, 500, 5000, 5000, 16, 16, True, True, None),
    ("GREE", 38000, 550, 1650, 550, 550, 9000, 4500, 16, 8, True, True, None),
    ("RCII", 38000, 400, 1200, 400, 400, 3500, 1750, 12, 12, True, False, None),
    ("METZ", 38000, 528, 528, 528, 1056, 6336, 3168, 0, 12, True, False, None),
    ("NEC16", 38000, 560, 1690, 560, 560, 9000, 4500, 8, 8, True, True, None),
    ("NEC42", 38000, 560, 1690, 560, 560, 9000, 4500, 8, 34, True, True, None),
    ("LOEWE", 38000, 600, 1600, 600, 600, 5000, 5000, 0, 16, True, False, None),
    ("MELINERA", 38000, 550, 1550, 550, 550, 5000, 5000, 16, 16, True, False, None),
    ("RC6A20", 36000, 444, 444, 444, 444, 2666, 889, 8, 20, True, True, "RC6A20"),
    ("IHELICOPTER", 38000, 600, 600, 600, 1200, 5000, 5000, 0, 14, False, False, None),
    ("HAMA", 38000, 550, 1550, 550, 550, 5000, 5000, 0, 16, True, False, None),
    ("IRMP", 38000, 550, 1550, 550, 550, 5000, 5000, 0, 16, True, False, None),
    ("VITEC", 38000, 400, 1250, 400, 400, 5000, 5000, 0, 12, True, False, None),
    ("SAMSUNG_TC", 38000, 550, 1450, 550, 550, 5000, 5000, 24, 16, True, True, None),
    ("RUWIDO", 36000, 396, 396, 396, 1188, 396, 396, 8, 8, False, False, None),
    ("HUMAX", 38000, 550, 1550, 550, 550, 5000, 5000, 16, 16, True, True, None),
]

def main():
    # Write to CSV file
    with open('irmp_protocols.csv', 'w', newline='') as csvfile:
        fieldnames = [
            'Protocol', 
            'Carrier (Hz)', 
            'Pulse1 (µs)', 
            'Pause1 (µs)', 
            'Pulse0 (µs)', 
            'Pause0 (µs)', 
            'Header Pulse (µs)', 
            'Header Pause (µs)', 
            'Address Bits', 
            'Command Bits', 
            'Stop Bit', 
            'LSB First', 
            'Special Flags'
        ]
        
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        for protocol in IR_PROTOCOLS:
            name, carrier, pulse1, pause1, pulse0, pause0, hp, hpa, addr_bits, cmd_bits, stop_bit, lsb_first, flags = protocol
            
            writer.writerow({
                'Protocol': name,
                'Carrier (Hz)': carrier,
                'Pulse1 (µs)': pulse1,
                'Pause1 (µs)': pause1,
                'Pulse0 (µs)': pulse0,
                'Pause0 (µs)': pause0,
                'Header Pulse (µs)': hp,
                'Header Pause (µs)': hpa,
                'Address Bits': addr_bits,
                'Command Bits': cmd_bits,
                'Stop Bit': 'Yes' if stop_bit else 'No',
                'LSB First': 'Yes' if lsb_first else 'No',
                'Special Flags': flags if flags else ''
            })
    
    print(f"Created irmp_protocols.csv with {len(IR_PROTOCOLS)} protocols")

if __name__ == "__main__":
    main()