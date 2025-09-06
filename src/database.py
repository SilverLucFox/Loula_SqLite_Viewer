"""
Database operations for SQLite Viewer
"""

import sqlite3
import os
import json


class DatabaseManager:
    """Handles all database operations"""

    def __init__(self):
        self.connection = None
        self.db_path = None
        self.db_name = None

    def connect(self, db_path, db_name):
        """Connect to a SQLite database"""
        try:
            self.connection = sqlite3.connect(db_path)
            self.db_path = db_path
            self.db_name = db_name
            return True
        except sqlite3.Error as e:
            print(f"Connection error: {e}")
            return False

    def disconnect(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()
            self.connection = None
            self.db_path = None
            self.db_name = None

    def get_tables(self):
        """Get list of all tables in the database"""
        if not self.connection:
            return []
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            return [row[0] for row in cursor.fetchall()]
        except sqlite3.Error:
            return []

    def get_table_data(self, table_name, limit=1000):
        """Get data from a specific table"""
        if not self.connection:
            return []
        try:
            cursor = self.connection.cursor()
            cursor.execute(f"SELECT * FROM {table_name} LIMIT {limit}")
            return cursor.fetchall()
        except sqlite3.Error:
            return []

    def get_table_schema(self, table_name):
        """Get schema information for a table"""
        if not self.connection:
            return []
        try:
            cursor = self.connection.cursor()
            cursor.execute(f"PRAGMA table_info({table_name});")
            return cursor.fetchall()
        except sqlite3.Error:
            return []

    def execute_sql(self, sql):
        """Execute a SQL statement"""
        if not self.connection:
            return "No database connected"
        try:
            cursor = self.connection.cursor()
            cursor.execute(sql)
            if sql.strip().upper().startswith('SELECT'):
                rows = cursor.fetchall()
                return rows
            else:
                self.connection.commit()
                return "Executed successfully"
        except sqlite3.Error as e:
            return f"Error: {e}"
