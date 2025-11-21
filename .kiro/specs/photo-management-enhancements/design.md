# Design Document: Photo Management Enhancements

## Overview

This design enhances the photo viewing and management experience in PicMe by adding lightbox preview, download tracking, a downloads section, organization display, and event search functionality.

## Architecture

### Component Overview

```
┌─────────────────────────────────────────────────────────────┐
│                  Photo Management System                     │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────────┐         ┌──────────────────┐          │
│  │  Event Display   │         │  Photo Lightbox  │          │
│  │                  │         │                  │          │
│  │ - Organization   │────────▶│ - Enlarged view  │          │
│  │ - Search filter  │         │ - Download btn   │          │
│  │ - Event cards    │         │ - Navigation     │          │
│  └──────────────────┘         └──────────────────┘          │
│           │                            │                     │
│           │                            │                     │
│           ▼                            ▼                     │
│  ┌──────────────────┐         ┌──────────────────┐          │
│  │  Download API    │         │  Downloads DB    │          │
│  │                  │         │                  │          │
│  │ - Track download │────────▶│ - user_id        │          │
│  │ - Store history  │         │ - photo_url      │          │
│  │ - Prevent dupes  │         │ - event_id       │          │
│  └──────────────────┘         │ - downloaded_at  │          │
│                                └──────────────────┘          │
│                                         │                    │
│                                         ▼                    │
│                                ┌──────────────────┐          │
│                                │  My Downloads    │          │
│                                │                  │          │
│                                │ - Grid display   │          │
│                                │ - Re-download    │          │
│                                │ - Event info     │          │
│                                └──────────────────┘          │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

## Database Schema

### New Table: downloads

```sql
CREATE TABLE downloads (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    photo_url VARCHAR(500) NOT NULL,
    event_id VARCHAR(50) NOT NULL,
    event_name VARCHAR(255) NOT NULL,
    downloaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY unique_download (user_id, photo_url),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_user_downloads (user_id, downloaded_at)
);
```

### Modified: events_data.json Structure

```json
{
  "id": "event_123",
  "name": "Summer Festival",
  "location": "Central Park",
  "date": "2025-07-15",
  "category": "Music",
  "image": "/static/images/default_event.jpg",
  "photos_count": 150,
  "qr_code": "/api/qr_code/event_123",
  "created_by": 5,
  "organization_name": "Tech Events Inc",  // NEW: Added during creation
  "created_at": "2025-11-11T12:00:00"
}
```

## Components and Interfaces

### 1. Photo Lightbox Component

#### HTML Structure
```html
<div id="photo-lightbox" class="hidden fixed inset-0 z-50 bg-black/90">
    <button id="close-lightbox" class="absolute top-4 right-4">×</button>
    <button id="prev-photo" class="absolute left-4 top-1/2">‹</button>
    <button id="next-photo" class="absolute right-4 top-1/2">›</button>
    
    <div class="flex items-center justify-center h-full">
        <img id="lightbox-image" src="" class="max-w-full max-h-full">
    </div>
    
    <div class="absolute bottom-4 left-1/2 transform -translate-x-1/2">
        <button id="download-photo-btn" class="bg-indigo-600 text-white px-6 py-3">
            Download Photo
        </button>
    </div>
</div>
```

#### JavaScript API
```javascript
class PhotoLightbox {
    constructor(photos, currentIndex);
    open(index);
    close();
    next();
    previous();
    downloadCurrent();
}
```

### 2. Download Tracking API

#### POST /api/download-photo
**Purpose:** Track photo download and add to user's download history

**Request:**
```json
{
  "photo_url": "/photos/event_123/all/watermarked_photo.jpg",
  "event_id": "event_123",
  "event_name": "Summer Festival"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Photo added to your downloads",
  "already_downloaded": false
}
```

#### GET /api/my-downloads
**Purpose:** Retrieve user's download history

**Response:**
```json
{
  "success": true,
  "downloads": [
    {
      "id": 1,
      "photo_url": "/photos/event_123/all/photo.jpg",
      "event_id": "event_123",
      "event_name": "Summer Festival",
      "downloaded_at": "2025-11-11T12:00:00"
    }
  ],
  "total": 15
}
```

### 3. My Downloads Page

#### Route: GET /my_downloads
**Purpose:** Display user's downloaded photos

**Template:** my_downloads.html

**Features:**
- Grid layout (responsive)
- Event name display
- Download date
- Re-download button
- Lightbox integration

### 4. Organization Name Integration

#### Modified Event Creation
```python
# Get organization name from admin session
organization_name = session.get('organization_name', 'Unknown')

