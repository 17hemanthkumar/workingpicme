# Implementation Plan: Event Editing Functionality

- [x] 1. Implement backend API endpoint for fetching single event


  - Create GET `/api/events/<event_id>` endpoint
  - Return event details in JSON format
  - Handle event not found error
  - Add error logging for debugging
  - _Requirements: 2.2_


- [ ] 2. Implement backend API endpoint for updating events
  - Create PUT `/api/events/<event_id>` endpoint with admin authentication
  - Validate all required fields (name, location, date, category, organization_name)
  - Validate field lengths (max 200 characters for text fields)
  - Check event ownership (only creator can edit)
  - Update only specified fields while preserving all other data
  - Implement atomic file write with backup
  - Return updated event data on success
  - Handle validation errors with specific error messages
  - Handle authorization errors (401, 403)
  - Handle not found errors (404)

  - _Requirements: 3.1-3.5, 4.1-4.5, 5.1-5.5, 6.1-6.5, 7.1-7.5, 8.1-8.5, 9.1-9.5, 12.1-12.5, 13.1-13.5, 14.1-14.5_

- [ ] 3. Add Edit button to event cards in admin dashboard
  - Add Edit button to each event card in event_organizer.html
  - Style button to match existing dashboard design (Tailwind CSS)
  - Position button next to other action buttons
  - Add edit icon (pencil) to button
  - Make button responsive for mobile devices

  - Add onclick handler to open edit modal
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 15.1, 15.2, 15.3, 15.4, 15.5_

- [ ] 4. Create edit modal HTML structure
  - Add edit modal container with backdrop to event_organizer.html
  - Create modal header with title and close button
  - Add form with input fields for all editable fields
  - Add Event Name input field with validation
  - Add Location input field with validation
  - Add Date input field (date picker)
  - Add Category dropdown with predefined options
  - Add Organization Name input field with validation
  - Add error message placeholders for each field
  - Add Cancel and Save buttons
  - Add loading indicator overlay

  - Style modal to match existing dashboard design
  - Make modal responsive for mobile devices
  - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 15.1, 15.2, 15.3, 15.4, 15.5_

- [ ] 5. Implement JavaScript function to open edit modal
  - Create `openEditModal(eventId)` function
  - Fetch event details from GET `/api/events/<event_id>` endpoint
  - Populate form fields with current event data

  - Handle date formatting for date input field
  - Show modal and prevent body scrolling
  - Handle fetch errors with user-friendly messages
  - _Requirements: 2.1, 2.2, 2.3_

- [ ] 6. Implement JavaScript function to close edit modal
  - Create `closeEditModal()` function

  - Hide modal and restore body scrolling
  - Clear form fields
  - Clear validation errors
  - Reset current event ID
  - _Requirements: 2.5, 16.1, 16.2, 16.3, 16.4, 16.5_

- [ ] 7. Implement client-side form validation
  - Create `validateEditForm()` function
  - Validate event name is not empty and within 200 characters
  - Validate location is not empty and within 200 characters
  - Validate date is not empty and in valid format

  - Validate category is selected
  - Validate organization name is not empty and within 200 characters
  - Show field-specific error messages below invalid inputs
  - Highlight invalid fields with red border
  - Return validation status (true/false)
  - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.5_

- [ ] 8. Implement form submission handler
  - Add submit event listener to edit form
  - Prevent default form submission
  - Run client-side validation

  - Show loading indicator during save
  - Collect form data into JSON object
  - Send PUT request to `/api/events/<event_id>` endpoint
  - Handle successful response (show success message, close modal, reload events)
  - Handle error response (show error message)
  - Hide loading indicator after completion


  - _Requirements: 9.1, 9.2, 9.3, 9.4, 9.5, 14.1, 14.2, 14.3, 14.4, 14.5_

- [ ] 9. Implement modal close on Escape key and backdrop click
  - Add keydown event listener for Escape key
  - Close modal when Escape is pressed
  - Add click event listener to modal backdrop
  - Close modal when clicking outside modal content
  - _Requirements: 16.3, 16.4_

- [ ] 10. Implement real-time UI updates after save
  - Reload events list after successful save
  - Update event card with new data without full page refresh
  - Ensure updated data displays immediately on admin dashboard
  - _Requirements: 10.1, 10.2_

- [ ] 11. Verify data integrity preservation
  - Test that photos are preserved after event edit
  - Test that cover_thumbnail is preserved after event edit
  - Test that QR code is preserved after event edit
  - Test that photos_count is preserved after event edit
  - Test that event ID and created_at are preserved after event edit
  - _Requirements: 12.1, 12.2, 12.3, 12.4, 12.5_

- [ ] 12. Verify real-time reflection on user pages
  - Test that updated event name displays on event discovery page
  - Test that updated location displays on event discovery page
  - Test that updated organization name displays on event discovery page
  - Test that updated event displays on homepage featured events
  - Test that updated event displays on event detail page
  - _Requirements: 10.3, 10.4, 10.5_

- [ ] 13. Verify search functionality with updated data
  - Test search by updated event name returns correct results
  - Test search by updated organization name returns correct results
  - Test search with partial match of updated names
  - Verify old names no longer return the event in search
  - _Requirements: 11.1, 11.2, 11.3, 11.4, 11.5_

- [ ] 14. Test authorization and security
  - Test that only logged-in admins can access edit endpoint
  - Test that admin can only edit their own events
  - Test that attempting to edit another admin's event returns 403 error
  - Test that Edit button only shows for events created by logged-in admin
  - Verify input sanitization prevents XSS attacks
  - _Requirements: 13.1, 13.2, 13.3, 13.4, 13.5_

- [ ] 15. Test error handling scenarios
  - Test network error during save shows appropriate message
  - Test validation errors display correctly
  - Test server error shows user-friendly message
  - Test editing non-existent event shows error
  - Verify all errors are logged on backend
  - _Requirements: 14.1, 14.2, 14.3, 14.4, 14.5_

- [ ] 16. Verify existing features preservation
  - Test that event creation still works
  - Test that event deletion still works
  - Test that photo upload still works
  - Test that photo viewing still works
  - Test that photo deletion still works
  - Test that thumbnail upload/update still works
  - Test that QR code download still works
  - _Requirements: 17.1, 17.2, 17.3, 17.4, 17.5_

- [ ] 17. Test responsive design and UI consistency
  - Test edit modal on desktop screens
  - Test edit modal on tablet screens
  - Test edit modal on mobile screens
  - Verify button styles match existing dashboard
  - Verify color scheme matches (indigo primary, gray secondary)
  - Verify spacing and padding are consistent
  - _Requirements: 15.1, 15.2, 15.3, 15.4, 15.5_

- [ ] 18. Final integration testing
  - Create new event as admin A
  - Edit event as admin A (verify success)
  - Try to edit event as admin B (verify failure)
  - Verify updated event displays correctly on all pages
  - Search for event by new name (verify found)
  - Search for event by old name (verify not found)
  - Verify photos and thumbnails intact
  - Test complete user flow from admin edit to user view
  - _Requirements: All requirements_
