# Implementation Plan: Admin Dashboard Enhancements

- [x] 1. Set up data model and file system structure



  - Add `cover_thumbnail` field to events data structure with default value
  - Create `uploads/thumbnails/` directory for storing event cover images
  - Create default placeholder thumbnail image in static assets
  - Write migration script to add `cover_thumbnail` field to existing events in `events_data.json`



  - _Requirements: 4.1, 4.2, 4.3, 4.4, 7.1, 7.2, 7.3_

- [ ] 2. Implement backend API for photo retrieval
  - Create GET `/api/events/<event_id>/photos` endpoint with admin authentication
  - Implement function to list all photos in event upload directory



  - Exclude QR code files from photo list
  - Return photo metadata including filename, URL, size, and upload timestamp
  - Add error handling for non-existent events
  - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 9.1, 9.2, 10.1_

- [x] 3. Implement backend API for photo deletion



  - Create DELETE `/api/events/<event_id>/photos/<filename>` endpoint with admin authentication
  - Implement file deletion from uploads directory
  - Implement cleanup of processed photos (individual and group folders)
  - Update photo count in `events_data.json` after deletion
  - Add comprehensive error handling for file not found and permission errors
  - Invalidate relevant caches after deletion
  - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 8.1, 8.2, 8.3, 8.4, 8.5, 9.1, 9.3, 10.2_




- [ ] 4. Implement backend API for thumbnail management
  - Create POST `/api/events/<event_id>/thumbnail` endpoint for initial thumbnail upload
  - Create PUT `/api/events/<event_id>/thumbnail` endpoint for thumbnail updates
  - Implement thumbnail file validation (type, size, format)



  - Save thumbnails to `uploads/thumbnails/` directory with unique filenames
  - Update event data in `events_data.json` with thumbnail path
  - Implement thumbnail replacement logic (delete old, save new)
  - Add error handling for invalid files and upload failures
  - _Requirements: 4.1, 4.2, 4.3, 4.4, 6.1, 6.2, 6.3, 6.4, 6.5, 9.3, 10.3_




- [ ] 5. Modify event creation endpoint to support thumbnails
  - Update POST `/api/create_event` to accept multipart form data instead of JSON
  - Add optional thumbnail file handling during event creation
  - Save thumbnail if provided, otherwise use default placeholder
  - Store thumbnail path in event data structure

  - Maintain backward compatibility with existing event creation flow
  - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5, 13.1_

- [ ] 6. Update admin dashboard navigation
  - Remove "Home" link from navigation bar in `event_organizer.html`
  - Remove "Events" link from navigation bar
  - Remove "My Photos" link from navigation bar
  - Keep "My Dashboard" link and ensure it navigates to `/event_organizer`
  - Maintain organization name display and logout button


  - Verify responsive design works correctly with simplified navigation
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 11.1, 11.2, 11.3, 11.4, 11.5_

- [ ] 7. Add cover thumbnail display to event cards
  - Add thumbnail image element to event card template
  - Display cover thumbnail at top of each event card
  - Use default placeholder if thumbnail not available


  - Implement consistent thumbnail dimensions and styling
  - Add "Edit Thumbnail" button to event cards
  - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5, 11.1, 11.2, 11.3, 11.5_

- [ ] 8. Implement thumbnail upload UI and functionality
  - Create thumbnail upload modal/dialog component
  - Add file input for thumbnail selection
  - Implement client-side file validation (type and size)


  - Create JavaScript function to handle thumbnail upload via POST API
  - Create JavaScript function to handle thumbnail update via PUT API
  - Display upload progress and success/error messages
  - Update event card thumbnail display after successful upload
  - _Requirements: 4.1, 4.2, 6.1, 6.2, 6.3, 6.4, 6.5, 10.3, 11.1, 11.2, 11.3_

- [x] 9. Add photo viewing functionality to event cards

  - Add "View Photos" button to each event card
  - Create expandable/collapsible photo section in event card
  - Implement JavaScript function to fetch photos from GET API
  - Create responsive photo grid layout (3-4 columns desktop, 2 tablet, 1 mobile)
  - Display "No photos uploaded yet" message when event has no photos
  - Add loading indicator while fetching photos
  - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 12.1, 12.2, 12.3, 12.4, 12.5_


- [ ] 10. Implement photo deletion UI and functionality
  - Add delete button/icon to each photo thumbnail in grid
  - Show delete button on hover for better UX
  - Implement confirmation dialog before deletion
  - Create JavaScript function to call DELETE API endpoint
  - Remove photo from UI grid after successful deletion
  - Update event photo count display after deletion
  - Display error messages if deletion fails



  - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 10.2, 11.1, 11.2, 11.3_

- [ ] 11. Add thumbnail upload to event creation form
  - Add file input field for cover thumbnail in create event form
  - Update form submission to use FormData for multipart upload
  - Include thumbnail file in event creation request if provided
  - Display preview of selected thumbnail before submission
  - Show validation errors for invalid thumbnail files
  - Update event card to display new thumbnail after creation
  - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5, 10.3, 10.5, 13.1_

- [ ] 12. Implement comprehensive error handling
  - Add user-friendly error messages for all API failures
  - Implement proper HTTP status codes for all error scenarios
  - Add client-side validation with clear error messages
  - Handle network errors gracefully with retry options
  - Log errors on backend for debugging
  - Display toast/notification for success and error messages
  - _Requirements: 10.1, 10.2, 10.3, 10.4, 10.5_

- [ ] 13. Verify existing functionality preservation
  - Test event creation without thumbnail (should use default)
  - Test event deletion (should clean up all files including thumbnail)
  - Test QR code download functionality
  - Test photo upload to events
  - Test admin authentication and session management
  - Verify non-admin users cannot access photo management endpoints
  - _Requirements: 9.1, 9.2, 9.3, 9.4, 9.5, 13.1, 13.2, 13.3, 13.4, 13.5_

- [ ] 14. Synchronize thumbnails across user-facing pages
  - Update event_discovery.html to use cover_thumbnail instead of image field
  - Update homepage.html featured events to use cover_thumbnail
  - Update event_detail.html to use cover_thumbnail if displayed
  - Ensure fallback to default thumbnail when cover_thumbnail is not set
  - Test thumbnail display on all user pages after admin upload
  - Test thumbnail update reflects immediately on user pages
  - _Requirements: 13.1, 13.2, 13.3, 13.4, 13.5_

- [ ] 15. Testing and validation
  - Write unit tests for photo retrieval endpoint
  - Write unit tests for photo deletion with cleanup
  - Write unit tests for thumbnail upload and update
  - Test responsive design on mobile, tablet, and desktop
  - Test error scenarios (invalid files, missing permissions, network errors)
  - Perform manual testing of complete user flow
  - _Requirements: All requirements_
