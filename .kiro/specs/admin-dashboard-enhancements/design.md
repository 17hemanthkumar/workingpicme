# Design Document: Admin Dashboard Enhancements

## Overview

This design document outlines the architecture and implementation approach for simplifying the admin dashboard by consolidating event photo management directly within the Events section, removing redundant navigation items, and adding event cover thumbnail functionality. The solution maintains all existing functionality while providing a more streamlined admin experience.

### Key Design Goals

1. Simplify admin navigation by removing redundant sections (Home, Events, My Photos)
2. Consolidate photo management within event cards for direct access
3. Add event cover thumbnail upload and display functionality
4. Enable photo deletion with proper cleanup of storage and database
5. Maintain backward compatibility with existing features
6. Preserve security and admin-only access controls

## Architecture

### System Components

The system follows the existing Flask-based architecture with the following components:

```
┌─────────────────────────────────────────────────────────────┐
│                     Frontend Layer                           │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  event_organizer.html (Admin Dashboard)              │  │
│  │  - Simplified Navigation                             │  │
│  │  - Event Cards with Photo Management                 │  │
│  │  - Cover Thumbnail Display                           │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                     Backend Layer (Flask)                    │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  API Endpoints                                        │  │
│  │  - GET /api/events/:id/photos (new)                  │  │
│  │  - DELETE /api/events/:id/photos/:filename (new)     │  │
│  │  - POST /api/events/:id/thumbnail (new)              │  │
│  │  - PUT /api/events/:id/thumbnail (new)               │  │
│  │  - POST /api/create_event (modified)                 │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                     Data Layer                               │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  events_data.json (modified)                         │  │
│  │  - Add cover_thumbnail field                         │  │
│  │                                                       │  │
│  │  File System                                         │  │
│  │  - uploads/event_*/                                  │  │
│  │  - processed/event_*/                                │  │
│  │  - uploads/thumbnails/ (new)                         │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

## Components and Interfaces

### 1. Frontend Components

#### 1.1 Simplified Navigation Bar

**Location:** `frontend/pages/event_organizer.html`

**Changes:**
- Remove navigation links: Home, Events, My Photos
- Keep: My Dashboard, Organization Name, Logout button
- Maintain responsive design and styling

**HTML Structure:**
```html
<nav class="bg-white/90 backdrop-blur-md border-b border-gray-200 shadow-sm sticky top-0 z-50">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between items-center h-16">
            <a href="/event_organizer" class="flex items-center space-x-2">
                <!-- Logo -->
            </a>
            <div class="flex items-center space-x-4">
                <span class="text-sm text-gray-600">{{ organization_name }}</span>
                <a href="/admin/logout" class="px-4 py-2 rounded-md">Logout</a>
            </div>
        </div>
    </div>
</nav>
```

#### 1.2 Event Card with Photo Management

**Location:** `frontend/pages/event_organizer.html`

**New Features:**
- Cover thumbnail display
- "View Photos" expandable section
- Photo grid with delete buttons
- "Edit Thumbnail" button

**Component Structure:**
```html
<div class="event-card">
    <!-- Cover Thumbnail -->
    <img src="{{ event.cover_thumbnail }}" class="event-cover" />
    
    <!-- Event Details -->
    <div class="event-info">...</div>
    
    <!-- Photo Management Section -->
    <div class="photo-management">
        <button onclick="togglePhotos(eventId)">View Photos</button>
        <div id="photos-{{ event.id }}" class="photos-grid hidden">
            <!-- Photos loaded dynamically -->
        </div>
    </div>
    
    <!-- Upload Section -->
    <form class="upload-form">...</form>
    
    <!-- Thumbnail Management -->
    <button onclick="editThumbnail(eventId)">Edit Thumbnail</button>
</div>
```

#### 1.3 Photo Grid Component

**Functionality:**
- Display photos in responsive grid (3-4 columns desktop, 2 tablet, 1 mobile)
- Show delete button on hover
- Confirm before deletion
- Update UI after deletion

**JavaScript Functions:**
```javascript
async function loadEventPhotos(eventId) {
    // Fetch photos from API
    // Render in grid with delete buttons
}

