#!/usr/bin/env python3
"""
API Endpoints for Enhanced Multi-Angle Face Detection System

Flask-based REST API that exposes all system functionality:
- Photo upload and processing
- Live face scanning
- Search and retrieval
- System management

Features:
- RESTful API design
- JSON request/response format
- Error handling and validation
- File upload support
- Real-time processing
"""

from flask import Flask, request, jsonify, send_file
from werkzeug.utils import secure_filename
import os
import uuid
import json
from datetime import datetime
from typing import Dict, List, Optional
import traceback

# Import our components
from photo_processor import PhotoProcessor
from live_face_scanner_enhanced import LiveFaceScanner
from multi_angle_database import MultiAngleFaceDatabase
from enhanced_matching_engine import EnhancedMatchingEngine

# Initialize Flask app
app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['UPLOAD_FOLDER'] = '../uploads'

# Allowed file extensions
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp'}

# Global components (initialized on first use)
photo_processor = None
live_scanner = None
database = None
matching_engine = None

def init_components():
    """Initialize components on first use"""
    global photo_processor, live_scanner, database, matching_engine
    
    if photo_processor is None:
        print("Initializing API components...")
        photo_processor = PhotoProcessor()
        live_scanner = LiveFaceScanner(min_quality=0.5)
        database = MultiAngleFaceDatabase()
        matching_engine = EnhancedMatchingEngine(database)
        print("✓ API components initialized")

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def create_error_response(message: str, status_code: int = 400) -> tuple:
    """Create standardized error response"""
    return jsonify({
        'success': False,
        'error': message,
        'timestamp': datetime.now().isoformat()
    }), status_code

def create_success_response(data: Dict, message: str = "Success") -> tuple:
    """Create standardized success response"""
    response = {
        'success': True,
        'message': message,
        'data': data,
        'timestamp': datetime.now().isoformat()
    }
    return jsonify(response), 200

# ============================================================================
# PHOTO PROCESSING ENDPOINTS
# ============================================================================

@app.route('/api/photos/upload', methods=['POST'])
def upload_photo():
    """
    Upload and process a single photo
    
    Form data:
    - file: Photo file
    - event_id: Event identifier
    
    Returns:
    - Processing results with detected faces and persons
    """
    try:
        init_components()
        
        # Validate request
        if 'file' not in request.files:
            return create_error_response("No file provided")
        
        if 'event_id' not in request.form:
            return create_error_response("No event_id provided")
        
        file = request.files['file']
        event_id = request.form['event_id']
        
        if file.filename == '':
            return create_error_response("No file selected")
        
        if not allowed_file(file.filename):
            return create_error_response("File type not allowed")
        
        # Save uploaded file
        filename = secure_filename(file.filename)
        unique_filename = f"{uuid.uuid4()}_{filename}"
        
        # Create event directory if it doesn't exist
        event_dir = os.path.join(app.config['UPLOAD_FOLDER'], f"event_{event_id}")
        os.makedirs(event_dir, exist_ok=True)
        
        file_path = os.path.join(event_dir, unique_filename)
        file.save(file_path)
        
        # Process photo
        result = photo_processor.process_photo(file_path, event_id)
        
        return create_success_response({
            'photo_path': file_path,
            'processing_result': result
        }, "Photo uploaded and processed successfully")
        
    except Exception as e:
        return create_error_response(f"Upload error: {str(e)}", 500)

@app.route('/api/photos/process-event', methods=['POST'])
def process_event():
    """
    Process all photos in an event directory
    
    JSON body:
    {
        "event_id": "string",
        "photos_dir": "string",
        "force_reprocess": boolean (optional)
    }
    
    Returns:
    - Batch processing results
    """
    try:
        init_components()
        
        data = request.get_json()
        if not data:
            return create_error_response("No JSON data provided")
        
        event_id = data.get('event_id')
        photos_dir = data.get('photos_dir')
        force_reprocess = data.get('force_reprocess', False)
        
        if not event_id:
            return create_error_response("event_id is required")
        
        if not photos_dir:
            return create_error_response("photos_dir is required")
        
        if not os.path.exists(photos_dir):
            return create_error_response(f"Directory not found: {photos_dir}")
        
        # Process event
        result = photo_processor.process_event(event_id, photos_dir, force_reprocess)
        
        return create_success_response({
            'event_processing_result': result
        }, "Event processing completed")
        
    except Exception as e:
        return create_error_response(f"Event processing error: {str(e)}", 500)

