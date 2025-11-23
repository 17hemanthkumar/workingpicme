"""
Test all face detection methods individually to verify they work
"""

import cv2
import os
from robust_face_detector import RobustFaceDetector

# Initialize detector
detector = RobustFaceDetector()

# Test image
test_image_path = "../uploads/event_931cd6b8/2516695c_WhatsApp_Image_2025-11-20_at_5.05.29_PM.jpeg"

if not os.path.exists(test_image_path):
    print(f"Error: Test image not found at {test_image_path}")
    exit(1)

# Load image
image = cv2.imread(test_image_path)
print(f"Loaded image: {image.shape}")
print("=" * 70)

# Test each detector individually
print("\nTesting each detector individually on the same image:")
print("=" * 70)

# 1. MTCNN
print("\n1. MTCNN Detector:")
print("-" * 70)
if detector.models_loaded.get('mtcnn'):
    faces = detector.detect_faces_mtcnn(image)
    print(f"   Detected: {len(faces)} face(s)")
    if len(faces) > 0:
        for i, face in enumerate(faces[:3]):  # Show first 3
            print(f"   Face {i+1}: box={face['box']}, confidence={face['confidence']:.3f}")
else:
    print("   ✗ MTCNN not loaded")

# 2. DNN
print("\n2. DNN Detector:")
print("-" * 70)
if detector.models_loaded.get('dnn'):
    faces = detector.detect_faces_dnn(image)
    print(f"   Detected: {len(faces)} face(s)")
    if len(faces) > 0:
        for i, face in enumerate(faces[:3]):  # Show first 3
            print(f"   Face {i+1}: box={face['box']}, confidence={face['confidence']:.3f}")
else:
    print("   ✗ DNN not loaded")

# 3. Haar Cascade
print("\n3. Haar Cascade Detector:")
print("-" * 70)
if detector.models_loaded.get('haar'):
    faces = detector.detect_faces_haar(image)
    print(f"   Detected: {len(faces)} face(s)")
    if len(faces) > 0:
        for i, face in enumerate(faces[:3]):  # Show first 3
            print(f"   Face {i+1}: box={face['box']}, confidence={face['confidence']:.3f}, method={face['method']}")
else:
    print("   ✗ Haar not loaded")

# 4. HOG
print("\n4. HOG Detector:")
print("-" * 70)
if detector.models_loaded.get('hog'):
    faces = detector.detect_faces_hog(image)
    print(f"   Detected: {len(faces)} face(s)")
    if len(faces) > 0:
        for i, face in enumerate(faces[:3]):  # Show first 3
            print(f"   Face {i+1}: box={face['box']}, confidence={face['confidence']:.3f}")
else:
    print("   ✗ HOG not loaded")

print("\n" + "=" * 70)
print("SUMMARY:")
print("=" * 70)
print(f"MTCNN:  {'✓ Working' if detector.models_loaded.get('mtcnn') else '✗ Not loaded'}")
print(f"DNN:    {'✓ Working' if detector.models_loaded.get('dnn') else '✗ Not loaded'}")
print(f"Haar:   {'✓ Working' if detector.models_loaded.get('haar') else '✗ Not loaded'}")
print(f"HOG:    {'✓ Working' if detector.models_loaded.get('hog') else '✗ Not loaded'}")
print("=" * 70)
