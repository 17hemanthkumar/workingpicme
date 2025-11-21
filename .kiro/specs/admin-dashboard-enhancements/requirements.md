# Requirements Document: Admin Dashboard Enhancements

## Introduction

This feature simplifies the admin dashboard by consolidating event photo management directly within the Events section, removing redundant navigation items, and adding event cover thumbnail functionality. The goal is to create a more streamlined and efficient admin experience while maintaining all existing functionality.

## Glossary

- **Admin**: An event organizer who manages events and uploads photos
- **Event Cover Thumbnail**: A representative image displayed on the event card to visually identify the event
- **Event Photo Management**: The ability to view, upload, and delete photos associated with an event
- **Admin Dashboard**: The event organizer interface for creating and managing events
- **Photo Storage**: File system and database storage for event photos
- **Event Card**: A visual representation of an event in the admin dashboard

## Requirements

### Requirement 1: Simplified Navigation

**User Story:** As an admin, I want a simplified navigation menu without redundant sections, so that I can focus on event management efficiently.

#### Acceptance Criteria

1. THE System SHALL remove the "Home" link from the admin dashboard navigation
2. THE System SHALL remove the "Events" link from the admin dashboard navigation
3. THE System SHALL remove the "My Photos" link from the admin dashboard navigation
4. THE System SHALL keep the "My Dashboard" link in the navigation
5. THE System SHALL maintain the organization name display and logout button in the navigation

### Requirement 2: Event Photo Viewing

**User Story:** As an admin, I want to view all photos for each event directly in the Events section, so that I can see what photos are available without navigating elsewhere.

#### Acceptance Criteria

1. WHEN an admin views an event card, THE System SHALL display a "View Photos" button or expandable section
2. WHEN an admin clicks "View Photos", THE System SHALL retrieve all photos for that event from the database
3. WHEN photos are displayed, THE System SHALL show both group photos and individual photos
4. WHEN photos are displayed, THE System SHALL render them in a grid layout with thumbnails
5. WHEN no photos exist for an event, THE System SHALL display a message "No photos uploaded yet"

### Requirement 3: Event Photo Deletion

**User Story:** As an admin, I want to delete specific photos from an event, so that I can remove unwanted or incorrect photos.

#### Acceptance Criteria

1. WHEN an admin views event photos, THE System SHALL display a delete button or icon on each photo thumbnail
2. WHEN an admin clicks the delete button, THE System SHALL prompt for confirmation before deletion
3. WHEN deletion is confirmed, THE System SHALL remove the photo file from the file system
4. WHEN deletion is confirmed, THE System SHALL remove the photo reference from the database
5. WHEN deletion completes, THE System SHALL update the photo grid to reflect the removal

### Requirement 4: Event Cover Thumbnail Upload

**User Story:** As an admin, I want to upload a cover thumbnail when creating an event, so that the event has a visual representation.

#### Acceptance Criteria

1. WHEN an admin creates a new event, THE System SHALL display a file input field for uploading a cover thumbnail
2. WHEN a cover thumbnail is uploaded, THE System SHALL validate the file is an image (jpg, jpeg, png, gif)
3. WHEN a cover thumbnail is valid, THE System SHALL store it in a designated thumbnails directory
4. WHEN a cover thumbnail is stored, THE System SHALL save the thumbnail path in the events table
5. WHEN no thumbnail is uploaded, THE System SHALL use a default placeholder image

### Requirement 5: Event Cover Thumbnail Display

**User Story:** As an admin, I want to see the cover thumbnail on each event card, so that I can visually identify events quickly.

#### Acceptance Criteria

1. WHEN the admin dashboard loads events, THE System SHALL retrieve the cover thumbnail path for each event
2. WHEN an event has a cover thumbnail, THE System SHALL display it prominently on the event card
3. WHEN an event has no cover thumbnail, THE System SHALL display a default placeholder image
4. THE System SHALL display the thumbnail with consistent dimensions across all event cards
5. THE System SHALL optimize thumbnail loading for performance

### Requirement 6: Event Cover Thumbnail Modification

**User Story:** As an admin, I want to update or replace an event's cover thumbnail, so that I can change the visual representation if needed.

#### Acceptance Criteria

1. WHEN an admin views an event card, THE System SHALL display an "Edit Thumbnail" or "Change Cover" button
2. WHEN an admin clicks the edit button, THE System SHALL display a file input for uploading a new thumbnail
3. WHEN a new thumbnail is uploaded, THE System SHALL replace the existing thumbnail file
4. WHEN a new thumbnail is uploaded, THE System SHALL update the thumbnail path in the database
5. WHEN the update completes, THE System SHALL display the new thumbnail on the event card

