#!/usr/bin/env python3
"""
Deep Feature Extractor for Enhanced Face Detection System

Extracts 128D face encodings, 68-point facial landmarks, and analyzes detailed facial features.
Integrates with the EnhancedFaceDetector for the multi-angle face detection system.

Features:
- 128D face encoding extraction (using face_recognition library)
- 68-point facial landmark detection (using dlib)
- Detailed feature analysis (eyes, nose, jaw, facial hair, glasses)
- Compatible with MySQL database storage
"""

import cv2
import numpy as np
import face_recognition
import dlib
from typing import Dict, List, Tuple, Optional
import json

class DeepFeatureExtractor:
    """
    Deep feature extractor for comprehensive facial analysis
    """
    
    def __init__(self):
        """Initialize the feature extractor with face_recognition and dlib models"""
        print("=" * 70)
        print("INITIALIZING DEEP FEATURE EXTRACTOR")
        print("=" * 70)
        
        self.models_loaded = {}
        self.extraction_stats = {
            'encodings_extracted': 0,
            'landmarks_extracted': 0,
            'features_analyzed': 0,
            'total_extractions': 0
        }
        
        # Load models
        self._load_models()
        
        print("✓ Deep Feature Extractor initialized successfully")
        print("=" * 70)
        print()
    
    def _load_models(self):
        """Load face_recognition and dlib models"""
        print("\nLoading feature extraction models...")
        
        # face_recognition library is already loaded (uses dlib internally)
        try:
            # Test face_recognition
            test_img = np.zeros((100, 100, 3), dtype=np.uint8)
            _ = face_recognition.face_encodings(test_img)
            self.models_loaded['face_recognition'] = True
            print("  ✓ face_recognition library loaded")
        except Exception as e:
            print(f"  ✗ face_recognition failed to load: {e}")
            self.models_loaded['face_recognition'] = False
        
        # dlib shape predictor is used internally by face_recognition
        # We'll use face_recognition's landmark detection
        self.models_loaded['dlib'] = True
        print("  ✓ dlib (via face_recognition) loaded")
        
        if not any(self.models_loaded.values()):
            raise Exception("No feature extraction models could be loaded!")
        
        print(f"\n  Loaded {sum(self.models_loaded.values())}/{len(self.models_loaded)} models")
    
    def extract_encoding(self, face_image: np.ndarray, face_location: Optional[Tuple] = None) -> Optional[np.ndarray]:
        """
        Extract 128D face encoding
        
        Args:
            face_image: Face image (BGR format from OpenCV)
            face_location: Optional face location (top, right, bottom, left)
        
        Returns:
            128-dimensional numpy array or None if extraction fails
        """
        try:
            # Convert BGR to RGB (face_recognition expects RGB)
            rgb_image = cv2.cvtColor(face_image, cv2.COLOR_BGR2RGB)
            
            # Extract encoding
            if face_location:
                # Use provided face location
                encodings = face_recognition.face_encodings(rgb_image, [face_location])
            else:
                # Detect face automatically
                encodings = face_recognition.face_encodings(rgb_image)
            
            if encodings:
                self.extraction_stats['encodings_extracted'] += 1
                return encodings[0]  # Return first encoding
            
            return None
        except Exception as e:
            print(f"Encoding extraction error: {e}")
            return None
    
    def extract_landmarks(self, face_image: np.ndarray, face_location: Optional[Tuple] = None) -> Optional[Dict]:
        """
        Extract 68 facial landmarks
        
        Args:
            face_image: Face image (BGR format from OpenCV)
            face_location: Optional face location (top, right, bottom, left)
        
        Returns:
            Dictionary with landmark points or None if extraction fails
        """
        try:
            # Convert BGR to RGB
            rgb_image = cv2.cvtColor(face_image, cv2.COLOR_BGR2RGB)
            
            # Extract landmarks
            if face_location:
                landmarks_list = face_recognition.face_landmarks(rgb_image, [face_location])
            else:
                landmarks_list = face_recognition.face_landmarks(rgb_image)
            
            if landmarks_list:
                self.extraction_stats['landmarks_extracted'] += 1
                return landmarks_list[0]  # Return first face landmarks
            
            return None
        except Exception as e:
            print(f"Landmark extraction error: {e}")
            return None
    
    def analyze_features(self, face_image: np.ndarray, landmarks: Optional[Dict] = None) -> Dict:
        """
        Analyze detailed facial features
        
        Args:
            face_image: Face image (BGR format)
            landmarks: Optional facial landmarks dictionary
        
        Returns:
            Dictionary with feature measurements and attributes
        """
        features = {}
        
        # If no landmarks provided, extract them
        if landmarks is None:
            landmarks = self.extract_landmarks(face_image)
        
        if landmarks:
            # Calculate eye distance
            features['eye_distance'] = self._calculate_eye_distance(landmarks)
            
            # Measure nose dimensions
            nose_features = self._measure_nose(landmarks)
            features['nose_width'] = nose_features['width']
            features['nose_height'] = nose_features['height']
            
            # Measure jaw width
            features['jaw_width'] = self._measure_jaw_width(landmarks)
            
            # Measure mouth width
            features['mouth_width'] = self._measure_mouth_width(landmarks)
            
            # Calculate face dimensions
            face_dims = self._calculate_face_dimensions(landmarks)
            features['face_width'] = face_dims['width']
            features['face_height'] = face_dims['height']
        else:
            # Set default values if landmarks not available
            features['eye_distance'] = None
            features['nose_width'] = None
            features['nose_height'] = None
            features['jaw_width'] = None
            features['mouth_width'] = None
            features['face_width'] = None
            features['face_height'] = None
        
        # Detect facial hair (image-based)
        facial_hair = self._detect_facial_hair(face_image, landmarks)
        features['has_facial_hair'] = facial_hair['has_facial_hair']
        features['facial_hair_type'] = facial_hair['type']
        
        # Detect glasses (image-based)
        features['glasses'] = self._detect_glasses(face_image, landmarks)
        
        # Estimate age (simple heuristic)
        features['age_estimate'] = self._estimate_age(face_image, landmarks)
        
        # Estimate gender (simple heuristic)
        features['gender_estimate'] = self._estimate_gender(face_image, landmarks)
        
        # Estimate emotion (simple heuristic)
        features['emotion_estimate'] = self._estimate_emotion(face_image, landmarks)
        
        self.extraction_stats['features_analyzed'] += 1
        return features
    
    def extract_all(self, face_image: np.ndarray, face_location: Optional[Tuple] = None) -> Dict:
        """
        Extract all features at once (encoding, landmarks, and analysis)
        
        Args:
            face_image: Face image (BGR format)
            face_location: Optional face location (top, right, bottom, left)
        
        Returns:
            Dictionary with all extracted features
        """
        self.extraction_stats['total_extractions'] += 1
        
        result = {
            'encoding': None,
            'landmarks': None,
            'features': {}
        }
        
        # Extract encoding
        result['encoding'] = self.extract_encoding(face_image, face_location)
        
        # Extract landmarks
        result['landmarks'] = self.extract_landmarks(face_image, face_location)
        
        # Analyze features
        result['features'] = self.analyze_features(face_image, result['landmarks'])
        
        return result
    
    # Helper methods for feature calculations
    
    def _calculate_eye_distance(self, landmarks: Dict) -> float:
        """Calculate distance between eye centers"""
        if 'left_eye' in landmarks and 'right_eye' in landmarks:
            left_eye_center = np.mean(landmarks['left_eye'], axis=0)
            right_eye_center = np.mean(landmarks['right_eye'], axis=0)
            distance = np.linalg.norm(left_eye_center - right_eye_center)
            return float(distance)
        return 0.0
    
    def _measure_nose(self, landmarks: Dict) -> Dict:
        """Measure nose dimensions"""
        if 'nose_bridge' in landmarks and 'nose_tip' in landmarks:
            nose_points = landmarks['nose_bridge'] + landmarks['nose_tip']
            nose_array = np.array(nose_points)
            
            width = np.max(nose_array[:, 0]) - np.min(nose_array[:, 0])
            height = np.max(nose_array[:, 1]) - np.min(nose_array[:, 1])
            
            return {'width': float(width), 'height': float(height)}
        return {'width': 0.0, 'height': 0.0}
    
    def _measure_jaw_width(self, landmarks: Dict) -> float:
        """Measure jaw width"""
        if 'chin' in landmarks:
            chin_points = np.array(landmarks['chin'])
            width = np.max(chin_points[:, 0]) - np.min(chin_points[:, 0])
            return float(width)
        return 0.0
    
    def _measure_mouth_width(self, landmarks: Dict) -> float:
        """Measure mouth width"""
        if 'top_lip' in landmarks and 'bottom_lip' in landmarks:
            mouth_points = landmarks['top_lip'] + landmarks['bottom_lip']
            mouth_array = np.array(mouth_points)
            width = np.max(mouth_array[:, 0]) - np.min(mouth_array[:, 0])
            return float(width)
        return 0.0
    
    def _calculate_face_dimensions(self, landmarks: Dict) -> Dict:
        """Calculate overall face dimensions"""
        # Combine all landmark points
        all_points = []
        for key, points in landmarks.items():
            all_points.extend(points)
        
        if all_points:
            points_array = np.array(all_points)
            width = np.max(points_array[:, 0]) - np.min(points_array[:, 0])
            height = np.max(points_array[:, 1]) - np.min(points_array[:, 1])
            return {'width': float(width), 'height': float(height)}
        
        return {'width': 0.0, 'height': 0.0}
    
    def _detect_facial_hair(self, face_image: np.ndarray, landmarks: Optional[Dict]) -> Dict:
        """Detect presence and type of facial hair (simplified heuristic)"""
        # This is a simplified approach - in production, use a trained model
        
        if landmarks and 'chin' in landmarks:
            # Analyze chin region for facial hair
            chin_points = np.array(landmarks['chin'])
            
            # Get chin region
            y_min = int(np.min(chin_points[:, 1]))
            y_max = int(face_image.shape[0])
            x_min = int(np.min(chin_points[:, 0]))
            x_max = int(np.max(chin_points[:, 0]))
            
            # Ensure valid region
            if y_max > y_min and x_max > x_min:
                chin_region = face_image[y_min:y_max, x_min:x_max]
                
                # Convert to grayscale
                gray_chin = cv2.cvtColor(chin_region, cv2.COLOR_BGR2GRAY)
                
                # Calculate darkness (facial hair is typically darker)
                avg_darkness = np.mean(gray_chin)
                
                # Simple threshold (this is very basic)
                if avg_darkness < 100:  # Darker region suggests facial hair
                    return {'has_facial_hair': True, 'type': 'beard'}
        
        return {'has_facial_hair': False, 'type': 'none'}
    
    def _detect_glasses(self, face_image: np.ndarray, landmarks: Optional[Dict]) -> bool:
        """Detect presence of glasses (simplified heuristic)"""
        # This is a simplified approach - in production, use a trained model
        
        if landmarks and 'left_eye' in landmarks and 'right_eye' in landmarks:
            # Analyze eye regions for glasses frames
            left_eye = np.array(landmarks['left_eye'])
            right_eye = np.array(landmarks['right_eye'])
            
            # Get eye regions
            for eye_points in [left_eye, right_eye]:
                y_min = max(0, int(np.min(eye_points[:, 1])) - 10)
                y_max = min(face_image.shape[0], int(np.max(eye_points[:, 1])) + 10)
                x_min = max(0, int(np.min(eye_points[:, 0])) - 10)
                x_max = min(face_image.shape[1], int(np.max(eye_points[:, 0])) + 10)
                
                if y_max > y_min and x_max > x_min:
                    eye_region = face_image[y_min:y_max, x_min:x_max]
                    
                    # Edge detection (glasses have strong edges)
                    gray_eye = cv2.cvtColor(eye_region, cv2.COLOR_BGR2GRAY)
                    edges = cv2.Canny(gray_eye, 50, 150)
                    edge_density = np.sum(edges > 0) / edges.size
                    
                    # High edge density suggests glasses
                    if edge_density > 0.15:
                        return True
        
        return False
    
    def _estimate_age(self, face_image: np.ndarray, landmarks: Optional[Dict]) -> Optional[int]:
        """Estimate age (placeholder - would need trained model)"""
        # This is a placeholder - real age estimation requires a trained model
        # For now, return None to indicate not implemented
        return None
    
    def _estimate_gender(self, face_image: np.ndarray, landmarks: Optional[Dict]) -> Optional[str]:
        """Estimate gender (placeholder - would need trained model)"""
        # This is a placeholder - real gender estimation requires a trained model
        # For now, return None to indicate not implemented
        return None
    
    def _estimate_emotion(self, face_image: np.ndarray, landmarks: Optional[Dict]) -> Optional[str]:
        """Estimate emotion (placeholder - would need trained model)"""
        # This is a placeholder - real emotion detection requires a trained model
        # For now, return None to indicate not implemented
        return None
    
    def get_extraction_stats(self) -> Dict:
        """Get extraction statistics"""
        return self.extraction_stats.copy()
    
    def reset_stats(self):
        """Reset extraction statistics"""
        for key in self.extraction_stats:
            self.extraction_stats[key] = 0


