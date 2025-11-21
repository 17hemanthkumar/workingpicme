# Implementation Plan: Separate Admin Authentication System

## Task List

- [x] 1. Database Setup
  - ✅ Admin table already created in XAMPP
  - Table name: `admin` (not `admins`)
  - Primary key: `admin_id` (not `id`)
  - Optional: Add index on email column if not exists
  - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5_

- [x] 2. Backend - Admin Authentication Routes




- [ ] 2.1 Create admin registration endpoint
  - Implement POST /admin/register route
  - Validate organization name, email, and password
  - Hash password using Werkzeug
  - INSERT INTO admin table (use admin_id column)
  - Handle duplicate email errors

  - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 8.1, 8.2, 8.3, 8.4, 8.5_

- [ ] 2.2 Create admin login endpoint
  - Implement POST /admin/login route
  - Validate email and password
  - SELECT FROM admin table (use admin_id column)
  - Create admin session on success

  - Return appropriate error messages
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 10.1, 10.2, 10.3, 10.4, 10.5_

- [x] 2.3 Create admin logout endpoint

  - Implement GET /admin/logout route


  - Clear all admin session data
  - Redirect to admin login page
  - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5_

- [x] 3. Backend - Session Management

- [ ] 3.1 Implement admin session creation
  - Store admin_logged_in flag
  - Store admin_id, admin_email, organization_name
  - Set session as modified
  - _Requirements: 4.1, 4.2_


- [ ] 3.2 Create admin_required decorator
  - Check for admin_logged_in in session
  - Redirect to admin login if not authenticated



  - Allow access if authenticated
  - _Requirements: 5.1, 5.2, 5.3_

- [ ] 3.3 Apply admin_required to protected routes
  - Add decorator to /event_organizer route
  - Add decorator to /api/create_event route
  - Add decorator to /api/upload_photos route

  - Add decorator to /api/events DELETE route
  - _Requirements: 5.4, 5.5_

- [ ] 4. Frontend - Admin Login Page
- [x] 4.1 Create admin_login.html



  - Design login form with email and password fields
  - Add "Login as Admin" button
  - Add link to admin signup
  - Add link to user login
  - Style with Tailwind CSS
  - _Requirements: 1.1, 6.2, 6.5_


- [ ] 4.2 Implement admin login JavaScript
  - Handle form submission
  - Send POST request to /admin/login
  - Handle success response (redirect to dashboard)
  - Handle error response (display error message)
  - _Requirements: 1.4, 1.5, 10.1_





- [ ] 5. Frontend - Admin Signup Page
- [ ] 5.1 Create admin_signup.html
  - Design signup form with organization name, email, password
  - Add "Register Organization" button

  - Add link to admin login
  - Add password strength indicator
  - Style with Tailwind CSS
  - _Requirements: 2.1, 6.4, 6.5_

- [ ] 5.2 Implement admin signup JavaScript
  - Handle form submission
  - Validate all fields are filled
  - Send POST request to /admin/register
  - Handle success response (redirect to login)
  - Handle error response (display error message)
  - _Requirements: 2.2, 2.4, 2.5, 10.2, 10.4_

- [ ] 6. Frontend - Update Navigation
- [ ] 6.1 Update index.html navigation
  - Add "Admin Login" link



  - Keep existing "User Login" link
  - Differentiate between admin and user access
  - _Requirements: 6.1, 6.2, 6.5_

- [x] 6.2 Update event_organizer.html

  - Display organization name from session
  - Update logout link to /admin/logout
  - Show admin-specific welcome message
  - _Requirements: 9.3_

- [ ] 7. Backend - Route Serving
- [ ] 7.1 Create admin page serving routes
  - Implement GET /admin/login route
  - Implement GET /admin/signup route
  - Serve admin_login.html and admin_signup.html
  - _Requirements: 6.2, 6.4_

- [ ] 7.2 Update event organizer route
  - Apply @admin_required decorator
  - Pass organization name to template
  - Maintain existing functionality
  - _Requirements: 9.1, 9.2, 9.4, 9.5_

- [ ] 8. Database Helper Functions
- [ ] 8.1 Create admin database queries
  - Function to check if admin email exists (SELECT FROM admin)
  - Function to create new admin (INSERT INTO admin)
  - Function to get admin by email (SELECT FROM admin WHERE email)
  - Function to verify admin credentials
  - Use admin_id as primary key in all queries
  - _Requirements: 2.3, 2.4, 3.1, 3.2, 3.3_

- [ ] 9. Security Enhancements
- [ ] 9.1 Implement password validation
  - Check minimum password length (6 characters)
  - Validate email format
  - Sanitize organization name input
  - _Requirements: 8.5, 10.4_

- [ ] 9.2 Add SQL injection prevention
  - Use parameterized queries for all database operations
  - Validate and sanitize all user inputs
  - _Requirements: 3.1, 3.2, 3.3_

- [ ] 10. Testing and Validation
- [ ] 10.1 Test admin registration flow
  - Register new admin with valid data
  - Test duplicate email handling
  - Test missing fields validation
  - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5_

- [ ] 10.2 Test admin login flow
  - Login with valid credentials
  - Test invalid credentials
  - Verify session creation
  - Verify redirect to dashboard
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5_

- [ ] 10.3 Test admin logout flow
  - Logout and verify session cleared
  - Verify redirect to login page
  - Test access to protected routes after logout
  - _Requirements: 7.1, 7.2, 7.3_

- [ ] 10.4 Test route protection
  - Access admin routes without login
  - Access admin routes with user login
  - Access admin routes with admin login
  - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5_

- [ ] 11. Documentation
- [ ] 11.1 Create admin setup guide
  - Document database setup steps
  - Document admin registration process
  - Document admin login process
  - _Requirements: All_

- [ ] 11.2 Update README
  - Add admin authentication section
  - Document admin vs user differences
  - Add troubleshooting guide
  - _Requirements: All_

## Implementation Order

1. **Database Setup** (Task 1) - Foundation
2. **Backend Authentication** (Tasks 2.1, 2.2, 2.3) - Core functionality
3. **Session Management** (Tasks 3.1, 3.2, 3.3) - Security
4. **Frontend Pages** (Tasks 4, 5) - User interface
5. **Navigation Updates** (Task 6) - Integration
6. **Route Serving** (Task 7) - Connectivity
7. **Database Helpers** (Task 8) - Optimization
8. **Security** (Task 9) - Hardening
9. **Testing** (Task 10) - Validation
10. **Documentation** (Task 11) - Completion

## Notes

- All password handling uses Werkzeug security functions
- Sessions are completely isolated between users and admins
- Existing user functionality remains unchanged
- Admin dashboard maintains all current features
- Database uses MySQL via XAMPP
- Frontend uses Tailwind CSS for styling
