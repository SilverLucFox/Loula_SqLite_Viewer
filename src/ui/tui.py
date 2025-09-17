"""
Text User Interface for Loula's SQLite Viewer
"""

import curses
import os
from src.database.database import DatabaseManager
from src.config.config import ConfigManager
from src.ui.ui_utils import UIUtils
from src.ui.screens import ConnectionScreens
from src.tools.tools import SQLTools
from src.ui.table_browser import TableBrowser


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

        # Initialize utility classes
        self.ui = UIUtils(self.db, self.config)
        self.ui.db_color = self.db_color
        self.connection_screens = ConnectionScreens(self.db, self.config, self.ui)
        self.sql_tools = SQLTools(self.db, self.config, self.ui)
        self.table_browser = TableBrowser(self.db, self.config, self.ui)

    def save_database_to_list(self):
        """Add current database to saved databases"""
        if self.db.db_path and self.db.db_name:
            db_info = {
                'path': self.db.db_path,
                'name': self.db.db_name,
                'color': getattr(self, 'db_color', 3)
            }
            self.config.add_saved_database(db_info)

    # Screen methods - delegate to ConnectionScreens
    def select_color_screen(self, stdscr):
        return self.connection_screens.select_color_screen(stdscr)

    def connection_screen(self, stdscr):
        return self.connection_screens.connection_screen(stdscr)

    def connect_saved_screen(self, stdscr):
        return self.connection_screens.connect_saved_screen(stdscr)

    def connect_new_screen(self, stdscr):
        return self.connection_screens.connect_new_screen(stdscr)

    # Table browser methods - delegate to TableBrowser
    def split_screen_table_browser(self, stdscr):
        return self.table_browser.split_screen_table_browser(stdscr)

    def view_record_details(self, stdscr, table_name, record, schema):
        return self.table_browser.view_record_details(stdscr, table_name, record, schema)

    # SQL Tools methods - delegate to SQLTools
    def sql_input_screen(self, stdscr):
        return self.sql_tools.sql_input_screen(stdscr)

    def insert_record_tool(self, stdscr):
        return self.sql_tools.insert_record_tool(stdscr)

    def update_record_tool(self, stdscr):
        return self.sql_tools.update_record_tool(stdscr)

    def delete_record_tool(self, stdscr):
        return self.sql_tools.delete_record_tool(stdscr)

    def create_table_tool(self, stdscr):
        return self.sql_tools.create_table_tool(stdscr)

    def drop_table_tool(self, stdscr):
        return self.sql_tools.drop_table_tool(stdscr)

    def view_table_structure_tool(self, stdscr):
        return self.sql_tools.view_table_structure_tool(stdscr)

    def custom_sql_tool(self, stdscr):
        return self.sql_tools.custom_sql_tool(stdscr)

    # UI methods - delegate to UIUtils
    def draw_menu(self, stdscr, title, options, selected):
        return self.ui.draw_menu(stdscr, title, options, selected)

    def format_table_data(self, data, schema, max_width):
        return self.ui.format_table_data(data, schema, max_width)

    def tools_menu(self, stdscr):
        """Tools submenu"""
        tools_options = [
            "Insert Record",
            "Update Record",
            "Delete Record",
            "Create Table",
            "Drop Table",
            "View Table Structure",
            "Custom SQL Query",
            "Back to Main Menu"
        ]
        selected = 0
        while True:
            self.draw_menu(stdscr, "Tools Menu", tools_options, selected)
            key = stdscr.getch()
            if key == curses.KEY_UP:
                selected = (selected - 1) % len(tools_options)
            elif key == curses.KEY_DOWN:
                selected = (selected + 1) % len(tools_options)
            elif key == 10 or key == 13:  # Enter
                if selected == 0:
                    self.insert_record_tool(stdscr)
                elif selected == 1:
                    self.update_record_tool(stdscr)
                elif selected == 2:
                    self.delete_record_tool(stdscr)
                elif selected == 3:
                    self.create_table_tool(stdscr)
                elif selected == 4:
                    self.drop_table_tool(stdscr)
                elif selected == 5:
                    self.view_table_structure_tool(stdscr)
                elif selected == 6:
                    self.custom_sql_tool(stdscr)
                elif selected == 7:
                    break
            elif key == ord('q'):
                break

    def read_me_screen(self, stdscr):
        """Display the Read Me/Developer Note screen"""
        h, w = stdscr.getmaxyx()
        stdscr.clear()
        self.ui.draw_main_title(stdscr)

        # Developer note content
        content = [
            "📖 Developer Note - SilverFox",
            "",
            "🎯 Programmer Note - SilverFox",
            "",
            "About Loula's SQLite Viewer:",
            "A professional console-based SQLite database viewer and editor with an enhanced TUI interface.",
            "",
            "Features:",
            "• Professional TUI Interface - Navigate with arrow keys, just like Linux task managers (htop)",
            "• Color-coded Display - Easy to read interface with visual feedback",
            "• Database Management - Save multiple databases with custom colors",
            "• Menu-driven Navigation - No need to remember commands",
            "• Connect to SQLite databases - Save database path and name for quick reconnection",
            "• Browse Tables and Schemas - View table structures and data",
            "• Execute SQL Commands - Full SQL support for queries and modifications",
            "• Advanced Tools - Insert, Update, Delete records and manage table structures",
            "• Split-Screen Table Browser - Professional layout with pagination",
            "• Robust Error Handling - Professional-grade reliability",
            "",
            "Interface:",
            "• Arrow Keys: Navigate menu options",
            "• Enter: Select option",
            "• 'q': Quit application",
            "• 'b' or Escape: Go back to previous menu",
            "",
            "Main Menu Options:",
            "• Connect to Database - Connect to ANY SQLite database file",
            "• Browse Tables - Split-screen interface to browse tables and contents",
            "• Execute SQL - Run custom SQL queries",
            "• Tools - Access advanced database tools (Insert, Update, Delete, Create Table, etc.)",
            "• Read Me - View developer information and project details",
            "• Disconnect - Close current database connection",
            "• Quit - Exit the application",
            "",
            "Technical Stack:",
            "• Python 3.6+",
            "• curses library for TUI (windows-curses for Windows)",
            "• SQLite3 for database operations",
            "• JSON for configuration persistence",
            "• Modular architecture with separate UI, core, database, config, and tools layers",
            "• Cross-platform compatibility (Windows, Linux, macOS)",
            "",
            "Project Structure:",
            "• Core Module - Main entry point and CLI interface",
            "• Database Module - SQLite database operations",
            "• UI Module - Text User Interface components",
            "• Config Module - Configuration and persistence",
            "• Tools Module - SQL and utility tools",
            "",
            "Version: 2.2.3",
            "Developer: SilverFox",
            "Date: September 2025",
            "Latest Update: Enhanced TUI interface with split-screen table browser",
            "",
            "Built with ❤️ for professional database management and development!"
        ]

        # Display content with scrolling if needed
        max_lines = h - 4  # Leave space for title and instructions
        start_line = 0

        while True:
            stdscr.clear()
            self.ui.draw_main_title(stdscr)

            # Display visible portion of content
            for i in range(max_lines):
                if start_line + i < len(content):
                    line = content[start_line + i]
                    # Truncate line if too long for screen
                    if len(line) > w - 4:
                        line = line[:w - 7] + "..."
                    stdscr.addstr(2 + i, 2, line, curses.color_pair(5))

            # Navigation instructions
            if len(content) > max_lines:
                stdscr.addstr(h - 2, 2, "Use ↑↓ to scroll, 'q' to quit", curses.color_pair(6))
            else:
                stdscr.addstr(h - 2, 2, "Press 'q' to return to main menu", curses.color_pair(6))

            stdscr.refresh()
            key = stdscr.getch()

            if key == curses.KEY_UP and start_line > 0:
                start_line -= 1
            elif key == curses.KEY_DOWN and start_line < len(content) - max_lines:
                start_line += 1
            elif key == ord('q'):
                break

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
            "Tools",
            "Read Me",
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
                    elif self.selected_option == 3:  # Tools
                        self.tools_menu(stdscr)
                    elif self.selected_option == 4:  # Read Me
                        self.read_me_screen(stdscr)
                    elif self.selected_option == 5:  # Disconnect
                        self.db.disconnect()
                    elif self.selected_option == 6:  # Quit
                        break
                elif key == ord('q'):
                    break

    def run(self):
        """Run the TUI"""
        curses.wrapper(self.main_loop)
