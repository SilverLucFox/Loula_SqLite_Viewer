#!/usr/bin/env python3
"""
Loula's SQLite Viewer - Main Entry Point
"""

import os
import sys

try:
    import curses
    HAS_CURSES = True
except ImportError:
    HAS_CURSES = False

def can_use_curses():
    """Check if curses can actually be used in this environment"""
    if not HAS_CURSES:
        return False

    # Check if stdout/stderr exist and are TTYs
    try:
        if sys.stdout is None or sys.stderr is None:
            return False
        if not sys.stdout.isatty() or not sys.stderr.isatty():
            return False
    except (AttributeError, OSError):
        # Handle cases where isatty() is not available or fails
        return False

    # Check for environment variables that indicate non-interactive environments
    non_interactive_terms = ['dumb', 'unknown', '']
    term = os.environ.get('TERM', '').lower()
    if term in non_interactive_terms:
        return False

    # Check if we're running in certain IDEs or environments
    if os.environ.get('PYCHARM_HOSTED') or os.environ.get('VSCODE_PID'):
        return False

    return True

from src.ui.tui import SQLiteTUI
from src.core.cli import SQLiteCLI


def main():
    """Main application entry point"""
    if can_use_curses():
        try:
            tui = SQLiteTUI()
            tui.run()
        except KeyboardInterrupt:
            print("\nGoodbye!")
        except Exception as e:
            # Handle curses initialization errors and other TUI issues
            error_msg = str(e).lower()
            if any(keyword in error_msg for keyword in ['curses', 'tty', 'terminal', 'fileno', 'initscr']):
                print("Terminal interface not available in this environment.")
                print("Falling back to command-line interface...")
                print("For enhanced interface, try running in a proper terminal.")
                print()
                try:
                    cli = SQLiteCLI()
                    cli.cmdloop()
                except Exception as cli_error:
                    print(f"CLI also failed: {cli_error}")
                    print("Please check your Python environment and try again.")
            else:
                # Re-raise non-curses related errors
                raise
    else:
        print("Using command-line interface.")
        if not HAS_CURSES:
            print("Note: curses not available. Install windows-curses for enhanced interface: pip install windows-curses")
        else:
            print("Note: Terminal environment not suitable for interactive interface.")
        print()
        try:
            cli = SQLiteCLI()
            cli.cmdloop()
        except Exception as e:
            print(f"CLI failed: {e}")
            print("Please check your Python environment and try again.")


if __name__ == "__main__":
    main()
