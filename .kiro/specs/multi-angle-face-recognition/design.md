# Design Document: Multi-Angle Face Recognition System

## Overview

This design document specifies a comprehensive multi-angle face recognition system that enhances the existing PicMe face scanner application. The system implements a three-stage sequential scanning process to capture facial features from multiple perspectives (center, left profile, right profile), enabling robust face recognition in challenging conditions including partial face visibility, accessories, and low-light environments.

The design builds upon the existing `LiveFaceScanner` and `RobustFaceDetector` components, extending them with multi-angle encoding storage, weighted matching algorithms, and enhanced recognition capabilities.

## Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    User Interface Layer                      │
│  (Camera Feed, Instructions, Progress, Feedback)            │
└────────────────────┬────────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────────┐
│              Face Scanning Controller                        │
│  - Stage Management (Center → Left → Right)                 │
│  - User Guidance & Progress Tracking                        │
│  - Quality Validation & Retry Logic                         │
└────────────────────┬────────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────────┐
│           Multi-Angle Face Detector                         │
│  - Face Detection (RobustFaceDetector)                      │
│  - Pose Estimation & Angle Validation                       │
│  - Quality Assessment (brightness, sharpness, size)         │
└────────────────────┬────────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────────┐
│           Encoding Generation & Storage                      │
│  - Multi-Angle Encoding Generation                          │
│  - Angle Labeling (center, left, right)                    │
│  - Persistent Storage with User Association                 │
└────────────────────┬────────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────────┐
│         Weighted Matching Engine                            │
│  - Multi-Angle Comparison                                   │
│  - Angle-Aware Weighting                                    │
│  - Confidence Scoring                                       │
│  - Configurable Tolerance                                   │
└─────────────────────────────────────────────────────────────┘
```

### Component Interaction Flow

**Enrollment Flow:**
1. User initiates face scanning
2. Controller guides through 3 stages (center, left, right)
3. Each stage: detect → validate → capture → encode
4. All encodings stored with angle labels and user ID
5. Success confirmation displayed

**Recognition Flow:**
1. Photo uploaded for processing
2. Faces detected using RobustFaceDetector
3. For each face: extract encoding
4. Weighted matching against all stored multi-angle encodings
5. Return matches with confidence scores

## Components and Interfaces

### 1. MultiAngleFaceScanner

Enhanced version of `LiveFaceScanner` with three-stage scanning process.

```python
class MultiAngleFaceScanner:
    """
    Multi-angle face scanning system with sequential capture stages
    """
    
    # Scanning stages
    STAGES = ['center', 'left', 'right']
    
    # Stage configurations
    STAGE_CONFIG = {
        'center': {
            'name': 'Center Face',
            'instruction': 'Please face the camera directly and keep your face centered',
            'yaw_range': (-15, 15),
            'step_number': 1
        },
        'left': {
            'name': 'Left Profile',
            'instruction': 'Please turn your head to the LEFT',
            'yaw_range': (-55, -25),
            'step_number': 2
        },
        'right': {
            'name': 'Right Profile',
            'instruction': 'Please turn your head to the RIGHT',
            'yaw_range': (25, 55),
            'step_number': 3
        }
    }
    
    def __init__(self):
        """Initialize scanner with stage tracking"""
        
    def start_scanning_session(self, user_id: str) -> Dict:
        """Start new scanning session for user"""
        
    def get_current_stage_info(self) -> Dict:
        """Get information about current scanning stage"""
        
    def detect_and_validate_face(self, frame: np.ndarray) -> Tuple[bool, Optional[Dict], str]:
        """Detect face and validate for current stage"""
        
    def capture_current_stage(self, frame: np.ndarray) -> Tuple[bool, str]:
        """Capture face for current stage"""
        
    def advance_to_next_stage(self) -> bool:
        """Move to next scanning stage"""
        
    def retry_current_stage(self):
        """Retry current stage after failure"""
        
    def is_session_complete(self) -> bool:
        """Check if all stages completed"""
        
    def finalize_session(self) -> Dict:
        """Finalize session and return summary"""
        
    def cancel_session(self):
        """Cancel session and cleanup"""
