"""
Complete reprocessing with verification
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import process_images
import shutil

print("=" * 70)
print("COMPLETE REPROCESSING WITH VERIFICATION")
print("=" * 70)

event_id = "event_931cd6b8"

# Step 1: Clear processed folder
processed_dir = os.path.join("..", "processed", event_id)
if os.path.exists(processed_dir):
    print(f"\n1. Clearing: {processed_dir}")
    shutil.rmtree(processed_dir)
    print("   ✓ Cleared")
else:
    print("\n1. No processed folder to clear")

# Step 2: Process photos
print(f"\n2. Processing photos for: {event_id}")
print("-" * 70)

try:
    process_images(event_id)
    print("\n✓ Processing complete")
except Exception as e:
    print(f"\n✗ Error: {e}")
    import traceback
    traceback.print_exc()

# Step 3: Verify results
print("\n3. Verification:")
print("-" * 70)

if os.path.exists(processed_dir):
    person_folders = [f for f in os.listdir(processed_dir) if os.path.isdir(os.path.join(processed_dir, f))]
    print(f"   Person folders created: {len(person_folders)}")
    
    total_individual = 0
    total_group = 0
    
    for person in person_folders[:5]:  # Show first 5
        person_path = os.path.join(processed_dir, person)
        individual_path = os.path.join(person_path, "individual")
        group_path = os.path.join(person_path, "group")
        
        ind_count = len(os.listdir(individual_path)) if os.path.exists(individual_path) else 0
        grp_count = len(os.listdir(group_path)) if os.path.exists(group_path) else 0
        
        total_individual += ind_count
        total_group += grp_count
        
        print(f"   {person}: {ind_count} individual, {grp_count} group")
    
    if len(person_folders) > 5:
        print(f"   ... and {len(person_folders) - 5} more")
    
    print(f"\n   Total: {total_individual} individual photos, {total_group} group photos")
else:
    print("   ✗ No processed folder created")

print("\n" + "=" * 70)
print("REPROCESSING COMPLETE")
print("=" * 70)
