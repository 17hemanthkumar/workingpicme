# Design Document: Event Editing Functionality

## Overview

This design document outlines the architecture and implementation approach for enabling admins to edit event details directly from the admin dashboard. The solution provides a seamless editing experience with real-time synchronization across all user-facing pages while preserving all existing event data and functionality.

### Key Design Goals

1. Add Edit button to each event card in admin dashboard
2. Provide intuitive edit form with validation
3. Enable editing of event name, location, date, category, and organization name
4. Ensure real-time reflection of changes on all pages
5. Maintain data integrity (preserve photos, thumbnails, QR codes)
6. Implement proper authorization (only event creator can edit)
7. Preserve all existing dashboard functionality

## Architecture

### System Components

```
┌─────────────────────────────────────────────────────────────┐
│                     Frontend Layer                           │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  event_organizer.html (Admin Dashboard)              │  │
│  │  - Edit Button on Event Cards                        │  │
│  │  - Edit Modal with Form                              │  │
│  │  - Form Validation                                   │  │
│  │  - Real-time UI Updates                              │  │
│  └──────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  User Pages (Auto-updated)                           │  │
│  │  - event_discovery.html                              │  │
│  │  - homepage.html                                     │  │
│  │  - event_detail.html                                 │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                     Backend Layer (Flask)                    │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  New API Endpoint                                     │  │
│  │  - PUT /api/events/<event_id> (update event)         │  │
│  │                                                       │  │
│  │  Existing Endpoints (unchanged)                      │  │
│  │  - GET /api/events (list all events)                 │  │
│  │  - POST /api/create_event                            │  │
│  │  - DELETE /api/events/<event_id>                     │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                     Data Layer                               │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  events_data.json                                    │  │
│  │  - Update event fields atomically                    │  │
│  │  - Preserve all existing fields                      │  │
│  │  - Maintain data integrity                           │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

## Components and Interfaces

### 1. Frontend Components

#### 1.1 Edit Button on Event Cards

**Location:** `frontend/pages/event_organizer.html`

**Implementation:**
```html
<!-- Add to each event card -->
<button onclick="openEditModal('${event.id}')" 
        class="px-3 py-1.5 bg-blue-600 text-white text-sm rounded-md hover:bg-blue-700 transition-colors">
    <svg class="w-4 h-4 inline mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"></path>
    </svg>
    Edit Event
