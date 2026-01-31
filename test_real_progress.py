#!/usr/bin/env python3
"""Test real-time progress with os.write"""

import os
import sys
import time

print("Testing real-time progress with os.write (unbuffered)...")
print()

total = 100
for i in range(1, total + 1):
    percent = (i / total) * 100
    mb_downloaded = i / 10
    mb_total = 10
    
    bar_length = 30
    filled = int(bar_length * i / total)
    bar = "█" * filled + "░" * (bar_length - filled)
    
    progress_line = f"\r[{bar}] {percent:5.1f}% {mb_downloaded:6.1f}/{mb_total:6.1f} MB"
    
    # Use os.write for unbuffered output
    os.write(2, progress_line.encode('utf-8'))
    
    time.sleep(0.02)  # Simulate download

os.write(2, b"\n")
print("Progress test complete!")
