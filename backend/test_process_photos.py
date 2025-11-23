"""
Test photo processing with robust detection
"""

import sys
import os

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import required modules
from app import process_images

print("=" * 70)
print("TEST: Process Photos with Robust Detection")
print("=" * 70)

# Process event
event_id = "event_931cd6b8"
print(f"\nProcessing event: {event_id}")
print("-" * 70)

try:
    process_images(event_id)
    print("\n" + "=" * 70)
    print("PROCESSING COMPLETE")
    print("=" * 70)
except Exception as e:
    print(f"\n✗ Error: {e}")
    import traceback
    traceback.print_exc()