```

### 2. MultiAngleEncodingManager

Manages storage and retrieval of multi-angle face encodings.

```python
class MultiAngleEncodingManager:
    """
    Manages multi-angle face encodings with persistent storage
    """
    
    def __init__(self, storage_path: str):
        """Initialize with storage path"""
        
    def store_user_encodings(
        self, 
        user_id: str, 
        encodings: Dict[str, np.ndarray],
        metadata: Dict
    ) -> bool:
        """Store all three angle encodings for user"""
        
    def get_user_encodings(self, user_id: str) -> Optional[Dict[str, np.ndarray]]:
        """Retrieve all encodings for user"""
        
    def get_all_encodings(self) -> Dict[str, Dict[str, np.ndarray]]:
        """Get all stored encodings (for matching)"""
        
    def update_encoding(
        self, 
        user_id: str, 
        angle: str, 
        encoding: np.ndarray
    ) -> bool:
        """Update specific angle encoding"""
        
    def delete_user_encodings(self, user_id: str) -> bool:
        """Delete all encodings for user"""
        
    def export_encodings_to_json(self, output_path: str) -> bool:
        """Export encodings to JSON format"""
        
    def import_encodings_from_json(self, input_path: str) -> bool:
        """Import encodings from JSON format"""
```

### 3. WeightedFaceMatcher

Implements weighted matching algorithm considering all three angles.

```python
class WeightedFaceMatcher:
    """
    Weighted face matching using multi-angle encodings
    """
    
    # Default weights for different input angles
    DEFAULT_WEIGHTS = {
        'frontal': {'center': 0.7, 'left': 0.15, 'right': 0.15},
        'left_profile': {'center': 0.2, 'left': 0.7, 'right': 0.1},
        'right_profile': {'center': 0.2, 'left': 0.1, 'right': 0.7},
        'unknown': {'center': 0.4, 'left': 0.3, 'right': 0.3}
    }
    
    def __init__(self, tolerance: float = 0.6):
        """Initialize matcher with tolerance"""
        
    def estimate_face_angle(
        self, 
        face_landmarks: Dict
    ) -> str:
        """Estimate angle of detected face (frontal, left_profile, right_profile, unknown)"""
        
    def match_face(
        self, 
        input_encoding: np.ndarray,
        input_landmarks: Optional[Dict],
        stored_encodings: Dict[str, Dict[str, np.ndarray]]
    ) -> List[Tuple[str, float]]:
        """
        Match input face against all stored multi-angle encodings
        
        Returns:
            List of (user_id, confidence_score) tuples, sorted by confidence
        """
        
    def calculate_weighted_distance(
        self,
        input_encoding: np.ndarray,
        user_encodings: Dict[str, np.ndarray],
        input_angle: str
    ) -> float:
        """Calculate weighted distance for a user"""
        
    def set_tolerance(self, tolerance: float):
        """Update matching tolerance"""
        
    def set_custom_weights(self, angle_type: str, weights: Dict[str, float]):
        """Set custom weights for specific angle type"""
```

### 4. EnhancedRobustDetector

Extension of `RobustFaceDetector` with additional preprocessing for challenging conditions.

```python
class EnhancedRobustDetector(RobustFaceDetector):
    """
    Enhanced robust detector with additional preprocessing for accessories and low-light
    """
    
    def detect_with_accessories(
        self, 
        image: np.ndarray
    ) -> Tuple[List[Dict], bool]:
        """
        Detect faces with accessories (sunglasses, etc.)
        
        Returns:
            Tuple of (detections, accessories_detected)
        """
        
    def detect_in_low_light(
        self, 
        image: np.ndarray
    ) -> List[Dict]:
        """Detect faces in low-light conditions with aggressive enhancement"""
        
    def detect_partial_faces(
        self, 
        image: np.ndarray
    ) -> List[Dict]:
        """Detect partially visible faces"""
        
    def preprocess_for_accessories(
        self, 
        image: np.ndarray
    ) -> np.ndarray:
        """Preprocess image to handle accessories"""
        
    def preprocess_for_low_light(
        self, 
        image: np.ndarray
    ) -> np.ndarray:
        """Aggressive preprocessing for low-light images"""
