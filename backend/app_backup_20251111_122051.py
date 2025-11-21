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

# PERFORMANCE: Enable Gzip compression (70% smaller responses)
Compress(app)

# PERFORMANCE: Configure caching
cache = Cache(app, config={
    'CACHE_TYPE': 'simple',  # Use 'redis' for production
    'CACHE_DEFAULT_TIMEOUT': 300  # 5 minutes
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
        if elapsed > 1.0:  # Log requests taking more than 1 second
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

def process_images(event_id):
    # Lazy load heavy dependencies
    face_recognition = get_face_recognition()
    shutil = get_shutil()
    traceback = get_traceback()
    model = get_face_model()
    
    try:
        input_dir = os.path.join(app.config['UPLOAD_FOLDER'], event_id)
        output_dir = os.path.join(app.config['PROCESSED_FOLDER'], event_id)
        os.makedirs(output_dir, exist_ok=True)

        print(f"--- [PROCESS] Starting for event: {event_id} ---")
        for filename in os.listdir(input_dir):
            if filename.lower().endswith(('.png', '.jpg', '.jpeg')) and not filename.endswith('_qr.png'):
                image_path = os.path.join(input_dir, filename)
                print(f"--- [PROCESS] Image: {filename}")
                try:
                    image = face_recognition.load_image_file(image_path)
                    face_encodings = face_recognition.face_encodings(image)
                    print(f"--- [PROCESS] Found {len(face_encodings)} face(s) in {filename}")
                    
                    person_ids_in_image = {model.learn_face(encoding) for encoding in face_encodings}

                    if len(face_encodings) > 0:
                        for pid in person_ids_in_image:
                            person_dir = os.path.join(output_dir, pid)
                            os.makedirs(os.path.join(person_dir, "individual"), exist_ok=True)
                            os.makedirs(os.path.join(person_dir, "group"), exist_ok=True)

                            if len(face_encodings) == 1:
                                shutil.copy(image_path, os.path.join(person_dir, "individual", filename))
                            shutil.copy(image_path, os.path.join(person_dir, "group", f"watermarked_{filename}"))
                except Exception as e:
                    print(f"  -> ERROR processing {filename}: {e}")
                    traceback.print_exc()
        model.save_model()
        print(f"--- [PROCESS] Finished for event: {event_id} ---")
    except Exception as e:
        print(f"  -> FATAL ERROR during processing for event {event_id}: {e}")
        traceback.print_exc()

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

@app.route('/event_organizer')
@login_required
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

# --- CORE API & FILE SERVING ROUTES ---

@app.route('/api/events/<event_id>', methods=['GET'])
@cache.cached(timeout=300, query_string=True)  # PERFORMANCE: Cache for 5 minutes
def get_single_event(event_id):
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
            
            individual_dir = os.path.join(person_dir, "individual")
            group_dir = os.path.join(person_dir, "group")
            individual_photos = [f for f in os.listdir(individual_dir)] if os.path.exists(individual_dir) else []
            group_photos = [f for f in os.listdir(group_dir) if f.startswith('watermarked_')] if os.path.exists(group_dir) else []
            
            return jsonify({
                "success": True, 
                "person_id": person_id, 
                "individual_photos": individual_photos, 
                "group_photos": group_photos, 
                "event_id": event_id
            })
        else:
            return jsonify({"success": False, "error": "No confident match found."}), 404

    except Exception as e:
        print(f"RECOGNIZE ERROR: {e}")
        return jsonify({"success": False, "error": "An internal error occurred."}), 500

# --- EVENT ORGANIZER API ROUTES ---
@app.route('/api/create_event', methods=['POST'])
@login_required
def create_event():
    try:
        data = request.get_json()
        event_name = data.get('eventName')
        event_location = data.get('eventLocation')
        event_date = data.get('eventDate')
        event_category = data.get('eventCategory', 'General')
        
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
        
        events_data = get_events_cached().copy()  # PERFORMANCE: Use cached data
        
        new_event = {
            "id": event_id, "name": event_name, "location": event_location,
            "date": event_date, "category": event_category, "image": "/static/images/default_event.jpg",
            "photos_count": 0, "qr_code": f"/api/qr_code/{event_id}",
            "created_by": session.get('user_id'), "created_at": datetime.now().isoformat()
        }
        events_data.append(new_event)
        
        with open(EVENTS_DATA_PATH, 'w') as f:
            json.dump(events_data, f, indent=2)
        
        invalidate_events_cache()  # PERFORMANCE: Invalidate cache
        cache.delete('view//api/events')  # Clear API cache

        return jsonify({"success": True, "event_id": event_id, "message": "Event created successfully!"}), 201
        
    except Exception as e:
        print(f"Error creating event: {e}")
        return jsonify({"success": False, "error": "Failed to create event"}), 500

@app.route('/api/qr_code/<event_id>', methods=['GET'])
def get_qr_code(event_id):
    qr_path = os.path.join(app.config['UPLOAD_FOLDER'], event_id, f"{event_id}_qr.png")
    if os.path.exists(qr_path):
        return send_from_directory(os.path.join(app.config['UPLOAD_FOLDER'], event_id), f"{event_id}_qr.png")
    return "QR Code not found", 404

@app.route('/api/upload_photos/<event_id>', methods=['POST'])
@login_required
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

@app.route('/api/events', methods=['GET'])
@cache.cached(timeout=300)  # PERFORMANCE: Cache for 5 minutes
def api_get_all_events():
    try:
        events_data = get_events_cached()  # PERFORMANCE: Use cached data
        return jsonify(events_data)
    except Exception as e:
        print(f"Error loading events: {e}")
        return jsonify([])

@app.route('/api/events/<event_id>', methods=['DELETE'])
@login_required
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
    return jsonify({"success": True, "photos": photo_urls})

@app.route('/photos/<event_id>/all/<filename>')
def get_public_photo(event_id, filename):
    event_dir = os.path.join(app.config['PROCESSED_FOLDER'], event_id)
    for person_id in os.listdir(event_dir):
        photo_path = os.path.join(event_dir, person_id, "group", filename)
        if os.path.exists(photo_path):
            return send_from_directory(os.path.join(event_dir, person_id, "group"), filename)
    return "File Not Found", 404

@app.route('/photos/<event_id>/<person_id>/<photo_type>/<filename>')
@login_required
def get_private_photo(event_id, person_id, photo_type, filename):
    photo_path = os.path.join(app.config['PROCESSED_FOLDER'], event_id, person_id, photo_type)
    return send_from_directory(photo_path, filename)

# --- MAIN EXECUTION BLOCK ---
def process_existing_uploads_async():
    """Process existing uploads in background after server starts"""
    import time
    time.sleep(2)  # Wait for server to fully start
    
    threading = get_threading()
    print("--- [LOG] Checking for existing photos (background)... ---")
    if os.path.exists(UPLOAD_FOLDER):
        for event_id in os.listdir(UPLOAD_FOLDER):
            if os.path.isdir(os.path.join(UPLOAD_FOLDER, event_id)):
                threading.Thread(target=process_images, args=(event_id,)).start()

if __name__ == '__main__':
    if not os.path.exists(EVENTS_DATA_PATH):
        with open(EVENTS_DATA_PATH, 'w') as f:
            json.dump([], f)
    
    # Start background processing AFTER server starts
    import threading
    threading.Thread(target=process_existing_uploads_async, daemon=True).start()
    
    # PERFORMANCE: Use debug=False in production
    app.run(host='0.0.0.0', port=5000, debug=True)
