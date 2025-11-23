"""
Test MTCNN with optimized configuration
"""

import cv2
import os

print("=" * 70)
print("MTCNN Configuration Test")
print("=" * 70)

# Test image
test_image = "../uploads/event_931cd6b8/2516695c_WhatsApp_Image_2025-11-20_at_5.05.29_PM.jpeg"

if not os.path.exists(test_image):
    print(f"Error: Test image not found at {test_image}")
    exit(1)

# Load image
image = cv2.imread(test_image)
print(f"\nTest image: {os.path.basename(test_image)}")
print(f"Image size: {image.shape}")

# Test 1: Default MTCNN
print("\n" + "=" * 70)
print("Test 1: Default MTCNN Configuration")
print("=" * 70)

try:
    from mtcnn import MTCNN
    
    detector_default = MTCNN()
    rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    
    print("Running detection with default settings...")
    faces_default = detector_default.detect_faces(rgb_image)
    
    print(f"\nResults:")
    print(f"  Faces detected: {len(faces_default)}")
    if len(faces_default) > 0:
        confidences = [f['confidence'] for f in faces_default]
        print(f"  Confidence range: {min(confidences):.3f} - {max(confidences):.3f}")
        print(f"  Average confidence: {sum(confidences)/len(confidences):.3f}")
        
        # Show first 3 faces
        print(f"\n  First 3 detections:")
        for i, face in enumerate(faces_default[:3]):
            box = face['box']
            conf = face['confidence']
            print(f"    Face {i+1}: box={box}, confidence={conf:.3f}")
    
except Exception as e:
    print(f"Error: {e}")

# Test 2: Optimized MTCNN
print("\n" + "=" * 70)
print("Test 2: Optimized MTCNN Configuration")
print("=" * 70)

try:
    from mtcnn import MTCNN
    
    # Optimized configuration
    detector_optimized = MTCNN(
        min_face_size=20,
        steps_threshold=[0.6, 0.7, 0.7],
        scale_factor=0.709
    )
    
    print("Configuration:")
    print("  min_face_size: 20px")
    print("  steps_threshold: [0.6, 0.7, 0.7] (P-Net, R-Net, O-Net)")
    print("  scale_factor: 0.709")
    
    rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    
    print("\nRunning detection with optimized settings...")
    faces_optimized = detector_optimized.detect_faces(rgb_image)
    
    print(f"\nResults:")
    print(f"  Faces detected: {len(faces_optimized)}")
    if len(faces_optimized) > 0:
        confidences = [f['confidence'] for f in faces_optimized]
        print(f"  Confidence range: {min(confidences):.3f} - {max(confidences):.3f}")
        print(f"  Average confidence: {sum(confidences)/len(confidences):.3f}")
        
        # Show first 3 faces
        print(f"\n  First 3 detections:")
        for i, face in enumerate(faces_optimized[:3]):
            box = face['box']
            conf = face['confidence']
            print(f"    Face {i+1}: box={box}, confidence={conf:.3f}")
    
except Exception as e:
    print(f"Error: {e}")

# Comparison
print("\n" + "=" * 70)
print("Comparison")
print("=" * 70)

try:
    print(f"\nDefault MTCNN:   {len(faces_default)} faces")
    print(f"Optimized MTCNN: {len(faces_optimized)} faces")
    
    difference = len(faces_optimized) - len(faces_default)
    if difference > 0:
        print(f"\n✅ Optimized config detected {difference} more face(s)")
    elif difference < 0:
        print(f"\n⚠️  Optimized config detected {abs(difference)} fewer face(s)")
    else:
        print(f"\n✓ Both configurations detected the same number of faces")
    
except:
    pass

print("\n" + "=" * 70)
print("Test Complete")
print("=" * 70)
