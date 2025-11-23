#!/usr/bin/env python3
"""
Test Enhanced Face Detector

Comprehensive tests for the EnhancedFaceDetector class including:
- Multi-algorithm detection
- Angle estimation
- Quality scoring
- Edge cases and error handling
"""

import cv2
import numpy as np
import sys
from enhanced_face_detector import EnhancedFaceDetector

def create_test_image(size=(400, 400), face_type='frontal'):
    """
    Create a synthetic test image with a face-like pattern
    
    Args:
        size: Image dimensions (width, height)
        face_type: Type of face to simulate
        
    Returns:
        numpy array representing the test image
    """
    img = np.ones((size[1], size[0], 3), dtype=np.uint8) * 200  # Gray background
    
    # Draw a simple face-like pattern
    center_x, center_y = size[0] // 2, size[1] // 2
    
    # Face oval
    cv2.ellipse(img, (center_x, center_y), (80, 100), 0, 0, 360, (180, 150, 120), -1)
    
    # Eyes
    cv2.circle(img, (center_x - 30, center_y - 20), 10, (50, 50, 50), -1)
    cv2.circle(img, (center_x + 30, center_y - 20), 10, (50, 50, 50), -1)
    
    # Nose
    cv2.line(img, (center_x, center_y), (center_x, center_y + 30), (150, 120, 100), 2)
    
    # Mouth
    cv2.ellipse(img, (center_x, center_y + 50), (30, 15), 0, 0, 180, (100, 50, 50), 2)
    
    return img

def test_initialization():
    """Test 1: Detector initialization"""
    print("\n" + "=" * 70)
    print("TEST 1: Detector Initialization")
    print("=" * 70)
    
    try:
        detector = EnhancedFaceDetector()
        print("✓ Detector initialized successfully")
        
        # Check which detectors loaded
        loaded_count = sum(detector.detectors_loaded.values())
        total_count = len(detector.detectors_loaded)
        print(f"✓ Loaded {loaded_count}/{total_count} detection algorithms")
        
        for method, loaded in detector.detectors_loaded.items():
            status = "✓" if loaded else "✗"
            print(f"  {status} {method.upper()}")
        
        return detector, True
    except Exception as e:
        print(f"✗ Initialization failed: {e}")
        return None, False

