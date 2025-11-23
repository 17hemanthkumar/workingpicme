# Requirements Document

## Introduction

The Enhanced Multi-Angle Face Detection System is an advanced face recognition platform designed to detect, analyze, and match faces from multiple angles. The system will process uploaded photos to detect faces, extract deep facial features, store multi-angle encodings, and enable real-time face scanning with instant photo retrieval capabilities.

## Glossary

- **System**: The Enhanced Multi-Angle Face Detection System
- **Face Detection**: The process of identifying and locating faces in images
- **Face Encoding**: A 128-dimensional numerical representation of a face
- **Multi-Angle**: Support for frontal, profile (45°), and side (90°) face views
- **Quality Score**: A numerical assessment of face image quality based on blur, lighting, and size
- **Person**: An individual identified in the system with one or more face encodings
- **Live Scanner**: Real-time webcam-based face capture and matching component
- **Facial Features**: Detailed measurements including eye distance, nose dimensions, jaw width, facial hair, and glasses
- **Group Photo**: A photo containing multiple detected faces
- **Individual Photo**: A photo containing a single detected face

## Requirements

### Requirement 1: Multi-Algorithm Face Detection

**User Story:** As a system administrator, I want the system to detect faces using multiple algorithms, so that detection accuracy is maximized across various image conditions.

#### Acceptance Criteria

1. WHEN an image is processed THEN the System SHALL detect faces using MTCNN algorithm
2. WHEN MTCNN fails to detect faces THEN the System SHALL attempt detection using Haar Cascade algorithm
3. WHEN Haar Cascade fails to detect faces THEN the System SHALL attempt detection using HOG algorithm
4. WHEN a face is detected THEN the System SHALL record the detection method used
5. WHEN multiple faces are detected in an image THEN the System SHALL process each face independently

### Requirement 2: Face Angle Estimation

**User Story:** As a system administrator, I want the system to estimate face angles from facial landmarks, so that faces can be categorized and matched appropriately.

#### Acceptance Criteria

1. WHEN a face is detected THEN the System SHALL extract facial landmarks
2. WHEN facial landmarks are extracted THEN the System SHALL estimate the face angle
3. WHEN the face angle is estimated THEN the System SHALL classify it as frontal, left_45, right_45, left_90, or right_90
4. WHEN the angle is classified THEN the System SHALL store the angle classification with the face detection
5. WHEN angle estimation fails THEN the System SHALL default to frontal classification

### Requirement 3: Face Quality Assessment

**User Story:** As a system administrator, I want the system to assess face quality, so that only high-quality encodings are used for matching.

#### Acceptance Criteria

1. WHEN a face is detected THEN the System SHALL calculate a blur score
2. WHEN a face is detected THEN the System SHALL calculate a lighting score
3. WHEN a face is detected THEN the System SHALL calculate a size score
4. WHEN all quality metrics are calculated THEN the System SHALL compute an overall quality score
5. WHEN the quality score is below 0.5 THEN the System SHALL mark the face as low quality

### Requirement 4: Deep Feature Extraction

**User Story:** As a system administrator, I want the system to extract detailed facial features, so that faces can be accurately identified and analyzed.

#### Acceptance Criteria

1. WHEN a face is detected THEN the System SHALL generate a 128-dimensional face encoding
2. WHEN a face is detected THEN the System SHALL extract 68 facial landmark points
3. WHEN landmarks are extracted THEN the System SHALL calculate eye distance
4. WHEN landmarks are extracted THEN the System SHALL measure nose width and height
5. WHEN landmarks are extracted THEN the System SHALL measure jaw width
6. WHEN landmarks are extracted THEN the System SHALL detect presence of facial hair
7. WHEN landmarks are extracted THEN the System SHALL detect presence of glasses

### Requirement 5: Multi-Angle Storage

**User Story:** As a system administrator, I want the system to store multiple face angles per person, so that matching accuracy is improved across different viewing angles.

