# Design Document

## Overview

The Enhanced Multi-Angle Face Detection System is a comprehensive face recognition platform that combines multiple detection algorithms, deep feature extraction, multi-angle storage, and real-time matching capabilities. The system processes uploaded photos to detect and analyze faces, stores multiple angle encodings per person, and enables instant face-based photo retrieval through live webcam scanning.

The architecture follows a layered approach with clear separation between detection, feature extraction, storage, matching, and API layers. This design ensures modularity, testability, and scalability.

## Architecture

### System Layers

```
┌─────────────────────────────────────────────────────────────┐
│                     API Layer (Flask)                       │
│  - Photo Upload/Processing Endpoints                        │
│  - Live Scanning Endpoints                                  │
│  - Search Endpoints                                         │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                   Processing Layer                          │
│  ┌──────────────────────────────────────────────┐          │
│  │  PhotoProcessor                              │          │
│  │  - Batch photo processing                    │          │
│  │  - Face detection orchestration              │          │
│  └──────────────────────────────────────────────┘          │
│  ┌──────────────────────────────────────────────┐          │
│  │  LiveFaceScanner                             │          │
│  │  - Webcam capture                            │          │
│  │  - Real-time matching                        │          │
│  └──────────────────────────────────────────────┘          │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                   Core Components                           │
│  ┌──────────────────────────────────────────────┐          │
│  │  EnhancedFaceDetector                        │          │
│  │  - Multi-algorithm detection                 │          │
│  │  - Angle estimation                          │          │
│  │  - Quality scoring                           │          │
│  └──────────────────────────────────────────────┘          │
│  ┌──────────────────────────────────────────────┐          │
│  │  DeepFeatureExtractor                        │          │
│  │  - 128D encoding generation                  │          │
│  │  - Facial landmark extraction                │          │
│  │  - Feature analysis                          │          │
│  └──────────────────────────────────────────────┘          │
│  ┌──────────────────────────────────────────────┐          │
│  │  EnhancedMatchingEngine                      │          │
│  │  - Multi-angle comparison                    │          │
│  │  - Weighted confidence scoring               │          │
│  │  - Fast nearest-neighbor search              │          │
│  └──────────────────────────────────────────────┘          │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                   Data Layer                                │
│  ┌──────────────────────────────────────────────┐          │
│  │  MultiAngleFaceDatabase                      │          │
│  │  - Person management                         │          │
│  │  - Multi-angle encoding storage              │          │
│  │  - Photo associations                        │          │
│  └──────────────────────────────────────────────┘          │
│  ┌──────────────────────────────────────────────┐          │
│  │  SQLite Database                             │          │
│  │  - 6 core tables                             │          │
│  │  - Performance indexes                       │          │
│  │  - Foreign key constraints                   │          │
│  └──────────────────────────────────────────────┘          │
└─────────────────────────────────────────────────────────────┘
```

### Data Flow

**Photo Processing Flow:**
```
Upload Photo → Detect Faces → Extract Features → Match/Create Person → Store Encodings → Associate Photo
```

**Live Scanning Flow:**
```
Capture Face → Validate Quality → Extract Encoding → Match Person → Retrieve Photos → Return Results
```

## Components and Interfaces

### 1. EnhancedFaceDetector

**Purpose:** Detect faces using multiple algorithms with angle estimation and quality assessment.

**Interface:**
```python
class EnhancedFaceDetector:
    def __init__(self):
        """Initialize all detection algorithms"""
        
    def detect_faces(self, image: np.ndarray) -> List[Dict]:
        """
        Detect all faces in an image
        
        Args:
            image: Input image as numpy array
            
        Returns:
            List of face detections with bbox, method, confidence
        """
        
    def estimate_angle(self, face_image: np.ndarray, landmarks: np.ndarray) -> str:
        """
        Estimate face angle from landmarks
        
        Args:
            face_image: Cropped face image
            landmarks: 68-point facial landmarks
            
        Returns:
            Angle classification: 'frontal', 'left_45', 'right_45', 'left_90', 'right_90'
        """
        
    def calculate_quality_score(self, face_image: np.ndarray) -> Dict[str, float]:
        """
        Calculate face quality metrics
        
        Args:
            face_image: Cropped face image
            
        Returns:
            Dictionary with blur_score, lighting_score, size_score, overall_score
        """
```

