# Database Mapping Reference

## Admin Table Structure (XAMPP)

### Table Name
```
admin  (NOT admins)
```

### Columns
```sql
admin_id            INT AUTO_INCREMENT PRIMARY KEY
organization_name   VARCHAR(100) NOT NULL
email               VARCHAR(100) NOT NULL UNIQUE
password            VARCHAR(255) NOT NULL
created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP
```

## Important Notes

### ⚠️ Column Name Differences
- Primary Key: `admin_id` (NOT `id`)
- Table Name: `admin` (NOT `admins`)

### SQL Query Examples

#### ✅ CORRECT Queries
```sql
-- Registration
INSERT INTO admin (organization_name, email, password) 
VALUES (%s, %s, %s)

-- Login
SELECT admin_id, organization_name, email, password 
FROM admin 
WHERE email = %s

-- Check if email exists
SELECT admin_id FROM admin WHERE email = %s
```

#### ❌ INCORRECT Queries (Don't use these)
```sql
-- Wrong table name
INSERT INTO admins (organization_name, email, password) VALUES (...)

-- Wrong column name
SELECT id, organization_name FROM admin WHERE email = %s
```

## Python Code Mapping

### Session Storage
```python
# Store admin_id (not id)
session['admin_id'] = admin['admin_id']
session['admin_email'] = admin['email']
session['organization_name'] = admin['organization_name']
session['admin_logged_in'] = True
```

### Database Queries
```python
# Registration
cursor.execute(
    "INSERT INTO admin (organization_name, email, password) VALUES (%s, %s, %s)",
    (organization_name, email, hashed_password)
)

# Login
cursor.execute(
    "SELECT admin_id, organization_name, email, password FROM admin WHERE email = %s",
    (email,)
)
admin = cursor.fetchone()

# Access admin_id
admin_id = admin['admin_id']  # NOT admin['id']
```

## Verification Checklist

Before running any query, verify:
- [ ] Table name is `admin` (not `admins`)
- [ ] Primary key is `admin_id` (not `id`)
- [ ] Using parameterized queries (%s placeholders)
- [ ] Column names match exactly

## Quick Reference

| Spec Document Says | Actual Database Has |
|-------------------|---------------------|
| `admins` table    | `admin` table       |
| `id` column       | `admin_id` column   |
| VARCHAR(255)      | VARCHAR(100)        |

**Always use the "Actual Database Has" column in your code!**
