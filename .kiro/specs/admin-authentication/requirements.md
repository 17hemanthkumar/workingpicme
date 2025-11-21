# Requirements Document: Separate Admin Authentication System

## Introduction

This feature implements a dedicated admin authentication system separate from the regular user login. Event organizers will have their own login/signup flow with organization details, while maintaining access to the existing event organizer dashboard functionality.

## Glossary

- **Admin**: An event organizer who manages events and uploads photos
- **User**: A regular attendee who views events and scans their face to find photos
- **Admin Session**: Server-side session data for authenticated admins
- **User Session**: Server-side session data for authenticated users
- **Organization**: The company or entity that the admin represents
- **Dashboard**: The event organizer interface for creating and managing events

## Requirements

### Requirement 1: Separate Admin Authentication

**User Story:** As an event organizer, I want a dedicated admin login system separate from regular users, so that my organization's access is properly managed.

#### Acceptance Criteria

1. WHEN an admin visits the admin login page, THE System SHALL display a login form with email and password fields
2. WHEN an admin submits valid credentials, THE System SHALL authenticate against the admin table in the database
3. WHEN authentication succeeds, THE System SHALL create an admin session with admin_id, admin_email, and organization_name
4. WHEN authentication succeeds, THE System SHALL redirect the admin to the event organizer dashboard
5. WHEN authentication fails, THE System SHALL display an error message and remain on the login page

### Requirement 2: Admin Registration

**User Story:** As a new event organizer, I want to register my organization with an admin account, so that I can start creating events.

#### Acceptance Criteria

1. WHEN an admin visits the admin signup page, THE System SHALL display a registration form with organization name, email, and password fields
2. WHEN an admin submits the registration form with valid data, THE System SHALL hash the password using Werkzeug security
3. WHEN registration data is valid, THE System SHALL store the admin credentials in the admins table
4. WHEN an email already exists in the admins table, THE System SHALL return an error message
5. WHEN registration succeeds, THE System SHALL redirect to the admin login page with a success message

### Requirement 3: Database Schema

**User Story:** As a system administrator, I want admin data stored securely in a separate table, so that admin and user data are properly isolated.

#### Acceptance Criteria

1. THE System SHALL create an admins table with columns: id, organization_name, email, password, created_at
2. THE System SHALL set id as the primary key with auto-increment
3. THE System SHALL set email as unique to prevent duplicate registrations
4. THE System SHALL store passwords as hashed values using Werkzeug generate_password_hash
5. THE System SHALL set created_at with a default timestamp

### Requirement 4: Session Management

**User Story:** As an admin, I want my login session to be secure and separate from user sessions, so that my access is properly managed.

#### Acceptance Criteria

1. WHEN an admin logs in successfully, THE System SHALL store admin_logged_in=True in the session
2. WHEN an admin logs in successfully, THE System SHALL store admin_id, admin_email, and organization_name in the session
3. WHEN an admin accesses protected routes, THE System SHALL verify admin_logged_in is True
4. WHEN an admin logs out, THE System SHALL clear all admin session data
5. WHEN a user logs in, THE System SHALL NOT have access to admin routes

### Requirement 5: Admin Route Protection

**User Story:** As a system administrator, I want admin routes protected by authentication, so that only logged-in admins can access the dashboard.

#### Acceptance Criteria

1. THE System SHALL create an admin_required decorator function
2. WHEN an unauthenticated user accesses an admin route, THE System SHALL redirect to the admin login page
3. WHEN an authenticated admin accesses an admin route, THE System SHALL allow access
4. THE System SHALL apply admin_required to /event_organizer route
5. THE System SHALL apply admin_required to all event creation and management routes

### Requirement 6: Separate Login Pages

**User Story:** As a user, I want clear separation between user and admin login pages, so that I don't accidentally try to log in to the wrong system.

#### Acceptance Criteria

1. THE System SHALL serve user login at /login route
2. THE System SHALL serve admin login at /admin/login route
3. THE System SHALL serve user signup at /signup route
4. THE System SHALL serve admin signup at /admin/signup route
5. THE System SHALL display clear labels indicating "Admin Login" vs "User Login"

### Requirement 7: Admin Logout

**User Story:** As an admin, I want to securely log out of my admin session, so that my account remains secure.

#### Acceptance Criteria

1. WHEN an admin clicks logout, THE System SHALL clear all admin session data
2. WHEN logout completes, THE System SHALL redirect to the admin login page
3. THE System SHALL provide an admin logout route at /admin/logout
4. WHEN a user logs out, THE System SHALL NOT affect admin sessions
5. WHEN an admin logs out, THE System SHALL NOT affect user sessions

### Requirement 8: Password Security

**User Story:** As a system administrator, I want admin passwords stored securely, so that accounts are protected from unauthorized access.

#### Acceptance Criteria

1. THE System SHALL hash all admin passwords using Werkzeug generate_password_hash before storage
2. THE System SHALL verify passwords using Werkzeug check_password_hash during login
3. THE System SHALL NOT store plain text passwords in the database
4. THE System SHALL use a secure hashing algorithm (pbkdf2:sha256)
5. THE System SHALL validate password strength (minimum 6 characters)

### Requirement 9: Dashboard Access

**User Story:** As an admin, I want to access the event organizer dashboard after login, so that I can manage my events.

#### Acceptance Criteria

1. WHEN an admin logs in successfully, THE System SHALL redirect to /event_organizer
2. WHEN an admin accesses /event_organizer without login, THE System SHALL redirect to /admin/login
3. THE System SHALL display the admin's organization name in the dashboard
4. THE System SHALL maintain all existing dashboard functionality
5. THE System SHALL allow admins to create, edit, and delete events

### Requirement 10: Error Handling

**User Story:** As an admin, I want clear error messages when login or registration fails, so that I can correct any issues.

#### Acceptance Criteria

1. WHEN admin login fails, THE System SHALL display "Invalid email or password"
2. WHEN admin registration fails due to duplicate email, THE System SHALL display "Email already registered"
3. WHEN database connection fails, THE System SHALL display "Database connection failed"
4. WHEN required fields are missing, THE System SHALL display "All fields are required"
5. THE System SHALL return appropriate HTTP status codes (400, 401, 409, 500)