# ============================================================================
# LIVE SCANNING ENDPOINTS
# ============================================================================

@app.route('/api/scan/capture', methods=['POST'])
def capture_face():
    """
    Capture face from webcam
    
    JSON body:
    {
        "camera_index": int (optional, default 0),
        "timeout": int (optional, default 30),
        "min_quality": float (optional, default 0.5)
    }
    
    Returns:
    - Captured face info and quality metrics
    """
    try:
        init_components()
        
        data = request.get_json() or {}
        camera_index = data.get('camera_index', 0)
        timeout = data.get('timeout', 30)
        min_quality = data.get('min_quality', 0.5)
        
        # Update scanner quality if different
        if min_quality != live_scanner.min_quality:
            live_scanner.min_quality = min_quality
        
        # Capture face
        result = live_scanner.capture_face(camera_index, timeout)
        
        # Convert face image to base64 if captured
        if result['success'] and result['face_image'] is not None:
            import cv2
            import base64
            
            # Encode image as JPEG
            _, buffer = cv2.imencode('.jpg', result['face_image'])
            img_base64 = base64.b64encode(buffer).decode('utf-8')
            
            result['face_image_base64'] = img_base64
            result['face_image'] = None  # Remove numpy array
        
        return create_success_response({
            'capture_result': result
        }, "Face capture completed")
        
    except Exception as e:
        return create_error_response(f"Capture error: {str(e)}", 500)

@app.route('/api/scan/match', methods=['POST'])
def scan_and_match():
    """
    Complete scan and match workflow
    
    JSON body:
    {
        "camera_index": int (optional, default 0),
        "timeout": int (optional, default 30)
    }
    
    Returns:
    - Match results with person info and photos
    """
    try:
        init_components()
        
        data = request.get_json() or {}
        camera_index = data.get('camera_index', 0)
        timeout = data.get('timeout', 30)
        
        # Scan and match
        result = live_scanner.scan_and_match(camera_index, timeout)
        
        return create_success_response({
            'scan_result': result
        }, "Scan and match completed")
        
    except Exception as e:
        return create_error_response(f"Scan and match error: {str(e)}", 500)

# ============================================================================
# SEARCH AND RETRIEVAL ENDPOINTS
# ============================================================================

@app.route('/api/search/person/<int:person_id>/photos', methods=['GET'])
def get_person_photos(person_id):
    """
    Get all photos of a specific person
    
    URL parameters:
    - person_id: Person identifier
    
    Query parameters:
    - type: 'individual', 'group', or 'all' (default 'all')
    - limit: Maximum number of photos (default 50)
    
    Returns:
    - Person photos with metadata
    """
    try:
        init_components()
        
        photo_type = request.args.get('type', 'all')
        limit = int(request.args.get('limit', 50))
        
        # Get photos
        photos = live_scanner.get_person_photos(person_id)
        
        # Filter by type
        if photo_type == 'individual':
            filtered_photos = photos['individual'][:limit]
        elif photo_type == 'group':
            filtered_photos = photos['group'][:limit]
        else:
            all_photos = photos['individual'] + photos['group']
            all_photos.sort(key=lambda x: x.get('match_confidence', 0), reverse=True)
            filtered_photos = all_photos[:limit]
        
        return create_success_response({
            'person_id': person_id,
            'photo_type': photo_type,
            'photos': filtered_photos,
            'total_individual': len(photos['individual']),
            'total_group': len(photos['group'])
        }, f"Retrieved {len(filtered_photos)} photos")
        
    except Exception as e:
        return create_error_response(f"Photo retrieval error: {str(e)}", 500)

