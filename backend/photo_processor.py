#!/usr/bin/env python3
"""
Photo Processor for Enhanced Multi-Angle Face Detection System

Orchestrates the complete photo processing workflow by integrating all components:
- EnhancedFaceDetector: Detect faces with angle and quality assessment
- DeepFeatureExtractor: Extract 128D encodings and facial features
- MultiAngleFaceDatabase: Store persons, encodings, and associations
- EnhancedMatchingEngine: Match faces against database

Features:
- Single photo processing
- Batch processing with progress tracking
- Error handling and logging
- Complete end-to-end workflow
"""

import cv2
import numpy as np
import os
import uuid
from typing import Dict, List, Optional
from datetime import datetime

from enhanced_face_detector import EnhancedFaceDetector
from deep_feature_extractor import DeepFeatureExtractor
from multi_angle_database import MultiAngleFaceDatabase
from enhanced_matching_engine import EnhancedMatchingEngine


class PhotoProcessor:
    """
    Photo processor that orchestrates the complete face detection workflow
    """
    
    def __init__(self, db_config: Optional[Dict] = None):
        """
        Initialize photo processor with all components
        
        Args:
            db_config: Optional database configuration
        """
        print("=" * 70)
        print("INITIALIZING PHOTO PROCESSOR")
        print("=" * 70)
        
        # Initialize all components
        print("\nLoading components...")
        self.detector = EnhancedFaceDetector()
        self.extractor = DeepFeatureExtractor()
        
        # Initialize database
        if db_config:
            self.database = MultiAngleFaceDatabase(**db_config)
        else:
            self.database = MultiAngleFaceDatabase()
        
        # Initialize matching engine
        self.matcher = EnhancedMatchingEngine(self.database, threshold=0.6)
        
        # Processing statistics
        self.stats = {
            'photos_processed': 0,
            'faces_detected': 0,
            'persons_created': 0,
            'persons_matched': 0,
            'errors': 0
        }
        
        print("✓ Photo Processor initialized successfully")
        print("=" * 70)
        print()
    
    def process_photo(self, photo_path: str, event_id: str) -> Dict:
        """
        Process single photo end-to-end
        
        Args:
            photo_path: Path to photo file
            event_id: Event identifier
            
        Returns:
            Processing results dictionary
        """
        print(f"\n{'=' * 70}")
        print(f"PROCESSING PHOTO: {os.path.basename(photo_path)}")
        print('=' * 70)
        
        result = {
            'success': False,
            'photo_path': photo_path,
            'event_id': event_id,
            'faces_detected': 0,
            'faces_processed': 0,
            'persons_matched': [],
            'persons_created': [],
            'errors': []
        }
        
        try:
            # Step 1: Load image
            print("\n1. Loading image...")
            image = cv2.imread(photo_path)
            if image is None:
                raise ValueError(f"Failed to load image: {photo_path}")
            print(f"✓ Image loaded: {image.shape[1]}x{image.shape[0]}")
            
            # Step 2: Add photo to database
            print("\n2. Adding photo to database...")
            filename = os.path.basename(photo_path)
            photo_id = self.database.add_photo(event_id, filename, photo_path)
            print(f"✓ Photo added: ID={photo_id}")
            
            # Step 3: Detect faces
            print("\n3. Detecting faces...")
            detections = self.detector.detect_faces(image)
            result['faces_detected'] = len(detections)
            print(f"✓ Detected {len(detections)} face(s)")
            
            if len(detections) == 0:
                self.database.mark_photo_processed(photo_id)
                result['success'] = True
                return result
            
            # Step 4: Process each detected face
            print("\n4. Processing detected faces...")
            for idx, detection in enumerate(detections, 1):
                print(f"\n  --- Face {idx}/{len(detections)} ---")
                
                try:
                    face_result = self._process_face(
                        image, detection, photo_id, event_id
                    )
                    
                    if face_result['success']:
                        result['faces_processed'] += 1
                        if face_result['matched']:
                            result['persons_matched'].append(face_result['person_id'])
                        else:
                            result['persons_created'].append(face_result['person_id'])
                    else:
                        result['errors'].append(face_result.get('error', 'Unknown error'))
                        
                except Exception as e:
                    error_msg = f"Face {idx} processing error: {str(e)}"
                    print(f"  ✗ {error_msg}")
                    result['errors'].append(error_msg)
                    self.stats['errors'] += 1
            
            # Step 5: Mark photo as processed
            print("\n5. Finalizing...")
            self.database.mark_photo_processed(photo_id)
            result['success'] = True
            self.stats['photos_processed'] += 1
            
            print(f"\n✓ Photo processing complete:")
            print(f"  Faces detected: {result['faces_detected']}")
            print(f"  Faces processed: {result['faces_processed']}")
            print(f"  Persons matched: {len(result['persons_matched'])}")
            print(f"  Persons created: {len(result['persons_created'])}")
            
        except Exception as e:
            error_msg = f"Photo processing error: {str(e)}"
            print(f"\n✗ {error_msg}")
            result['errors'].append(error_msg)
            self.stats['errors'] += 1
        
        return result
    
    def _process_face(self, image: np.ndarray, detection: Dict, 
                     photo_id: int, event_id: str) -> Dict:
        """
        Process a single detected face
        
        Args:
            image: Full image
            detection: Face detection result
            photo_id: Photo ID in database
            event_id: Event identifier
            
        Returns:
            Face processing result
        """
        result = {
            'success': False,
            'matched': False,
            'person_id': None
        }
        
        # Extract face region
        bbox = detection['bbox']
        x, y, w, h = bbox
        face_img = image[y:y+h, x:x+w]
        
        print(f"  Face size: {w}x{h}")
        print(f"  Detection method: {detection['method']}")
        print(f"  Detection confidence: {detection['confidence']:.3f}")
        
        # Extract features
        print(f"  Extracting features...")
        features = self.extractor.extract_all(face_img)
        
        if features['encoding'] is None:
            result['error'] = "Failed to extract encoding"
            return result
        
        print(f"  ✓ Encoding extracted: 128D")
        
        # Estimate angle and quality
        angle = detection.get('angle', 'frontal')
        quality_scores = self.detector.calculate_quality_score(face_img)
        quality = quality_scores['overall_score']
        
        print(f"  Angle: {angle}, Quality: {quality:.3f}")
        
        # Match against database
        print(f"  Matching against database...")
        match_result = self.matcher.match_face(features['encoding'], angle=angle)
        
        if match_result['matched']:
            # Matched existing person
            person_id = match_result['person_id']
            confidence = match_result['confidence']
            print(f"  ✓ Matched person {person_id} (confidence: {confidence:.3f})")
            
            result['matched'] = True
            result['person_id'] = person_id
            self.stats['persons_matched'] += 1
        else:
            # Create new person
            person_uuid = str(uuid.uuid4())
            person_id = self.database.add_person(person_uuid=person_uuid)
            print(f"  ✓ Created new person {person_id}")
            
            result['matched'] = False
            result['person_id'] = person_id
            self.stats['persons_created'] += 1
        
        # Add face detection record
        detection_id = self.database.add_face_detection(
            photo_id=photo_id,
            person_id=person_id,
            bbox=bbox,
            angle=angle,
            quality_score=quality,
            detection_method=detection['method'],
            detection_confidence=detection['confidence']
        )
        
        # Store encoding
        self.database.add_face_encoding(
            person_id=person_id,
            encoding=features['encoding'],
            angle=angle,
            quality_score=quality,
            face_detection_id=detection_id
        )
        
        # Associate photo with person
        is_group = len(self.detector.detect_faces(image)) > 1
        self.database.associate_photo(
            person_id=person_id,
            photo_id=photo_id,
            is_group=is_group,
            confidence=match_result.get('confidence', 1.0),
            face_detection_id=detection_id
        )
        
        self.stats['faces_detected'] += 1
        result['success'] = True
        
        return result
    
    def process_event(self, event_id: str, photos_dir: str, 
                     force_reprocess: bool = False) -> Dict:
        """
        Process all photos in an event (batch processing)
        
        Args:
            event_id: Event identifier
            photos_dir: Directory containing photos
            force_reprocess: Whether to reprocess already processed photos
            
        Returns:
            Batch processing results
        """
        print(f"\n{'=' * 70}")
        print(f"BATCH PROCESSING EVENT: {event_id}")
        print('=' * 70)
        
        result = {
            'success': False,
            'event_id': event_id,
            'total_photos': 0,
            'processed_photos': 0,
            'skipped_photos': 0,
            'total_faces': 0,
            'errors': []
        }
        
        try:
            # Find all image files
            print(f"\n1. Scanning directory: {photos_dir}")
            image_extensions = ('.jpg', '.jpeg', '.png', '.bmp')
            photo_files = [
                f for f in os.listdir(photos_dir)
                if f.lower().endswith(image_extensions)
            ]
            
            result['total_photos'] = len(photo_files)
            print(f"✓ Found {len(photo_files)} photo(s)")
            
            if len(photo_files) == 0:
                result['success'] = True
                return result
            
            # Process each photo
            print(f"\n2. Processing photos...")
            for idx, filename in enumerate(photo_files, 1):
                photo_path = os.path.join(photos_dir, filename)
                
                print(f"\n{'=' * 70}")
                print(f"Photo {idx}/{len(photo_files)}: {filename}")
                print('=' * 70)
                
                # Check if already processed
                if not force_reprocess:
                    # TODO: Check database if photo already processed
                    pass
                
                # Process photo
                photo_result = self.process_photo(photo_path, event_id)
                
                if photo_result['success']:
                    result['processed_photos'] += 1
                    result['total_faces'] += photo_result['faces_detected']
                else:
                    result['errors'].extend(photo_result['errors'])
                
                # Progress update
                progress = (idx / len(photo_files)) * 100
                print(f"\nProgress: {progress:.1f}% ({idx}/{len(photo_files)})")
            
            result['success'] = True
            
            # Print summary
            print(f"\n{'=' * 70}")
            print("BATCH PROCESSING SUMMARY")
            print('=' * 70)
            print(f"Event ID: {event_id}")
            print(f"Total photos: {result['total_photos']}")
            print(f"Processed: {result['processed_photos']}")
            print(f"Skipped: {result['skipped_photos']}")
            print(f"Total faces detected: {result['total_faces']}")
            print(f"Errors: {len(result['errors'])}")
            
        except Exception as e:
            error_msg = f"Batch processing error: {str(e)}"
            print(f"\n✗ {error_msg}")
            result['errors'].append(error_msg)
        
        return result
    
    def get_statistics(self) -> Dict:
        """Get processing statistics"""
        return self.stats.copy()
    
    def reset_statistics(self):
        """Reset processing statistics"""
        for key in self.stats:
            self.stats[key] = 0
    
    def close(self):
        """Close database connection"""
        self.database.close()
        print("✓ Photo Processor closed")