```

## Data Models

### UserEncodingRecord

```python
@dataclass
class UserEncodingRecord:
    """Record of user's multi-angle face encodings"""
    user_id: str
    encodings: Dict[str, np.ndarray]  # {'center': array, 'left': array, 'right': array}
    capture_metadata: Dict[str, Any]  # Quality scores, timestamps, etc.
    created_at: datetime
    updated_at: datetime
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for storage"""
        
    @classmethod
    def from_dict(cls, data: Dict) -> 'UserEncodingRecord':
        """Create from dictionary"""
```

### ScanningSession

```python
@dataclass
class ScanningSession:
    """Represents an active scanning session"""
    session_id: str
    user_id: str
    current_stage: str
    stages_completed: List[str]
    captured_encodings: Dict[str, np.ndarray]
    quality_scores: Dict[str, float]
    retry_counts: Dict[str, int]
    started_at: datetime
    status: str  # 'in_progress', 'completed', 'cancelled', 'failed'
```

### MatchResult

```python
@dataclass
class MatchResult:
    """Result of face matching operation"""
    user_id: str
    confidence_score: float
    matched_angles: List[str]  # Which angles contributed to match
    individual_distances: Dict[str, float]  # Distance for each angle
    weighted_distance: float
    input_angle_estimate: str
    match_quality: str  # 'high', 'medium', 'low'
```

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system-essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: Sequential stage completion

*For any* scanning session, when a stage is successfully completed, the system should only advance to the next stage in the sequence (center → left → right), and should not skip stages or proceed out of order.

**Validates: Requirements 1.1, 1.4, 1.6**

### Property 2: Complete encoding set requirement

*For any* user enrollment, when the scanning process completes successfully, the system should have exactly three encodings stored (center, left, right), each properly labeled with its angle.

**Validates: Requirements 1.3, 1.5, 1.7, 1.8, 3.2, 3.3**

### Property 3: Progress indicator accuracy

*For any* scanning stage, the displayed progress indicator should correctly show the current step number (1, 2, or 3) and the total number of steps (3).

**Validates: Requirements 2.1**

### Property 4: Retry preserves completed stages

*For any* scanning session where a stage fails and retry is initiated, all previously completed stages should remain intact and should not require re-capture.

**Validates: Requirements 2.3**

### Property 5: Multi-angle matching coverage

*For any* face matching operation, the system should compare the input encoding against all three stored angle encodings (center, left, right) for each user.

**Validates: Requirements 4.1, 7.1**

### Property 6: Angle-appropriate weighting

*For any* face matching operation where the input face angle is detected as frontal, the center encoding should receive the highest weight in the matching calculation.

**Validates: Requirements 7.3**

### Property 7: Profile weighting priority

*For any* face matching operation where the input face is detected as a left or right profile, the corresponding profile encoding should receive the highest weight in the matching calculation.

**Validates: Requirements 4.2, 7.4**

### Property 8: Confidence score bounds

*For any* face matching operation that produces a match, the confidence score should be a value between 0 and 100 inclusive.

**Validates: Requirements 4.4, 5.4**

### Property 9: Tolerance threshold enforcement

*For any* face matching operation with a configured tolerance threshold, a match should only be returned when the weighted distance is less than or equal to the tolerance value.

**Validates: Requirements 7.5, 8.3**

### Property 10: Encoding persistence

*For any* user with successfully captured encodings, retrieving the encodings from storage should return the same three angle encodings that were originally stored.

**Validates: Requirements 3.5**

### Property 11: Session cancellation cleanup

*For any* scanning session that is cancelled, all partial data should be removed and the system should return to the initial state with no residual session data.

**Validates: Requirements 9.5**

### Property 12: Robust detection fallback

*For any* image where the primary detection algorithm fails to detect faces, the system should attempt detection using at least one fallback algorithm before reporting failure.

**Validates: Requirements 6.2**

## Error Handling

### Error Categories

1. **Detection Errors**
   - No face detected in frame
   - Multiple faces detected
   - Face quality insufficient (too dark, too blurry, wrong size)
   - Wrong angle detected for current stage

2. **Encoding Errors**
   - Failed to generate encoding from detected face
   - Encoding generation timeout
   - Invalid encoding format

3. **Storage Errors**
   - Failed to write encodings to storage
   - Storage path inaccessible
   - Corrupted encoding data on read
   - Insufficient storage space

4. **Matching Errors**
   - No stored encodings available for comparison
   - Invalid input encoding format
   - Matching algorithm failure

### Error Handling Strategies

**Detection Errors:**
- Provide real-time feedback to guide user
- Allow unlimited retries with clear instructions
- Implement timeout with retry option (30 seconds per stage)
- Log detection failures for debugging

**Encoding Errors:**
- Retry encoding generation up to 3 times
- If persistent failure, allow stage retry
- Log encoding errors with frame metadata
- Preserve captured frame for manual review

**Storage Errors:**
- Implement retry logic with exponential backoff
- Keep encodings in memory during retry attempts
- Provide option to export encodings for manual backup
- Alert user if storage consistently fails

**Matching Errors:**
- Return empty match list rather than crashing
- Log matching errors with input details
- Provide fallback to standard single-encoding matching
- Alert administrator if matching consistently fails

### Recovery Mechanisms

1. **Stage-Level Recovery**: Failed stage can be retried without restarting entire session
2. **Session Persistence**: Session state saved periodically to allow recovery from crashes
3. **Partial Enrollment**: If only 2 angles captured, allow completion later
4. **Encoding Validation**: Validate encodings before storage, reject invalid data
5. **Graceful Degradation**: If multi-angle matching fails, fall back to single-angle matching

## Testing Strategy

### Unit Testing

Unit tests will verify specific examples and edge cases:

**Scanner Component Tests:**
- Test stage progression with valid captures
- Test retry logic for failed stages
- Test session cancellation and cleanup
- Test quality validation thresholds
- Test angle detection accuracy with known poses

**Encoding Manager Tests:**
- Test storage and retrieval of encodings
- Test handling of corrupted data
- Test concurrent access to storage
- Test export/import functionality
- Test deletion of user encodings

**Matcher Component Tests:**
- Test weighted distance calculation
- Test angle estimation from landmarks
- Test tolerance threshold enforcement
- Test confidence score calculation
- Test handling of missing angles

**Edge Cases:**
- Empty storage (no users enrolled)
- Single user enrolled
- Identical twins (should have different encodings)
- Same user re-enrolling (should update, not duplicate)
- Partial encoding sets (missing one angle)

### Property-Based Testing

Property-based tests will verify universal properties across all inputs using the **Hypothesis** library for Python.

**Test Configuration:**
- Minimum 100 iterations per property test
- Use custom strategies for generating face encodings, landmarks, and angles
- Tag each test with corresponding correctness property

**Property Test Generators:**

```python
# Custom strategies for property testing
@st.composite
def face_encoding_strategy(draw):
    """Generate valid face encoding (128-dimensional normalized vector)"""
    encoding = draw(st.lists(
        st.floats(min_value=-1.0, max_value=1.0, allow_nan=False),
        min_size=128,
        max_size=128
    ))
    # Normalize
    arr = np.array(encoding)
    return arr / np.linalg.norm(arr)

@st.composite
def multi_angle_encodings_strategy(draw):
    """Generate complete set of multi-angle encodings"""
    return {
        'center': draw(face_encoding_strategy()),
        'left': draw(face_encoding_strategy()),
        'right': draw(face_encoding_strategy())
    }

@st.composite
def face_landmarks_strategy(draw):
    """Generate valid face landmarks dictionary"""
    # Simplified landmark generation
    return {
        'nose_tip': [(draw(st.integers(100, 200)), draw(st.integers(100, 200)))],
        'left_eye': [(draw(st.integers(80, 120)), draw(st.integers(80, 120))) for _ in range(6)],
        'right_eye': [(draw(st.integers(180, 220)), draw(st.integers(80, 120))) for _ in range(6)]
    }

@st.composite
def scanning_session_strategy(draw):
    """Generate valid scanning session state"""
    stages = ['center', 'left', 'right']
    completed = draw(st.lists(st.sampled_from(stages), unique=True, max_size=3))
    return {
        'current_stage': draw(st.sampled_from(stages)),
        'stages_completed': completed,
        'captured_encodings': {stage: draw(face_encoding_strategy()) for stage in completed}
    }
```

**Property Test Implementation:**

Each correctness property will be implemented as a property-based test:

```python
# Example property test structure
@given(session=scanning_session_strategy())
def test_property_1_sequential_stage_completion(session):
    """
    Feature: multi-angle-face-recognition, Property 1: Sequential stage completion
    
    For any scanning session, when a stage is successfully completed,
    the system should only advance to the next stage in the sequence.
    """
    scanner = MultiAngleFaceScanner()
    # Test implementation
    ...

@given(
    user_encodings=multi_angle_encodings_strategy(),
    input_encoding=face_encoding_strategy(),
    tolerance=st.floats(min_value=0.3, max_value=0.8)
)
def test_property_9_tolerance_threshold_enforcement(user_encodings, input_encoding, tolerance):
    """
    Feature: multi-angle-face-recognition, Property 9: Tolerance threshold enforcement
    
    For any face matching operation with a configured tolerance threshold,
    a match should only be returned when the weighted distance is less than or equal to the tolerance.
    """
    matcher = WeightedFaceMatcher(tolerance=tolerance)
    # Test implementation
    ...
```

### Integration Testing

Integration tests will verify component interactions:

- End-to-end scanning session (UI → Scanner → Storage)
- Photo processing with multi-angle matching
- Robust detection with multiple algorithms
- Storage persistence across application restarts
- API endpoints for scanning and matching

### Performance Testing

- Scanning session completion time (target: < 30 seconds)
- Matching speed with 1000+ enrolled users (target: < 500ms per photo)
- Storage I/O performance
- Memory usage during scanning and matching
- Concurrent session handling

## Implementation Notes

### Technology Stack

- **Language**: Python 3.8+
- **Face Detection**: OpenCV, dlib, MTCNN
- **Face Recognition**: face_recognition library
- **Storage**: JSON files with base64-encoded encodings
- **Testing**: pytest, Hypothesis (property-based testing)
- **API**: Flask REST endpoints

### Dependencies

```
face_recognition>=1.3.0
opencv-python>=4.5.0
numpy>=1.19.0
mtcnn>=0.1.1
dlib>=19.22.0
hypothesis>=6.0.0  # For property-based testing
pytest>=7.0.0
```

### Performance Considerations

1. **Encoding Generation**: ~200ms per angle on modern CPU
2. **Matching**: O(n) where n = number of enrolled users
3. **Storage**: JSON format for portability, consider binary format for large deployments
4. **Caching**: Cache frequently matched users in memory
5. **Parallel Processing**: Use multiprocessing for batch photo processing

### Security Considerations

1. **Encoding Storage**: Encrypt encodings at rest
2. **Session Management**: Implement session timeouts
3. **Access Control**: Authenticate API endpoints
4. **Data Privacy**: Allow users to delete their encodings
5. **Audit Logging**: Log all enrollment and matching operations

### Migration from Existing System

The existing `LiveFaceScanner` and `FaceRecognitionModel` will be extended rather than replaced:

1. **Backward Compatibility**: Support both single-encoding and multi-angle matching
2. **Gradual Migration**: Allow users to re-enroll with multi-angle scanning
3. **Data Migration**: Convert existing single encodings to center-only multi-angle format
4. **Feature Flag**: Enable/disable multi-angle features via configuration

### Future Enhancements

1. **Video-Based Enrollment**: Capture all angles from continuous video
2. **3D Face Modeling**: Generate 3D face model from multi-angle captures
3. **Liveness Detection**: Prevent spoofing with photo/video
4. **Age Progression**: Update encodings as users age
5. **Expression Invariance**: Handle different facial expressions
