#!/usr/bin/env python3
"""
Test Enhanced MySQL Database Schema

Tests the enhanced face detection MySQL schema to ensure:
- All tables are created correctly
- Foreign key constraints work
- Indexes are in place
- Triggers function properly
- Views return expected data
"""

import mysql.connector
import json
import numpy as np
from datetime import datetime

# Database configuration (same as app.py)
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'picme_db'
}

def test_mysql_schema():
    """
    Test the enhanced MySQL database schema
    
    Returns:
        bool: True if all tests pass, False otherwise
    """
    
    print("=" * 70)
    print("TESTING ENHANCED MYSQL DATABASE SCHEMA")
    print("=" * 70)
    print(f"Database: {DB_CONFIG['database']}")
    print(f"Host: {DB_CONFIG['host']}")
    print(f"Timestamp: {datetime.now()}")
    print()
    
    try:
        # Connect to database
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        print("Test 1: Verify table structure...")
        
        # Test table existence
        expected_tables = ['photos', 'persons', 'face_detections', 'face_encodings', 'facial_features', 'person_photos']
        
        cursor.execute("""
            SELECT TABLE_NAME 
            FROM information_schema.TABLES 
            WHERE TABLE_SCHEMA = %s 
            AND TABLE_NAME IN (%s, %s, %s, %s, %s, %s)
        """, (DB_CONFIG['database'],) + tuple(expected_tables))
        
        tables = [row[0] for row in cursor.fetchall()]
        
        for table in expected_tables:
            if table in tables:
                print(f"  ✓ Table '{table}' exists")
            else:
                print(f"  ✗ Table '{table}' not found")
                return False
        
        print("\nTest 2: Test basic CRUD operations...")
        
        # Test inserting data
        print("  Testing data insertion...")
        
        # Insert test photo
        cursor.execute("""
            INSERT INTO photos (event_id, filename, filepath, file_size, image_width, image_height)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, ('test_event_001', 'test_photo.jpg', '/path/to/test_photo.jpg', 1024000, 1920, 1080))
        photo_id = cursor.lastrowid
        print(f"    ✓ Inserted photo with ID: {photo_id}")
        
        # Insert test person
        cursor.execute("""
            INSERT INTO persons (person_uuid, name, confidence_score)
            VALUES (%s, %s, %s)
        """, ('person_001_uuid', 'Test Person', 0.95))
        person_id = cursor.lastrowid
        print(f"    ✓ Inserted person with ID: {person_id}")
        
        # Insert test face detection
        face_bbox = json.dumps({'x': 100, 'y': 150, 'width': 200, 'height': 250})
        cursor.execute("""
            INSERT INTO face_detections (photo_id, person_id, face_bbox, detection_confidence, 
                                       detection_method, angle_estimate, quality_score)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (photo_id, person_id, face_bbox, 0.92, 'mtcnn', 'frontal', 0.85))
        face_detection_id = cursor.lastrowid
        print(f"    ✓ Inserted face detection with ID: {face_detection_id}")
        
        # Insert test face encoding (simulate 128D vector)
        encoding_vector = np.random.rand(128).astype(np.float32).tobytes()
        cursor.execute("""
            INSERT INTO face_encodings (face_detection_id, person_id, encoding_vector, angle, quality_score)
            VALUES (%s, %s, %s, %s, %s)
        """, (face_detection_id, person_id, encoding_vector, 'frontal', 0.88))
        encoding_id = cursor.lastrowid
        print(f"    ✓ Inserted face encoding with ID: {encoding_id}")
        
        # Insert test facial features
        landmarks_data = json.dumps([[100, 120], [150, 125], [200, 130]])
        cursor.execute("""
            INSERT INTO facial_features (face_detection_id, landmarks, eye_distance, nose_width, 
                                       jaw_width, has_facial_hair, glasses)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (face_detection_id, landmarks_data, 45.5, 25.2, 120.8, 0, 1))
        features_id = cursor.lastrowid
        print(f"    ✓ Inserted facial features with ID: {features_id}")
        
        # Insert person-photo association
        cursor.execute("""
            INSERT INTO person_photos (person_id, photo_id, is_group_photo, match_confidence)
            VALUES (%s, %s, %s, %s)
        """, (person_id, photo_id, 0, 0.92))
        association_id = cursor.lastrowid
        print(f"    ✓ Inserted person-photo association with ID: {association_id}")
        
        print("\nTest 3: Test foreign key constraints...")
        
        # Test valid foreign key
        try:
            cursor.execute("""
                INSERT INTO face_detections (photo_id, person_id, face_bbox, detection_confidence)
                VALUES (%s, %s, %s, %s)
            """, (photo_id, person_id, '{"x": 50, "y": 60, "width": 100, "height": 120}', 0.80))
            print("    ✓ Valid foreign key constraint works")
        except mysql.connector.IntegrityError:
            print("    ✗ Valid foreign key constraint failed")
            return False
        
        # Test invalid foreign key
        try:
            cursor.execute("""
                INSERT INTO face_detections (photo_id, person_id, face_bbox, detection_confidence)
                VALUES (%s, %s, %s, %s)
            """, (99999, person_id, '{"x": 50, "y": 60, "width": 100, "height": 120}', 0.80))
            print("    ✗ Invalid foreign key constraint not enforced")
            return False
        except mysql.connector.IntegrityError:
            print("    ✓ Invalid foreign key constraint properly rejected")
        
        print("\nTest 4: Test triggers...")
        
        # Check if photo face_count was updated by trigger
        cursor.execute("SELECT face_count, has_faces FROM photos WHERE id = %s", (photo_id,))
        result = cursor.fetchone()
        face_count, has_faces = result if result else (0, 0)
        
        if face_count >= 2 and has_faces == 1:
            print(f"    ✓ Photo face_count trigger works (count: {face_count}, has_faces: {has_faces})")
        else:
            print(f"    ✗ Photo face_count trigger failed (count: {face_count}, has_faces: {has_faces})")
            return False
        
        # Check if person total_photos was updated by trigger
        cursor.execute("SELECT total_photos FROM persons WHERE id = %s", (person_id,))
        result = cursor.fetchone()
        total_photos = result[0] if result else 0
        
        if total_photos >= 1:
            print(f"    ✓ Person total_photos trigger works (count: {total_photos})")
        else:
            print(f"    ✗ Person total_photos trigger failed (count: {total_photos})")
            return False
        
        print("\nTest 5: Test views...")
        
        # Test person_summary view
        cursor.execute("SELECT * FROM person_summary WHERE id = %s", (person_id,))
        person_summary = cursor.fetchone()
        
        if person_summary:
            print(f"    ✓ person_summary view works (found person: {person_summary[2]})")
        else:
            print("    ✗ person_summary view failed")
            return False
        
        # Test photo_summary view
        cursor.execute("SELECT * FROM photo_summary WHERE id = %s", (photo_id,))
        photo_summary = cursor.fetchone()
        
        if photo_summary:
            print(f"    ✓ photo_summary view works (faces: {photo_summary[6]}, persons: {photo_summary[7]})")
        else:
            print("    ✗ photo_summary view failed")
            return False
        
        print("\nTest 6: Test indexes...")
        
        # Check if indexes exist
        cursor.execute("""
            SELECT COUNT(*) 
            FROM information_schema.STATISTICS 
            WHERE TABLE_SCHEMA = %s 
            AND INDEX_NAME LIKE 'idx_%%'
        """, (DB_CONFIG['database'],))
        
        index_count = cursor.fetchone()[0]
        
        if index_count >= 20:
            print(f"    ✓ Indexes created ({index_count} indexes found)")
        else:
            print(f"    ✗ Missing indexes ({index_count} indexes found)")
            return False
        
        print("\nTest 7: Test data retrieval...")
        
        # Test complex query with joins
        cursor.execute("""
            SELECT p.name, ph.filename, fd.detection_method, fd.angle_estimate, fe.quality_score
            FROM persons p
            JOIN face_detections fd ON p.id = fd.person_id
            JOIN photos ph ON fd.photo_id = ph.id
            JOIN face_encodings fe ON fd.id = fe.face_detection_id
            WHERE p.id = %s
        """, (person_id,))
        
        results = cursor.fetchall()
        
        if results:
            print(f"    ✓ Complex join query works ({len(results)} results)")
            for result in results:
                print(f"      - {result[0]} in {result[1]} ({result[2]}, {result[3]}, quality: {result[4]:.2f})")
        else:
            print("    ✗ Complex join query failed")
            return False
        
        # Rollback test data (don't save test data)
        conn.rollback()
        cursor.close()
        conn.close()
        
        print("\n" + "=" * 70)
        print("✅ ALL MYSQL DATABASE SCHEMA TESTS PASSED")
        print("=" * 70)
        print("Database schema is ready for use!")
        print()
        print("Schema features verified:")
        print(f"  ✓ {len(expected_tables)} tables with proper structure")
        print(f"  ✓ {index_count} performance indexes")
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
        
    except mysql.connector.Error as e:
        print(f"\n❌ Database error: {e}")
        return False
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """
    Main function to test the MySQL database schema
    """
    
    print("\n🔍 Checking MySQL connection...")
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        print(f"✓ Connected to MySQL database: {DB_CONFIG['database']}")
        conn.close()
    except mysql.connector.Error as e:
        print(f"❌ Cannot connect to MySQL database: {e}")
        print("\nMake sure:")
        print("1. XAMPP is running")
        print("2. MySQL service is started")
        print("3. Database 'picme_db' exists")
        return
    
    print()
    success = test_mysql_schema()
    
    if success:
        print("\n🎉 Database schema tests completed successfully!")
    else:
        print("\n💥 Database schema tests failed!")

if __name__ == "__main__":
    main()
