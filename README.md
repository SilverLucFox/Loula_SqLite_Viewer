# Loula SQLite Viewer

A professional console-based SQLite database viewer and editor with an enhanced TUI interface.

## Features

- **Professional TUI Interface** - Navigate with arrow keys, just like Linux task managers (htop)
- **Color-coded Display** - Easy to read interface with visual feedback
- **Database Management** - Save multiple databases with custom colors
- **Menu-driven Navigation** - No need to remember commands
- **Connect to SQLite databases** - Save database path and name for quick reconnection
- **Browse Tables and Schemas** - View table structures and data
- **Execute SQL Commands** - Full SQL support for queries and modifications
- **Robust Error Handling** - Professional-grade reliability

## Interface

The viewer features a professional Text User Interface (TUI) similar to Linux task managers:

- **Arrow Keys**: Navigate menu options
- **Enter**: Select option
- **'q'**: Quit application
- **'b' or Escape**: Go back to previous menu

## Usage

### Running the Application

```bash
# Run with TUI (recommended)
python main.py

# Or run the legacy single-file version
python sqlite_viewer.py
```

### Main Menu Options:

- **Connect to Database**: Connect to ANY SQLite database file by entering path and name
- **Browse Tables**: **NEW!** Split-screen interface to browse tables and their contents with pagination
- **Execute SQL**: Run custom SQL queries
- **Disconnect**: Close current database connection
- **Quit**: Exit the application

### Navigation:

- Use ↑↓ arrow keys to highlight options
- Press Enter to choose
- Press 'q' to quit from any screen

### Table Browser Features:

- **Split-Screen Layout**: Table list on left, data on right
- **Professional Table Format**: Properly aligned columns with headers and separators
- **Auto Column Sizing**: Columns adjust to content with smart truncation
- **Table Selection**: Use ↑↓ to select tables from the left panel
- **Data Pagination**: Use ←→ to navigate through large tables
- **Column Headers**: Automatic display of column names with table separators
- **Page Information**: Shows current page and total rows

## Requirements

- Python 3.6+
- `windows-curses` (automatically installed for Windows)

## Examples

1. **Connect to a new database**:

   - Select "Connect to Database"
   - Choose "Connect to New Database"
   - Enter path: `C:\path\to\your\database.db`
   - Enter name: `mydatabase`
   - Select a color for the database

2. **Connect to a saved database**:

   - Select "Connect to Database"
   - Choose "Connect to Saved Database"
   - Use arrow keys to select from saved databases (shown in their assigned colors)
   - Press Enter to connect
   - Press 'd' to delete a saved database

3. **Browse and query**:
   - Use "Browse Tables" to open the split-screen table browser
   - Use ↑↓ to select tables from the left panel
   - Use ←→ to navigate through table pages on the right
   - Use "Execute SQL" to run custom queries like `SELECT * FROM users WHERE age > 25`

The interface remembers your saved databases with their colors and automatically reconnects to the last used database on startup!

## Project Structure

```
Loula_SqLite_Viewer/
├── main.py              # Application entry point
├── tui.py               # Text User Interface (TUI)
├── cli.py               # Command Line Interface (CLI)
├── database.py          # Database operations
├── config.py            # Configuration management
├── sqlite_viewer.py     # Legacy single-file version
├── create_test_db.py    # Test database creator
├── test_viewer.py       # Test scripts
├── __init__.py          # Package initialization
├── db_config.json       # User configuration
└── README.md           # This file
```

### Architecture

- **main.py**: Entry point that chooses between TUI and CLI
- **tui.py**: Professional text-based user interface with menus
- **cli.py**: Command-line interface for scripting
- **database.py**: All SQLite database operations
- **config.py**: Configuration and saved databases management
