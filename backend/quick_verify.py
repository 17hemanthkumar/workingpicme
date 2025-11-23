"""
Quick verification that face detection works
"""

import cv2
import os
from robust_face_detector import RobustFaceDetector

print("=" * 70)
print("QUICK VERIFICATION: Face Detection")
print("=" * 70)

# Initialize detector
print("\n1. Initializing robust detector...")
detector = RobustFaceDetector()
print("   ✓ Detector loaded")

# Test on actual photo
photo_path = "../uploads/event_931cd6b8/2516695c_WhatsApp_Image_2025-11-20_at_5.05.29_PM.jpeg"

print(f"\n2. Testing detection on: {os.path.basename(photo_path)}")

if not os.path.exists(photo_path):
    print("   ✗ Photo not found")
else:
    img = cv2.imread(photo_path)
    if img is None:
        print("   ✗ Could not load image")
    else:
        print(f"   ✓ Image loaded: {img.shape}")
        
        # Detect faces
        faces, method = detector.detect_faces_robust(img, use_preprocessing=True)
        
        print(f"\n3. Detection Results:")
        print(f"   Method used: {method}")
        print(f"   Faces detected: {len(faces)}")
        
        if len(faces) > 0:
            print("\n   ✓ FACE DETECTION WORKING!")
            for i, face in enumerate(faces[:5]):
                box = face['box']
                conf = face.get('confidence', 0)
                print(f"      Face {i+1}: box={box}, confidence={conf:.2f}")
        else:
            print("\n   ✗ No faces detected")
        
        # Show stats
        print("\n4. Detection Statistics:")
        detector.print_stats()

print("\n" + "=" * 70)
print("VERIFICATION COMPLETE")
print("=" * 70)
