"""
Migration script to add organization_name field to existing events.
This script updates events_data.json to include organization_name for events that don't have it.
"""

import json
import os
import shutil
from datetime import datetime

# Path to events data file
EVENTS_DATA_PATH = os.path.join(os.path.dirname(__file__), 'events_data.json')
DEFAULT_ORG_NAME = 'Sample Organization'

def migrate_events_data():
    """Add organization_name field to all existing events that don't have it"""
    
    # Backup the original file
    backup_path = EVENTS_DATA_PATH + f'.backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}'
    
    try:
        # Read current events data
        with open(EVENTS_DATA_PATH, 'r') as f:
            events_data = json.load(f)
        
        # Create backup
        shutil.copy(EVENTS_DATA_PATH, backup_path)
        print(f"✓ Backup created: {backup_path}")
        
        # Add organization_name field to all events that don't have it
        updated_count = 0
        for event in events_data:
            if 'organization_name' not in event:
                event['organization_name'] = DEFAULT_ORG_NAME
                updated_count += 1
        
        # Write updated data back to file
        with open(EVENTS_DATA_PATH, 'w') as f:
            json.dump(events_data, f, indent=2)
        
        print(f"✓ Migration complete!")
        print(f"  - Total events: {len(events_data)}")
        print(f"  - Events updated: {updated_count}")
        print(f"  - Events already had organization_name: {len(events_data) - updated_count}")
        
        return True
        
    except FileNotFoundError:
        print(f"✗ Error: {EVENTS_DATA_PATH} not found")
        return False
    except json.JSONDecodeError:
        print(f"✗ Error: {EVENTS_DATA_PATH} contains invalid JSON")
        return False
    except Exception as e:
        print(f"✗ Error during migration: {e}")
        # Restore from backup if something went wrong
        if os.path.exists(backup_path):
            shutil.copy(backup_path, EVENTS_DATA_PATH)
            print(f"✓ Restored from backup")
        return False

if __name__ == '__main__':
    print("=" * 60)
    print("Event Organization Name Migration")
    print("=" * 60)
    print()
    
    success = migrate_events_data()
    
    print()
    if success:
        print("✓ Migration completed successfully!")
        print()
        print("Next steps:")
        print("1. Restart your Flask application")
        print("2. Verify events display organization names correctly")
        print("3. Test search functionality with organization and event names")
    else:
        print("✗ Migration failed. Please check the errors above.")
    
    print("=" * 60)