async function deletePhoto(eventId, filename) {
    // Confirm deletion
    // Call DELETE API
    // Remove from UI
    // Update photo count
}
```

### 2. Backend Components

#### 2.1 New API Endpoints

##### GET /api/events/:event_id/photos

**Purpose:** Retrieve all photos for a specific event

**Authentication:** Admin required

**Response:**
```json
{
    "success": true,
    "event_id": "event_abc123",
    "photos": [
        {
            "filename": "photo1.jpg",
            "url": "/uploads/event_abc123/photo1.jpg",
            "type": "uploaded",
            "size": 1024000,
            "uploaded_at": "2025-11-10T10:30:00"
        }
    ],
    "total_count": 42
}
```

**Implementation:**
```python
@app.route('/api/events/<event_id>/photos', methods=['GET'])
@admin_required
def get_event_photos(event_id):
    # Verify event exists
    # List files in uploads/event_id/
    # Exclude QR codes
    # Return photo metadata
```

##### DELETE /api/events/:event_id/photos/:filename

**Purpose:** Delete a specific photo from an event

**Authentication:** Admin required

**Request:** No body required

**Response:**
```json
{
    "success": true,
    "message": "Photo deleted successfully",
    "deleted_file": "photo1.jpg"
}
```

**Implementation:**
```python
@app.route('/api/events/<event_id>/photos/<filename>', methods=['DELETE'])
@admin_required
def delete_event_photo(event_id, filename):
    # Verify admin owns the event
    # Delete from uploads/event_id/filename
    # Delete from processed/event_id/*/individual/filename
    # Delete from processed/event_id/*/group/watermarked_filename
    # Update events_data.json photo count
    # Return success
```

**File Deletion Logic:**
1. Check if file exists in uploads directory
2. Delete from uploads/event_id/
3. Search and delete from all processed subdirectories
4. Handle errors gracefully (log but don't fail if file not found)
5. Update photo count in events_data.json

##### POST /api/events/:event_id/thumbnail

**Purpose:** Upload a cover thumbnail for an event

**Authentication:** Admin required

**Request:** Multipart form data with 'thumbnail' file

**Response:**
```json
{
    "success": true,
    "message": "Thumbnail uploaded successfully",
    "thumbnail_url": "/uploads/thumbnails/event_abc123_thumb.jpg"
}
```

**Implementation:**
```python
@app.route('/api/events/<event_id>/thumbnail', methods=['POST'])
@admin_required
def upload_event_thumbnail(event_id):
    # Validate file is image
    # Generate unique filename
    # Save to uploads/thumbnails/
    # Update events_data.json with thumbnail path
    # Return thumbnail URL
```

##### PUT /api/events/:event_id/thumbnail

**Purpose:** Update/replace an existing event thumbnail

**Authentication:** Admin required

**Request:** Multipart form data with 'thumbnail' file

**Response:**
```json
{
    "success": true,
    "message": "Thumbnail updated successfully",
    "thumbnail_url": "/uploads/thumbnails/event_abc123_thumb_v2.jpg"
}
```

**Implementation:**
```python
@app.route('/api/events/<event_id>/thumbnail', methods=['PUT'])
@admin_required
def update_event_thumbnail(event_id):
    # Delete old thumbnail file
    # Upload new thumbnail
    # Update events_data.json
    # Return new thumbnail URL
```

#### 2.2 Modified API Endpoints

##### POST /api/create_event (Modified)

**Changes:**
- Accept optional 'thumbnail' file in multipart form data
- Save thumbnail if provided
- Store thumbnail path in event data

**Updated Implementation:**
```python
@app.route('/api/create_event', methods=['POST'])
@admin_required
def create_event():
    # Parse form data (not JSON anymore)
    # Create event as before
    # If thumbnail provided:
    #   - Validate and save thumbnail
    #   - Add thumbnail_url to event data
    # Else:
    #   - Use default placeholder
    # Save to events_data.json