def main():
    """Test the Deep Feature Extractor"""
    print("\n" + "=" * 70)
    print("TESTING DEEP FEATURE EXTRACTOR")
    print("=" * 70)
    
    # Initialize extractor
    extractor = DeepFeatureExtractor()
    
    # Test with a sample image (if available)
    test_image_path = "../uploads/event_931cd6b8/10750d04_WhatsApp_Image_2025-11-20_at_5.13.03_PM.jpeg"
    
    if cv2.os.path.exists(test_image_path):
        print(f"\nTesting with image: {test_image_path}")
        image = cv2.imread(test_image_path)
        
        # Detect face first (using face_recognition)
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        face_locations = face_recognition.face_locations(rgb_image)
        
        if face_locations:
            print(f"\nFound {len(face_locations)} face(s)")
            
            # Extract features from first face
            face_location = face_locations[0]
            top, right, bottom, left = face_location
            face_img = image[top:bottom, left:right]
            
            print("\nExtracting all features...")
            result = extractor.extract_all(face_img, face_location)
            
            # Print results
            print("\n128D Encoding:")
            if result['encoding'] is not None:
                print(f"  ✓ Extracted ({result['encoding'].shape[0]} dimensions)")
                print(f"  Sample values: {result['encoding'][:5]}")
            else:
                print("  ✗ Failed to extract")
            
            print("\nFacial Landmarks:")
            if result['landmarks']:
                print(f"  ✓ Extracted {len(result['landmarks'])} landmark groups")
                for key in result['landmarks'].keys():
                    print(f"    - {key}: {len(result['landmarks'][key])} points")
            else:
                print("  ✗ Failed to extract")
            
            print("\nFacial Features:")
            for key, value in result['features'].items():
                if value is not None:
                    if isinstance(value, float):
                        print(f"  {key}: {value:.2f}")
                    else:
                        print(f"  {key}: {value}")
        else:
            print("\nNo faces detected in test image")
    else:
        print(f"\nTest image not found: {test_image_path}")
        print("Extractor initialized successfully but no test image available")
    
    # Print statistics
    print("\n" + "=" * 70)
    print("EXTRACTION STATISTICS")
    print("=" * 70)
    stats = extractor.get_extraction_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    print("\n✓ Deep Feature Extractor test complete")
    print("=" * 70)


if __name__ == "__main__":
    main()
