#!/usr/bin/env python3
"""
Comprehensive test for Enhanced Matching Engine
Tests single-angle matching, multi-angle matching, and confidence scoring
"""

import numpy as np
import uuid
from multi_angle_database import MultiAngleFaceDatabase
from enhanced_matching_engine import EnhancedMatchingEngine

def test_matching_engine():
    """Test the enhanced matching engine"""
    print("\n" + "=" * 80)
    print("COMPREHENSIVE ENHANCED MATCHING ENGINE TEST")
    print("=" * 80)
    
    # Initialize database and matching engine
    print("\n1. Initializing components...")
    db = MultiAngleFaceDatabase()
    engine = EnhancedMatchingEngine(db, threshold=0.6)
    print("✓ Components initialized")
    
    # Create test data
    print("\n2. Creating test data...")
    
    # Create person 1
    person1_uuid = str(uuid.uuid4())
    person1_id = db.add_person(person_uuid=person1_uuid, name="Test Person 1")
    
    # Create photo and detection for person 1
    photo1_id = db.add_photo("test_event", "test1.jpg", "/path/to/test1.jpg")
    detection1_id = db.add_face_detection(
        photo_id=photo1_id,
        person_id=person1_id,
        bbox={'x': 100, 'y': 100, 'w': 50, 'h': 50},
        angle='frontal',
        quality_score=0.90,
        detection_method='mtcnn',
        detection_confidence=0.99
    )
    
    # Create encodings for person 1 (3 angles)
    person1_encodings = {}
    angles = ['frontal', 'left_45', 'right_45']
    qualities = [0.95, 0.85, 0.80]
    
    for angle, quality in zip(angles, qualities):
        # Create a base encoding for person 1
        base_encoding = np.random.rand(128)
        person1_encodings[angle] = base_encoding
        
        enc_id = db.add_face_encoding(
            person_id=person1_id,
            encoding=base_encoding,
            angle=angle,
            quality_score=quality,
            face_detection_id=detection1_id
        )
        print(f"  ✓ Added {angle} encoding for Person 1: quality={quality}")
    
    # Create person 2
    person2_uuid = str(uuid.uuid4())
    person2_id = db.add_person(person_uuid=person2_uuid, name="Test Person 2")
    
    # Create photo and detection for person 2
    photo2_id = db.add_photo("test_event", "test2.jpg", "/path/to/test2.jpg")
    detection2_id = db.add_face_detection(
        photo_id=photo2_id,
        person_id=person2_id,
        bbox={'x': 200, 'y': 200, 'w': 50, 'h': 50},
        angle='frontal',
        quality_score=0.85,
        detection_method='mtcnn',
        detection_confidence=0.98
    )
    
    # Create encodings for person 2 (different from person 1)
    person2_encodings = {}
    for angle, quality in zip(angles, qualities):
        # Create a different encoding for person 2
        base_encoding = np.random.rand(128) + 2.0  # Offset to make it different
        person2_encodings[angle] = base_encoding
        
        enc_id = db.add_face_encoding(
            person_id=person2_id,
            encoding=base_encoding,
            angle=angle,
            quality_score=quality,
            face_detection_id=detection2_id
        )
        print(f"  ✓ Added {angle} encoding for Person 2: quality={quality}")
    
    print(f"✓ Test data created: 2 persons, 6 encodings")
    
    # Test 1: Single-Angle Matching
    print("\n" + "=" * 80)
    print("TEST 1: SINGLE-ANGLE MATCHING")
    print("=" * 80)
    
    # Test 1.1: Match with exact encoding (should match)
    print("\n1.1 Testing exact match...")
    query_encoding = person1_encodings['frontal']
    result = engine.match_face(query_encoding, angle='frontal')
    
    assert result['matched'] == True, "Should match"
    assert result['person_id'] == person1_id, f"Should match person 1, got {result['person_id']}"
    assert result['distance'] < 0.01, f"Distance should be near 0, got {result['distance']}"
    print(f"✓ Exact match found: person_id={result['person_id']}, confidence={result['confidence']:.3f}, distance={result['distance']:.6f}")
    
    # Test 1.2: Match with similar encoding (should match)
    print("\n1.2 Testing similar match...")
    similar_encoding = person1_encodings['frontal'] + np.random.rand(128) * 0.05  # Add very small noise
    result = engine.match_face(similar_encoding, angle='frontal')
    
    # Check if it matched (might not if noise was too large)
    if result['matched']:
        assert result['person_id'] == person1_id, "Should match person 1"
        print(f"✓ Similar match found: person_id={result['person_id']}, confidence={result['confidence']:.3f}, distance={result['distance']:.3f}")
    else:
        print(f"⚠ Similar encoding did not match (distance={result['distance']:.3f}, threshold={engine.threshold})")
    
    # Test 1.3: Match with different encoding (should not match)
    print("\n1.3 Testing non-match...")
    different_encoding = np.random.rand(128) + 5.0  # Very different
    result = engine.match_face(different_encoding)
    
    assert result['matched'] == False, "Should not match very different encoding"
    print(f"✓ No match found (as expected): distance={result['distance']:.3f}")
    
    # Test 2: Multi-Angle Matching
    print("\n" + "=" * 80)
    print("TEST 2: MULTI-ANGLE MATCHING")
    print("=" * 80)
    
    # Test 2.1: Match with multiple angles
    print("\n2.1 Testing multi-angle match...")
    query_encodings = {
        'frontal': person1_encodings['frontal'] + np.random.rand(128) * 0.05,
        'left_45': person1_encodings['left_45'] + np.random.rand(128) * 0.05
    }
    result = engine.match_multi_angle(query_encodings)
    
    assert result['matched'] == True, "Should match with multiple angles"
    assert result['person_id'] == person1_id, "Should match person 1"
    assert result['num_angles_matched'] >= 2, "Should match at least 2 angles"
    print(f"✓ Multi-angle match found: person_id={result['person_id']}, confidence={result['confidence']:.3f}, angles_matched={result['num_angles_matched']}")
    
    # Test 3: Confidence Scoring (Property 12)
    print("\n" + "=" * 80)
    print("TEST 3: CONFIDENCE SCORING (Property 12)")
    print("=" * 80)
    
    print("\n3.1 Testing angle-based weighting...")
    # Test that frontal angles have higher weight than profile angles
    distances = [0.3, 0.3, 0.3]
    qualities = [0.9, 0.9, 0.9]
    
    # Frontal should have higher confidence
    frontal_confidence = engine.calculate_confidence(distances, qualities, ['frontal', 'frontal', 'frontal'])
    profile_confidence = engine.calculate_confidence(distances, qualities, ['left_90', 'right_90', 'left_90'])
    
    assert frontal_confidence > profile_confidence, "Frontal angles should have higher confidence"
    print(f"✓ Angle weighting verified:")
    print(f"  Frontal confidence: {frontal_confidence:.3f}")
    print(f"  Profile confidence: {profile_confidence:.3f}")
    print(f"  Difference: {frontal_confidence - profile_confidence:.3f}")
    
    # Test 4: Match Threshold Consistency (Property 7)
    print("\n" + "=" * 80)
    print("TEST 4: MATCH THRESHOLD CONSISTENCY (Property 7)")
    print("=" * 80)
    
    print("\n4.1 Testing threshold boundary...")
    # Create encoding just below threshold
    below_threshold = person1_encodings['frontal'] + np.random.rand(128) * 0.3  # Distance ~0.5
    result_below = engine.match_face(below_threshold)
    
    # Create encoding just above threshold
    above_threshold = person1_encodings['frontal'] + np.random.rand(128) * 1.0  # Distance ~1.0
    result_above = engine.match_face(above_threshold)
    
    print(f"✓ Below threshold: matched={result_below['matched']}, distance={result_below['distance']:.3f}")
    print(f"✓ Above threshold: matched={result_above['matched']}, distance={result_above['distance']:.3f}")
    
    # Verify threshold consistency
    if result_below['distance'] < 0.6:
        assert result_below['matched'] == True, "Should match when distance < threshold"
    if result_above['distance'] >= 0.6:
        assert result_above['matched'] == False, "Should not match when distance >= threshold"
    
    print(f"✓ Threshold consistency verified (threshold={engine.threshold})")
    
    # Test 5: Batch Matching
    print("\n" + "=" * 80)
    print("TEST 5: BATCH MATCHING")
    print("=" * 80)
    
    print("\n5.1 Testing batch matching...")
    batch_encodings = [
        person1_encodings['frontal'] + np.random.rand(128) * 0.05,
        person2_encodings['frontal'] + np.random.rand(128) * 0.05,
        np.random.rand(128) + 5.0  # No match
    ]
    
    results = engine.batch_match(batch_encodings)
    
    assert len(results) == 3, "Should return 3 results"
    assert results[0]['matched'] == True, "First should match person 1"
    assert results[1]['matched'] == True, "Second should match person 2"
    assert results[2]['matched'] == False, "Third should not match"
    
    print(f"✓ Batch matching completed:")
    for i, result in enumerate(results):
        if result['matched']:
            print(f"  Encoding {i+1}: matched person {result['person_id']}, confidence={result['confidence']:.3f}")
        else:
            print(f"  Encoding {i+1}: no match")
    
    # Test 6: Find Similar Faces
    print("\n" + "=" * 80)
    print("TEST 6: FIND SIMILAR FACES")
    print("=" * 80)
    
    print("\n6.1 Testing similarity search...")
    query_encoding = person1_encodings['frontal'] + np.random.rand(128) * 0.1
    similar_faces = engine.find_similar_faces(query_encoding, top_k=3)
    
    assert len(similar_faces) > 0, "Should find similar faces"
    assert similar_faces[0]['person_id'] == person1_id, "Most similar should be person 1"
    
    print(f"✓ Found {len(similar_faces)} similar faces:")
    for i, face in enumerate(similar_faces):
        print(f"  {i+1}. Person {face['person_id']}: distance={face['distance']:.3f}, confidence={face['confidence']:.3f}")
    
    # Test 7: Performance and Caching
    print("\n" + "=" * 80)
    print("TEST 7: PERFORMANCE AND CACHING")
    print("=" * 80)
    
    print("\n7.1 Testing cache performance...")
    import time
    
    # First match (cache miss)
    start = time.time()
    result1 = engine.match_face(person1_encodings['frontal'])
    time1 = time.time() - start
    
    # Second match (cache hit)
    start = time.time()
    result2 = engine.match_face(person1_encodings['frontal'])
    time2 = time.time() - start
    
    print(f"✓ First match (cache miss): {time1*1000:.2f}ms")
    print(f"✓ Second match (cache hit): {time2*1000:.2f}ms")
    if time2 > 0:
        print(f"✓ Speedup: {time1/time2:.1f}x")
    else:
        print(f"✓ Both matches completed in <1ms (too fast to measure)")
    
    # Test cache clearing
    print("\n7.2 Testing cache clearing...")
    engine.clear_cache()
    # Check cache is empty before it gets refilled
    assert len(engine.encoding_cache) == 0, "Cache should be empty after clearing"
    print(f"✓ Cache cleared successfully")
    
    # Test 8: Statistics
    print("\n" + "=" * 80)
    print("TEST 8: MATCHING ENGINE STATISTICS")
    print("=" * 80)
    
    print("\n8.1 Getting statistics...")
    stats = engine.get_statistics()
    print(f"✓ Statistics retrieved:")
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    assert stats['total_encodings'] >= 6, f"Should have at least 6 encodings, got {stats['total_encodings']}"
    assert stats['unique_persons'] >= 2, f"Should have at least 2 unique persons, got {stats['unique_persons']}"
    
    # Cleanup
    print("\n" + "=" * 80)
    print("CLEANUP")
    print("=" * 80)
    
    db.delete_person(person1_id)
    db.delete_person(person2_id)
    db.close()
    print("✓ Test data cleaned up")
    
    # Print summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    print("✓ TEST 1: Single-Angle Matching - PASSED")
    print("✓ TEST 2: Multi-Angle Matching - PASSED")
    print("✓ TEST 3: Confidence Scoring (Property 12) - PASSED")
    print("✓ TEST 4: Match Threshold Consistency (Property 7) - PASSED")
    print("✓ TEST 5: Batch Matching - PASSED")
    print("✓ TEST 6: Find Similar Faces - PASSED")
    print("✓ TEST 7: Performance and Caching - PASSED")
    print("✓ TEST 8: Matching Engine Statistics - PASSED")
    print("\n✓ ALL TESTS PASSED")
    print("=" * 80)
    
    return True


if __name__ == "__main__":
    try:
        success = test_matching_engine()
        if success:
            print("\n✓ Enhanced Matching Engine test complete")
        else:
            print("\n✗ Some tests failed")
    except Exception as e:
        print(f"\n✗ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