#### Acceptance Criteria

1. WHEN a person is identified THEN the System SHALL store face encodings for each detected angle
2. WHEN multiple encodings exist for the same angle THEN the System SHALL keep the highest quality encoding
3. WHEN a person has encodings THEN the System SHALL mark the highest quality encoding as primary
4. WHEN storing encodings THEN the System SHALL store up to 5 different angles per person
5. WHEN the angle limit is reached THEN the System SHALL replace the lowest quality encoding if a higher quality one is available

### Requirement 6: Person Management

**User Story:** As a system administrator, I want the system to manage person records, so that individuals can be tracked across multiple photos.

#### Acceptance Criteria

1. WHEN a new face is detected THEN the System SHALL create a new person record with a unique UUID
2. WHEN a face matches an existing person THEN the System SHALL associate the face with that person
3. WHEN a person is associated with a photo THEN the System SHALL update the person's total photo count
4. WHEN a person is associated with a photo THEN the System SHALL update the person's last seen timestamp
5. WHEN a person record is created THEN the System SHALL initialize confidence score to 0.0

### Requirement 7: Enhanced Matching Engine

**User Story:** As a user, I want the system to match faces accurately using multi-angle comparison, so that I can find all photos of a specific person.

#### Acceptance Criteria

1. WHEN a face encoding is provided THEN the System SHALL compare it against all stored person encodings
2. WHEN comparing encodings THEN the System SHALL calculate Euclidean distance for each comparison
3. WHEN multiple angles exist for a person THEN the System SHALL compare against all angles
4. WHEN calculating match confidence THEN the System SHALL weight matches by encoding quality score
5. WHEN calculating match confidence THEN the System SHALL weight matches by angle type
6. WHEN a match distance is below 0.6 THEN the System SHALL consider it a positive match
7. WHEN multiple persons match THEN the System SHALL return the person with the highest confidence score

### Requirement 8: Photo Processing

**User Story:** As a user, I want to upload photos and have them automatically processed, so that faces are detected and stored without manual intervention.

#### Acceptance Criteria

1. WHEN photos are uploaded for an event THEN the System SHALL process each photo sequentially
2. WHEN processing a photo THEN the System SHALL detect all faces in the photo
3. WHEN faces are detected THEN the System SHALL extract features for each face
4. WHEN features are extracted THEN the System SHALL match each face against existing persons
5. WHEN a match is found THEN the System SHALL associate the photo with the matched person
6. WHEN no match is found THEN the System SHALL create a new person record
7. WHEN processing is complete THEN the System SHALL mark the photo as processed
8. WHEN processing fails THEN the System SHALL log the error and continue with remaining photos

### Requirement 9: Live Face Scanning

**User Story:** As a user, I want to scan my face using a webcam and instantly retrieve my photos, so that I can quickly access my event photos.

#### Acceptance Criteria

1. WHEN the live scanner is activated THEN the System SHALL access the default webcam
2. WHEN the webcam is accessed THEN the System SHALL capture a face image
3. WHEN a face is captured THEN the System SHALL validate the quality score is above 0.5
4. WHEN quality is insufficient THEN the System SHALL prompt the user to adjust position
5. WHEN quality is sufficient THEN the System SHALL extract face encoding
6. WHEN encoding is extracted THEN the System SHALL match against the database
7. WHEN a match is found THEN the System SHALL retrieve all photos containing the matched person
8. WHEN retrieving photos THEN the System SHALL separate individual photos from group photos
9. WHEN no match is found THEN the System SHALL inform the user no photos were found

### Requirement 10: Photo Retrieval

**User Story:** As a user, I want to retrieve both individual and group photos of a matched person, so that I can see all photos I appear in.

#### Acceptance Criteria

1. WHEN a person is matched THEN the System SHALL query all photos associated with that person
2. WHEN querying photos THEN the System SHALL identify photos with face_count equal to 1 as individual photos
3. WHEN querying photos THEN the System SHALL identify photos with face_count greater than 1 as group photos
4. WHEN returning results THEN the System SHALL include photo filename, filepath, and match confidence
5. WHEN returning results THEN the System SHALL sort photos by match confidence descending

