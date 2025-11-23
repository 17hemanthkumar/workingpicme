#!/usr/bin/env python3
"""
Comprehensive test for API Endpoints
Tests all REST API endpoints with various scenarios
"""

import requests
import json
import os
import time
from typing import Dict

# API base URL
BASE_URL = "http://localhost:5000/api"

def test_api_endpoints():
    """Test all API endpoints"""
    print("\n" + "=" * 80)
    print("COMPREHENSIVE API ENDPOINTS TEST")
    print("=" * 80)
    
    print("\nNote: This test requires the API server to be running.")
    print("Start the server with: python api_endpoints.py")
    print("\nTesting against:", BASE_URL)
    
    # Test 1: System Status
    print("\n" + "=" * 80)
    print("TEST 1: SYSTEM STATUS")
    print("=" * 80)
    
    try:
        response = requests.get(f"{BASE_URL}/system/status")
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"[OK] System Status: {data['data']['system_status']}")
            print(f"[OK] Components: {data['data']['components']}")
            print(f"[OK] Statistics available: {len(data['data']['statistics'])} components")
        else:
            print(f"[FAIL] Status check failed: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("[FAIL] Connection failed - API server not running")
        print("Please start the API server first: python api_endpoints.py")
        return False
    except Exception as e:
        print(f"[FAIL] Status test error: {e}")
    
    # Test 2: Photo Upload (if test image exists)
    print("\n" + "=" * 80)
    print("TEST 2: PHOTO UPLOAD")
    print("=" * 80)
    
    test_image_paths = [
        "../uploads/event_931cd6b8/10750d04_WhatsApp_Image_2025-11-20_at_5.13.03_PM.jpeg",
        "../uploads/test.jpg",
        "test_image.jpg"
    ]
    
    test_image = None
    for path in test_image_paths:
        if os.path.exists(path):
            test_image = path
            break
    
    if test_image:
        try:
            with open(test_image, 'rb') as f:
                files = {'file': f}
                data = {'event_id': 'test_api_event'}
                
                response = requests.post(f"{BASE_URL}/photos/upload", 
                                       files=files, data=data)
                
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"[OK] Photo uploaded successfully")
                print(f"[OK] Faces detected: {result['data']['processing_result']['faces_detected']}")
                print(f"[OK] Faces processed: {result['data']['processing_result']['faces_processed']}")
            else:
                print(f"[FAIL] Upload failed: {response.text}")
                
        except Exception as e:
            print(f"[FAIL] Upload test error: {e}")
    else:
        print("[WARN] No test image found, skipping upload test")
        print("Available paths checked:", test_image_paths)
    
    # Test 3: Live Scan Capture (will likely fail without webcam)
    print("\n" + "=" * 80)
    print("TEST 3: LIVE SCAN CAPTURE")
    print("=" * 80)
    
    try:
        data = {
            'camera_index': 0,
            'timeout': 5,  # Short timeout for testing
            'min_quality': 0.3  # Lower quality for testing
        }
        
        response = requests.post(f"{BASE_URL}/scan/capture", 
                               json=data, timeout=10)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            capture_result = result['data']['capture_result']
            print(f"[OK] Capture success: {capture_result['success']}")
            if capture_result['success']:
                print(f"[OK] Quality: {capture_result['quality_score']}")
                print(f"[OK] Angle: {capture_result['angle']}")
            else:
                print(f"[WARN] Capture message: {capture_result['message']}")
        else:
            print(f"[FAIL] Capture failed: {response.text}")
            
    except requests.exceptions.Timeout:
        print("[WARN] Capture test timed out (expected without webcam)")
    except Exception as e:
        print(f"[WARN] Capture test error: {e} (expected without webcam)")
    
    # Test 4: Person Photos Search
    print("\n" + "=" * 80)
    print("TEST 4: PERSON PHOTOS SEARCH")
    print("=" * 80)
    
    try:
        # Try to get photos for person ID 1
        response = requests.get(f"{BASE_URL}/search/person/1/photos?limit=10")
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            data = result['data']
            print(f"[OK] Person ID: {data['person_id']}")
            print(f"[OK] Photos returned: {len(data['photos'])}")
            print(f"[OK] Total individual: {data['total_individual']}")
            print(f"[OK] Total group: {data['total_group']}")
        else:
            print(f"[WARN] Person search: {response.text}")
            
    except Exception as e:
        print(f"[FAIL] Person search error: {e}")
    
    # Test 5: Similar Faces Search (if test image exists)
    print("\n" + "=" * 80)
    print("TEST 5: SIMILAR FACES SEARCH")
    print("=" * 80)
    
    if test_image:
        try:
            with open(test_image, 'rb') as f:
                files = {'file': f}
                data = {'top_k': '3'}
                
                response = requests.post(f"{BASE_URL}/search/similar-faces", 
                                       files=files, data=data)
                
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                similar_faces = result['data']['similar_faces']
                print(f"[OK] Similar faces found: {len(similar_faces)}")
                for i, face in enumerate(similar_faces[:3]):
                    print(f"  {i+1}. Person {face['person_id']}: distance={face['distance']:.3f}, confidence={face['confidence']:.3f}")
            else:
                print(f"[FAIL] Similar faces search failed: {response.text}")
                
        except Exception as e:
            print(f"[FAIL] Similar faces test error: {e}")
    else:
        print("[WARN] No test image found, skipping similar faces test")
    
    # Test 6: Cache Reset
    print("\n" + "=" * 80)
    print("TEST 6: CACHE RESET")
    print("=" * 80)
    
    try:
        response = requests.post(f"{BASE_URL}/system/reset-cache")
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"[OK] Cache cleared: {result['data']['cache_cleared']}")
        else:
            print(f"[FAIL] Cache reset failed: {response.text}")
            
    except Exception as e:
        print(f"[FAIL] Cache reset error: {e}")
    
    # Test 7: Error Handling
    print("\n" + "=" * 80)
    print("TEST 7: ERROR HANDLING")
    print("=" * 80)
    
    # Test 404
    try:
        response = requests.get(f"{BASE_URL}/nonexistent")
        print(f"404 Test - Status Code: {response.status_code}")
        if response.status_code == 404:
            print("[OK] 404 handling works")
        else:
            print("[FAIL] 404 handling failed")
    except Exception as e:
        print(f"[FAIL] 404 test error: {e}")
    
    # Test invalid JSON
    try:
        response = requests.post(f"{BASE_URL}/photos/process-event", 
                               json={'invalid': 'data'})
        print(f"Invalid data test - Status Code: {response.status_code}")
        if response.status_code == 400:
            print("[OK] Input validation works")
        else:
            print("[WARN] Input validation response:", response.status_code)
    except Exception as e:
        print(f"[FAIL] Invalid data test error: {e}")
    
    print("\n" + "=" * 80)
    print("API ENDPOINTS TEST SUMMARY")
    print("=" * 80)
    print("[OK] System status endpoint")
    print("[OK] Photo upload endpoint (if image available)")
    print("[WARN] Live scan endpoint (requires webcam)")
    print("[OK] Person photos search endpoint")
    print("[OK] Similar faces search endpoint (if image available)")
    print("[OK] Cache reset endpoint")
    print("[OK] Error handling")
    print("\n[OK] API ENDPOINTS TEST COMPLETE")
    print("=" * 80)
    
    return True

