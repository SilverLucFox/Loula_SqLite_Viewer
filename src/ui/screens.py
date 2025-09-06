"""
Screen classes for Loula's SQLite Viewer
"""

import curses
import os
from .ui_utils import UIUtils


class ConnectionScreens:
    """Screens for database connection management"""

    def __init__(self, db_manager, config_manager, ui_utils):
        self.db = db_manager
        self.config = config_manager
        self.ui = ui_utils

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
            self.ui.draw_main_title(stdscr)
            title = "Select Database Color"
            stdscr.addstr(2, (w - len(title)) // 2, title, curses.A_BOLD | curses.color_pair(2))

            for i, (name, color_id) in enumerate(colors):
                y = 4 + i
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
        self.ui.draw_main_title(stdscr)
        title = "Connection Type"
        stdscr.addstr(2, (w - len(title)) // 2, title, curses.A_BOLD | curses.color_pair(2))

        options = ["Connect to Saved Database", "Connect to New Database"]
        selected = 0

        while True:
            for i, option in enumerate(options):
                y = 4 + i
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
            self.ui.draw_main_title(stdscr)
            stdscr.addstr(3, 2, "No saved databases found!", curses.color_pair(7))
            stdscr.addstr(5, 2, "Use 'Connect to New Database' first.", curses.color_pair(5))
            stdscr.addstr(h - 1, 0, "Press any key to continue")
            stdscr.refresh()
            stdscr.getch()
            return

        selected = 0
        while True:
            stdscr.clear()
            self.ui.draw_main_title(stdscr)
            title = "Select Saved Database"
            stdscr.addstr(2, (w - len(title)) // 2, title, curses.A_BOLD | curses.color_pair(2))

            for i, db in enumerate(saved_dbs):
                y = 4 + i
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
                    self.ui.db_color = db.get('color', 3)  # Update the database color
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
        self.ui.draw_main_title(stdscr)

        title = "Connect to New Database"
        stdscr.addstr(2, (w - len(title)) // 2, title, curses.A_BOLD | curses.color_pair(2))

        stdscr.addstr(4, 2, "Database Path:", curses.color_pair(5))
        stdscr.addstr(5, 2, ">" , curses.color_pair(4))

        stdscr.addstr(7, 2, "Database Name:", curses.color_pair(5))
        stdscr.addstr(8, 2, ">" , curses.color_pair(4))

        # Input for path
        curses.echo()
        path = stdscr.getstr(5, 4, w - 6).decode('utf-8').strip()

        if not path:
            return

        # Input for name
        name = stdscr.getstr(8, 4, w - 6).decode('utf-8').strip()
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
            self.ui.db_color = color  # Update the database color

            # Success message
            stdscr.clear()
            stdscr.addstr(1, 2, f"Successfully connected to: {name}", curses.color_pair(color))
            stdscr.addstr(h - 1, 0, "Press any key to continue")
            stdscr.refresh()
            stdscr.getch()
