from flask import Flask, request, jsonify, send_from_directory, render_template, session, redirect, url_for
from functools import wraps
import os
import base64
import numpy as np
import cv2
import face_recognition
import shutil
import threading
import json
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import qrcode
from io import BytesIO
import uuid
from datetime import datetime
import traceback # Import for better error logging

# Import face recognition models
from face_model import FaceRecognitionModel
from multi_angle_face_model import (
    MultiAngleFaceModel, 
    preprocess_image_for_recognition, 
    detect_sunglasses,
    detect_face_orientation,
    assess_image_quality,
    analyze_photo_all_faces_all_angles
)

# --- CONFIGURATION ---
app = Flask(__name__, static_folder='../frontend/static', template_folder='../frontend/pages')
app.secret_key = 'your_super_secret_key_here'
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

# --- INITIALIZE THE ML MODELS ---
# Old model for backward compatibility
model = FaceRecognitionModel(data_file=KNOWN_FACES_DATA_PATH)

# New multi-angle model
MULTI_ANGLE_DATA_PATH = os.path.join(BASE_DIR, 'multi_angle_faces.dat')
multi_angle_model = MultiAngleFaceModel(data_file=MULTI_ANGLE_DATA_PATH)

# Migrate old data to new model if needed
if len(model.known_encodings) > 0 and len(multi_angle_model.known_faces) == 0:
    print("--- [INIT] Migrating old face data to multi-angle model ---")
    multi_angle_model.migrate_from_old_model(model.known_encodings, model.known_ids)
    print("--- [INIT] Migration complete ---")

# --- HELPER FUNCTIONS ---
def get_db_connection():
    try: return mysql.connector.connect(**DB_CONFIG)
    except mysql.connector.Error as err: print(f"DB Error: {err}"); return None

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'): return redirect(url_for('serve_login_page'))
        return f(*args, **kwargs)
    return decorated_function

# Import robust face detector
try:
    from robust_face_detector import RobustFaceDetector
    robust_detector = RobustFaceDetector()
    USE_ROBUST_DETECTION = True
    print("--- [INIT] Robust Face Detector loaded successfully ---")
except Exception as e:
    USE_ROBUST_DETECTION = False
    robust_detector = None
    print(f"--- [INIT] Robust Face Detector not available: {e} ---")
    print("--- [INIT] Falling back to standard face_recognition ---")

