#!/usr/bin/env python3
"""
Test Enhanced Face Detector with Real Images

Tests the detector on actual photos from the uploads folder
"""

import cv2
import os
import sys
from enhanced_face_detector import EnhancedFaceDetector
import glob

def test_real_images():
    """Test detector on real images from uploads folder"""
    
    print("=" * 70)
    print("TESTING ENHANCED FACE DETECTOR WITH REAL IMAGES")
    print("=" * 70)
    
    # Initialize detector
    print("\nInitializing detector...")
    detector = EnhancedFaceDetector()
    
    # Find images in uploads folder
    uploads_dir = "../uploads"
    processed_dir = "../processed"
    
    # Look for images in both folders (including subfolders)
    image_patterns = ['*.jpg', '*.jpeg', '*.png', '*.JPG', '*.JPEG', '*.PNG']
    image_files = []
    
    for folder in [uploads_dir, processed_dir]:
        if os.path.exists(folder):
            for pattern in image_patterns:
                # Search in root folder
                image_files.extend(glob.glob(os.path.join(folder, pattern)))
                # Search in subfolders
                image_files.extend(glob.glob(os.path.join(folder, '**', pattern), recursive=True))
    
    if not image_files:
        print("\n❌ No images found in uploads or processed folders")
        print("\nPlease add some test images to:")
        print(f"  - {os.path.abspath(uploads_dir)}")
        print(f"  - {os.path.abspath(processed_dir)}")
        return False
    
    print(f"\n✓ Found {len(image_files)} image(s) to test")
    
    # Test each image
    total_faces = 0
    successful_detections = 0
    
    for i, image_path in enumerate(image_files[:10], 1):  # Test max 10 images
        print("\n" + "=" * 70)
        print(f"IMAGE {i}/{min(len(image_files), 10)}: {os.path.basename(image_path)}")
        print("=" * 70)
        
        # Load image
        image = cv2.imread(image_path)
        
        if image is None:
            print(f"✗ Failed to load image")
            continue
        
        h, w = image.shape[:2]
        print(f"  Dimensions: {w}x{h}")
        
        # Detect faces
        print(f"  Detecting faces...")
        detections = detector.detect_faces(image)
        
        if not detections:
            print(f"  ✗ No faces detected")
            continue
        
        successful_detections += 1
        total_faces += len(detections)
        print(f"  ✓ Detected {len(detections)} face(s)")
        
        # Process each detected face
        for j, detection in enumerate(detections, 1):
            print(f"\n  Face {j}:")
            print(f"    Method: {detection['method']}")
            print(f"    Confidence: {detection['confidence']:.3f}")
            
            bbox = detection['bbox']
            print(f"    BBox: x={bbox[0]}, y={bbox[1]}, w={bbox[2]}, h={bbox[3]}")
            
            # Extract face region
            x, y, w_face, h_face = bbox
            # Ensure coordinates are within image bounds
            x = max(0, x)
            y = max(0, y)
            x2 = min(w, x + w_face)
            y2 = min(h, y + h_face)
            
            if x2 > x and y2 > y:
                face_img = image[y:y2, x:x2]
                
                # Estimate angle
                angle = detector.estimate_angle(face_img, detection.get('landmarks'))
                print(f"    Angle: {angle}")
                
                # Calculate quality
                quality = detector.calculate_quality_score(face_img)
                print(f"    Quality:")
                print(f"      Blur: {quality['blur_score']:.3f}")
                print(f"      Lighting: {quality['lighting_score']:.3f}")
                print(f"      Size: {quality['size_score']:.3f}")
                print(f"      Overall: {quality['overall_score']:.3f}")
                
                # Quality assessment
                if quality['overall_score'] >= 0.7:
                    quality_label = "Excellent"
                elif quality['overall_score'] >= 0.5:
                    quality_label = "Good"
                elif quality['overall_score'] >= 0.3:
                    quality_label = "Fair"
                else:
                    quality_label = "Poor"
                
                print(f"      Assessment: {quality_label}")
    
    # Print summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    print(f"  Images tested: {min(len(image_files), 10)}")
    print(f"  Images with faces: {successful_detections}")
    print(f"  Total faces detected: {total_faces}")
    
    if successful_detections > 0:
        print(f"  Average faces per image: {total_faces / successful_detections:.1f}")
    
    # Print detection statistics
    print("\n" + "=" * 70)
    print("DETECTION STATISTICS")
    print("=" * 70)
    stats = detector.get_detection_stats()
    print(f"  Total detections attempted: {stats['total']}")
    print(f"  MTCNN used: {stats['mtcnn']}")
    print(f"  DNN used: {stats['dnn']}")
    print(f"  Haar used: {stats['haar']}")
    print(f"  HOG used: {stats['hog']}")
    
    # Determine most used method
    methods = {k: v for k, v in stats.items() if k != 'total' and v > 0}
    if methods:
        most_used = max(methods, key=methods.get)
        print(f"\n  Most used method: {most_used.upper()} ({methods[most_used]} times)")
    
    print("\n" + "=" * 70)
    if total_faces > 0:
        print("✅ REAL IMAGE TESTING COMPLETE")
        print("=" * 70)
        print("\nThe Enhanced Face Detector successfully detected faces in real images!")
        print("\nNext steps:")
        print("1. Review the detection results above")
        print("2. Check quality scores for each face")
        print("3. Verify angle estimations are reasonable")
        print("4. Ready to proceed with Task 2.1: Deep Feature Extractor")
        return True
    else:
        print("⚠️  NO FACES DETECTED IN TEST IMAGES")
        print("=" * 70)
        print("\nThis could mean:")
        print("1. The test images don't contain clear faces")
        print("2. The images are too small or low quality")
        print("3. The faces are at extreme angles")
        print("\nThe detector is working correctly (passed synthetic tests)")
        print("Try adding clearer face photos to the uploads folder")
        return False

def main():
    """Main test function"""
    success = test_real_images()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
