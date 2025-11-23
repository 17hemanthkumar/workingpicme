"""
Debug DNN detector specifically
"""

import cv2
import numpy as np
import os

# Load image
test_image_path = "../uploads/event_931cd6b8/2516695c_WhatsApp_Image_2025-11-20_at_5.05.29_PM.jpeg"
image = cv2.imread(test_image_path)

print(f"Image shape: {image.shape}")
print(f"Image dtype: {image.dtype}")

# Load DNN model
model_path = "models"
prototxt_path = os.path.join(model_path, 'deploy.prototxt')
caffemodel_path = os.path.join(model_path, 'res10_300x300_ssd_iter_140000.caffemodel')

print(f"\nModel files:")
print(f"  Prototxt exists: {os.path.exists(prototxt_path)}")
print(f"  Caffemodel exists: {os.path.exists(caffemodel_path)}")

# Load detector
dnn_detector = cv2.dnn.readNetFromCaffe(prototxt_path, caffemodel_path)
print("✓ DNN detector loaded")

# Prepare image
h, w = image.shape[:2]
print(f"\nOriginal dimensions: {w}x{h}")

# Create blob
blob = cv2.dnn.blobFromImage(
    cv2.resize(image, (300, 300)), 
    1.0, 
    (300, 300), 
    (104.0, 177.0, 123.0)
)

print(f"Blob shape: {blob.shape}")

# Run detection
dnn_detector.setInput(blob)
detections = dnn_detector.forward()

print(f"\nDetections shape: {detections.shape}")
print(f"Number of detections: {detections.shape[2]}")

# Analyze all detections
print("\nAll detections (showing confidence scores):")
print("-" * 70)

for i in range(detections.shape[2]):
    confidence = detections[0, 0, i, 2]
    box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
    (x1, y1, x2, y2) = box.astype("int")
    
    print(f"Detection {i+1}: confidence={confidence:.4f}, box=({x1}, {y1}, {x2}, {y2})")
    
    # Show which would pass different thresholds
    if confidence > 0.5:
        print(f"  → Would pass 0.5 threshold")
    elif confidence > 0.3:
        print(f"  → Would pass 0.3 threshold")
    elif confidence > 0.1:
        print(f"  → Would pass 0.1 threshold")

print("\n" + "=" * 70)
print("Testing with different thresholds:")
print("=" * 70)

for threshold in [0.1, 0.2, 0.3, 0.4, 0.5]:
    count = 0
    for i in range(detections.shape[2]):
        confidence = detections[0, 0, i, 2]
        if confidence > threshold:
            count += 1
    print(f"Threshold {threshold}: {count} faces detected")