def process_images(event_id):
    """
    Process images for an event with ROBUST face detection:
    - Uses multiple detection algorithms with automatic fallback
    - Handles sunglasses, varying lighting, different angles
    - Image preprocessing for challenging scenarios
    - 1 face = INDIVIDUAL photo (stored ONLY in individual folder, NO watermark)
    - 2+ faces = GROUP photo (stored ONLY in group folder, WITH watermark prefix)
    """
    try:
        input_dir = os.path.join(app.config['UPLOAD_FOLDER'], event_id)
        output_dir = os.path.join(app.config['PROCESSED_FOLDER'], event_id)
        
        if not os.path.exists(input_dir):
            print(f"--- [PROCESS] No upload folder found for event: {event_id} ---")
            return
        
        os.makedirs(output_dir, exist_ok=True)

        print(f"--- [PROCESS] Starting for event: {event_id} ---")
        if USE_ROBUST_DETECTION:
            print(f"--- [PROCESS] Using ROBUST face detection (multi-algorithm + preprocessing) ---")
        else:
            print(f"--- [PROCESS] Using standard face detection ---")
        
        processed_count = 0
        skipped_count = 0
        robust_success_count = 0
        
        for filename in os.listdir(input_dir):
            if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp')) and not filename.endswith('_qr.png'):
                image_path = os.path.join(input_dir, filename)
                
                # CRITICAL FIX: Check if already processed WITH faces
                # Don't skip if photo was processed but had 0 faces detected
                already_processed_with_faces = False
                if os.path.exists(output_dir):
                    for person_folder in os.listdir(output_dir):
                        person_path = os.path.join(output_dir, person_folder)
                        if os.path.isdir(person_path):
                            # Check individual folder
                            individual_path = os.path.join(person_path, "individual", filename)
                            # Check group folder (with watermark)
                            group_path = os.path.join(person_path, "group", f"watermarked_{filename}")
                            if os.path.exists(individual_path) or os.path.exists(group_path):
                                already_processed_with_faces = True
                                break
                
                if already_processed_with_faces:
                    print(f"--- [PROCESS] Skipping {filename} (already processed with faces)")
                    skipped_count += 1
                    continue
                
                print(f"--- [PROCESS] Processing: {filename}")
                try:
                    face_encodings = []
                    face_count = 0
                    detection_method = 'standard'
                    
                    # Try ROBUST detection first
                    if USE_ROBUST_DETECTION and robust_detector:
                        try:
                            import cv2
                            image_cv = cv2.imread(image_path)
                            
                            if image_cv is not None:
                                # Use robust detection with preprocessing
                                face_detections, method = robust_detector.detect_faces_robust(
                                    image_cv,
                                    use_preprocessing=True,
                                    enhancement_level='medium'
                                )
                                
                                if face_detections:
                                    # Get encodings from detected faces
                                    face_encodings = robust_detector.get_face_encodings_from_detections(
                                        image_cv,
                                        face_detections
                                    )
                                    face_count = len(face_encodings)
                                    detection_method = f'robust_{method}'
                                    robust_success_count += 1
                                    print(f"--- [PROCESS] ROBUST detection ({method}): Found {face_count} face(s)")
                        except Exception as e:
                            print(f"--- [PROCESS] Robust detection failed: {e}, falling back to standard ---")
                    
                    # Fallback to standard detection if robust failed or not available
                    if face_count == 0:
                        image = face_recognition.load_image_file(image_path)
                        face_encodings = face_recognition.face_encodings(image)
                        face_count = len(face_encodings)
                        detection_method = 'standard'
                        print(f"--- [PROCESS] Standard detection: Found {face_count} face(s)")
                    
                    if face_count == 0:
                        print(f"--- [PROCESS] No faces detected by any method, skipping")
                        skipped_count += 1
                        continue
                    
                    # ENHANCED: Match faces using intelligent cross-angle matching
                    person_ids_in_image = set()
                    
                    # Analyze photo for orientation and quality
                    try:
                        # Load image for analysis
                        image_rgb = face_recognition.load_image_file(image_path)
                        
                        for i, face_encoding in enumerate(face_encodings):
                            # Get face location for this encoding
                            if USE_ROBUST_DETECTION and robust_detector and face_detections:
                                if i < len(face_detections):
                                    face_location = face_detections[i]['location']
                                else:
                                    face_location = None
                            else:
                                face_locations_list = face_recognition.face_locations(image_rgb)
                                face_location = face_locations_list[i] if i < len(face_locations_list) else None
                            
                            # Detect orientation and quality
                            orientation = 'unknown'
                            has_accessories = False
                            quality_score = 0.8  # Default
                            
                            if face_location:
                                orientation = detect_face_orientation(image_rgb, face_location)
                                has_accessories = detect_sunglasses(image_rgb, face_location)
                                quality_score = assess_image_quality(image_rgb, face_location)
                            
                            # Try ENHANCED multi-angle recognition with orientation awareness
                            person_id, confidence, matched_angle, distance, match_details = multi_angle_model.recognize_face_multi_angle(
                                face_encoding,
                                adaptive_tolerance=True,
                                photo_orientation=orientation,
                                has_accessories=has_accessories,
                                quality_score=quality_score
                            )
                            
                            if person_id:
                                person_ids_in_image.add(person_id)
                                print(f"--- [PROCESS] ✓ MATCHED {person_id} ---")
                                print(f"    Confidence: {confidence:.1f}%, Orientation: {orientation}, "
                                      f"Quality: {quality_score:.2f}, Accessories: {has_accessories}")
                            else:
                                # Fallback to old model for backward compatibility
                                person_id = model.learn_face(face_encoding)
                                person_ids_in_image.add(person_id)
                                print(f"--- [PROCESS] New face learned: {person_id} (via fallback) ---")
                    
                    except Exception as e:
                        print(f"--- [PROCESS] Error in enhanced matching: {e}, using basic matching ---")
                        # Fallback to basic matching
                        for face_encoding in face_encodings:
                            person_id, confidence, best_angle, distance, _ = multi_angle_model.recognize_face_multi_angle(
                                face_encoding,
                                adaptive_tolerance=True
                            )
                            
                            if person_id:
                                person_ids_in_image.add(person_id)
                            else:
                                person_id = model.learn_face(face_encoding)
                                person_ids_in_image.add(person_id)
                    
                    print(f"--- [PROCESS] Person IDs: {', '.join(person_ids_in_image)} (via {detection_method})")
                    
                    # CRITICAL: Classify based on face count
                    if face_count == 1:
                        # INDIVIDUAL PHOTO - store ONLY in individual folder, NO watermark
                        print(f"--- [PROCESS] Classifying as INDIVIDUAL photo")
                        for pid in person_ids_in_image:
                            person_dir = os.path.join(output_dir, pid)
                            individual_dir = os.path.join(person_dir, "individual")
                            os.makedirs(individual_dir, exist_ok=True)
                            
                            dest_path = os.path.join(individual_dir, filename)
                            shutil.copy(image_path, dest_path)
                            print(f"--- [PROCESS] Saved to: {pid}/individual/{filename}")
                    else:
                        # GROUP PHOTO - store ONLY in group folder, WITH watermark prefix
                        print(f"--- [PROCESS] Classifying as GROUP photo")
                        watermarked_filename = f"watermarked_{filename}"
                        for pid in person_ids_in_image:
                            person_dir = os.path.join(output_dir, pid)
                            group_dir = os.path.join(person_dir, "group")
                            os.makedirs(group_dir, exist_ok=True)
                            
                            dest_path = os.path.join(group_dir, watermarked_filename)
                            shutil.copy(image_path, dest_path)
                            print(f"--- [PROCESS] Saved to: {pid}/group/{watermarked_filename}")
                    
                    processed_count += 1
                    print(f"--- [PROCESS] ✓ Successfully processed {filename}")
                    
                except Exception as e:
                    print(f"--- [PROCESS] ERROR processing {filename}: {e}")
                    traceback.print_exc()
                    skipped_count += 1
        
        model.save_model()
        print(f"--- [PROCESS] Finished for event: {event_id} ---")
        print(f"--- [PROCESS] Processed: {processed_count}, Skipped: {skipped_count} ---")
        if USE_ROBUST_DETECTION:
            print(f"--- [PROCESS] Robust detection successful: {robust_success_count}/{processed_count} ---")
            if robust_detector:
                robust_detector.print_stats()
    except Exception as e:
        print(f"--- [PROCESS] FATAL ERROR during processing for event {event_id}: {e}")
        traceback.print_exc()


