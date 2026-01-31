#!/usr/bin/env python3
"""Test download progress display"""

import sys
import time

print("Testing real-time progress display with stderr...")
print()

# Simulate download with progress
total = 100
for i in range(1, total + 1):
    percent = (i / total) * 100
    progress_msg = f"  Progress: {percent:.1f}% ({i}/{total} MB)"
    sys.stderr.write(progress_msg + '\r')
    sys.stderr.flush()
    time.sleep(0.05)  # Simulate download delay

# Clear progress line
sys.stderr.write(" " * 80 + '\n')
sys.stderr.flush()
print("Download test complete!")
