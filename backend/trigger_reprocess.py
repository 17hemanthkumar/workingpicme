"""
Trigger photo reprocessing for all events
Run this after cleaning processed photos
"""
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(__file__))

from app import process_images, UPLOAD_FOLDER
import threading

def reprocess_all_events():
    """Reprocess all events with correct photo classification"""
    if not os.path.exists(UPLOAD_FOLDER):
        print("No upload folder found.")
        return
    
    event_ids = [
        d for d in os.listdir(UPLOAD_FOLDER) 
        if os.path.isdir(os.path.join(UPLOAD_FOLDER, d))
    ]
    
    if not event_ids:
        print("No events found to process.")
        return
    
    print(f"Found {len(event_ids)} events to reprocess:")
    for event_id in event_ids:
        print(f"  - {event_id}")
    
    print("\nStarting reprocessing...")
    for event_id in event_ids:
        print(f"\nProcessing: {event_id}")
        process_images(event_id)
    
    print("\n✅ All events reprocessed with correct classification!")
    print("   Individual photos (1 face) → individual/ folder (private)")
    print("   Group photos (2+ faces) → group/ folder (public)")

if __name__ == '__main__':
    reprocess_all_events()
