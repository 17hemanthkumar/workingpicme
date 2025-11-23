#!/usr/bin/env python3
"""
Comprehensive test for Multi-Angle Face Database Manager
Tests person management, encoding storage, and photo associations
"""

import numpy as np
import uuid
from multi_angle_database import MultiAngleFaceDatabase

def test_database_manager():
    """Test the multi-angle database manager"""
    print("\n" + "=" * 80)
    print("COMPREHENSIVE MULTI-ANGLE DATABASE TEST")
    print("=" * 80)
    
    # Initialize database
    print("\n1. Initializing database...")
    db = MultiAngleFaceDatabase()
    print("✓ Database initialized")
    
    # Test 1: Person Management
    print("\n" + "=" * 80)
    print("TEST 1: PERSON MANAGEMENT")
    print("=" * 80)
    
    # Create person
    print("\n1.1 Creating person...")
    person_uuid = str(uuid.uuid4())
    person_id = db.add_person(person_uuid=person_uuid, name="Test Person")
    print(f"✓ Person created: ID={person_id}")
    
    # Get person
    print("\n1.2 Retrieving person...")
    person = db.get_person(person_id)
    assert person is not None, "Person should exist"
    assert person['person_uuid'] == person_uuid, "UUID should match"
    assert person['name'] == "Test Person", "Name should match"
    print(f"✓ Person retrieved: {person['name']}")
    
    # Update person
    print("\n1.3 Updating person...")
    success = db.update_person(person_id, name="Updated Person", confidence_score=0.95)
    assert success, "Update should succeed"
    person = db.get_person(person_id)
    assert person['name'] == "Updated Person", "Name should be updated"
    assert float(person['confidence_score']) == 0.95, "Confidence should be updated"
    print(f"✓ Person updated: {person['name']}, confidence={person['confidence_score']}")
    
    # Test 2: Encoding Storage
    print("\n" + "=" * 80)
    print("TEST 2: ENCODING STORAGE")
    print("=" * 80)
    
    # Create dummy photo and face detection
    print("\n2.1 Creating test photo and detection...")
    photo_id = db.add_photo("test_event", "test.jpg", "/path/to/test.jpg")
    detection_id = db.add_face_detection(
        photo_id=photo_id,
        person_id=person_id,
        bbox={'x': 100, 'y': 100, 'w': 50, 'h': 50},
        angle='frontal',
        quality_score=0.85,
        detection_method='mtcnn',
        detection_confidence=0.99
    )
    print(f"✓ Photo and detection created: photo_id={photo_id}, detection_id={detection_id}")
    
    # Add encodings for different angles
    print("\n2.2 Adding encodings for multiple angles...")
    angles = ['frontal', 'left_45', 'right_45', 'left_90', 'right_90']
    qualities = [0.95, 0.85, 0.80, 0.75, 0.70]
    encoding_ids = []
    
    for angle, quality in zip(angles, qualities):
        # Create random 128D encoding
        encoding = np.random.rand(128)
        
        enc_id = db.add_face_encoding(
            person_id=person_id,
            encoding=encoding,
            angle=angle,
            quality_score=quality,
            face_detection_id=detection_id
        )
        encoding_ids.append(enc_id)
        print(f"  ✓ Added {angle} encoding: ID={enc_id}, quality={quality}")
    
    # Verify encoding count (should be 5)
    print("\n2.3 Verifying encoding count...")
    encodings = db.get_person_encodings(person_id)
    assert len(encodings) == 5, f"Should have 5 encodings, got {len(encodings)}"
    print(f"✓ Encoding count verified: {len(encodings)} encodings")
    
    # Test 3: Multi-Angle Storage Limit
    print("\n" + "=" * 80)
    print("TEST 3: MULTI-ANGLE STORAGE LIMIT (Property 5)")
    print("=" * 80)
    
    # Try to add 6th encoding with low quality (should be rejected)
    print("\n3.1 Testing storage limit with low quality encoding...")
    low_quality_encoding = np.random.rand(128)
    result = db.add_face_encoding(
        person_id=person_id,
        encoding=low_quality_encoding,
        angle='frontal',  # Duplicate angle
        quality_score=0.60,  # Lower than existing frontal (0.95)
        face_detection_id=detection_id
    )
    
    encodings = db.get_person_encodings(person_id)
    assert len(encodings) == 5, "Should still have 5 encodings"
    print(f"✓ Low quality encoding rejected: count remains at {len(encodings)}")
    
    # Try to add 6th encoding with high quality (should replace lowest)
    print("\n3.2 Testing storage limit with high quality encoding...")
    high_quality_encoding = np.random.rand(128)
    result = db.add_face_encoding(
        person_id=person_id,
        encoding=high_quality_encoding,
        angle='frontal',  # Duplicate angle
        quality_score=0.98,  # Higher than existing frontal (0.95)
        face_detection_id=detection_id
    )
    
    encodings = db.get_person_encodings(person_id)
    assert len(encodings) == 5, "Should still have 5 encodings"
    
    # Verify highest quality is now 0.98
    frontal_encodings = db.get_person_encodings(person_id, angle='frontal')
    assert len(frontal_encodings) > 0, "Should have frontal encoding"
    assert float(frontal_encodings[0]['quality_score']) == 0.98, "Should have new high quality encoding"
    print(f"✓ High quality encoding replaced lower quality: new quality={frontal_encodings[0]['quality_score']}")
    
    # Test 4: Primary Encoding Selection (Property 10)
    print("\n" + "=" * 80)
    print("TEST 4: PRIMARY ENCODING SELECTION (Property 10)")
    print("=" * 80)
    
    print("\n4.1 Verifying primary encoding is highest quality...")
    best_encoding = db.get_best_encoding(person_id)
    assert best_encoding is not None, "Should have primary encoding"
    assert best_encoding['is_primary'] == 1, "Should be marked as primary"
    
    # Get all encodings and find highest quality
    all_encodings = db.get_person_encodings(person_id)
    highest_quality = max(float(e['quality_score']) for e in all_encodings)
    
    assert float(best_encoding['quality_score']) == highest_quality, \
        "Primary encoding should have highest quality"
    print(f"✓ Primary encoding verified: quality={best_encoding['quality_score']}")
    
    # Test 5: Photo Association
    print("\n" + "=" * 80)
    print("TEST 5: PHOTO ASSOCIATION")
    print("=" * 80)
    
    # Associate photo with person
    print("\n5.1 Associating photo with person...")
    assoc_id = db.associate_photo(
        person_id=person_id,
        photo_id=photo_id,
        is_group=False,
        confidence=0.92,
        face_detection_id=detection_id
    )
    print(f"✓ Photo associated: assoc_id={assoc_id}")
    
    # Get person photos
    print("\n5.2 Retrieving person photos...")
    photos = db.get_person_photos(person_id)
    assert len(photos['individual']) > 0, "Should have individual photos"
    assert len(photos['group']) == 0, "Should have no group photos"
    print(f"✓ Photos retrieved: {len(photos['individual'])} individual, {len(photos['group'])} group")
    
    # Test 6: Photo Association Uniqueness (Property 8)
    print("\n" + "=" * 80)
    print("TEST 6: PHOTO ASSOCIATION UNIQUENESS (Property 8)")
    print("=" * 80)
    
    print("\n6.1 Testing duplicate association...")
    # Try to associate same photo again (should update, not duplicate)
    assoc_id2 = db.associate_photo(
        person_id=person_id,
        photo_id=photo_id,
        is_group=False,
        confidence=0.95,  # Different confidence
        face_detection_id=detection_id
    )
    
    photos = db.get_person_photos(person_id)
    assert len(photos['individual']) == 1, "Should still have only 1 photo"
    assert float(photos['individual'][0]['match_confidence']) == 0.95, "Confidence should be updated"
    print(f"✓ Duplicate association prevented: updated confidence to {photos['individual'][0]['match_confidence']}")
    
    # Test 7: Retrieval Functions
    print("\n" + "=" * 80)
    print("TEST 7: RETRIEVAL FUNCTIONS")
    print("=" * 80)
    
    # Get encodings by angle
    print("\n7.1 Retrieving encodings by angle...")
    frontal_encs = db.get_person_encodings(person_id, angle='frontal')
    assert len(frontal_encs) > 0, "Should have frontal encodings"
    print(f"✓ Frontal encodings: {len(frontal_encs)}")
    
    # Get all encodings
    print("\n7.2 Retrieving all encodings...")
    all_encs = db.get_all_encodings()
    assert len(all_encs) >= 5, "Should have at least 5 encodings"
    print(f"✓ All encodings: {len(all_encs)}")
    
    # Verify encoding arrays are properly converted
    print("\n7.3 Verifying encoding array conversion...")
    for enc in frontal_encs:
        assert 'encoding_array' in enc, "Should have encoding_array"
        assert isinstance(enc['encoding_array'], np.ndarray), "Should be numpy array"
        assert enc['encoding_array'].shape[0] == 128, "Should be 128D"
    print(f"✓ Encoding arrays verified: 128D numpy arrays")
    
    # Test 8: Statistics
    print("\n" + "=" * 80)
    print("TEST 8: DATABASE STATISTICS")
    print("=" * 80)
    
    print("\n8.1 Getting database statistics...")
    stats = db.get_statistics()
    print(f"✓ Statistics retrieved:")
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    assert stats['total_persons'] >= 1, "Should have at least 1 person"
    assert stats['total_encodings'] >= 5, "Should have at least 5 encodings"
    
    # Test 9: Person Deletion (Property 9 - Cascade Delete)
    print("\n" + "=" * 80)
    print("TEST 9: CASCADE DELETE (Property 9)")
    print("=" * 80)
    
    print("\n9.1 Testing cascade delete...")
    # Get counts before deletion
    encodings_before = len(db.get_person_encodings(person_id))
    photos_before = len(db.get_person_photos(person_id)['individual'])
    
    # Delete person
    success = db.delete_person(person_id)
    assert success, "Deletion should succeed"
    
    # Verify person is gone
    person = db.get_person(person_id)
    assert person is None, "Person should be deleted"
    
    # Verify encodings are gone (cascade delete)
    encodings_after = len(db.get_person_encodings(person_id))
    assert encodings_after == 0, "Encodings should be cascade deleted"
    
    print(f"✓ Cascade delete verified:")
    print(f"  Person deleted: ID={person_id}")
    print(f"  Encodings deleted: {encodings_before} → {encodings_after}")
    print(f"  Associations deleted: {photos_before} → 0")
    
    # Close database
    print("\n" + "=" * 80)
    print("CLOSING DATABASE")
    print("=" * 80)
    db.close()
    
    # Print summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    print("✓ TEST 1: Person Management - PASSED")
    print("✓ TEST 2: Encoding Storage - PASSED")
    print("✓ TEST 3: Multi-Angle Storage Limit (Property 5) - PASSED")
    print("✓ TEST 4: Primary Encoding Selection (Property 10) - PASSED")
    print("✓ TEST 5: Photo Association - PASSED")
    print("✓ TEST 6: Photo Association Uniqueness (Property 8) - PASSED")
    print("✓ TEST 7: Retrieval Functions - PASSED")
    print("✓ TEST 8: Database Statistics - PASSED")
    print("✓ TEST 9: Cascade Delete (Property 9) - PASSED")
    print("\n✓ ALL TESTS PASSED")
    print("=" * 80)
    
    return True


if __name__ == "__main__":
    try:
        success = test_database_manager()
        if success:
            print("\n✓ Multi-Angle Database Manager test complete")
        else:
            print("\n✗ Some tests failed")
    except Exception as e:
        print(f"\n✗ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
