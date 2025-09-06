"""
Table Browser for Loula's SQLite Viewer
"""

import curses
from ui_utils import UIUtils


class TableBrowser:
    """Table browsing functionality"""

    def __init__(self, db_manager, config_manager, ui_utils):
        self.db = db_manager
        self.config = config_manager
        self.ui = ui_utils

    def split_screen_table_browser(self, stdscr):
        """Split screen interface: left panel for table list, right panel for data"""
        h, w = stdscr.getmaxyx()

        # Draw main title "Loula's SQLite Viewer" with database color above both panels
        main_title = "Loula's SQLite Viewer"
        if self.db.db_name:
            title_color = getattr(self.ui, 'db_color', 3)
        else:
            title_color = 5  # White for no database connected

        stdscr.addstr(0, (w - len(main_title)) // 2, main_title, curses.A_BOLD | curses.color_pair(title_color))
        stdscr.addstr(1, 0, "=" * w, curses.color_pair(1))
        stdscr.refresh()

        # Create windows for split screen (starting from line 2 to leave space for title)
        left_width = max(20, w // 4)
        right_width = w - left_width - 1

        # Create windows starting from line 2
        left_win = curses.newwin(h - 2, left_width, 2, 0)
        right_win = curses.newwin(h - 2, right_width, 2, left_width + 1)

        # Get tables
        tables = self.db.get_tables()
        if not tables:
            return

        selected_table = 0
        table_page = 0
        selected_row = 0  # Track selected row in the current table
        rows_per_page = h - 8  # Leave space for headers and instructions (adjusted for title)
        table_selected = False  # Track if a table has been selected

        while True:
            # Clear windows
            left_win.clear()
            right_win.clear()

            # Draw left panel (table list)
            left_win.addstr(0, 0, "=" * left_width, curses.color_pair(1))
            left_win.addstr(1, 1, "Tables", curses.A_BOLD | curses.color_pair(2))

            for i, table in enumerate(tables):
                if i >= h - 6:  # Leave space for instructions (adjusted for title)
                    break
                y = 2 + i  # Start table list right after the title
                if i == selected_table:
                    left_win.addstr(y, 1, f"> {table}", curses.A_REVERSE | curses.color_pair(4))
                else:
                    left_win.addstr(y, 1, f"  {table}", curses.color_pair(5))

            left_win.addstr(h - 4, 1, "↑↓ select table" if not table_selected else "Table selected", curses.color_pair(6))
            left_win.addstr(h - 3, 1, "Enter select" if not table_selected else "Esc back", curses.color_pair(6))

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
                            headers, formatted_rows = self.ui.format_table_data(page_data, schema, right_width)

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
                                if y >= h - 6:  # Leave space for instructions (adjusted for title)
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
                                if y >= h - 6:
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
                        right_win.addstr(h - 5, 1, page_info, curses.color_pair(6))

                    # Record position indicator
                    current_page_data = data[start_idx:end_idx]
                    if current_page_data:
                        total_records = len(data)
                        current_record_global = start_idx + selected_row + 1  # 1-based indexing
                        record_info = f"Record {current_record_global} of {total_records}"
                        right_win.addstr(h - 6, 1, record_info, curses.color_pair(6))
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
                right_win.addstr(h - 4, 1, "↑↓ select record", curses.color_pair(6))
                right_win.addstr(h - 3, 1, "Enter view, ←→ page, Esc back", curses.color_pair(6))
            else:
                right_win.addstr(h - 4, 1, "Select a table first", curses.color_pair(6))
                right_win.addstr(h - 3, 1, "", curses.color_pair(6))

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
        self.ui.draw_main_title(stdscr)

        # Title
        title = f"Record Details - {table_name}"
        stdscr.addstr(2, (w - len(title)) // 2, title, curses.A_BOLD | curses.color_pair(2))

        if schema and record:
            # Display each field with its value
            for i, (col_info, value) in enumerate(zip(schema, record)):
                y = 4 + i * 2
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
            stdscr.addstr(4, 2, "Record data:", curses.A_BOLD | curses.color_pair(3))
            for i, value in enumerate(record):
                y = 6 + i
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
