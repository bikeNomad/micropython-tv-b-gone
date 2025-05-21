def is_similar(code1, code2, tolerance_percent=10, max_gap_us=20000):
    """
    Compare two IR codes for similarity up to the first gap > max_gap_us.
    
    Args:
        code1: First code tuple (name, on_us, off_us, ...)
        code2: Second code tuple (name, on_us, off_us, ...)
        tolerance_percent: Maximum percentage difference allowed between periods
        max_gap_us: Maximum gap in microseconds before stopping comparison
        
    Returns:
        bool: True if codes are similar within the given tolerance
    """
    # Extract timing values (skip the name if the first element is a string)
    values1 = code1[1:] if isinstance(code1[0], str) else code1
    values2 = code2[1:] if isinstance(code2[0], str) else code2
    
    # Find the length of the shorter code
    min_length = min(len(values1), len(values2))
    
    # Find the index of the first gap > max_gap_us in each code
    end_idx1 = min_length
    end_idx2 = min_length
    
    for i, val in enumerate(values1):
        if val > max_gap_us:
            end_idx1 = i
            break
            
    for i, val in enumerate(values2):
        if val > max_gap_us:
            end_idx2 = i
            break
    
    # Use the smaller of the two end indices
    end_idx = min(end_idx1, end_idx2)
    
    # If end_idx is 0, there's no data to compare before the first large gap
    if end_idx == 0:
        return False
    
    # Compare each pair of values up to the end index
    for i in range(end_idx):
        if i >= len(values1) or i >= len(values2):
            break
            
        val1 = values1[i]
        val2 = values2[i]
        
        # Calculate the percentage difference
        max_val = max(val1, val2)
        min_val = min(val1, val2)
        
        if max_val == 0 and min_val == 0:
            # Both values are zero, consider them similar
            continue
            
        percent_diff = ((max_val - min_val) / max_val) * 100
        
        if percent_diff > tolerance_percent:
            return False
    
    return True

def find_similar_codes(codes, tolerance_percent=10, max_gap_us=20000):
    """
    Find all pairs of similar codes in the provided list.
    
    Args:
        codes: List of code tuples
        tolerance_percent: Maximum percentage difference allowed
        max_gap_us: Maximum gap in microseconds before stopping comparison
        
    Returns:
        list: Pairs of similar codes as (name1, name2, matching_length)
    """
    similar_pairs = []
    
    for i in range(len(codes)):
        for j in range(i+1, len(codes)):
            if is_similar(codes[i], codes[j], tolerance_percent, max_gap_us):
                # Get code names for better reporting
                name1 = codes[i][0] if isinstance(codes[i][0], str) else f"Code {i}"
                name2 = codes[j][0] if isinstance(codes[j][0], str) else f"Code {j}"
                
                # Calculate the matching length (up to the first gap)
                values1 = codes[i][1:] if isinstance(codes[i][0], str) else codes[i]
                values2 = codes[j][1:] if isinstance(codes[j][0], str) else codes[j]
                
                # Find the index of the first gap > max_gap_us in each code
                end_idx1 = len(values1)
                for k, val in enumerate(values1):
                    if val > max_gap_us:
                        end_idx1 = k
                        break
                        
                end_idx2 = len(values2)
                for k, val in enumerate(values2):
                    if val > max_gap_us:
                        end_idx2 = k
                        break
                
                matching_length = min(end_idx1, end_idx2)
                
                similar_pairs.append((name1, name2, matching_length))
    
    return similar_pairs

def main():
    """
    Example usage to find similar codes in the CODES list.
    """
    from codes import CODES
    
    # Find similar codes with 10% tolerance, stopping at gaps > 20ms
    similar = find_similar_codes(CODES, 10, 20000)
    
    print(f"Found {len(similar)} similar code pairs:")
    for name1, name2, length in similar:
        print(f"  {name1} and {name2} (matching length before gap: {length})")

if __name__ == "__main__":
    main()