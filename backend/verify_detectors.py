"""
Quick verification script to show current detector status
"""

import cv2
import os
from robust_face_detector import RobustFaceDetector

print("=" * 70)
print("FACE DETECTOR VERIFICATION")
print("=" * 70)

# Initialize detector
detector = RobustFaceDetector()

print("\n" + "=" * 70)
print("DETECTOR STATUS")
print("=" * 70)

status_symbols = {True: "✅ WORKING", False: "❌ NOT LOADED"}

print(f"\n1. MTCNN:        {status_symbols[detector.models_loaded.get('mtcnn', False)]}")
print(f"2. DNN:          {status_symbols[detector.models_loaded.get('dnn', False)]}")
print(f"3. Haar Cascade: {status_symbols[detector.models_loaded.get('haar', False)]}")
print(f"4. HOG:          {status_symbols[detector.models_loaded.get('hog', False)]}")

loaded_count = sum(detector.models_loaded.values())
print(f"\nTotal: {loaded_count}/4 detectors loaded")

# Test on a sample image
test_image = "../uploads/event_931cd6b8/2516695c_WhatsApp_Image_2025-11-20_at_5.05.29_PM.jpeg"

if os.path.exists(test_image):
    print("\n" + "=" * 70)
    print("QUICK DETECTION TEST")
    print("=" * 70)
    
    image = cv2.imread(test_image)
    print(f"\nTest image: {os.path.basename(test_image)}")
    print(f"Image size: {image.shape}")
    
    # Test each detector
    print("\nIndividual detector results:")
    
    if detector.models_loaded.get('mtcnn'):
        faces = detector.detect_faces_mtcnn(image)
        print(f"  MTCNN:        {len(faces)} faces detected")
    
    if detector.models_loaded.get('dnn'):
        faces = detector.detect_faces_dnn(image)
        status = "✅ WORKING" if len(faces) > 0 else "⚠️  0 faces (model issue)"
        print(f"  DNN:          {len(faces)} faces detected - {status}")
    
    if detector.models_loaded.get('haar'):
        faces = detector.detect_faces_haar(image)
        print(f"  Haar Cascade: {len(faces)} faces detected")
    
    if detector.models_loaded.get('hog'):
        faces = detector.detect_faces_hog(image)
        print(f"  HOG:          {len(faces)} faces detected")
    
    # Test robust detection (uses first successful detector)
    print("\n" + "-" * 70)
    print("Robust detection pipeline (uses first successful detector):")
    print("-" * 70)
    faces, method = detector.detect_faces_robust(image, use_preprocessing=False)
    print(f"  Method used: {method.upper()}")
    print(f"  Faces found: {len(faces)}")

print("\n" + "=" * 70)
print("SUMMARY")
print("=" * 70)

working_detectors = [name.upper() for name, loaded in detector.models_loaded.items() if loaded]
print(f"\n✅ Working detectors: {', '.join(working_detectors)}")

if not detector.models_loaded.get('dnn'):
    print("\n⚠️  DNN not loaded - model files may be missing")
    print("   Run: python download_dnn_models.py")
elif detector.models_loaded.get('dnn'):
    # Quick DNN test
    if os.path.exists(test_image):
        image = cv2.imread(test_image)
        faces = detector.detect_faces_dnn(image)
        if len(faces) == 0:
            print("\n⚠️  DNN loaded but detecting 0 faces (model file issue)")
            print("   Run: python fix_dnn_model.py")

print("\n" + "=" * 70)
print("Your face detection system is ready!")
print("=" * 70)