</button>
```

**Positioning:** Place next to existing action buttons (View Photos, Delete, etc.)

#### 1.2 Edit Modal Component

**Structure:**
```html
<!-- Edit Event Modal -->
<div id="edit-event-modal" class="hidden fixed inset-0 z-50 overflow-y-auto">
    <!-- Backdrop -->
    <div class="fixed inset-0 bg-black bg-opacity-50 transition-opacity"></div>
    
    <!-- Modal Content -->
    <div class="flex items-center justify-center min-h-screen p-4">
        <div class="relative bg-white rounded-lg shadow-xl max-w-2xl w-full p-6">
            <!-- Header -->
            <div class="flex justify-between items-center mb-6">
                <h2 class="text-2xl font-bold text-gray-900">Edit Event Details</h2>
                <button onclick="closeEditModal()" class="text-gray-400 hover:text-gray-600">
                    <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                    </svg>
                </button>
            </div>
            
            <!-- Edit Form -->
            <form id="edit-event-form" class="space-y-4">
                <!-- Event Name -->
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">Event Name *</label>
                    <input type="text" id="edit-event-name" required maxlength="200"
                           class="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-indigo-500">
                    <p class="text-red-600 text-sm mt-1 hidden" id="error-event-name"></p>
                </div>
                
                <!-- Location -->
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">Location *</label>
                    <input type="text" id="edit-location" required maxlength="200"
                           class="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-indigo-500">
                    <p class="text-red-600 text-sm mt-1 hidden" id="error-location"></p>
                </div>
                
                <!-- Date -->
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">Date *</label>
                    <input type="date" id="edit-date" required
                           class="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-indigo-500">
                    <p class="text-red-600 text-sm mt-1 hidden" id="error-date"></p>
                </div>
                
                <!-- Category -->
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">Category *</label>
                    <select id="edit-category" required
                            class="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-indigo-500">
                        <option value="">Select Category</option>
                        <option value="Festival">Festival</option>
                        <option value="Corporate">Corporate</option>
                        <option value="Wedding">Wedding</option>
                        <option value="Conference">Conference</option>
                        <option value="Charity">Charity</option>
                        <option value="Sports">Sports</option>
                        <option value="Other">Other</option>
                    </select>
                    <p class="text-red-600 text-sm mt-1 hidden" id="error-category"></p>
                </div>
                
                <!-- Organization Name -->
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">Organization Name *</label>
                    <input type="text" id="edit-organization-name" required maxlength="200"
                           class="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-indigo-500">
                    <p class="text-red-600 text-sm mt-1 hidden" id="error-organization-name"></p>
                </div>
                
                <!-- Action Buttons -->
                <div class="flex justify-end space-x-3 mt-6 pt-4 border-t">
                    <button type="button" onclick="closeEditModal()"
                            class="px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50">
                        Cancel
                    </button>
                    <button type="submit"
                            class="px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700">
                        Save Changes
                    </button>
                </div>
            </form>
            
            <!-- Loading Indicator -->
            <div id="edit-loading" class="hidden absolute inset-0 bg-white bg-opacity-75 flex items-center justify-center rounded-lg">
                <div class="text-center">
                    <svg class="animate-spin h-10 w-10 text-indigo-600 mx-auto" fill="none" viewBox="0 0 24 24">
                        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    <p class="mt-2 text-gray-600">Saving changes...</p>
                </div>
            </div>
        </div>
    </div>
</div>
```

#### 1.3 JavaScript Functions

**Event Editing Module:**
```javascript
// Store current event ID being edited
let currentEditEventId = null;

// Open edit modal and load event data
async function openEditModal(eventId) {
    currentEditEventId = eventId;
    
    try {
        // Fetch current event data
        const response = await fetch(`/api/events/${eventId}`);
        const data = await response.json();
        
        if (data.success) {
            const event = data.event;
            
            // Populate form fields
            document.getElementById('edit-event-name').value = event.name || '';
            document.getElementById('edit-location').value = event.location || '';
            document.getElementById('edit-date').value = formatDateForInput(event.date);
            document.getElementById('edit-category').value = event.category || '';
            document.getElementById('edit-organization-name').value = event.organization_name || '';
            
            // Show modal
            document.getElementById('edit-event-modal').classList.remove('hidden');
            document.body.style.overflow = 'hidden';
        } else {
            alert('Failed to load event details');
        }
    } catch (error) {
        console.error('Error loading event:', error);
        alert('Failed to load event details');
    }
}

// Close edit modal
function closeEditModal() {
    document.getElementById('edit-event-modal').classList.add('hidden');
    document.body.style.overflow = '';
    currentEditEventId = null;
    
    // Clear form and errors
    document.getElementById('edit-event-form').reset();
    clearValidationErrors();
}

// Format date for input field (YYYY-MM-DD)
function formatDateForInput(dateString) {
    // Handle various date formats
    const date = new Date(dateString);
    if (isNaN(date.getTime())) {
        return '';
    }
    return date.toISOString().split('T')[0];
}

// Clear validation errors
function clearValidationErrors() {
    const errorElements = document.querySelectorAll('[id^="error-"]');
    errorElements.forEach(el => {
        el.textContent = '';
        el.classList.add('hidden');
    });
    
    const inputElements = document.querySelectorAll('#edit-event-form input, #edit-event-form select');
    inputElements.forEach(el => {
        el.classList.remove('border-red-500');
    });
}

