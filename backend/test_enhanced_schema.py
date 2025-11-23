#!/usr/bin/env python3
"""
Test Enhanced Database Schema

Tests the enhanced face detection database schema to ensure:
- All tables are created correctly
- Foreign key constraints work
- Indexes are in place
- Triggers function properly
- Views return expected data
"""

import sqlite3
import os
import sys
import json
import numpy as np
from datetime import datetime

def test_database_schema(db_path='database.db'):
    """
    Test the enhanced database schema
    
    Args:
        db_path (str): Path to the database file
    
    Returns:
        bool: True if all tests pass, False otherwise
    """
    
    print("=" * 70)
    print("TESTING ENHANCED DATABASE SCHEMA")
    print("=" * 70)
    print(f"Database: {db_path}")
    print(f"Timestamp: {datetime.now()}")
    print()
    
    if not os.path.exists(db_path):
        print(f"❌ Database file '{db_path}' not found!")
        print("Run 'python create_enhanced_schema.py' first.")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Enable foreign key constraints
        cursor.execute("PRAGMA foreign_keys = ON")
        
        print("Test 1: Verify table structure...")
        
        # Test table existence and structure
        expected_tables = {
            'photos': ['id', 'event_id', 'filename', 'filepath', 'upload_date', 'has_faces', 'processed', 'face_count'],
            'persons': ['id', 'person_uuid', 'name', 'created_date', 'last_seen', 'total_photos', 'confidence_score'],
            'face_detections': ['id', 'photo_id', 'person_id', 'face_bbox', 'detection_confidence', 'angle_estimate', 'quality_score'],
            'face_encodings': ['id', 'face_detection_id', 'person_id', 'encoding_vector', 'angle', 'quality_score'],
            'facial_features': ['id', 'face_detection_id', 'landmarks', 'eye_distance', 'nose_width', 'has_facial_hair'],
            'person_photos': ['id', 'person_id', 'photo_id', 'is_group_photo', 'match_confidence']
        }
        
        for table_name, expected_columns in expected_tables.items():
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = [row[1] for row in cursor.fetchall()]
            
            if not columns:
                print(f"  ❌ Table '{table_name}' not found")
                return False
            
            missing_columns = [col for col in expected_columns if col not in columns]
            if missing_columns:
                print(f"  ❌ Table '{table_name}' missing columns: {missing_columns}")
                return False
            
            print(f"  ✓ Table '{table_name}' - {len(columns)} columns")
        
        print("\nTest 2: Test basic CRUD operations...")
        
        # Test inserting data
        print("  Testing data insertion...")
        
        # Insert test photo
        cursor.execute("""
            INSERT INTO photos (event_id, filename, filepath, file_size, image_width, image_height)
            VALUES (?, ?, ?, ?, ?, ?)
        """, ('test_event_001', 'test_photo.jpg', '/path/to/test_photo.jpg', 1024000, 1920, 1080))
        photo_id = cursor.lastrowid
        print(f"    ✓ Inserted photo with ID: {photo_id}")
        
        # Insert test person
        cursor.execute("""
            INSERT INTO persons (person_uuid, name, confidence_score)
            VALUES (?, ?, ?)
        """, ('person_001_uuid', 'Test Person', 0.95))
        person_id = cursor.lastrowid
        print(f"    ✓ Inserted person with ID: {person_id}")
        
        # Insert test face detection
        face_bbox = json.dumps({'x': 100, 'y': 150, 'width': 200, 'height': 250})
        cursor.execute("""
            INSERT INTO face_detections (photo_id, person_id, face_bbox, detection_confidence, 
                                       detection_method, angle_estimate, quality_score)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (photo_id, person_id, face_bbox, 0.92, 'mtcnn', 'frontal', 0.85))
        face_detection_id = cursor.lastrowid
        print(f"    ✓ Inserted face detection with ID: {face_detection_id}")
        
        # Insert test face encoding (simulate 128D vector)
        encoding_vector = np.random.rand(128).astype(np.float32).tobytes()
        cursor.execute("""
            INSERT INTO face_encodings (face_detection_id, person_id, encoding_vector, angle, quality_score)
            VALUES (?, ?, ?, ?, ?)
        """, (face_detection_id, person_id, encoding_vector, 'frontal', 0.88))
        encoding_id = cursor.lastrowid
        print(f"    ✓ Inserted face encoding with ID: {encoding_id}")
        
        # Insert test facial features
        landmarks_data = json.dumps([[100, 120], [150, 125], [200, 130]])  # Simplified landmarks
        cursor.execute("""
            INSERT INTO facial_features (face_detection_id, landmarks, eye_distance, nose_width, 
                                       jaw_width, has_facial_hair, glasses)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (face_detection_id, landmarks_data, 45.5, 25.2, 120.8, 0, 1))
        features_id = cursor.lastrowid
        print(f"    ✓ Inserted facial features with ID: {features_id}")
        
        # Insert person-photo association
        cursor.execute("""
            INSERT INTO person_photos (person_id, photo_id, is_group_photo, match_confidence)
            VALUES (?, ?, ?, ?)
        """, (person_id, photo_id, 0, 0.92))
        association_id = cursor.lastrowid
        print(f"    ✓ Inserted person-photo association with ID: {association_id}")
        
        print("\nTest 3: Test foreign key constraints...")
        
        # Test valid foreign key
        try:
            cursor.execute("""
                INSERT INTO face_detections (photo_id, person_id, face_bbox, detection_confidence)
                VALUES (?, ?, ?, ?)
            """, (photo_id, person_id, '{"x": 50, "y": 60, "width": 100, "height": 120}', 0.80))
            print("    ✓ Valid foreign key constraint works")
        except sqlite3.IntegrityError:
            print("    ❌ Valid foreign key constraint failed")
            return False
        
        # Test invalid foreign key
        try:
            cursor.execute("""
                INSERT INTO face_detections (photo_id, person_id, face_bbox, detection_confidence)
                VALUES (?, ?, ?, ?)
            """, (99999, person_id, '{"x": 50, "y": 60, "width": 100, "height": 120}', 0.80))
            print("    ❌ Invalid foreign key constraint not enforced")
            return False
        except sqlite3.IntegrityError:
            print("    ✓ Invalid foreign key constraint properly rejected")
        
        print("\nTest 4: Test triggers...")
        
        # Check if photo face_count was updated by trigger
        cursor.execute("SELECT face_count, has_faces FROM photos WHERE id = ?", (photo_id,))
        face_count, has_faces = cursor.fetchone()
        
        if face_count >= 2 and has_faces == 1:  # We inserted 2 face detections
            print(f"    ✓ Photo face_count trigger works (count: {face_count}, has_faces: {has_faces})")
        else:
            print(f"    ❌ Photo face_count trigger failed (count: {face_count}, has_faces: {has_faces})")
            return False
        
        # Check if person total_photos was updated by trigger
        cursor.execute("SELECT total_photos FROM persons WHERE id = ?", (person_id,))
        total_photos = cursor.fetchone()[0]
        
        if total_photos >= 1:
            print(f"    ✓ Person total_photos trigger works (count: {total_photos})")
        else:
            print(f"    ❌ Person total_photos trigger failed (count: {total_photos})")
            return False
        
        print("\nTest 5: Test views...")
        
        # Test person_summary view
        cursor.execute("SELECT * FROM person_summary WHERE id = ?", (person_id,))
        person_summary = cursor.fetchone()
        
        if person_summary:
            print(f"    ✓ person_summary view works (found person: {person_summary[2]})")
        else:
            print("    ❌ person_summary view failed")
            return False
        
        # Test photo_summary view
        cursor.execute("SELECT * FROM photo_summary WHERE id = ?", (photo_id,))
        photo_summary = cursor.fetchone()
        
        if photo_summary:
            print(f"    ✓ photo_summary view works (faces: {photo_summary[6]}, persons: {photo_summary[7]})")
        else:
            print("    ❌ photo_summary view failed")
            return False
        
        print("\nTest 6: Test indexes...")
        
        # Check if indexes exist
        cursor.execute("SELECT name FROM sqlite_master WHERE type='index' AND name LIKE 'idx_%'")
        indexes = [row[0] for row in cursor.fetchall()]
        
        expected_indexes = [
            'idx_photos_event', 'idx_photos_has_faces', 'idx_face_detections_photo',
            'idx_face_encodings_person', 'idx_person_photos_person'
        ]
        
        found_indexes = [idx for idx in expected_indexes if idx in indexes]
        
        if len(found_indexes) >= len(expected_indexes) * 0.8:  # At least 80% of expected indexes
            print(f"    ✓ Indexes created ({len(found_indexes)}/{len(expected_indexes)} expected indexes found)")
        else:
            print(f"    ❌ Missing indexes ({len(found_indexes)}/{len(expected_indexes)} expected indexes found)")
            return False
        
        print("\nTest 7: Test data retrieval...")
        
        # Test complex query with joins
        cursor.execute("""
            SELECT p.name, ph.filename, fd.detection_method, fd.angle_estimate, fe.quality_score
            FROM persons p
            JOIN face_detections fd ON p.id = fd.person_id
            JOIN photos ph ON fd.photo_id = ph.id
            JOIN face_encodings fe ON fd.id = fe.face_detection_id
            WHERE p.id = ?
        """, (person_id,))
        
        results = cursor.fetchall()
        
        if results:
            print(f"    ✓ Complex join query works ({len(results)} results)")
            for result in results:
                print(f"      - {result[0]} in {result[1]} ({result[2]}, {result[3]}, quality: {result[4]:.2f})")
        else:
            print("    ❌ Complex join query failed")
            return False
        
        # Rollback test data (don't save test data)
        conn.rollback()
        conn.close()
        
        print("\n" + "=" * 70)
        print("✅ ALL DATABASE SCHEMA TESTS PASSED")
        print("=" * 70)
        print("Database schema is ready for use!")
        print()
        print("Schema features verified:")
        print(f"  ✓ {len(expected_tables)} tables with proper structure")
        print(f"  ✓ {len(indexes)} performance indexes")
        print("  ✓ Foreign key constraints")
        print("  ✓ Automatic triggers")
        print("  ✓ Summary views")
        print("  ✓ Complex queries")
        print()
        print("Next steps:")
        print("1. Continue with Task 1.2: Enhanced Face Detector")
        print("2. Start implementing face detection components")
        print("=" * 70)
        
        return True
        
    except sqlite3.Error as e:
        print(f"\n❌ Database error: {e}")
        import traceback
        traceback.print_exc()
        return False
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """
    Main function to test the database schema
    """
    
    db_path = 'database.db'
    
    success = test_database_schema(db_path)
    
    if success:
        print("\n🎉 Database schema tests completed successfully!")
        sys.exit(0)
    else:
        print("\n💥 Database schema tests failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
