# Implementation Plan: Photo Management Enhancements

- [x] 1. Create database schema and download tracking backend

  - [x] 1.1 Create downloads table in database


    - Add migration script or direct SQL to create downloads table with columns: id, user_id, photo_url, event_id, event_name, downloaded_at
    - Add unique constraint on (user_id, photo_url) to prevent duplicates
    - Add foreign key constraint to users table
    - Add indexes for performance optimization
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5_



  - [ ] 1.2 Implement download tracking API endpoint
    - Create POST /api/download-photo route in app.py
    - Validate user authentication (require login)
    - Accept photo_url, event_id, event_name in request body
    - Insert download record into database with user_id from session
    - Handle duplicate downloads gracefully (return success if already exists)


    - Return JSON response with success status
    - _Requirements: 2.3, 2.4, 3.2, 3.3, 3.4_

  - [ ] 1.3 Implement downloads retrieval API endpoint
    - Create GET /api/my-downloads route in app.py

    - Validate user authentication


    - Query downloads table for current user's downloads
    - Order by downloaded_at DESC (most recent first)
    - Return JSON with downloads array and total count
    - _Requirements: 4.2, 9.2_



- [ ] 2. Add organization name to events
  - [ ] 2.1 Update event creation to include organization name
    - Modify event creation route to retrieve organization_name from admin session
    - Add organization_name field to event data structure
    - Store organization_name in events_data.json when creating new events


    - Handle cases where organization_name is not available (default to "Unknown Organizer")
    - _Requirements: 5.1, 5.4_

  - [ ] 2.2 Update event display to show organization name
    - Modify event_discovery.html to display organization name in event cards
    - Add organization name below or beside event name




    - Style organization name appropriately (smaller text, gray color)
    - Ensure organization name displays on all event listings
    - _Requirements: 5.2, 5.3, 5.5_

- [ ] 3. Implement photo lightbox component


  - [ ] 3.1 Create lightbox HTML structure
    - Add lightbox modal HTML to event_detail.html
    - Include close button, navigation arrows, and download button
    - Add hidden class by default
    - Use fixed positioning with z-50 for overlay
    - Style with semi-transparent black background

    - _Requirements: 1.1, 1.2, 1.3, 7.1_

  - [ ] 3.2 Implement lightbox JavaScript functionality
    - Create PhotoLightbox class or functions in JavaScript
    - Implement open() method to display lightbox with selected photo
    - Implement close() method (triggered by close button, ESC key, or background click)

    - Implement next() and previous() navigation methods

    - Track current photo index
    - Update image src when navigating
    - _Requirements: 1.1, 1.4, 7.2, 7.3_

  - [ ] 3.3 Add lightbox navigation controls
    - Show/hide previous arrow based on current index

    - Show/hide next arrow based on current index
    - Disable arrows at boundaries (first/last photo)
    - Add keyboard navigation (arrow keys)
    - Add smooth transitions between photos
    - _Requirements: 1.5, 7.1, 7.4, 7.5_

  - [ ] 3.4 Integrate lightbox with photo thumbnails
    - Add click event listeners to all photo thumbnails on event detail page

    - Pass photo array and clicked index to lightbox
    - Ensure lightbox opens with correct photo
    - Maintain photo order from event display
    - _Requirements: 1.1, 1.2_




- [ ] 4. Implement download functionality in lightbox
  - [ ] 4.1 Create download button in lightbox
    - Add Download button to lightbox UI
    - Style button with clear visibility (indigo background, white text)
    - Add download icon to button

    - Position button at bottom-center of lightbox
    - _Requirements: 2.1, 8.1, 8.2_

  - [ ] 4.2 Implement download button functionality
    - Add click event listener to download button
    - Get current photo URL from lightbox
    - Create download link and trigger browser download

    - Call download tracking API after download initiates
    - Show loading indicator during API call
    - Show success message after tracking completes
    - _Requirements: 2.2, 2.3, 2.5, 8.4, 8.5_

  - [x] 4.3 Add download button hover effects

    - Implement hover state styling
    - Add visual feedback on hover
    - Ensure button is accessible and clearly clickable
    - _Requirements: 8.3_

