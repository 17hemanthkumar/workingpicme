"""
Migration script to add cover_thumbnail field to existing events.
This script updates events_data.json to include the new cover_thumbnail field.
"""

import json
import os
from datetime import datetime

# Path to events data file
EVENTS_DATA_PATH = os.path.join(os.path.dirname(__file__), 'events_data.json')
DEFAULT_THUMBNAIL = '/static/images/default_event_thumbnail.jpg'

def migrate_events_data():
    """Add cover_thumbnail field to all existing events"""
    
    # Backup the original file
    backup_path = f"{EVENTS_DATA_PATH}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    try:
        # Read current events data
        with open(EVENTS_DATA_PATH, 'r') as f:
            events_data = json.load(f)
        
        # Create backup
        with open(backup_path, 'w') as f:
            json.dump(events_data, f, indent=2)
        print(f"✓ Backup created: {backup_path}")
        
        # Add cover_thumbnail field to all events that don't have it
        updated_count = 0
        for event in events_data:
            if 'cover_thumbnail' not in event:
                event['cover_thumbnail'] = DEFAULT_THUMBNAIL
                updated_count += 1
        
        # Save updated data
        with open(EVENTS_DATA_PATH, 'w') as f:
            json.dump(events_data, f, indent=2)
        
        print(f"✓ Migration completed successfully!")
        print(f"  - Total events: {len(events_data)}")
        print(f"  - Events updated: {updated_count}")
        print(f"  - Events already had thumbnail: {len(events_data) - updated_count}")
        
        return True
        
    except FileNotFoundError:
        print(f"✗ Error: {EVENTS_DATA_PATH} not found")
        return False
    except json.JSONDecodeError as e:
        print(f"✗ Error: Invalid JSON in events_data.json - {e}")
        return False
    except Exception as e:
        print(f"✗ Error during migration: {e}")
        # Restore from backup if something went wrong
        if os.path.exists(backup_path):
            with open(backup_path, 'r') as f:
                backup_data = json.load(f)
            with open(EVENTS_DATA_PATH, 'w') as f:
                json.dump(backup_data, f, indent=2)
            print(f"✓ Restored from backup")
        return False

def verify_thumbnails_directory():
    """Ensure the thumbnails directory exists"""
    thumbnails_dir = os.path.join(os.path.dirname(__file__), '..', 'uploads', 'thumbnails')
    
    if not os.path.exists(thumbnails_dir):
        os.makedirs(thumbnails_dir, exist_ok=True)
        print(f"✓ Created thumbnails directory: {thumbnails_dir}")
    else:
        print(f"✓ Thumbnails directory already exists: {thumbnails_dir}")
    
    return thumbnails_dir

if __name__ == '__main__':
    print("=" * 60)
    print("Event Cover Thumbnail Migration")
    print("=" * 60)
    print()
    
    # Step 1: Verify/create thumbnails directory
    print("Step 1: Verifying thumbnails directory...")
    thumbnails_dir = verify_thumbnails_directory()
    print()
    
    # Step 2: Migrate events data
    print("Step 2: Migrating events data...")
    success = migrate_events_data()
    print()
    
    if success:
        print("=" * 60)
        print("Migration completed successfully! ✓")
        print("=" * 60)
        print()
        print("Next steps:")
        print("1. Add a default thumbnail image at:")
        print("   frontend/static/images/default_event_thumbnail.jpg")
        print("2. Restart your Flask application")
        print("3. Test event creation with thumbnail upload")
    else:
        print("=" * 60)
        print("Migration failed! ✗")
        print("=" * 60)
        print("Please check the error messages above and try again.")
