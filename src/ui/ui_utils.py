"""
UI Utility functions for Loula's SQLite Viewer
"""

import curses


class UIUtils:
    """Utility functions for UI operations"""

    def __init__(self, db_manager, config_manager):
        self.db = db_manager
        self.config = config_manager
        self.db_color = 3  # Default green

    def draw_main_title(self, stdscr, title_color=None):
        """Draw the main 'Loula's SQLite Viewer' title"""
        h, w = stdscr.getmaxyx()
        main_title = "Loula's SQLite Viewer"

        # Handle very small terminals
        if w < len(main_title) + 4:
            main_title = "Loula's Viewer"
        if w < len(main_title) + 4:
            main_title = "Loula"

        if title_color is None:
            if self.db.db_name:
                title_color = getattr(self, 'db_color', 3)
            else:
                title_color = 5  # White for no database connected

        try:
            stdscr.addstr(0, (w - len(main_title)) // 2, main_title, curses.A_BOLD | curses.color_pair(title_color))
            stdscr.addstr(1, 0, "=" * w, curses.color_pair(1))
        except curses.error:
            # Fallback for very small terminals
            try:
                stdscr.addstr(0, 0, main_title[:w-1], curses.A_BOLD | curses.color_pair(title_color))
                stdscr.addstr(1, 0, "=" * min(w, 20), curses.color_pair(1))
            except curses.error:
                pass  # Skip title if terminal is too small

    def draw_menu(self, stdscr, title, options, selected):
        """Draw a menu with options"""
        h, w = stdscr.getmaxyx()
        stdscr.clear()
        h, w = stdscr.getmaxyx()

        # Draw main title
        self.draw_main_title(stdscr)

        # Draw page title
        try:
            stdscr.addstr(2, (w - len(title)) // 2, title, curses.A_BOLD | curses.color_pair(2))
        except curses.error:
            try:
                stdscr.addstr(2, 0, title[:w-1], curses.A_BOLD | curses.color_pair(2))
            except curses.error:
                pass

        # Draw database status
        if self.db.db_name:
            status = f"Database: {self.db.db_name}"
            try:
                stdscr.addstr(3, 0, status, curses.color_pair(getattr(self, 'db_color', 3)))
            except curses.error:
                pass
        else:
            status = "Database: None"
            try:
                stdscr.addstr(3, 0, status, curses.color_pair(3))
            except curses.error:
                pass

        # Draw menu options
        for i, option in enumerate(options):
            y = 5 + i
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
