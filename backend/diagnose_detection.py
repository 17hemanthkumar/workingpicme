"""
Diagnostic script to test face detection on actual uploaded photos
"""

import cv2
import os
import sys

# Test 1: Check if photos exist and can be loaded
print("=" * 70)
print("DIAGNOSTIC TEST: Face Detection on Actual Photos")
print("=" * 70)

event_folder = "../uploads/event_931cd6b8"
photos = [
    "10750d04_WhatsApp_Image_2025-11-20_at_5.13.03_PM.jpeg",
    "2516695c_WhatsApp_Image_2025-11-20_at_5.05.29_PM.jpeg",
    "40aff6b6_WhatsApp_Image_2025-11-20_at_5.05.29_PM_1.jpeg",
    "e52140b7_WhatsApp_Image_2025-11-20_at_5.05.29_PM_1.jpeg"
]

print("\n1. Testing Image Loading:")
print("-" * 70)

for photo in photos:
    photo_path = os.path.join(event_folder, photo)
    exists = os.path.exists(photo_path)
    print(f"\n{photo}:")
    print(f"  Exists: {exists}")
    
    if exists:
        img = cv2.imread(photo_path)
        if img is not None:
            print(f"  ✓ Loaded successfully")
            print(f"  Shape: {img.shape}")
            print(f"  Dtype: {img.dtype}")
            print(f"  Min/Max: {img.min()}, {img.max()}")
        else:
            print(f"  ✗ Failed to load")

# Test 2: Try Haar Cascade directly
print("\n\n2. Testing Haar Cascade Detection:")
print("-" * 70)

try:
    haar_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
    face_cascade = cv2.CascadeClassifier(haar_path)
    print(f"✓ Haar Cascade loaded from: {haar_path}")
    
    for photo in photos[:2]:  # Test first 2 photos
        photo_path = os.path.join(event_folder, photo)
        if os.path.exists(photo_path):
            img = cv2.imread(photo_path)
            if img is not None:
                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                faces = face_cascade.detectMultiScale(
                    gray,
                    scaleFactor=1.1,
                    minNeighbors=5,
                    minSize=(30, 30)
                )
                print(f"\n{photo}:")
                print(f"  Haar detected: {len(faces)} face(s)")
                if len(faces) > 0:
                    for i, (x, y, w, h) in enumerate(faces):
                        print(f"    Face {i+1}: x={x}, y={y}, w={w}, h={h}")

except Exception as e:
    print(f"✗ Haar Cascade error: {e}")

# Test 3: Try HOG detector
print("\n\n3. Testing HOG Detection:")
print("-" * 70)

try:
    import dlib
    hog_detector = dlib.get_frontal_face_detector()
    print("✓ HOG detector loaded")
    
    for photo in photos[:2]:
        photo_path = os.path.join(event_folder, photo)
        if os.path.exists(photo_path):
            img = cv2.imread(photo_path)
            if img is not None:
                rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                faces = hog_detector(rgb, 1)
                print(f"\n{photo}:")
                print(f"  HOG detected: {len(faces)} face(s)")
                if len(faces) > 0:
                    for i, det in enumerate(faces):
                        print(f"    Face {i+1}: left={det.left()}, top={det.top()}, right={det.right()}, bottom={det.bottom()}")

except ImportError:
    print("✗ dlib not installed")
except Exception as e:
    print(f"✗ HOG error: {e}")

# Test 4: Try face_recognition library
print("\n\n4. Testing face_recognition Library:")
print("-" * 70)

try:
    import face_recognition
    print("✓ face_recognition library loaded")
    
    for photo in photos[:2]:
        photo_path = os.path.join(event_folder, photo)
        if os.path.exists(photo_path):
            img = face_recognition.load_image_file(photo_path)
            face_locations = face_recognition.face_locations(img)
            print(f"\n{photo}:")
            print(f"  face_recognition detected: {len(face_locations)} face(s)")
            if len(face_locations) > 0:
                for i, (top, right, bottom, left) in enumerate(face_locations):
                    print(f"    Face {i+1}: top={top}, right={right}, bottom={bottom}, left={left}")

except ImportError:
    print("✗ face_recognition not installed")
except Exception as e:
    print(f"✗ face_recognition error: {e}")

# Test 5: Try robust detector
print("\n\n5. Testing Robust Face Detector:")
print("-" * 70)

try:
    from robust_face_detector import RobustFaceDetector
    detector = RobustFaceDetector()
    print("✓ Robust detector initialized")
    
    for photo in photos[:2]:
        photo_path = os.path.join(event_folder, photo)
        if os.path.exists(photo_path):
            img = cv2.imread(photo_path)
            if img is not None:
                faces, method = detector.detect_faces_robust(img, use_preprocessing=True, enhancement_level='heavy')
                print(f"\n{photo}:")
                print(f"  Robust detector ({method}): {len(faces)} face(s)")
                if len(faces) > 0:
                    for i, face in enumerate(faces):
                        box = face['box']
                        conf = face.get('confidence', 0)
                        print(f"    Face {i+1}: box={box}, confidence={conf:.2f}")

except Exception as e:
    print(f"✗ Robust detector error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 70)
print("DIAGNOSTIC TEST COMPLETE")
print("=" * 70)
