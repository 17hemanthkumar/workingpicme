"""
preview_reset.py

Preview what will be deleted without actually deleting anything
"""

import sqlite3
import os
import glob

def preview_reset():
    """Show what would be deleted without actually deleting"""
    
    print("=" * 70)
    print("RESET PREVIEW - What will be deleted")
    print("=" * 70)
    print()
    
    items_to_delete = []
    
    # 1. Check database
    print("📊 Database Records:")
    try:
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        
        # Check photos table
        cursor.execute("SELECT COUNT(*) FROM photos WHERE has_faces = 1 OR processed = 1")
        processed_photos = cursor.fetchone()[0]
        if processed_photos > 0:
            items_to_delete.append(f"  • {processed_photos} processed photo flags")
        
        # Check for face-related tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [t[0] for t in cursor.fetchall()]
        
        for table in ['face_detections', 'face_encodings', 'person_photos']:
            if table in tables:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                if count > 0:
                    items_to_delete.append(f"  • {count} records from {table}")
        
        conn.close()
        
        if not items_to_delete:
            print("  (No database records to delete)")
        else:
            for item in items_to_delete:
                print(item)
    except Exception as e:
        print(f"  Error checking database: {e}")
    
    print()
    
    # 2. Check model files
    print("🤖 ML Model Files:")
    model_files = [
        'face_encodings.pkl',
        'known_face_encodings.pkl',
        'multi_angle_model.pkl',
        'face_recognition_model.pkl',
        'known_faces.dat',
        'multi_angle_faces.dat'
    ]
    
    found_models = []
    for model_file in model_files:
        if os.path.exists(model_file):
            size = os.path.getsize(model_file)
            found_models.append(f"  • {model_file} ({size:,} bytes)")
    
    if found_models:
        for model in found_models:
            print(model)
    else:
        print("  (No model files found)")
    
    print()
    
    # 3. Check face crops
    print("📁 Face Crops Directory:")
    if os.path.exists('face_crops'):
        face_files = glob.glob('face_crops/**/*', recursive=True)
        face_files = [f for f in face_files if os.path.isfile(f)]
        if face_files:
            total_size = sum(os.path.getsize(f) for f in face_files)
            print(f"  • {len(face_files)} face crop files ({total_size:,} bytes)")
        else:
            print("  (Directory exists but is empty)")
    else:
        print("  (Directory doesn't exist)")
    
    print()
    
    # 4. Check statistics files
    print("📈 Statistics Files:")
    stats_files = [
        'detection_stats.json',
        'face_detection_stats.json',
        'processing_stats.json'
    ]
    
    found_stats = []
    for stats_file in stats_files:
        if os.path.exists(stats_file):
            size = os.path.getsize(stats_file)
            found_stats.append(f"  • {stats_file} ({size:,} bytes)")
    
    if found_stats:
        for stat in found_stats:
            print(stat)
    else:
        print("  (No statistics files found)")
    
    print()
    print("=" * 70)
    print("IMPORTANT: Photos themselves will NOT be deleted!")
    print("=" * 70)
    print()
    print("To proceed with reset, run: python complete_system_reset.py")
    print()

if __name__ == "__main__":
    preview_reset()
