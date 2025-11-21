# Design Document: Separate Admin Authentication System

## Overview

This design implements a dual authentication system for PicMe, separating admin (event organizer) authentication from regular user authentication. Admins will have dedicated login/signup pages and sessions, while maintaining access to the existing event organizer dashboard.

## Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     PicMe Application                        │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────────┐         ┌──────────────────┐          │
│  │   User Auth      │         │   Admin Auth     │          │
│  │                  │         │                  │          │
│  │ /login           │         │ /admin/login     │          │
│  │ /signup          │         │ /admin/signup    │          │
│  │ /logout          │         │ /admin/logout    │          │
│  │                  │         │                  │          │
│  │ Session:         │         │ Session:         │          │
│  │ - user_id        │         │ - admin_id       │          │
│  │ - user_email     │         │ - admin_email    │          │
│  │ - logged_in      │         │ - organization   │          │
│  │                  │         │ - admin_logged_in│          │
│  └──────────────────┘         └──────────────────┘          │
│           │                            │                     │
│           ├────────────────────────────┤                     │
│           │                            │                     │
│  ┌────────▼────────┐         ┌────────▼────────┐            │
│  │  User Routes    │         │  Admin Routes   │            │
│  │                 │         │                 │            │
│  │ @login_required │         │ @admin_required │            │
│  │                 │         │                 │            │
│  │ - /homepage     │         │ - /event_org... │            │
│  │ - /events       │         │ - /api/create...│            │
│  │ - /my_photos    │         │ - /api/upload...│            │
│  └─────────────────┘         └─────────────────┘            │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

### Database Schema

