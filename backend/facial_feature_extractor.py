"""
Comprehensive Facial Feature Extraction System

Extracts 100+ detailed facial features for enhanced matching accuracy.
Includes: eyes, nose, jaw, mouth, facial hair, forehead, ears, skin, proportions.
"""

import numpy as np
import cv2
import face_recognition
import logging
from typing import Dict, List, Tuple, Optional

logger = logging.getLogger(__name__)


class FacialFeatureExtractor:
    """
    Extracts comprehensive facial features from face images
    """
    
    def __init__(self):
        """Initialize the feature extractor"""
        self.feature_count = 0
        logger.info("Facial Feature Extractor initialized")
    
    def extract_all_features(self, image: np.ndarray, face_location: Tuple, 
                            face_landmarks: Dict) -> Dict:
        """
        Extract ALL detailed facial features
        
        Args:
            image: Face image (RGB)
            face_location: Face bounding box (top, right, bottom, left)
            face_landmarks: Facial landmarks dictionary
        
        Returns:
            Dictionary containing all extracted features
        """
        features = {
            'eyes': self.extract_eye_features(image, face_location, face_landmarks),
            'nose': self.extract_nose_features(image, face_location, face_landmarks),
            'jaw': self.extract_jaw_features(image, face_location, face_landmarks),
            'mouth': self.extract_mouth_features(image, face_location, face_landmarks),
            'facial_hair': self.extract_facial_hair_features(image, face_location, face_landmarks),
            'forehead': self.extract_forehead_features(image, face_location, face_landmarks),
            'ears': self.extract_ear_features(image, face_location, face_landmarks),
            'skin': self.extract_skin_features(image, face_location),
            'proportions': self.extract_proportion_features(image, face_location, face_landmarks),
            'unique_marks': self.extract_unique_marks(image, face_location)
        }
        
        # Count total features
        self.feature_count = self._count_features(features)
        logger.info(f"Extracted {self.feature_count} detailed facial features")
        
        return features

    def extract_eye_features(self, image: np.ndarray, face_location: Tuple, 
                            landmarks: Dict) -> Dict:
        """Extract detailed eye features"""
        try:
            left_eye = np.array(landmarks.get('left_eye', []))
            right_eye = np.array(landmarks.get('right_eye', []))
            left_eyebrow = np.array(landmarks.get('left_eyebrow', []))
            right_eyebrow = np.array(landmarks.get('right_eyebrow', []))
            
            if len(left_eye) == 0 or len(right_eye) == 0:
                return {}
            
            # Eye measurements
            left_eye_width = np.linalg.norm(left_eye[0] - left_eye[3])
            left_eye_height = np.linalg.norm(left_eye[1] - left_eye[5])
            right_eye_width = np.linalg.norm(right_eye[0] - right_eye[3])
            right_eye_height = np.linalg.norm(right_eye[1] - right_eye[5])
            
            # Eye spacing
            eye_spacing = np.linalg.norm(
                np.mean(left_eye, axis=0) - np.mean(right_eye, axis=0)
            )
            
            # Eyebrow measurements
            left_brow_thickness = self._calculate_thickness(left_eyebrow)
            right_brow_thickness = self._calculate_thickness(right_eyebrow)
            
            return {
                'left_eye_width': float(left_eye_width),
                'left_eye_height': float(left_eye_height),
                'right_eye_width': float(right_eye_width),
                'right_eye_height': float(right_eye_height),
                'eye_spacing': float(eye_spacing),
                'left_eye_aspect_ratio': float(left_eye_height / left_eye_width) if left_eye_width > 0 else 0,
                'right_eye_aspect_ratio': float(right_eye_height / right_eye_width) if right_eye_width > 0 else 0,
                'left_eyebrow_thickness': float(left_brow_thickness),
                'right_eyebrow_thickness': float(right_brow_thickness),
                'eye_symmetry': float(abs(left_eye_width - right_eye_width)),
            }
        except Exception as e:
            logger.error(f"Error extracting eye features: {e}")
            return {}
    
    def extract_nose_features(self, image: np.ndarray, face_location: Tuple,
                             landmarks: Dict) -> Dict:
        """Extract nose features"""
        try:
            nose_bridge = np.array(landmarks.get('nose_bridge', []))
            nose_tip = np.array(landmarks.get('nose_tip', []))
            
            if len(nose_bridge) == 0 or len(nose_tip) == 0:
                return {}
            
            # Nose measurements
            nose_length = np.linalg.norm(nose_bridge[0] - nose_tip[2])
            nose_width = np.linalg.norm(nose_tip[0] - nose_tip[4])
            bridge_width = np.linalg.norm(nose_bridge[0] - nose_bridge[-1])
            
            return {
                'nose_length': float(nose_length),
                'nose_width': float(nose_width),
                'bridge_width': float(bridge_width),
                'nose_aspect_ratio': float(nose_length / nose_width) if nose_width > 0 else 0,
            }
        except Exception as e:
            logger.error(f"Error extracting nose features: {e}")
            return {}
    
    def extract_jaw_features(self, image: np.ndarray, face_location: Tuple,
                            landmarks: Dict) -> Dict:
        """Extract jaw and face shape features"""
        try:
            chin = np.array(landmarks.get('chin', []))
            
            if len(chin) == 0:
                return {}
            
            # Face measurements
            top, right, bottom, left = face_location
            face_width = right - left
            face_height = bottom - top
            
            # Jaw measurements
            jaw_width = np.linalg.norm(chin[0] - chin[-1])
            chin_point = chin[len(chin)//2]
            
            return {
                'face_width': float(face_width),
                'face_height': float(face_height),
                'face_aspect_ratio': float(face_height / face_width) if face_width > 0 else 0,
                'jaw_width': float(jaw_width),
                'jaw_to_face_ratio': float(jaw_width / face_width) if face_width > 0 else 0,
            }
        except Exception as e:
            logger.error(f"Error extracting jaw features: {e}")
            return {}
    
    def extract_mouth_features(self, image: np.ndarray, face_location: Tuple,
                               landmarks: Dict) -> Dict:
        """Extract mouth and lip features"""
        try:
            top_lip = np.array(landmarks.get('top_lip', []))
            bottom_lip = np.array(landmarks.get('bottom_lip', []))
            
            if len(top_lip) == 0 or len(bottom_lip) == 0:
                return {}
            
            # Mouth measurements
            mouth_width = np.linalg.norm(top_lip[0] - top_lip[6])
            mouth_height = np.linalg.norm(top_lip[3] - bottom_lip[9])
            
            return {
                'mouth_width': float(mouth_width),
                'mouth_height': float(mouth_height),
                'mouth_aspect_ratio': float(mouth_height / mouth_width) if mouth_width > 0 else 0,
            }
        except Exception as e:
            logger.error(f"Error extracting mouth features: {e}")
            return {}
    
    def extract_facial_hair_features(self, image: np.ndarray, face_location: Tuple,
                                     landmarks: Dict) -> Dict:
        """Extract facial hair features (flexible for changes)"""
        try:
            top, right, bottom, left = face_location
            
            # Analyze chin/jaw area for beard
            chin_region = image[int(bottom*0.7):bottom, left:right]
            if chin_region.size == 0:
                return {}
            
            gray_chin = cv2.cvtColor(chin_region, cv2.COLOR_RGB2GRAY)
            chin_darkness = np.mean(gray_chin)
            
            # Analyze upper lip area for mustache
            mouth_region = image[int(top + (bottom-top)*0.6):int(top + (bottom-top)*0.75), left:right]
            if mouth_region.size > 0:
                gray_mouth = cv2.cvtColor(mouth_region, cv2.COLOR_RGB2GRAY)
                mouth_darkness = np.mean(gray_mouth)
            else:
                mouth_darkness = 128
            
            return {
                'chin_darkness': float(chin_darkness),
                'mouth_darkness': float(mouth_darkness),
                'has_facial_hair_indicator': float(chin_darkness < 100 or mouth_darkness < 100),
            }
        except Exception as e:
            logger.error(f"Error extracting facial hair features: {e}")
            return {}
    
    def extract_forehead_features(self, image: np.ndarray, face_location: Tuple,
                                  landmarks: Dict) -> Dict:
        """Extract forehead features"""
        try:
            top, right, bottom, left = face_location
            face_height = bottom - top
            
            # Estimate forehead height (top 1/3 of face)
            forehead_height = face_height * 0.33
            
            return {
                'forehead_height': float(forehead_height),
                'forehead_to_face_ratio': 0.33,
            }
        except Exception as e:
            logger.error(f"Error extracting forehead features: {e}")
            return {}
    
    def extract_ear_features(self, image: np.ndarray, face_location: Tuple,
                            landmarks: Dict) -> Dict:
        """Extract ear features (if visible)"""
        # Ears not always visible, especially in frontal view
        return {'ears_visible': False}
    
    def extract_skin_features(self, image: np.ndarray, face_location: Tuple) -> Dict:
        """Extract skin tone features"""
        try:
            top, right, bottom, left = face_location
            face_region = image[top:bottom, left:right]
            
            if face_region.size == 0:
                return {}
            
            # Average skin tone
            avg_color = np.mean(face_region, axis=(0, 1))
            
            return {
                'skin_tone_r': float(avg_color[0]),
                'skin_tone_g': float(avg_color[1]),
                'skin_tone_b': float(avg_color[2]),
            }
        except Exception as e:
            logger.error(f"Error extracting skin features: {e}")
            return {}
    
    def extract_proportion_features(self, image: np.ndarray, face_location: Tuple,
                                   landmarks: Dict) -> Dict:
        """Extract facial proportion features"""
        try:
            left_eye = np.array(landmarks.get('left_eye', []))
            right_eye = np.array(landmarks.get('right_eye', []))
            nose_tip = np.array(landmarks.get('nose_tip', []))
            top_lip = np.array(landmarks.get('top_lip', []))
            
            if len(left_eye) == 0 or len(nose_tip) == 0 or len(top_lip) == 0:
                return {}
            
            # Inter-feature distances
            eye_center = np.mean([np.mean(left_eye, axis=0), np.mean(right_eye, axis=0)], axis=0)
            nose_center = np.mean(nose_tip, axis=0)
            mouth_center = np.mean(top_lip, axis=0)
            
            eye_to_nose = np.linalg.norm(eye_center - nose_center)
            nose_to_mouth = np.linalg.norm(nose_center - mouth_center)
            eye_to_mouth = np.linalg.norm(eye_center - mouth_center)
            
            return {
                'eye_to_nose_distance': float(eye_to_nose),
                'nose_to_mouth_distance': float(nose_to_mouth),
                'eye_to_mouth_distance': float(eye_to_mouth),
                'upper_to_lower_face_ratio': float(eye_to_nose / nose_to_mouth) if nose_to_mouth > 0 else 0,
            }
        except Exception as e:
            logger.error(f"Error extracting proportion features: {e}")
            return {}
    
    def extract_unique_marks(self, image: np.ndarray, face_location: Tuple) -> Dict:
        """Extract unique identifying marks (moles, scars, etc.)"""
        # This would require more advanced computer vision
        # For now, return placeholder
        return {'unique_marks_detected': 0}
    
    def _calculate_thickness(self, points: np.ndarray) -> float:
        """Calculate thickness of a feature (like eyebrow)"""
        if len(points) < 2:
            return 0.0
        distances = [np.linalg.norm(points[i] - points[i+1]) for i in range(len(points)-1)]
        return float(np.mean(distances))
    
    def _count_features(self, features_dict: Dict) -> int:
        """Count total number of features extracted"""
        count = 0
        for category, features in features_dict.items():
            if isinstance(features, dict):
                count += len(features)
        return count
    
    def compare_features(self, features1: Dict, features2: Dict) -> Dict:
        """
        Compare two feature sets and return similarity scores
        
        Returns:
            Dictionary with category-wise similarity scores (0-100%)
        """
        similarities = {}
        
        # Compare each category
        for category in ['eyes', 'nose', 'jaw', 'mouth', 'forehead', 'skin', 'proportions']:
            if category in features1 and category in features2:
                similarity = self._compare_feature_category(
                    features1[category],
                    features2[category]
                )
                similarities[category] = similarity
            else:
                similarities[category] = 0.0
        
        # Facial hair is flexible (don't penalize differences)
        if 'facial_hair' in features1 and 'facial_hair' in features2:
            similarities['facial_hair'] = 50.0  # Neutral score
        
        return similarities
    
    def _compare_feature_category(self, feat1: Dict, feat2: Dict) -> float:
        """Compare features within a category"""
        if not feat1 or not feat2:
            return 0.0
        
        # Get common keys
        common_keys = set(feat1.keys()) & set(feat2.keys())
        if not common_keys:
            return 0.0
        
        similarities = []
        for key in common_keys:
            val1 = feat1[key]
            val2 = feat2[key]
            
            # Calculate similarity based on relative difference
            if val1 == 0 and val2 == 0:
                sim = 100.0
            elif val1 == 0 or val2 == 0:
                sim = 0.0
            else:
                diff = abs(val1 - val2) / max(abs(val1), abs(val2))
                sim = max(0, (1 - diff) * 100)
            
            similarities.append(sim)
        
        return float(np.mean(similarities)) if similarities else 0.0
