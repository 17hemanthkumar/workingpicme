#!/usr/bin/env python3
"""
Multi-Angle Face Database Manager

Manages database operations for the Enhanced Multi-Angle Face Detection System.
Handles person management, encoding storage, and photo associations with MySQL support.

Features:
- Person CRUD operations
- Multi-angle encoding storage (up to 5 angles per person)
- Photo association management
- Transaction handling
- Query optimization
"""

import mysql.connector
from mysql.connector import Error
import numpy as np
import json
import uuid
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from contextlib import contextmanager

class MultiAngleFaceDatabase:
    """
    Database manager for multi-angle face detection system
    """
    
    def __init__(self, host='localhost', user='root', password='', database='picme_db'):
        """
        Initialize database connection
        
        Args:
            host: MySQL host
            user: MySQL user
            password: MySQL password
            database: Database name
        """
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.connection = None
        
        print("=" * 70)
        print("INITIALIZING MULTI-ANGLE FACE DATABASE")
        print("=" * 70)
        
        # Connect to database
        self._connect()
        
        print("✓ Multi-Angle Face Database initialized successfully")
        print("=" * 70)
        print()
    
    def _connect(self):
        """Establish database connection"""
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database,
                autocommit=False  # Manual transaction control
            )
            print(f"✓ Connected to MySQL database: {self.database}")
        except Error as e:
            print(f"✗ Database connection error: {e}")
            raise
    
    @contextmanager
    def get_cursor(self, dictionary=True):
        """
        Context manager for database cursor
        
        Args:
            dictionary: Return results as dictionaries
            
        Yields:
            MySQL cursor
        """
        cursor = self.connection.cursor(dictionary=dictionary)
        try:
            yield cursor
        finally:
            cursor.close()
    
    def commit(self):
        """Commit current transaction"""
        if self.connection:
            self.connection.commit()
    
    def rollback(self):
        """Rollback current transaction"""
        if self.connection:
            self.connection.rollback()
    
    def close(self):
        """Close database connection"""
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print("✓ Database connection closed")
    
    # ========================================================================
    # PERSON MANAGEMENT
    # ========================================================================
    
    def add_person(self, person_uuid: Optional[str] = None, name: Optional[str] = None) -> int:
        """
        Create new person record
        
        Args:
            person_uuid: Unique identifier (generated if not provided)
            name: Optional person name
            
        Returns:
            Person ID
        """
        if person_uuid is None:
            person_uuid = str(uuid.uuid4())
        
        query = """
            INSERT INTO persons (person_uuid, name, confidence_score)
            VALUES (%s, %s, 0.0)
        """
        
        try:
            with self.get_cursor() as cursor:
                cursor.execute(query, (person_uuid, name))
                self.commit()
                person_id = cursor.lastrowid
                print(f"✓ Created person: ID={person_id}, UUID={person_uuid}")
                return person_id
        except Error as e:
            self.rollback()
            print(f"✗ Error creating person: {e}")
            raise
    
    def get_person(self, person_id: int) -> Optional[Dict]:
        """
        Get person details
        
        Args:
            person_id: Person identifier
            
        Returns:
            Person record or None
        """
        query = """
            SELECT * FROM persons WHERE id = %s
        """
        
        try:
            with self.get_cursor() as cursor:
                cursor.execute(query, (person_id,))
                return cursor.fetchone()
        except Error as e:
            print(f"✗ Error getting person: {e}")
            return None
    
    def get_person_by_uuid(self, person_uuid: str) -> Optional[Dict]:
        """
        Get person by UUID
        
        Args:
            person_uuid: Person UUID
            
        Returns:
            Person record or None
        """
        query = """
            SELECT * FROM persons WHERE person_uuid = %s
        """
        
        try:
            with self.get_cursor() as cursor:
                cursor.execute(query, (person_uuid,))
                return cursor.fetchone()
        except Error as e:
            print(f"✗ Error getting person by UUID: {e}")
            return None
    
    def update_person(self, person_id: int, name: Optional[str] = None, 
                     confidence_score: Optional[float] = None) -> bool:
        """
        Update person record
        
        Args:
            person_id: Person identifier
            name: New name (optional)
            confidence_score: New confidence score (optional)
            
        Returns:
            Success status
        """
        updates = []
        params = []
        
        if name is not None:
            updates.append("name = %s")
            params.append(name)
        
        if confidence_score is not None:
            updates.append("confidence_score = %s")
            params.append(confidence_score)
        
        if not updates:
            return True
        
        params.append(person_id)
        query = f"""
            UPDATE persons 
            SET {', '.join(updates)}, updated_date = CURRENT_TIMESTAMP
            WHERE id = %s
        """
        
        try:
            with self.get_cursor() as cursor:
                cursor.execute(query, params)
                self.commit()
                return cursor.rowcount > 0
        except Error as e:
            self.rollback()
            print(f"✗ Error updating person: {e}")
            return False
    
    def delete_person(self, person_id: int) -> bool:
        """
        Delete person record (cascades to encodings and associations)
        
        Args:
            person_id: Person identifier
            
        Returns:
            Success status
        """
        query = """
            DELETE FROM persons WHERE id = %s
        """
        
        try:
            with self.get_cursor() as cursor:
                cursor.execute(query, (person_id,))
                self.commit()
                print(f"✓ Deleted person: ID={person_id}")
                return cursor.rowcount > 0
        except Error as e:
            self.rollback()
            print(f"✗ Error deleting person: {e}")
            return False
    
    def get_all_persons(self, limit: int = 100, offset: int = 0) -> List[Dict]:
        """
        Get all persons with pagination
        
        Args:
            limit: Maximum number of records
            offset: Starting offset
            
        Returns:
            List of person records
        """
        query = """
            SELECT * FROM persons 
            ORDER BY last_seen DESC, created_date DESC
            LIMIT %s OFFSET %s
        """
        
        try:
            with self.get_cursor() as cursor:
                cursor.execute(query, (limit, offset))
                return cursor.fetchall()
        except Error as e:
            print(f"✗ Error getting persons: {e}")
            return []
    
    # ========================================================================
    # ENCODING STORAGE
    # ========================================================================
    
    def add_face_encoding(self, person_id: int, encoding: np.ndarray, angle: str,
                         quality_score: float, face_detection_id: int) -> int:
        """
        Store face encoding for specific angle
        
        Args:
            person_id: Person identifier
            encoding: 128D encoding vector
            angle: Angle classification
            quality_score: Quality score (0-1)
            face_detection_id: Associated detection ID
            
        Returns:
            Encoding ID
        """
        # Convert numpy array to bytes
        encoding_bytes = encoding.tobytes()
        
        # Check if we need to replace an existing encoding
        existing_count = self._get_encoding_count(person_id)
        
        if existing_count >= 5:
            # Check if this angle already exists
            existing_angle = self._get_encoding_by_angle(person_id, angle)
            
            if existing_angle:
                # Replace if new quality is better
                if quality_score > existing_angle['quality_score']:
                    self._delete_encoding(existing_angle['id'])
                else:
                    print(f"⚠ Skipping encoding: existing angle has better quality")
                    return existing_angle['id']
            else:
                # Replace lowest quality encoding
                lowest = self._get_lowest_quality_encoding(person_id)
                if lowest and quality_score > lowest['quality_score']:
                    self._delete_encoding(lowest['id'])
                else:
                    print(f"⚠ Skipping encoding: quality not high enough to replace")
                    return -1
        
        query = """
            INSERT INTO face_encodings 
            (face_detection_id, person_id, encoding_vector, angle, quality_score, is_primary)
            VALUES (%s, %s, %s, %s, %s, 0)
        """
        
        try:
            with self.get_cursor() as cursor:
                cursor.execute(query, (face_detection_id, person_id, encoding_bytes, 
                                      angle, quality_score))
                self.commit()
                encoding_id = cursor.lastrowid
                
                # Update primary encoding if this is the best quality
                self._update_primary_encoding(person_id)
                
                print(f"✓ Stored encoding: ID={encoding_id}, angle={angle}, quality={quality_score:.3f}")
                return encoding_id
        except Error as e:
            self.rollback()
            print(f"✗ Error storing encoding: {e}")
            raise
    
    def get_person_encodings(self, person_id: int, angle: Optional[str] = None) -> List[Dict]:
        """
        Retrieve encodings for a person
        
        Args:
            person_id: Person identifier
            angle: Optional angle filter
            
        Returns:
            List of encoding records
        """
        if angle:
            query = """
                SELECT * FROM face_encodings 
                WHERE person_id = %s AND angle = %s
                ORDER BY quality_score DESC
            """
            params = (person_id, angle)
        else:
            query = """
                SELECT * FROM face_encodings 
                WHERE person_id = %s
                ORDER BY is_primary DESC, quality_score DESC
            """
            params = (person_id,)
        
        try:
            with self.get_cursor() as cursor:
                cursor.execute(query, params)
                encodings = cursor.fetchall()
                
                # Convert encoding_vector bytes back to numpy array
                for enc in encodings:
                    if enc['encoding_vector']:
                        enc['encoding_array'] = np.frombuffer(enc['encoding_vector'], dtype=np.float64)
                
                return encodings
        except Error as e:
            print(f"✗ Error getting encodings: {e}")
            return []
    
    def get_best_encoding(self, person_id: int) -> Optional[Dict]:
        """
        Get best quality encoding (primary encoding)
        
        Args:
            person_id: Person identifier
            
        Returns:
            Best encoding record or None
        """
        query = """
            SELECT * FROM face_encodings 
            WHERE person_id = %s AND is_primary = 1
            LIMIT 1
        """
        
        try:
            with self.get_cursor() as cursor:
                cursor.execute(query, (person_id,))
                encoding = cursor.fetchone()
                
                if encoding and encoding['encoding_vector']:
                    encoding['encoding_array'] = np.frombuffer(encoding['encoding_vector'], dtype=np.float64)
                
                return encoding
        except Error as e:
            print(f"✗ Error getting best encoding: {e}")
            return None
    
    def get_all_encodings(self) -> List[Dict]:
        """
        Get all encodings from database (for matching)
        
        Returns:
            List of all encoding records
        """
        query = """
            SELECT * FROM face_encodings 
            ORDER BY person_id, is_primary DESC, quality_score DESC
        """
        
        try:
            with self.get_cursor() as cursor:
                cursor.execute(query)
                encodings = cursor.fetchall()
                
                # Convert encoding_vector bytes back to numpy array
                for enc in encodings:
                    if enc['encoding_vector']:
                        enc['encoding_array'] = np.frombuffer(enc['encoding_vector'], dtype=np.float64)
                
                return encodings
        except Error as e:
            print(f"✗ Error getting all encodings: {e}")
            return []
    
    def _get_encoding_count(self, person_id: int) -> int:
        """Get number of encodings for a person"""
        query = "SELECT COUNT(*) as count FROM face_encodings WHERE person_id = %s"
        
        with self.get_cursor() as cursor:
            cursor.execute(query, (person_id,))
            result = cursor.fetchone()
            return result['count'] if result else 0
    
    def _get_encoding_by_angle(self, person_id: int, angle: str) -> Optional[Dict]:
        """Get encoding for specific angle"""
        query = """
            SELECT * FROM face_encodings 
            WHERE person_id = %s AND angle = %s
            LIMIT 1
        """
        
        with self.get_cursor() as cursor:
            cursor.execute(query, (person_id, angle))
            return cursor.fetchone()
    
    def _get_lowest_quality_encoding(self, person_id: int) -> Optional[Dict]:
        """Get lowest quality encoding for a person"""
        query = """
            SELECT * FROM face_encodings 
            WHERE person_id = %s
            ORDER BY quality_score ASC
            LIMIT 1
        """
        
        with self.get_cursor() as cursor:
            cursor.execute(query, (person_id,))
            return cursor.fetchone()
    
    def _delete_encoding(self, encoding_id: int):
        """Delete an encoding"""
        query = "DELETE FROM face_encodings WHERE id = %s"
        
        with self.get_cursor() as cursor:
            cursor.execute(query, (encoding_id,))
            self.commit()
    
    def _update_primary_encoding(self, person_id: int):
        """Update primary encoding to highest quality"""
        # Clear all primary flags
        query1 = """
            UPDATE face_encodings 
            SET is_primary = 0 
            WHERE person_id = %s
        """
        
        # Set highest quality as primary
        query2 = """
            UPDATE face_encodings 
            SET is_primary = 1 
            WHERE id = (
                SELECT id FROM (
                    SELECT id FROM face_encodings 
                    WHERE person_id = %s
                    ORDER BY quality_score DESC
                    LIMIT 1
                ) AS temp
            )
        """
        
        with self.get_cursor() as cursor:
            cursor.execute(query1, (person_id,))
            cursor.execute(query2, (person_id,))
            self.commit()
    
    # ========================================================================
    # PHOTO ASSOCIATION
    # ========================================================================
    
    def associate_photo(self, person_id: int, photo_id: int, is_group: bool,
                       confidence: float, face_detection_id: Optional[int] = None) -> int:
        """
        Associate photo with person
        
        Args:
            person_id: Person identifier
            photo_id: Photo identifier
            is_group: Whether photo contains multiple faces
            confidence: Match confidence score
            face_detection_id: Associated face detection ID
            
        Returns:
            Association ID
        """
        # Get face count from photo
        face_count = self._get_photo_face_count(photo_id)
        
        query = """
            INSERT INTO person_photos 
            (person_id, photo_id, is_group_photo, face_count_in_photo, 
             match_confidence, face_detection_id)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
            match_confidence = VALUES(match_confidence),
            face_detection_id = VALUES(face_detection_id)
        """
        
        try:
            with self.get_cursor() as cursor:
                cursor.execute(query, (person_id, photo_id, is_group, face_count,
                                      confidence, face_detection_id))
                self.commit()
                assoc_id = cursor.lastrowid
                print(f"✓ Associated photo: person={person_id}, photo={photo_id}, confidence={confidence:.3f}")
                return assoc_id
        except Error as e:
            self.rollback()
            print(f"✗ Error associating photo: {e}")
            raise
    
    def get_person_photos(self, person_id: int) -> Dict[str, List[Dict]]:
        """
        Get all photos for a person
        
        Args:
            person_id: Person identifier
            
        Returns:
            Dictionary with 'individual' and 'group' photo lists
        """
        query = """
            SELECT pp.*, ph.filename, ph.filepath, ph.event_id
            FROM person_photos pp
            JOIN photos ph ON pp.photo_id = ph.id
            WHERE pp.person_id = %s
            ORDER BY pp.match_confidence DESC, ph.upload_date DESC
        """
        
        try:
            with self.get_cursor() as cursor:
                cursor.execute(query, (person_id,))
                photos = cursor.fetchall()
                
                # Separate into individual and group photos
                result = {
                    'individual': [p for p in photos if not p['is_group_photo']],
                    'group': [p for p in photos if p['is_group_photo']]
                }
                
                return result
        except Error as e:
            print(f"✗ Error getting person photos: {e}")
            return {'individual': [], 'group': []}
    
    def _get_photo_face_count(self, photo_id: int) -> int:
        """Get face count for a photo"""
        query = "SELECT face_count FROM photos WHERE id = %s"
        
        with self.get_cursor() as cursor:
            cursor.execute(query, (photo_id,))
            result = cursor.fetchone()
            return result['face_count'] if result else 1
    
    # ========================================================================
    # PHOTO MANAGEMENT
    # ========================================================================
    
    def add_photo(self, event_id: str, filename: str, filepath: str) -> int:
        """
        Add photo record
        
        Args:
            event_id: Event identifier
            filename: Photo filename
            filepath: Photo file path
            
        Returns:
            Photo ID
        """
        query = """
            INSERT INTO photos (event_id, filename, filepath)
            VALUES (%s, %s, %s)
            ON DUPLICATE KEY UPDATE
            filepath = VALUES(filepath),
            updated_date = CURRENT_TIMESTAMP
        """
        
        try:
            with self.get_cursor() as cursor:
                cursor.execute(query, (event_id, filename, filepath))
                self.commit()
                return cursor.lastrowid
        except Error as e:
            self.rollback()
            print(f"✗ Error adding photo: {e}")
            raise
    
    def get_photo(self, photo_id: int) -> Optional[Dict]:
        """Get photo details"""
        query = "SELECT * FROM photos WHERE id = %s"
        
        try:
            with self.get_cursor() as cursor:
                cursor.execute(query, (photo_id,))
                return cursor.fetchone()
        except Error as e:
            print(f"✗ Error getting photo: {e}")
            return None
    
    def mark_photo_processed(self, photo_id: int) -> bool:
        """Mark photo as processed"""
        query = """
            UPDATE photos 
            SET processed = 1, updated_date = CURRENT_TIMESTAMP
            WHERE id = %s
        """
        
        try:
            with self.get_cursor() as cursor:
                cursor.execute(query, (photo_id,))
                self.commit()
                return cursor.rowcount > 0
        except Error as e:
            self.rollback()
            print(f"✗ Error marking photo processed: {e}")
            return False
    
    # ========================================================================
    # FACE DETECTION MANAGEMENT
    # ========================================================================
    
    def add_face_detection(self, photo_id: int, person_id: Optional[int],
                          bbox: Dict, angle: str, quality_score: float,
                          detection_method: str, detection_confidence: float) -> int:
        """
        Add face detection record
        
        Args:
            photo_id: Photo identifier
            person_id: Person identifier (optional)
            bbox: Bounding box dictionary
            angle: Angle classification
            quality_score: Quality score
            detection_method: Detection method used
            detection_confidence: Detection confidence
            
        Returns:
            Face detection ID
        """
        bbox_json = json.dumps(bbox)
        
        query = """
            INSERT INTO face_detections 
            (photo_id, person_id, face_bbox, angle_estimate, quality_score,
             detection_method, detection_confidence)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        
        try:
            with self.get_cursor() as cursor:
                cursor.execute(query, (photo_id, person_id, bbox_json, angle,
                                      quality_score, detection_method, detection_confidence))
                self.commit()
                return cursor.lastrowid
        except Error as e:
            self.rollback()
            print(f"✗ Error adding face detection: {e}")
            raise
    
    # ========================================================================
    # STATISTICS
    # ========================================================================
    
    def get_statistics(self) -> Dict:
        """Get database statistics"""
        stats = {}
        
        queries = {
            'total_persons': "SELECT COUNT(*) as count FROM persons",
            'total_photos': "SELECT COUNT(*) as count FROM photos",
            'total_detections': "SELECT COUNT(*) as count FROM face_detections",
            'total_encodings': "SELECT COUNT(*) as count FROM face_encodings",
            'processed_photos': "SELECT COUNT(*) as count FROM photos WHERE processed = 1"
        }
        
        try:
            with self.get_cursor() as cursor:
                for key, query in queries.items():
                    cursor.execute(query)
                    result = cursor.fetchone()
                    stats[key] = result['count'] if result else 0
            
            return stats
        except Error as e:
            print(f"✗ Error getting statistics: {e}")
            return {}


def main():
    """Test the Multi-Angle Face Database"""
    print("\n" + "=" * 70)
    print("TESTING MULTI-ANGLE FACE DATABASE")
    print("=" * 70)
    
    # Initialize database
    db = MultiAngleFaceDatabase()
    
    # Get statistics
    print("\nDatabase Statistics:")
    stats = db.get_statistics()
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    # Close connection
    db.close()
    
    print("\n✓ Multi-Angle Face Database test complete")
    print("=" * 70)


if __name__ == "__main__":
    main()
