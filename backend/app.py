# PERFORMANCE OPTIMIZED VERSION OF APP.PY
# This file includes compression, caching, and optimized database handling

from flask import Flask, request, jsonify, send_from_directory, render_template, session, redirect, url_for, make_response
from flask_compress import Compress  # NEW: Gzip compression
from flask_caching import Cache  # NEW: Response caching
from functools import wraps
import os
import json
import uuid
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

# Lazy imports - only load heavy libraries when needed
_face_recognition = None
_cv2 = None
_np = None
_qrcode = None
_mysql_connector = None
_shutil = None
_threading = None
_traceback = None
_face_model = None

def get_face_recognition():
    global _face_recognition
    if _face_recognition is None:
        import face_recognition
        _face_recognition = face_recognition
    return _face_recognition

def get_cv2():
    global _cv2
    if _cv2 is None:
        import cv2
        _cv2 = cv2
    return _cv2

def get_numpy():
    global _np
    if _np is None:
        import numpy as np
        _np = np
    return _np

def get_qrcode():
    global _qrcode
    if _qrcode is None:
        import qrcode
        _qrcode = qrcode
    return _qrcode

def get_mysql_connector():
    global _mysql_connector
    if _mysql_connector is None:
        import mysql.connector
        _mysql_connector = mysql.connector
    return _mysql_connector

def get_shutil():
    global _shutil
    if _shutil is None:
        import shutil
        _shutil = shutil
    return _shutil

def get_threading():
    global _threading
    if _threading is None:
        import threading
        _threading = threading
    return _threading

def get_traceback():
    global _traceback
    if _traceback is None:
        import traceback
        _traceback = traceback
    return _traceback

def get_face_model():
    global _face_model
    if _face_model is None:
        from face_model import FaceRecognitionModel
        _face_model = FaceRecognitionModel(data_file=KNOWN_FACES_DATA_PATH)
    return _face_model

# --- CONFIGURATION ---
app = Flask(__name__, static_folder='../frontend/static', template_folder='../frontend/pages')
app.secret_key = 'your_super_secret_key_here'

# PERFORMANCE: Enable Gzip compression with optimal settings
app.config['COMPRESS_MIMETYPES'] = [
    'text/html', 'text/css', 'text/xml', 'application/json',
    'application/javascript', 'text/javascript'
]
app.config['COMPRESS_LEVEL'] = 6  # Balance between speed and compression
app.config['COMPRESS_MIN_SIZE'] = 500  # Only compress files > 500 bytes
Compress(app)

# PERFORMANCE: Configure caching with optimized settings
cache = Cache(app, config={
    'CACHE_TYPE': 'simple',
    'CACHE_DEFAULT_TIMEOUT': 300,
    'CACHE_THRESHOLD': 100  # Max 100 cached items
})

DB_CONFIG = {'host': 'localhost', 'user': 'root', 'password': '', 'database': 'picme_db'}
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, '..', 'uploads')
PROCESSED_FOLDER = os.path.join(BASE_DIR, '..', 'processed')
EVENTS_DATA_PATH = os.path.join(BASE_DIR, '..', 'events_data.json')
KNOWN_FACES_DATA_PATH = os.path.join(BASE_DIR, 'known_faces.dat')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['PROCESSED_FOLDER'] = PROCESSED_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)

# PERFORMANCE: In-memory cache for events data
_events_cache = None
_events_cache_time = 0
EVENTS_CACHE_TTL = 60  # seconds

def get_events_cached():
    """Get events from cache or file"""
    global _events_cache, _events_cache_time
    import time
    current_time = time.time()
    
    if _events_cache is None or (current_time - _events_cache_time) > EVENTS_CACHE_TTL:
        if os.path.exists(EVENTS_DATA_PATH):
            with open(EVENTS_DATA_PATH, 'r') as f:
                _events_cache = json.load(f)
        else:
            _events_cache = []
        _events_cache_time = current_time
    
    return _events_cache

def invalidate_events_cache():
    """Invalidate events cache when data changes"""
    global _events_cache
    _events_cache = None

# PERFORMANCE: Add cache headers for static assets
@app.after_request
def add_cache_headers(response):
    """Add appropriate cache headers based on content type"""
    # Cache static assets for 1 year
    if request.path.startswith('/static/'):
        response.cache_control.max_age = 31536000  # 1 year
        response.cache_control.public = True
        response.headers['Expires'] = (datetime.now() + timedelta(days=365)).strftime('%a, %d %b %Y %H:%M:%S GMT')
        # Add ETag for better caching
        if response.status_code == 200:
            response.add_etag()
    
    # Cache photos for 1 week
    elif request.path.startswith('/photos/'):
        response.cache_control.max_age = 604800  # 1 week
        response.cache_control.public = True
    
    # Cache API responses for 5 minutes
    elif request.path.startswith('/api/events') and request.method == 'GET':
        response.cache_control.max_age = 300  # 5 minutes
        response.cache_control.public = True
    
    # Don't cache dynamic pages and POST requests
    elif request.method == 'POST' or 'login' in request.path or 'logout' in request.path:
        response.cache_control.no_cache = True
        response.cache_control.no_store = True
        response.cache_control.must_revalidate = True
    
    return response

# PERFORMANCE: Request timing middleware
import time

@app.before_request
def before_request():
    """Track request start time"""
    request.start_time = time.time()

@app.after_request
def after_request(response):
    """Log slow requests"""
    if hasattr(request, 'start_time'):
        elapsed = time.time() - request.start_time
        # Only log very slow requests (>2 seconds) to reduce noise
        if elapsed > 2.0:
            print(f"⚠️  SLOW REQUEST: {request.method} {request.path} took {elapsed:.2f}s")
    return response

