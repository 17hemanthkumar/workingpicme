-- ============================================================================
-- Enhanced Face Detection System - MySQL Schema
-- Database: picme_db
-- ============================================================================
-- This script adds 6 new tables to your existing picme_db database
-- for the enhanced multi-angle face detection system
-- 
-- INSTRUCTIONS:
-- 1. Open phpMyAdmin in XAMPP
-- 2. Select the 'picme_db' database
-- 3. Go to the 'Import' tab
-- 4. Choose this file and click 'Go'
-- ============================================================================

USE picme_db;

-- ============================================================================
-- TABLE 1: photos - Photo metadata
-- ============================================================================
CREATE TABLE IF NOT EXISTS photos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    event_id VARCHAR(255) NOT NULL,
    filename VARCHAR(255) NOT NULL,
    filepath VARCHAR(500) NOT NULL,
    upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    has_faces BOOLEAN DEFAULT 0,
    processed BOOLEAN DEFAULT 0,
    face_count INT DEFAULT 0,
    file_size BIGINT,
    image_width INT,
    image_height INT,
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY unique_event_filename (event_id, filename),
    INDEX idx_event_id (event_id),
    INDEX idx_has_faces (has_faces),
    INDEX idx_processed (processed),
    INDEX idx_upload_date (upload_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================================
-- TABLE 2: persons - Person registry
-- ============================================================================
CREATE TABLE IF NOT EXISTS persons (
    id INT AUTO_INCREMENT PRIMARY KEY,
    person_uuid VARCHAR(36) UNIQUE NOT NULL,
    name VARCHAR(255),
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_seen TIMESTAMP NULL,
    total_photos INT DEFAULT 0,
    confidence_score DECIMAL(5,4) DEFAULT 0.0,
    is_verified BOOLEAN DEFAULT 0,
    notes TEXT,
    updated_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_person_uuid (person_uuid),
    INDEX idx_name (name),
    INDEX idx_last_seen (last_seen)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================================
-- TABLE 3: face_detections - Detected faces with angles and quality
-- ============================================================================
CREATE TABLE IF NOT EXISTS face_detections (
    id INT AUTO_INCREMENT PRIMARY KEY,
    photo_id INT NOT NULL,
    person_id INT,
    face_bbox TEXT NOT NULL,
    face_crop_path VARCHAR(500),
    detection_confidence DECIMAL(5,4),
    detection_method VARCHAR(50),
    angle_estimate VARCHAR(50),
    quality_score DECIMAL(5,4),
    blur_score DECIMAL(5,4),
    lighting_score DECIMAL(5,4),
    size_score DECIMAL(5,4),
    is_primary BOOLEAN DEFAULT 0,
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (photo_id) REFERENCES photos(id) ON DELETE CASCADE,
    FOREIGN KEY (person_id) REFERENCES persons(id) ON DELETE SET NULL,
    INDEX idx_photo_id (photo_id),
    INDEX idx_person_id (person_id),
    INDEX idx_angle_estimate (angle_estimate),
    INDEX idx_quality_score (quality_score),
    INDEX idx_detection_method (detection_method),
    INDEX idx_is_primary (is_primary)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================================
-- TABLE 4: face_encodings - 128D encodings per angle
-- ============================================================================
CREATE TABLE IF NOT EXISTS face_encodings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    face_detection_id INT NOT NULL,
    person_id INT NOT NULL,
    encoding_vector BLOB NOT NULL,
    angle VARCHAR(50) NOT NULL,
    quality_score DECIMAL(5,4) DEFAULT 0.0,
    is_primary BOOLEAN DEFAULT 0,
    encoding_method VARCHAR(50) DEFAULT 'face_recognition',
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (face_detection_id) REFERENCES face_detections(id) ON DELETE CASCADE,
    FOREIGN KEY (person_id) REFERENCES persons(id) ON DELETE CASCADE,
    INDEX idx_person_id (person_id),
    INDEX idx_angle (angle),
    INDEX idx_quality_score (quality_score),
    INDEX idx_is_primary (is_primary),
    INDEX idx_face_detection_id (face_detection_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================================
-- TABLE 5: facial_features - Deep feature analysis
-- ============================================================================
CREATE TABLE IF NOT EXISTS facial_features (
    id INT AUTO_INCREMENT PRIMARY KEY,
    face_detection_id INT NOT NULL,
    landmarks BLOB,
    eye_distance DECIMAL(10,4),
    nose_width DECIMAL(10,4),
    nose_height DECIMAL(10,4),
    jaw_width DECIMAL(10,4),
    mouth_width DECIMAL(10,4),
    face_width DECIMAL(10,4),
    face_height DECIMAL(10,4),
    has_facial_hair BOOLEAN DEFAULT 0,
    facial_hair_type VARCHAR(50),
    glasses BOOLEAN DEFAULT 0,
    age_estimate INT,
    gender_estimate VARCHAR(20),
    emotion_estimate VARCHAR(50),
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (face_detection_id) REFERENCES face_detections(id) ON DELETE CASCADE,
    INDEX idx_face_detection_id (face_detection_id),
    INDEX idx_glasses (glasses),
    INDEX idx_has_facial_hair (has_facial_hair),
    INDEX idx_age_estimate (age_estimate),
    INDEX idx_gender_estimate (gender_estimate)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================================
-- TABLE 6: person_photos - Photo associations
-- ============================================================================
CREATE TABLE IF NOT EXISTS person_photos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    person_id INT NOT NULL,
    photo_id INT NOT NULL,
    is_group_photo BOOLEAN DEFAULT 0,
    face_count_in_photo INT DEFAULT 1,
    match_confidence DECIMAL(5,4),
    face_detection_id INT,
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (person_id) REFERENCES persons(id) ON DELETE CASCADE,
    FOREIGN KEY (photo_id) REFERENCES photos(id) ON DELETE CASCADE,
    FOREIGN KEY (face_detection_id) REFERENCES face_detections(id) ON DELETE SET NULL,
    UNIQUE KEY unique_person_photo (person_id, photo_id),
    INDEX idx_person_id (person_id),
    INDEX idx_photo_id (photo_id),
    INDEX idx_is_group_photo (is_group_photo),
    INDEX idx_match_confidence (match_confidence)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================================
-- TRIGGERS - Automatic updates
-- ============================================================================

-- Trigger: Update person total_photos count when person_photos is inserted
DELIMITER $$
CREATE TRIGGER IF NOT EXISTS update_person_photo_count_insert
AFTER INSERT ON person_photos
FOR EACH ROW
BEGIN
    UPDATE persons 
    SET total_photos = (
        SELECT COUNT(*) FROM person_photos 
        WHERE person_id = NEW.person_id
    ),
    last_seen = CURRENT_TIMESTAMP,
    updated_date = CURRENT_TIMESTAMP
    WHERE id = NEW.person_id;
END$$
DELIMITER ;

-- Trigger: Update person total_photos count when person_photos is deleted
DELIMITER $$
CREATE TRIGGER IF NOT EXISTS update_person_photo_count_delete
AFTER DELETE ON person_photos
FOR EACH ROW
BEGIN
    UPDATE persons 
    SET total_photos = (
        SELECT COUNT(*) FROM person_photos 
        WHERE person_id = OLD.person_id
    ),
    updated_date = CURRENT_TIMESTAMP
    WHERE id = OLD.person_id;
END$$
DELIMITER ;

-- Trigger: Update photo face_count when face_detections is inserted
DELIMITER $$
CREATE TRIGGER IF NOT EXISTS update_photo_face_count_insert
AFTER INSERT ON face_detections
FOR EACH ROW
BEGIN
    UPDATE photos 
    SET face_count = (
        SELECT COUNT(*) FROM face_detections 
        WHERE photo_id = NEW.photo_id
    ),
    has_faces = 1,
    updated_date = CURRENT_TIMESTAMP
    WHERE id = NEW.photo_id;
END$$
DELIMITER ;

-- Trigger: Update photo face_count when face_detections is deleted
DELIMITER $$
CREATE TRIGGER IF NOT EXISTS update_photo_face_count_delete
AFTER DELETE ON face_detections
FOR EACH ROW
BEGIN
    DECLARE face_count_val INT;
    
    SELECT COUNT(*) INTO face_count_val
    FROM face_detections 
    WHERE photo_id = OLD.photo_id;
    
    UPDATE photos 
    SET face_count = face_count_val,
    has_faces = IF(face_count_val > 0, 1, 0),
    updated_date = CURRENT_TIMESTAMP
    WHERE id = OLD.photo_id;
END$$
DELIMITER ;

-- ============================================================================
-- VIEWS - Summary data
-- ============================================================================

-- View: Person summary with photo counts
CREATE OR REPLACE VIEW person_summary AS
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
GROUP BY p.id, p.person_uuid, p.name, p.total_photos, p.confidence_score, p.last_seen, p.created_date;

-- View: Photo summary with face information
CREATE OR REPLACE VIEW photo_summary AS
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
GROUP BY ph.id, ph.event_id, ph.filename, ph.face_count, ph.processed, ph.upload_date;

-- ============================================================================
-- VERIFICATION QUERIES
-- ============================================================================
-- Run these queries after import to verify the schema was created successfully

-- Check tables
SELECT 'Tables Created:' as Status;
SELECT TABLE_NAME, TABLE_ROWS, CREATE_TIME 
FROM information_schema.TABLES 
WHERE TABLE_SCHEMA = 'picme_db' 
AND TABLE_NAME IN ('photos', 'persons', 'face_detections', 'face_encodings', 'facial_features', 'person_photos')
ORDER BY TABLE_NAME;

-- Check indexes
SELECT 'Indexes Created:' as Status;
SELECT TABLE_NAME, INDEX_NAME, COLUMN_NAME 
FROM information_schema.STATISTICS 
WHERE TABLE_SCHEMA = 'picme_db' 
AND TABLE_NAME IN ('photos', 'persons', 'face_detections', 'face_encodings', 'facial_features', 'person_photos')
AND INDEX_NAME LIKE 'idx_%'
ORDER BY TABLE_NAME, INDEX_NAME;

-- Check triggers
SELECT 'Triggers Created:' as Status;
SELECT TRIGGER_NAME, EVENT_MANIPULATION, EVENT_OBJECT_TABLE 
FROM information_schema.TRIGGERS 
WHERE TRIGGER_SCHEMA = 'picme_db'
ORDER BY TRIGGER_NAME;

-- Check views
SELECT 'Views Created:' as Status;
SELECT TABLE_NAME 
FROM information_schema.VIEWS 
WHERE TABLE_SCHEMA = 'picme_db'
ORDER BY TABLE_NAME;

-- ============================================================================
-- SCHEMA CREATION COMPLETE
-- ============================================================================
-- Summary:
-- ✓ 6 tables created (photos, persons, face_detections, face_encodings, facial_features, person_photos)
-- ✓ 27 indexes created for performance
-- ✓ 4 triggers created for automatic updates
-- ✓ 2 views created for summary data
-- ✓ Foreign key constraints enabled
-- 
-- Next steps:
-- 1. Verify the tables were created by running the verification queries above
-- 2. Test the schema with the Python test script
-- 3. Continue with Task 1.2: Enhanced Face Detector
-- ============================================================================
