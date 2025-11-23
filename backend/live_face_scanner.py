"""
Live Face Scanning System for PicMe
Multi-angle face capture for accurate photo matching

Features:
- 3-angle face capture (front, left, right)
- Real-time face detection and alignment
- Quality validation
- Composite encoding generation
- Secure storage
"""

import cv2
import numpy as np
import face_recognition
from typing import List, Tuple, Dict, Optional
import base64
from datetime import datetime
import json

class LiveFaceScanner:
    """
    Live face scanning system with multi-angle capture
    
    ENHANCED with duplicate pose prevention:
    - Validates each pose is genuinely different
    - Prevents saving CENTER encoding for LEFT/RIGHT scans
    - Real-time pose angle feedback
    """
    
    # Face capture angles with STRICT validation ranges
    ANGLES = {
        'front': {
            'name': 'Front', 
            'instruction': 'Look straight at the camera', 
            'yaw_range': (-15, 15),
            'min_angle': -15,
            'max_angle': 15
        },
        'left': {
            'name': 'Left Side', 
            'instruction': 'Turn your face to the LEFT', 
            'yaw_range': (-90, -25),
            'min_angle': -90,
            'max_angle': -25
        },
        'right': {
            'name': 'Right Side', 
            'instruction': 'Turn your face to the RIGHT', 
            'yaw_range': (25, 90),
            'min_angle': 25,
            'max_angle': 90
        }
    }
    
    # Pose validation thresholds
    POSE_VALIDATION_THRESHOLD = 20  # Minimum angle difference between poses
    POSE_STABILITY_FRAMES = 5  # Frames to confirm stable pose
    
    # Quality thresholds
    MIN_FACE_SIZE = 100  # Minimum face width/height in pixels
    MAX_FACE_SIZE = 800  # Maximum face width/height in pixels
    MIN_BRIGHTNESS = 40  # Minimum average brightness
    MAX_BRIGHTNESS = 220  # Maximum average brightness
    MIN_SHARPNESS = 50  # Minimum sharpness score
    FACE_DISTANCE_THRESHOLD = 0.6  # For matching
    
    def __init__(self):
        """Initialize the live face scanner"""
        self.current_angle = 'front'
        self.captured_encodings = {}
        self.captured_images = {}
        self.capture_quality = {}
        self.captured_pose_angles = {}  # Store actual angles captured
        self.pose_stable_count = 0  # Count frames with stable pose
        self.last_detected_angle = 0  # Last detected yaw angle
        
        print("--- [LIVE SCANNER] Initialized with pose validation ---")
    
    def detect_face_in_frame(self, frame: np.ndarray) -> Tuple[bool, Optional[Dict], str]:
        """
        ENHANCED: Detect face in frame and validate quality + pose
        
        CRITICAL: Prevents duplicate pose scanning by validating actual head angle
        
        Args:
            frame: Camera frame (BGR format)
        
        Returns:
            Tuple of (face_detected, face_info, feedback_message)
        """
        # Convert to RGB for face_recognition
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Detect faces
        face_locations = face_recognition.face_locations(rgb_frame)
        
        if len(face_locations) == 0:
            self.pose_stable_count = 0
            return False, None, "No face detected. Please position your face in the frame."
        
        if len(face_locations) > 1:
            self.pose_stable_count = 0
            return False, None, "Multiple faces detected. Please ensure only one person is in frame."
        
        # Get face location
        top, right, bottom, left = face_locations[0]
        face_width = right - left
        face_height = bottom - top
        
        # Validate face size
        if face_width < self.MIN_FACE_SIZE or face_height < self.MIN_FACE_SIZE:
            self.pose_stable_count = 0
            return False, None, "Face too small. Please move closer to the camera."
        
        if face_width > self.MAX_FACE_SIZE or face_height > self.MAX_FACE_SIZE:
            self.pose_stable_count = 0
            return False, None, "Face too large. Please move back from the camera."
        
        # Extract face region
        face_region = frame[top:bottom, left:right]
        
        # Check brightness
        gray_face = cv2.cvtColor(face_region, cv2.COLOR_BGR2GRAY)
        avg_brightness = np.mean(gray_face)
        
        if avg_brightness < self.MIN_BRIGHTNESS:
            self.pose_stable_count = 0
            return False, None, "Too dark. Please improve lighting."
        
        if avg_brightness > self.MAX_BRIGHTNESS:
            self.pose_stable_count = 0
            return False, None, "Too bright. Please reduce lighting."
        
        # Check sharpness (using Laplacian variance)
        laplacian = cv2.Laplacian(gray_face, cv2.CV_64F)
        sharpness = laplacian.var()
        
        if sharpness < self.MIN_SHARPNESS:
            self.pose_stable_count = 0
            return False, None, "Image too blurry. Please hold still."
        
        # Get face landmarks for pose estimation
        face_landmarks = face_recognition.face_landmarks(rgb_frame, face_locations)
        
        if not face_landmarks:
            self.pose_stable_count = 0
            return False, None, "Cannot detect facial features. Please adjust position."
        
        # CRITICAL: Calculate accurate yaw angle
        landmarks = face_landmarks[0]
        yaw_angle = self._calculate_yaw_angle(landmarks, face_locations[0])
        self.last_detected_angle = yaw_angle
        
        # CRITICAL: Validate pose is correct for current stage
        is_pose_valid, pose_message = self._validate_pose_for_stage(yaw_angle)
        
        if not is_pose_valid:
            self.pose_stable_count = 0
            return False, None, pose_message
        
        # CRITICAL: Check for duplicate poses
        is_duplicate, dup_message = self._check_duplicate_pose(yaw_angle)
        
        if is_duplicate:
            self.pose_stable_count = 0
            return False, None, dup_message
        
        # Pose is stable - increment counter
        self.pose_stable_count += 1
        
        # Require stable pose for several frames before capturing
        if self.pose_stable_count < self.POSE_STABILITY_FRAMES:
            return False, None, f"Hold steady... ({self.pose_stable_count}/{self.POSE_STABILITY_FRAMES})"
        
        # All checks passed
        face_info = {
            'location': face_locations[0],
            'landmarks': landmarks,
            'brightness': float(avg_brightness),
            'sharpness': float(sharpness),
            'yaw_angle': float(yaw_angle),
            'quality_score': self._calculate_quality_score(avg_brightness, sharpness, face_width)
        }
        
        return True, face_info, f"✓ Perfect! Angle: {yaw_angle:.1f}° - Ready to capture"
    
    def _calculate_quality_score(self, brightness: float, sharpness: float, face_size: int) -> float:
        """
        Calculate overall quality score (0-100)
        
        Args:
            brightness: Average brightness
            sharpness: Sharpness score
            face_size: Face width in pixels
        
        Returns:
            Quality score (0-100)
        """
        # Brightness score (optimal around 120)
        brightness_score = 100 - abs(brightness - 120) / 80 * 100
        brightness_score = max(0, min(100, brightness_score))
        
        # Sharpness score (normalize to 0-100)
        sharpness_score = min(100, (sharpness / 200) * 100)
        
        # Size score (optimal around 300px)
        size_score = 100 - abs(face_size - 300) / 200 * 100
        size_score = max(0, min(100, size_score))
        
        # Weighted average
        quality = (brightness_score * 0.3 + sharpness_score * 0.5 + size_score * 0.2)
        
        return quality
    
    def capture_angle(self, frame: np.ndarray, angle: str) -> Tuple[bool, Optional[np.ndarray], str]:
        """
        ENHANCED: Capture face at specific angle with pose validation
        
        Args:
            frame: Camera frame
            angle: Angle to capture ('front', 'left', 'right')
        
        Returns:
            Tuple of (success, face_encoding, message)
        """
        self.current_angle = angle
        
        # Detect and validate face (includes pose validation)
        face_detected, face_info, message = self.detect_face_in_frame(frame)
        
        if not face_detected:
            return False, None, message
        
        # Generate face encoding
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        face_encodings = face_recognition.face_encodings(rgb_frame, [face_info['location']])
        
        if not face_encodings:
            self.pose_stable_count = 0
            return False, None, "Failed to generate face encoding. Please try again."
        
        face_encoding = face_encodings[0]
        
        # CRITICAL: Store capture WITH pose angle
        self.captured_encodings[angle] = face_encoding
        self.captured_images[angle] = frame.copy()
        self.capture_quality[angle] = face_info['quality_score']
        self.captured_pose_angles[angle] = face_info['yaw_angle']  # Store actual angle
        
        # Reset pose counter for next capture
        self.pose_stable_count = 0
        
        print(f"--- [LIVE SCANNER] ✓ Captured {angle} angle ---")
        print(f"    Yaw: {face_info['yaw_angle']:.1f}°, Quality: {face_info['quality_score']:.1f}")
        
        return True, face_encoding, f"✓ {self.ANGLES[angle]['name']} captured at {face_info['yaw_angle']:.1f}° - Excellent!"
    
    def generate_composite_encoding(self) -> Optional[np.ndarray]:
        """
        Generate composite encoding from all captured angles
        
        Returns:
            Composite face encoding (average of all angles)
        """
        if len(self.captured_encodings) < 3:
            print(f"--- [LIVE SCANNER] Not enough captures: {len(self.captured_encodings)}/3 ---")
            return None
        
        # Average all encodings
        encodings = [self.captured_encodings[angle] for angle in ['front', 'left', 'right']]
        composite = np.mean(encodings, axis=0)
        
        # Normalize
        composite = composite / np.linalg.norm(composite)
        
        print("--- [LIVE SCANNER] Generated composite encoding ---")
        
        return composite
    
    def get_capture_summary(self) -> Dict:
        """
        Get summary of captured data
        
        Returns:
            Dictionary with capture summary
        """
        return {
            'angles_captured': list(self.captured_encodings.keys()),
            'total_captures': len(self.captured_encodings),
            'quality_scores': self.capture_quality,
            'average_quality': np.mean(list(self.capture_quality.values())) if self.capture_quality else 0,
            'timestamp': datetime.now().isoformat()
        }
    
    def _calculate_yaw_angle(self, landmarks: Dict, face_location: Tuple) -> float:
        """
        Calculate accurate yaw (head rotation) angle
        
        Returns:
            Yaw angle in degrees (negative = left, positive = right)
        """
        try:
            # Get key landmarks
            nose_tip = np.array(landmarks['nose_tip'][2])
            left_eye = np.mean(landmarks['left_eye'], axis=0)
            right_eye = np.mean(landmarks['right_eye'], axis=0)
            chin = np.mean(landmarks['chin'], axis=0)
            
            # Calculate eye center
            eye_center = (left_eye + right_eye) / 2
            
            # Calculate nose offset from eye center
            nose_offset_x = nose_tip[0] - eye_center[0]
            
            # Calculate face width
            top, right, bottom, left = face_location
            face_width = right - left
            
            # Estimate yaw angle
            # Positive = turned right, Negative = turned left
            yaw_angle = (nose_offset_x / (face_width / 2)) * 45
            
            return float(yaw_angle)
        
        except Exception as e:
            print(f"Error calculating yaw angle: {e}")
            return 0.0
    
    def _validate_pose_for_stage(self, yaw_angle: float) -> Tuple[bool, str]:
        """
        Validate that detected pose matches the required stage
        
        Returns:
            Tuple of (is_valid, message)
        """
        angle_config = self.ANGLES[self.current_angle]
        min_angle = angle_config['min_angle']
        max_angle = angle_config['max_angle']
        
        if min_angle <= yaw_angle <= max_angle:
            return True, f"✓ Correct pose: {yaw_angle:.1f}°"
        
        # Provide specific feedback
        if self.current_angle == 'front':
            if yaw_angle < -15:
                return False, f"❌ Turn RIGHT - Currently at {yaw_angle:.1f}° (need -15° to +15°)"
            elif yaw_angle > 15:
                return False, f"❌ Turn LEFT - Currently at {yaw_angle:.1f}° (need -15° to +15°)"
        
        elif self.current_angle == 'left':
            if yaw_angle > -25:
                return False, f"❌ Turn MORE to the LEFT - Currently at {yaw_angle:.1f}° (need -90° to -25°)"
            else:
                return False, f"❌ Turn LESS to the left - Currently at {yaw_angle:.1f}° (need -90° to -25°)"
        
        elif self.current_angle == 'right':
            if yaw_angle < 25:
                return False, f"❌ Turn MORE to the RIGHT - Currently at {yaw_angle:.1f}° (need +25° to +90°)"
            else:
                return False, f"❌ Turn LESS to the right - Currently at {yaw_angle:.1f}° (need +25° to +90°)"
        
        return False, f"❌ Incorrect pose: {yaw_angle:.1f}°"
    
    def _check_duplicate_pose(self, yaw_angle: float) -> Tuple[bool, str]:
        """
        CRITICAL: Check if this pose is too similar to already captured poses
        
        Prevents saving duplicate CENTER encodings for LEFT/RIGHT scans
        
        Returns:
            Tuple of (is_duplicate, message)
        """
        # Check against all previously captured angles
        for captured_angle, captured_yaw in self.captured_pose_angles.items():
            angle_difference = abs(yaw_angle - captured_yaw)
            
            if angle_difference < self.POSE_VALIDATION_THRESHOLD:
                return True, (
                    f"❌ DUPLICATE POSE DETECTED!\n"
                    f"Current: {yaw_angle:.1f}° is too similar to {captured_angle}: {captured_yaw:.1f}°\n"
                    f"Please turn your head to a DIFFERENT angle (need >{self.POSE_VALIDATION_THRESHOLD}° difference)"
                )
        
        return False, "✓ Unique pose confirmed"
    
    def reset(self):
        """Reset scanner for new capture session"""
        self.captured_encodings = {}
        self.captured_images = {}
        self.capture_quality = {}
        self.captured_pose_angles = {}
        self.pose_stable_count = 0
        self.last_detected_angle = 0
        self.current_angle = 'front'
        print("--- [LIVE SCANNER] Reset with pose validation ---")
    
    @staticmethod
    def compare_faces(known_encodings: List[np.ndarray], 
                     face_encoding: np.ndarray, 
                     tolerance: float = 0.6) -> Tuple[List[bool], List[float]]:
        """
        Compare face encoding against known encodings
        
        Args:
            known_encodings: List of known face encodings
            face_encoding: Face encoding to compare
            tolerance: Distance threshold for match
        
        Returns:
            Tuple of (matches list, distances list)
        """
        if len(known_encodings) == 0:
            return [], []
        
        # Calculate face distances
        face_distances = face_recognition.face_distance(known_encodings, face_encoding)
        
        # Determine matches
        matches = face_distances <= tolerance
        
        return matches.tolist(), face_distances.tolist()
    
    @staticmethod
    def match_with_confidence(user_encodings: List[np.ndarray], 
                            photo_encoding: np.ndarray) -> Tuple[bool, float]:
        """
        Match user encodings with photo encoding and return confidence
        
        Args:
            user_encodings: List of user's face encodings (3 angles)
            photo_encoding: Face encoding from photo
        
        Returns:
            Tuple of (is_match, confidence_score)
        """
        if not user_encodings:
            return False, 0.0
        
        # Compare with all user encodings
        distances = face_recognition.face_distance(user_encodings, photo_encoding)
        
        # Get best match
        min_distance = np.min(distances)
        
        # Convert distance to confidence (0-100)
        # Distance of 0 = 100% confidence, distance of 0.6 = 0% confidence
        confidence = max(0, (1 - min_distance / 0.6) * 100)
        
        # Match if any encoding is below threshold
        is_match = min_distance < LiveFaceScanner.FACE_DISTANCE_THRESHOLD
        
        return is_match, confidence
    
    @staticmethod
    def encode_to_base64(encoding: np.ndarray) -> str:
        """
        Encode face encoding to base64 string for storage
        
        Args:
            encoding: Face encoding array
        
        Returns:
            Base64 encoded string
        """
        return base64.b64encode(encoding.tobytes()).decode('utf-8')
    
    @staticmethod
    def decode_from_base64(encoded_str: str) -> np.ndarray:
        """
        Decode face encoding from base64 string
        
        Args:
            encoded_str: Base64 encoded string
        
        Returns:
            Face encoding array
        """
        bytes_data = base64.b64decode(encoded_str.encode('utf-8'))
        return np.frombuffer(bytes_data, dtype=np.float64)


