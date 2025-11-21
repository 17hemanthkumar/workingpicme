"""
Script to reprocess existing photos with correct classification
Run this once to fix existing photos
"""
import os
import shutil

PROCESSED_FOLDER = os.path.join(os.path.dirname(__file__), '..', 'processed')

def clean_processed_photos():
    """Remove all processed photos so they can be re-classified correctly"""
    if os.path.exists(PROCESSED_FOLDER):
        print(f"Cleaning processed folder: {PROCESSED_FOLDER}")
        for event_id in os.listdir(PROCESSED_FOLDER):
            event_path = os.path.join(PROCESSED_FOLDER, event_id)
            if os.path.isdir(event_path):
                print(f"  Removing: {event_id}")
                shutil.rmtree(event_path)
        print("✅ Cleaned! Photos will be re-processed with correct classification.")
        print("   Individual photos (1 face) → individual/ folder (private)")
        print("   Group photos (2+ faces) → group/ folder (public)")
    else:
        print("No processed folder found.")

if __name__ == '__main__':
    response = input("This will delete all processed photos. They will be re-classified correctly. Continue? (yes/no): ")
    if response.lower() == 'yes':
        clean_processed_photos()
    else:
        print("Cancelled.")