- [ ] 5. Create My Downloads page
  - [ ] 5.1 Create My Downloads route and template
    - Add GET /my_downloads route in app.py
    - Require user authentication
    - Create my_downloads.html template
    - Add navigation link to My Downloads in user menu
    - _Requirements: 4.1_

  - [ ] 5.2 Implement downloads grid display
    - Create responsive grid layout (2-4 columns based on screen size)
    - Display photo thumbnails in grid
    - Show event name for each photo
    - Show download date for each photo
    - Add empty state message when no downloads exist
    - _Requirements: 4.3, 4.4, 9.1, 9.2, 9.3, 9.4, 9.5_

  - [ ] 5.3 Add re-download functionality
    - Add re-download button for each photo
    - Implement click handler to download photo again

    - Show download button on hover or always visible




    - Provide visual feedback on download

    - _Requirements: 4.5, 9.4_

  - [ ] 5.4 Integrate lightbox with My Downloads page
    - Make photos clickable to open in lightbox
    - Pass downloads array to lightbox



    - Enable navigation between downloaded photos
    - Include download button in lightbox on this page
    - _Requirements: 4.5_


- [ ] 6. Implement event search functionality
  - [x] 6.1 Add search bar to event discovery page

    - Add search input field at top of event_discovery.html
    - Style search bar prominently
    - Add search icon
    - Add placeholder text "Search by organization name..."
    - Add clear button when text is entered
    - _Requirements: 6.1_

  - [ ] 6.2 Implement client-side search filtering
    - Add JavaScript event listener for search input
    - Implement filterEvents() function
    - Filter events by organization name (case-insensitive)
    - Update displayed events in real-time as user types
    - Show all events when search is empty
    - _Requirements: 6.2, 6.3, 6.4, 6.5_

  - [ ] 6.3 Add search result feedback
    - Show count of filtered results
    - Display "No events found" message when no matches
    - Highlight matching organization names (optional enhancement)
    - _Requirements: 6.5_

- [ ] 7. Performance optimizations
  - [ ] 7.1 Implement lazy loading for photo thumbnails
    - Add lazy loading attribute to img tags
    - Use Intersection Observer for custom lazy loading if needed
    - Load thumbnails as they come into viewport
    - _Requirements: 10.1_

  - [ ] 7.2 Add caching for downloads list
    - Implement server-side caching for downloads API (5 minutes)
    - Invalidate cache when new download is added
    - Use session-based or memory-based cache
    - _Requirements: 10.2_

  - [ ] 7.3 Optimize image URLs and preloading
    - Use optimized/compressed image URLs for thumbnails
    - Preload next/previous photos when viewing in lightbox
    - Implement image preloading logic
    - _Requirements: 10.3, 10.4_

- [ ] 8. Testing and validation
  - [ ] 8.1 Test lightbox functionality
    - Test opening lightbox from thumbnails
    - Test navigation between photos
    - Test closing lightbox (button, ESC, background click)
    - Test keyboard navigation
    - _Requirements: 1.1, 1.4, 1.5, 7.1, 7.2, 7.3_

  - [ ] 8.2 Test download tracking
    - Test download button in lightbox
    - Verify download tracking API records downloads
    - Test duplicate download prevention
    - Verify downloads appear in My Downloads
    - _Requirements: 2.2, 2.3, 3.2, 3.3_

  - [ ] 8.3 Test My Downloads page
    - Test page loads with user's downloads
    - Test grid layout responsiveness
    - Test re-download functionality
    - Test lightbox integration
    - Test empty state display
    - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5, 9.1, 9.2, 9.3, 9.4, 9.5_

  - [ ] 8.4 Test organization display and search
    - Test organization name displays on event cards
    - Test search filters events correctly
    - Test case-insensitive search
    - Test search with no results
    - Test search clear functionality
    - _Requirements: 5.2, 5.5, 6.1, 6.2, 6.3, 6.4, 6.5_

  - [ ] 8.5 Test error handling
    - Test download without login (should require auth)
    - Test download with invalid photo URL
    - Test My Downloads without login
    - Test database errors are handled gracefully
    - _Requirements: All error handling requirements_