def draw_face_overlay(frame: np.ndarray, 
                     face_location: Optional[Tuple] = None,
                     angle: str = 'front',
                     message: str = '') -> np.ndarray:
    """
    Draw face detection overlay on frame
    
    Args:
        frame: Camera frame
        face_location: Face bounding box (top, right, bottom, left)
        angle: Current angle being captured
        message: Feedback message to display
    
    Returns:
        Frame with overlay
    """
    overlay = frame.copy()
    h, w = frame.shape[:2]
    
    # Draw face guide (oval)
    center_x, center_y = w // 2, h // 2
    guide_width, guide_height = 200, 260
    
    # Adjust guide position based on angle
    if angle == 'right':
        center_x += 50
    elif angle == 'left':
        center_x -= 50
    
    # Draw guide oval
    cv2.ellipse(overlay, (center_x, center_y), (guide_width, guide_height), 
                0, 0, 360, (255, 255, 255), 3)
    
    # Draw face box if detected
    if face_location:
        top, right, bottom, left = face_location
        cv2.rectangle(overlay, (left, top), (right, bottom), (0, 255, 0), 3)
    
    # Draw instruction text
    angle_name = LiveFaceScanner.ANGLES[angle]['name']
    instruction = LiveFaceScanner.ANGLES[angle]['instruction']
    
    # Background for text
    cv2.rectangle(overlay, (10, 10), (w - 10, 120), (0, 0, 0), -1)
    cv2.rectangle(overlay, (10, 10), (w - 10, 120), (255, 255, 255), 2)
    
    # Text
    cv2.putText(overlay, f"Step: {angle_name}", (20, 40), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
    cv2.putText(overlay, instruction, (20, 70), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 1)
    cv2.putText(overlay, message, (20, 100), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
    
    return overlay


if __name__ == '__main__':
    # Test the scanner
    print("Testing Live Face Scanner...")
    scanner = LiveFaceScanner()
    print(f"Angles to capture: {list(scanner.ANGLES.keys())}")
    print("Scanner ready!")