def main():
    """Test the Photo Processor"""
    print("\n" + "=" * 70)
    print("TESTING PHOTO PROCESSOR")
    print("=" * 70)
    
    # Initialize processor
    processor = PhotoProcessor()
    
    # Test with sample photos if available
    test_dir = "../uploads/event_931cd6b8"
    
    if os.path.exists(test_dir):
        print(f"\nTesting with photos from: {test_dir}")
        
        # Process first photo as test
        photo_files = [f for f in os.listdir(test_dir) 
                      if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
        
        if photo_files:
            test_photo = os.path.join(test_dir, photo_files[0])
            result = processor.process_photo(test_photo, "test_event")
            
            print(f"\nTest Result:")
            print(f"  Success: {result['success']}")
            print(f"  Faces detected: {result['faces_detected']}")
            print(f"  Faces processed: {result['faces_processed']}")
    else:
        print(f"\nTest directory not found: {test_dir}")
        print("Processor initialized successfully but no test photos available")
    
    # Print statistics
    print("\n" + "=" * 70)
    print("PROCESSING STATISTICS")
    print("=" * 70)
    stats = processor.get_statistics()
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    # Close processor
    processor.close()
    
    print("\n✓ Photo Processor test complete")
    print("=" * 70)


if __name__ == "__main__":
    main()
