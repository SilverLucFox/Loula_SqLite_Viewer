#!/usr/bin/env python3
"""
Loula's SQLite Viewer - Main Entry Point
"""

try:
    import curses
    HAS_CURSES = True
except ImportError:
    HAS_CURSES = False

from src.ui.tui import SQLiteTUI
from src.core.cli import SQLiteCLI


def main():
    """Main application entry point"""
    if HAS_CURSES:
        try:
            tui = SQLiteTUI()
            tui.run()
        except KeyboardInterrupt:
            print("\nGoodbye!")
    else:
        print("curses not available. Using command-line interface.")
        print("For enhanced interface, install windows-curses: pip install windows-curses")
        cli = SQLiteCLI()
        cli.cmdloop()


if __name__ == "__main__":
    main()
