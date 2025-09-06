"""
Text User Interface for Loula's SQLite Viewer
"""

import curses
import os
from database import DatabaseManager
from config import ConfigManager


class SQLiteTUI:
    """Text User Interface for SQLite database management"""

    def __init__(self):
        self.db = DatabaseManager()
        self.config = ConfigManager()
        self.current_menu = 'main'
        self.selected_option = 0
        self.db_color = 3  # Default green

        # Load last connected database
        last_db = self.config.get_last_connected()
        if last_db and os.path.exists(last_db.get('path', '')):
            self.db.connect(last_db['path'], last_db['name'])
            self.db_color = last_db.get('color', 3)

    def save_database_to_list(self):
        """Add current database to saved databases"""
        if self.db.db_path and self.db.db_name:
            db_info = {
                'path': self.db.db_path,
                'name': self.db.db_name,
                'color': getattr(self, 'db_color', 3)
            }
            self.config.add_saved_database(db_info)

    def select_color_screen(self, stdscr):
        """Color selection screen"""
        h, w = stdscr.getmaxyx()
        colors = [
            ("Green", 3),
            ("Blue", 1),
            ("Red", 7),
            ("Yellow", 2),
            ("Cyan", 6),
            ("Magenta", 5)
        ]

        selected = 0
        while True:
            stdscr.clear()
            title = "Select Database Color"
            stdscr.addstr(0, 0, "=" * w, curses.color_pair(1))
            stdscr.addstr(1, (w - len(title)) // 2, title, curses.A_BOLD | curses.color_pair(2))

            for i, (name, color_id) in enumerate(colors):
                y = 3 + i
                if i == selected:
                    stdscr.addstr(y, 2, f"> {name}", curses.A_REVERSE | curses.color_pair(4))
                else:
                    stdscr.addstr(y, 2, f"  {name}", curses.color_pair(color_id))

            stdscr.addstr(h - 1, 0, "Use ↑↓ to select color, Enter to confirm, 'q' to cancel", curses.color_pair(6))
            stdscr.refresh()

            key = stdscr.getch()
            if key == curses.KEY_UP:
                selected = (selected - 1) % len(colors)
            elif key == curses.KEY_DOWN:
                selected = (selected + 1) % len(colors)
            elif key == 10 or key == 13:  # Enter
                return colors[selected][1]
            elif key == ord('q'):
                return None

    def connection_screen(self, stdscr):
        """Database connection screen"""
        h, w = stdscr.getmaxyx()

        # Connection type selection
        stdscr.clear()
        title = "Connection Type"
        stdscr.addstr(0, 0, "=" * w, curses.color_pair(1))
        stdscr.addstr(1, (w - len(title)) // 2, title, curses.A_BOLD | curses.color_pair(2))

        options = ["Connect to Saved Database", "Connect to New Database"]
        selected = 0

        while True:
            for i, option in enumerate(options):
                y = 3 + i
                if i == selected:
                    stdscr.addstr(y, 2, f"> {option}", curses.A_REVERSE | curses.color_pair(4))
                else:
                    stdscr.addstr(y, 2, f"  {option}", curses.color_pair(5))

            stdscr.addstr(h - 1, 0, "Use ↑↓ to select, Enter to confirm", curses.color_pair(6))
            stdscr.refresh()

            key = stdscr.getch()
            if key == curses.KEY_UP:
                selected = (selected - 1) % len(options)
            elif key == curses.KEY_DOWN:
                selected = (selected + 1) % len(options)
            elif key == 10 or key == 13:  # Enter
                if selected == 0:  # Saved database
                    return self.connect_saved_screen(stdscr)
                else:  # New database
                    return self.connect_new_screen(stdscr)
            elif key == 27:  # Escape
                return

    def connect_saved_screen(self, stdscr):
        """Connect to saved database screen"""
        h, w = stdscr.getmaxyx()
        saved_dbs = self.config.get_saved_databases()

        if not saved_dbs:
            stdscr.clear()
            stdscr.addstr(1, 2, "No saved databases found!", curses.color_pair(7))
            stdscr.addstr(3, 2, "Use 'Connect to New Database' first.", curses.color_pair(5))
            stdscr.addstr(h - 1, 0, "Press any key to continue")
            stdscr.refresh()
            stdscr.getch()
            return

        selected = 0
        while True:
            stdscr.clear()
            title = "Select Saved Database"
            stdscr.addstr(0, 0, "=" * w, curses.color_pair(1))
            stdscr.addstr(1, (w - len(title)) // 2, title, curses.A_BOLD | curses.color_pair(2))

            for i, db in enumerate(saved_dbs):
                y = 3 + i
                if y >= h - 2:
                    break
                name = db['name']
                color = db.get('color', 3)
                if i == selected:
                    stdscr.addstr(y, 2, f"> {name}", curses.A_REVERSE | curses.color_pair(4))
                else:
                    stdscr.addstr(y, 2, f"  {name}", curses.color_pair(color))

            stdscr.addstr(h - 1, 0, "Use ↑↓ to select, Enter to connect, 'd' to delete, Escape to cancel", curses.color_pair(6))
            stdscr.refresh()

            key = stdscr.getch()
            if key == curses.KEY_UP:
                selected = (selected - 1) % len(saved_dbs)
            elif key == curses.KEY_DOWN:
                selected = (selected + 1) % len(saved_dbs)
            elif key == 10 or key == 13:  # Enter
                db = saved_dbs[selected]
                if self.db.connect(db['path'], db['name']):
                    self.config.set_last_connected(db)
                    stdscr.clear()
                    stdscr.addstr(1, 2, f"Connected to: {self.db.db_name}", curses.color_pair(db.get('color', 3)))
                    stdscr.addstr(h - 1, 0, "Press any key to continue")
                    stdscr.refresh()
                    stdscr.getch()
                    return
            elif key == ord('d'):  # Delete
                self.config.remove_saved_database(saved_dbs[selected]['path'])
                saved_dbs = self.config.get_saved_databases()
                if not saved_dbs:
                    return
                selected = min(selected, len(saved_dbs) - 1)
            elif key == 27:  # Escape
                return

    def connect_new_screen(self, stdscr):
        """Connect to new database screen"""
        h, w = stdscr.getmaxyx()
        stdscr.clear()

        title = "Connect to New Database"
        stdscr.addstr(0, 0, "=" * w, curses.color_pair(1))
        stdscr.addstr(1, (w - len(title)) // 2, title, curses.A_BOLD | curses.color_pair(2))

        stdscr.addstr(3, 2, "Database Path:", curses.color_pair(5))
        stdscr.addstr(4, 2, ">" , curses.color_pair(4))

        stdscr.addstr(6, 2, "Database Name:", curses.color_pair(5))
        stdscr.addstr(7, 2, ">" , curses.color_pair(4))

        # Input for path
        curses.echo()
        path = stdscr.getstr(4, 4, w - 6).decode('utf-8').strip()

        if not path:
            return

        # Input for name
        name = stdscr.getstr(7, 4, w - 6).decode('utf-8').strip()
        curses.noecho()

        if not name:
            name = os.path.splitext(os.path.basename(path))[0]

        # Validate path
        if not os.path.exists(path):
            stdscr.clear()
            stdscr.addstr(1, 2, f"Error: File '{path}' does not exist!", curses.color_pair(7))
            stdscr.addstr(h - 1, 0, "Press any key to continue")
            stdscr.refresh()
            stdscr.getch()
            return

        # Select color
        color = self.select_color_screen(stdscr)
        if color is None:
            return

        # Connect
        if self.db.connect(path, name):
            db_info = {'path': path, 'name': name, 'color': color}
            self.config.add_saved_database(db_info)
            self.config.set_last_connected(db_info)

            # Success message
            stdscr.clear()
            stdscr.addstr(1, 2, f"Successfully connected to: {name}", curses.color_pair(color))
            stdscr.addstr(h - 1, 0, "Press any key to continue")
            stdscr.refresh()
            stdscr.getch()

    def format_table_data(self, data, schema, max_width):
        """Format table data with proper column alignment"""
        if not data or not schema:
            return [], []

        # Get column names
        col_names = [col[1] for col in schema]

        # Calculate column widths
        col_widths = []
        for i, col_name in enumerate(col_names):
            # Start with column name length
            max_col_width = len(col_name)

            # Check data in this column
            for row in data:
                if i < len(row):
                    cell_content = str(row[i]) if row[i] is not None else "NULL"
                    max_col_width = max(max_col_width, len(cell_content))

            # Limit column width to prevent overflow
            max_col_width = min(max_col_width, 20)  # Max 20 chars per column
            col_widths.append(max_col_width)

        # Calculate total width needed
        total_width = sum(col_widths) + len(col_widths) * 3 + 1  # spaces between columns

        # If too wide, reduce column widths proportionally
        if total_width > max_width - 4:
            scale_factor = (max_width - 4 - len(col_widths) * 3 - 1) / sum(col_widths)
            col_widths = [max(5, int(width * scale_factor)) for width in col_widths]

        # Format header
        header_parts = []
        for i, col_name in enumerate(col_names):
            width = col_widths[i]
            if len(col_name) > width:
                col_name = col_name[:width-3] + "..."
            header_parts.append(f"{col_name:<{width}}")

        formatted_header = " │ ".join(header_parts)
        formatted_separator = "─┼─".join("─" * width for width in col_widths)

        # Format data rows
        formatted_rows = []
        for row in data:
            row_parts = []
            for i, cell in enumerate(row):
                if i >= len(col_widths):
                    break
                width = col_widths[i]
                cell_content = str(cell) if cell is not None else "NULL"
                if len(cell_content) > width:
                    cell_content = cell_content[:width-3] + "..."
                row_parts.append(f"{cell_content:<{width}}")

            formatted_rows.append(" │ ".join(row_parts))

        return [formatted_header, formatted_separator], formatted_rows

    def split_screen_table_browser(self, stdscr):
        """Split screen interface: left panel for table list, right panel for data"""
        h, w = stdscr.getmaxyx()

        # Create windows for split screen
        left_width = max(20, w // 4)
        right_width = w - left_width - 1

        # Create windows
        left_win = curses.newwin(h, left_width, 0, 0)
        right_win = curses.newwin(h, right_width, 0, left_width + 1)

        # Get tables
        tables = self.db.get_tables()
        if not tables:
            return

        selected_table = 0
        table_page = 0
        selected_row = 0  # Track selected row in the current table
        rows_per_page = h - 6  # Leave space for headers and instructions
        table_selected = False  # Track if a table has been selected

        while True:
            # Clear windows
            left_win.clear()
            right_win.clear()

            # Draw left panel (table list)
            left_win.addstr(0, 0, "=" * left_width, curses.color_pair(1))
            left_win.addstr(1, 1, "Tables", curses.A_BOLD | curses.color_pair(2))

            for i, table in enumerate(tables):
                if i >= h - 4:  # Leave space for instructions
                    break
                y = 3 + i
                if i == selected_table:
                    left_win.addstr(y, 1, f"> {table}", curses.A_REVERSE | curses.color_pair(4))
                else:
                    left_win.addstr(y, 1, f"  {table}", curses.color_pair(5))

            left_win.addstr(h - 2, 1, "↑↓ select table" if not table_selected else "Table selected", curses.color_pair(6))
            left_win.addstr(h - 1, 1, "Enter select" if not table_selected else "Esc back", curses.color_pair(6))

            # Draw right panel (table data)
            if table_selected:
                current_table = tables[selected_table]
                data = self.db.get_table_data(current_table, limit=1000)  # Get more data for pagination

                right_win.addstr(0, 0, "=" * right_width, curses.color_pair(1))
                title = f"{current_table} (Page {table_page + 1})"
                right_win.addstr(1, 1, title, curses.A_BOLD | curses.color_pair(2))

                if data:
                    # Calculate pagination
                    start_idx = table_page * rows_per_page
                    end_idx = start_idx + rows_per_page
                    page_data = data[start_idx:end_idx]

                    # Display column headers and data with proper formatting
                    try:
                        schema = self.db.get_table_schema(current_table)
                        if schema:
                            headers, formatted_rows = self.format_table_data(page_data, schema, right_width)

                            # Display headers
                            right_win.addstr(3, 1, headers[0], curses.A_BOLD | curses.color_pair(3))
                            if len(headers) > 1:
                                right_win.addstr(4, 1, headers[1], curses.color_pair(3))
                                data_start_y = 6
                            else:
                                data_start_y = 5

                            # Display data rows
                            for i, row_str in enumerate(formatted_rows):
                                y = data_start_y + i
                                if y >= h - 4:  # Leave space for instructions
                                    break
                                if i == selected_row:
                                    right_win.addstr(y, 1, f"> {row_str}", curses.A_REVERSE | curses.color_pair(4))
                                else:
                                    right_win.addstr(y, 1, f"  {row_str}", curses.color_pair(5))
                        else:
                            # Fallback to simple display if no schema
                            data_start_y = 3
                            for i, row in enumerate(page_data):
                                y = data_start_y + i
                                if y >= h - 4:
                                    break
                                row_str = " | ".join(str(cell) for cell in row)
                                if len(row_str) > right_width - 4:
                                    row_str = row_str[:right_width-7] + "..."
                                if i == selected_row:
                                    right_win.addstr(y, 1, f"> {row_str}", curses.A_REVERSE | curses.color_pair(4))
                                else:
                                    right_win.addstr(y, 1, f"  {row_str}", curses.color_pair(5))
                    except Exception as e:
                        # Fallback on error
                        data_start_y = 3
                        right_win.addstr(3, 1, f"Error displaying table: {str(e)}", curses.color_pair(7))

                    # Pagination info
                    total_pages = (len(data) + rows_per_page - 1) // rows_per_page
                    if total_pages > 1:
                        page_info = f"Page {table_page + 1}/{total_pages} ({len(data)} rows)"
                        right_win.addstr(h - 3, 1, page_info, curses.color_pair(6))

                    # Record position indicator
                    current_page_data = data[start_idx:end_idx]
                    if current_page_data:
                        total_records = len(data)
                        current_record_global = start_idx + selected_row + 1  # 1-based indexing
                        record_info = f"Record {current_record_global} of {total_records}"
                        right_win.addstr(h - 4, 1, record_info, curses.color_pair(6))
                else:
                    right_win.addstr(3, 1, "No data in table", curses.color_pair(7))
            else:
                # No table selected - show instructions
                right_win.addstr(0, 0, "=" * right_width, curses.color_pair(1))
                right_win.addstr(1, 1, "Table Browser", curses.A_BOLD | curses.color_pair(2))
                right_win.addstr(3, 1, "Use arrow keys to select a table", curses.color_pair(5))
                right_win.addstr(4, 1, "Press Enter to browse its records", curses.color_pair(5))

            # Instructions
            if table_selected:
                right_win.addstr(h - 2, 1, "↑↓ select record", curses.color_pair(6))
                right_win.addstr(h - 1, 1, "Enter view, ←→ page, Esc back", curses.color_pair(6))
            else:
                right_win.addstr(h - 2, 1, "Select a table first", curses.color_pair(6))
                right_win.addstr(h - 1, 1, "", curses.color_pair(6))

            # Refresh windows
            left_win.refresh()
            right_win.refresh()

            # Handle input
            key = stdscr.getch()

            if not table_selected:
                # Table selection mode
                if key == curses.KEY_UP:
                    selected_table = (selected_table - 1) % len(tables)
                elif key == curses.KEY_DOWN:
                    selected_table = (selected_table + 1) % len(tables)
                elif key == 10 or key == 13:  # Enter - select table
                    table_selected = True
                    selected_row = 0
                    table_page = 0
                elif key == 27:  # Escape
                    break
            else:
                # Record selection mode
                if key == curses.KEY_UP:
                    if selected_row > 0:
                        selected_row -= 1
                elif key == curses.KEY_DOWN:
                    current_page_data = data[start_idx:end_idx] if data else []
                    if selected_row < len(current_page_data) - 1:
                        selected_row += 1
                elif key == curses.KEY_LEFT:
                    if table_page > 0:
                        table_page -= 1
                        selected_row = 0  # Reset row selection when changing pages
                elif key == curses.KEY_RIGHT:
                    data = self.db.get_table_data(current_table, limit=1000)
                    max_pages = (len(data) + rows_per_page - 1) // rows_per_page
                    if table_page < max_pages - 1:
                        table_page += 1
                        selected_row = 0  # Reset row selection when changing pages
                elif key == 10 or key == 13:  # Enter - view selected record
                    if data:
                        current_page_data = data[start_idx:end_idx]
                        if selected_row < len(current_page_data):
                            selected_record = current_page_data[selected_row]
                            self.view_record_details(stdscr, current_table, selected_record, schema)
                elif key == 27:  # Escape - back to table selection
                    table_selected = False
                    selected_row = 0

    def view_record_details(self, stdscr, table_name, record, schema):
        """View detailed information for a selected record"""
        h, w = stdscr.getmaxyx()
        stdscr.clear()

        # Title
        title = f"Record Details - {table_name}"
        stdscr.addstr(0, 0, "=" * w, curses.color_pair(1))
        stdscr.addstr(1, (w - len(title)) // 2, title, curses.A_BOLD | curses.color_pair(2))

        if schema and record:
            # Display each field with its value
            for i, (col_info, value) in enumerate(zip(schema, record)):
                y = 3 + i * 2
                if y >= h - 2:
                    break

                # Field name
                field_name = col_info[1]  # Column name
                field_type = col_info[2]  # Column type
                stdscr.addstr(y, 2, f"{field_name} ({field_type}):", curses.A_BOLD | curses.color_pair(3))

                # Field value
                value_str = str(value) if value is not None else "NULL"
                # Handle long values by wrapping or truncating
                if len(value_str) > w - 10:
                    value_str = value_str[:w-13] + "..."

                stdscr.addstr(y + 1, 4, value_str, curses.color_pair(5))
        else:
            # Fallback for records without schema
            stdscr.addstr(3, 2, "Record data:", curses.A_BOLD | curses.color_pair(3))
            for i, value in enumerate(record):
                y = 5 + i
                if y >= h - 2:
                    break
                value_str = str(value) if value is not None else "NULL"
                if len(value_str) > w - 10:
                    value_str = value_str[:w-13] + "..."
                stdscr.addstr(y, 4, f"Field {i+1}: {value_str}", curses.color_pair(5))

        # Instructions
        stdscr.addstr(h - 1, 0, "Press any key to return to table browser", curses.color_pair(6))
        stdscr.refresh()

        # Wait for user input
        stdscr.getch()

    def sql_input_screen(self, stdscr):
        """SQL query input screen with quick tools"""
        h, w = stdscr.getmaxyx()

        # Quick tools menu
        quick_tools = [
            "Insert Record",
            "Update Record",
            "Delete Record",
            "Create Table",
            "Drop Table",
            "View Table Structure",
            "Custom SQL Query",
            "Back to Main Menu"
        ]

        selected_tool = 0

        while True:
            stdscr.clear()
            title = "SQL Tools & Queries"
            stdscr.addstr(0, 0, "=" * w, curses.color_pair(1))
            stdscr.addstr(1, (w - len(title)) // 2, title, curses.A_BOLD | curses.color_pair(2))

            # Show current database
            if self.db.db_name:
                db_status = f"Database: {self.db.db_name}"
                stdscr.addstr(2, 0, db_status, curses.color_pair(getattr(self, 'db_color', 3)))

            # Display quick tools
            for i, tool in enumerate(quick_tools):
                y = 4 + i
                if y >= h - 2:
                    break
                if i == selected_tool:
                    stdscr.addstr(y, 2, f"> {tool}", curses.A_REVERSE | curses.color_pair(4))
                else:
                    stdscr.addstr(y, 2, f"  {tool}", curses.color_pair(5))

            stdscr.addstr(h - 1, 0, "Use ↑↓ to select tool, Enter to use, Escape to cancel", curses.color_pair(6))
            stdscr.refresh()

            key = stdscr.getch()

            if key == curses.KEY_UP:
                selected_tool = (selected_tool - 1) % len(quick_tools)
            elif key == curses.KEY_DOWN:
                selected_tool = (selected_tool + 1) % len(quick_tools)
            elif key == 10 or key == 13:  # Enter
                if selected_tool == 0:  # Insert Record
                    self.insert_record_tool(stdscr)
                elif selected_tool == 1:  # Update Record
                    self.update_record_tool(stdscr)
                elif selected_tool == 2:  # Delete Record
                    self.delete_record_tool(stdscr)
                elif selected_tool == 3:  # Create Table
                    self.create_table_tool(stdscr)
                elif selected_tool == 4:  # Drop Table
                    self.drop_table_tool(stdscr)
                elif selected_tool == 5:  # View Table Structure
                    self.view_table_structure_tool(stdscr)
                elif selected_tool == 6:  # Custom SQL Query
                    self.custom_sql_tool(stdscr)
                elif selected_tool == 7:  # Back to Main Menu
                    return
            elif key == 27:  # Escape
                return

    def insert_record_tool(self, stdscr):
        """Quick tool for inserting a record"""
        h, w = stdscr.getmaxyx()

        # Get available tables
        tables = self.db.get_tables()
        if not tables:
            stdscr.clear()
            stdscr.addstr(1, 2, "No tables found in database!", curses.color_pair(7))
            stdscr.addstr(h - 1, 0, "Press any key to continue")
            stdscr.refresh()
            stdscr.getch()
            return

        # Select table
        selected_table = 0
        while True:
            stdscr.clear()
            title = "Insert Record - Select Table"
            stdscr.addstr(0, 0, "=" * w, curses.color_pair(1))
            stdscr.addstr(1, (w - len(title)) // 2, title, curses.A_BOLD | curses.color_pair(2))

            for i, table in enumerate(tables):
                y = 3 + i
                if y >= h - 2:
                    break
                if i == selected_table:
                    stdscr.addstr(y, 2, f"> {table}", curses.A_REVERSE | curses.color_pair(4))
                else:
                    stdscr.addstr(y, 2, f"  {table}", curses.color_pair(5))

            stdscr.addstr(h - 1, 0, "Use ↑↓ to select table, Enter to continue, Escape to cancel", curses.color_pair(6))
            stdscr.refresh()

            key = stdscr.getch()
            if key == curses.KEY_UP:
                selected_table = (selected_table - 1) % len(tables)
            elif key == curses.KEY_DOWN:
                selected_table = (selected_table + 1) % len(tables)
            elif key == 10 or key == 13:  # Enter
                break
            elif key == 27:  # Escape
                return

        table_name = tables[selected_table]
        schema = self.db.get_table_schema(table_name)

        if not schema:
            stdscr.clear()
            stdscr.addstr(1, 2, f"Could not get schema for table {table_name}", curses.color_pair(7))
            stdscr.addstr(h - 1, 0, "Press any key to continue")
            stdscr.refresh()
            stdscr.getch()
            return

        # Input values for each column
        values = []
        for col_info in schema:
            col_name, col_type = col_info[1], col_info[2]

            stdscr.clear()
            title = f"Insert Record - {table_name}"
            stdscr.addstr(0, 0, "=" * w, curses.color_pair(1))
            stdscr.addstr(1, (w - len(title)) // 2, title, curses.A_BOLD | curses.color_pair(2))

            stdscr.addstr(3, 2, f"Enter value for {col_name} ({col_type}):", curses.color_pair(5))
            stdscr.addstr(4, 2, ">" , curses.color_pair(4))

            curses.echo()
            value = stdscr.getstr(4, 4, w - 6).decode('utf-8').strip()
            curses.noecho()

            if value.lower() == 'null':
                values.append(None)
            elif col_type.upper() in ['INTEGER', 'REAL', 'NUMERIC']:
                try:
                    values.append(float(value) if '.' in value else int(value))
                except ValueError:
                    values.append(value)
            else:
                values.append(value)

        # Generate and execute INSERT statement
        placeholders = ', '.join(['?' for _ in values])
        columns = ', '.join([col[1] for col in schema])
        sql = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"

        try:
            result = self.db.execute_sql(sql, values)
            stdscr.clear()
            stdscr.addstr(1, 2, "Record inserted successfully!", curses.color_pair(3))
            stdscr.addstr(3, 2, f"Table: {table_name}", curses.color_pair(5))
            stdscr.addstr(h - 1, 0, "Press any key to continue")
            stdscr.refresh()
            stdscr.getch()
        except Exception as e:
            stdscr.clear()
            stdscr.addstr(1, 2, f"Error inserting record: {str(e)}", curses.color_pair(7))
            stdscr.addstr(h - 1, 0, "Press any key to continue")
            stdscr.refresh()
            stdscr.getch()

    def update_record_tool(self, stdscr):
        """Quick tool for updating a record"""
        h, w = stdscr.getmaxyx()

        # Get available tables
        tables = self.db.get_tables()
        if not tables:
            stdscr.clear()
            stdscr.addstr(1, 2, "No tables found in database!", curses.color_pair(7))
            stdscr.addstr(h - 1, 0, "Press any key to continue")
            stdscr.refresh()
            stdscr.getch()
            return

        # Select table
        selected_table = 0
        while True:
            stdscr.clear()
            title = "Update Record - Select Table"
            stdscr.addstr(0, 0, "=" * w, curses.color_pair(1))
            stdscr.addstr(1, (w - len(title)) // 2, title, curses.A_BOLD | curses.color_pair(2))

            for i, table in enumerate(tables):
                y = 3 + i
                if y >= h - 2:
                    break
                if i == selected_table:
                    stdscr.addstr(y, 2, f"> {table}", curses.A_REVERSE | curses.color_pair(4))
                else:
                    stdscr.addstr(y, 2, f"  {table}", curses.color_pair(5))

            stdscr.addstr(h - 1, 0, "Use ↑↓ to select table, Enter to continue, Escape to cancel", curses.color_pair(6))
            stdscr.refresh()

            key = stdscr.getch()
            if key == curses.KEY_UP:
                selected_table = (selected_table - 1) % len(tables)
            elif key == curses.KEY_DOWN:
                selected_table = (selected_table + 1) % len(tables)
            elif key == 10 or key == 13:  # Enter
                break
            elif key == 27:  # Escape
                return

        table_name = tables[selected_table]
        schema = self.db.get_table_schema(table_name)

        if not schema:
            stdscr.clear()
            stdscr.addstr(1, 2, f"Could not get schema for table {table_name}", curses.color_pair(7))
            stdscr.addstr(h - 1, 0, "Press any key to continue")
            stdscr.refresh()
            stdscr.getch()
            return

        # Get record ID or primary key for identification
        stdscr.clear()
        title = f"Update Record - {table_name}"
        stdscr.addstr(0, 0, "=" * w, curses.color_pair(1))
        stdscr.addstr(1, (w - len(title)) // 2, title, curses.A_BOLD | curses.color_pair(2))

        stdscr.addstr(3, 2, "Enter record ID (primary key value):", curses.color_pair(5))
        stdscr.addstr(4, 2, ">" , curses.color_pair(4))

        curses.echo()
        record_id = stdscr.getstr(4, 4, w - 6).decode('utf-8').strip()
        curses.noecho()

        if not record_id:
            return

        # Select which column to update
        selected_col = 0
        while True:
            stdscr.clear()
            stdscr.addstr(0, 0, "=" * w, curses.color_pair(1))
            stdscr.addstr(1, (w - len(title)) // 2, title, curses.A_BOLD | curses.color_pair(2))

            stdscr.addstr(3, 2, f"Select column to update (Record ID: {record_id}):", curses.color_pair(5))

            for i, col_info in enumerate(schema):
                y = 5 + i
                if y >= h - 2:
                    break
                col_name, col_type = col_info[1], col_info[2]
                if i == selected_col:
                    stdscr.addstr(y, 2, f"> {col_name} ({col_type})", curses.A_REVERSE | curses.color_pair(4))
                else:
                    stdscr.addstr(y, 2, f"  {col_name} ({col_type})", curses.color_pair(5))

            stdscr.addstr(h - 1, 0, "Use ↑↓ to select column, Enter to continue, Escape to cancel", curses.color_pair(6))
            stdscr.refresh()

            key = stdscr.getch()
            if key == curses.KEY_UP:
                selected_col = (selected_col - 1) % len(schema)
            elif key == curses.KEY_DOWN:
                selected_col = (selected_col + 1) % len(schema)
            elif key == 10 or key == 13:  # Enter
                break
            elif key == 27:  # Escape
                return

        col_info = schema[selected_col]
        col_name, col_type = col_info[1], col_info[2]

        # Input new value
        stdscr.clear()
        stdscr.addstr(0, 0, "=" * w, curses.color_pair(1))
        stdscr.addstr(1, (w - len(title)) // 2, title, curses.A_BOLD | curses.color_pair(2))

        stdscr.addstr(3, 2, f"Enter new value for {col_name} ({col_type}):", curses.color_pair(5))
        stdscr.addstr(4, 2, ">" , curses.color_pair(4))

        curses.echo()
        new_value = stdscr.getstr(4, 4, w - 6).decode('utf-8').strip()
        curses.noecho()

        # Convert value based on type
        if new_value.lower() == 'null':
            final_value = None
        elif col_type.upper() in ['INTEGER', 'REAL', 'NUMERIC']:
            try:
                final_value = float(new_value) if '.' in new_value else int(new_value)
            except ValueError:
                final_value = new_value
        else:
            final_value = new_value

        # Generate and execute UPDATE statement
        sql = f"UPDATE {table_name} SET {col_name} = ? WHERE rowid = ?"

        try:
            result = self.db.execute_sql(sql, [final_value, record_id])
            stdscr.clear()
            stdscr.addstr(1, 2, "Record updated successfully!", curses.color_pair(3))
            stdscr.addstr(3, 2, f"Table: {table_name}", curses.color_pair(5))
            stdscr.addstr(4, 2, f"Column: {col_name}", curses.color_pair(5))
            stdscr.addstr(h - 1, 0, "Press any key to continue")
            stdscr.refresh()
            stdscr.getch()
        except Exception as e:
            stdscr.clear()
            stdscr.addstr(1, 2, f"Error updating record: {str(e)}", curses.color_pair(7))
            stdscr.addstr(h - 1, 0, "Press any key to continue")
            stdscr.refresh()
            stdscr.getch()

    def delete_record_tool(self, stdscr):
        """Quick tool for deleting a record"""
        h, w = stdscr.getmaxyx()

        # Get available tables
        tables = self.db.get_tables()
        if not tables:
            stdscr.clear()
            stdscr.addstr(1, 2, "No tables found in database!", curses.color_pair(7))
            stdscr.addstr(h - 1, 0, "Press any key to continue")
            stdscr.refresh()
            stdscr.getch()
            return

        # Select table
        selected_table = 0
        while True:
            stdscr.clear()
            title = "Delete Record - Select Table"
            stdscr.addstr(0, 0, "=" * w, curses.color_pair(1))
            stdscr.addstr(1, (w - len(title)) // 2, title, curses.A_BOLD | curses.color_pair(2))

            for i, table in enumerate(tables):
                y = 3 + i
                if y >= h - 2:
                    break
                if i == selected_table:
                    stdscr.addstr(y, 2, f"> {table}", curses.A_REVERSE | curses.color_pair(4))
                else:
                    stdscr.addstr(y, 2, f"  {table}", curses.color_pair(5))

            stdscr.addstr(h - 1, 0, "Use ↑↓ to select table, Enter to continue, Escape to cancel", curses.color_pair(6))
            stdscr.refresh()

            key = stdscr.getch()
            if key == curses.KEY_UP:
                selected_table = (selected_table - 1) % len(tables)
            elif key == curses.KEY_DOWN:
                selected_table = (selected_table + 1) % len(tables)
            elif key == 10 or key == 13:  # Enter
                break
            elif key == 27:  # Escape
                return

        table_name = tables[selected_table]

        # Get record ID
        stdscr.clear()
        title = f"Delete Record - {table_name}"
        stdscr.addstr(0, 0, "=" * w, curses.color_pair(1))
        stdscr.addstr(1, (w - len(title)) // 2, title, curses.A_BOLD | curses.color_pair(2))

        stdscr.addstr(3, 2, "Enter record ID to delete:", curses.color_pair(5))
        stdscr.addstr(4, 2, ">" , curses.color_pair(4))

        curses.echo()
        record_id = stdscr.getstr(4, 4, w - 6).decode('utf-8').strip()
        curses.noecho()

        if not record_id:
            return

        # Confirm deletion
        stdscr.clear()
        stdscr.addstr(0, 0, "=" * w, curses.color_pair(1))
        stdscr.addstr(1, (w - len(title)) // 2, title, curses.A_BOLD | curses.color_pair(2))

        stdscr.addstr(3, 2, f"Are you sure you want to delete record ID {record_id}?", curses.color_pair(7))
        stdscr.addstr(4, 2, "from table " + table_name + "?", curses.color_pair(7))
        stdscr.addstr(6, 2, "Press 'y' to confirm, any other key to cancel", curses.color_pair(5))

        stdscr.refresh()
        key = stdscr.getch()

        if key != ord('y'):
            return

        # Execute DELETE statement
        sql = f"DELETE FROM {table_name} WHERE rowid = ?"

        try:
            result = self.db.execute_sql(sql, [record_id])
            stdscr.clear()
            stdscr.addstr(1, 2, "Record deleted successfully!", curses.color_pair(3))
            stdscr.addstr(3, 2, f"Table: {table_name}", curses.color_pair(5))
            stdscr.addstr(4, 2, f"Record ID: {record_id}", curses.color_pair(5))
            stdscr.addstr(h - 1, 0, "Press any key to continue")
            stdscr.refresh()
            stdscr.getch()
        except Exception as e:
            stdscr.clear()
            stdscr.addstr(1, 2, f"Error deleting record: {str(e)}", curses.color_pair(7))
            stdscr.addstr(h - 1, 0, "Press any key to continue")
            stdscr.refresh()
            stdscr.getch()

    def draw_menu(self, stdscr, title, options, selected):
        """Draw a menu with options"""
        h, w = stdscr.getmaxyx()
        stdscr.clear()
        h, w = stdscr.getmaxyx()

        # Draw title
        title_str = f" Loula's SQLite Viewer - {title} "
        stdscr.addstr(0, 0, "=" * w, curses.color_pair(1))
        stdscr.addstr(1, (w - len(title_str)) // 2, title_str, curses.A_BOLD | curses.color_pair(2))

        # Draw database status
        if self.db.db_name:
            status = f"Database: {self.db.db_name}"
            stdscr.addstr(2, 0, status, curses.color_pair(getattr(self, 'db_color', 3)))
        else:
            status = "Database: None"
            stdscr.addstr(2, 0, status, curses.color_pair(3))

        # Draw menu options
        for i, option in enumerate(options):
            y = 4 + i
            if y >= h - 2:
                break
            if i == selected:
                stdscr.addstr(y, 2, f"> {option}", curses.A_REVERSE | curses.color_pair(4))
            else:
                stdscr.addstr(y, 2, f"  {option}", curses.color_pair(5))

        # Draw instructions
        instructions = "Use ↑↓ to navigate, Enter to select, 'q' to quit"
        stdscr.addstr(h - 1, 0, instructions, curses.color_pair(6))

        stdscr.refresh()

    def main_loop(self, stdscr):
        """Main TUI loop"""
        # Initialize colors
        curses.start_color()
        curses.init_pair(1, curses.COLOR_BLUE, curses.COLOR_BLACK)    # Borders
        curses.init_pair(2, curses.COLOR_YELLOW, curses.COLOR_BLACK)  # Title
        curses.init_pair(3, curses.COLOR_GREEN, curses.COLOR_BLACK)   # Status
        curses.init_pair(4, curses.COLOR_BLACK, curses.COLOR_WHITE)   # Selected
        curses.init_pair(5, curses.COLOR_WHITE, curses.COLOR_BLACK)   # Normal
        curses.init_pair(6, curses.COLOR_CYAN, curses.COLOR_BLACK)    # Instructions
        curses.init_pair(7, curses.COLOR_RED, curses.COLOR_BLACK)     # Error

        curses.curs_set(0)  # Hide cursor
        stdscr.keypad(True)  # Enable keypad

        main_options = [
            "Connect to Database",
            "Browse Tables",
            "Execute SQL",
            "Disconnect",
            "Quit"
        ]

        while True:
            if self.current_menu == 'main':
                self.draw_menu(stdscr, "Main Menu", main_options, self.selected_option)

                key = stdscr.getch()

                if key == curses.KEY_UP:
                    self.selected_option = (self.selected_option - 1) % len(main_options)
                elif key == curses.KEY_DOWN:
                    self.selected_option = (self.selected_option + 1) % len(main_options)
                elif key == 10 or key == 13:  # Enter
                    if self.selected_option == 0:  # Connect
                        self.connection_screen(stdscr)
                    elif self.selected_option == 1:  # Browse Tables
                        self.split_screen_table_browser(stdscr)
                    elif self.selected_option == 2:  # Execute SQL
                        self.sql_input_screen(stdscr)
                    elif self.selected_option == 3:  # Disconnect
                        self.db.disconnect()
                    elif self.selected_option == 4:  # Quit
                        break
                elif key == ord('q'):
                    break

    def run(self):
        """Run the TUI"""
        curses.wrapper(self.main_loop)

    def create_table_tool(self, stdscr):
        """Quick tool for creating a new table"""
        h, w = stdscr.getmaxyx()

        # Get table name
        stdscr.clear()
        title = "Create New Table"
        stdscr.addstr(0, 0, "=" * w, curses.color_pair(1))
        stdscr.addstr(1, (w - len(title)) // 2, title, curses.A_BOLD | curses.color_pair(2))

        stdscr.addstr(3, 2, "Enter table name:", curses.color_pair(5))
        stdscr.addstr(4, 2, ">" , curses.color_pair(4))

        curses.echo()
        table_name = stdscr.getstr(4, 4, w - 6).decode('utf-8').strip()
        curses.noecho()

        if not table_name:
            return

        # Get number of columns
        stdscr.clear()
        stdscr.addstr(0, 0, "=" * w, curses.color_pair(1))
        stdscr.addstr(1, (w - len(title)) // 2, title, curses.A_BOLD | curses.color_pair(2))

        stdscr.addstr(3, 2, f"Table: {table_name}", curses.color_pair(3))
        stdscr.addstr(4, 2, "Enter number of columns:", curses.color_pair(5))
        stdscr.addstr(5, 2, ">" , curses.color_pair(4))

        curses.echo()
        try:
            num_cols = int(stdscr.getstr(5, 4, 10).decode('utf-8').strip())
        except ValueError:
            num_cols = 0
        curses.noecho()

        if num_cols <= 0:
            return

        # Define columns
        columns = []
        for i in range(num_cols):
            stdscr.clear()
            stdscr.addstr(0, 0, "=" * w, curses.color_pair(1))
            stdscr.addstr(1, (w - len(title)) // 2, title, curses.A_BOLD | curses.color_pair(2))

            stdscr.addstr(3, 2, f"Table: {table_name} - Column {i+1}/{num_cols}", curses.color_pair(3))

            # Column name
            stdscr.addstr(5, 2, "Column name:", curses.color_pair(5))
            stdscr.addstr(6, 2, ">" , curses.color_pair(4))

            curses.echo()
            col_name = stdscr.getstr(6, 4, w - 6).decode('utf-8').strip()
            curses.noecho()

            if not col_name:
                continue

            # Column type
            stdscr.clear()
            stdscr.addstr(0, 0, "=" * w, curses.color_pair(1))
            stdscr.addstr(1, (w - len(title)) // 2, title, curses.A_BOLD | curses.color_pair(2))

            stdscr.addstr(3, 2, f"Table: {table_name} - Column {i+1}: {col_name}", curses.color_pair(3))

            types = ["TEXT", "INTEGER", "REAL", "BLOB", "NUMERIC"]
            selected_type = 0

            while True:
                stdscr.addstr(5, 2, "Select data type:", curses.color_pair(5))

                for j, col_type in enumerate(types):
                    y = 7 + j
                    if j == selected_type:
                        stdscr.addstr(y, 2, f"> {col_type}", curses.A_REVERSE | curses.color_pair(4))
                    else:
                        stdscr.addstr(y, 2, f"  {col_type}", curses.color_pair(5))

                stdscr.addstr(h - 1, 0, "Use ↑↓ to select type, Enter to confirm", curses.color_pair(6))
                stdscr.refresh()

                key = stdscr.getch()
                if key == curses.KEY_UP:
                    selected_type = (selected_type - 1) % len(types)
                elif key == curses.KEY_DOWN:
                    selected_type = (selected_type + 1) % len(types)
                elif key == 10 or key == 13:  # Enter
                    break

            columns.append(f"{col_name} {types[selected_type]}")

        if not columns:
            return

        # Generate CREATE TABLE statement
        columns_str = ', '.join(columns)
        sql = f"CREATE TABLE {table_name} ({columns_str})"

        try:
            result = self.db.execute_sql(sql)
            stdscr.clear()
            stdscr.addstr(1, 2, "Table created successfully!", curses.color_pair(3))
            stdscr.addstr(3, 2, f"Table: {table_name}", curses.color_pair(5))
            stdscr.addstr(4, 2, f"Columns: {len(columns)}", curses.color_pair(5))
            stdscr.addstr(h - 1, 0, "Press any key to continue")
            stdscr.refresh()
            stdscr.getch()
        except Exception as e:
            stdscr.clear()
            stdscr.addstr(1, 2, f"Error creating table: {str(e)}", curses.color_pair(7))
            stdscr.addstr(h - 1, 0, "Press any key to continue")
            stdscr.refresh()
            stdscr.getch()

    def drop_table_tool(self, stdscr):
        """Quick tool for dropping a table"""
        h, w = stdscr.getmaxyx()

        # Get available tables
        tables = self.db.get_tables()
        if not tables:
            stdscr.clear()
            stdscr.addstr(1, 2, "No tables found in database!", curses.color_pair(7))
            stdscr.addstr(h - 1, 0, "Press any key to continue")
            stdscr.refresh()
            stdscr.getch()
            return

        # Select table
        selected_table = 0
        while True:
            stdscr.clear()
            title = "Drop Table - Select Table"
            stdscr.addstr(0, 0, "=" * w, curses.color_pair(1))
            stdscr.addstr(1, (w - len(title)) // 2, title, curses.A_BOLD | curses.color_pair(2))

            for i, table in enumerate(tables):
                y = 3 + i
                if y >= h - 2:
                    break
                if i == selected_table:
                    stdscr.addstr(y, 2, f"> {table}", curses.A_REVERSE | curses.color_pair(4))
                else:
                    stdscr.addstr(y, 2, f"  {table}", curses.color_pair(5))

            stdscr.addstr(h - 1, 0, "Use ↑↓ to select table, Enter to continue, Escape to cancel", curses.color_pair(6))
            stdscr.refresh()

            key = stdscr.getch()
            if key == curses.KEY_UP:
                selected_table = (selected_table - 1) % len(tables)
            elif key == curses.KEY_DOWN:
                selected_table = (selected_table + 1) % len(tables)
            elif key == 10 or key == 13:  # Enter
                break
            elif key == 27:  # Escape
                return

        table_name = tables[selected_table]

        # Confirm deletion
        stdscr.clear()
        title = f"Drop Table - {table_name}"
        stdscr.addstr(0, 0, "=" * w, curses.color_pair(1))
        stdscr.addstr(1, (w - len(title)) // 2, title, curses.A_BOLD | curses.color_pair(2))

        stdscr.addstr(3, 2, f"Are you sure you want to drop table '{table_name}'?", curses.color_pair(7))
        stdscr.addstr(4, 2, "This action cannot be undone!", curses.color_pair(7))
        stdscr.addstr(6, 2, "Press 'y' to confirm, any other key to cancel", curses.color_pair(5))

        stdscr.refresh()
        key = stdscr.getch()

        if key != ord('y'):
            return

        # Execute DROP TABLE statement
        sql = f"DROP TABLE {table_name}"

        try:
            result = self.db.execute_sql(sql)
            stdscr.clear()
            stdscr.addstr(1, 2, "Table dropped successfully!", curses.color_pair(3))
            stdscr.addstr(3, 2, f"Dropped table: {table_name}", curses.color_pair(5))
            stdscr.addstr(h - 1, 0, "Press any key to continue")
            stdscr.refresh()
            stdscr.getch()
        except Exception as e:
            stdscr.clear()
            stdscr.addstr(1, 2, f"Error dropping table: {str(e)}", curses.color_pair(7))
            stdscr.addstr(h - 1, 0, "Press any key to continue")
            stdscr.refresh()
            stdscr.getch()

    def view_table_structure_tool(self, stdscr):
        """Quick tool for viewing table structure"""
        h, w = stdscr.getmaxyx()

        # Get available tables
        tables = self.db.get_tables()
        if not tables:
            stdscr.clear()
            stdscr.addstr(1, 2, "No tables found in database!", curses.color_pair(7))
            stdscr.addstr(h - 1, 0, "Press any key to continue")
            stdscr.refresh()
            stdscr.getch()
            return

        # Select table
        selected_table = 0
        while True:
            stdscr.clear()
            title = "View Table Structure - Select Table"
            stdscr.addstr(0, 0, "=" * w, curses.color_pair(1))
            stdscr.addstr(1, (w - len(title)) // 2, title, curses.A_BOLD | curses.color_pair(2))

            for i, table in enumerate(tables):
                y = 3 + i
                if y >= h - 2:
                    break
                if i == selected_table:
                    stdscr.addstr(y, 2, f"> {table}", curses.A_REVERSE | curses.color_pair(4))
                else:
                    stdscr.addstr(y, 2, f"  {table}", curses.color_pair(5))

            stdscr.addstr(h - 1, 0, "Use ↑↓ to select table, Enter to view, Escape to cancel", curses.color_pair(6))
            stdscr.refresh()

            key = stdscr.getch()
            if key == curses.KEY_UP:
                selected_table = (selected_table - 1) % len(tables)
            elif key == curses.KEY_DOWN:
                selected_table = (selected_table + 1) % len(tables)
            elif key == 10 or key == 13:  # Enter
                break
            elif key == 27:  # Escape
                return

        table_name = tables[selected_table]
        schema = self.db.get_table_schema(table_name)

        if not schema:
            stdscr.clear()
            stdscr.addstr(1, 2, f"Could not get schema for table {table_name}", curses.color_pair(7))
            stdscr.addstr(h - 1, 0, "Press any key to continue")
            stdscr.refresh()
            stdscr.getch()
            return

        # Display table structure
        stdscr.clear()
        title = f"Table Structure - {table_name}"
        stdscr.addstr(0, 0, "=" * w, curses.color_pair(1))
        stdscr.addstr(1, (w - len(title)) // 2, title, curses.A_BOLD | curses.color_pair(2))

        stdscr.addstr(3, 2, "Column Name", curses.A_BOLD | curses.color_pair(3))
        stdscr.addstr(3, 20, "Type", curses.A_BOLD | curses.color_pair(3))
        stdscr.addstr(3, 35, "Nullable", curses.A_BOLD | curses.color_pair(3))
        stdscr.addstr(3, 50, "Default", curses.A_BOLD | curses.color_pair(3))
        stdscr.addstr(4, 2, "-" * (w - 4), curses.color_pair(3))

        for i, col_info in enumerate(schema):
            y = 5 + i
            if y >= h - 2:
                break

            col_id, col_name, col_type, not_null, default_val, pk = col_info

            stdscr.addstr(y, 2, col_name[:17], curses.color_pair(5))
            stdscr.addstr(y, 20, col_type[:14], curses.color_pair(5))
            stdscr.addstr(y, 35, "NO" if not_null else "YES", curses.color_pair(5))
            stdscr.addstr(y, 50, str(default_val)[:w-52] if default_val else "", curses.color_pair(5))

        stdscr.addstr(h - 1, 0, "Press any key to continue", curses.color_pair(6))
        stdscr.refresh()
        stdscr.getch()

    def custom_sql_tool(self, stdscr):
        """Custom SQL query tool"""
        h, w = stdscr.getmaxyx()

        stdscr.clear()
        title = "Custom SQL Query"
        stdscr.addstr(0, 0, "=" * w, curses.color_pair(1))
        stdscr.addstr(1, (w - len(title)) // 2, title, curses.A_BOLD | curses.color_pair(2))

        stdscr.addstr(3, 2, "Enter SQL query:", curses.color_pair(5))
        stdscr.addstr(4, 2, ">" , curses.color_pair(4))

        curses.echo()
        sql = stdscr.getstr(4, 4, w - 6).decode('utf-8').strip()
        curses.noecho()

        if not sql:
            return

        try:
            result = self.db.execute_sql(sql)
            stdscr.clear()
            stdscr.addstr(0, 0, "SQL Result:", curses.A_BOLD | curses.color_pair(2))

            if isinstance(result, list):
                if result:
                    # Display results
                    for i, row in enumerate(result):
                        y = 2 + i
                        if y >= h - 2:
                            break
                        row_str = " | ".join(str(cell) for cell in row)
                        if len(row_str) > w - 4:
                            row_str = row_str[:w-7] + "..."
                        stdscr.addstr(y, 2, row_str, curses.color_pair(5))
                else:
                    stdscr.addstr(2, 2, "Query executed successfully (no results)", curses.color_pair(3))
            else:
                stdscr.addstr(2, 2, f"Result: {result}", curses.color_pair(3))

            stdscr.addstr(h - 1, 0, "Press any key to continue", curses.color_pair(6))
            stdscr.refresh()
            stdscr.getch()
        except Exception as e:
            stdscr.clear()
            stdscr.addstr(1, 2, f"SQL Error: {str(e)}", curses.color_pair(7))
            stdscr.addstr(h - 1, 0, "Press any key to continue")
            stdscr.refresh()
            stdscr.getch()
