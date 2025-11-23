"""
Test script for Enhanced Multi-Angle Face Recognition System

This script tests the bidirectional cross-angle matching functionality.
"""

import numpy as np
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from multi_angle_face_model import (
    MultiAngleFaceModel,
    detect_face_orientation,
    assess_image_quality
)
from face_recognition_config import (
    MINIMUM_MATCH_CONFIDENCE,
    TOLERANCE_NORMAL,
    get_weights_for_orientation,
    validate_config
)

def test_configuration():
    """Test configuration system"""
    print("=" * 70)
    print("TEST 1: Configuration System")
    print("=" * 70)
    
    print(f"✓ Minimum Match Confidence: {MINIMUM_MATCH_CONFIDENCE}%")
    print(f"✓ Normal Tolerance: {TOLERANCE_NORMAL}")
    
    # Test weight retrieval
    for orientation in ['center', 'left', 'right', 'angle_left', 'angle_right', 'unknown']:
        weights = get_weights_for_orientation(orientation)
        print(f"✓ Weights for {orientation}: {weights}")
    
    # Validate config
    is_valid = validate_config()
    print(f"✓ Configuration valid: {is_valid}")
    print()


def test_model_initialization():
    """Test model initialization"""
    print("=" * 70)
    print("TEST 2: Model Initialization")
    print("=" * 70)
    
    model = MultiAngleFaceModel(data_file='test_multi_angle_faces.dat')
    print(f"✓ Model initialized")
    print(f"✓ Known faces: {len(model.known_faces)}")
    print(f"✓ Tolerance settings: {model.TOLERANCE_SETTINGS}")
    print()
    
    return model


def test_multi_angle_storage(model):
    """Test multi-angle encoding storage"""
    print("=" * 70)
    print("TEST 3: Multi-Angle Encoding Storage")
    print("=" * 70)
    
    # Create dummy encodings (128-dimensional vectors)
    center_encoding = np.random.rand(128)
    left_encoding = np.random.rand(128)
    right_encoding = np.random.rand(128)
    
    # Normalize encodings
    center_encoding = center_encoding / np.linalg.norm(center_encoding)
    left_encoding = left_encoding / np.linalg.norm(left_encoding)
    right_encoding = right_encoding / np.linalg.norm(right_encoding)
    
    encodings_dict = {
        'center': center_encoding,
        'left': left_encoding,
        'right': right_encoding
    }
    
    quality_scores = {
        'center': 85.5,
        'left': 82.3,
        'right': 88.1
    }
    
    # Learn face
    person_id = model.learn_face_multi_angle(encodings_dict, quality_scores)
    print(f"✓ Stored multi-angle encodings for: {person_id}")
    print(f"✓ Angles stored: {list(encodings_dict.keys())}")
    print(f"✓ Quality scores: {quality_scores}")
    print()
    
    return person_id, encodings_dict


def test_cross_angle_matching(model, person_id, stored_encodings):
    """Test cross-angle matching"""
    print("=" * 70)
    print("TEST 4: Cross-Angle Matching")
    print("=" * 70)
    
    test_cases = [
        {
            'name': 'Same angle (center → center)',
            'test_encoding': stored_encodings['center'],
            'orientation': 'center',
            'expected_match': True
        },
        {
            'name': 'Cross angle (center → left)',
            'test_encoding': stored_encodings['center'],
            'orientation': 'left',
            'expected_match': True
        },
        {
            'name': 'Cross angle (left → right)',
            'test_encoding': stored_encodings['left'],
            'orientation': 'right',
            'expected_match': True
        },
        {
            'name': 'Cross angle (right → center)',
            'test_encoding': stored_encodings['right'],
            'orientation': 'center',
            'expected_match': True
        }
    ]
    
    for test_case in test_cases:
        print(f"\nTest: {test_case['name']}")
        print("-" * 50)
        
        matched_id, confidence, matched_angle, distance, details = model.recognize_face_multi_angle(
            test_case['test_encoding'],
            adaptive_tolerance=True,
            photo_orientation=test_case['orientation'],
            has_accessories=False,
            quality_score=0.85
        )
        
        is_match = matched_id == person_id
        status = "✓ PASS" if is_match == test_case['expected_match'] else "✗ FAIL"
        
        print(f"{status}")
        print(f"  Matched ID: {matched_id}")
        print(f"  Confidence: {confidence:.1f}%")
        print(f"  Distance: {distance:.3f}")
        print(f"  Orientation: {test_case['orientation']}")
        
        if details:
            print(f"  Center distance: {details.get('distance_to_center', 0):.3f}")
            print(f"  Left distance: {details.get('distance_to_left', 0):.3f}")
            print(f"  Right distance: {details.get('distance_to_right', 0):.3f}")
    
    print()


