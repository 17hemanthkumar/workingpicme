import sqlite3
import os

db_path = 'database.db'

if not os.path.exists(db_path):
    print("Database does not exist")
else:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in cursor.fetchall()]
    print(f"Database exists with {len(tables)} tables:")
    for table in tables:
        print(f"  - {table}")
    conn.close()