def test_face_detection(detector):
    """Test 2: Face detection on synthetic image"""
    print("\n" + "=" * 70)
    print("TEST 2: Face Detection")
    print("=" * 70)
    
    try:
        # Create test image
        test_img = create_test_image()
        print("✓ Created synthetic test image")
        
        # Detect faces
        detections = detector.detect_faces(test_img)
        print(f"✓ Detection completed")
        print(f"  Detected {len(detections)} face(s)")
        
        if detections:
            for i, det in enumerate(detections, 1):
                print(f"\n  Face {i}:")
                print(f"    Method: {det['method']}")
                print(f"    Confidence: {det['confidence']:.2f}")
                print(f"    BBox: {det['bbox']}")
        
        return True
    except Exception as e:
        print(f"✗ Face detection failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_angle_estimation(detector):
    """Test 3: Angle estimation"""
    print("\n" + "=" * 70)
    print("TEST 3: Angle Estimation")
    print("=" * 70)
    
    try:
        # Test with different face orientations
        test_cases = [
            ('frontal', create_test_image(face_type='frontal')),
            ('profile', create_test_image(face_type='profile'))
        ]
        
        for face_type, test_img in test_cases:
            print(f"\n  Testing {face_type} face:")
            
            # Create a face region (simulated)
            face_region = test_img[100:300, 100:300]
            
            # Estimate angle
            angle = detector.estimate_angle(face_region)
            print(f"    Estimated angle: {angle}")
            
            # Validate angle is one of the expected values
            valid_angles = ['frontal', 'left_45', 'right_45', 'left_90', 'right_90']
            if angle in valid_angles:
                print(f"    ✓ Valid angle classification")
            else:
                print(f"    ✗ Invalid angle: {angle}")
                return False
        
        print("\n✓ Angle estimation test passed")
        return True
    except Exception as e:
        print(f"✗ Angle estimation failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_quality_scoring(detector):
    """Test 4: Quality scoring"""
    print("\n" + "=" * 70)
    print("TEST 4: Quality Scoring")
    print("=" * 70)
    
    try:
        # Create test images with different quality characteristics
        test_cases = [
            ('normal', create_test_image()),
            ('small', create_test_image(size=(100, 100))),
            ('large', create_test_image(size=(600, 600)))
        ]
        
        for case_name, test_img in test_cases:
            print(f"\n  Testing {case_name} image:")
            
            # Extract face region
            h, w = test_img.shape[:2]
            face_region = test_img[h//4:3*h//4, w//4:3*w//4]
            
            # Calculate quality
            quality = detector.calculate_quality_score(face_region)
            
            print(f"    Blur score: {quality['blur_score']:.3f}")
            print(f"    Lighting score: {quality['lighting_score']:.3f}")
            print(f"    Size score: {quality['size_score']:.3f}")
            print(f"    Overall score: {quality['overall_score']:.3f}")
            
            # Validate scores are in range [0, 1]
            for score_name, score_value in quality.items():
                if not (0.0 <= score_value <= 1.0):
                    print(f"    ✗ {score_name} out of range: {score_value}")
                    return False
            
            print(f"    ✓ All scores in valid range [0, 1]")
        
        print("\n✓ Quality scoring test passed")
        return True
    except Exception as e:
        print(f"✗ Quality scoring failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_edge_cases(detector):
    """Test 5: Edge cases and error handling"""
    print("\n" + "=" * 70)
    print("TEST 5: Edge Cases")
    print("=" * 70)
    
    try:
        # Test 1: Empty image
        print("\n  Testing empty image:")
        empty_img = np.zeros((100, 100, 3), dtype=np.uint8)
        detections = detector.detect_faces(empty_img)
        print(f"    Detections: {len(detections)}")
        print(f"    ✓ Handled empty image")
        
        # Test 2: Very small image
        print("\n  Testing very small image:")
        tiny_img = np.ones((10, 10, 3), dtype=np.uint8) * 128
        detections = detector.detect_faces(tiny_img)
        print(f"    Detections: {len(detections)}")
        print(f"    ✓ Handled tiny image")
        
        # Test 3: Grayscale image
        print("\n  Testing grayscale image:")
        gray_img = np.ones((200, 200), dtype=np.uint8) * 128
        # Convert to BGR for detector
        bgr_img = cv2.cvtColor(gray_img, cv2.COLOR_GRAY2BGR)
        detections = detector.detect_faces(bgr_img)
        print(f"    Detections: {len(detections)}")
        print(f"    ✓ Handled grayscale image")
        
        # Test 4: Very bright image
        print("\n  Testing very bright image:")
        bright_img = np.ones((200, 200, 3), dtype=np.uint8) * 250
        detections = detector.detect_faces(bright_img)
        print(f"    Detections: {len(detections)}")
        print(f"    ✓ Handled bright image")
        
        # Test 5: Very dark image
        print("\n  Testing very dark image:")
        dark_img = np.ones((200, 200, 3), dtype=np.uint8) * 10
        detections = detector.detect_faces(dark_img)
        print(f"    Detections: {len(detections)}")
        print(f"    ✓ Handled dark image")
        
        print("\n✓ Edge cases test passed")
        return True
    except Exception as e:
        print(f"✗ Edge cases test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_statistics(detector):
    """Test 6: Detection statistics"""
    print("\n" + "=" * 70)
    print("TEST 6: Detection Statistics")
    print("=" * 70)
    
    try:
        # Get statistics
        stats = detector.get_detection_stats()
        print("\n  Current statistics:")
        for method, count in stats.items():
            print(f"    {method}: {count}")
        
        # Reset statistics
        detector.reset_stats()
        stats_after_reset = detector.get_detection_stats()
        
        # Verify reset
        all_zero = all(count == 0 for count in stats_after_reset.values())
        if all_zero:
            print("\n  ✓ Statistics reset successfully")
        else:
            print("\n  ✗ Statistics reset failed")
            return False
        
        print("\n✓ Statistics test passed")
        return True
    except Exception as e:
        print(f"✗ Statistics test failed: {e}")
        return False

def run_all_tests():
    """Run all tests"""
    print("\n" + "=" * 70)
    print("ENHANCED FACE DETECTOR - COMPREHENSIVE TEST SUITE")
    print("=" * 70)
    
    results = {}
    
    # Test 1: Initialization
    detector, results['initialization'] = test_initialization()
    
    if not detector:
        print("\n" + "=" * 70)
        print("❌ TESTS FAILED - Could not initialize detector")
        print("=" * 70)
        return False
    
    # Test 2: Face Detection
    results['detection'] = test_face_detection(detector)
    
    # Test 3: Angle Estimation
    results['angle_estimation'] = test_angle_estimation(detector)
    
    # Test 4: Quality Scoring
    results['quality_scoring'] = test_quality_scoring(detector)
    
    # Test 5: Edge Cases
    results['edge_cases'] = test_edge_cases(detector)
    
    # Test 6: Statistics
    results['statistics'] = test_statistics(detector)
    
    # Print summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    
    passed = sum(results.values())
    total = len(results)
    
    for test_name, passed_test in results.items():
        status = "✓ PASS" if passed_test else "✗ FAIL"
        print(f"  {status}: {test_name.replace('_', ' ').title()}")
    
    print("\n" + "=" * 70)
    if passed == total:
        print(f"✅ ALL TESTS PASSED ({passed}/{total})")
        print("=" * 70)
        print("\nEnhanced Face Detector is ready for use!")
        print("\nNext steps:")
        print("1. Test with real images")
        print("2. Continue with Task 1.2.4: Test face detection")
        print("3. Move to Task 2.1: Deep Feature Extractor")
        return True
    else:
        print(f"❌ SOME TESTS FAILED ({passed}/{total} passed)")
        print("=" * 70)
        return False

def main():
    """Main test function"""
    success = run_all_tests()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
