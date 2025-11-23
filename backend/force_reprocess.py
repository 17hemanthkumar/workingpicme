"""
Force reprocess all photos in an event
Clears processed folders and triggers fresh processing
"""

import os
import shutil
import sys

def force_reprocess_event(event_id):
    """
    Force reprocess all photos for an event
    
    Args:
        event_id: Event ID to reprocess
    """
    print(f"=" * 70)
    print(f"FORCE REPROCESS: {event_id}")
    print(f"=" * 70)
    
    # Paths
    processed_dir = os.path.join("..", "processed", event_id)
    uploads_dir = os.path.join("..", "uploads", event_id)
    
    # Check if event exists
    if not os.path.exists(uploads_dir):
        print(f"✗ Event not found: {uploads_dir}")
        return False
    
    # Count photos
    photo_count = len([f for f in os.listdir(uploads_dir) 
                      if f.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.webp')) 
                      and not f.endswith('_qr.png')])
    
    print(f"\nEvent: {event_id}")
    print(f"Photos to process: {photo_count}")
    
    # Clear processed folder
    if os.path.exists(processed_dir):
        print(f"\nClearing processed folder: {processed_dir}")
        try:
            shutil.rmtree(processed_dir)
            print("✓ Processed folder cleared")
        except Exception as e:
            print(f"✗ Error clearing folder: {e}")
            return False
    else:
        print("\nNo processed folder exists yet")
    
    print("\n✓ Ready for reprocessing")
    print("\nTo trigger processing, run:")
    print(f"  python app.py")
    print(f"  # Or restart the Flask server")
    
    return True


if __name__ == '__main__':
    # Default event
    event_id = "event_931cd6b8"
    
    # Allow command line argument
    if len(sys.argv) > 1:
        event_id = sys.argv[1]
    
    force_reprocess_event(event_id)
