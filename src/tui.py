"""
Text User Interface for SQLite Viewer
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
        rows_per_page = h - 6  # Leave space for headers and instructions

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

            left_win.addstr(h - 2, 1, "↑↓ select", curses.color_pair(6))
            left_win.addstr(h - 1, 1, "Enter view", curses.color_pair(6))

            # Draw right panel (table data)
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
                            right_win.addstr(y, 1, row_str, curses.color_pair(5))
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
                            right_win.addstr(y, 1, row_str, curses.color_pair(5))
                except Exception as e:
                    # Fallback on error
                    data_start_y = 3
                    right_win.addstr(3, 1, f"Error displaying table: {str(e)}", curses.color_pair(7))

                # Pagination info
                total_pages = (len(data) + rows_per_page - 1) // rows_per_page
                if total_pages > 1:
                    page_info = f"Page {table_page + 1}/{total_pages} ({len(data)} rows)"
                    right_win.addstr(h - 3, 1, page_info, curses.color_pair(6))

            else:
                right_win.addstr(3, 1, "No data in table", curses.color_pair(7))

            # Instructions
            right_win.addstr(h - 2, 1, "←→ page", curses.color_pair(6))
            right_win.addstr(h - 1, 1, "Esc back", curses.color_pair(6))

            # Refresh windows
            left_win.refresh()
            right_win.refresh()

            # Handle input
            key = stdscr.getch()

            if key == curses.KEY_UP:
                selected_table = (selected_table - 1) % len(tables)
                table_page = 0  # Reset page when changing tables
            elif key == curses.KEY_DOWN:
                selected_table = (selected_table + 1) % len(tables)
                table_page = 0  # Reset page when changing tables
            elif key == curses.KEY_LEFT:
                if table_page > 0:
                    table_page -= 1
            elif key == curses.KEY_RIGHT:
                data = self.db.get_table_data(current_table, limit=1000)
                max_pages = (len(data) + rows_per_page - 1) // rows_per_page
                if table_page < max_pages - 1:
                    table_page += 1
            elif key == 10 or key == 13:  # Enter - could add more functionality
                pass
            elif key == 27:  # Escape
                break

    def sql_input_screen(self, stdscr):
        """SQL query input screen"""
        h, w = stdscr.getmaxyx()
        stdscr.clear()

        title = "SQL Query"
        stdscr.addstr(0, 0, "=" * w, curses.color_pair(1))
        stdscr.addstr(1, (w - len(title)) // 2, title, curses.A_BOLD | curses.color_pair(2))

        stdscr.addstr(3, 2, "Enter SQL query:", curses.color_pair(5))
        stdscr.addstr(4, 2, ">" , curses.color_pair(4))

        # Simple input handling
        curses.echo()
        sql = stdscr.getstr(4, 4, w - 6).decode('utf-8')
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

    def draw_menu(self, stdscr, title, options, selected):
        """Draw a menu with options"""
        h, w = stdscr.getmaxyx()
        stdscr.clear()
        h, w = stdscr.getmaxyx()

        # Draw title
        title_str = f" SQLite Viewer - {title} "
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