**Detection Strategy:**
1. Try MTCNN first (best for frontal faces)
2. Fall back to Haar Cascade (fast, works in various conditions)
3. Fall back to HOG (good for profile faces)
4. Return all detected faces with method used

**Angle Estimation Algorithm:**
- Calculate nose tip to face center vector
- Calculate eye center line angle
- Classify based on landmark positions:
  - Frontal: Both eyes visible, nose centered
  - Profile 45°: One eye partially visible
  - Profile 90°: One eye not visible

**Quality Scoring:**
- Blur: Laplacian variance (higher = sharper)
- Lighting: Histogram analysis (balanced = better)
- Size: Face area relative to image (larger = better)
- Overall: Weighted average of all metrics

### 2. DeepFeatureExtractor

**Purpose:** Extract 128D encodings and detailed facial features.

**Interface:**
```python
class DeepFeatureExtractor:
    def __init__(self):
        """Initialize face_recognition and dlib models"""
        
    def extract_encoding(self, face_image: np.ndarray) -> np.ndarray:
        """
        Extract 128D face encoding
        
        Args:
            face_image: Cropped face image
            
        Returns:
            128-dimensional numpy array
        """
        
    def extract_landmarks(self, face_image: np.ndarray) -> np.ndarray:
        """
        Extract 68 facial landmarks
        
        Args:
            face_image: Cropped face image
            
        Returns:
            68x2 numpy array of (x, y) coordinates
        """
        
    def analyze_features(self, face_image: np.ndarray, landmarks: np.ndarray) -> Dict:
        """
        Analyze detailed facial features
        
        Args:
            face_image: Cropped face image
            landmarks: 68-point landmarks
            
        Returns:
            Dictionary with measurements and attributes
        """
```

**Feature Analysis:**
- Eye distance: Distance between eye centers
- Nose dimensions: Width and height from landmarks
- Jaw width: Distance between jaw points
- Facial hair: Texture analysis in chin/mustache regions
- Glasses: Edge detection around eyes

### 3. MultiAngleFaceDatabase

**Purpose:** Manage person records and multi-angle encoding storage.

**Interface:**
```python
class MultiAngleFaceDatabase:
    def __init__(self, db_path: str):
        """Initialize database connection"""
        
    def add_person(self, person_uuid: str, name: str = None) -> int:
        """
        Create new person record
        
        Args:
            person_uuid: Unique identifier
            name: Optional person name
            
        Returns:
            Person ID
        """
        
    def add_face_encoding(self, person_id: int, encoding: np.ndarray, 
                         angle: str, quality: float, face_detection_id: int) -> int:
        """
        Store face encoding for specific angle
        
        Args:
            person_id: Person identifier
            encoding: 128D encoding vector
            angle: Angle classification
            quality: Quality score
            face_detection_id: Associated detection ID
            
        Returns:
            Encoding ID
        """
        
    def get_person_encodings(self, person_id: int, angle: str = None) -> List[Dict]:
        """
        Retrieve encodings for a person
        
        Args:
            person_id: Person identifier
            angle: Optional angle filter
            
        Returns:
            List of encoding records
        """
        
    def associate_photo(self, person_id: int, photo_id: int, 
                       is_group: bool, confidence: float) -> int:
        """
        Associate photo with person
        
        Args:
            person_id: Person identifier
            photo_id: Photo identifier
            is_group: Whether photo contains multiple faces
            confidence: Match confidence score
            
        Returns:
            Association ID
        """
```

**Storage Strategy:**
- Store up to 5 angles per person
- Keep highest quality encoding per angle
- Mark best overall encoding as primary
- Replace lowest quality when limit reached

### 4. EnhancedMatchingEngine

**Purpose:** Match faces against database with multi-angle support.

**Interface:**
```python
class EnhancedMatchingEngine:
    def __init__(self, database: MultiAngleFaceDatabase, threshold: float = 0.6):
        """Initialize matching engine"""
        
    def match_face(self, encoding: np.ndarray, angle: str = None) -> Dict:
        """
        Match single encoding against database
        
        Args:
            encoding: 128D encoding to match
            angle: Optional angle hint
            
        Returns:
            Match result with person_id, confidence, distance
        """
        
    def match_multi_angle(self, encodings: Dict[str, np.ndarray]) -> Dict:
        """
        Match multiple angles simultaneously
        
        Args:
            encodings: Dictionary mapping angles to encodings
            
        Returns:
            Best match result with weighted confidence
        """
        
    def calculate_confidence(self, distances: List[float], 
                           qualities: List[float], 
                           angles: List[str]) -> float:
        """
        Calculate weighted match confidence
        
        Args:
            distances: List of encoding distances
            qualities: List of encoding quality scores
            angles: List of angle classifications
            
        Returns:
            Weighted confidence score (0-1)
        """
```