def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# --- ROUTES FOR SERVING PAGES ---
@app.route('/')
def serve_index(): return render_template('index.html')
@app.route('/login')
def serve_login_page(): return render_template('login.html')
@app.route('/signup')
def serve_signup_page(): return render_template('signup.html')
@app.route('/homepage')
@login_required
def serve_homepage(): return render_template('homepage.html')
@app.route('/event_discovery')
@login_required
def serve_event_discovery(): return render_template('event_discovery.html')
@app.route('/event_detail')
@login_required
def serve_event_detail(): return render_template('event_detail.html')
@app.route('/biometric_authentication_portal')
@login_required
def serve_biometric_authentication_portal(): return render_template('biometric_authentication_portal.html')
@app.route('/personal_photo_gallery')
@login_required
def serve_personal_photo_gallery(): return render_template('personal_photo_gallery.html')
@app.route('/event_organizer')
@login_required
def serve_event_organizer(): return render_template('event_organizer.html')
@app.route('/admin_login')
def serve_admin_login(): return render_template('admin_login.html')
@app.route('/admin_dashboard')
def serve_admin_dashboard():
    if not session.get('admin_logged_in'):
        return redirect(url_for('serve_admin_login'))
    return render_template('admin_dashboard.html')

# --- AUTHENTICATION API ROUTES ---
@app.route('/register', methods=['POST'])
def register_user():
    data = request.get_json()
    full_name, email, password = data.get('fullName'), data.get('email'), data.get('password')
    if not all([full_name, email, password]): return jsonify({"success": False, "error": "All fields are required"}), 400
    hashed_password = generate_password_hash(password)
    conn = get_db_connection()
    if conn is None: return jsonify({"success": False, "error": "Database connection failed"}), 500
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
        if cursor.fetchone(): return jsonify({"success": False, "error": "Email already registered"}), 409
        cursor.execute("INSERT INTO users (full_name, email, password) VALUES (%s, %s, %s)", (full_name, email, hashed_password))
        conn.commit()
        return jsonify({"success": True, "message": "Registration successful!"}), 201
    except mysql.connector.Error as err:
        conn.rollback(); return jsonify({"success": False, "error": "Registration failed"}), 500
    finally:
        cursor.close(); conn.close()

