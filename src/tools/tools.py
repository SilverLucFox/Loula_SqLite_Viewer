"""
SQL Tools for Loula's SQLite Viewer
"""

import curses
from src.ui.ui_utils import UIUtils


class SQLTools:
    """SQL tool functions"""

    def __init__(self, db_manager, config_manager, ui_utils):
        self.db = db_manager
        self.config = config_manager
        self.ui = ui_utils

    def sql_input_screen(self, stdscr):
        """SQL query input screen"""
        h, w = stdscr.getmaxyx()
        stdscr.clear()
        self.ui.draw_main_title(stdscr)

        title = "SQL Query"
        stdscr.addstr(2, (w - len(title)) // 2, title, curses.A_BOLD | curses.color_pair(2))

        stdscr.addstr(4, 2, "Enter SQL query:", curses.color_pair(5))
        stdscr.addstr(5, 2, ">" , curses.color_pair(4))

        # Simple input handling
        curses.echo()
        sql = stdscr.getstr(5, 4, w - 6).decode('utf-8')
        curses.noecho()

        if sql:
            result = self.db.execute_sql(sql)
            stdscr.clear()
            stdscr.addstr(0, 0, "SQL Result:", curses.A_BOLD)
            if isinstance(result, list):
                for i, row in enumerate(result):
                    y = 2 + i
                    if y >= h - 2:
                        break
                    row_str = " | ".join(str(cell) for cell in row)
                    stdscr.addstr(y, 2, row_str)
            else:
                stdscr.addstr(2, 2, str(result))

            stdscr.addstr(h - 1, 0, "Press any key to continue")
            stdscr.refresh()
            stdscr.getch()

    def insert_record_tool(self, stdscr):
        """Insert record tool"""
        h, w = stdscr.getmaxyx()
        stdscr.clear()
        self.ui.draw_main_title(stdscr)

        title = "Insert Record"
        stdscr.addstr(2, (w - len(title)) // 2, title, curses.A_BOLD | curses.color_pair(2))

        stdscr.addstr(4, 2, "Table name:", curses.color_pair(5))
        stdscr.addstr(5, 2, ">" , curses.color_pair(4))

        curses.echo()
        table_name = stdscr.getstr(5, 4, w - 6).decode('utf-8').strip()
        curses.noecho()

        if not table_name:
            return

        # Get table schema
        schema = self.db.get_table_schema(table_name)
        if not schema:
            stdscr.clear()
            stdscr.addstr(1, 2, f"Table '{table_name}' not found!", curses.color_pair(7))
            stdscr.addstr(h - 1, 0, "Press any key to continue")
            stdscr.refresh()
            stdscr.getch()
            return

        # Collect values for each column
        values = []
        for i, (col_id, col_name, col_type, *_) in enumerate(schema):
            y = 7 + i * 2
            if y >= h - 2:
                break

            stdscr.addstr(y, 2, f"{col_name} ({col_type}):", curses.A_BOLD | curses.color_pair(3))
            stdscr.addstr(y + 1, 2, ">" , curses.color_pair(4))

            curses.echo()
            value = stdscr.getstr(y + 1, 4, w - 6).decode('utf-8').strip()
            curses.noecho()

            # Handle NULL values
            if value.upper() == 'NULL' or value == '':
                values.append(None)
            else:
                values.append(value)

        # Generate INSERT SQL
        columns = [col[1] for col in schema]
        placeholders = ', '.join(['?' for _ in columns])
        sql = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({placeholders})"

        try:
            result = self.db.execute_sql(sql, values)
            stdscr.clear()
            stdscr.addstr(1, 2, "Record inserted successfully!", curses.color_pair(3))
        except Exception as e:
            stdscr.clear()
            stdscr.addstr(1, 2, f"Error inserting record: {str(e)}", curses.color_pair(7))

        stdscr.addstr(h - 1, 0, "Press any key to continue")
        stdscr.refresh()
        stdscr.getch()

    def update_record_tool(self, stdscr):
        """Update record tool"""
        h, w = stdscr.getmaxyx()
        stdscr.clear()
        self.ui.draw_main_title(stdscr)

        title = "Update Record"
        stdscr.addstr(2, (w - len(title)) // 2, title, curses.A_BOLD | curses.color_pair(2))

        stdscr.addstr(4, 2, "Table name:", curses.color_pair(5))
        stdscr.addstr(5, 2, ">" , curses.color_pair(4))

        curses.echo()
        table_name = stdscr.getstr(5, 4, w - 6).decode('utf-8').strip()
        curses.noecho()

        if not table_name:
            return

        # Get table schema
        schema = self.db.get_table_schema(table_name)
        if not schema:
            stdscr.clear()
            stdscr.addstr(1, 2, f"Table '{table_name}' not found!", curses.color_pair(7))
            stdscr.addstr(h - 1, 0, "Press any key to continue")
            stdscr.refresh()
            stdscr.getch()
            return

        # Get WHERE condition
        stdscr.addstr(7, 2, "WHERE condition (e.g., id = 1):", curses.color_pair(5))
        stdscr.addstr(8, 2, ">" , curses.color_pair(4))

        curses.echo()
        where_condition = stdscr.getstr(8, 4, w - 6).decode('utf-8').strip()
        curses.noecho()

        if not where_condition:
            return

        # Collect new values
        set_parts = []
        for i, (col_id, col_name, col_type, *_) in enumerate(schema):
            y = 10 + i * 2
            if y >= h - 4:
                break

            stdscr.addstr(y, 2, f"New {col_name} ({col_type}):", curses.A_BOLD | curses.color_pair(3))
            stdscr.addstr(y + 1, 2, ">" , curses.color_pair(4))

            curses.echo()
            value = stdscr.getstr(y + 1, 4, w - 6).decode('utf-8').strip()
            curses.noecho()

            if value.upper() != 'NULL' and value != '':
                if col_type.upper() in ['TEXT', 'VARCHAR', 'CHAR']:
                    set_parts.append(f"{col_name} = '{value}'")
                else:
                    set_parts.append(f"{col_name} = {value}")

        if not set_parts:
            stdscr.clear()
            stdscr.addstr(1, 2, "No values to update!", curses.color_pair(7))
            stdscr.addstr(h - 1, 0, "Press any key to continue")
            stdscr.refresh()
            stdscr.getch()
            return

        # Generate UPDATE SQL
        sql = f"UPDATE {table_name} SET {', '.join(set_parts)} WHERE {where_condition}"

        try:
            result = self.db.execute_sql(sql)
            stdscr.clear()
            stdscr.addstr(1, 2, f"Updated {result} record(s) successfully!", curses.color_pair(3))
        except Exception as e:
            stdscr.clear()
            stdscr.addstr(1, 2, f"Error updating record: {str(e)}", curses.color_pair(7))

        stdscr.addstr(h - 1, 0, "Press any key to continue")
        stdscr.refresh()
        stdscr.getch()

    def delete_record_tool(self, stdscr):
        """Delete record tool"""
        h, w = stdscr.getmaxyx()
        stdscr.clear()
        self.ui.draw_main_title(stdscr)

        title = "Delete Record"
        stdscr.addstr(2, (w - len(title)) // 2, title, curses.A_BOLD | curses.color_pair(2))

        stdscr.addstr(4, 2, "Table name:", curses.color_pair(5))
        stdscr.addstr(5, 2, ">" , curses.color_pair(4))

        curses.echo()
        table_name = stdscr.getstr(5, 4, w - 6).decode('utf-8').strip()
        curses.noecho()

        if not table_name:
            return

        stdscr.addstr(7, 2, "WHERE condition (e.g., id = 1):", curses.color_pair(5))
        stdscr.addstr(8, 2, ">" , curses.color_pair(4))

        curses.echo()
        where_condition = stdscr.getstr(8, 4, w - 6).decode('utf-8').strip()
        curses.noecho()

        if not where_condition:
            return

        # Confirm deletion
        stdscr.addstr(10, 2, f"Are you sure you want to delete from {table_name}?", curses.color_pair(7))
        stdscr.addstr(11, 2, f"WHERE {where_condition}", curses.color_pair(7))
        stdscr.addstr(13, 2, "Type 'yes' to confirm:", curses.color_pair(5))
        stdscr.addstr(14, 2, ">" , curses.color_pair(4))

        curses.echo()
        confirmation = stdscr.getstr(14, 4, 10).decode('utf-8').strip().lower()
        curses.noecho()

        if confirmation != 'yes':
            return

        # Generate DELETE SQL
        sql = f"DELETE FROM {table_name} WHERE {where_condition}"

        try:
            result = self.db.execute_sql(sql)
            stdscr.clear()
            stdscr.addstr(1, 2, f"Deleted {result} record(s) successfully!", curses.color_pair(3))
        except Exception as e:
            stdscr.clear()
            stdscr.addstr(1, 2, f"Error deleting record: {str(e)}", curses.color_pair(7))

        stdscr.addstr(h - 1, 0, "Press any key to continue")
        stdscr.refresh()
        stdscr.getch()

    def create_table_tool(self, stdscr):
        """Create table tool"""
        h, w = stdscr.getmaxyx()
        stdscr.clear()
        self.ui.draw_main_title(stdscr)

        title = "Create Table"
        stdscr.addstr(2, (w - len(title)) // 2, title, curses.A_BOLD | curses.color_pair(2))

        stdscr.addstr(4, 2, "Table name:", curses.color_pair(5))
        stdscr.addstr(5, 2, ">" , curses.color_pair(4))

        curses.echo()
        table_name = stdscr.getstr(5, 4, w - 6).decode('utf-8').strip()
        curses.noecho()

        if not table_name:
            return

        stdscr.addstr(7, 2, "Column definitions (e.g., id INTEGER PRIMARY KEY, name TEXT):", curses.color_pair(5))
        stdscr.addstr(8, 2, ">" , curses.color_pair(4))

        curses.echo()
        columns = stdscr.getstr(8, 4, w - 6).decode('utf-8').strip()
        curses.noecho()

        if not columns:
            return

        # Generate CREATE TABLE SQL
        sql = f"CREATE TABLE {table_name} ({columns})"

        try:
            self.db.execute_sql(sql)
            stdscr.clear()
            stdscr.addstr(1, 2, f"Table '{table_name}' created successfully!", curses.color_pair(3))
        except Exception as e:
            stdscr.clear()
            stdscr.addstr(1, 2, f"Error creating table: {str(e)}", curses.color_pair(7))

        stdscr.addstr(h - 1, 0, "Press any key to continue")
        stdscr.refresh()
        stdscr.getch()

    def drop_table_tool(self, stdscr):
        """Drop table tool"""
        h, w = stdscr.getmaxyx()
        stdscr.clear()
        self.ui.draw_main_title(stdscr)

        title = "Drop Table"
        stdscr.addstr(2, (w - len(title)) // 2, title, curses.A_BOLD | curses.color_pair(2))

        stdscr.addstr(4, 2, "Table name:", curses.color_pair(5))
        stdscr.addstr(5, 2, ">" , curses.color_pair(4))

        curses.echo()
        table_name = stdscr.getstr(5, 4, w - 6).decode('utf-8').strip()
        curses.noecho()

        if not table_name:
            return

        # Confirm deletion
        stdscr.addstr(7, 2, f"Are you sure you want to drop table '{table_name}'?", curses.color_pair(7))
        stdscr.addstr(9, 2, "Type 'yes' to confirm:", curses.color_pair(5))
        stdscr.addstr(10, 2, ">" , curses.color_pair(4))

        curses.echo()
        confirmation = stdscr.getstr(10, 4, 10).decode('utf-8').strip().lower()
        curses.noecho()

        if confirmation != 'yes':
            return

        # Generate DROP TABLE SQL
        sql = f"DROP TABLE {table_name}"

        try:
            self.db.execute_sql(sql)
            stdscr.clear()
            stdscr.addstr(1, 2, f"Table '{table_name}' dropped successfully!", curses.color_pair(3))
        except Exception as e:
            stdscr.clear()
            stdscr.addstr(1, 2, f"Error dropping table: {str(e)}", curses.color_pair(7))

        stdscr.addstr(h - 1, 0, "Press any key to continue")
        stdscr.refresh()
        stdscr.getch()

    def view_table_structure_tool(self, stdscr):
        """View table structure tool"""
        h, w = stdscr.getmaxyx()
        stdscr.clear()
        self.ui.draw_main_title(stdscr)

        title = "View Table Structure"
        stdscr.addstr(2, (w - len(title)) // 2, title, curses.A_BOLD | curses.color_pair(2))

        stdscr.addstr(4, 2, "Table name:", curses.color_pair(5))
        stdscr.addstr(5, 2, ">" , curses.color_pair(4))

        curses.echo()
        table_name = stdscr.getstr(5, 4, w - 6).decode('utf-8').strip()
        curses.noecho()

        if not table_name:
            return

        # Get table schema
        schema = self.db.get_table_schema(table_name)
        if not schema:
            stdscr.clear()
            stdscr.addstr(1, 2, f"Table '{table_name}' not found!", curses.color_pair(7))
            stdscr.addstr(h - 1, 0, "Press any key to continue")
            stdscr.refresh()
            stdscr.getch()
            return

        # Display schema
        stdscr.clear()
        self.ui.draw_main_title(stdscr)
        stdscr.addstr(2, (w - len(f"Structure of {table_name}")) // 2, f"Structure of {table_name}", curses.A_BOLD | curses.color_pair(2))

        for i, (col_id, col_name, col_type, *_) in enumerate(schema):
            y = 4 + i
            if y >= h - 2:
                break
            stdscr.addstr(y, 2, f"{col_name}: {col_type}", curses.color_pair(5))

        stdscr.addstr(h - 1, 0, "Press any key to continue")
        stdscr.refresh()
        stdscr.getch()

    def custom_sql_tool(self, stdscr):
        """Custom SQL query tool"""
        h, w = stdscr.getmaxyx()
        stdscr.clear()
        self.ui.draw_main_title(stdscr)

        title = "Custom SQL Query"
        stdscr.addstr(2, (w - len(title)) // 2, title, curses.A_BOLD | curses.color_pair(2))

        stdscr.addstr(4, 2, "Enter SQL query:", curses.color_pair(5))
        stdscr.addstr(5, 2, ">" , curses.color_pair(4))

        curses.echo()
        sql = stdscr.getstr(5, 4, w - 6).decode('utf-8')
        curses.noecho()

        if not sql:
            return

        try:
            result = self.db.execute_sql(sql)
            stdscr.clear()
            stdscr.addstr(0, 0, "SQL Result:", curses.A_BOLD)
            if isinstance(result, list):
                for i, row in enumerate(result):
                    y = 2 + i
                    if y >= h - 2:
                        break
                    row_str = " | ".join(str(cell) for cell in row)
                    stdscr.addstr(y, 2, row_str)
            else:
                stdscr.addstr(2, 2, str(result))
        except Exception as e:
            stdscr.clear()
            stdscr.addstr(1, 2, f"Error executing SQL: {str(e)}", curses.color_pair(7))

        stdscr.addstr(h - 1, 0, "Press any key to continue")
        stdscr.refresh()
        stdscr.getch()
