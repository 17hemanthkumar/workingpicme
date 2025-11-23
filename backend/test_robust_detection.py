"""
Test Script for Robust Face Detection System
Tests all detection methods and preprocessing
"""

import os
import sys

def test_imports():
    """Test if all required libraries can be imported"""
    print("\n" + "="*80)
    print("TEST 1: Testing Imports")
    print("="*80)
    
    results = {}
    
    # Test OpenCV
    try:
        import cv2
        print(f"✓ OpenCV version: {cv2.__version__}")
        results['opencv'] = True
    except ImportError as e:
        print(f"✗ OpenCV import failed: {e}")
        results['opencv'] = False
    
    # Test MTCNN
    try:
        from mtcnn import MTCNN
        print("✓ MTCNN imported successfully")
        results['mtcnn'] = True
    except ImportError as e:
        print(f"✗ MTCNN import failed: {e}")
        results['mtcnn'] = False
    
    # Test dlib
    try:
        import dlib
        print("✓ dlib imported successfully")
        results['dlib'] = True
    except ImportError as e:
        print(f"✗ dlib import failed: {e}")
        results['dlib'] = False
    
    # Test face_recognition
    try:
        import face_recognition
        print("✓ face_recognition imported successfully")
        results['face_recognition'] = True
    except ImportError as e:
        print(f"✗ face_recognition import failed: {e}")
        results['face_recognition'] = False
    
    return results

def test_robust_detector():
    """Test the RobustFaceDetector class"""
    print("\n" + "="*80)
    print("TEST 2: Testing RobustFaceDetector")
    print("="*80)
    
    try:
        from robust_face_detector import RobustFaceDetector
        
        detector = RobustFaceDetector()
        
        print("\nDetector initialized successfully!")
        print(f"\nAvailable detection methods:")
        for method, available in detector.models_loaded.items():
            status = "✓ Available" if available else "✗ Not available"
            print(f"  {method.upper()}: {status}")
        
        available_count = sum(detector.models_loaded.values())
        print(f"\nTotal: {available_count}/4 detection methods available")
        
        if available_count == 0:
            print("\n⚠ WARNING: No detection methods available!")
            print("  Please install at least one of: mtcnn, dlib, or opencv")
            return False
        
        return True
        
    except Exception as e:
        print(f"\n✗ RobustFaceDetector test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_preprocessing():
    """Test image preprocessing"""
    print("\n" + "="*80)
    print("TEST 3: Testing Image Preprocessing")
    print("="*80)
    
    try:
        import cv2
        import numpy as np
        from robust_face_detector import RobustFaceDetector
        
        # Create a test image
        test_image = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
        
        detector = RobustFaceDetector()
        
        # Test preprocessing
        variants = detector.preprocess_image(test_image, enhancement_level='medium')
        
        print(f"\n✓ Preprocessing successful!")
        print(f"  Generated {len(variants)} image variants")
        print(f"  Enhancement level: medium")
        
        # Test different enhancement levels
        for level in ['light', 'medium', 'heavy']:
            variants = detector.preprocess_image(test_image, enhancement_level=level)
            print(f"  {level.capitalize()} enhancement: {len(variants)} variants")
        
        return True
        
    except Exception as e:
        print(f"\n✗ Preprocessing test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_detection_on_sample():
    """Test detection on a sample image if available"""
    print("\n" + "="*80)
    print("TEST 4: Testing Detection on Sample Image")
    print("="*80)
    
    # Look for a sample image in uploads folder
    uploads_dir = os.path.join(os.path.dirname(__file__), '..', 'uploads')
    
    sample_image = None
    if os.path.exists(uploads_dir):
        for event_folder in os.listdir(uploads_dir):
            event_path = os.path.join(uploads_dir, event_folder)
            if os.path.isdir(event_path):
                for filename in os.listdir(event_path):
                    if filename.lower().endswith(('.jpg', '.jpeg', '.png')) and not filename.endswith('_qr.png'):
                        sample_image = os.path.join(event_path, filename)
                        break
            if sample_image:
                break
    
    if not sample_image:
        print("⚠ No sample image found in uploads folder")
        print("  Skipping detection test")
        return True
    
    try:
        import cv2
        from robust_face_detector import RobustFaceDetector
        
        print(f"\nTesting on: {os.path.basename(sample_image)}")
        
        # Load image
        image = cv2.imread(sample_image)
        if image is None:
            print(f"✗ Could not load image")
            return False
        
        print(f"  Image size: {image.shape[1]}x{image.shape[0]}")
        
        # Detect faces
        detector = RobustFaceDetector()
        faces, method = detector.detect_faces_robust(image, use_preprocessing=True)
        
        print(f"\n✓ Detection complete!")
        print(f"  Method used: {method.upper()}")
        print(f"  Faces detected: {len(faces)}")
        
        if faces:
            for i, face in enumerate(faces, 1):
                print(f"\n  Face {i}:")
                print(f"    Confidence: {face['confidence']:.2f}")
                print(f"    Method: {face['method']}")
                print(f"    Box: {face['box']}")
        
        return True
        
    except Exception as e:
        print(f"\n✗ Detection test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("\n" + "="*80)
    print("ROBUST FACE DETECTION SYSTEM - TEST SUITE")
    print("="*80)
    
    results = []
    
    # Run tests
    results.append(('Imports', test_imports()))
    results.append(('RobustFaceDetector', test_robust_detector()))
    results.append(('Preprocessing', test_preprocessing()))
    results.append(('Sample Detection', test_detection_on_sample()))
    
    # Summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{test_name}: {status}")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n✓ All tests passed! Robust detection system is ready.")
    elif passed > 0:
        print("\n⚠ Some tests failed, but system may still work with reduced capabilities.")
    else:
        print("\n✗ All tests failed. Please check installation.")
    
    print("="*80)

if __name__ == '__main__':
    main()
