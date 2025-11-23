"""
Robust Face Detection System for PicMe
Handles challenging scenarios: sunglasses, varying lighting, different angles

Features:
- Multiple detection algorithms with automatic fallback
- Image preprocessing pipeline
- Support for partially obscured faces
- Pose-invariant detection
"""

import cv2
import numpy as np
from typing import List, Tuple, Optional, Dict
import os

class RobustFaceDetector:
    """
    Multi-algorithm face detector with preprocessing and fallback mechanisms
    """
    
    def __init__(self):
        """Initialize all face detection models"""
        self.models_loaded = {}
        self.detection_stats = {
            'mtcnn': 0,
            'dnn': 0,
            'haar': 0,
            'hog': 0,
            'preprocessing_used': 0
        }
        
        # Load models
        self._load_models()
    
    def _load_models(self):
        """Load all available face detection models"""
        print("--- [ROBUST DETECTOR] Loading face detection models... ---")
        
        # 1. Try to load MTCNN (best for sunglasses/occlusions)
        try:
            from mtcnn import MTCNN
            # Configure MTCNN with optimized settings
            # min_face_size: Minimum face size to detect (20px works well)
            # steps_threshold: [P-Net, R-Net, O-Net] - lowered for better detection
            # scale_factor: Pyramid scale factor (0.709 is default)
            self.mtcnn_detector = MTCNN(
                min_face_size=20,
                steps_threshold=[0.6, 0.7, 0.7],
                scale_factor=0.709
            )
            self.models_loaded['mtcnn'] = True
            print("--- [ROBUST DETECTOR] ✓ MTCNN loaded (primary) ---")
            print("--- [ROBUST DETECTOR]   Config: min_face_size=20px, steps_threshold=[0.6, 0.7, 0.7] ---")
        except ImportError:
            self.models_loaded['mtcnn'] = False
            print("--- [ROBUST DETECTOR] ✗ MTCNN not available (install: pip install mtcnn tensorflow) ---")
        
        # 2. Load DNN-based detector (good for various lighting)
        try:
            model_path = os.path.join(os.path.dirname(__file__), 'models')
            os.makedirs(model_path, exist_ok=True)
            
            prototxt_path = os.path.join(model_path, 'deploy.prototxt')
            caffemodel_path = os.path.join(model_path, 'res10_300x300_ssd_iter_140000.caffemodel')
            
            if os.path.exists(prototxt_path) and os.path.exists(caffemodel_path):
                self.dnn_detector = cv2.dnn.readNetFromCaffe(prototxt_path, caffemodel_path)
                self.models_loaded['dnn'] = True
                print("--- [ROBUST DETECTOR] ✓ DNN detector loaded (secondary) ---")
            else:
                self.models_loaded['dnn'] = False
                print("--- [ROBUST DETECTOR] ✗ DNN model files not found ---")
                print("--- [ROBUST DETECTOR]   Download from: https://github.com/opencv/opencv/tree/master/samples/dnn/face_detector ---")
        except Exception as e:
            self.models_loaded['dnn'] = False
            print(f"--- [ROBUST DETECTOR] ✗ DNN detector failed: {e} ---")
        
        # 3. Load Haar Cascade (lightweight fallback)
        try:
            haar_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
            self.haar_detector = cv2.CascadeClassifier(haar_path)
            
            # Also load profile face detector
            haar_profile_path = cv2.data.haarcascades + 'haarcascade_profileface.xml'
            self.haar_profile_detector = cv2.CascadeClassifier(haar_profile_path)
            
            self.models_loaded['haar'] = True
            print("--- [ROBUST DETECTOR] ✓ Haar Cascade loaded (fallback) ---")
        except Exception as e:
            self.models_loaded['haar'] = False
            print(f"--- [ROBUST DETECTOR] ✗ Haar Cascade failed: {e} ---")
        
        # 4. HOG detector (using dlib if available)
        try:
            import dlib
            self.hog_detector = dlib.get_frontal_face_detector()
            self.models_loaded['hog'] = True
            print("--- [ROBUST DETECTOR] ✓ HOG detector loaded (dlib) ---")
        except ImportError:
            self.models_loaded['hog'] = False
            print("--- [ROBUST DETECTOR] ✗ HOG detector not available (install: pip install dlib) ---")
        
        print(f"--- [ROBUST DETECTOR] Loaded {sum(self.models_loaded.values())}/4 detectors ---")
    
    def preprocess_image(self, image: np.ndarray, enhancement_level: str = 'medium') -> List[np.ndarray]:
        """
        Preprocess image with multiple enhancement techniques
        
        Args:
            image: Input image (BGR format)
            enhancement_level: 'light', 'medium', 'heavy'
        
        Returns:
            List of preprocessed image variants
        """
        variants = [image.copy()]  # Original
        
        # Convert to grayscale for some operations
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # 1. Histogram Equalization (better contrast)
        if enhancement_level in ['medium', 'heavy']:
            equalized = cv2.equalizeHist(gray)
            equalized_bgr = cv2.cvtColor(equalized, cv2.COLOR_GRAY2BGR)
            variants.append(equalized_bgr)
        
        # 2. CLAHE (Contrast Limited Adaptive Histogram Equalization)
        if enhancement_level in ['medium', 'heavy']:
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
            clahe_applied = clahe.apply(gray)
            clahe_bgr = cv2.cvtColor(clahe_applied, cv2.COLOR_GRAY2BGR)
            variants.append(clahe_bgr)
        
        # 3. Brightness/Contrast Normalization
        if enhancement_level in ['heavy']:
            alpha = 1.2  # Contrast control
            beta = 10    # Brightness control
            adjusted = cv2.convertScaleAbs(image, alpha=alpha, beta=beta)
            variants.append(adjusted)
        
        # 4. Noise Reduction
        if enhancement_level in ['medium', 'heavy']:
            denoised = cv2.fastNlMeansDenoisingColored(image, None, 10, 10, 7, 21)
            variants.append(denoised)
        
        # 5. Sharpening (for blurry images)
        if enhancement_level in ['heavy']:
            kernel = np.array([[-1,-1,-1],
                             [-1, 9,-1],
                             [-1,-1,-1]])
            sharpened = cv2.filter2D(image, -1, kernel)
            variants.append(sharpened)
        
        # 6. Gamma Correction (for dark images)
        if enhancement_level in ['heavy']:
            gamma = 1.5
            inv_gamma = 1.0 / gamma
            table = np.array([((i / 255.0) ** inv_gamma) * 255
                            for i in np.arange(0, 256)]).astype("uint8")
            gamma_corrected = cv2.LUT(image, table)
            variants.append(gamma_corrected)
        
        return variants
    
    def detect_faces_mtcnn(self, image: np.ndarray) -> List[Dict]:
        """
        Detect faces using MTCNN (best for sunglasses/occlusions)
        
        Returns:
            List of face dictionaries with 'box' and 'confidence'
        """
        if not self.models_loaded.get('mtcnn'):
            return []
        
        try:
            # MTCNN expects RGB
            rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            detections = self.mtcnn_detector.detect_faces(rgb_image)
            
            faces = []
            for detection in detections:
                # Lowered threshold from 0.90 to 0.85 for better detection
                if detection['confidence'] > 0.85:  # Confidence threshold
                    box = detection['box']
                    x1, y1, w, h = box[0], box[1], box[2], box[3]
                    
                    # Ensure coordinates are valid
                    if w <= 0 or h <= 0:
                        continue
                    
                    faces.append({
                        'box': (x1, y1, x1 + w, y1 + h),
                        'confidence': detection['confidence'],
                        'method': 'mtcnn'
                    })
            
            if faces:
                self.detection_stats['mtcnn'] += 1
            
            return faces
        except Exception as e:
            print(f"--- [ROBUST DETECTOR] MTCNN error: {e} ---")
            return []
    
    def detect_faces_dnn(self, image: np.ndarray) -> List[Dict]:
        """
        Detect faces using DNN (good for various lighting)
        
        Returns:
            List of face dictionaries with 'box' and 'confidence'
        """
        if not self.models_loaded.get('dnn'):
            return []
        
        try:
            h, w = image.shape[:2]
            
            # Prepare blob
            blob = cv2.dnn.blobFromImage(
                cv2.resize(image, (300, 300)), 
                1.0, 
                (300, 300), 
                (104.0, 177.0, 123.0)
            )
            
            self.dnn_detector.setInput(blob)
            detections = self.dnn_detector.forward()
            
            faces = []
            for i in range(detections.shape[2]):
                confidence = detections[0, 0, i, 2]
                
                # Lowered threshold from 0.5 to 0.3 for better detection
                if confidence > 0.3:  # Confidence threshold
                    box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
                    (x1, y1, x2, y2) = box.astype("int")
                    
                    # Ensure coordinates are within image bounds
                    x1, y1 = max(0, x1), max(0, y1)
                    x2, y2 = min(w, x2), min(h, y2)
                    
                    # Skip invalid boxes
                    if x2 <= x1 or y2 <= y1:
                        continue
                    
                    faces.append({
                        'box': (x1, y1, x2, y2),
                        'confidence': float(confidence),
                        'method': 'dnn'
                    })
            
            if faces:
                self.detection_stats['dnn'] += 1
            
            return faces
        except Exception as e:
            print(f"--- [ROBUST DETECTOR] DNN error: {e} ---")
            return []
    
    def detect_faces_haar(self, image: np.ndarray) -> List[Dict]:
        """
        Detect faces using Haar Cascade (lightweight fallback)
        
        Returns:
            List of face dictionaries with 'box' and 'confidence'
        """
        if not self.models_loaded.get('haar'):
            return []
        
        try:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Detect frontal faces
            frontal_faces = self.haar_detector.detectMultiScale(
                gray,
                scaleFactor=1.1,
                minNeighbors=5,
                minSize=(30, 30),
                flags=cv2.CASCADE_SCALE_IMAGE
            )
            
            # Detect profile faces
            profile_faces = self.haar_profile_detector.detectMultiScale(
                gray,
                scaleFactor=1.1,
                minNeighbors=5,
                minSize=(30, 30),
                flags=cv2.CASCADE_SCALE_IMAGE
            )
            
            faces = []
            
            # Add frontal faces
            for (x, y, w, h) in frontal_faces:
                faces.append({
                    'box': (x, y, x + w, y + h),
                    'confidence': 0.8,  # Haar doesn't provide confidence
                    'method': 'haar_frontal'
                })
            
            # Add profile faces
            for (x, y, w, h) in profile_faces:
                faces.append({
                    'box': (x, y, x + w, y + h),
                    'confidence': 0.7,  # Lower confidence for profile
                    'method': 'haar_profile'
                })
            
            if faces:
                self.detection_stats['haar'] += 1
            
            return faces
        except Exception as e:
            print(f"--- [ROBUST DETECTOR] Haar error: {e} ---")
            return []
    
    def detect_faces_hog(self, image: np.ndarray) -> List[Dict]:
        """
        Detect faces using HOG (pose-invariant, good for sunglasses)
        
        Returns:
            List of face dictionaries with 'box' and 'confidence'
        """
        if not self.models_loaded.get('hog'):
            return []
        
        try:
            import dlib
            
            # Convert to RGB for dlib
            rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            # Detect faces with upsampling for better detection
            # upsample=1 means we'll upsample the image once before detecting
            dets = self.hog_detector(rgb_image, 1)
            
            faces = []
            for det in dets:
                faces.append({
                    'box': (det.left(), det.top(), det.right(), det.bottom()),
                    'confidence': 0.90,  # HOG is very reliable for accessories
                    'method': 'hog'
                })
            
            if faces:
                self.detection_stats['hog'] += 1
                print(f"--- [ROBUST DETECTOR] HOG detected {len(faces)} face(s) ---")
            
            return faces
        except Exception as e:
            print(f"--- [ROBUST DETECTOR] HOG error: {e} ---")
            return []
    
    def detect_faces_robust(
        self, 
        image: np.ndarray, 
        use_preprocessing: bool = True,
        enhancement_level: str = 'medium'  # Changed to 'medium' for speed
    ) -> Tuple[List[Dict], str]:
        """
        OPTIMIZED: Robust face detection with multiple algorithms
        Enhanced for sunglasses, accessories, and challenging conditions
        
        CRITICAL FIX: Reduced preprocessing variants for speed
        
        Args:
            image: Input image (BGR format)
            use_preprocessing: Whether to use image preprocessing
            enhancement_level: 'light', 'medium', 'heavy'
        
        Returns:
            Tuple of (list of detected faces, detection method used)
        """
        # Try each detection method in order of speed and reliability
        # CRITICAL: Try on original image first, then preprocess only if needed
        detection_methods = [
            ('haar', self.detect_faces_haar),    # Fastest, try first
            ('hog', self.detect_faces_hog),      # Good for sunglasses
            ('dnn', self.detect_faces_dnn),      # Good for lighting
            ('mtcnn', self.detect_faces_mtcnn),  # Slowest, try last
        ]
        
        # PHASE 1: Try all methods on original image (fast)
        for method_name, detect_func in detection_methods:
            if not self.models_loaded.get(method_name):
                continue
            
            faces = detect_func(image)
            
            if faces:
                print(f"--- [ROBUST DETECTOR] ✓ {method_name.upper()} found {len(faces)} face(s) ---")
                return faces, method_name
        
        # PHASE 2: If no faces found, try with preprocessing (slower)
        if use_preprocessing:
            print("--- [ROBUST DETECTOR] No faces found, trying with preprocessing... ---")
            self.detection_stats['preprocessing_used'] += 1
            
            # Create only 2-3 most effective variants (not 7!)
            image_variants = [
                image,  # Original
                self._quick_enhance(image)  # Single enhanced version
            ]
            
            for method_name, detect_func in detection_methods:
                if not self.models_loaded.get(method_name):
                    continue
                
                for variant_idx, img_variant in enumerate(image_variants[1:], 1):  # Skip original (already tried)
                    faces = detect_func(img_variant)
                    
                    if faces:
                        print(f"--- [ROBUST DETECTOR] ✓ {method_name.upper()} found {len(faces)} face(s) with preprocessing ---")
                        return faces, f"{method_name}_enhanced"
        
        print("--- [ROBUST DETECTOR] ✗ No faces detected by any method ---")
        return [], 'none'
    
    def _quick_enhance(self, image: np.ndarray) -> np.ndarray:
        """
        Quick single-pass enhancement for speed
        
        Returns:
            Enhanced image
        """
        try:
            # CLAHE for better contrast (most effective single enhancement)
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
            enhanced_gray = clahe.apply(gray)
            enhanced = cv2.cvtColor(enhanced_gray, cv2.COLOR_GRAY2BGR)
            return enhanced
        except:
            return image
    
    def get_face_encodings_from_detections(
        self, 
        image: np.ndarray, 
        face_detections: List[Dict]
    ) -> List[np.ndarray]:
        """
        Extract face encodings from detected face regions
        
        Args:
            image: Original image
            face_detections: List of face detection dictionaries
        
        Returns:
            List of face encodings
        """
        try:
            import face_recognition
            
            encodings = []
            
            for detection in face_detections:
                x1, y1, x2, y2 = detection['box']
                
                # Ensure coordinates are within image bounds
                h, w = image.shape[:2]
                x1, y1 = max(0, x1), max(0, y1)
                x2, y2 = min(w, x2), min(h, y2)
                
                # Convert box format for face_recognition
                # face_recognition uses (top, right, bottom, left)
                face_location = (y1, x2, y2, x1)
                
                # Get encoding
                rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                encoding = face_recognition.face_encodings(rgb_image, [face_location])
                
                if encoding:
                    encodings.append(encoding[0])
            
            return encodings
        except Exception as e:
            print(f"--- [ROBUST DETECTOR] Error getting encodings: {e} ---")
            return []
    
    def print_stats(self):
        """Print detection statistics"""
        print("\n--- [ROBUST DETECTOR] Detection Statistics ---")
        print(f"  MTCNN detections: {self.detection_stats['mtcnn']}")
        print(f"  DNN detections: {self.detection_stats['dnn']}")
        print(f"  Haar detections: {self.detection_stats['haar']}")
        print(f"  HOG detections: {self.detection_stats['hog']}")
        print(f"  Preprocessing used: {self.detection_stats['preprocessing_used']} times")
        print("--- [ROBUST DETECTOR] End Statistics ---\n")


# Convenience function for easy integration
def detect_faces_robust(image_path: str, use_preprocessing: bool = True) -> Tuple[List, str]:
    """
    Convenience function to detect faces in an image file
    
    Args:
        image_path: Path to image file
        use_preprocessing: Whether to use preprocessing
    
    Returns:
        Tuple of (list of face detections, method used)
    """
    detector = RobustFaceDetector()
    image = cv2.imread(image_path)
    
    if image is None:
        print(f"--- [ROBUST DETECTOR] Error: Could not load image {image_path} ---")
        return [], 'error'
    
    faces, method = detector.detect_faces_robust(image, use_preprocessing)
    return faces, method


if __name__ == '__main__':
    # Test the detector
    print("Testing Robust Face Detector...")
    detector = RobustFaceDetector()
    detector.print_stats()
