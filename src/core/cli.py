"""
Command Line Interface for Loula's SQLite Viewer
"""

import cmd
import shlex
import readline
from src.database.database import DatabaseManager
from src.config.config import ConfigManager

# Fix for Python 3.13 on Windows: set readline.backend to avoid AttributeError
readline.backend = 'readline'


class SQLiteCLI(cmd.Cmd):
    """Command Line Interface for SQLite database management"""

    intro = "Welcome to Loula's SQLite Viewer CLI. Type 'help' for commands."
    prompt = 'sqlite> '

    def __init__(self):
        super().__init__()
        self.db = DatabaseManager()
        self.config = ConfigManager()

        # Load last connected database
        last_db = self.config.get_last_connected()
        if last_db:
            self.db.connect(last_db['path'], last_db['name'])

    def do_connect(self, arg):
        """Connect to a SQLite database: connect <path> <name>"""
        try:
            args = shlex.split(arg)
            if len(args) != 2:
                print("Usage: connect <path> <name>")
                return
            path, name = args
            if not self.db.connect(path, name):
                return

            # Save to config
            db_info = {'path': path, 'name': name, 'color': 3}
            self.config.add_saved_database(db_info)
            self.config.set_last_connected(db_info)
            print(f"Connected to database: {name}")

        except ValueError:
            print("Invalid arguments.")

    def do_disconnect(self, arg):
        """Disconnect from the current database."""
        self.db.disconnect()
        print("Disconnected.")

    def do_tables(self, arg):
        """List all tables in the database."""
        tables = self.db.get_tables()
        if tables:
            print("Tables:")
            for table in tables:
                print(f"  {table}")
        else:
            print("No tables found.")

    def do_schema(self, arg):
        """Show schema of a table: schema <table_name>"""
        if not arg:
            print("Usage: schema <table_name>")
            return

        schema = self.db.get_table_schema(arg)
        if schema:
            print(f"Schema for table '{arg}':")
            print("Column Name | Type | Not Null | Default | Primary Key")
            for col in schema:
                print(f"{col[1]} | {col[2]} | {col[3]} | {col[4]} | {col[5]}")
        else:
            print(f"Table '{arg}' not found.")

    def do_sql(self, arg):
        """Execute a SQL statement: sql <statement>"""
        if not arg:
            print("Usage: sql <statement>")
            return

        result = self.db.execute_sql(arg)
        if isinstance(result, list):
            for row in result:
                print(row)
        else:
            print(result)

    def do_quit(self, arg):
        """Quit Loula's SQLite Viewer."""
        self.db.disconnect()
        print("Goodbye.")
        return True

    def default(self, line):
        print(f"Unknown command: {line}. Type 'help' for available commands.")
