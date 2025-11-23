#!/usr/bin/env python3
"""
Comprehensive test for Deep Feature Extractor
Tests encoding extraction, landmark detection, and feature analysis
"""

import cv2
import numpy as np
import os
from deep_feature_extractor import DeepFeatureExtractor
from enhanced_face_detector import EnhancedFaceDetector

def test_deep_feature_extractor():
    """Test the deep feature extractor with real images"""
    print("\n" + "=" * 80)
    print("COMPREHENSIVE DEEP FEATURE EXTRACTOR TEST")
    print("=" * 80)
    
    # Initialize components
    print("\n1. Initializing components...")
    detector = EnhancedFaceDetector()
    extractor = DeepFeatureExtractor()
    print("✓ Components initialized")
    
    # Find test images
    test_dirs = [
        "../uploads/event_931cd6b8",
        "../uploads",
        "../processed"
    ]
    
    test_images = []
    for test_dir in test_dirs:
        if os.path.exists(test_dir):
            for file in os.listdir(test_dir):
                if file.lower().endswith(('.jpg', '.jpeg', '.png')):
                    test_images.append(os.path.join(test_dir, file))
                    if len(test_images) >= 5:  # Test with up to 5 images
                        break
        if test_images:
            break
    
    if not test_images:
        print("\n✗ No test images found")
        return False
    
    print(f"\n2. Found {len(test_images)} test image(s)")
    
    # Test each image
    total_faces = 0
    successful_extractions = 0
    
    for idx, image_path in enumerate(test_images, 1):
        print(f"\n{'=' * 80}")
        print(f"TEST IMAGE {idx}: {os.path.basename(image_path)}")
        print('=' * 80)
        
        # Load image
        image = cv2.imread(image_path)
        if image is None:
            print(f"✗ Failed to load image")
            continue
        
        print(f"Image size: {image.shape[1]}x{image.shape[0]}")
        
        # Detect faces
        print("\n3. Detecting faces...")
        detections = detector.detect_faces(image)
        print(f"✓ Detected {len(detections)} face(s)")
        
        if not detections:
            continue
        
        total_faces += len(detections)
        
        # Process each detected face
        for face_idx, detection in enumerate(detections, 1):
            print(f"\n  --- Face {face_idx} ---")
            
            # Extract face region
            bbox = detection['bbox']
            x, y, w, h = bbox
            face_img = image[y:y+h, x:x+w]
            
            print(f"  Face size: {w}x{h}")
            print(f"  Detection method: {detection['method']}")
            print(f"  Confidence: {detection['confidence']:.3f}")
            
            # Test 1: Extract 128D encoding
            print("\n  TEST 1: 128D Encoding Extraction")
            encoding = extractor.extract_encoding(face_img)
            if encoding is not None:
                print(f"  ✓ Encoding extracted: {encoding.shape[0]} dimensions")
                print(f"    Sample values: [{encoding[0]:.4f}, {encoding[1]:.4f}, {encoding[2]:.4f}, ...]")
                
                # Verify dimensionality
                assert encoding.shape[0] == 128, f"Expected 128 dimensions, got {encoding.shape[0]}"
                print(f"  ✓ Dimensionality verified: 128D")
            else:
                print(f"  ✗ Encoding extraction failed")
                continue
            
            # Test 2: Extract facial landmarks
            print("\n  TEST 2: Facial Landmark Extraction")
            landmarks = extractor.extract_landmarks(face_img)
            if landmarks:
                print(f"  ✓ Landmarks extracted: {len(landmarks)} groups")
                for key, points in landmarks.items():
                    print(f"    - {key}: {len(points)} points")
            else:
                print(f"  ✗ Landmark extraction failed")
            
            # Test 3: Analyze facial features
            print("\n  TEST 3: Facial Feature Analysis")
            features = extractor.analyze_features(face_img, landmarks)
            print(f"  ✓ Features analyzed: {len(features)} measurements")
            
            # Display feature measurements
            print("\n  Feature Measurements:")
            for key, value in features.items():
                if value is not None:
                    if isinstance(value, float):
                        print(f"    {key}: {value:.2f}")
                    elif isinstance(value, bool):
                        print(f"    {key}: {value}")
                    else:
                        print(f"    {key}: {value}")
                else:
                    print(f"    {key}: N/A")
            
            # Test 4: Extract all features at once
            print("\n  TEST 4: Extract All Features")
            all_features = extractor.extract_all(face_img)
            
            has_encoding = all_features['encoding'] is not None
            has_landmarks = all_features['landmarks'] is not None
            has_features = len(all_features['features']) > 0
            
            print(f"  Encoding: {'✓' if has_encoding else '✗'}")
            print(f"  Landmarks: {'✓' if has_landmarks else '✗'}")
            print(f"  Features: {'✓' if has_features else '✗'}")
            
            if has_encoding and has_landmarks and has_features:
                successful_extractions += 1
                print(f"  ✓ All features extracted successfully")
            else:
                print(f"  ✗ Some features failed to extract")
    
    # Print summary
    print(f"\n{'=' * 80}")
    print("TEST SUMMARY")
    print('=' * 80)
    print(f"Images tested: {len(test_images)}")
    print(f"Total faces detected: {total_faces}")
    print(f"Successful extractions: {successful_extractions}/{total_faces}")
    
    # Print extraction statistics
    stats = extractor.get_extraction_stats()
    print(f"\nExtraction Statistics:")
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    # Calculate success rate
    if total_faces > 0:
        success_rate = (successful_extractions / total_faces) * 100
        print(f"\nSuccess Rate: {success_rate:.1f}%")
        
        if success_rate >= 80:
            print("✓ TEST PASSED: Feature extraction working well")
            return True
        else:
            print("✗ TEST FAILED: Low success rate")
            return False
    else:
        print("\n✗ TEST INCONCLUSIVE: No faces detected")
        return False


def test_encoding_properties():
    """Test correctness properties for encodings"""
    print("\n" + "=" * 80)
    print("TESTING ENCODING PROPERTIES")
    print("=" * 80)
    
    extractor = DeepFeatureExtractor()
    
    # Create test face images
    print("\n1. Testing with synthetic faces...")
    
    # Test 1: Encoding dimensionality property
    print("\nProperty 1: Encoding Dimensionality")
    print("For any successfully extracted encoding, it should have exactly 128 dimensions")
    
    # Create a simple test face (white square on black background)
    test_face = np.zeros((100, 100, 3), dtype=np.uint8)
    test_face[25:75, 25:75] = 255  # White square
    
    encoding = extractor.extract_encoding(test_face)
    if encoding is not None:
        assert encoding.shape[0] == 128, f"Expected 128 dimensions, got {encoding.shape[0]}"
        print(f"✓ Property verified: Encoding has {encoding.shape[0]} dimensions")
    else:
        print("✗ Could not extract encoding from synthetic face")
    
    print("\n✓ Property tests complete")


if __name__ == "__main__":
    # Run comprehensive test
    success = test_deep_feature_extractor()
    
    # Run property tests
    test_encoding_properties()
    
    print("\n" + "=" * 80)
    if success:
        print("✓ ALL TESTS PASSED")
    else:
        print("⚠ SOME TESTS FAILED OR INCONCLUSIVE")
    print("=" * 80)