**Matching Algorithm:**
1. Calculate Euclidean distance between encodings
2. Apply angle-based weights:
   - Frontal: 1.0
   - 45° profile: 0.8
   - 90° profile: 0.6
3. Apply quality-based weights (0.3 quality + 0.7 distance)
4. Return match if weighted distance < threshold
5. Select person with highest confidence

**Performance Optimization:**
- Cache frequently accessed encodings
- Use numpy vectorization for distance calculations
- Index database queries by angle
- Batch process multiple matches

### 5. PhotoProcessor

**Purpose:** Orchestrate photo processing workflow.

**Interface:**
```python
class PhotoProcessor:
    def __init__(self):
        """Initialize all components"""
        
    def process_photo(self, photo_path: str, event_id: str) -> Dict:
        """
        Process single photo
        
        Args:
            photo_path: Path to photo file
            event_id: Event identifier
            
        Returns:
            Processing results with face count, persons identified
        """
        
    def process_event(self, event_id: str, force_reprocess: bool = False) -> Dict:
        """
        Process all photos in event
        
        Args:
            event_id: Event identifier
            force_reprocess: Whether to reprocess already processed photos
            
        Returns:
            Batch processing results
        """
```

**Processing Workflow:**
1. Load image from file
2. Detect all faces using EnhancedFaceDetector
3. For each detected face:
   - Extract encoding and features
   - Estimate angle and quality
   - Match against database
   - Create new person if no match
   - Store encoding and features
   - Associate photo with person
4. Update photo processing status
5. Return summary statistics

### 6. LiveFaceScanner

**Purpose:** Real-time face capture and matching.

**Interface:**
```python
class LiveFaceScanner:
    def __init__(self):
        """Initialize scanner components"""
        
    def capture_face(self, camera_index: int = 0, 
                    min_quality: float = 0.5) -> Dict:
        """
        Capture face from webcam
        
        Args:
            camera_index: Camera device index
            min_quality: Minimum quality threshold
            
        Returns:
            Captured face data with encoding and quality
        """
        
    def scan_and_match(self, camera_index: int = 0) -> Dict:
        """
        Complete scan and match workflow
        
        Args:
            camera_index: Camera device index
            
        Returns:
            Match results with person info and photos
        """
        
    def get_person_photos(self, person_id: int) -> Dict:
        """
        Retrieve all photos of person
        
        Args:
            person_id: Person identifier
            
        Returns:
            Individual and group photos with metadata
        """
```

**Capture Strategy:**
1. Open webcam stream
2. Detect face in frame
3. Validate quality score
4. Prompt user to adjust if quality low
5. Capture when quality sufficient
6. Extract encoding
7. Match against database
8. Retrieve and return photos

## Data Models

### Database Schema

**photos**
- id (PK)
- event_id
- filename
- filepath
- upload_date
- has_faces
- processed
- face_count

**persons**
- id (PK)
- person_uuid (UNIQUE)
- name
- created_date
- last_seen
- total_photos
- confidence_score

**face_detections**
- id (PK)
- photo_id (FK → photos)
- person_id (FK → persons)
- face_bbox (JSON)
- face_crop_path
- detection_confidence
- detection_method
- angle_estimate
- quality_score
- created_date

**face_encodings**
- id (PK)
- face_detection_id (FK → face_detections)
- person_id (FK → persons)
- encoding_vector (BLOB)
- angle
- quality_score
- is_primary
- created_date

**facial_features**
- id (PK)
- face_detection_id (FK → face_detections)
- landmarks (BLOB)
- eye_distance
- nose_width
- nose_height
- jaw_width
- mouth_width
- has_facial_hair
- facial_hair_type
- glasses
- age_estimate
- gender_estimate
- created_date

**person_photos**
- id (PK)
- person_id (FK → persons)
- photo_id (FK → photos)
- is_group_photo
- face_count_in_photo
- match_confidence
- created_date
- UNIQUE(person_id, photo_id)

### Indexes

