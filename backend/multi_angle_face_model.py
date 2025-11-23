"""
Multi-Angle Face Recognition Model
Stores and matches faces using 3 angle encodings (center, left, right)
Handles accessories, low light, and partial faces

ENHANCED with bidirectional cross-angle matching:
- Intelligent orientation-aware weighting
- Adaptive tolerance for challenging conditions
- 70% minimum confidence threshold
- Comprehensive photo analysis
"""

import face_recognition
import numpy as np
import os
import pickle
import logging
import cv2

# Import configuration
try:
    from face_recognition_config import (
        MINIMUM_MATCH_CONFIDENCE,
        TOLERANCE_NORMAL,
        TOLERANCE_WITH_ACCESSORIES,
        TOLERANCE_LOW_QUALITY,
        TOLERANCE_SIDE_PROFILE,
        TOLERANCE_PARTIAL_FACE,
        get_tolerance_for_conditions,
        get_weights_for_orientation
    )
    USE_CONFIG = True
except ImportError:
    USE_CONFIG = False
    logger.warning("Configuration file not found, using default values")

# Setup logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class MultiAngleFaceModel:
    """
    Enhanced face recognition model with multi-angle encoding support
    
    Features:
    - Multi-angle encoding storage (center, left, right)
    - Intelligent cross-angle weighted matching
    - Orientation-aware matching
    - Adaptive tolerance for challenging conditions
    - 70% minimum confidence threshold
    """
    
    # Tolerance settings for different scenarios
    if USE_CONFIG:
        TOLERANCE_SETTINGS = {
            'default': TOLERANCE_NORMAL,
            'with_accessories': TOLERANCE_WITH_ACCESSORIES,
            'low_light': TOLERANCE_LOW_QUALITY,
            'side_profile': TOLERANCE_SIDE_PROFILE,
            'partial_face': TOLERANCE_PARTIAL_FACE
        }
    else:
        TOLERANCE_SETTINGS = {
            'default': 0.6,
            'with_accessories': 0.65,
            'low_light': 0.65,
            'side_profile': 0.62,
            'partial_face': 0.68
        }
    
    def __init__(self, data_file='multi_angle_faces.dat'):
        """
        Initialize the multi-angle face model
        
        Data structure:
        {
            'person_0001': {
                'encodings': {
                    'center': np.array(...),
                    'left': np.array(...),
                    'right': np.array(...)
                },
                'metadata': {
                    'created_at': '2025-11-22',
                    'quality_scores': {'center': 85.5, 'left': 82.3, 'right': 88.1}
                }
            }
        }
        """
        self.data_file = data_file
        self.known_faces = {}  # person_id -> {encodings, metadata}
        self.load_model()
    
    def load_model(self):
        """Load multi-angle face data from file"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'rb') as f:
                    self.known_faces = pickle.load(f)
                logger.info(f"--- [MULTI-ANGLE MODEL] Loaded {len(self.known_faces)} known faces ---")
                
                # Log encoding counts
                for person_id, data in self.known_faces.items():
                    angle_count = len(data.get('encodings', {}))
                    logger.debug(f"  {person_id}: {angle_count} angle encodings")
            except Exception as e:
                logger.error(f"--- [MULTI-ANGLE MODEL] Error loading: {e}. Starting fresh ---")
                self.known_faces = {}
        else:
            logger.info("--- [MULTI-ANGLE MODEL] No existing data file. Starting fresh ---")
    
    def save_model(self):
        """Save multi-angle face data to file"""
        try:
            with open(self.data_file, 'wb') as f:
                pickle.dump(self.known_faces, f)
            logger.info(f"--- [MULTI-ANGLE MODEL] Saved {len(self.known_faces)} faces ---")
        except Exception as e:
            logger.error(f"--- [MULTI-ANGLE MODEL] Error saving: {e} ---")
    
    def learn_face_multi_angle(self, encodings_dict, quality_scores=None):
        """
        Learn a new face with multiple angle encodings
        
        Args:
            encodings_dict: {'center': encoding, 'left': encoding, 'right': encoding}
            quality_scores: Optional quality scores for each angle
        
        Returns:
            person_id: Assigned or matched person ID
        """
        if not encodings_dict or 'center' not in encodings_dict:
            logger.error("--- [MULTI-ANGLE MODEL] No center encoding provided ---")
            return None
        
        # Check if this person already exists (using center encoding)
        center_encoding = encodings_dict['center']
        existing_person_id = self._find_existing_person(center_encoding)
        
        if existing_person_id:
            logger.info(f"--- [MULTI-ANGLE MODEL] Matched existing person: {existing_person_id} ---")
            # Update encodings if better quality
            self._update_encodings_if_better(existing_person_id, encodings_dict, quality_scores)
            return existing_person_id
        else:
            # Create new person
            new_id = f"person_{len(self.known_faces) + 1:04d}"
            self.known_faces[new_id] = {
                'encodings': encodings_dict,
                'metadata': {
                    'quality_scores': quality_scores or {},
                    'angle_count': len(encodings_dict)
                }
            }
            logger.info(f"--- [MULTI-ANGLE MODEL] Created new person: {new_id} with {len(encodings_dict)} angles ---")
            self.save_model()
            return new_id
    
    def _find_existing_person(self, encoding, tolerance=0.5):
        """
        Find if encoding matches an existing person
        
        Args:
            encoding: Face encoding to match
            tolerance: Distance threshold for matching
        
        Returns:
            person_id or None
        """
        if not self.known_faces:
            return None
        
        best_match_id = None
        best_distance = float('inf')
        
        for person_id, data in self.known_faces.items():
            encodings = data.get('encodings', {})
            
            # Compare against all stored angles
            for angle, stored_encoding in encodings.items():
                distance = face_recognition.face_distance([stored_encoding], encoding)[0]
                
                if distance < best_distance:
                    best_distance = distance
                    best_match_id = person_id
        
        if best_distance <= tolerance:
            logger.debug(f"Found existing person {best_match_id} with distance {best_distance:.2f}")
            return best_match_id
        
        return None
    
    def _update_encodings_if_better(self, person_id, new_encodings, new_quality_scores):
        """Update encodings if new ones have better quality"""
        if person_id not in self.known_faces:
            return
        
        current_data = self.known_faces[person_id]
        current_encodings = current_data.get('encodings', {})
        current_quality = current_data.get('metadata', {}).get('quality_scores', {})
        
        updated = False
        for angle, new_encoding in new_encodings.items():
            new_quality = new_quality_scores.get(angle, 0) if new_quality_scores else 0
            current_q = current_quality.get(angle, 0)
            
            if angle not in current_encodings or new_quality > current_q:
                current_encodings[angle] = new_encoding
                current_quality[angle] = new_quality
                updated = True
                logger.debug(f"Updated {angle} encoding for {person_id}")
        
        if updated:
            self.known_faces[person_id]['encodings'] = current_encodings
            self.known_faces[person_id]['metadata']['quality_scores'] = current_quality
            self.save_model()
    
    def recognize_face_multi_angle(self, photo_encoding, adaptive_tolerance=True, photo_orientation=None, 
                                   has_accessories=False, quality_score=1.0):
        """
        ENHANCED: Recognize face using intelligent cross-angle weighted matching
        
        This implements the bidirectional multi-angle matching algorithm that:
        - Compares photo against ALL stored angles (center, left, right)
        - Applies intelligent weighting based on detected photo orientation
        - Uses adaptive tolerance for accessories, lighting, and quality
        - Enforces 70% minimum confidence threshold
        
        Args:
            photo_encoding: Encoding from uploaded photo
            adaptive_tolerance: Use adaptive tolerance based on conditions
            photo_orientation: Detected orientation ('center', 'left', 'right', 'angle_left', 'angle_right', 'unknown')
            has_accessories: Whether photo shows accessories (sunglasses, mask, etc.)
            quality_score: Image quality score (0-1)
        
        Returns:
            Tuple of (person_id, confidence, best_angle, distance, match_details)
        """
        if not self.known_faces:
            logger.warning("--- [MULTI-ANGLE MODEL] No known faces to match against ---")
            return None, 0.0, None, float('inf'), {}
        
        best_person_id = None
        best_weighted_distance = float('inf')
        best_match_details = {}
        
        # CRITICAL: Compare against ALL known faces using weighted cross-angle matching
        for person_id, data in self.known_faces.items():
            encodings = data.get('encodings', {})
            
            # Calculate distances to ALL three stored angles
            distance_to_center = float('inf')
            distance_to_left = float('inf')
            distance_to_right = float('inf')
            
            if 'center' in encodings:
                distance_to_center = face_recognition.face_distance([encodings['center']], photo_encoding)[0]
            if 'left' in encodings:
                distance_to_left = face_recognition.face_distance([encodings['left']], photo_encoding)[0]
            if 'right' in encodings:
                distance_to_right = face_recognition.face_distance([encodings['right']], photo_encoding)[0]
            
            logger.debug(f"  {person_id} - Center: {distance_to_center:.3f}, Left: {distance_to_left:.3f}, Right: {distance_to_right:.3f}")
            
            # SMART WEIGHTING: Apply orientation-aware weights
            if photo_orientation == 'center':
                # Photo is frontal - prioritize center encoding
                weighted_distance = (
                    distance_to_center * 0.6 +  # 60% weight to center
                    distance_to_left * 0.2 +     # 20% weight to left
                    distance_to_right * 0.2      # 20% weight to right
                )
                primary_distance = distance_to_center
                
            elif photo_orientation == 'left' or photo_orientation == 'angle_left':
                # Photo shows left profile - prioritize left encoding
                weighted_distance = (
                    distance_to_left * 0.6 +     # 60% weight to left
                    distance_to_center * 0.3 +   # 30% weight to center
                    distance_to_right * 0.1      # 10% weight to right
                )
                primary_distance = distance_to_left
                
            elif photo_orientation == 'right' or photo_orientation == 'angle_right':
                # Photo shows right profile - prioritize right encoding
                weighted_distance = (
                    distance_to_right * 0.6 +    # 60% weight to right
                    distance_to_center * 0.3 +   # 30% weight to center
                    distance_to_left * 0.1       # 10% weight to left
                )
                primary_distance = distance_to_right
                
            else:
                # Unknown orientation - use minimum distance approach
                primary_distance = min(distance_to_center, distance_to_left, distance_to_right)
                weighted_distance = (distance_to_center + distance_to_left + distance_to_right) / 3
            
            # Use the BEST (minimum) distance for final decision
            final_distance = min(primary_distance, weighted_distance)
            
            if final_distance < best_weighted_distance:
                best_weighted_distance = final_distance
                best_person_id = person_id
                best_match_details = {
                    'person_id': person_id,
                    'photo_orientation': photo_orientation or 'unknown',
                    'distance_to_center': distance_to_center,
                    'distance_to_left': distance_to_left,
                    'distance_to_right': distance_to_right,
                    'weighted_distance': weighted_distance,
                    'primary_distance': primary_distance,
                    'final_distance': final_distance,
                    'has_accessories': has_accessories,
                    'quality_score': quality_score
                }
        
        # ADAPTIVE TOLERANCE based on photo conditions
        base_tolerance = self.TOLERANCE_SETTINGS['default']  # 0.6
        
        # Adjust tolerance for challenging conditions
        if has_accessories:
            base_tolerance = self.TOLERANCE_SETTINGS['with_accessories']  # 0.65
        
        if quality_score < 0.5:
            base_tolerance += 0.05  # More lenient for low quality
        
        if photo_orientation in ['left', 'right', 'angle_left', 'angle_right']:
            base_tolerance = max(base_tolerance, self.TOLERANCE_SETTINGS['side_profile'])  # 0.62
        
        # Convert distance to confidence percentage (0-100%)
        # Distance of 0 = 100% match, Distance of 1 = 0% match
        confidence_percentage = max(0, (1 - best_weighted_distance) * 100)
        
        # CRITICAL: Apply 70% minimum threshold requirement
        # Convert tolerance to minimum confidence requirement
        min_confidence_required = (1 - base_tolerance) * 100
        
        # Override if calculated threshold is higher than 70%
        MINIMUM_MATCH_THRESHOLD = 70.0  # 70% confidence as per requirements
        if min_confidence_required > MINIMUM_MATCH_THRESHOLD:
            min_confidence_required = MINIMUM_MATCH_THRESHOLD
        
        # Determine if it's a match
        is_match = confidence_percentage >= min_confidence_required
        
        # Update match details
        best_match_details.update({
            'confidence_percentage': round(confidence_percentage, 2),
            'min_confidence_required': round(min_confidence_required, 2),
            'is_match': is_match,
            'tolerance_used': base_tolerance
        })
        
        # Log the matching attempt
        if is_match:
            logger.info(f"--- [MULTI-ANGLE MODEL] ✓ MATCH: {best_person_id} ---")
            logger.info(f"    Confidence: {confidence_percentage:.1f}% (threshold: {min_confidence_required:.1f}%)")
            logger.info(f"    Orientation: {photo_orientation}, Distance: {best_weighted_distance:.3f}")
            return best_person_id, confidence_percentage, photo_orientation, best_weighted_distance, best_match_details
        else:
            logger.info(f"--- [MULTI-ANGLE MODEL] NO MATCH ---")
            logger.info(f"    Best: {best_person_id}, Confidence: {confidence_percentage:.1f}% < {min_confidence_required:.1f}%")
            logger.info(f"    Distance: {best_weighted_distance:.3f} > Tolerance: {base_tolerance}")
            return None, 0.0, None, best_weighted_distance, best_match_details
    
    def get_all_encodings_flat(self):
        """
        Get all encodings as flat lists (for backward compatibility)
        
        Returns:
            Tuple of (encodings_list, ids_list)
        """
        all_encodings = []
        all_ids = []
        
        for person_id, data in self.known_faces.items():
            encodings = data.get('encodings', {})
            for angle, encoding in encodings.items():
                all_encodings.append(encoding)
                all_ids.append(f"{person_id}_{angle}")
        
        return all_encodings, all_ids
    
    def get_person_encodings(self, person_id):
        """Get all encodings for a specific person"""
        if person_id in self.known_faces:
            return self.known_faces[person_id].get('encodings', {})
        return {}
    
    def migrate_from_old_model(self, old_encodings, old_ids):
        """
        Migrate data from old single-encoding model
        
        Args:
            old_encodings: List of encodings from old model
            old_ids: List of person IDs from old model
        """
        logger.info(f"--- [MULTI-ANGLE MODEL] Migrating {len(old_ids)} faces from old model ---")
        
        for encoding, person_id in zip(old_encodings, old_ids):
            if person_id not in self.known_faces:
                # Store old encoding as 'center' angle
                self.known_faces[person_id] = {
                    'encodings': {'center': encoding},
                    'metadata': {
                        'migrated': True,
                        'angle_count': 1
                    }
                }
                logger.debug(f"  Migrated {person_id} (center only)")
        
        self.save_model()
        logger.info("--- [MULTI-ANGLE MODEL] Migration complete ---")


# Utility functions for image preprocessing and detection

def preprocess_image_for_recognition(image):
    """
    Enhance image quality before face detection and encoding
    
    Args:
        image: Input image (RGB format)
    
    Returns:
        Enhanced image
    """
    try:
        # Convert to RGB if needed
        if len(image.shape) == 2:  # Grayscale
            image = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
        
        # Enhance brightness and contrast using CLAHE
        lab = cv2.cvtColor(image, cv2.COLOR_RGB2LAB)
        l, a, b = cv2.split(lab)
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
        l = clahe.apply(l)
        enhanced = cv2.merge([l, a, b])
        enhanced = cv2.cvtColor(enhanced, cv2.COLOR_LAB2RGB)
        
        # Denoise
        denoised = cv2.fastNlMeansDenoisingColored(enhanced, None, 10, 10, 7, 21)
        
        logger.debug("Image preprocessing complete")
        return denoised
    except Exception as e:
        logger.error(f"Error in preprocessing: {e}")
        return image


def detect_sunglasses(image, face_location):
    """
    Detect if person is wearing sunglasses
    
    Args:
        image: Face image (RGB)
        face_location: Face bounding box (top, right, bottom, left)
    
    Returns:
        True if sunglasses detected
    """
    try:
        # Get facial landmarks
        landmarks = face_recognition.face_landmarks(image, [face_location])
        
        if not landmarks:
            return False
        
        # Extract eye region
        top, right, bottom, left = face_location
        eye_region = image[top:bottom, left:right]
        
        # Convert to grayscale
        gray = cv2.cvtColor(eye_region, cv2.COLOR_RGB2GRAY)
        
        # Calculate mean intensity in eye regions
        mean_intensity = np.mean(gray)
        
        # If very dark, likely wearing sunglasses
        is_dark = mean_intensity < 50
        
        if is_dark:
            logger.debug(f"Sunglasses detected (intensity: {mean_intensity:.1f})")
        
        return is_dark
    except Exception as e:
        logger.error(f"Error detecting sunglasses: {e}")
        return False


def detect_face_orientation(image, face_location):
    """
    Detect if face is frontal, left profile, or right profile
    
    Args:
        image: Face image (RGB format)
        face_location: Face bounding box (top, right, bottom, left)
    
    Returns:
        str: 'center', 'left', 'right', 'angle_left', 'angle_right', or 'unknown'
    """
    try:
        # Get facial landmarks
        face_landmarks_list = face_recognition.face_landmarks(image, [face_location])
        
        if len(face_landmarks_list) == 0:
            logger.debug("No landmarks detected for orientation")
            return 'unknown'
        
        landmarks = face_landmarks_list[0]
        
        # Get key facial features
        nose_bridge = landmarks.get('nose_bridge', [])
        left_eye = landmarks.get('left_eye', [])
        right_eye = landmarks.get('right_eye', [])
        left_eyebrow = landmarks.get('left_eyebrow', [])
        right_eyebrow = landmarks.get('right_eyebrow', [])
        
        if not nose_bridge or not left_eye or not right_eye:
            return 'unknown'
        
        # Calculate visibility of left vs right features
        top, right_bound, bottom, left_bound = face_location
        face_width = right_bound - left_bound
        face_center_x = (left_bound + right_bound) / 2
        
        # Count visible points for each side
        left_features = left_eyebrow + left_eye
        right_features = right_eyebrow + right_eye
        
        left_visibility = len([p for p in left_features if left_bound <= p[0] <= right_bound])
        right_visibility = len([p for p in right_features if left_bound <= p[0] <= right_bound])
        
        # Calculate nose bridge angle
        if len(nose_bridge) >= 2:
            nose_start = np.array(nose_bridge[0])
            nose_end = np.array(nose_bridge[-1])
            nose_vector = nose_end - nose_start
            
            # Calculate horizontal offset of nose from face center
            nose_center_x = np.mean([p[0] for p in nose_bridge])
            nose_offset = nose_center_x - face_center_x
            nose_offset_ratio = nose_offset / (face_width / 2) if face_width > 0 else 0
        else:
            nose_offset_ratio = 0
        
        # Determine orientation based on feature visibility and nose position
        visibility_diff = left_visibility - right_visibility
        
        logger.debug(f"Orientation detection - Left vis: {left_visibility}, Right vis: {right_visibility}, "
                    f"Nose offset ratio: {nose_offset_ratio:.2f}")
        
        # Frontal face: both sides visible, nose centered
        if abs(visibility_diff) <= 3 and abs(nose_offset_ratio) < 0.15:
            return 'center'
        
        # Left profile: right side more visible, nose shifted left
        elif visibility_diff < -3 or nose_offset_ratio < -0.15:
            if abs(nose_offset_ratio) > 0.35 or visibility_diff < -6:
                return 'left'  # Strong left profile
            else:
                return 'angle_left'  # Slight left turn
        
        # Right profile: left side more visible, nose shifted right
        elif visibility_diff > 3 or nose_offset_ratio > 0.15:
            if abs(nose_offset_ratio) > 0.35 or visibility_diff > 6:
                return 'right'  # Strong right profile
            else:
                return 'angle_right'  # Slight right turn
        
        else:
            return 'center'  # Default to center
    
    except Exception as e:
        logger.error(f"Error detecting face orientation: {e}")
        return 'unknown'


def assess_image_quality(image, face_location):
    """
    Assess quality of the face region
    
    Args:
        image: Face image (RGB format)
        face_location: Face bounding box (top, right, bottom, left)
    
    Returns:
        float: Quality score from 0 (poor) to 1 (excellent)
    """
    try:
        top, right, bottom, left = face_location
        face_region = image[top:bottom, left:right]
        
        if face_region.size == 0:
            return 0.0
        
        # Convert to grayscale
        gray = cv2.cvtColor(face_region, cv2.COLOR_RGB2GRAY)
        
        # 1. Check sharpness using Laplacian variance
        laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
        sharpness_score = min(laplacian_var / 500, 1.0)  # Normalize
        
        # 2. Check brightness
        mean_brightness = np.mean(gray)
        brightness_score = 1.0 - abs(mean_brightness - 127) / 127  # Optimal at 127
        
        # 3. Check contrast
        contrast = gray.std()
        contrast_score = min(contrast / 50, 1.0)  # Normalize
        
        # 4. Check resolution
        face_width = right - left
        face_height = bottom - top
        resolution_score = min(min(face_width, face_height) / 100, 1.0)
        
        # Combined quality score
        quality_score = (
            sharpness_score * 0.3 +
            brightness_score * 0.25 +
            contrast_score * 0.25 +
            resolution_score * 0.2
        )
        
        logger.debug(f"Quality assessment - Sharpness: {sharpness_score:.2f}, Brightness: {brightness_score:.2f}, "
                    f"Contrast: {contrast_score:.2f}, Resolution: {resolution_score:.2f}, Overall: {quality_score:.2f}")
        
        return quality_score
    
    except Exception as e:
        logger.error(f"Error assessing image quality: {e}")
        return 0.5  # Return neutral score on error


def analyze_photo_all_faces_all_angles(photo_path):
    """
    CRITICAL FUNCTION: Extract encodings from ALL faces in photo with orientation detection
    
    This function:
    - Loads and preprocesses the image
    - Detects all faces using robust detection
    - Generates encodings for each face
    - Detects face orientation (center, left, right, etc.)
    - Detects accessories (sunglasses, masks)
    - Assesses image quality
    
    Args:
        photo_path: Path to photo file
    
    Returns:
        List of face data dictionaries, each containing:
        {
            'face_index': int,
            'encoding': np.ndarray,
            'orientation': str,
            'location': tuple,
            'has_sunglasses': bool,
            'has_mask': bool,
            'quality_score': float
        }
    """
    try:
        # Load image
        image = face_recognition.load_image_file(photo_path)
        
        # Preprocess for better detection
        image = preprocess_image_for_recognition(image)
        
        # Detect all faces
        face_locations = face_recognition.face_locations(image, model='cnn')  # Use CNN for better accuracy
        
        if len(face_locations) == 0:
            logger.warning(f"No faces detected in {photo_path}")
            return []
        
        logger.info(f"Detected {len(face_locations)} face(s) in {photo_path}")
        
        faces_data = []
        
        # Process each detected face
        for idx, face_location in enumerate(face_locations):
            try:
                # Generate encoding for this face
                face_encodings = face_recognition.face_encodings(image, [face_location])
                
                if not face_encodings:
                    logger.warning(f"Could not generate encoding for face {idx}")
                    continue
                
                face_encoding = face_encodings[0]
                
                # Detect face orientation
                orientation = detect_face_orientation(image, face_location)
                
                # Detect accessories
                has_sunglasses = detect_sunglasses(image, face_location)
                has_mask = False  # TODO: Implement mask detection if needed
                
                # Assess image quality
                quality_score = assess_image_quality(image, face_location)
                
                faces_data.append({
                    'face_index': idx,
                    'encoding': face_encoding,
                    'orientation': orientation,
                    'location': face_location,
                    'has_sunglasses': has_sunglasses,
                    'has_mask': has_mask,
                    'quality_score': quality_score
                })
                
                logger.debug(f"Face {idx}: orientation={orientation}, quality={quality_score:.2f}, "
                           f"sunglasses={has_sunglasses}")
            
            except Exception as e:
                logger.error(f"Error processing face {idx} in {photo_path}: {e}")
                continue
        
        return faces_data
    
    except Exception as e:
        logger.error(f"Error analyzing photo {photo_path}: {e}")
        return []