@app.route('/api/search/similar-faces', methods=['POST'])
def find_similar_faces():
    """
    Find faces similar to uploaded image
    
    Form data:
    - file: Face image file
    - top_k: Number of results (optional, default 5)
    
    Returns:
    - List of similar faces with distances and confidence
    """
    try:
        init_components()
        
        if 'file' not in request.files:
            return create_error_response("No file provided")
        
        file = request.files['file']
        top_k = int(request.form.get('top_k', 5))
        
        if file.filename == '':
            return create_error_response("No file selected")
        
        if not allowed_file(file.filename):
            return create_error_response("File type not allowed")
        
        # Save temporary file
        temp_filename = f"temp_{uuid.uuid4()}_{secure_filename(file.filename)}"
        temp_path = os.path.join(app.config['UPLOAD_FOLDER'], temp_filename)
        file.save(temp_path)
        
        try:
            # Load and process image
            import cv2
            image = cv2.imread(temp_path)
            
            if image is None:
                return create_error_response("Failed to load image")
            
            # Detect face
            from enhanced_face_detector import EnhancedFaceDetector
            detector = EnhancedFaceDetector()
            detections = detector.detect_faces(image)
            
            if len(detections) == 0:
                return create_error_response("No face detected in image")
            
            # Extract encoding from first face
            detection = detections[0]
            bbox = detection['bbox']
            x, y, w, h = bbox
            face_img = image[y:y+h, x:x+w]
            
            from deep_feature_extractor import DeepFeatureExtractor
            extractor = DeepFeatureExtractor()
            encoding = extractor.extract_encoding(face_img)
            
            if encoding is None:
                return create_error_response("Failed to extract face encoding")
            
            # Find similar faces
            similar_faces = matching_engine.find_similar_faces(encoding, top_k)
            
            return create_success_response({
                'query_face': {
                    'bbox': bbox,
                    'angle': detection.get('angle', 'frontal'),
                    'confidence': detection['confidence']
                },
                'similar_faces': similar_faces
            }, f"Found {len(similar_faces)} similar faces")
            
        finally:
            # Clean up temp file
            if os.path.exists(temp_path):
                os.remove(temp_path)
        
    except Exception as e:
        return create_error_response(f"Similar faces search error: {str(e)}", 500)

# ============================================================================
# SYSTEM MANAGEMENT ENDPOINTS
# ============================================================================

@app.route('/api/system/status', methods=['GET'])
def get_system_status():
    """
    Get system status and statistics
    
    Returns:
    - System health and component status
    """
    try:
        init_components()
        
        # Get statistics from all components
        db_stats = database.get_statistics()
        matching_stats = matching_engine.get_statistics()
        processing_stats = photo_processor.get_statistics()
        
        return create_success_response({
            'system_status': 'healthy',
            'components': {
                'database': 'connected',
                'photo_processor': 'ready',
                'live_scanner': 'ready',
                'matching_engine': 'ready'
            },
            'statistics': {
                'database': db_stats,
                'matching_engine': matching_stats,
                'photo_processor': processing_stats
            }
        }, "System status retrieved")
        
    except Exception as e:
        return create_error_response(f"System status error: {str(e)}", 500)

@app.route('/api/system/reset-cache', methods=['POST'])
def reset_cache():
    """
    Reset matching engine cache
    
    Returns:
    - Cache reset confirmation
    """
    try:
        init_components()
        
        matching_engine.clear_cache()
        
        return create_success_response({
            'cache_cleared': True
        }, "Cache reset successfully")
        
    except Exception as e:
        return create_error_response(f"Cache reset error: {str(e)}", 500)

# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.errorhandler(404)
def not_found(error):
    return create_error_response("Endpoint not found", 404)

@app.errorhandler(405)
def method_not_allowed(error):
    return create_error_response("Method not allowed", 405)

@app.errorhandler(413)
def request_entity_too_large(error):
    return create_error_response("File too large (max 16MB)", 413)

@app.errorhandler(500)
def internal_server_error(error):
    return create_error_response("Internal server error", 500)

# ============================================================================
# MAIN APPLICATION
# ============================================================================

if __name__ == '__main__':
    print("\n" + "=" * 70)
    print("ENHANCED FACE DETECTION API SERVER")
    print("=" * 70)
    print("\nAvailable endpoints:")
    print("  POST /api/photos/upload")
    print("  POST /api/photos/process-event")
    print("  POST /api/scan/capture")
    print("  POST /api/scan/match")
    print("  GET  /api/search/person/<id>/photos")
    print("  POST /api/search/similar-faces")
    print("  GET  /api/system/status")
    print("  POST /api/system/reset-cache")
    print("\n" + "=" * 70)
    
    # Create upload directory
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # Run development server
    app.run(debug=True, host='0.0.0.0', port=5000)
