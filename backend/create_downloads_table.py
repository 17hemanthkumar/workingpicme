"""
Database migration script to create the downloads table
Run this script to add the downloads table to your existing picme_db database
"""

import mysql.connector

DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'picme_db'
}

def create_downloads_table():
    """Create the downloads table in the database"""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # Check if table already exists
        cursor.execute("""
            SELECT COUNT(*)
            FROM information_schema.tables 
            WHERE table_schema = 'picme_db' 
            AND table_name = 'downloads'
        """)
        
        if cursor.fetchone()[0] > 0:
            print("✓ Downloads table already exists")
            cursor.close()
            conn.close()
            return True
        
        # Create downloads table
        create_table_query = """
        CREATE TABLE downloads (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            photo_url VARCHAR(500) NOT NULL,
            event_id VARCHAR(50) NOT NULL,
            event_name VARCHAR(255) NOT NULL,
            downloaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE KEY unique_download (user_id, photo_url),
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            INDEX idx_user_downloads (user_id, downloaded_at)
        )
        """
        
        cursor.execute(create_table_query)
        conn.commit()
        
        print("✓ Downloads table created successfully!")
        
        cursor.close()
        conn.close()
        return True
        
    except mysql.connector.Error as err:
        print(f"✗ Error creating downloads table: {err}")
        return False

if __name__ == "__main__":
    print("Creating downloads table...")
    create_downloads_table()