```

### 3. Data Models

#### 3.1 Event Data Structure (Modified)

**File:** `backend/events_data.json`

**Updated Schema:**
```json
{
    "id": "event_abc123",
    "name": "Summer Festival 2025",
    "location": "San Francisco, CA",
    "date": "2025-07-15",
    "category": "Festival",
    "image": "/static/images/default_event.jpg",
    "cover_thumbnail": "/uploads/thumbnails/event_abc123_thumb.jpg",  // NEW
    "photos_count": 42,
    "qr_code": "/api/qr_code/event_abc123",
    "created_by": 1,
    "organization_name": "EventCo Inc",
    "created_at": "2025-11-10T10:00:00"
}
```

**New Field:**
- `cover_thumbnail` (string, nullable): Path to the event's cover thumbnail image
  - Default: `/static/images/default_event_thumbnail.jpg`
  - Format: `/uploads/thumbnails/{event_id}_thumb_{timestamp}.{ext}`

#### 3.2 Photo Metadata Structure

**Purpose:** Track photo information for display and management

**Structure:**
```javascript
{
    filename: "abc123_photo.jpg",
    url: "/uploads/event_abc123/abc123_photo.jpg",
    type: "uploaded",  // or "processed"
    size: 1024000,  // bytes
    uploaded_at: "2025-11-10T10:30:00"
}
```

### 4. File System Structure

#### 4.1 Current Structure
```
uploads/
├── event_abc123/
│   ├── photo1.jpg
│   ├── photo2.jpg
│   └── event_abc123_qr.png
└── event_xyz789/
    └── ...

processed/
├── event_abc123/
│   ├── person_001/
│   │   ├── individual/
│   │   │   └── photo1.jpg
│   │   └── group/
│   │       └── watermarked_photo2.jpg
│   └── person_002/
│       └── ...
└── event_xyz789/
    └── ...
```

#### 4.2 New Structure (with thumbnails)
```
uploads/
├── event_abc123/
│   ├── photo1.jpg
│   ├── photo2.jpg
│   └── event_abc123_qr.png
├── event_xyz789/
│   └── ...
└── thumbnails/              // NEW
    ├── event_abc123_thumb.jpg
    ├── event_xyz789_thumb.png
    └── default_event_thumbnail.jpg

processed/
└── (unchanged)
```

## Error Handling

### 1. Photo Deletion Errors

**Scenarios:**
- File not found in uploads
- File not found in processed
- Permission denied
- Disk I/O error

**Handling Strategy:**
```python
def delete_photo_with_cleanup(event_id, filename):
    errors = []
    
    # Try to delete from uploads
    try:
        upload_path = os.path.join(UPLOAD_FOLDER, event_id, filename)
        if os.path.exists(upload_path):
            os.remove(upload_path)
    except Exception as e:
        errors.append(f"Upload deletion failed: {e}")
    
    # Try to delete from processed (all person directories)
    try:
        processed_event_dir = os.path.join(PROCESSED_FOLDER, event_id)
        if os.path.exists(processed_event_dir):
            for person_id in os.listdir(processed_event_dir):
                # Delete from individual
                individual_path = os.path.join(processed_event_dir, person_id, "individual", filename)
                if os.path.exists(individual_path):
                    os.remove(individual_path)
                
                # Delete from group (with watermark prefix)
                group_path = os.path.join(processed_event_dir, person_id, "group", f"watermarked_{filename}")
                if os.path.exists(group_path):
                    os.remove(group_path)
    except Exception as e:
        errors.append(f"Processed deletion failed: {e}")
    
    # Log errors but don't fail the request
    if errors:
        print(f"Photo deletion warnings: {errors}")
    
    return len(errors) == 0
```

### 2. Thumbnail Upload Errors

**Scenarios:**
- Invalid file type
- File too large
- Disk space full
- Permission denied

**Validation:**
```python
ALLOWED_THUMBNAIL_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif'}
MAX_THUMBNAIL_SIZE = 5 * 1024 * 1024  # 5MB

def validate_thumbnail(file):
    # Check file extension
    if not allowed_file(file.filename):
        return False, "Invalid file type. Use JPG, PNG, or GIF"
    
    # Check file size
    file.seek(0, os.SEEK_END)
    size = file.tell()
    file.seek(0)
    
    if size > MAX_THUMBNAIL_SIZE:
        return False, "File too large. Maximum 5MB"
    
    return True, None