new_event = {
    # ... existing fields ...
    "organization_name": organization_name,  # NEW
    "created_by": session.get('admin_id')
}
```

#### Event Display
```html
<div class="event-card">
    <h3>{{ event.name }}</h3>
    <p class="text-sm text-gray-600">
        by {{ event.organization_name }}
    </p>
</div>
```

### 5. Event Search Component

#### HTML Structure
```html
<div class="search-container">
    <input type="text" 
           id="event-search" 
           placeholder="Search by organization name..."
           class="search-input">
</div>
```

#### JavaScript Filter
```javascript
function filterEvents(searchTerm) {
    const events = allEvents.filter(event => 
        event.organization_name
            .toLowerCase()
            .includes(searchTerm.toLowerCase())
    );
    displayEvents(events);
}
```

## Data Models

### Download Model
```python
class Download:
    id: int
    user_id: int
    photo_url: str
    event_id: str
    event_name: str
    downloaded_at: datetime
```

### Enhanced Event Model
```python
class Event:
    id: str
    name: str
    location: str
    date: str
    category: str
    image: str
    photos_count: int
    qr_code: str
    created_by: int
    organization_name: str  # NEW
    created_at: datetime
```

## Error Handling

### Download Errors
- **401 Unauthorized:** User not logged in
- **404 Not Found:** Photo doesn't exist
- **500 Internal Server Error:** Database error

### Error Messages
```python
ERROR_MESSAGES = {
    'not_logged_in': 'Please login to download photos',
    'photo_not_found': 'Photo not found',
    'download_failed': 'Failed to track download',
    'db_error': 'Database error occurred'
}
```

## Security Considerations

### Download Authorization
- Only logged-in users can download
- Track downloads per user
- Prevent unauthorized access to private photos
- Validate photo URLs before download

### SQL Injection Prevention
```python
# Use parameterized queries
cursor.execute(
    "INSERT INTO downloads (user_id, photo_url, event_id, event_name) VALUES (%s, %s, %s, %s)",
    (user_id, photo_url, event_id, event_name)
)
```

## Testing Strategy

### Unit Tests
1. Test lightbox open/close
2. Test photo navigation (next/previous)
3. Test download tracking
4. Test duplicate download prevention
5. Test organization name display
6. Test event search filtering

### Integration Tests
1. Test complete download flow
2. Test My Downloads page loading
3. Test search with various organization names
4. Test lightbox with multiple photos
5. Test download history persistence

## Performance Considerations

### Image Loading
- Lazy load thumbnails
- Preload next/previous photos in lightbox
- Use optimized image URLs
- Cache downloaded photos list

### Database Optimization
- Index on (user_id, downloaded_at)
- Unique constraint on (user_id, photo_url)
- Limit query results
- Use connection pooling

### Caching
- Cache downloads list for 5 minutes
- Cache organization names
- Invalidate cache on new download

## UI/UX Design

### Lightbox Design
- Full-screen overlay
- Semi-transparent black background (90% opacity)
- Centered photo with max-width/max-height
- White close button (top-right)
- Navigation arrows (left/right)
- Download button (bottom-center)
- Smooth fade-in animation

### My Downloads Page
- Responsive grid (2-4 columns)
- Photo thumbnails with hover effect
- Event name badge
- Download date display
- Re-download button on hover
- Empty state message

### Search Bar
- Prominent placement at top
- Search icon
- Placeholder text
- Real-time filtering
- Clear button when text entered
