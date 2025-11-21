"""
Database Connection Pool for improved performance
Optional: Use this for better database connection management
"""
from mysql.connector import pooling
import mysql.connector

class DatabasePool:
    _instance = None
    _pool = None
    
    def __new__(cls, config):
        if cls._instance is None:
            cls._instance = super(DatabasePool, cls).__new__(cls)
        return cls._instance
    
    def __init__(self, config):
        if self._pool is None:
            try:
                self._pool = pooling.MySQLConnectionPool(
                    pool_name="picme_pool",
                    pool_size=5,  # Adjust based on your needs
                    pool_reset_session=True,
                    **config
                )
                print("--- [DB POOL] Connection pool created successfully ---")
            except mysql.connector.Error as err:
                print(f"--- [DB POOL] Error creating pool: {err} ---")
                self._pool = None
    
    def get_connection(self):
        """Get a connection from the pool"""
        if self._pool:
            try:
                return self._pool.get_connection()
            except mysql.connector.Error as err:
                print(f"--- [DB POOL] Error getting connection: {err} ---")
                return None
        return None

# Usage in app.py:
# Replace get_db_connection() with:
# 
# from db_pool import DatabasePool
# db_pool = DatabasePool(DB_CONFIG)
# 
# def get_db_connection():
#     return db_pool.get_connection()
