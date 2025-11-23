#!/usr/bin/env python3
"""
Enhanced Face Detection Database Schema

Creates the complete database schema for the enhanced multi-angle face detection system.
Includes all tables, indexes, and constraints as specified in the design document.

Tables created:
- photos: Photo metadata
- persons: Person registry
- face_detections: Detected faces with angles
- face_encodings: 128D encodings per angle
- facial_features: Deep feature analysis
- person_photos: Photo associations
"""

import sqlite3
import os
import sys
from datetime import datetime

def create_enhanced_schema(db_path='database.db'):
    """
    Create the enhanced face detection database schema
    
    Args:
        db_path (str): Path to the database file
    
    Returns:
        bool: True if successful, False otherwise
    """
    
    print("=" * 70)
    print("ENHANCED FACE DETECTION - DATABASE SCHEMA CREATION")
    print("=" * 70)
    print(f"Database: {db_path}")
    print(f"Timestamp: {datetime.now()}")
    print()
    
    try:
        # Connect to database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Enable foreign key constraints
        cursor.execute("PRAGMA foreign_keys = ON")
        
        print("Step 1: Creating core tables...")
        
        # 1. Photos table - Photo metadata
        print("  Creating 'photos' table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS photos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_id TEXT NOT NULL,
                filename TEXT NOT NULL,
                filepath TEXT NOT NULL,
                upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                has_faces BOOLEAN DEFAULT 0,
                processed BOOLEAN DEFAULT 0,
                face_count INTEGER DEFAULT 0,
                file_size INTEGER,
                image_width INTEGER,
                image_height INTEGER,
                created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(event_id, filename)
            )
        """)
        
        # 2. Persons table - Person registry
        print("  Creating 'persons' table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS persons (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                person_uuid TEXT UNIQUE NOT NULL,
                name TEXT,
                created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_seen TIMESTAMP,
                total_photos INTEGER DEFAULT 0,
                confidence_score REAL DEFAULT 0.0,
                is_verified BOOLEAN DEFAULT 0,
                notes TEXT,
                updated_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # 3. Face detections table - Detected faces with angles
        print("  Creating 'face_detections' table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS face_detections (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                photo_id INTEGER NOT NULL,
                person_id INTEGER,
                face_bbox TEXT NOT NULL,
                face_crop_path TEXT,
                detection_confidence REAL,
                detection_method TEXT,
                angle_estimate TEXT,
                quality_score REAL,
                blur_score REAL,
                lighting_score REAL,
                size_score REAL,
                is_primary BOOLEAN DEFAULT 0,
                created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (photo_id) REFERENCES photos(id) ON DELETE CASCADE,
                FOREIGN KEY (person_id) REFERENCES persons(id) ON DELETE SET NULL
            )
        """)
        
        # 4. Face encodings table - 128D encodings per angle
        print("  Creating 'face_encodings' table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS face_encodings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                face_detection_id INTEGER NOT NULL,
                person_id INTEGER NOT NULL,
                encoding_vector BLOB NOT NULL,
                angle TEXT NOT NULL,
                quality_score REAL DEFAULT 0.0,
                is_primary BOOLEAN DEFAULT 0,
                encoding_method TEXT DEFAULT 'face_recognition',
                created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (face_detection_id) REFERENCES face_detections(id) ON DELETE CASCADE,
                FOREIGN KEY (person_id) REFERENCES persons(id) ON DELETE CASCADE
            )
        """)
        
        # 5. Facial features table - Deep feature analysis
        print("  Creating 'facial_features' table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS facial_features (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                face_detection_id INTEGER NOT NULL,
                landmarks BLOB,
                eye_distance REAL,
                nose_width REAL,
                nose_height REAL,
                jaw_width REAL,
                mouth_width REAL,
                face_width REAL,
                face_height REAL,
                has_facial_hair BOOLEAN DEFAULT 0,
                facial_hair_type TEXT,
                glasses BOOLEAN DEFAULT 0,
                age_estimate INTEGER,
                gender_estimate TEXT,
                emotion_estimate TEXT,
                created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (face_detection_id) REFERENCES face_detections(id) ON DELETE CASCADE
            )
        """)
        
        # 6. Person photos table - Photo associations
        print("  Creating 'person_photos' table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS person_photos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                person_id INTEGER NOT NULL,
                photo_id INTEGER NOT NULL,
                is_group_photo BOOLEAN DEFAULT 0,
                face_count_in_photo INTEGER DEFAULT 1,
                match_confidence REAL,
                face_detection_id INTEGER,
                created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (person_id) REFERENCES persons(id) ON DELETE CASCADE,
                FOREIGN KEY (photo_id) REFERENCES photos(id) ON DELETE CASCADE,
                FOREIGN KEY (face_detection_id) REFERENCES face_detections(id) ON DELETE SET NULL,
                UNIQUE(person_id, photo_id)
            )
        """)
        
        print("\nStep 2: Creating performance indexes...")
        
        # Performance indexes
        indexes = [
            # Photos table indexes
            "CREATE INDEX IF NOT EXISTS idx_photos_event ON photos(event_id)",
            "CREATE INDEX IF NOT EXISTS idx_photos_has_faces ON photos(has_faces)",
            "CREATE INDEX IF NOT EXISTS idx_photos_processed ON photos(processed)",
            "CREATE INDEX IF NOT EXISTS idx_photos_upload_date ON photos(upload_date)",
            
            # Persons table indexes
            "CREATE INDEX IF NOT EXISTS idx_persons_uuid ON persons(person_uuid)",
            "CREATE INDEX IF NOT EXISTS idx_persons_name ON persons(name)",
            "CREATE INDEX IF NOT EXISTS idx_persons_last_seen ON persons(last_seen)",
            
            # Face detections table indexes
            "CREATE INDEX IF NOT EXISTS idx_face_detections_photo ON face_detections(photo_id)",
            "CREATE INDEX IF NOT EXISTS idx_face_detections_person ON face_detections(person_id)",
            "CREATE INDEX IF NOT EXISTS idx_face_detections_angle ON face_detections(angle_estimate)",
            "CREATE INDEX IF NOT EXISTS idx_face_detections_quality ON face_detections(quality_score)",
            "CREATE INDEX IF NOT EXISTS idx_face_detections_method ON face_detections(detection_method)",
            "CREATE INDEX IF NOT EXISTS idx_face_detections_primary ON face_detections(is_primary)",
            
            # Face encodings table indexes
            "CREATE INDEX IF NOT EXISTS idx_face_encodings_person ON face_encodings(person_id)",
            "CREATE INDEX IF NOT EXISTS idx_face_encodings_angle ON face_encodings(angle)",
            "CREATE INDEX IF NOT EXISTS idx_face_encodings_quality ON face_encodings(quality_score)",
            "CREATE INDEX IF NOT EXISTS idx_face_encodings_primary ON face_encodings(is_primary)",
            "CREATE INDEX IF NOT EXISTS idx_face_encodings_detection ON face_encodings(face_detection_id)",
            
            # Facial features table indexes
            "CREATE INDEX IF NOT EXISTS idx_facial_features_detection ON facial_features(face_detection_id)",
            "CREATE INDEX IF NOT EXISTS idx_facial_features_glasses ON facial_features(glasses)",
            "CREATE INDEX IF NOT EXISTS idx_facial_features_facial_hair ON facial_features(has_facial_hair)",
            "CREATE INDEX IF NOT EXISTS idx_facial_features_age ON facial_features(age_estimate)",
            "CREATE INDEX IF NOT EXISTS idx_facial_features_gender ON facial_features(gender_estimate)",
            
            # Person photos table indexes
            "CREATE INDEX IF NOT EXISTS idx_person_photos_person ON person_photos(person_id)",
            "CREATE INDEX IF NOT EXISTS idx_person_photos_photo ON person_photos(photo_id)",
            "CREATE INDEX IF NOT EXISTS idx_person_photos_group ON person_photos(is_group_photo)",
            "CREATE INDEX IF NOT EXISTS idx_person_photos_confidence ON person_photos(match_confidence)",
        ]
        
        for i, index_sql in enumerate(indexes, 1):
            print(f"  Creating index {i}/{len(indexes)}...")
            cursor.execute(index_sql)
        
        print("\nStep 3: Creating database triggers...")
        
        # Trigger to update persons.total_photos when person_photos changes
        cursor.execute("""
            CREATE TRIGGER IF NOT EXISTS update_person_photo_count_insert
            AFTER INSERT ON person_photos
            BEGIN
                UPDATE persons 
                SET total_photos = (
                    SELECT COUNT(*) FROM person_photos 
                    WHERE person_id = NEW.person_id
                ),
                last_seen = CURRENT_TIMESTAMP,
                updated_date = CURRENT_TIMESTAMP
                WHERE id = NEW.person_id;
            END
        """)
        
        cursor.execute("""
            CREATE TRIGGER IF NOT EXISTS update_person_photo_count_delete
            AFTER DELETE ON person_photos
            BEGIN
                UPDATE persons 
                SET total_photos = (
                    SELECT COUNT(*) FROM person_photos 
                    WHERE person_id = OLD.person_id
                ),
                updated_date = CURRENT_TIMESTAMP
                WHERE id = OLD.person_id;
            END
        """)
        
        # Trigger to update photos.face_count when face_detections changes
        cursor.execute("""
            CREATE TRIGGER IF NOT EXISTS update_photo_face_count_insert
            AFTER INSERT ON face_detections
            BEGIN
                UPDATE photos 
                SET face_count = (
                    SELECT COUNT(*) FROM face_detections 
                    WHERE photo_id = NEW.photo_id
                ),
                has_faces = 1,
                updated_date = CURRENT_TIMESTAMP
                WHERE id = NEW.photo_id;
            END
        """)
        
        cursor.execute("""
            CREATE TRIGGER IF NOT EXISTS update_photo_face_count_delete
            AFTER DELETE ON face_detections
            BEGIN
                UPDATE photos 
                SET face_count = (
                    SELECT COUNT(*) FROM face_detections 
                    WHERE photo_id = OLD.photo_id
                ),
                has_faces = CASE WHEN (
                    SELECT COUNT(*) FROM face_detections 
                    WHERE photo_id = OLD.photo_id
                ) > 0 THEN 1 ELSE 0 END,
                updated_date = CURRENT_TIMESTAMP
                WHERE id = OLD.photo_id;
            END
        """)
        
        print("\nStep 4: Creating database views...")
        
        # View for person summary with photo counts
        cursor.execute("""
            CREATE VIEW IF NOT EXISTS person_summary AS
            SELECT 
                p.id,
                p.person_uuid,
                p.name,
                p.total_photos,
                p.confidence_score,
                p.last_seen,
                p.created_date,
                COUNT(DISTINCT pp.photo_id) as actual_photo_count,
                COUNT(DISTINCT CASE WHEN pp.is_group_photo = 1 THEN pp.photo_id END) as group_photo_count,
                COUNT(DISTINCT CASE WHEN pp.is_group_photo = 0 THEN pp.photo_id END) as individual_photo_count,
                AVG(pp.match_confidence) as avg_match_confidence
            FROM persons p
            LEFT JOIN person_photos pp ON p.id = pp.person_id
            GROUP BY p.id, p.person_uuid, p.name, p.total_photos, p.confidence_score, p.last_seen, p.created_date
        """)
        
        # View for photo summary with face information
        cursor.execute("""
            CREATE VIEW IF NOT EXISTS photo_summary AS
            SELECT 
                ph.id,
                ph.event_id,
                ph.filename,
                ph.face_count,
                ph.processed,
                ph.upload_date,
                COUNT(DISTINCT fd.id) as actual_face_count,
                COUNT(DISTINCT fd.person_id) as unique_persons,
                AVG(fd.quality_score) as avg_quality_score,
                GROUP_CONCAT(DISTINCT fd.detection_method) as detection_methods,
                GROUP_CONCAT(DISTINCT fd.angle_estimate) as angles_detected
            FROM photos ph
            LEFT JOIN face_detections fd ON ph.id = fd.photo_id
            GROUP BY ph.id, ph.event_id, ph.filename, ph.face_count, ph.processed, ph.upload_date
        """)
        
        # Commit all changes
        conn.commit()
        
        print("\nStep 5: Verifying schema creation...")
        
        # Verify tables were created
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        tables = [row[0] for row in cursor.fetchall()]
        
        expected_tables = ['photos', 'persons', 'face_detections', 'face_encodings', 'facial_features', 'person_photos']
        
        print(f"  Expected tables: {len(expected_tables)}")
        print(f"  Created tables: {len([t for t in tables if t in expected_tables])}")
        
        for table in expected_tables:
            if table in tables:
                print(f"  ✓ {table}")
            else:
                print(f"  ✗ {table} - MISSING!")
                return False
        
        # Verify indexes were created
        cursor.execute("SELECT name FROM sqlite_master WHERE type='index' AND name LIKE 'idx_%' ORDER BY name")
        created_indexes = [row[0] for row in cursor.fetchall()]
        print(f"  Created indexes: {len(created_indexes)}")
        
        # Verify triggers were created
        cursor.execute("SELECT name FROM sqlite_master WHERE type='trigger' ORDER BY name")
        created_triggers = [row[0] for row in cursor.fetchall()]
        print(f"  Created triggers: {len(created_triggers)}")
        
        # Verify views were created
        cursor.execute("SELECT name FROM sqlite_master WHERE type='view' ORDER BY name")
        created_views = [row[0] for row in cursor.fetchall()]
        print(f"  Created views: {len(created_views)}")
        
        conn.close()
        
        print("\n" + "=" * 70)
        print("✅ DATABASE SCHEMA CREATION SUCCESSFUL")
        print("=" * 70)
        print(f"Database file: {os.path.abspath(db_path)}")
        print(f"File size: {os.path.getsize(db_path):,} bytes")
        print(f"Tables created: {len(expected_tables)}")
        print(f"Indexes created: {len(created_indexes)}")
        print(f"Triggers created: {len(created_triggers)}")
        print(f"Views created: {len(created_views)}")
        print()
        print("Next steps:")
        print("1. Run: python test_enhanced_schema.py")
        print("2. Continue with Task 1.2: Enhanced Face Detector")
        print("=" * 70)
        
        return True
        
    except sqlite3.Error as e:
        print(f"\n❌ Database error: {e}")
        return False
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """
    Main function to create the database schema
    """
    
    # Check if database already exists
    db_path = 'database.db'
    
    if os.path.exists(db_path):
        # Check if it has tables
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        conn.close()
        
        if tables:
            response = input(f"Database '{db_path}' already exists with tables. Recreate? (y/N): ")
            if response.lower() != 'y':
                print("Schema creation cancelled.")
                return
            
            # Backup existing database
            backup_path = f"database_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
            os.rename(db_path, backup_path)
            print(f"Existing database backed up to: {backup_path}")
    
    # Create the schema
    success = create_enhanced_schema(db_path)
    
    if success:
        print("\n🎉 Enhanced face detection database schema created successfully!")
        sys.exit(0)
    else:
        print("\n💥 Schema creation failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
