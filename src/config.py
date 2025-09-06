"""
Configuration management for SQLite Viewer
"""

import json
import os


class ConfigManager:
    """Manages application configuration and saved databases"""

    def __init__(self, config_file='db_config.json'):
        self.config_file = config_file
        self.saved_databases = []
        self.last_connected = None
        self.load_config()

    def load_config(self):
        """Load configuration from file"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    self.saved_databases = config.get('saved_databases', [])
                    self.last_connected = config.get('last_connected')
            except json.JSONDecodeError:
                pass

    def save_config(self):
        """Save configuration to file"""
        config = {
            'saved_databases': self.saved_databases,
            'last_connected': self.last_connected
        }
        try:
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
        except IOError:
            pass

    def add_saved_database(self, db_info):
        """Add a database to saved databases"""
        # Remove if already exists
        self.saved_databases = [db for db in self.saved_databases
                               if db['path'] != db_info['path']]
        self.saved_databases.append(db_info)
        self.save_config()

    def remove_saved_database(self, db_path):
        """Remove a database from saved databases"""
        self.saved_databases = [db for db in self.saved_databases
                               if db['path'] != db_path]
        self.save_config()

    def get_saved_databases(self):
        """Get list of saved databases"""
        return self.saved_databases

    def set_last_connected(self, db_info):
        """Set the last connected database"""
        self.last_connected = db_info
        self.save_config()

    def get_last_connected(self):
        """Get the last connected database"""
        return self.last_connected