```sql
CREATE INDEX idx_photos_event ON photos(event_id);
CREATE INDEX idx_photos_has_faces ON photos(has_faces);
CREATE INDEX idx_face_detections_photo ON face_detections(photo_id);
CREATE INDEX idx_face_detections_person ON face_detections(person_id);
CREATE INDEX idx_face_detections_angle ON face_detections(angle_estimate);
CREATE INDEX idx_face_encodings_person ON face_encodings(person_id);
CREATE INDEX idx_face_encodings_angle ON face_encodings(angle);
CREATE INDEX idx_face_encodings_quality ON face_encodings(quality_score);
CREATE INDEX idx_person_photos_person ON person_photos(person_id);
CREATE INDEX idx_person_photos_photo ON person_photos(photo_id);
```

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system-essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: Face Detection Completeness
*For any* image containing faces, at least one detection algorithm should successfully detect faces when the faces meet minimum size requirements (>30 pixels).
**Validates: Requirements 1.1, 1.2, 1.3**

### Property 2: Angle Classification Consistency
*For any* detected face with valid landmarks, the angle estimation should produce one of the five valid classifications (frontal, left_45, right_45, left_90, right_90).
**Validates: Requirements 2.2, 2.3**

### Property 3: Quality Score Bounds
*For any* detected face, all quality scores (blur, lighting, size, overall) should be bounded between 0.0 and 1.0 inclusive.
**Validates: Requirements 3.1, 3.2, 3.3, 3.4**

### Property 4: Encoding Dimensionality
*For any* successfully extracted face encoding, the encoding vector should have exactly 128 dimensions.
**Validates: Requirements 4.1**

### Property 5: Multi-Angle Storage Limit
*For any* person in the database, the number of stored encodings should not exceed 5 angles, and when at capacity, adding a higher quality encoding should replace the lowest quality existing encoding.
**Validates: Requirements 5.2, 5.4, 5.5**

### Property 6: Person UUID Uniqueness
*For any* two distinct person records in the database, their person_uuid values should be different.
**Validates: Requirements 6.1**

### Property 7: Match Threshold Consistency
*For any* face encoding match, if the Euclidean distance is below the threshold (0.6), it should be classified as a positive match; otherwise it should not be classified as a match.
**Validates: Requirements 7.2, 7.6**

### Property 8: Photo Association Uniqueness
*For any* person-photo pair, there should be at most one association record in the person_photos table.
**Validates: Requirements 15.4**

### Property 9: Cascade Delete Integrity
*For any* photo deletion, all associated face_detections, face_encodings, facial_features, and person_photos records should also be deleted.
**Validates: Requirements 15.1, 15.2, 15.3**

### Property 10: Quality-Based Primary Selection
*For any* person with multiple encodings, the encoding marked as primary should have the highest quality_score among all encodings for that person.
**Validates: Requirements 5.3**

### Property 11: Group Photo Classification
*For any* photo in the database, it should be classified as a group photo if and only if its face_count is greater than 1.
**Validates: Requirements 10.2, 10.3**

### Property 12: Match Confidence Weighting
*For any* multi-angle match calculation, the confidence score should be a weighted combination where frontal angles contribute more (weight 1.0) than profile angles (weight 0.6-0.8).
**Validates: Requirements 7.4, 7.5**

### Property 13: Processing Idempotency
*For any* photo that has been processed, reprocessing the same photo should produce consistent face detections and encodings (within tolerance for non-deterministic algorithms).
**Validates: Requirements 8.7**

### Property 14: Live Scan Quality Validation
*For any* live face capture, if the quality score is below 0.5, the system should reject the capture and prompt for repositioning.
**Validates: Requirements 9.3, 9.4**

### Property 15: API Response Consistency
*For any* valid API request, the response should include a "success" boolean field and appropriate data or error message based on the operation result.
**Validates: Requirements 12.7**

## Error Handling

### Detection Errors
- **No faces detected**: Log warning, mark photo as processed with face_count=0
- **Detection algorithm failure**: Try next algorithm in sequence
- **All algorithms fail**: Log error, continue with next photo

### Feature Extraction Errors
- **Encoding extraction fails**: Skip face, log error
- **Landmark detection fails**: Use default angle classification (frontal)
- **Feature analysis fails**: Store partial features, continue processing

### Database Errors
- **Connection failure**: Retry with exponential backoff
- **Constraint violation**: Rollback transaction, log error
- **Query timeout**: Cancel query, return error to caller