// Show validation error
function showValidationError(fieldId, message) {
    const errorEl = document.getElementById(`error-${fieldId}`);
    const inputEl = document.getElementById(`edit-${fieldId}`);
    
    if (errorEl && inputEl) {
        errorEl.textContent = message;
        errorEl.classList.remove('hidden');
        inputEl.classList.add('border-red-500');
    }
}

// Validate form
function validateEditForm() {
    clearValidationErrors();
    let isValid = true;
    
    const eventName = document.getElementById('edit-event-name').value.trim();
    const location = document.getElementById('edit-location').value.trim();
    const date = document.getElementById('edit-date').value;
    const category = document.getElementById('edit-category').value;
    const orgName = document.getElementById('edit-organization-name').value.trim();
    
    if (!eventName) {
        showValidationError('event-name', 'Event name is required');
        isValid = false;
    } else if (eventName.length > 200) {
        showValidationError('event-name', 'Event name must be 200 characters or less');
        isValid = false;
    }
    
    if (!location) {
        showValidationError('location', 'Location is required');
        isValid = false;
    } else if (location.length > 200) {
        showValidationError('location', 'Location must be 200 characters or less');
        isValid = false;
    }
    
    if (!date) {
        showValidationError('date', 'Date is required');
        isValid = false;
    }
    
    if (!category) {
        showValidationError('category', 'Category is required');
        isValid = false;
    }
    
    if (!orgName) {
        showValidationError('organization-name', 'Organization name is required');
        isValid = false;
    } else if (orgName.length > 200) {
        showValidationError('organization-name', 'Organization name must be 200 characters or less');
        isValid = false;
    }
    
    return isValid;
}