@app.route('/login', methods=['POST'])
def login_user():
    data = request.get_json()
    email, password = data.get('email'), data.get('password')
    if not all([email, password]): return jsonify({"success": False, "error": "Email and password are required"}), 400
    conn = get_db_connection()
    if conn is None: return jsonify({"success": False, "error": "Database connection failed"}), 500
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
    except mysql.connector.Error as err:
        print(f"Error during login: {err}")
        return jsonify({"success": False, "error": "An internal server error occurred during login."}), 500
    finally:
        cursor.close(); conn.close()

@app.route('/logout')
def logout_user():
    session.clear()
    return redirect(url_for('serve_index'))

@app.route('/admin_login', methods=['POST'])
def admin_login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    # Admin credentials (in production, use environment variables or database)
    ADMIN_USERNAME = 'admin'
    ADMIN_PASSWORD = 'admin123'  # Change this in production!
    
    if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
        session['admin_logged_in'] = True
        session['admin_username'] = username
        return jsonify({"success": True, "message": "Admin login successful"}), 200
    else:
        return jsonify({"success": False, "error": "Invalid admin credentials"}), 401

@app.route('/admin_logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    session.pop('admin_username', None)
    return redirect(url_for('serve_admin_login'))

# --- CORE API & FILE SERVING ROUTES ---

# THIS IS THE FUNCTION THAT WAS MISSING AND CAUSED THE 405 ERROR
@app.route('/api/events/<event_id>', methods=['GET'])
def get_single_event(event_id):
    try:
        if not os.path.exists(EVENTS_DATA_PATH):
            return jsonify({"success": False, "error": "Events data not found"}), 404
        
        with open(EVENTS_DATA_PATH, 'r') as f:
            events_data = json.load(f)
        
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
    try:
        data = request.get_json()
        image_data = data.get('image')
        event_id = data.get('event_id', 'default_event')
        multi_angle = data.get('multi_angle', False)
        all_encodings = data.get('encodings', [])
        
        if not image_data: 
            return jsonify({"success": False, "error": "No image provided"}), 400
        
        print(f"--- [RECOGNIZE] Multi-angle mode: {multi_angle}, Encodings received: {len(all_encodings)} ---")
        
        # Decode and process the primary image
        img_bytes = base64.b64decode(image_data)
        np_arr = np.frombuffer(img_bytes, np.uint8)
        img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
        
        # Use robust detection for better accuracy
        face_encodings_to_match = []
        
        if USE_ROBUST_DETECTION and robust_detector and multi_angle and len(all_encodings) == 3:
            # Process all three angle images with robust detection
            print("--- [RECOGNIZE] Using ROBUST multi-angle recognition ---")
            for enc_data in all_encodings:
                angle = enc_data.get('angle')
                angle_image_data = enc_data.get('image')
                
                try:
                    angle_img_bytes = base64.b64decode(angle_image_data)
                    angle_np_arr = np.frombuffer(angle_img_bytes, np.uint8)
                    angle_img = cv2.imdecode(angle_np_arr, cv2.IMREAD_COLOR)
                    
                    # Use robust detection
                    face_detections, method = robust_detector.detect_faces_robust(
                        angle_img,
                        use_preprocessing=True,
                        enhancement_level='medium'
                    )
                    
                    if face_detections:
                        # Get encodings from detected faces
                        encodings = robust_detector.get_face_encodings_from_detections(
                            angle_img,
                            face_detections
                        )
                        if encodings:
                            face_encodings_to_match.extend(encodings)
                            print(f"--- [RECOGNIZE] {angle} angle: Found encoding via {method} ---")
                    else:
                        # Fallback to standard detection
                        rgb_img = cv2.cvtColor(angle_img, cv2.COLOR_BGR2RGB)
                        face_locations = face_recognition.face_locations(rgb_img)
                        if face_locations:
                            encodings = face_recognition.face_encodings(rgb_img, face_locations)
                            if encodings:
                                face_encodings_to_match.extend(encodings)
                                print(f"--- [RECOGNIZE] {angle} angle: Found encoding via standard detection ---")
                except Exception as e:
                    print(f"--- [RECOGNIZE] Error processing {angle} angle: {e} ---")
                    continue
        else:
            # Standard single-image recognition
            rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            face_locations = face_recognition.face_locations(rgb_img)
            if not face_locations: 
                return jsonify({"success": False, "error": "No face detected in scan."}), 400
            
            scanned_encodings = face_recognition.face_encodings(rgb_img, face_locations)
            if scanned_encodings:
                face_encodings_to_match = [scanned_encodings[0]]
        
        if not face_encodings_to_match:
            return jsonify({"success": False, "error": "No face detected in any angle."}), 400
        
        print(f"--- [RECOGNIZE] Total encodings to match: {len(face_encodings_to_match)} ---")
        
        # Multi-angle matching: Try to match with ANY of the captured encodings
        best_person_id = None
        best_distance = float('inf')
        
        for encoding in face_encodings_to_match:
            person_id = model.recognize_face(encoding)
            if person_id:
                # Calculate distance to get confidence
                if model.known_encodings:
                    distances = face_recognition.face_distance(model.known_encodings, encoding)
                    min_distance = np.min(distances)
                    if min_distance < best_distance:
                        best_distance = min_distance
                        best_person_id = person_id
                        print(f"--- [RECOGNIZE] Better match found: {person_id} with distance {min_distance:.2f} ---")
        
        # If multi-angle scan, store the encodings in multi-angle model
        if multi_angle and len(face_encodings_to_match) >= 3 and not best_person_id:
            print("--- [RECOGNIZE] Storing new multi-angle encodings ---")
            encodings_dict = {}
            quality_scores = {}
            
            for i, enc_data in enumerate(all_encodings):
                angle = enc_data.get('angle')
                if i < len(face_encodings_to_match):
                    encodings_dict[angle] = face_encodings_to_match[i]
                    quality_scores[angle] = 85.0  # Default quality score
            
            # Learn the new face with multi-angle encodings
            new_person_id = multi_angle_model.learn_face_multi_angle(encodings_dict, quality_scores)
            if new_person_id:
                best_person_id = new_person_id
                best_distance = 0.0
                print(f"--- [RECOGNIZE] Created new person: {new_person_id} with {len(encodings_dict)} angles ---")
        
        # Try ENHANCED multi-angle model recognition if standard matching didn't work
        if not best_person_id and len(face_encodings_to_match) > 0:
            print("--- [RECOGNIZE] Trying ENHANCED multi-angle model recognition ---")
            
            # Detect orientation and quality from the primary image
            rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            face_locations = face_recognition.face_locations(rgb_img)
            
            orientation = 'unknown'
            has_accessories = False
            quality_score = 0.8
            
            if face_locations:
                orientation = detect_face_orientation(rgb_img, face_locations[0])
                has_accessories = detect_sunglasses(rgb_img, face_locations[0])
                quality_score = assess_image_quality(rgb_img, face_locations[0])
                print(f"--- [RECOGNIZE] Detected: orientation={orientation}, accessories={has_accessories}, quality={quality_score:.2f} ---")
            
            for encoding in face_encodings_to_match:
                person_id, confidence, matched_angle, distance, match_details = multi_angle_model.recognize_face_multi_angle(
                    encoding,
                    adaptive_tolerance=True,
                    photo_orientation=orientation,
                    has_accessories=has_accessories,
                    quality_score=quality_score
                )
                if person_id and distance < best_distance:
                    best_person_id = person_id
                    best_distance = distance
                    print(f"--- [RECOGNIZE] ✓ Enhanced multi-angle match: {person_id} ---")
                    print(f"    Confidence: {confidence:.1f}%, Orientation: {orientation}, Distance: {distance:.3f}")
                    break
        
        if best_person_id:
            person_dir = os.path.join(app.config['PROCESSED_FOLDER'], event_id, best_person_id)
            if not os.path.exists(person_dir): 
                return jsonify({"success": False, "error": "Match found, but no photos in this event."}), 404
            
            individual_dir = os.path.join(person_dir, "individual")
            group_dir = os.path.join(person_dir, "group")
            individual_photos = [f for f in os.listdir(individual_dir)] if os.path.exists(individual_dir) else []
            group_photos = [f for f in os.listdir(group_dir) if f.startswith('watermarked_')] if os.path.exists(group_dir) else []
            
            confidence = max(0, (1 - best_distance / 0.6) * 100)
            print(f"--- [RECOGNIZE] ✓ Match: {best_person_id}, Confidence: {confidence:.1f}%, Photos: {len(individual_photos)} individual, {len(group_photos)} group ---")
            
            return jsonify({
                "success": True, 
                "person_id": best_person_id, 
                "individual_photos": individual_photos, 
                "group_photos": group_photos, 
                "event_id": event_id,
                "confidence": round(confidence, 1),
                "multi_angle_used": multi_angle and len(face_encodings_to_match) > 1
            })
        else:
            return jsonify({"success": False, "error": "No confident match found. Please try again with better lighting."}), 404

    except Exception as e:
        print(f"RECOGNIZE ERROR: {e}")
        traceback.print_exc()
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
        
        qr_data = f"http://127.0.0.1:5000/event_detail?event_id={event_id}"
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(qr_data)
        qr.make(fit=True)
        qr_img = qr.make_image(fill_color="black", back_color="white")
        qr_path = os.path.join(event_upload_dir, f"{event_id}_qr.png")
        qr_img.save(qr_path)
        
        events_data = []
        if os.path.exists(EVENTS_DATA_PATH):
            with open(EVENTS_DATA_PATH, 'r') as f:
                events_data = json.load(f)
        
        new_event = {
            "id": event_id, "name": event_name, "location": event_location,
            "date": event_date, "category": event_category, "image": "/static/images/default_event.jpg",
            "photos_count": 0, "qr_code": f"/api/qr_code/{event_id}",
            "created_by": session.get('user_id'), "created_at": datetime.now().isoformat()
        }
        events_data.append(new_event)
        with open(EVENTS_DATA_PATH, 'w') as f:
            json.dump(events_data, f, indent=2)

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
        threading.Thread(target=process_images, args=(event_id,)).start()

        if os.path.exists(EVENTS_DATA_PATH):
            with open(EVENTS_DATA_PATH, 'r') as f:
                events_data = json.load(f)
            for event in events_data:
                if event['id'] == event_id:
                    event['photos_count'] += len(uploaded_files)
                    break
            with open(EVENTS_DATA_PATH, 'w') as f:
                json.dump(events_data, f, indent=2)
        return jsonify({
            "success": True, 
            "message": f"Successfully uploaded {len(uploaded_files)} photos",
            "uploaded_files": uploaded_files
        }), 200
    except Exception as e:
        print(f"Error uploading photos: {e}")
        return jsonify({"success": False, "error": "Failed to upload photos"}), 500

@app.route('/api/events', methods=['GET'])
def api_get_all_events():
    try:
        if os.path.exists(EVENTS_DATA_PATH):
            with open(EVENTS_DATA_PATH, 'r') as f:
                return jsonify(json.load(f))
        return jsonify([])
    except Exception as e:
        print(f"Error loading events: {e}")
        return jsonify([])

@app.route('/api/events/<event_id>', methods=['DELETE'])
@login_required
def delete_event(event_id):
    try:
        if os.path.exists(EVENTS_DATA_PATH):
            with open(EVENTS_DATA_PATH, 'r') as f:
                events_data = json.load(f)
            events_data = [event for event in events_data if event['id'] != event_id]
            with open(EVENTS_DATA_PATH, 'w') as f:
                json.dump(events_data, f, indent=2)
        
        event_upload_dir = os.path.join(app.config['UPLOAD_FOLDER'], event_id)
        event_processed_dir = os.path.join(app.config['PROCESSED_FOLDER'], event_id)
        if os.path.exists(event_upload_dir): shutil.rmtree(event_upload_dir)
        if os.path.exists(event_processed_dir): shutil.rmtree(event_processed_dir)
        return jsonify({"success": True, "message": "Event deleted successfully."})
    except Exception as e:
        print(f"Error deleting event: {e}")
        return jsonify({"success": False, "error": "Failed to delete event"}), 500

# --- FILE SERVING ROUTES ---

# NEW: Get ALL uploaded photos for an event (including unprocessed)
@app.route('/api/events/<event_id>/all-photos', methods=['GET'])
@login_required
def get_all_event_photos(event_id):
    """Get ALL uploaded photos for an event, including those without faces"""
    try:
        upload_dir = os.path.join(app.config['UPLOAD_FOLDER'], event_id)
        processed_dir = os.path.join(app.config['PROCESSED_FOLDER'], event_id)
        
        photos = []
        
        # Get all uploaded photos
        if os.path.exists(upload_dir):
            for filename in os.listdir(upload_dir):
                if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp')) and not filename.endswith('_qr.png'):
                    file_path = os.path.join(upload_dir, filename)
                    file_stats = os.stat(file_path)
                    
                    # Check if processed
                    is_processed = False
                    face_count = 0
                    if os.path.exists(processed_dir):
                        for person_folder in os.listdir(processed_dir):
                            person_path = os.path.join(processed_dir, person_folder)
                            if os.path.isdir(person_path):
                                individual_path = os.path.join(person_path, "individual", filename)
                                group_path = os.path.join(person_path, "group", f"watermarked_{filename}")
                                if os.path.exists(individual_path):
                                    is_processed = True
                                    face_count = 1
                                    break
                                elif os.path.exists(group_path):
                                    is_processed = True
                                    face_count = 2  # At least 2
                                    break
                    
                    photos.append({
                        "filename": filename,
                        "url": f"/uploads/{event_id}/{filename}",
                        "size": file_stats.st_size,
                        "uploaded_at": datetime.fromtimestamp(file_stats.st_mtime).isoformat(),
                        "is_processed": is_processed,
                        "face_count": face_count,
                        "type": "group" if face_count >= 2 else ("individual" if face_count == 1 else "unprocessed")
                    })
        
        return jsonify({
            "success": True,
            "event_id": event_id,
            "photos": sorted(photos, key=lambda x: x['uploaded_at'], reverse=True),
            "total": len(photos)
        })
    except Exception as e:
        print(f"Error getting all event photos: {e}")
        traceback.print_exc()
        return jsonify({"success": False, "error": "Failed to retrieve photos"}), 500

# NEW: Serve uploaded photos directly
@app.route('/uploads/<event_id>/<filename>')
@login_required
def serve_uploaded_photo(event_id, filename):
    """Serve photos from uploads folder"""
    upload_dir = os.path.join(app.config['UPLOAD_FOLDER'], event_id)
    return send_from_directory(upload_dir, filename)

# NEW: Delete a photo
@app.route('/api/photos/<event_id>/<filename>', methods=['DELETE'])
@login_required
def delete_photo(event_id, filename):
    """Delete a photo from uploads and processed folders"""
    try:
        deleted_files = []
        
        # Delete from uploads folder
        upload_path = os.path.join(app.config['UPLOAD_FOLDER'], event_id, filename)
        if os.path.exists(upload_path):
            os.remove(upload_path)
            deleted_files.append(f"uploads/{event_id}/{filename}")
        
        # Delete from processed folders
        processed_dir = os.path.join(app.config['PROCESSED_FOLDER'], event_id)
        if os.path.exists(processed_dir):
            for person_folder in os.listdir(processed_dir):
                person_path = os.path.join(processed_dir, person_folder)
                if os.path.isdir(person_path):
                    # Check individual folder
                    individual_path = os.path.join(person_path, "individual", filename)
                    if os.path.exists(individual_path):
                        os.remove(individual_path)
                        deleted_files.append(f"processed/{event_id}/{person_folder}/individual/{filename}")
                    
                    # Check group folder (with watermark)
                    group_path = os.path.join(person_path, "group", f"watermarked_{filename}")
                    if os.path.exists(group_path):
                        os.remove(group_path)
                        deleted_files.append(f"processed/{event_id}/{person_folder}/group/watermarked_{filename}")
        
        # Update event photo count
        if os.path.exists(EVENTS_DATA_PATH):
            with open(EVENTS_DATA_PATH, 'r') as f:
                events_data = json.load(f)
            for event in events_data:
                if event['id'] == event_id and event.get('photos_count', 0) > 0:
                    event['photos_count'] -= 1
                    break
            with open(EVENTS_DATA_PATH, 'w') as f:
                json.dump(events_data, f, indent=2)
        
        return jsonify({
            "success": True,
            "message": f"Photo deleted successfully",
            "deleted_files": deleted_files
        })
    except Exception as e:
        print(f"Error deleting photo: {e}")
        traceback.print_exc()
        return jsonify({"success": False, "error": "Failed to delete photo"}), 500

# NEW: Get all photos for current user (dashboard)
@app.route('/api/my-photos', methods=['GET'])
@login_required
def get_my_photos():
    """Get all photos uploaded by the current user across all events"""
    try:
        user_id = session.get('user_id')
        all_photos = []
        
        # Get events created by user
        if os.path.exists(EVENTS_DATA_PATH):
            with open(EVENTS_DATA_PATH, 'r') as f:
                events_data = json.load(f)
            
            user_events = [e for e in events_data if e.get('created_by') == user_id]
            
            for event in user_events:
                event_id = event['id']
                upload_dir = os.path.join(app.config['UPLOAD_FOLDER'], event_id)
                
                if os.path.exists(upload_dir):
                    for filename in os.listdir(upload_dir):
                        if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp')) and not filename.endswith('_qr.png'):
                            file_path = os.path.join(upload_dir, filename)
                            file_stats = os.stat(file_path)
                            
                            all_photos.append({
                                "filename": filename,
                                "url": f"/uploads/{event_id}/{filename}",
                                "event_id": event_id,
                                "event_name": event['name'],
                                "size": file_stats.st_size,
                                "uploaded_at": datetime.fromtimestamp(file_stats.st_mtime).isoformat()
                            })
        
        return jsonify({
            "success": True,
            "photos": sorted(all_photos, key=lambda x: x['uploaded_at'], reverse=True),
            "total": len(all_photos)
        })
    except Exception as e:
        print(f"Error getting user photos: {e}")
        traceback.print_exc()
        return jsonify({"success": False, "error": "Failed to retrieve photos"}), 500

# EXISTING: Get processed group photos for an event
@app.route('/api/events/<event_id>/photos', methods=['GET'])
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
def process_existing_uploads_on_startup():
    print("--- [LOG] Checking for existing photos on startup... ---")
    if os.path.exists(UPLOAD_FOLDER):
        for event_id in os.listdir(UPLOAD_FOLDER):
            if os.path.isdir(os.path.join(UPLOAD_FOLDER, event_id)):
                threading.Thread(target=process_images, args=(event_id,)).start()

if __name__ == '__main__':
    if not os.path.exists(EVENTS_DATA_PATH):
        with open(EVENTS_DATA_PATH, 'w') as f:
            json.dump([], f)
    process_existing_uploads_on_startup()
    app.run(host='0.0.0.0', port=5000, debug=True)