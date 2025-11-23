#!/usr/bin/env python3
"""
Enhanced Face Detector for Multi-Angle Face Detection System

Integrates multiple detection algorithms with angle estimation and quality assessment.
Builds on the existing RobustFaceDetector with additional features for the enhanced system.

Features:
- Multi-algorithm detection (MTCNN, Haar, HOG, DNN)
- Face angle estimation from landmarks
- Quality scoring (blur, lighting, size)
- Bounding box extraction and normalization
"""

import cv2
import numpy as np
from typing import List, Dict, Tuple, Optional
import dlib
from mtcnn import MTCNN

class EnhancedFaceDetector:
    """
    Enhanced face detector with multi-algorithm support, angle estimation, and quality assessment
    """
    
    def __init__(self):
        """Initialize all detection algorithms and models"""
        print("=" * 70)
        print("INITIALIZING ENHANCED FACE DETECTOR")
        print("=" * 70)
        
        self.detectors_loaded = {}
        self.detection_stats = {
            'mtcnn': 0,
            'haar': 0,
            'hog': 0,
            'dnn': 0,
            'total': 0
        }
        
        # Load all detection models
        self._load_detectors()
        
        print("✓ Enhanced Face Detector initialized successfully")
        print("=" * 70)
        print()
    
    def _load_detectors(self):
        """Load all available face detection models"""
        print("\nLoading detection models...")
        
        # 1. Load MTCNN (best for frontal faces, handles occlusions)
        try:
            self.mtcnn = MTCNN(
                min_face_size=20,
                steps_threshold=[0.6, 0.7, 0.7],
                scale_factor=0.709
            )
            self.detectors_loaded['mtcnn'] = True
            print("  ✓ MTCNN loaded")
        except Exception as e:
            print(f"  ✗ MTCNN failed to load: {e}")
            self.detectors_loaded['mtcnn'] = False
        
        # 2. Load Haar Cascade (fast, works in various conditions)
        try:
            haar_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
            self.haar_cascade = cv2.CascadeClassifier(haar_path)
            if self.haar_cascade.empty():
                raise Exception("Failed to load Haar cascade")
            self.detectors_loaded['haar'] = True
            print("  ✓ Haar Cascade loaded")
        except Exception as e:
            print(f"  ✗ Haar Cascade failed to load: {e}")
            self.detectors_loaded['haar'] = False
        
        # 3. Load HOG (good for profile faces)
        try:
            self.hog_detector = dlib.get_frontal_face_detector()
            self.detectors_loaded['hog'] = True
            print("  ✓ HOG (dlib) loaded")
        except Exception as e:
            print(f"  ✗ HOG failed to load: {e}")
            self.detectors_loaded['hog'] = False
        
        # 4. Load DNN (deep learning based, very accurate)
        try:
            model_file = "models/res10_300x300_ssd_iter_140000.caffemodel"
            config_file = "models/deploy.prototxt"
            if cv2.os.path.exists(model_file) and cv2.os.path.exists(config_file):
                self.dnn_net = cv2.dnn.readNetFromCaffe(config_file, model_file)
                self.detectors_loaded['dnn'] = True
                print("  ✓ DNN (Caffe) loaded")
            else:
                self.detectors_loaded['dnn'] = False
                print("  ✗ DNN model files not found")
        except Exception as e:
            print(f"  ✗ DNN failed to load: {e}")
            self.detectors_loaded['dnn'] = False
        
        # Check if at least one detector loaded
        if not any(self.detectors_loaded.values()):
            raise Exception("No face detectors could be loaded!")
        
        print(f"\n  Loaded {sum(self.detectors_loaded.values())}/{len(self.detectors_loaded)} detectors")
    
    def detect_faces(self, image: np.ndarray) -> List[Dict]:
        """
        Detect all faces in an image using multiple algorithms
        
        Args:
            image: Input image as numpy array (BGR format)
            
        Returns:
            List of face detections, each containing:
            - bbox: (x, y, width, height)
            - confidence: detection confidence score
            - method: detection method used
            - landmarks: facial landmarks if available
        """
        self.detection_stats['total'] += 1
        detections = []
        
        # Try MTCNN first (best overall performance)
        if self.detectors_loaded.get('mtcnn', False):
            detections = self._detect_mtcnn(image)
            if detections:
                self.detection_stats['mtcnn'] += 1
                return detections
        
        # Fall back to DNN
        if self.detectors_loaded.get('dnn', False):
            detections = self._detect_dnn(image)
            if detections:
                self.detection_stats['dnn'] += 1
                return detections
        
        # Fall back to Haar Cascade
        if self.detectors_loaded.get('haar', False):
            detections = self._detect_haar(image)
            if detections:
                self.detection_stats['haar'] += 1
                return detections
        
        # Fall back to HOG
        if self.detectors_loaded.get('hog', False):
            detections = self._detect_hog(image)
            if detections:
                self.detection_stats['hog'] += 1
                return detections
        
        return []
    
    def _detect_mtcnn(self, image: np.ndarray) -> List[Dict]:
        """Detect faces using MTCNN"""
        try:
            # MTCNN expects RGB
            rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            results = self.mtcnn.detect_faces(rgb_image)
            
            detections = []
            for result in results:
                bbox = result['box']
                # Ensure positive dimensions
                x, y, w, h = bbox
                if w > 0 and h > 0:
                    detections.append({
                        'bbox': (max(0, x), max(0, y), w, h),
                        'confidence': result['confidence'],
                        'method': 'mtcnn',
                        'landmarks': result.get('keypoints', None)
                    })
            
            return detections
        except Exception as e:
            print(f"MTCNN detection error: {e}")
            return []
    
    def _detect_dnn(self, image: np.ndarray) -> List[Dict]:
        """Detect faces using DNN"""
        try:
            h, w = image.shape[:2]
            blob = cv2.dnn.blobFromImage(
                cv2.resize(image, (300, 300)), 1.0,
                (300, 300), (104.0, 177.0, 123.0)
            )
            
            self.dnn_net.setInput(blob)
            detections_dnn = self.dnn_net.forward()
            
            detections = []
            for i in range(detections_dnn.shape[2]):
                confidence = detections_dnn[0, 0, i, 2]
                
                if confidence > 0.5:
                    box = detections_dnn[0, 0, i, 3:7] * np.array([w, h, w, h])
                    (x1, y1, x2, y2) = box.astype("int")
                    
                    # Convert to (x, y, width, height)
                    bbox_w = x2 - x1
                    bbox_h = y2 - y1
                    
                    if bbox_w > 0 and bbox_h > 0:
                        detections.append({
                            'bbox': (x1, y1, bbox_w, bbox_h),
                            'confidence': float(confidence),
                            'method': 'dnn',
                            'landmarks': None
                        })
            
            return detections
        except Exception as e:
            print(f"DNN detection error: {e}")
            return []
    
    def _detect_haar(self, image: np.ndarray) -> List[Dict]:
        """Detect faces using Haar Cascade"""
        try:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            faces = self.haar_cascade.detectMultiScale(
                gray,
                scaleFactor=1.1,
                minNeighbors=5,
                minSize=(30, 30)
            )
            
            detections = []
            for (x, y, w, h) in faces:
                detections.append({
                    'bbox': (int(x), int(y), int(w), int(h)),
                    'confidence': 0.8,  # Haar doesn't provide confidence
                    'method': 'haar',
                    'landmarks': None
                })
            
            return detections
        except Exception as e:
            print(f"Haar detection error: {e}")
            return []
    
    def _detect_hog(self, image: np.ndarray) -> List[Dict]:
        """Detect faces using HOG (dlib)"""
        try:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            faces = self.hog_detector(gray, 1)
            
            detections = []
            for face in faces:
                x = face.left()
                y = face.top()
                w = face.right() - x
                h = face.bottom() - y
                
                detections.append({
                    'bbox': (int(x), int(y), int(w), int(h)),
                    'confidence': 0.85,  # HOG doesn't provide confidence
                    'method': 'hog',
                    'landmarks': None
                })
            
            return detections
        except Exception as e:
            print(f"HOG detection error: {e}")
            return []
    
    def estimate_angle(self, face_image: np.ndarray, landmarks: Optional[Dict] = None) -> str:
        """
        Estimate face angle from facial landmarks or image analysis
        
        Args:
            face_image: Cropped face image
            landmarks: Optional facial landmarks from MTCNN
            
        Returns:
            Angle classification: 'frontal', 'left_45', 'right_45', 'left_90', 'right_90'
        """
        if landmarks and 'left_eye' in landmarks and 'right_eye' in landmarks:
            # Use landmarks for angle estimation
            left_eye = np.array(landmarks['left_eye'])
            right_eye = np.array(landmarks['right_eye'])
            
            # Get nose landmark safely
            if 'nose' in landmarks:
                nose = np.array(landmarks['nose'])
            else:
                nose = np.array([face_image.shape[1]//2, face_image.shape[0]//2])
            
            # Calculate eye center line angle
            eye_center = (left_eye + right_eye) / 2
            eye_vector = right_eye - left_eye
            angle_rad = np.arctan2(eye_vector[1], eye_vector[0])
            angle_deg = np.degrees(angle_rad)
            
            # Calculate nose position relative to eye center
            nose_offset = nose[0] - eye_center[0]
            face_width = np.linalg.norm(eye_vector)
            nose_ratio = nose_offset / face_width if face_width > 0 else 0
            
            # Classify angle based on eye line tilt and nose position
            if abs(angle_deg) < 15 and abs(nose_ratio) < 0.2:
                return 'frontal'
            elif nose_ratio > 0.3:
                return 'left_45' if angle_deg < 30 else 'left_90'
            elif nose_ratio < -0.3:
                return 'right_45' if angle_deg > -30 else 'right_90'
            else:
                return 'frontal'
        else:
            # Fallback: Use simple image-based estimation
            # This is a simplified approach - in production, you'd use a trained model
            gray = cv2.cvtColor(face_image, cv2.COLOR_BGR2GRAY) if len(face_image.shape) == 3 else face_image
            
            # Analyze left vs right half brightness (simple heuristic)
            h, w = gray.shape
            left_half = gray[:, :w//2]
            right_half = gray[:, w//2:]
            
            left_brightness = np.mean(left_half)
            right_brightness = np.mean(right_half)
            brightness_diff = abs(left_brightness - right_brightness)
            
            # If one side is significantly darker, it might be a profile
            if brightness_diff > 20:
                if left_brightness < right_brightness:
                    return 'left_45'
                else:
                    return 'right_45'
            
            return 'frontal'
    
    def calculate_quality_score(self, face_image: np.ndarray) -> Dict[str, float]:
        """
        Calculate face quality metrics
        
        Args:
            face_image: Cropped face image
            
        Returns:
            Dictionary with blur_score, lighting_score, size_score, overall_score
        """
        scores = {}
        
        # 1. Blur Score (using Laplacian variance)
        gray = cv2.cvtColor(face_image, cv2.COLOR_BGR2GRAY) if len(face_image.shape) == 3 else face_image
        laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
        # Normalize: higher variance = sharper image
        blur_score = min(1.0, laplacian_var / 500.0)  # 500 is a reasonable threshold
        scores['blur_score'] = float(blur_score)
        
        # 2. Lighting Score (histogram analysis)
        hist = cv2.calcHist([gray], [0], None, [256], [0, 256])
        hist = hist.flatten() / hist.sum()  # Normalize
        
        # Good lighting has a balanced histogram (not too dark or too bright)
        # Calculate entropy as a measure of distribution
        hist = hist[hist > 0]  # Remove zeros for log calculation
        entropy = -np.sum(hist * np.log2(hist))
        # Normalize entropy (max entropy for 256 bins is 8)
        lighting_score = min(1.0, entropy / 6.0)  # 6 is a good balanced value
        scores['lighting_score'] = float(lighting_score)
        
        # 3. Size Score (based on face dimensions)
        h, w = face_image.shape[:2]
        face_area = h * w
        # Prefer faces that are at least 80x80 pixels
        min_area = 80 * 80
        optimal_area = 200 * 200
        
        if face_area < min_area:
            size_score = face_area / min_area
        elif face_area < optimal_area:
            size_score = 0.5 + 0.5 * (face_area - min_area) / (optimal_area - min_area)
        else:
            size_score = 1.0
        
        scores['size_score'] = float(size_score)
        
        # 4. Overall Score (weighted average)
        overall_score = (
            0.4 * blur_score +      # Blur is most important
            0.3 * lighting_score +   # Lighting is important
            0.3 * size_score         # Size is important
        )
        scores['overall_score'] = float(overall_score)
        
        return scores
    
    def get_detection_stats(self) -> Dict:
        """Get detection statistics"""
        return self.detection_stats.copy()
    
    def reset_stats(self):
        """Reset detection statistics"""
        for key in self.detection_stats:
            self.detection_stats[key] = 0


def main():
    """Test the Enhanced Face Detector"""
    print("\n" + "=" * 70)
    print("TESTING ENHANCED FACE DETECTOR")
    print("=" * 70)
    
    # Initialize detector
    detector = EnhancedFaceDetector()
    
    # Test with a sample image (if available)
    test_image_path = "../uploads/test_face.jpg"
    
    if cv2.os.path.exists(test_image_path):
        print(f"\nTesting with image: {test_image_path}")
        image = cv2.imread(test_image_path)
        
        # Detect faces
        detections = detector.detect_faces(image)
        print(f"\nDetected {len(detections)} face(s)")
        
        # Process each detection
        for i, detection in enumerate(detections, 1):
            print(f"\nFace {i}:")
            print(f"  Method: {detection['method']}")
            print(f"  Confidence: {detection['confidence']:.2f}")
            print(f"  BBox: {detection['bbox']}")
            
            # Extract face region
            x, y, w, h = detection['bbox']
            face_img = image[y:y+h, x:x+w]
            
            # Estimate angle
            angle = detector.estimate_angle(face_img, detection.get('landmarks'))
            print(f"  Angle: {angle}")
            
            # Calculate quality
            quality = detector.calculate_quality_score(face_img)
            print(f"  Quality Scores:")
            print(f"    Blur: {quality['blur_score']:.2f}")
            print(f"    Lighting: {quality['lighting_score']:.2f}")
            print(f"    Size: {quality['size_score']:.2f}")
            print(f"    Overall: {quality['overall_score']:.2f}")
    else:
        print(f"\nTest image not found: {test_image_path}")
        print("Detector initialized successfully but no test image available")
    
    # Print statistics
    print("\n" + "=" * 70)
    print("DETECTION STATISTICS")
    print("=" * 70)
    stats = detector.get_detection_stats()
    for method, count in stats.items():
        print(f"  {method}: {count}")
    
    print("\n✓ Enhanced Face Detector test complete")
    print("=" * 70)


if __name__ == "__main__":
    main()
