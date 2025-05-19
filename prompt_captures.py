import re
import os
import sys

LINE_RE = re.compile(r"^(-?)\s*(\d+)(\*?)\s+(.*)")
CAPTURES = os.getcwd() + "/captures/"
captured_files = os.listdir(CAPTURES)

for line in open("processed_codes.txt", "r"):
    m = LINE_RE.match(line)
    # print(m.groups())
    if m.groups()[0] == "-":
        print("Skip")
        continue
    number = m.groups()[1]
    filename = number + ".csv"
    if filename in captured_files:
        print(f"File {filename} exists")
        continue
    print(f"Setup for capturing {number}")
    try:
        os.system(f"python3 2>/dev/null capture_saleae.py {number}")
        os.system(f"python3 analyze_signal.py captures/{number}.csv")
    except KeyboardInterrupt:
        sys.exit(1)