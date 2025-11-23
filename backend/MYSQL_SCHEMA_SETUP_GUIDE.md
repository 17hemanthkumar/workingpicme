# MySQL Schema Setup Guide

## 📋 Overview

This guide will help you add the enhanced face detection tables to your existing MySQL `picme_db` database in XAMPP.

---

## ✅ Prerequisites

Before starting, make sure:
- ✓ XAMPP is installed and running
- ✓ MySQL service is started in XAMPP Control Panel
- ✓ Database `picme_db` exists
- ✓ You have access to phpMyAdmin

---

## 🚀 Step-by-Step Installation

### Step 1: Start XAMPP Services

1. Open **XAMPP Control Panel**
2. Start **Apache** (if not already running)
3. Start **MySQL** (if not already running)
4. Both should show green "Running" status

### Step 2: Open phpMyAdmin

1. Click the **Admin** button next to MySQL in XAMPP Control Panel
   - OR go to: `http://localhost/phpmyadmin/`
2. You should see the phpMyAdmin interface

### Step 3: Select Your Database

1. In the left sidebar, click on **`picme_db`**
2. You should see your existing `users` table

### Step 4: Import the Schema

1. Click on the **Import** tab at the top
2. Click **Choose File** button
3. Navigate to: `backend/enhanced_schema_mysql.sql`
4. Select the file
5. Scroll down and click **Go** button
6. Wait for the import to complete

### Step 5: Verify Installation

You should see a success message like:
```
Import has been successfully finished, 6 queries executed.
```

Check that these tables now exist in your database:
- ✓ photos
- ✓ persons
- ✓ face_detections
- ✓ face_encodings
- ✓ facial_features
- ✓ person_photos

### Step 6: Run Python Test Script

Open a terminal in the `backend` folder and run:

```bash
python test_mysql_schema.py
```

You should see:
```
✅ ALL MYSQL DATABASE SCHEMA TESTS PASSED
```

---

## 📊 What Was Created

### 6 New Tables

1. **`photos`** (13 columns)
   - Stores photo metadata
   - Tracks processing status
   - Links to events

2. **`persons`** (10 columns)
   - Person registry with UUID
   - Tracks photo counts
   - Stores confidence scores

3. **`face_detections`** (14 columns)
   - Detected faces with bounding boxes
   - Angle estimates (frontal, profile, side)
   - Quality scores (blur, lighting, size)

4. **`face_encodings`** (9 columns)
   - 128D face encodings
   - Multiple angles per person
   - Quality-based primary selection

5. **`facial_features`** (17 columns)
   - Detailed facial measurements
   - Landmark data
   - Attributes (glasses, facial hair, age, gender)

6. **`person_photos`** (8 columns)
   - Links persons to photos
   - Tracks group vs individual photos
   - Match confidence scores

### 27 Performance Indexes

Optimized indexes for:
- Fast photo lookups by event
- Quick person searches by UUID/name
- Efficient face detection queries
- Angle-based encoding retrieval

### 4 Automatic Triggers

- Auto-update person photo counts
- Auto-update photo face counts
- Auto-set has_faces flag
- Auto-update timestamps

### 2 Summary Views

- `person_summary` - Person stats with photo counts
- `photo_summary` - Photo stats with face information

---

## 🔍 Verification Queries

Run these in phpMyAdmin SQL tab to verify:

### Check Tables
```sql
SELECT TABLE_NAME, TABLE_ROWS 
FROM information_schema.TABLES 
WHERE TABLE_SCHEMA = 'picme_db' 
AND TABLE_NAME IN ('photos', 'persons', 'face_detections', 'face_encodings', 'facial_features', 'person_photos');
```

### Check Indexes
```sql
SELECT TABLE_NAME, INDEX_NAME 
FROM information_schema.STATISTICS 
WHERE TABLE_SCHEMA = 'picme_db' 
AND INDEX_NAME LIKE 'idx_%'
ORDER BY TABLE_NAME;
```

### Check Triggers
```sql
SELECT TRIGGER_NAME, EVENT_OBJECT_TABLE 
FROM information_schema.TRIGGERS 
WHERE TRIGGER_SCHEMA = 'picme_db';
```

### Check Views
```sql
SELECT TABLE_NAME 
FROM information_schema.VIEWS 
WHERE TABLE_SCHEMA = 'picme_db';
```

---

## 🔧 Troubleshooting

### Problem: "Table already exists" error

**Solution**: The schema uses `CREATE TABLE IF NOT EXISTS`, so this shouldn't happen. If it does:
1. The tables might already be created
2. Check if they exist in phpMyAdmin
3. If they're incomplete, drop them and re-import

### Problem: "Cannot connect to database"

**Solution**:
1. Make sure MySQL is running in XAMPP
2. Check that `picme_db` database exists
3. Verify credentials in `app.py` match your MySQL setup

### Problem: "Foreign key constraint fails"

**Solution**:
1. Make sure you imported the FULL SQL file
2. Tables must be created in order (photos and persons first)
3. Re-import the complete schema

### Problem: Python test script fails

**Solution**:
1. Make sure `mysql-connector-python` is installed:
   ```bash
   pip install mysql-connector-python
   ```
2. Check database credentials in `test_mysql_schema.py`
3. Verify XAMPP MySQL is running

---

## 📝 Database Configuration

Your app uses these settings (from `app.py`):

```python
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'picme_db'
}
```

If your MySQL has a password, update it in:
- `backend/app.py`
- `backend/test_mysql_schema.py`

---

## 🎯 Next Steps

After successful installation:

1. ✅ **Task 1.1 Complete** - Database schema created
2. ➡️ **Task 1.2** - Implement Enhanced Face Detector
3. ➡️ **Task 2.1** - Implement Deep Feature Extractor
4. ➡️ Continue with remaining tasks

---

## 📚 Schema Documentation

### Table Relationships

```
photos (1) ←→ (many) face_detections
persons (1) ←→ (many) face_detections
persons (1) ←→ (many) face_encodings
face_detections (1) ←→ (1) facial_features
face_detections (1) ←→ (many) face_encodings
persons (many) ←→ (many) photos (via person_photos)
```

### Foreign Key Constraints

- `face_detections.photo_id` → `photos.id` (CASCADE DELETE)
- `face_detections.person_id` → `persons.id` (SET NULL)
- `face_encodings.face_detection_id` → `face_detections.id` (CASCADE DELETE)
- `face_encodings.person_id` → `persons.id` (CASCADE DELETE)
- `facial_features.face_detection_id` → `face_detections.id` (CASCADE DELETE)
- `person_photos.person_id` → `persons.id` (CASCADE DELETE)
- `person_photos.photo_id` → `photos.id` (CASCADE DELETE)

---

## ✅ Success Checklist

- [ ] XAMPP MySQL is running
- [ ] phpMyAdmin is accessible
- [ ] `picme_db` database exists
- [ ] SQL file imported successfully
- [ ] 6 tables created
- [ ] 27 indexes created
- [ ] 4 triggers created
- [ ] 2 views created
- [ ] Python test script passes
- [ ] Ready for Task 1.2

---

## 🆘 Need Help?

If you encounter issues:

1. Check the error message in phpMyAdmin
2. Verify XAMPP services are running
3. Review the troubleshooting section above
4. Check that all files are in the correct location
5. Ensure you have the latest version of the SQL file

---

**Status**: Ready for Implementation  
**Database**: MySQL (picme_db)  
**Tables**: 6 created  
**Next Task**: 1.2 - Enhanced Face Detector
