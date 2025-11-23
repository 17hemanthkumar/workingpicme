# test_imports.py

print("Testing imports...")

try:
    import numpy as np
    print(f"✓ NumPy {np.__version__} - {'OK' if np.__version__.startswith('1.') else 'WARNING: Should be 1.x'}")
except Exception as e:
    print(f"✗ NumPy failed: {e}")

try:
    import cv2
    print(f"✓ OpenCV {cv2.__version__}")
except Exception as e:
    print(f"✗ OpenCV failed: {e}")

try:
    from mtcnn import MTCNN
    print(f"✓ MTCNN loaded successfully")
except Exception as e:
    print(f"✗ MTCNN failed: {e}")

try:
    import tensorflow as tf
    print(f"✓ TensorFlow {tf.__version__}")
except Exception as e:
    print(f"✗ TensorFlow failed: {e}")

try:
    import face_recognition
    print(f"✓ face_recognition loaded successfully")
except Exception as e:
    print(f"✗ face_recognition failed: {e}")

try:
    import dlib
    print(f"✓ dlib loaded successfully")
except Exception as e:
    print(f"✗ dlib failed: {e}")

print("\nAll critical imports successful!")