// Handle form submission
document.getElementById('edit-event-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    if (!validateEditForm()) {
        return;
    }
    
    // Show loading indicator
    document.getElementById('edit-loading').classList.remove('hidden');
    
    try {
        const formData = {
            name: document.getElementById('edit-event-name').value.trim(),
            location: document.getElementById('edit-location').value.trim(),
            date: document.getElementById('edit-date').value,
            category: document.getElementById('edit-category').value,
            organization_name: document.getElementById('edit-organization-name').value.trim()
        };
        
        const response = await fetch(`/api/events/${currentEditEventId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData)
        });
        
        const data = await response.json();
        
        if (data.success) {
            // Show success message
            alert('Event updated successfully!');
            
            // Close modal
            closeEditModal();
            
            // Reload events to show updated data
            await loadEvents();
        } else {
            alert(data.error || 'Failed to update event');
        }
    } catch (error) {
        console.error('Error updating event:', error);
        alert('Failed to update event. Please try again.');
    } finally {
        document.getElementById('edit-loading').classList.add('hidden');
    }
});

// Close modal on Escape key
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && !document.getElementById('edit-event-modal').classList.contains('hidden')) {
        closeEditModal();
    }
});

// Close modal on backdrop click
document.getElementById('edit-event-modal')?.addEventListener('click', (e) => {
    if (e.target.id === 'edit-event-modal') {
        closeEditModal();
    }
});
```

### 2. Backend Components

#### 2.1 New API Endpoint: PUT /api/events/<event_id>

**Purpose:** Update event details

**Authentication:** Admin required

**Authorization:** Only event creator can edit

**Request Body:**
```json
{
    "name": "Updated Event Name",
    "location": "New Location",
    "date": "2025-12-31",
    "category": "Festival",
    "organization_name": "Updated Organization"
}
```

**Response (Success):**
```json
{
    "success": true,
    "message": "Event updated successfully",
    "event": {
        "id": "event_abc123",
        "name": "Updated Event Name",
        "location": "New Location",
        "date": "2025-12-31",
        "category": "Festival",
        "organization_name": "Updated Organization",
        "cover_thumbnail": "/uploads/thumbnails/event_abc123_thumb.jpg",
        "photos_count": 42,
        "qr_code": "/api/qr_code/event_abc123",
        "created_by": 1,
        "created_at": "2025-11-10T10:00:00"
    }
}
```

**Response (Error):**
```json
{
    "success": false,
    "error": "Event not found"
}
```

**Implementation:**
```python
@app.route('/api/events/<event_id>', methods=['PUT'])
@admin_required
def update_event(event_id):
    """Update event details"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['name', 'location', 'date', 'category', 'organization_name']
        for field in required_fields:
            if field not in data or not data[field].strip():
                return jsonify({
                    "success": False,
                    "error": f"{field.replace('_', ' ').title()} is required"
                }), 400
        
        # Validate field lengths
        if len(data['name']) > 200:
            return jsonify({"success": False, "error": "Event name too long"}), 400
        if len(data['location']) > 200:
            return jsonify({"success": False, "error": "Location too long"}), 400
        if len(data['organization_name']) > 200:
            return jsonify({"success": False, "error": "Organization name too long"}), 400
        
        # Load events data
        events_data = get_events_cached()
        
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
        save_events_data_atomic(events_data)
        
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

def save_events_data_atomic(events_data):
    """Save events data atomically with backup"""
    import tempfile
    import shutil
    
    # Write to temporary file first
    temp_fd, temp_path = tempfile.mkstemp(suffix='.json', dir=os.path.dirname(EVENTS_DATA_PATH))
    try:
        with os.fdopen(temp_fd, 'w') as f:
            json.dump(events_data, f, indent=2)
        
        # Create backup of current file
        if os.path.exists(EVENTS_DATA_PATH):
            backup_path = EVENTS_DATA_PATH + '.backup'
            shutil.copy(EVENTS_DATA_PATH, backup_path)
        
        # Atomic rename
        shutil.move(temp_path, EVENTS_DATA_PATH)
        
    except Exception as e:
        # Clean up temp file if it exists
        if os.path.exists(temp_path):
            os.remove(temp_path)
        raise e

def invalidate_events_cache():
    """Invalidate events cache to force reload"""
    # If using caching, clear the cache here
    # For now, the get_events_cached() function reads from file each time
    pass
```

#### 2.2 Modified API Endpoint: GET /api/events/<event_id>

**Purpose:** Get single event details (needed for edit form)

**Implementation:**
```python
@app.route('/api/events/<event_id>', methods=['GET'])
def get_event_by_id(event_id):
    """Get single event details"""
    try:
        events_data = get_events_cached()
        
        event = next((e for e in events_data if e['id'] == event_id), None)
        
        if not event:
            return jsonify({"success": False, "error": "Event not found"}), 404
        
        return jsonify({"success": True, "event": event}), 200
        
    except Exception as e:
        print(f"Error fetching event: {e}")
        return jsonify({"success": False, "error": "Internal server error"}), 500
```

### 3. Data Model

**Event Structure (Unchanged):**
```json
{
    "id": "event_abc123",
    "name": "Event Name",
    "location": "Event Location",
    "date": "2025-12-31",
    "category": "Festival",
    "image": "/static/images/default_event.jpg",
    "cover_thumbnail": "/uploads/thumbnails/event_abc123_thumb.jpg",
    "photos_count": 42,
    "qr_code": "/api/qr_code/event_abc123",
    "created_by": 1,
    "organization_name": "Organization Name",
    "created_at": "2025-11-10T10:00:00"
}
```

**Editable Fields:**
- `name` - Event name
- `location` - Event location
- `date` - Event date
- `category` - Event category
- `organization_name` - Organization name

**Preserved Fields (Not Editable):**
- `id` - Event ID
- `image` - Legacy image field
- `cover_thumbnail` - Event thumbnail
- `photos_count` - Number of photos
- `qr_code` - QR code URL
- `created_by` - Admin ID who created the event
- `created_at` - Creation timestamp

## Real-Time Synchronization

### How It Works

1. **Admin Updates Event:**
   - Admin clicks Edit button
   - Fills out form with new values
   - Clicks Save
   - Backend updates events_data.json atomically

2. **Admin Dashboard Updates:**
   - After successful save, frontend calls `loadEvents()` to refresh the event list
   - Updated event displays immediately with new values

3. **User Pages Auto-Update:**
   - User pages fetch events from `/api/events` endpoint
   - Since events_data.json is updated, next page load shows new values
   - No caching issues because data is read from file on each request

4. **Search Results Update:**
   - Search filters events by name and organization_name
   - Updated values are immediately searchable
   - No cache clearing needed

### Data Flow

```
Admin Edits Event
       ↓
PUT /api/events/<id>
       ↓
Validate Input
       ↓
Check Authorization
       ↓
Update events_data.json (Atomic Write)
       ↓
Return Success
       ↓
Frontend Reloads Events
       ↓
Admin Dashboard Shows Updated Event
       ↓
User Visits Event Discovery Page
       ↓
GET /api/events
       ↓
Returns Updated Events from File
       ↓
User Sees Updated Information
```

## Error Handling

### Validation Errors

**Client-Side:**
- Empty required fields → Show field-specific error
- Field too long → Show character limit error
- Invalid date format → Show date format error

**Server-Side:**
- Missing required fields → Return 400 with error message
- Field length exceeded → Return 400 with error message
- Invalid data format → Return 400 with error message

### Authorization Errors

- Not logged in → Return 401 Unauthorized
- Not event creator → Return 403 Forbidden
- Event not found → Return 404 Not Found

### System Errors

- File write error → Return 500 with generic error
- JSON parse error → Return 500 with generic error
- Network error → Show user-friendly message on frontend

## Security Considerations

### Authorization

1. **Admin Authentication:**
   - All edit endpoints require `@admin_required` decorator
   - Session must contain valid `admin_id`

2. **Event Ownership:**
   - Verify `event.created_by == session.admin_id`
   - Prevent admins from editing other admins' events

3. **Input Validation:**
   - Sanitize all input fields
   - Enforce maximum lengths
   - Validate data types

### Data Integrity

1. **Atomic Writes:**
   - Write to temporary file first
   - Create backup before overwriting
   - Use atomic rename operation

2. **Field Preservation:**
   - Only update specified fields
   - Preserve all other event data
   - Maintain data structure consistency

## Testing Strategy

### Unit Tests

```python
def test_update_event_success():
    # Test successful event update
    pass

def test_update_event_unauthorized():
    # Test updating another admin's event
    pass

def test_update_event_validation():
    # Test validation errors
    pass

def test_update_event_not_found():
    # Test updating non-existent event
    pass
```

### Integration Tests

1. Edit event → Verify admin dashboard shows changes
2. Edit event → Verify event discovery page shows changes
3. Edit event → Verify homepage shows changes
4. Edit organization name → Verify search finds event by new name
5. Edit event name → Verify search finds event by new name

### Manual Testing Checklist

- [ ] Click Edit button opens modal with current values
- [ ] Submit empty form shows validation errors
- [ ] Submit valid form updates event successfully
- [ ] Updated event displays on admin dashboard
- [ ] Updated event displays on event discovery page
- [ ] Updated event displays on homepage
- [ ] Search by new organization name finds event
- [ ] Search by new event name finds event
- [ ] Cancel button closes modal without saving
- [ ] Escape key closes modal
- [ ] Click outside modal closes it
- [ ] Photos and thumbnail preserved after edit
- [ ] Cannot edit another admin's event

## Deployment Checklist

- [ ] Add edit modal HTML to event_organizer.html
- [ ] Add edit JavaScript functions
- [ ] Implement PUT /api/events/<event_id> endpoint
- [ ] Implement GET /api/events/<event_id> endpoint
- [ ] Add atomic file write function
- [ ] Test all validation rules
- [ ] Test authorization checks
- [ ] Verify real-time updates work
- [ ] Test on mobile devices
- [ ] Backup events_data.json before deployment