#### Existing: users table
```sql
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    full_name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### New: admin table (Already Created)
```sql
CREATE TABLE admin (
    admin_id INT AUTO_INCREMENT PRIMARY KEY,
    organization_name VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Note:** Table already exists in picme_db database via XAMPP.

## Components and Interfaces

### 1. Admin Authentication Routes

#### POST /admin/register
**Purpose:** Register a new admin account

**Request:**
```json
{
  "organizationName": "Tech Events Inc",
  "email": "admin@techevents.com",
  "password": "securepass123"
}
```

**Response (Success):**
```json
{
  "success": true,
  "message": "Admin registration successful!"
}
```

**Response (Error):**
```json
{
  "success": false,
  "error": "Email already registered"
}
```

#### POST /admin/login
**Purpose:** Authenticate admin and create session

**Request:**
```json
{
  "email": "admin@techevents.com",
  "password": "securepass123"
}
```

**Response (Success):**
```json
{
  "success": true,
  "message": "Login successful!",
  "redirect": "/event_organizer"
}
```

**Response (Error):**
```json
{
  "success": false,
  "error": "Invalid email or password"
}
```

#### GET /admin/logout
**Purpose:** Clear admin session and redirect

**Response:** Redirect to /admin/login

### 2. Admin Decorator

```python
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('admin_logged_in'):
            return redirect(url_for('serve_admin_login_page'))
        return f(*args, **kwargs)
    return decorated_function
```

### 3. Session Structure

#### User Session
```python
{
    'logged_in': True,
    'user_id': 123,
    'user_email': 'user@example.com'
}
```

#### Admin Session
```python
{
    'admin_logged_in': True,
    'admin_id': 456,
    'admin_email': 'admin@techevents.com',
    'organization_name': 'Tech Events Inc'
}
```

### 4. Frontend Pages

#### /admin/login (admin_login.html)
- Email input field
- Password input field
- "Login as Admin" button
- Link to admin signup
- Link to user login
- Organization branding

#### /admin/signup (admin_signup.html)
- Organization name input
- Email input field
- Password input field
- "Register Organization" button
- Link to admin login
- Terms and conditions

## Data Models

### Admin Model (Python representation)
```python
class Admin:
    admin_id: int  # Note: column name is admin_id, not id
    organization_name: str
    email: str
    password: str  # hashed
    created_at: datetime
```

**Important:** All database queries must use:
- Table name: `admin` (not `admins`)
- Primary key: `admin_id` (not `id`)

### Session Data
```python
# Admin session keys
ADMIN_SESSION_KEYS = [
    'admin_logged_in',
    'admin_id',
    'admin_email',
    'organization_name'
]

# User session keys
USER_SESSION_KEYS = [
    'logged_in',
    'user_id',
    'user_email'
]
```

## Error Handling

### Authentication Errors
- **401 Unauthorized:** Invalid credentials
- **403 Forbidden:** Not logged in as admin
- **409 Conflict:** Email already exists
- **500 Internal Server Error:** Database connection failed

### Error Messages
```python
ERROR_MESSAGES = {
    'invalid_credentials': 'Invalid email or password',
    'email_exists': 'Email already registered',
    'db_error': 'Database connection failed',
    'missing_fields': 'All fields are required',
    'not_authorized': 'Admin access required'
}
```

## Security Considerations

### Password Hashing
```python
from werkzeug.security import generate_password_hash, check_password_hash

# Registration
hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

# Login
is_valid = check_password_hash(stored_hash, provided_password)
```

### Session Security
- Use Flask's secure session cookies
- Set `app.secret_key` to a strong random value
- Enable `SESSION_COOKIE_HTTPONLY = True`
- Enable `SESSION_COOKIE_SECURE = True` in production
- Set appropriate session timeout

### SQL Injection Prevention
- Use parameterized queries
- Never concatenate user input into SQL
```python
# Good
cursor.execute("SELECT * FROM admins WHERE email = %s", (email,))

# Bad
cursor.execute(f"SELECT * FROM admins WHERE email = '{email}'")
```

## Testing Strategy

### Unit Tests
1. Test admin registration with valid data
2. Test admin registration with duplicate email
3. Test admin login with valid credentials
4. Test admin login with invalid credentials
5. Test admin_required decorator
6. Test session management
7. Test password hashing

### Integration Tests
1. Test complete admin registration flow
2. Test complete admin login flow
3. Test admin logout flow
4. Test admin access to protected routes
5. Test user cannot access admin routes
6. Test admin cannot access user-only routes

### Manual Testing
1. Register new admin account
2. Login as admin
3. Access event organizer dashboard
4. Create an event
5. Logout as admin
6. Verify cannot access dashboard
7. Login as regular user
8. Verify cannot access admin routes

## Migration Plan

### Step 1: Database Setup
```sql
-- Create admins table
CREATE TABLE admins (
    id INT AUTO_INCREMENT PRIMARY KEY,
    organization_name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Add index for faster lookups
CREATE INDEX idx_admin_email ON admins(email);
```

### Step 2: Backend Implementation
1. Create admin authentication routes
2. Create admin_required decorator
3. Update event organizer routes with admin_required
4. Create admin session management
5. Add admin logout route

### Step 3: Frontend Implementation
1. Create admin_login.html
2. Create admin_signup.html
3. Update navigation to include admin links
4. Update event_organizer.html to show organization name

### Step 4: Testing
1. Test admin registration
2. Test admin login
3. Test admin access control
4. Test session isolation
5. Test logout functionality

## Performance Considerations

### Database Queries
- Use connection pooling (already implemented)
- Add index on admin email column
- Cache admin session data

### Session Management
- Use server-side sessions
- Set appropriate session timeout (30 minutes)
- Clean up expired sessions

## Deployment Notes

### Environment Variables
```python
# Add to .env or config
ADMIN_SESSION_TIMEOUT = 1800  # 30 minutes
SESSION_COOKIE_SECURE = True  # HTTPS only
SESSION_COOKIE_HTTPONLY = True
```

### Database Migration
```bash
# Run SQL script to create admins table
mysql -u root -p picme_db < create_admins_table.sql
```

### Verification Checklist
- [ ] Admins table created
- [ ] Admin routes accessible
- [ ] User routes still work
- [ ] Sessions properly isolated
- [ ] Passwords properly hashed
- [ ] Error handling works
- [ ] Logout clears sessions
- [ ] Dashboard shows organization name