```

### 3. API Error Responses

**Standard Error Format:**
```json
{
    "success": false,
    "error": "Descriptive error message",
    "error_code": "PHOTO_NOT_FOUND",
    "details": {
        "event_id": "event_abc123",
        "filename": "photo1.jpg"
    }
}
```

**HTTP Status Codes:**
- 400: Bad Request (invalid input)
- 401: Unauthorized (not logged in)
- 403: Forbidden (not admin)
- 404: Not Found (event or photo doesn't exist)
- 409: Conflict (duplicate thumbnail)
- 500: Internal Server Error

## Testing Strategy

### 1. Unit Tests

**Backend Tests:**
```python
# test_photo_management.py

def test_get_event_photos_success():
    # Test retrieving photos for valid event
    pass

def test_get_event_photos_empty():
    # Test event with no photos
    pass

def test_delete_photo_success():
    # Test successful photo deletion
    pass

def test_delete_photo_not_found():
    # Test deleting non-existent photo
    pass

def test_upload_thumbnail_success():
    # Test successful thumbnail upload
    pass

def test_upload_thumbnail_invalid_type():
    # Test uploading invalid file type
    pass

def test_update_thumbnail_success():
    # Test replacing existing thumbnail
    pass
```

**Frontend Tests:**
```javascript
// test_event_card.js

describe('Event Photo Management', () => {
    test('loads photos when View Photos clicked', async () => {
        // Test photo loading
    });
    
    test('deletes photo with confirmation', async () => {
        // Test photo deletion flow
    });
    
    test('updates UI after deletion', async () => {
        // Test UI update
    });
});
```

### 2. Integration Tests

**Test Scenarios:**
1. Create event with thumbnail → Verify thumbnail saved and displayed
2. Upload photos → View photos → Delete photo → Verify removal
3. Edit thumbnail → Verify old thumbnail deleted and new one displayed
4. Delete event → Verify all photos and thumbnail cleaned up
5. Non-admin access → Verify 403 errors

### 3. Manual Testing Checklist

**Navigation:**
- [ ] Verify Home, Events, My Photos links removed
- [ ] Verify My Dashboard link works
- [ ] Verify logout works
- [ ] Verify responsive design on mobile

**Event Creation:**
- [ ] Create event without thumbnail (uses default)
- [ ] Create event with thumbnail (displays correctly)
- [ ] Verify thumbnail appears on event card

**Photo Management:**
- [ ] Click "View Photos" expands photo grid
- [ ] Photos display in responsive grid
- [ ] Delete button appears on hover
- [ ] Confirm dialog shows before deletion
- [ ] Photo removed from UI after deletion
- [ ] Photo count updates after deletion

**Thumbnail Management:**
- [ ] Click "Edit Thumbnail" shows upload dialog
- [ ] Upload new thumbnail replaces old one
- [ ] Invalid file types rejected
- [ ] Large files rejected

**Error Handling:**
- [ ] Network errors show user-friendly messages
- [ ] Invalid operations show appropriate errors
- [ ] Non-admin access blocked

## Security Considerations

### 1. Authentication and Authorization

**Admin-Only Access:**
- All photo management endpoints require `@admin_required` decorator
- Verify admin session before processing requests
- Check admin owns the event before allowing modifications

**Session Validation:**
```python
def verify_admin_owns_event(event_id):
    admin_id = session.get('admin_id')
    events_data = get_events_cached()
    event = next((e for e in events_data if e['id'] == event_id), None)
    
    if not event:
        return False, "Event not found"
    
    if event.get('created_by') != admin_id:
        return False, "Unauthorized: You don't own this event"
    
    return True, None
```

### 2. File Upload Security

**Validation:**
- Whitelist allowed file extensions
- Validate file MIME types
- Limit file sizes
- Sanitize filenames using `secure_filename()`
- Generate unique filenames to prevent overwrites

**Path Traversal Prevention:**
```python
def safe_file_path(base_dir, event_id, filename):
    # Sanitize inputs
    event_id = secure_filename(event_id)
    filename = secure_filename(filename)
    
    # Build path
    full_path = os.path.join(base_dir, event_id, filename)
    
    # Verify path is within base directory
    if not os.path.abspath(full_path).startswith(os.path.abspath(base_dir)):
        raise ValueError("Invalid path")
    
    return full_path
