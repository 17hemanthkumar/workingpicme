"""Check what tables exist in the database"""
import sqlite3

conn = sqlite3.connect('database.db')
cursor = conn.cursor()

cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()

print("Database tables:")
for table in tables:
    print(f"  • {table[0]}")

conn.close()