### Requirement 11: Database Schema

**User Story:** As a system administrator, I want a well-structured database schema, so that data is organized efficiently and queries perform quickly.

#### Acceptance Criteria

1. WHEN the database is initialized THEN the System SHALL create a photos table with event_id, filename, filepath, and processing status
2. WHEN the database is initialized THEN the System SHALL create a persons table with person_uuid, name, and statistics
3. WHEN the database is initialized THEN the System SHALL create a face_detections table with photo_id, person_id, bbox, angle, and quality
4. WHEN the database is initialized THEN the System SHALL create a face_encodings table with person_id, encoding_vector, angle, and quality
5. WHEN the database is initialized THEN the System SHALL create a facial_features table with measurements and attributes
6. WHEN the database is initialized THEN the System SHALL create a person_photos table for photo associations
7. WHEN the database is initialized THEN the System SHALL create indexes on frequently queried columns
8. WHEN the database is initialized THEN the System SHALL enable foreign key constraints

### Requirement 12: API Endpoints

**User Story:** As a frontend developer, I want RESTful API endpoints, so that I can integrate face detection features into the user interface.

#### Acceptance Criteria

1. WHEN a POST request is made to /api/photos/upload THEN the System SHALL accept photo files and event_id
2. WHEN a POST request is made to /api/photos/process-event THEN the System SHALL process all photos for the specified event
3. WHEN a POST request is made to /api/scan/capture THEN the System SHALL capture a face from the webcam
4. WHEN a POST request is made to /api/scan/match THEN the System SHALL match the captured face and return photos
5. WHEN a GET request is made to /api/search/person/{id}/photos THEN the System SHALL return all photos of that person
6. WHEN a POST request is made to /api/search/similar-faces THEN the System SHALL find similar faces in the database
7. WHEN an API error occurs THEN the System SHALL return appropriate HTTP status codes and error messages

### Requirement 13: Performance Requirements

**User Story:** As a user, I want the system to process faces quickly, so that I can get results without long wait times.

#### Acceptance Criteria

1. WHEN detecting faces in a photo THEN the System SHALL complete detection within 500 milliseconds
2. WHEN extracting features from a face THEN the System SHALL complete extraction within 200 milliseconds
3. WHEN matching a face against the database THEN the System SHALL complete matching within 100 milliseconds
4. WHEN retrieving photos for a person THEN the System SHALL complete retrieval within 200 milliseconds
5. WHEN processing a live scan THEN the System SHALL complete the entire workflow within 2 seconds

### Requirement 14: Error Handling

**User Story:** As a system administrator, I want comprehensive error handling, so that the system remains stable and provides useful error information.

#### Acceptance Criteria

1. WHEN a file upload fails THEN the System SHALL return an error message indicating the failure reason
2. WHEN face detection fails THEN the System SHALL log the error and continue processing
3. WHEN database operations fail THEN the System SHALL rollback transactions and return an error
4. WHEN the webcam is unavailable THEN the System SHALL inform the user and suggest troubleshooting steps
5. WHEN an API request is malformed THEN the System SHALL return a 400 Bad Request with validation errors

### Requirement 15: Data Integrity

**User Story:** As a system administrator, I want data integrity constraints, so that the database remains consistent and reliable.

#### Acceptance Criteria

1. WHEN a photo is deleted THEN the System SHALL cascade delete all associated face detections
2. WHEN a person is deleted THEN the System SHALL cascade delete all associated encodings
3. WHEN a face detection is deleted THEN the System SHALL cascade delete associated facial features
4. WHEN inserting duplicate person-photo associations THEN the System SHALL prevent the duplicate insertion
5. WHEN foreign key constraints are violated THEN the System SHALL reject the operation and return an error