```

### 3. Data Integrity

**Atomic Operations:**
- Update events_data.json atomically (write to temp file, then rename)
- Rollback on errors
- Validate JSON before writing

**Backup Strategy:**
```python
def update_events_data_safe(events_data):
    # Write to temporary file
    temp_path = EVENTS_DATA_PATH + '.tmp'
    with open(temp_path, 'w') as f:
        json.dump(events_data, f, indent=2)
    
    # Backup current file
    if os.path.exists(EVENTS_DATA_PATH):
        backup_path = EVENTS_DATA_PATH + '.backup'
        shutil.copy(EVENTS_DATA_PATH, backup_path)
    
    # Rename temp to actual
    os.replace(temp_path, EVENTS_DATA_PATH)
```

## Performance Considerations

### 1. Photo Loading Optimization

**Lazy Loading:**
- Load photos only when "View Photos" is clicked
- Use pagination for events with many photos (>50)
- Implement virtual scrolling for large photo grids

**Caching:**
```python
@cache.cached(timeout=300, key_prefix='event_photos')
def get_event_photos_cached(event_id):
    # Cache photo list for 5 minutes
    pass
```

### 2. Thumbnail Optimization

**Image Processing:**
- Resize thumbnails to standard dimensions (e.g., 400x300)
- Compress thumbnails to reduce file size
- Use WebP format for better compression (with fallback)

**Implementation:**
```python
from PIL import Image

def create_optimized_thumbnail(file, max_size=(400, 300)):
    img = Image.open(file)
    img.thumbnail(max_size, Image.LANCZOS)
    
    # Save as WebP with quality 85
    output_path = f"thumbnail_{uuid.uuid4().hex}.webp"
    img.save(output_path, 'WEBP', quality=85)
    
    return output_path
```

### 3. Deletion Performance

**Batch Operations:**
- Delete files asynchronously to avoid blocking
- Use background tasks for cleanup
- Implement retry logic for failed deletions

**Background Deletion:**
```python
import threading

def delete_photo_async(event_id, filename):
    def _delete():
        delete_photo_with_cleanup(event_id, filename)
    
    thread = threading.Thread(target=_delete)
    thread.start()
```

## Migration Strategy

### 1. Database Migration

**Add cover_thumbnail field to existing events:**

```python
# migration_add_thumbnails.py

def migrate_events_data():
    with open(EVENTS_DATA_PATH, 'r') as f:
        events_data = json.load(f)
    
    # Add cover_thumbnail field to all events
    for event in events_data:
        if 'cover_thumbnail' not in event:
            event['cover_thumbnail'] = '/static/images/default_event_thumbnail.jpg'
    
    # Save updated data
    with open(EVENTS_DATA_PATH, 'w') as f:
        json.dump(events_data, f, indent=2)
    
    print(f"Migrated {len(events_data)} events")
```

### 2. File System Setup

**Create thumbnails directory:**
```python
def setup_thumbnail_directory():
    thumbnail_dir = os.path.join(UPLOAD_FOLDER, 'thumbnails')
    os.makedirs(thumbnail_dir, exist_ok=True)
    
    # Copy default thumbnail
    default_src = 'static/images/default_event_thumbnail.jpg'
    default_dst = os.path.join(thumbnail_dir, 'default_event_thumbnail.jpg')
    if not os.path.exists(default_dst):
        shutil.copy(default_src, default_dst)
```

### 3. Backward Compatibility

**Graceful Degradation:**
- If cover_thumbnail is missing, use default
- If thumbnail file doesn't exist, use placeholder
- Old events without thumbnails continue to work

## Implementation Notes

### 1. Frontend JavaScript Organization

**Recommended Structure:**
```javascript
// Event Photo Management Module
const EventPhotoManager = {
    async loadPhotos(eventId) { ... },
    async deletePhoto(eventId, filename) { ... },
    renderPhotoGrid(photos) { ... },
    showDeleteConfirmation(filename) { ... }
};