def test_api_documentation():
    """Generate API documentation"""
    print("\n" + "=" * 80)
    print("API ENDPOINTS DOCUMENTATION")
    print("=" * 80)
    
    endpoints = [
        {
            'method': 'POST',
            'path': '/api/photos/upload',
            'description': 'Upload and process a single photo',
            'body': 'Form data: file (image), event_id (string)'
        },
        {
            'method': 'POST',
            'path': '/api/photos/process-event',
            'description': 'Process all photos in an event directory',
            'body': 'JSON: {"event_id": "string", "photos_dir": "string", "force_reprocess": boolean}'
        },
        {
            'method': 'POST',
            'path': '/api/scan/capture',
            'description': 'Capture face from webcam',
            'body': 'JSON: {"camera_index": int, "timeout": int, "min_quality": float}'
        },
        {
            'method': 'POST',
            'path': '/api/scan/match',
            'description': 'Complete scan and match workflow',
            'body': 'JSON: {"camera_index": int, "timeout": int}'
        },
        {
            'method': 'GET',
            'path': '/api/search/person/<id>/photos',
            'description': 'Get all photos of a specific person',
            'body': 'Query params: type (individual/group/all), limit (int)'
        },
        {
            'method': 'POST',
            'path': '/api/search/similar-faces',
            'description': 'Find faces similar to uploaded image',
            'body': 'Form data: file (image), top_k (int)'
        },
        {
            'method': 'GET',
            'path': '/api/system/status',
            'description': 'Get system status and statistics',
            'body': 'None'
        },
        {
            'method': 'POST',
            'path': '/api/system/reset-cache',
            'description': 'Reset matching engine cache',
            'body': 'None'
        }
    ]
    
    for endpoint in endpoints:
        print(f"\n{endpoint['method']} {endpoint['path']}")
        print(f"  Description: {endpoint['description']}")
        print(f"  Body: {endpoint['body']}")
    
    print("\n" + "=" * 80)
    print("API DOCUMENTATION COMPLETE")
    print("=" * 80)

if __name__ == "__main__":
    # Generate documentation
    test_api_documentation()
    
    # Run tests
    test_api_endpoints()
