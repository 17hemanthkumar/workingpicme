"""
Test Pose Validation and Duplicate Detection
"""

import numpy as np
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from live_face_scanner import LiveFaceScanner

def test_pose_validation():
    """Test pose validation logic"""
    print("=" * 70)
    print("TEST: Pose Validation and Duplicate Detection")
    print("=" * 70)
    
    scanner = LiveFaceScanner()
    
    # Test 1: Validate CENTER pose
    print("\n1. Testing CENTER pose validation:")
    print("-" * 50)
    
    test_angles = [0, 5, -5, 10, -10, 20, -20]
    for angle in test_angles:
        is_valid, message = scanner._validate_pose_for_stage(angle)
        status = "✓ PASS" if is_valid else "✗ FAIL"
        print(f"  Angle {angle:+.1f}°: {status} - {message}")
    
    # Test 2: Validate LEFT pose
    print("\n2. Testing LEFT pose validation:")
    print("-" * 50)
    scanner.current_angle = 'left'
    
    test_angles = [0, -10, -20, -30, -40, -50, -60]
    for angle in test_angles:
        is_valid, message = scanner._validate_pose_for_stage(angle)
        status = "✓ PASS" if is_valid else "✗ FAIL"
        print(f"  Angle {angle:+.1f}°: {status} - {message}")
    
    # Test 3: Validate RIGHT pose
    print("\n3. Testing RIGHT pose validation:")
    print("-" * 50)
    scanner.current_angle = 'right'
    
    test_angles = [0, 10, 20, 30, 40, 50, 60]
    for angle in test_angles:
        is_valid, message = scanner._validate_pose_for_stage(angle)
        status = "✓ PASS" if is_valid else "✗ FAIL"
        print(f"  Angle {angle:+.1f}°: {status} - {message}")
    
    # Test 4: Duplicate pose detection
    print("\n4. Testing DUPLICATE pose detection:")
    print("-" * 50)
    
    # Simulate capturing CENTER at 3°
    scanner.captured_pose_angles['front'] = 3.0
    print(f"  Captured 'front' at 3.0°")
    
    # Try to capture similar angles
    test_angles = [2, 5, 10, 25, -30]
    for angle in test_angles:
        is_dup, message = scanner._check_duplicate_pose(angle)
        status = "✗ DUPLICATE" if is_dup else "✓ UNIQUE"
        print(f"  Test angle {angle:+.1f}°: {status}")
        if is_dup:
            print(f"    {message}")
    
    # Test 5: Multiple captures with validation
    print("\n5. Testing full capture sequence:")
    print("-" * 50)
    
    scanner.reset()
    
    # Simulate CENTER capture
    scanner.captured_pose_angles['front'] = 2.5
    print(f"  ✓ Captured 'front' at 2.5°")
    
    # Try to capture LEFT at various angles
    scanner.current_angle = 'left'
    test_angles = [5, -10, -35, -45]
    
    for angle in test_angles:
        # Check if valid for LEFT stage
        is_valid, val_msg = scanner._validate_pose_for_stage(angle)
        
        # Check if duplicate
        is_dup, dup_msg = scanner._check_duplicate_pose(angle)
        
        if is_valid and not is_dup:
            print(f"  ✓ Would capture 'left' at {angle:.1f}° - VALID & UNIQUE")
        elif is_dup:
            print(f"  ✗ Cannot capture at {angle:.1f}° - DUPLICATE")
        else:
            print(f"  ✗ Cannot capture at {angle:.1f}° - INVALID POSE")
    
    print("\n" + "=" * 70)
    print("POSE VALIDATION TESTS COMPLETE")
    print("=" * 70)


def test_feature_extractor():
    """Test facial feature extractor"""
    print("\n" + "=" * 70)
    print("TEST: Facial Feature Extractor")
    print("=" * 70)
    
    try:
        from facial_feature_extractor import FacialFeatureExtractor
        
        extractor = FacialFeatureExtractor()
        print("✓ Feature extractor initialized")
        
        # Create dummy landmarks
        dummy_landmarks = {
            'left_eye': [(100, 100), (105, 100), (110, 100), (105, 105), (100, 105), (95, 100)],
            'right_eye': [(150, 100), (155, 100), (160, 100), (155, 105), (150, 105), (145, 100)],
            'left_eyebrow': [(95, 90), (100, 88), (105, 87), (110, 88), (115, 90)],
            'right_eyebrow': [(145, 90), (150, 88), (155, 87), (160, 88), (165, 90)],
            'nose_bridge': [(125, 110), (125, 120), (125, 130), (125, 140)],
            'nose_tip': [(120, 150), (125, 152), (130, 150), (135, 148), (140, 150)],
            'top_lip': [(110, 170), (120, 168), (130, 168), (140, 168), (150, 170)],
            'bottom_lip': [(110, 180), (120, 182), (130, 182), (140, 182), (150, 180)],
            'chin': [(100, 200), (110, 210), (120, 215), (130, 220), (140, 215), (150, 210), (160, 200)]
        }
        
        dummy_face_location = (50, 200, 250, 50)  # top, right, bottom, left
        dummy_image = np.random.randint(0, 255, (300, 300, 3), dtype=np.uint8)
        
        # Extract features
        features = extractor.extract_all_features(
            dummy_image,
            dummy_face_location,
            dummy_landmarks
        )
        
        print(f"✓ Extracted {extractor.feature_count} features")
        print("\nFeature categories:")
        for category, feats in features.items():
            if isinstance(feats, dict):
                print(f"  - {category}: {len(feats)} features")
        
        # Test feature comparison
        features2 = extractor.extract_all_features(
            dummy_image,
            dummy_face_location,
            dummy_landmarks
        )
        
        similarities = extractor.compare_features(features, features2)
        print("\nFeature similarity scores (same face):")
        for category, score in similarities.items():
            print(f"  - {category}: {score:.1f}%")
        
        print("\n✓ Feature extraction and comparison working!")
        
    except Exception as e:
        print(f"✗ Error testing feature extractor: {e}")
        import traceback
        traceback.print_exc()
    
    print("=" * 70)


if __name__ == '__main__':
    test_pose_validation()
    test_feature_extractor()