### Requirement 7: Database Schema Updates

**User Story:** As a system administrator, I want the database schema updated to support cover thumbnails, so that thumbnail data is properly stored.

#### Acceptance Criteria

1. THE System SHALL add a cover_thumbnail column to the events table
2. THE System SHALL set cover_thumbnail as a TEXT or VARCHAR field to store file paths
3. THE System SHALL allow cover_thumbnail to be NULL for events without thumbnails
4. THE System SHALL create a migration or update script to add the column to existing databases
5. THE System SHALL maintain backward compatibility with existing event records

### Requirement 8: Photo Storage Management

**User Story:** As a system administrator, I want deleted photos removed from storage, so that disk space is not wasted on unused files.

#### Acceptance Criteria

1. WHEN a photo is deleted, THE System SHALL remove the file from the uploads directory
2. WHEN a photo is deleted, THE System SHALL remove the file from the processed directory if it exists
3. WHEN a photo is deleted, THE System SHALL remove any associated thumbnail files
4. WHEN file deletion fails, THE System SHALL log the error and continue with database deletion
5. THE System SHALL verify file existence before attempting deletion

### Requirement 9: Admin-Only Access Control

**User Story:** As a system administrator, I want photo management restricted to admins only, so that regular users cannot modify event photos.

#### Acceptance Criteria

1. THE System SHALL require admin authentication for all photo upload endpoints
2. THE System SHALL require admin authentication for all photo deletion endpoints
3. THE System SHALL require admin authentication for thumbnail upload and modification endpoints
4. WHEN a non-admin attempts to access photo management, THE System SHALL return a 403 Forbidden error
5. THE System SHALL verify admin session before processing any photo management requests

### Requirement 10: Error Handling and Validation

**User Story:** As an admin, I want clear error messages when photo operations fail, so that I can understand and resolve issues.

#### Acceptance Criteria

1. WHEN photo upload fails, THE System SHALL display a descriptive error message
2. WHEN photo deletion fails, THE System SHALL display an error message and not remove the photo from the UI
3. WHEN thumbnail upload fails, THE System SHALL display an error and allow retry
4. WHEN file size exceeds limits, THE System SHALL display "File too large" error
5. WHEN invalid file types are uploaded, THE System SHALL display "Invalid file type" error

### Requirement 11: UI Consistency

**User Story:** As an admin, I want the dashboard to maintain consistent styling and layout, so that the interface feels cohesive.

#### Acceptance Criteria

1. THE System SHALL use the existing Tailwind CSS styling for all new UI components
2. THE System SHALL match button styles with existing dashboard buttons
3. THE System SHALL maintain the same color scheme (indigo primary, gray secondary)
4. THE System SHALL ensure responsive design works on mobile and desktop
5. THE System SHALL maintain consistent spacing and padding with existing elements

### Requirement 12: Photo Grid Display

**User Story:** As an admin, I want event photos displayed in an organized grid, so that I can easily browse and manage them.

#### Acceptance Criteria

1. WHEN photos are displayed, THE System SHALL render them in a responsive grid layout
2. THE System SHALL display 3-4 photos per row on desktop screens
3. THE System SHALL display 2 photos per row on tablet screens
4. THE System SHALL display 1 photo per row on mobile screens
5. THE System SHALL show photo thumbnails with consistent aspect ratios

### Requirement 13: Thumbnail Synchronization Across User Pages

**User Story:** As a user, I want to see the updated event thumbnail on all public pages when an admin changes it, so that I can visually identify events consistently.

#### Acceptance Criteria

1. WHEN an admin uploads a cover thumbnail, THE System SHALL display the thumbnail on the event discovery page
2. WHEN an admin uploads a cover thumbnail, THE System SHALL display the thumbnail on the homepage featured events section
3. WHEN an admin uploads a cover thumbnail, THE System SHALL display the thumbnail on the event detail page
4. WHEN an admin updates a cover thumbnail, THE System SHALL reflect the change on all user-facing pages immediately
5. WHEN no thumbnail is set, THE System SHALL display a default placeholder image on all user-facing pages

### Requirement 14: Existing Functionality Preservation

**User Story:** As an admin, I want all existing dashboard features to continue working, so that my workflow is not disrupted.

#### Acceptance Criteria

1. THE System SHALL maintain the ability to create new events
2. THE System SHALL maintain the ability to delete events
3. THE System SHALL maintain the ability to download event QR codes
4. THE System SHALL maintain the ability to upload photos to events
5. THE System SHALL maintain admin authentication and session management