def test_adaptive_tolerance(model, person_id, stored_encodings):
    """Test adaptive tolerance for challenging conditions"""
    print("=" * 70)
    print("TEST 5: Adaptive Tolerance")
    print("=" * 70)
    
    # Add some noise to simulate challenging conditions
    noisy_encoding = stored_encodings['center'] + np.random.normal(0, 0.1, 128)
    noisy_encoding = noisy_encoding / np.linalg.norm(noisy_encoding)
    
    test_cases = [
        {
            'name': 'Normal conditions',
            'has_accessories': False,
            'quality_score': 0.9
        },
        {
            'name': 'With sunglasses',
            'has_accessories': True,
            'quality_score': 0.9
        },
        {
            'name': 'Low quality',
            'has_accessories': False,
            'quality_score': 0.4
        },
        {
            'name': 'Sunglasses + Low quality',
            'has_accessories': True,
            'quality_score': 0.4
        }
    ]
    
    for test_case in test_cases:
        print(f"\nTest: {test_case['name']}")
        print("-" * 50)
        
        matched_id, confidence, matched_angle, distance, details = model.recognize_face_multi_angle(
            noisy_encoding,
            adaptive_tolerance=True,
            photo_orientation='center',
            has_accessories=test_case['has_accessories'],
            quality_score=test_case['quality_score']
        )
        
        is_match = matched_id == person_id
        status = "✓ MATCH" if is_match else "✗ NO MATCH"
        
        print(f"{status}")
        print(f"  Confidence: {confidence:.1f}%")
        print(f"  Distance: {distance:.3f}")
        print(f"  Tolerance used: {details.get('tolerance_used', 0):.3f}")
        print(f"  Min confidence required: {details.get('min_confidence_required', 0):.1f}%")
    
    print()


def test_70_percent_threshold(model):
    """Test 70% confidence threshold"""
    print("=" * 70)
    print("TEST 6: 70% Confidence Threshold")
    print("=" * 70)
    
    # Create a test encoding
    test_encoding = np.random.rand(128)
    test_encoding = test_encoding / np.linalg.norm(test_encoding)
    
    # Store it
    encodings_dict = {
        'center': test_encoding,
        'left': np.random.rand(128) / np.linalg.norm(np.random.rand(128)),
        'right': np.random.rand(128) / np.linalg.norm(np.random.rand(128))
    }
    
    person_id = model.learn_face_multi_angle(encodings_dict)
    
    # Test with varying distances
    test_distances = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7]
    
    print("\nDistance → Confidence → Match Decision:")
    print("-" * 50)
    
    for dist in test_distances:
        # Create encoding at specific distance
        test_enc = test_encoding + np.random.normal(0, dist, 128)
        test_enc = test_enc / np.linalg.norm(test_enc)
        
        matched_id, confidence, _, actual_dist, details = model.recognize_face_multi_angle(
            test_enc,
            adaptive_tolerance=True,
            photo_orientation='center'
        )
        
        is_match = matched_id is not None
        threshold = details.get('min_confidence_required', 70.0)
        
        print(f"Distance: {actual_dist:.3f} → Confidence: {confidence:.1f}% → "
              f"{'✓ MATCH' if is_match else '✗ NO MATCH'} (threshold: {threshold:.1f}%)")
    
    print()


def run_all_tests():
    """Run all tests"""
    print("\n")
    print("=" * 70)
    print("ENHANCED MULTI-ANGLE FACE RECOGNITION SYSTEM - TEST SUITE")
    print("=" * 70)
    print()
    
    try:
        # Test 1: Configuration
        test_configuration()
        
        # Test 2: Model initialization
        model = test_model_initialization()
        
        # Test 3: Multi-angle storage
        person_id, stored_encodings = test_multi_angle_storage(model)
        
        # Test 4: Cross-angle matching
        test_cross_angle_matching(model, person_id, stored_encodings)
        
        # Test 5: Adaptive tolerance
        test_adaptive_tolerance(model, person_id, stored_encodings)
        
        # Test 6: 70% threshold
        test_70_percent_threshold(model)
        
        print("=" * 70)
        print("ALL TESTS COMPLETED")
        print("=" * 70)
        print()
        
        # Cleanup test file
        if os.path.exists('test_multi_angle_faces.dat'):
            os.remove('test_multi_angle_faces.dat')
            print("✓ Cleaned up test data file")
        
    except Exception as e:
        print(f"\n✗ TEST FAILED WITH ERROR: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    run_all_tests()