// Thumbnail Management Module
const ThumbnailManager = {
    async uploadThumbnail(eventId, file) { ... },
    async updateThumbnail(eventId, file) { ... },
    showUploadDialog(eventId) { ... }
};
```

### 2. CSS Styling Guidelines

**Photo Grid:**
```css
.photos-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
    gap: 1rem;
    padding: 1rem;
}

.photo-item {
    position: relative;
    aspect-ratio: 1;
    overflow: hidden;
    border-radius: 0.5rem;
}

.photo-item:hover .delete-button {
    opacity: 1;
}

.delete-button {
    position: absolute;
    top: 0.5rem;
    right: 0.5rem;
    opacity: 0;
    transition: opacity 0.2s;
}
```

### 3. API Response Caching

**Cache Invalidation Strategy:**
- Invalidate event photos cache when photo uploaded/deleted
- Invalidate events list cache when event created/deleted
- Use cache keys with event_id for granular control

```python
def invalidate_event_cache(event_id):
    cache.delete(f'event_photos_{event_id}')
    cache.delete('view//api/events')
```

## Thumbnail Synchronization Across User Pages

### Problem Statement

Currently, the system stores event thumbnails in the `cover_thumbnail` field, but user-facing pages (event_discovery.html, homepage.html, event_detail.html) display the `image` field instead. This causes a disconnect where admin thumbnail updates don't reflect on user pages.

### Solution Design

**Approach 1: Update User Pages to Use cover_thumbnail (Recommended)**

Modify all user-facing pages to use `event.cover_thumbnail` instead of `event.image`:

**Files to Update:**
1. `frontend/pages/event_discovery.html` - Event cards in discovery grid
2. `frontend/pages/homepage.html` - Featured events section
3. `frontend/pages/event_detail.html` - Event header (if applicable)

**Changes Required:**
```javascript
// Before:
<img src="${event.image || '/static/images/default_event.jpg'}" ...>

// After:
<img src="${event.cover_thumbnail || '/static/images/default_event_thumbnail.jpg'}" ...>
```

**Approach 2: Sync cover_thumbnail to image field (Alternative)**

When admin uploads/updates thumbnail, also update the `image` field:

```python
# In thumbnail upload/update endpoints
event['image'] = thumbnail_url
event['cover_thumbnail'] = thumbnail_url
```

**Recommendation:** Use Approach 1 as it maintains clear separation between the legacy `image` field and the new `cover_thumbnail` field, making the codebase more maintainable.

### Implementation Details

**1. Event Discovery Page**
- Location: `frontend/pages/event_discovery.html`
- Update the event card template in the `displayEvents()` function
- Change image source from `event.image` to `event.cover_thumbnail`

**2. Homepage Featured Events**
- Location: `frontend/pages/homepage.html`
- Update the `loadFeaturedEvents()` function
- Change image source in the event card template

**3. Event Detail Page**
- Location: `frontend/pages/event_detail.html`
- If event thumbnail is displayed, update to use `cover_thumbnail`
- Ensure fallback to default thumbnail if not set

### Fallback Strategy

All pages must handle missing thumbnails gracefully:

```javascript
const thumbnailUrl = event.cover_thumbnail || '/static/images/default_event_thumbnail.jpg';
```

### Testing Checklist

- [ ] Admin uploads thumbnail → Verify appears on event discovery page
- [ ] Admin uploads thumbnail → Verify appears on homepage featured events
- [ ] Admin updates thumbnail → Verify change reflects on all user pages
- [ ] Event without thumbnail → Verify default placeholder shows on all pages
- [ ] Test with browser cache cleared to ensure no caching issues

## Deployment Checklist

- [ ] Run database migration script
- [ ] Create thumbnails directory
- [ ] Copy default thumbnail image
- [ ] Update frontend templates
- [ ] Deploy backend API changes
- [ ] Test all endpoints
- [ ] Verify admin authentication
- [ ] Test photo deletion cleanup
- [ ] Verify thumbnail upload/update
- [ ] Test responsive design
- [ ] Monitor error logs
- [ ] Backup events_data.json before deployment
