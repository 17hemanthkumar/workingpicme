# Requirements Document: Photo Management Enhancements

## Introduction

This feature enhances the user experience for viewing, downloading, and managing event photos in PicMe. Users will be able to preview photos in a lightbox, download them, track their downloads, and search events by organization name.

## Glossary

- **Lightbox**: A modal overlay that displays an enlarged photo with navigation and download options
- **Download History**: A record of photos downloaded by a user
- **Organization Filter**: Search functionality to filter events by organization name
- **Photo Preview**: Enlarged view of a photo in a modal/popup
- **User Session**: Server-side session data for authenticated users
- **Downloaded Photos Section**: User's personal collection of downloaded photos

## Requirements

### Requirement 1: Photo Lightbox Preview

**User Story:** As a user, I want to click on a photo thumbnail to see it enlarged, so that I can view details before downloading.

#### Acceptance Criteria

1. WHEN a user clicks on a photo thumbnail, THE System SHALL display the photo in an enlarged lightbox overlay
2. WHEN the lightbox opens, THE System SHALL display the full-size photo centered on screen
3. WHEN the lightbox is open, THE System SHALL dim the background content
4. WHEN a user clicks outside the photo or presses ESC, THE System SHALL close the lightbox
5. THE System SHALL display navigation arrows for viewing next/previous photos in the lightbox

### Requirement 2: Photo Download Functionality

**User Story:** As a user, I want to download photos I like, so that I can save them to my device.

#### Acceptance Criteria

1. WHEN a user views a photo in the lightbox, THE System SHALL display a Download button
2. WHEN a user clicks the Download button, THE System SHALL initiate a file download to the user's device
3. WHEN a download completes, THE System SHALL record the download in the user's download history
4. WHEN a download is recorded, THE System SHALL store the user_id, photo_url, event_id, and download timestamp
5. THE System SHALL provide visual feedback when a download is initiated

### Requirement 3: Download History Tracking

**User Story:** As a user, I want my downloaded photos tracked, so that I can access them later without re-downloading.

#### Acceptance Criteria

1. THE System SHALL create a downloads table with columns: id, user_id, photo_url, event_id, event_name, downloaded_at
2. WHEN a user downloads a photo, THE System SHALL insert a record into the downloads table
3. THE System SHALL prevent duplicate download records for the same user and photo
4. THE System SHALL associate downloads with the logged-in user's user_id
5. THE System SHALL store the event name for easy reference

### Requirement 4: My Downloads Section

**User Story:** As a user, I want to see all photos I've downloaded, so that I can re-download or view them again.

#### Acceptance Criteria

1. THE System SHALL create a /my_downloads route accessible to logged-in users
2. WHEN a user accesses My Downloads, THE System SHALL retrieve all download records for that user
3. THE System SHALL display downloaded photos in a grid layout
4. THE System SHALL show the event name and download date for each photo
5. THE System SHALL allow users to click photos to view in lightbox and re-download

### Requirement 5: Organization Name Display

**User Story:** As a user, I want to see which organization created each event, so that I can identify events from specific organizers.

#### Acceptance Criteria

1. WHEN events are created, THE System SHALL store the admin's organization_name with the event
2. WHEN events are displayed, THE System SHALL show the organization name below or beside the event name
3. THE System SHALL retrieve organization_name from the admin table using created_by field
4. WHEN organization_name is not available, THE System SHALL display "Unknown Organizer"
5. THE System SHALL display organization name in event cards on discovery page

### Requirement 6: Event Search by Organization

**User Story:** As a user, I want to search events by organization name, so that I can quickly find events from specific organizers.

#### Acceptance Criteria

1. THE System SHALL display a search input field at the top of the event discovery page
2. WHEN a user types in the search field, THE System SHALL filter events by organization name
3. THE System SHALL perform case-insensitive search matching
4. WHEN search text is empty, THE System SHALL display all events
5. THE System SHALL update the displayed events in real-time as the user types

### Requirement 7: Lightbox Navigation

**User Story:** As a user, I want to navigate between photos in the lightbox, so that I can view multiple photos without closing the preview.

#### Acceptance Criteria

1. WHEN the lightbox is open, THE System SHALL display previous and next navigation arrows
2. WHEN a user clicks the next arrow, THE System SHALL display the next photo in the event
3. WHEN a user clicks the previous arrow, THE System SHALL display the previous photo
4. WHEN viewing the first photo, THE System SHALL disable or hide the previous arrow
5. WHEN viewing the last photo, THE System SHALL disable or hide the next arrow

### Requirement 8: Download Button Styling

**User Story:** As a user, I want a clear and accessible download button, so that I can easily download photos.

#### Acceptance Criteria

1. THE System SHALL display a Download button in the lightbox with an icon
2. THE System SHALL style the button to be clearly visible against the photo
3. WHEN a user hovers over the Download button, THE System SHALL show a hover effect
4. WHEN a download is in progress, THE System SHALL show a loading indicator
5. WHEN a download completes, THE System SHALL show a success message

### Requirement 9: My Downloads Page Layout

**User Story:** As a user, I want my downloads page to be well-organized, so that I can easily find previously downloaded photos.

#### Acceptance Criteria

1. THE System SHALL display downloads in a responsive grid (2-4 columns based on screen size)
2. THE System SHALL show the most recently downloaded photos first
3. THE System SHALL display event name and download date for each photo
4. THE System SHALL provide a "Re-download" button for each photo
5. WHEN no downloads exist, THE System SHALL display a helpful message

### Requirement 10: Performance Optimization

**User Story:** As a user, I want photo operations to be fast, so that my experience is smooth.

#### Acceptance Criteria

1. THE System SHALL lazy-load photo thumbnails in the grid
2. THE System SHALL cache the downloads list for 5 minutes
3. THE System SHALL use optimized image URLs for thumbnails
4. THE System SHALL preload the next photo when viewing in lightbox
5. THE System SHALL minimize database queries for download tracking