# --- HELPER FUNCTIONS ---
def get_db_connection():
    mysql_connector = get_mysql_connector()
    try: 
        return mysql_connector.connect(**DB_CONFIG)
    except mysql_connector.Error as err: 
        print(f"DB Error: {err}")
        return None

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'): 
            return redirect(url_for('serve_login_page'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    """Decorator to protect admin-only routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('admin_logged_in'):
            return redirect(url_for('serve_admin_login_page'))
        return f(*args, **kwargs)
    return decorated_function

def process_images(event_id):
    """Process images for an event - optimized to run in background without blocking"""
    # Lazy load heavy dependencies
    face_recognition = get_face_recognition()
    shutil = get_shutil()
    traceback = get_traceback()
    model = get_face_model()
    
    try:
        input_dir = os.path.join(app.config['UPLOAD_FOLDER'], event_id)
        output_dir = os.path.join(app.config['PROCESSED_FOLDER'], event_id)
        
        # Check if directory exists and has images
        if not os.path.exists(input_dir):
            return
            
        os.makedirs(output_dir, exist_ok=True)

        print(f"--- [PROCESS] Starting for event: {event_id} ---")
        
        # Get list of images to process
        images_to_process = [
            f for f in os.listdir(input_dir) 
            if f.lower().endswith(('.png', '.jpg', '.jpeg')) and not f.endswith('_qr.png')
        ]
        
        # PERFORMANCE: Skip if already processed
        if len(images_to_process) == 0:
            print(f"--- [PROCESS] No images to process for event: {event_id} ---")
            return
        
        # Process images with minimal logging
        for filename in images_to_process:
            image_path = os.path.join(input_dir, filename)
            try:
                image = face_recognition.load_image_file(image_path)
                face_encodings = face_recognition.face_encodings(image)
                
                # Only log if faces found
                if len(face_encodings) > 0:
                    person_ids_in_image = {model.learn_face(encoding) for encoding in face_encodings}

                    for pid in person_ids_in_image:
                        person_dir = os.path.join(output_dir, pid)
                        os.makedirs(os.path.join(person_dir, "individual"), exist_ok=True)
                        os.makedirs(os.path.join(person_dir, "group"), exist_ok=True)

                        # PRIVACY FIX: Classify photos correctly
                        if len(face_encodings) == 1:
                            # Individual photo - ONLY in individual folder (private)
                            shutil.copy(image_path, os.path.join(person_dir, "individual", filename))
                        else:
                            # Group photo - ONLY in group folder (public)
                            shutil.copy(image_path, os.path.join(person_dir, "group", f"watermarked_{filename}"))
            except Exception as e:
                # Silent error handling - don't spam console
                pass
                
        model.save_model()
        print(f"--- [PROCESS] Completed event: {event_id} ({len(images_to_process)} images) ---")
    except Exception as e:
        # Silent error handling
        pass

def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# --- ROUTES FOR SERVING PAGES ---
@app.route('/')
def serve_index(): 
    return render_template('index.html')

@app.route('/login')
def serve_login_page(): 
    return render_template('login.html')

@app.route('/signup')
def serve_signup_page(): 
    return render_template('signup.html')

@app.route('/admin/login')
def serve_admin_login_page():
    return render_template('admin_login.html')

@app.route('/admin/signup')
def serve_admin_signup_page():
    return render_template('admin_signup.html')

@app.route('/homepage')
@login_required
def serve_homepage(): 
    return render_template('homepage.html')

@app.route('/event_discovery')
@login_required
def serve_event_discovery(): 
    return render_template('event_discovery.html')

@app.route('/event_detail')
@login_required
def serve_event_detail(): 
    return render_template('event_detail.html')

@app.route('/biometric_authentication_portal')
@login_required
def serve_biometric_authentication_portal(): 
    return render_template('biometric_authentication_portal.html')

@app.route('/personal_photo_gallery')
@login_required
def serve_personal_photo_gallery(): 
    return render_template('personal_photo_gallery.html')

@app.route('/my_downloads')
@login_required
def serve_my_downloads():
    """Serve the My Downloads page for users to view their downloaded photos"""
    return render_template('my_downloads.html')

@app.route('/event_organizer')
@admin_required
def serve_event_organizer(): 
    return render_template('event_organizer.html')

# --- AUTHENTICATION API ROUTES ---
@app.route('/register', methods=['POST'])
def register_user():
    data = request.get_json()
    full_name, email, password = data.get('fullName'), data.get('email'), data.get('password')
    if not all([full_name, email, password]): 
        return jsonify({"success": False, "error": "All fields are required"}), 400
    
    hashed_password = generate_password_hash(password)
    conn = get_db_connection()
    if conn is None: 
        return jsonify({"success": False, "error": "Database connection failed"}), 500
    
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
        if cursor.fetchone(): 
            return jsonify({"success": False, "error": "Email already registered"}), 409
        
        cursor.execute("INSERT INTO users (full_name, email, password) VALUES (%s, %s, %s)", 
                      (full_name, email, hashed_password))
        conn.commit()
        return jsonify({"success": True, "message": "Registration successful!"}), 201
    except Exception as err:
        conn.rollback()
        return jsonify({"success": False, "error": "Registration failed"}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/login', methods=['POST'])
def login_user():
    data = request.get_json()
    email, password = data.get('email'), data.get('password')
    if not all([email, password]): 
        return jsonify({"success": False, "error": "Email and password are required"}), 400
    
    conn = get_db_connection()
    if conn is None: 
        return jsonify({"success": False, "error": "Database connection failed"}), 500
    
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT id, email, password FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()
        if user and check_password_hash(user['password'], password):
            session['logged_in'] = True
            session['user_id'] = user['id']
            session['user_email'] = user['email']
            return jsonify({"success": True, "message": "Login successful!"}), 200
        else:
            return jsonify({"success": False, "error": "Invalid email or password"}), 401
    except Exception as err:
        print(f"Error during login: {err}")
        return jsonify({"success": False, "error": "An internal server error occurred during login."}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/logout')
def logout_user():
    session.clear()
    return redirect(url_for('serve_index'))

# --- ADMIN AUTHENTICATION API ROUTES ---
@app.route('/admin/register', methods=['POST'])
def register_admin():
    """Register a new admin (event organizer)"""
    data = request.get_json()
    organization_name = data.get('organizationName')
    email = data.get('email')
    password = data.get('password')
    
    if not all([organization_name, email, password]):
        return jsonify({"success": False, "error": "All fields are required"}), 400
    
    # Validate password length
    if len(password) < 6:
        return jsonify({"success": False, "error": "Password must be at least 6 characters"}), 400
    
    hashed_password = generate_password_hash(password)
    conn = get_db_connection()
    if conn is None:
        return jsonify({"success": False, "error": "Database connection failed"}), 500
    
    cursor = conn.cursor()
    try:
        # Check if email already exists
        cursor.execute("SELECT admin_id FROM admin WHERE email = %s", (email,))
        if cursor.fetchone():
            return jsonify({"success": False, "error": "Email already registered"}), 409
        
        # Insert new admin
        cursor.execute(
            "INSERT INTO admin (organization_name, email, password) VALUES (%s, %s, %s)",
            (organization_name, email, hashed_password)
        )
        conn.commit()
        return jsonify({"success": True, "message": "Admin registration successful!"}), 201
    except Exception as err:
        conn.rollback()
        print(f"Error during admin registration: {err}")
        return jsonify({"success": False, "error": "Registration failed"}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/admin/login', methods=['POST'])
def login_admin():
    """Authenticate admin and create admin session"""
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    
    if not all([email, password]):
        return jsonify({"success": False, "error": "Email and password are required"}), 400
    
    conn = get_db_connection()
    if conn is None:
        return jsonify({"success": False, "error": "Database connection failed"}), 500
    
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            "SELECT admin_id, organization_name, email, password FROM admin WHERE email = %s",
            (email,)
        )
        admin = cursor.fetchone()
        
        if admin and check_password_hash(admin['password'], password):
            # Create admin session
            session['admin_logged_in'] = True
            session['admin_id'] = admin['admin_id']
            session['admin_email'] = admin['email']
            session['organization_name'] = admin['organization_name']
            session.modified = True
            
            return jsonify({
                "success": True,
                "message": "Login successful!",
                "redirect": "/event_organizer"
            }), 200
        else:
            return jsonify({"success": False, "error": "Invalid email or password"}), 401
    except Exception as err:
        print(f"Error during admin login: {err}")
        return jsonify({"success": False, "error": "An internal server error occurred during login."}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/admin/logout')
def logout_admin():
    """Clear admin session and redirect to admin login"""
    # Clear only admin session keys
    session.pop('admin_logged_in', None)
    session.pop('admin_id', None)
    session.pop('admin_email', None)
    session.pop('organization_name', None)
    return redirect(url_for('serve_admin_login_page'))

# --- CORE API & FILE SERVING ROUTES ---

@app.route('/api/events/<event_id>', methods=['GET', 'PUT'])
def handle_single_event(event_id):
    """Handle GET and PUT requests for single event"""
    if request.method == 'GET':
        try:
            events_data = get_events_cached()  # PERFORMANCE: Use cached data
            event = next((e for e in events_data if e['id'] == event_id), None)

            if event:
                return jsonify({"success": True, "event": event})
            else:
                return jsonify({"success": False, "error": "Event not found"}), 404
                
        except Exception as e:
            print(f"Error getting single event: {e}")
            return jsonify({"success": False, "error": "Internal server error"}), 500
    
    elif request.method == 'PUT':
        # Check admin authentication
        if 'admin_id' not in session:
            return jsonify({"success": False, "error": "Unauthorized"}), 401
        
        try:
            data = request.get_json()
            
            # Validate required fields
            required_fields = ['name', 'location', 'date', 'category', 'organization_name']
            for field in required_fields:
                if field not in data or not str(data[field]).strip():
                    return jsonify({
                        "success": False,
                        "error": f"{field.replace('_', ' ').title()} is required"
                    }), 400
            
            # Validate field lengths
            if len(data['name']) > 200:
                return jsonify({"success": False, "error": "Event name too long (max 200 characters)"}), 400
            if len(data['location']) > 200:
                return jsonify({"success": False, "error": "Location too long (max 200 characters)"}), 400
            if len(data['organization_name']) > 200:
                return jsonify({"success": False, "error": "Organization name too long (max 200 characters)"}), 400
            
            # Load events data
            events_data = get_events_cached().copy()
            
            # Find the event
            event = None
            event_index = None
            for idx, evt in enumerate(events_data):
                if evt['id'] == event_id:
                    event = evt
                    event_index = idx
                    break
            
            if not event:
                return jsonify({"success": False, "error": "Event not found"}), 404
            
            # Check authorization - only event creator can edit
            admin_id = session.get('admin_id')
            if event.get('created_by') != admin_id:
                return jsonify({
                    "success": False,
                    "error": "Unauthorized: You can only edit your own events"
                }), 403
            
            # Update event fields (preserve all other fields)
            event['name'] = data['name'].strip()
            event['location'] = data['location'].strip()
            event['date'] = data['date']
            event['category'] = data['category'].strip()
            event['organization_name'] = data['organization_name'].strip()
            
            # Save updated events data atomically
            events_data[event_index] = event
            
            # Write to temporary file first
            import tempfile
            temp_fd, temp_path = tempfile.mkstemp(suffix='.json', dir=os.path.dirname(EVENTS_DATA_PATH))
            try:
                with os.fdopen(temp_fd, 'w') as f:
                    json.dump(events_data, f, indent=2)
                
                # Create backup of current file
                if os.path.exists(EVENTS_DATA_PATH):
                    backup_path = EVENTS_DATA_PATH + '.backup'
                    shutil_module = get_shutil()
                    shutil_module.copy(EVENTS_DATA_PATH, backup_path)
                
                # Atomic rename
                shutil_module.move(temp_path, EVENTS_DATA_PATH)
            except Exception as e:
                # Clean up temp file if it exists
                if os.path.exists(temp_path):
                    os.remove(temp_path)
                raise e
            
            # Invalidate cache
            invalidate_events_cache()
            
            print(f"Event {event_id} updated successfully: {event['name']}")
            
            return jsonify({
                "success": True,
                "message": "Event updated successfully",
                "event": event
            }), 200
            
        except Exception as e:
            print(f"Error updating event: {e}")
            import traceback
            traceback.print_exc()
            return jsonify({
                "success": False,
                "error": "Internal server error"
            }), 500

@app.route('/recognize', methods=['POST'])
@login_required
def recognize_face():
    # Lazy load heavy dependencies
    import base64
    face_recognition = get_face_recognition()
    cv2 = get_cv2()
    np = get_numpy()
    model = get_face_model()
    
    try:
        data = request.get_json()
        image_data = data.get('image')
        event_id = data.get('event_id', 'default_event')
        if not image_data: 
            return jsonify({"success": False, "error": "No image provided"}), 400
        
        img_bytes = base64.b64decode(image_data)
        np_arr = np.frombuffer(img_bytes, np.uint8)
        img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
        rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        face_locations = face_recognition.face_locations(rgb_img)
        if not face_locations: 
            return jsonify({"success": False, "error": "No face detected in scan."}), 400
        
        scanned_encoding = face_recognition.face_encodings(rgb_img, face_locations)[0]
        person_id = model.recognize_face(scanned_encoding)
        
        if person_id:
            person_dir = os.path.join(app.config['PROCESSED_FOLDER'], event_id, person_id)
            if not os.path.exists(person_dir): 
                return jsonify({"success": False, "error": "Match found, but no photos in this event."}), 404
            
            # PRIVACY: Store person_id in session for this event
            session[f'person_id_{event_id}'] = person_id
            session.modified = True
            
            individual_dir = os.path.join(person_dir, "individual")
            group_dir = os.path.join(person_dir, "group")
            individual_photos = [f for f in os.listdir(individual_dir)] if os.path.exists(individual_dir) else []
            group_photos = [f for f in os.listdir(group_dir) if f.startswith('watermarked_')] if os.path.exists(group_dir) else []
            
            return jsonify({
                "success": True, 
                "person_id": person_id, 
                "individual_photos": individual_photos, 
                "group_photos": group_photos, 
                "event_id": event_id,
                "message": f"Face recognized! Found {len(individual_photos)} individual photos and {len(group_photos)} group photos."
            })
        else:
            return jsonify({"success": False, "error": "No confident match found."}), 404

    except Exception as e:
        print(f"RECOGNIZE ERROR: {e}")
        return jsonify({"success": False, "error": "An internal error occurred."}), 500

# --- EVENT ORGANIZER API ROUTES ---
@app.route('/api/create_event', methods=['POST'])
@admin_required
def create_event():
    try:
        # Check if request has form data (with optional thumbnail) or JSON
        if request.content_type and 'multipart/form-data' in request.content_type:
            # Multipart form data (with optional thumbnail)
            event_name = request.form.get('eventName')
            event_location = request.form.get('eventLocation')
            event_date = request.form.get('eventDate')
            event_category = request.form.get('eventCategory', 'General')
            thumbnail_file = request.files.get('thumbnail')
        else:
            # JSON data (backward compatibility)
            data = request.get_json()
            event_name = data.get('eventName')
            event_location = data.get('eventLocation')
            event_date = data.get('eventDate')
            event_category = data.get('eventCategory', 'General')
            thumbnail_file = None
        
        if not all([event_name, event_location, event_date]):
            return jsonify({"success": False, "error": "All fields are required"}), 400
        
        event_id = f"event_{uuid.uuid4().hex[:8]}"
        event_upload_dir = os.path.join(app.config['UPLOAD_FOLDER'], event_id)
        os.makedirs(event_upload_dir, exist_ok=True)
        
        # Lazy load QR code library
        qrcode = get_qrcode()
        qr_data = f"http://127.0.0.1:5000/event_detail?event_id={event_id}"
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(qr_data)
        qr.make(fit=True)
        qr_img = qr.make_image(fill_color="black", back_color="white")
        qr_path = os.path.join(event_upload_dir, f"{event_id}_qr.png")
        qr_img.save(qr_path)
        
        # Handle optional thumbnail upload
        thumbnail_url = '/static/images/default_event_thumbnail.jpg'  # Default
        
        if thumbnail_file and thumbnail_file.filename != '':
            # Validate thumbnail
            if allowed_file(thumbnail_file.filename):
                # Check file size
                thumbnail_file.seek(0, os.SEEK_END)
                file_size = thumbnail_file.tell()
                thumbnail_file.seek(0)
                
                MAX_SIZE = 5 * 1024 * 1024  # 5MB
                if file_size <= MAX_SIZE:
                    # Save thumbnail
                    file_ext = secure_filename(thumbnail_file.filename).rsplit('.', 1)[1].lower()
                    thumbnail_filename = f"{event_id}_thumb_{uuid.uuid4().hex[:8]}.{file_ext}"
                    
                    thumbnails_dir = os.path.join(app.config['UPLOAD_FOLDER'], 'thumbnails')
                    os.makedirs(thumbnails_dir, exist_ok=True)
                    
                    thumbnail_path = os.path.join(thumbnails_dir, thumbnail_filename)
                    thumbnail_file.save(thumbnail_path)
                    
                    thumbnail_url = f"/uploads/thumbnails/{thumbnail_filename}"
                    print(f"Thumbnail saved: {thumbnail_url}")
                else:
                    print(f"Thumbnail too large ({file_size} bytes), using default")
            else:
                print(f"Invalid thumbnail file type, using default")
        
        events_data = get_events_cached().copy()  # PERFORMANCE: Use cached data
        
        # Get organization name from admin session
        organization_name = session.get('organization_name', 'Unknown Organizer')
        
        new_event = {
            "id": event_id, "name": event_name, "location": event_location,
            "date": event_date, "category": event_category, "image": "/static/images/default_event.jpg",
            "cover_thumbnail": thumbnail_url,  # NEW: Add thumbnail
            "photos_count": 0, "qr_code": f"/api/qr_code/{event_id}",
            "created_by": session.get('admin_id'), 
            "organization_name": organization_name,
            "created_at": datetime.now().isoformat()
        }
        events_data.append(new_event)
        
        with open(EVENTS_DATA_PATH, 'w') as f:
            json.dump(events_data, f, indent=2)
        
        invalidate_events_cache()  # PERFORMANCE: Invalidate cache
        cache.delete('view//api/events')  # Clear API cache

        return jsonify({
            "success": True, 
            "event_id": event_id, 
            "message": "Event created successfully!",
            "thumbnail_url": thumbnail_url
        }), 201
        
    except Exception as e:
        print(f"Error creating event: {e}")
        return jsonify({"success": False, "error": "Failed to create event"}), 500

@app.route('/api/update_event/<event_id>', methods=['POST'])
@admin_required
def update_event_details(event_id):
    """Update event details"""
    try:
        data = request.get_json()
        print(f"Received update request for event {event_id}: {data}")
        
        # Validate required fields
        required_fields = ['name', 'location', 'date', 'category', 'organization_name']
        for field in required_fields:
            if field not in data or not str(data[field]).strip():
                return jsonify({
                    "success": False,
                    "error": f"{field.replace('_', ' ').title()} is required"
                }), 400
        
        # Validate field lengths
        if len(data['name']) > 200:
            return jsonify({"success": False, "error": "Event name too long (max 200 characters)"}), 400
        if len(data['location']) > 200:
            return jsonify({"success": False, "error": "Location too long (max 200 characters)"}), 400
        if len(data['organization_name']) > 200:
            return jsonify({"success": False, "error": "Organization name too long (max 200 characters)"}), 400
        
        # Load events data
        if os.path.exists(EVENTS_DATA_PATH):
            with open(EVENTS_DATA_PATH, 'r') as f:
                events_data = json.load(f)
        else:
            return jsonify({"success": False, "error": "Events data not found"}), 404
        
        # Find the event
        event = None
        event_index = None
        for idx, evt in enumerate(events_data):
            if evt['id'] == event_id:
                event = evt
                event_index = idx
                break
        
        if not event:
            return jsonify({"success": False, "error": "Event not found"}), 404
        
        # Check authorization - only event creator can edit
        # Allow editing if: event has no creator (null) OR current admin created it
        admin_id = session.get('admin_id')
        event_creator = event.get('created_by')
        
        if event_creator is not None and event_creator != admin_id:
            return jsonify({
                "success": False,
                "error": "Unauthorized: You can only edit your own events"
            }), 403
        
        # Update event fields (preserve all other fields)
        event['name'] = data['name'].strip()
        event['location'] = data['location'].strip()
        event['date'] = data['date']
        event['category'] = data['category'].strip()
        event['organization_name'] = data['organization_name'].strip()
        
        # Save updated events data
        events_data[event_index] = event
        
        with open(EVENTS_DATA_PATH, 'w') as f:
            json.dump(events_data, f, indent=2)
        
        # Invalidate cache
        invalidate_events_cache()
        cache.delete('view//api/events')
        
        print(f"Event {event_id} updated successfully: {event['name']}")
        
        return jsonify({
            "success": True,
            "message": "Event updated successfully",
            "event": event
        }), 200
        
    except Exception as e:
        print(f"Error updating event: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "success": False,
            "error": "Internal server error"
        }), 500

@app.route('/api/qr_code/<event_id>', methods=['GET'])
def get_qr_code(event_id):
    qr_path = os.path.join(app.config['UPLOAD_FOLDER'], event_id, f"{event_id}_qr.png")
    if os.path.exists(qr_path):
        return send_from_directory(os.path.join(app.config['UPLOAD_FOLDER'], event_id), f"{event_id}_qr.png")
    return "QR Code not found", 404

@app.route('/api/upload_photos/<event_id>', methods=['POST'])
@admin_required
def upload_event_photos(event_id):
    try:
        if 'photos' not in request.files:
            return jsonify({"success": False, "error": "No photos uploaded"}), 400
        
        files = request.files.getlist('photos')
        if not files or files[0].filename == '':
            return jsonify({"success": False, "error": "No photos selected"}), 400
        
        event_dir = os.path.join(app.config['UPLOAD_FOLDER'], event_id)
        if not os.path.exists(event_dir):
            return jsonify({"success": False, "error": "Event not found"}), 404
        
        uploaded_files = []
        for file in files:
            if file and allowed_file(file.filename):
                filename = f"{uuid.uuid4().hex[:8]}_{secure_filename(file.filename)}"
                file_path = os.path.join(event_dir, filename)
                file.save(file_path)
                uploaded_files.append(filename)
        
        # Lazy load threading
        threading = get_threading()
        threading.Thread(target=process_images, args=(event_id,)).start()

        # Update events data
        events_data = get_events_cached().copy()
        for event in events_data:
            if event['id'] == event_id:
                event['photos_count'] += len(uploaded_files)
                break
        
        with open(EVENTS_DATA_PATH, 'w') as f:
            json.dump(events_data, f, indent=2)
        
        invalidate_events_cache()  # PERFORMANCE: Invalidate cache
        
        return jsonify({
            "success": True, 
            "message": f"Successfully uploaded {len(uploaded_files)} photos",
            "uploaded_files": uploaded_files
        }), 200
    except Exception as e:
        print(f"Error uploading photos: {e}")
        return jsonify({"success": False, "error": "Failed to upload photos"}), 500

@app.route('/api/admin/events/<event_id>/photos', methods=['GET'])
@admin_required
def get_admin_event_photos(event_id):
    """
    Admin-only endpoint to retrieve all uploaded photos for an event.
    Returns original uploaded photos (not processed ones) for management.
    """
    try:
        # Verify event exists
        events_data = get_events_cached()
        event = next((e for e in events_data if e['id'] == event_id), None)
        
        if not event:
            return jsonify({
                "success": False, 
                "error": "Event not found"
            }), 404
        
        # Get photos from uploads directory
        event_dir = os.path.join(app.config['UPLOAD_FOLDER'], event_id)
        
        if not os.path.exists(event_dir):
            return jsonify({
                "success": True,
                "event_id": event_id,
                "photos": [],
                "total_count": 0
            }), 200
        
        # List all image files, excluding QR codes
        photos = []
        for filename in os.listdir(event_dir):
            # Skip QR codes and non-image files
            if filename.endswith('_qr.png') or not filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp')):
                continue
            
            file_path = os.path.join(event_dir, filename)
            
            # Get file metadata
            try:
                file_stat = os.stat(file_path)
                file_size = file_stat.st_size
                upload_time = datetime.fromtimestamp(file_stat.st_mtime).isoformat()
            except:
                file_size = 0
                upload_time = None
            
            photos.append({
                "filename": filename,
                "url": f"/uploads/{event_id}/{filename}",
                "type": "uploaded",
                "size": file_size,
                "uploaded_at": upload_time
            })
        
        # Sort by upload time (newest first)
        photos.sort(key=lambda x: x['uploaded_at'] or '', reverse=True)
        
        return jsonify({
            "success": True,
            "event_id": event_id,
            "photos": photos,
            "total_count": len(photos)
        }), 200
        
    except Exception as e:
        print(f"Error retrieving event photos: {e}")
        return jsonify({
            "success": False, 
            "error": "Failed to retrieve photos"
        }), 500

@app.route('/api/admin/events/<event_id>/photos/<filename>', methods=['DELETE'])
@admin_required
def delete_event_photo(event_id, filename):
    """
    Admin-only endpoint to delete a specific photo from an event.
    Removes the photo from uploads directory and all processed directories.
    """
    try:
        # Verify event exists
        events_data = get_events_cached()
        event = next((e for e in events_data if e['id'] == event_id), None)
        
        if not event:
            return jsonify({
                "success": False,
                "error": "Event not found"
            }), 404
        
        # Sanitize filename to prevent path traversal
        filename = secure_filename(filename)
        
        deletion_errors = []
        files_deleted = 0
        
        # 1. Delete from uploads directory
        upload_path = os.path.join(app.config['UPLOAD_FOLDER'], event_id, filename)
        if os.path.exists(upload_path):
            try:
                os.remove(upload_path)
                files_deleted += 1
                print(f"Deleted from uploads: {upload_path}")
            except Exception as e:
                deletion_errors.append(f"Upload deletion failed: {str(e)}")
                print(f"Error deleting upload: {e}")
        else:
            deletion_errors.append(f"Photo not found in uploads: {filename}")
        
        # 2. Delete from processed directories (all person folders)
        processed_event_dir = os.path.join(app.config['PROCESSED_FOLDER'], event_id)
        if os.path.exists(processed_event_dir):
            for person_id in os.listdir(processed_event_dir):
                person_dir = os.path.join(processed_event_dir, person_id)
                
                # Delete from individual folder
                individual_path = os.path.join(person_dir, "individual", filename)
                if os.path.exists(individual_path):
                    try:
                        os.remove(individual_path)
                        files_deleted += 1
                        print(f"Deleted from individual: {individual_path}")
                    except Exception as e:
                        deletion_errors.append(f"Individual photo deletion failed for {person_id}: {str(e)}")
                
                # Delete from group folder (with watermark prefix)
                watermarked_filename = f"watermarked_{filename}"
                group_path = os.path.join(person_dir, "group", watermarked_filename)
                if os.path.exists(group_path):
                    try:
                        os.remove(group_path)
                        files_deleted += 1
                        print(f"Deleted from group: {group_path}")
                    except Exception as e:
                        deletion_errors.append(f"Group photo deletion failed for {person_id}: {str(e)}")
        
        # 3. Update photo count in events_data.json
        if files_deleted > 0:
            events_data_copy = events_data.copy()
            for event in events_data_copy:
                if event['id'] == event_id:
                    # Decrement photo count (but not below 0)
                    event['photos_count'] = max(0, event.get('photos_count', 0) - 1)
                    break
            
            try:
                with open(EVENTS_DATA_PATH, 'w') as f:
                    json.dump(events_data_copy, f, indent=2)
                invalidate_events_cache()
                print(f"Updated photo count for event {event_id}")
            except Exception as e:
                deletion_errors.append(f"Failed to update photo count: {str(e)}")
        
        # Determine response based on results
        if files_deleted == 0:
            return jsonify({
                "success": False,
                "error": "Photo not found or already deleted",
                "details": deletion_errors
            }), 404
        
        if deletion_errors:
            # Partial success
            return jsonify({
                "success": True,
                "message": f"Photo deleted with warnings ({files_deleted} files removed)",
                "deleted_file": filename,
                "files_deleted": files_deleted,
                "warnings": deletion_errors
            }), 200
        
        # Complete success
        return jsonify({
            "success": True,
            "message": "Photo deleted successfully",
            "deleted_file": filename,
            "files_deleted": files_deleted
        }), 200
        
    except Exception as e:
        print(f"Error deleting photo: {e}")
        return jsonify({
            "success": False,
            "error": "Failed to delete photo",
            "details": str(e)
        }), 500

@app.route('/api/admin/events/<event_id>/thumbnail', methods=['POST'])
@admin_required
def upload_event_thumbnail(event_id):
    """
    Admin-only endpoint to upload a cover thumbnail for an event.
    """
    try:
        # Verify event exists
        events_data = get_events_cached()
        event = next((e for e in events_data if e['id'] == event_id), None)
        
        if not event:
            return jsonify({
                "success": False,
                "error": "Event not found"
            }), 404
        
        # Check if thumbnail file is in request
        if 'thumbnail' not in request.files:
            return jsonify({
                "success": False,
                "error": "No thumbnail file provided"
            }), 400
        
        thumbnail_file = request.files['thumbnail']
        
        if thumbnail_file.filename == '':
            return jsonify({
                "success": False,
                "error": "No file selected"
            }), 400
        
        # Validate file type
        if not allowed_file(thumbnail_file.filename):
            return jsonify({
                "success": False,
                "error": "Invalid file type. Please use JPG, PNG, or GIF"
            }), 400
        
        # Validate file size (5MB max)
        thumbnail_file.seek(0, os.SEEK_END)
        file_size = thumbnail_file.tell()
        thumbnail_file.seek(0)
        
        MAX_SIZE = 5 * 1024 * 1024  # 5MB
        if file_size > MAX_SIZE:
            return jsonify({
                "success": False,
                "error": "File too large. Maximum size is 5MB"
            }), 400
        
        # Generate unique filename
        file_ext = secure_filename(thumbnail_file.filename).rsplit('.', 1)[1].lower()
        thumbnail_filename = f"{event_id}_thumb_{uuid.uuid4().hex[:8]}.{file_ext}"
        
        # Save to thumbnails directory
        thumbnails_dir = os.path.join(app.config['UPLOAD_FOLDER'], 'thumbnails')
        os.makedirs(thumbnails_dir, exist_ok=True)
        
        thumbnail_path = os.path.join(thumbnails_dir, thumbnail_filename)
        thumbnail_file.save(thumbnail_path)
        
        # Update event data with thumbnail URL
        thumbnail_url = f"/uploads/thumbnails/{thumbnail_filename}"
        
        events_data_copy = events_data.copy()
        for evt in events_data_copy:
            if evt['id'] == event_id:
                evt['cover_thumbnail'] = thumbnail_url
                break
        
        with open(EVENTS_DATA_PATH, 'w') as f:
            json.dump(events_data_copy, f, indent=2)
        
        invalidate_events_cache()
        
        return jsonify({
            "success": True,
            "message": "Thumbnail uploaded successfully",
            "thumbnail_url": thumbnail_url
        }), 200
        
    except Exception as e:
        print(f"Error uploading thumbnail: {e}")
        return jsonify({
            "success": False,
            "error": "Failed to upload thumbnail",
            "details": str(e)
        }), 500

@app.route('/api/admin/events/<event_id>/thumbnail', methods=['PUT'])
@admin_required
def update_event_thumbnail(event_id):
    """
    Admin-only endpoint to update/replace an existing event thumbnail.
    """
    try:
        # Verify event exists
        events_data = get_events_cached()
        event = next((e for e in events_data if e['id'] == event_id), None)
        
        if not event:
            return jsonify({
                "success": False,
                "error": "Event not found"
            }), 404
        
        # Check if thumbnail file is in request
        if 'thumbnail' not in request.files:
            return jsonify({
                "success": False,
                "error": "No thumbnail file provided"
            }), 400
        
        thumbnail_file = request.files['thumbnail']
        
        if thumbnail_file.filename == '':
            return jsonify({
                "success": False,
                "error": "No file selected"
            }), 400
        
        # Validate file type
        if not allowed_file(thumbnail_file.filename):
            return jsonify({
                "success": False,
                "error": "Invalid file type. Please use JPG, PNG, or GIF"
            }), 400
        
        # Validate file size (5MB max)
        thumbnail_file.seek(0, os.SEEK_END)
        file_size = thumbnail_file.tell()
        thumbnail_file.seek(0)
        
        MAX_SIZE = 5 * 1024 * 1024  # 5MB
        if file_size > MAX_SIZE:
            return jsonify({
                "success": False,
                "error": "File too large. Maximum size is 5MB"
            }), 400
        
        # Delete old thumbnail if it exists and is not the default
        old_thumbnail = event.get('cover_thumbnail', '')
        if old_thumbnail and not old_thumbnail.endswith('default_event_thumbnail.jpg'):
            # Extract filename from URL
            if old_thumbnail.startswith('/uploads/thumbnails/'):
                old_filename = old_thumbnail.split('/')[-1]
                old_path = os.path.join(app.config['UPLOAD_FOLDER'], 'thumbnails', old_filename)
                if os.path.exists(old_path):
                    try:
                        os.remove(old_path)
                        print(f"Deleted old thumbnail: {old_path}")
                    except Exception as e:
                        print(f"Warning: Could not delete old thumbnail: {e}")
        
        # Generate unique filename for new thumbnail
        file_ext = secure_filename(thumbnail_file.filename).rsplit('.', 1)[1].lower()
        thumbnail_filename = f"{event_id}_thumb_{uuid.uuid4().hex[:8]}.{file_ext}"
        
        # Save new thumbnail
        thumbnails_dir = os.path.join(app.config['UPLOAD_FOLDER'], 'thumbnails')
        os.makedirs(thumbnails_dir, exist_ok=True)
        
        thumbnail_path = os.path.join(thumbnails_dir, thumbnail_filename)
        thumbnail_file.save(thumbnail_path)
        
        # Update event data with new thumbnail URL
        thumbnail_url = f"/uploads/thumbnails/{thumbnail_filename}"
        
        events_data_copy = events_data.copy()
        for evt in events_data_copy:
            if evt['id'] == event_id:
                evt['cover_thumbnail'] = thumbnail_url
                break
        
        with open(EVENTS_DATA_PATH, 'w') as f:
            json.dump(events_data_copy, f, indent=2)
        
        invalidate_events_cache()
        
        return jsonify({
            "success": True,
            "message": "Thumbnail updated successfully",
            "thumbnail_url": thumbnail_url
        }), 200
        
    except Exception as e:
        print(f"Error updating thumbnail: {e}")
        return jsonify({
            "success": False,
            "error": "Failed to update thumbnail",
            "details": str(e)
        }), 500

@app.route('/api/events', methods=['GET'])
@cache.cached(timeout=300)  # PERFORMANCE: Cache for 5 minutes
def api_get_all_events():
    try:
        events_data = get_events_cached()  # PERFORMANCE: Use cached data
        return jsonify(events_data)
    except Exception as e:
        print(f"Error loading events: {e}")
        return jsonify([])

@app.route('/api/events/<event_id>', methods=['PUT'])
@admin_required
def update_event(event_id):
    """Update event details"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['name', 'location', 'date', 'category', 'organization_name']
        for field in required_fields:
            if field not in data or not str(data[field]).strip():
                return jsonify({
                    "success": False,
                    "error": f"{field.replace('_', ' ').title()} is required"
                }), 400
        
        # Validate field lengths
        if len(data['name']) > 200:
            return jsonify({"success": False, "error": "Event name too long (max 200 characters)"}), 400
        if len(data['location']) > 200:
            return jsonify({"success": False, "error": "Location too long (max 200 characters)"}), 400
        if len(data['organization_name']) > 200:
            return jsonify({"success": False, "error": "Organization name too long (max 200 characters)"}), 400
        
        # Load events data
        events_data = get_events_cached().copy()
        
        # Find the event
        event = None
        event_index = None
        for idx, evt in enumerate(events_data):
            if evt['id'] == event_id:
                event = evt
                event_index = idx
                break
        
        if not event:
            return jsonify({"success": False, "error": "Event not found"}), 404
        
        # Check authorization - only event creator can edit
        admin_id = session.get('admin_id')
        if event.get('created_by') != admin_id:
            return jsonify({
                "success": False,
                "error": "Unauthorized: You can only edit your own events"
            }), 403
        
        # Update event fields (preserve all other fields)
        event['name'] = data['name'].strip()
        event['location'] = data['location'].strip()
        event['date'] = data['date']
        event['category'] = data['category'].strip()
        event['organization_name'] = data['organization_name'].strip()
        
        # Save updated events data atomically
        events_data[event_index] = event
        
        # Write to temporary file first
        import tempfile
        temp_fd, temp_path = tempfile.mkstemp(suffix='.json', dir=os.path.dirname(EVENTS_DATA_PATH))
        try:
            with os.fdopen(temp_fd, 'w') as f:
                json.dump(events_data, f, indent=2)
            
            # Create backup of current file
            if os.path.exists(EVENTS_DATA_PATH):
                backup_path = EVENTS_DATA_PATH + '.backup'
                shutil = get_shutil()
                shutil.copy(EVENTS_DATA_PATH, backup_path)
            
            # Atomic rename
            shutil.move(temp_path, EVENTS_DATA_PATH)
        except Exception as e:
            # Clean up temp file if it exists
            if os.path.exists(temp_path):
                os.remove(temp_path)
            raise e
        
        # Invalidate cache
        invalidate_events_cache()
        
        return jsonify({
            "success": True,
            "message": "Event updated successfully",
            "event": event
        }), 200
        
    except Exception as e:
        print(f"Error updating event: {e}")
        return jsonify({
            "success": False,
            "error": "Internal server error"
        }), 500

@app.route('/api/events/<event_id>', methods=['DELETE'])
@admin_required
def delete_event(event_id):
    shutil = get_shutil()
    try:
        events_data = get_events_cached().copy()
        events_data = [event for event in events_data if event['id'] != event_id]
        
        with open(EVENTS_DATA_PATH, 'w') as f:
            json.dump(events_data, f, indent=2)
        
        event_upload_dir = os.path.join(app.config['UPLOAD_FOLDER'], event_id)
        event_processed_dir = os.path.join(app.config['PROCESSED_FOLDER'], event_id)
        if os.path.exists(event_upload_dir): 
            shutil.rmtree(event_upload_dir)
        if os.path.exists(event_processed_dir): 
            shutil.rmtree(event_processed_dir)
        
        invalidate_events_cache()  # PERFORMANCE: Invalidate cache
        cache.delete('view//api/events')  # Clear API cache
        
        return jsonify({"success": True, "message": "Event deleted successfully."})
    except Exception as e:
        print(f"Error deleting event: {e}")
        return jsonify({"success": False, "error": "Failed to delete event"}), 500

# --- FILE SERVING ROUTES ---
@app.route('/api/events/<event_id>/photos', methods=['GET'])
@cache.cached(timeout=300, query_string=True)  # PERFORMANCE: Cache for 5 minutes
def get_event_photos(event_id):
    """Get only GROUP photos for an event (public access)"""
    event_dir = os.path.join(app.config['PROCESSED_FOLDER'], event_id)
    if not os.path.exists(event_dir):
        return jsonify({"success": False, "error": "No photos found for this event yet."}), 404
    
    unique_photos = set()
    for person_id in os.listdir(event_dir):
        group_dir = os.path.join(event_dir, person_id, "group")
        if os.path.exists(group_dir):
            for filename in os.listdir(group_dir):
                if filename.startswith('watermarked_'):
                    unique_photos.add(filename)
    
    photo_urls = [f"/photos/{event_id}/all/{filename}" for filename in sorted(list(unique_photos))]
    return jsonify({
        "success": True, 
        "photos": photo_urls,
        "photo_type": "group",
        "message": "Showing group photos only. Scan your face to see your individual photos."
    })

@app.route('/api/events/<event_id>/my-photos', methods=['GET'])
@login_required
def get_my_event_photos(event_id):
    """Get user's INDIVIDUAL photos after face recognition (private access)"""
    # Check if user has scanned their face for this event
    person_id = session.get(f'person_id_{event_id}')
    
    if not person_id:
        return jsonify({
            "success": False, 
            "error": "Please scan your face first to access your individual photos.",
            "requires_scan": True
        }), 403
    
    event_dir = os.path.join(app.config['PROCESSED_FOLDER'], event_id)
    person_dir = os.path.join(event_dir, person_id)
    
    if not os.path.exists(person_dir):
        return jsonify({
            "success": False, 
            "error": "No photos found for you in this event."
        }), 404
    
    # Get individual photos (only this person)
    individual_dir = os.path.join(person_dir, "individual")
    individual_photos = []
    if os.path.exists(individual_dir):
        individual_photos = [
            f"/photos/{event_id}/{person_id}/individual/{f}" 
            for f in os.listdir(individual_dir)
        ]
    
    # Get group photos (where this person appears)
    group_dir = os.path.join(person_dir, "group")
    group_photos = []
    if os.path.exists(group_dir):
        group_photos = [
            f"/photos/{event_id}/{person_id}/group/{f}" 
            for f in os.listdir(group_dir) 
            if f.startswith('watermarked_')
        ]
    
    return jsonify({
        "success": True,
        "person_id": person_id,
        "individual_photos": individual_photos,
        "group_photos": group_photos,
        "total_photos": len(individual_photos) + len(group_photos),
        "message": f"Found {len(individual_photos)} individual photos and {len(group_photos)} group photos of you."
    })

@app.route('/api/download-photo', methods=['POST'])
@login_required
def download_photo():
    """Track photo download and add to user's download history"""
    try:
        data = request.get_json()
        photo_url = data.get('photo_url')
        event_id = data.get('event_id')
        event_name = data.get('event_name')
        user_id = session.get('user_id')
        
        if not all([photo_url, event_id, event_name, user_id]):
            return jsonify({
                "success": False,
                "error": "Missing required fields"
            }), 400
        
        conn = get_db_connection()
        if not conn:
            return jsonify({
                "success": False,
                "error": "Database connection failed"
            }), 500
        
        cursor = conn.cursor()
        
        # Check if already downloaded (duplicate check)
        cursor.execute(
            "SELECT id FROM downloads WHERE user_id = %s AND photo_url = %s",
            (user_id, photo_url)
        )
        existing = cursor.fetchone()
        
        if existing:
            cursor.close()
            conn.close()
            return jsonify({
                "success": True,
                "message": "Photo already in your downloads",
                "already_downloaded": True
            })
        
        # Insert new download record
        cursor.execute(
            """INSERT INTO downloads (user_id, photo_url, event_id, event_name) 
               VALUES (%s, %s, %s, %s)""",
            (user_id, photo_url, event_id, event_name)
        )
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({
            "success": True,
            "message": "Photo added to your downloads",
            "already_downloaded": False
        })
        
    except Exception as e:
        print(f"Error tracking download: {e}")
        return jsonify({
            "success": False,
            "error": "Failed to track download"
        }), 500

@app.route('/api/my-downloads', methods=['GET'])
@login_required
def get_my_downloads():
    """Retrieve user's download history"""
    try:
        user_id = session.get('user_id')
        
        if not user_id:
            return jsonify({
                "success": False,
                "error": "User not authenticated"
            }), 401
        
        conn = get_db_connection()
        if not conn:
            return jsonify({
                "success": False,
                "error": "Database connection failed"
            }), 500
        
        cursor = conn.cursor(dictionary=True)
        
        # Get all downloads for this user, ordered by most recent first
        cursor.execute(
            """SELECT id, photo_url, event_id, event_name, downloaded_at 
               FROM downloads 
               WHERE user_id = %s 
               ORDER BY downloaded_at DESC""",
            (user_id,)
        )
        downloads = cursor.fetchall()
        
        # Convert datetime to string for JSON serialization
        for download in downloads:
            if download['downloaded_at']:
                download['downloaded_at'] = download['downloaded_at'].strftime('%Y-%m-%d %H:%M:%S')
        
        cursor.close()
        conn.close()
        
        return jsonify({
            "success": True,
            "downloads": downloads,
            "total": len(downloads)
        })
        
    except Exception as e:
        print(f"Error retrieving downloads: {e}")
        return jsonify({
            "success": False,
            "error": "Failed to retrieve downloads"
        }), 500

@app.route('/uploads/<event_id>/<filename>')
@admin_required
def serve_uploaded_photo(event_id, filename):
    """Serve uploaded photos - ADMIN ONLY for photo management"""
    event_dir = os.path.join(app.config['UPLOAD_FOLDER'], event_id)
    
    if not os.path.exists(event_dir):
        return "Event Not Found", 404
    
    photo_path = os.path.join(event_dir, filename)
    if not os.path.exists(photo_path):
        return "Photo Not Found", 404
    
    return send_from_directory(event_dir, filename)

@app.route('/uploads/thumbnails/<filename>')
def serve_thumbnail(filename):
    """Serve event thumbnail images - PUBLIC ACCESS for event cards"""
    thumbnails_dir = os.path.join(app.config['UPLOAD_FOLDER'], 'thumbnails')
    
    if not os.path.exists(thumbnails_dir):
        return "Thumbnails directory not found", 404
    
    thumbnail_path = os.path.join(thumbnails_dir, filename)
    if not os.path.exists(thumbnail_path):
        # Return default thumbnail if specific one not found
        return redirect('/static/images/default_event_thumbnail.jpg')
    
    return send_from_directory(thumbnails_dir, filename)

@app.route('/photos/<event_id>/all/<filename>')
def get_public_photo(event_id, filename):
    """Serve ONLY group photos (public access) - Individual photos are BLOCKED"""
    # SECURITY: Only serve files with 'watermarked_' prefix (group photos)
    if not filename.startswith('watermarked_'):
        return "Access Denied - Individual photos require face scan", 403
    
    event_dir = os.path.join(app.config['PROCESSED_FOLDER'], event_id)
    if not os.path.exists(event_dir):
        return "Event Not Found", 404
        
    for person_id in os.listdir(event_dir):
        photo_path = os.path.join(event_dir, person_id, "group", filename)
        if os.path.exists(photo_path):
            return send_from_directory(os.path.join(event_dir, person_id, "group"), filename)
    return "File Not Found", 404

@app.route('/photos/<event_id>/<person_id>/<photo_type>/<filename>')
@login_required
def get_private_photo(event_id, person_id, photo_type, filename):
    """Serve individual/group photos - ONLY after face scan verification"""
    # SECURITY: Verify user has scanned their face for this event
    session_person_id = session.get(f'person_id_{event_id}')
    
    if not session_person_id:
        return "Access Denied - Please scan your face first", 403
    
    # SECURITY: Users can only access their own photos
    if session_person_id != person_id:
        return "Access Denied - You can only access your own photos", 403
    
    # SECURITY: Only allow 'individual' or 'group' photo types
    if photo_type not in ['individual', 'group']:
        return "Invalid photo type", 400
    
    photo_path = os.path.join(app.config['PROCESSED_FOLDER'], event_id, person_id, photo_type)
    if not os.path.exists(os.path.join(photo_path, filename)):
        return "Photo Not Found", 404
        
    return send_from_directory(photo_path, filename)

# --- ADMIN ROUTES ---
@app.route('/admin/reprocess-event/<event_id>', methods=['POST'])
@login_required
def admin_reprocess_event(event_id):
    """Admin endpoint to manually trigger photo reprocessing for an event"""
    threading = get_threading()
    threading.Thread(target=process_images, args=(event_id,), daemon=True).start()
    return jsonify({
        "success": True,
        "message": f"Started reprocessing photos for event {event_id}"
    })

@app.route('/admin/reprocess-all', methods=['POST'])
@login_required
def admin_reprocess_all():
    """Admin endpoint to reprocess all events"""
    threading = get_threading()
    
    if os.path.exists(UPLOAD_FOLDER):
        event_ids = [
            d for d in os.listdir(UPLOAD_FOLDER) 
            if os.path.isdir(os.path.join(UPLOAD_FOLDER, d))
        ]
        
        for event_id in event_ids:
            threading.Thread(target=process_images, args=(event_id,), daemon=True).start()
        
        return jsonify({
            "success": True,
            "message": f"Started reprocessing {len(event_ids)} events",
            "events": event_ids
        })
    
    return jsonify({"success": False, "error": "No events found"})

# --- MAIN EXECUTION BLOCK ---
def process_existing_uploads_async():
    """Process existing uploads in background - DISABLED for performance"""
    # PERFORMANCE FIX: Don't process on startup, only when photos are uploaded
    pass

if __name__ == '__main__':
    if not os.path.exists(EVENTS_DATA_PATH):
        with open(EVENTS_DATA_PATH, 'w') as f:
            json.dump([], f)
    
    # PERFORMANCE FIX: Disabled automatic background processing
    # Images will be processed only when uploaded via /api/upload_photos
    print("--- [SERVER] Starting optimized server (background processing disabled) ---")
    
    # PERFORMANCE: Use debug=False in production
    app.run(host='0.0.0.0', port=5000, debug=True, threaded=True)
