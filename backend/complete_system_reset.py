"""
complete_system_reset.py

WARNING: This will delete ALL face detection data and reset the system
"""

import sqlite3
import os
import shutil
import sys

def complete_reset():
    """Nuclear option - reset everything"""
    
    print("=" * 70)
    print("COMPLETE SYSTEM RESET - ALL FACE DATA WILL BE DELETED")
    print("=" * 70)
    print()
    
    # Track what we're deleting
    deleted_items = []
    errors = []
    
    # 1. Reset database flags
    print("Step 1: Resetting database...")
    try:
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        
        # Clear all processing flags
        cursor.execute("UPDATE photos SET has_faces = 0, processed = 0")
        photo_count = cursor.rowcount
        deleted_items.append(f"Reset {photo_count} photo processing flags")
        
        # Delete all face detection records (if table exists)
        try:
            cursor.execute("DELETE FROM face_detections")
            deleted_items.append(f"Deleted {cursor.rowcount} face detection records")
        except sqlite3.OperationalError:
            deleted_items.append("face_detections table doesn't exist (skipped)")
        
        # Delete all face encodings (if table exists)
        try:
            cursor.execute("DELETE FROM face_encodings")
            deleted_items.append(f"Deleted {cursor.rowcount} face encoding records")
        except sqlite3.OperationalError:
            deleted_items.append("face_encodings table doesn't exist (skipped)")
        
        # Delete person-photo associations (if table exists)
        try:
            cursor.execute("DELETE FROM person_photos")
            deleted_items.append(f"Deleted {cursor.rowcount} person-photo associations")
        except sqlite3.OperationalError:
            deleted_items.append("person_photos table doesn't exist (skipped)")
        
        conn.commit()
        conn.close()
        print("✓ Database reset complete")
    except Exception as e:
        errors.append(f"Database error: {e}")
        print(f"✗ Database error: {e}")
    
    print()
    
    # 2. Delete ML model files
    print("Step 2: Deleting ML model files...")
    model_files = [
        'face_encodings.pkl',
        'known_face_encodings.pkl',
        'multi_angle_model.pkl',
        'face_recognition_model.pkl',
        'known_faces.dat',
        'multi_angle_faces.dat'
    ]
    
    for model_file in model_files:
        try:
            if os.path.exists(model_file):
                os.remove(model_file)
                deleted_items.append(f"Deleted {model_file}")
                print(f"✓ Deleted {model_file}")
            else:
                print(f"  {model_file} doesn't exist (skipped)")
        except Exception as e:
            errors.append(f"Error deleting {model_file}: {e}")
            print(f"✗ Error deleting {model_file}: {e}")
    
    print()
    
    # 3. Clear face crops directory
    print("Step 3: Clearing face crops directory...")
    try:
        if os.path.exists('face_crops'):
            shutil.rmtree('face_crops')
            deleted_items.append("Cleared face_crops directory")
            print("✓ Cleared face_crops directory")
        
        os.makedirs('face_crops', exist_ok=True)
        print("✓ Recreated face_crops directory")
    except Exception as e:
        errors.append(f"Error with face_crops: {e}")
        print(f"✗ Error with face_crops: {e}")
    
    print()
    
    # 4. Reset detection statistics
    print("Step 4: Clearing detection statistics...")
    stats_files = [
        'detection_stats.json',
        'face_detection_stats.json',
        'processing_stats.json'
    ]
    
    for stats_file in stats_files:
        try:
            if os.path.exists(stats_file):
                os.remove(stats_file)
                deleted_items.append(f"Deleted {stats_file}")
                print(f"✓ Deleted {stats_file}")
            else:
                print(f"  {stats_file} doesn't exist (skipped)")
        except Exception as e:
            errors.append(f"Error deleting {stats_file}: {e}")
            print(f"✗ Error deleting {stats_file}: {e}")
    
    print()
    
    # 5. Clear any cached face data
    print("Step 5: Clearing cached face data...")
    cache_dirs = ['__pycache__', '.cache', 'temp_faces']
    
    for cache_dir in cache_dirs:
        try:
            if os.path.exists(cache_dir):
                shutil.rmtree(cache_dir)
                deleted_items.append(f"Cleared {cache_dir}")
                print(f"✓ Cleared {cache_dir}")
        except Exception as e:
            errors.append(f"Error clearing {cache_dir}: {e}")
            print(f"✗ Error clearing {cache_dir}: {e}")
    
    print()
    print("=" * 70)
    print("RESET SUMMARY")
    print("=" * 70)
    
    print(f"\n✓ Successfully completed {len(deleted_items)} operations:")
    for item in deleted_items:
        print(f"  • {item}")
    
    if errors:
        print(f"\n✗ Encountered {len(errors)} errors:")
        for error in errors:
            print(f"  • {error}")
    else:
        print("\n✓ No errors encountered")
    
    print()
    print("=" * 70)
    print("SYSTEM RESET COMPLETE - Ready for fresh detection")
    print("=" * 70)
    print()
    print("Next steps:")
    print("1. Rebuild face detection system with multi-angle support")
    print("2. Process photos with new enhanced detection")
    print("3. Test live face scanning with deep feature analysis")
    print()

def main():
    """Main entry point with confirmation"""
    print()
    print("⚠️  WARNING: DESTRUCTIVE OPERATION ⚠️")
    print()
    print("This will permanently delete:")
    print("  • All face detection records")
    print("  • All face encodings")
    print("  • All person-photo associations")
    print("  • All ML model files")
    print("  • All face crops")
    print("  • All detection statistics")
    print()
    print("Photos themselves will NOT be deleted, only face data.")
    print()
    
    response = input("Are you sure you want to DELETE ALL face data? (type 'YES' to confirm): ")
    
    if response == "YES":
        print()
        complete_reset()
    else:
        print()
        print("Reset cancelled - no changes made")
        print()

if __name__ == "__main__":
    main()
