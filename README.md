# Loula's SQLite Viewer

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
python -m src.core.main

# Or run the CLI version
python -c "from src.core.cli import SQLiteCLI; cli = SQLiteCLI(); cli.cmdloop()"
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

## Installation

1. Clone or download the repository
2. Ensure Python 3.6+ is installed
3. For Windows users, the `windows-curses` package will be used for TUI if available
4. Run the application as described in Usage

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
├── src/
│   ├── __init__.py          # Package initialization
│   ├── core/
│   │   ├── __init__.py      # Core module
│   │   ├── main.py          # Application entry point
│   │   └── cli.py           # Command Line Interface (CLI)
│   ├── database/
│   │   ├── __init__.py      # Database module
│   │   └── database.py      # Database operations
│   ├── ui/
│   │   ├── __init__.py      # UI module
│   │   ├── tui.py           # Text User Interface (TUI)
│   │   ├── screens.py       # Screen classes for TUI
│   │   ├── table_browser.py # Table browsing functionality
│   │   └── ui_utils.py      # UI utility functions
│   ├── config/
│   │   ├── __init__.py      # Config module
│   │   ├── config.py        # Configuration management
│   │   └── db_config.json   # User configuration
│   └── tools/
│       ├── __init__.py      # Tools module
│       └── tools.py         # SQL tools
├── LICENSE
├── README.md                # This file
└── __pycache__/
```

### Architecture

The application is organized into modular components:

- **Core Module (`src/core/`)**: Contains the main entry point and CLI interface
  - `main.py`: Entry point that chooses between TUI and CLI based on curses availability
  - `cli.py`: Command-line interface for scripting and headless operation

- **Database Module (`src/database/`)**: Handles all SQLite database operations
  - `database.py`: DatabaseManager class for connecting, querying, and managing SQLite databases

- **UI Module (`src/ui/`)**: Text User Interface components
  - `tui.py`: Main TUI class coordinating the interface
  - `screens.py`: Individual screen classes for different menus
  - `table_browser.py`: Table browsing and data display functionality
  - `ui_utils.py`: Utility functions for UI operations

- **Config Module (`src/config/`)**: Configuration and persistence
  - `config.py`: ConfigManager class for saving databases and settings
  - `db_config.json`: JSON file storing saved databases and last connection

- **Tools Module (`src/tools/`)**: SQL and utility tools
  - `tools.py`: SQLTools class for executing queries and SQL operations

### How It Works

1. **Startup**: `main.py` checks for curses library availability
   - If available, launches TUI mode with `SQLiteTUI`
   - If not, falls back to CLI mode with `SQLiteCLI`

2. **TUI Mode**: Uses curses for full-screen text interface
   - `SQLiteTUI` manages the main loop and menu navigation
   - Delegates to `ConnectionScreens` for connection management
   - Uses `TableBrowser` for data browsing
   - Leverages `SQLTools` for query execution

3. **Database Operations**: All database interactions go through `DatabaseManager`
   - Connects to SQLite files
   - Executes queries and fetches results
   - Manages connections and transactions

4. **Configuration**: `ConfigManager` handles persistence
   - Saves database connections with colors
   - Remembers last connected database
   - Stores settings in JSON format

5. **CLI Mode**: Command-line interface for automation
   - Interactive shell with commands like `connect`, `select`, etc.
   - Useful for scripting and headless environments
