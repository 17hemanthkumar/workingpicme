#!/usr/bin/env python3
"""
Live Face Scanner for Enhanced Multi-Angle Face Detection System

Real-time webcam-based face capture and matching with instant photo retrieval.
Integrates with the complete face detection system for live scanning use cases.

Features:
- Webcam face capture with quality validation
- Real-time face matching
- Instant photo retrieval (individual and group photos)
- Quality feedback for user positioning
"""

import cv2
import numpy as np
from typing import Dict, List, Optional
import time

from enhanced_face_detector import EnhancedFaceDetector
from deep_feature_extractor import DeepFeatureExtractor
from multi_angle_database import MultiAngleFaceDatabase
from enhanced_matching_engine import EnhancedMatchingEngine


class LiveFaceScanner:
    """
    Live face scanner for webcam-based face capture and matching
    """
    
    def __init__(self, db_config: Optional[Dict] = None, min_quality: float = 0.5):
        """
        Initialize live face scanner
        
        Args:
            db_config: Optional database configuration
            min_quality: Minimum quality threshold for capture (default 0.5)
        """
        print("=" * 70)
        print("INITIALIZING LIVE FACE SCANNER")
        print("=" * 70)
        
        self.min_quality = min_quality
        
        # Initialize components
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
        
        print(f"✓ Minimum quality threshold: {min_quality}")
        print("✓ Live Face Scanner initialized successfully")
        print("=" * 70)
        print()
    
    def capture_face(self, camera_index: int = 0, timeout: int = 30) -> Dict:
        """
        Capture face from webcam with quality validation
        
        Args:
            camera_index: Camera device index (default 0)
            timeout: Maximum time to wait for quality capture (seconds)
            
        Returns:
            Capture result with face image and quality info
        """
        print(f"\n{'=' * 70}")
        print("CAPTURING FACE FROM WEBCAM")
        print('=' * 70)
        
        result = {
            'success': False,
            'face_image': None,
            'quality_score': 0.0,
            'angle': None,
            'message': ''
        }
        
        # Open webcam
        print(f"\n1. Opening webcam (camera {camera_index})...")
        cap = cv2.VideoCapture(camera_index)
        
        if not cap.isOpened():
            result['message'] = f"Failed to open camera {camera_index}"
            print(f"✗ {result['message']}")
            return result
        
        print("✓ Webcam opened")
        print(f"\n2. Waiting for quality face (minimum quality: {self.min_quality})...")
        print("   Position your face in front of the camera...")
        
        start_time = time.time()
        frame_count = 0
        best_capture = None
        best_quality = 0.0
        
        try:
            while True:
                # Check timeout
                if time.time() - start_time > timeout:
                    if best_capture is not None:
                        print(f"\n⚠ Timeout reached, using best capture (quality: {best_quality:.3f})")
                        result['success'] = True
                        result['face_image'] = best_capture['face_image']
                        result['quality_score'] = best_quality
                        result['angle'] = best_capture['angle']
                        result['message'] = f"Captured with quality {best_quality:.3f}"
                    else:
                        result['message'] = "Timeout: No face detected"
                        print(f"\n✗ {result['message']}")
                    break
                
                # Read frame
                ret, frame = cap.read()
                if not ret:
                    result['message'] = "Failed to read frame"
                    break
                
                frame_count += 1
                
                # Detect faces (check every 5 frames for performance)
                if frame_count % 5 == 0:
                    detections = self.detector.detect_faces(frame)
                    
                    if len(detections) > 0:
                        # Get first face
                        detection = detections[0]
                        bbox = detection['bbox']
                        x, y, w, h = bbox
                        face_img = frame[y:y+h, x:x+w]
                        
                        # Calculate quality
                        quality_scores = self.detector.calculate_quality_score(face_img)
                        quality = quality_scores['overall_score']
                        angle = detection.get('angle', 'frontal')
                        
                        print(f"\r   Frame {frame_count}: Quality={quality:.3f}, Angle={angle}", end='')
                        
                        # Check if quality is sufficient
                        if quality >= self.min_quality:
                            result['success'] = True
                            result['face_image'] = face_img.copy()
                            result['quality_score'] = quality
                            result['angle'] = angle
                            result['message'] = f"Captured with quality {quality:.3f}"
                            print(f"\n✓ Quality face captured!")
                            break
                        
                        # Track best capture
                        if quality > best_quality:
                            best_quality = quality
                            best_capture = {
                                'face_image': face_img.copy(),
                                'angle': angle
                            }
                
                # Small delay
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    result['message'] = "Capture cancelled by user"
                    break
        
        finally:
            cap.release()
            cv2.destroyAllWindows()
        
        return result
    
    def scan_and_match(self, camera_index: int = 0, timeout: int = 30) -> Dict:
        """
        Complete scan and match workflow
        
        Args:
            camera_index: Camera device index
            timeout: Maximum time to wait for capture
            
        Returns:
            Match result with person info and photos
        """
        print(f"\n{'=' * 70}")
        print("LIVE SCAN AND MATCH")
        print('=' * 70)
        
        result = {
            'success': False,
            'matched': False,
            'person_id': None,
            'confidence': 0.0,
            'photos': {'individual': [], 'group': []},
            'message': ''
        }
        
        # Step 1: Capture face
        print("\nStep 1: Capturing face...")
        capture_result = self.capture_face(camera_index, timeout)
        
        if not capture_result['success']:
            result['message'] = f"Capture failed: {capture_result['message']}"
            print(f"✗ {result['message']}")
            return result
        
        face_img = capture_result['face_image']
        quality = capture_result['quality_score']
        angle = capture_result['angle']
        
        print(f"✓ Face captured: quality={quality:.3f}, angle={angle}")
        
        # Step 2: Extract encoding
        print("\nStep 2: Extracting face encoding...")
        encoding = self.extractor.extract_encoding(face_img)
        
        if encoding is None:
            result['message'] = "Failed to extract face encoding"
            print(f"✗ {result['message']}")
            return result
        
        print(f"✓ Encoding extracted: 128D")
        
        # Step 3: Match against database
        print("\nStep 3: Matching against database...")
        match_result = self.matcher.match_face(encoding, angle=angle)
        
        if match_result['matched']:
            person_id = match_result['person_id']
            confidence = match_result['confidence']
            
            print(f"✓ Match found: Person {person_id} (confidence: {confidence:.3f})")
            
            result['matched'] = True
            result['person_id'] = person_id
            result['confidence'] = confidence
            
            # Step 4: Retrieve photos
            print("\nStep 4: Retrieving photos...")
            photos = self.get_person_photos(person_id)
            result['photos'] = photos
            
            print(f"✓ Photos retrieved:")
            print(f"  Individual photos: {len(photos['individual'])}")
            print(f"  Group photos: {len(photos['group'])}")
            
            result['success'] = True
            result['message'] = f"Match found with {confidence:.1%} confidence"
        else:
            print(f"✗ No match found (best distance: {match_result['distance']:.3f})")
            result['message'] = "No matching person found in database"
            result['success'] = True  # Scan succeeded, just no match
        
        return result
    
    def get_person_photos(self, person_id: int) -> Dict[str, List[Dict]]:
        """
        Retrieve all photos of a person
        
        Args:
            person_id: Person identifier
            
        Returns:
            Dictionary with 'individual' and 'group' photo lists
        """
        photos = self.database.get_person_photos(person_id)
        
        # Sort by confidence
        photos['individual'].sort(key=lambda x: x.get('match_confidence', 0), reverse=True)
        photos['group'].sort(key=lambda x: x.get('match_confidence', 0), reverse=True)
        
        return photos
    
    def close(self):
        """Close database connection"""
        self.database.close()
        print("✓ Live Face Scanner closed")