### API Errors
- **Invalid request**: Return 400 Bad Request with validation errors
- **Resource not found**: Return 404 Not Found
- **Server error**: Return 500 Internal Server Error, log stack trace
- **Timeout**: Return 504 Gateway Timeout

### Webcam Errors
- **Camera not available**: Return error message with troubleshooting steps
- **Capture failure**: Retry up to 3 times
- **Quality too low**: Prompt user to adjust lighting/position

## Testing Strategy

### Unit Testing

**Test Framework**: pytest

**Test Coverage**:
- Face detection with various image conditions
- Angle estimation accuracy
- Quality score calculation
- Encoding extraction
- Landmark detection
- Feature analysis
- Database CRUD operations
- Matching algorithm accuracy
- API endpoint request/response

**Test Files**:
- `test_enhanced_detector.py`
- `test_feature_extractor.py`
- `test_database.py`
- `test_matching_engine.py`
- `test_photo_processor.py`
- `test_live_scanner.py`
- `test_api.py`

### Property-Based Testing

**Test Framework**: Hypothesis (Python property-based testing library)

**Configuration**: Each property test should run a minimum of 100 iterations

**Test Tagging**: Each property-based test must include a comment with the format:
```python
# Feature: enhanced-face-detection, Property 1: Face Detection Completeness
```

**Property Tests**:
1. Test encoding dimensionality across random face images
2. Test quality score bounds with generated face data
3. Test angle classification consistency
4. Test multi-angle storage limits
5. Test match threshold consistency
6. Test cascade delete integrity
7. Test primary encoding selection

### Integration Testing

**Test Scenarios**:
- End-to-end photo upload and processing
- Live scan and photo retrieval workflow
- Multi-angle matching across different poses
- Batch processing of event photos
- API request/response cycles

### Performance Testing

**Benchmarks**:
- Face detection: <500ms per photo
- Feature extraction: <200ms per face
- Database match: <100ms per encoding
- Photo retrieval: <200ms per person
- Live scan workflow: <2s total

**Load Testing**:
- Concurrent API requests (100 users)
- Large batch processing (1000 photos)
- Database query performance (10,000 persons)

## Performance Optimization

### Detection Optimization
- Use MTCNN with optimized parameters
- Resize large images before detection
- Skip detection for very small faces (<30px)
- Cache detection models in memory

### Matching Optimization
- Index encodings by angle in database
- Use numpy vectorization for distance calculations
- Cache frequently accessed person encodings
- Implement early termination for obvious non-matches

### Database Optimization
- Use prepared statements
- Batch insert operations
- Implement connection pooling
- Regular VACUUM and ANALYZE operations

### API Optimization
- Implement response caching
- Use async processing for batch operations
- Compress large responses
- Rate limiting for resource-intensive endpoints

## Security Considerations

### Data Privacy
- Store face encodings as binary blobs (not reversible to images)
- Implement access controls for person data
- Log access to sensitive operations
- Support data deletion requests (GDPR compliance)

### API Security
- Validate all input parameters
- Sanitize file uploads
- Implement rate limiting
- Use HTTPS for all endpoints
- Authenticate admin operations

### Database Security
- Use parameterized queries (prevent SQL injection)
- Encrypt sensitive data at rest
- Regular backups
- Audit logging for data modifications

## Deployment Considerations

### Dependencies
```
face_recognition==1.3.0
opencv-python==4.8.0
dlib==19.24.0
mtcnn==0.1.1
tensorflow==2.13.0
numpy==1.24.3
scipy==1.11.1
flask==2.3.2
hypothesis==6.92.0  # For property-based testing
pytest==7.4.3
```

### System Requirements
- Python 3.8+
- 4GB RAM minimum (8GB recommended)
- GPU optional (improves detection speed)
- Webcam for live scanning
- 10GB storage for face crops and database

### Configuration Files
- `config.py`: Detection thresholds, matching parameters
- `database_config.py`: Database connection settings
- `api_config.py`: API endpoints, CORS settings

## Future Enhancements

### Phase 2 Features
- Age progression matching
- Emotion recognition
- Face clustering for unknown persons
- Video processing support
- Mobile app integration
- Cloud storage integration
- Advanced analytics dashboard

### Scalability Improvements
- Distributed processing for large batches
- Redis caching layer
- PostgreSQL migration for larger datasets
- Microservices architecture
- Kubernetes deployment