def main():
    """Test the Live Face Scanner"""
    print("\n" + "=" * 70)
    print("TESTING LIVE FACE SCANNER")
    print("=" * 70)
    
    # Initialize scanner
    scanner = LiveFaceScanner(min_quality=0.5)
    
    print("\n" + "=" * 70)
    print("LIVE SCAN TEST")
    print("=" * 70)
    print("\nThis test requires a webcam.")
    print("The scanner will attempt to capture your face.")
    print("Press 'q' to cancel at any time.")
    print("\nNote: If no webcam is available, the test will fail gracefully.")
    
    # Attempt to scan (will fail if no webcam)
    try:
        result = scanner.scan_and_match(camera_index=0, timeout=10)
        
        print("\n" + "=" * 70)
        print("SCAN RESULT")
        print("=" * 70)
        print(f"Success: {result['success']}")
        print(f"Matched: {result['matched']}")
        if result['matched']:
            print(f"Person ID: {result['person_id']}")
            print(f"Confidence: {result['confidence']:.1%}")
            print(f"Individual photos: {len(result['photos']['individual'])}")
            print(f"Group photos: {len(result['photos']['group'])}")
        print(f"Message: {result['message']}")
        
    except Exception as e:
        print(f"\n⚠ Webcam test skipped: {str(e)}")
        print("This is expected if no webcam is available.")
    
    # Close scanner
    scanner.close()
    
    print("\n✓ Live Face Scanner test complete")
    print("=" * 70)


if __name__ == "__main__":
    main()
