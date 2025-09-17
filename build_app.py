#!/usr/bin/env python3
"""
Build script for Loula's SQLite Viewer
Creates standalone executables using PyInstaller
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

def run_command(cmd, description):
    """Run a command and handle errors"""
    print(f"\n{description}...")
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        print(f"✓ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ {description} failed:")
        print(f"Error: {e.stderr}")
        return False

def cleanup_build_artifacts():
    """Clean up build artifacts"""
    print("Cleaning up build artifacts...")
    for dir_name in ["build", "dist"]:
        if os.path.exists(dir_name):
            try:
                import shutil
                import time
                # Try to remove, if it fails, wait and retry
                try:
                    shutil.rmtree(dir_name)
                except PermissionError:
                    print(f"Waiting for {dir_name} to be available...")
                    time.sleep(2)
                    shutil.rmtree(dir_name)
                print(f"✓ Cleaned {dir_name} directory")
            except Exception as e:
                print(f"✗ Could not clean {dir_name}: {e}")
                return False
    return True

def create_executable():
    """Create standalone executable using PyInstaller"""
    print("Building Loula's SQLite Viewer executable...")

    # Determine platform-specific settings
    system = platform.system().lower()
    if system == "windows":
        exe_name = "sqlite-viewer.exe"
        console = True   # Show console on Windows for CLI/TUI apps
    else:
        exe_name = "sqlite-viewer"
        console = True   # Use console mode on Unix-like systems

    # Check if executable is currently running
    exe_path = os.path.join("dist", exe_name)
    if os.path.exists(exe_path):
        print(f"Warning: {exe_path} exists and may be in use.")
        print("Please close any running instances of the application before building.")

    # Clean up previous build artifacts
    if not cleanup_build_artifacts():
        return False

    # Create directories
    os.makedirs("build", exist_ok=True)
    os.makedirs("dist", exist_ok=True)

    # Determine platform-specific settings
    system = platform.system().lower()
    if system == "windows":
        exe_name = "sqlite-viewer.exe"
        console = False  # Use windowed mode on Windows
    else:
        exe_name = "sqlite-viewer"
        console = True   # Use console mode on Unix-like systems

    # PyInstaller command
    cmd = [
        "pyinstaller",
        "--onefile",                    # Create single executable
        "--name", "sqlite-viewer",      # Executable name
        "--distpath", "dist",           # Output directory
        "--workpath", "build",          # Working directory
        "--specpath", "build",          # Spec file directory
        "--clean",                      # Clean cache
        "--noconfirm",                  # Don't ask for confirmation
    ]

    # For console applications like SQLite Viewer, we always want to show the console
    # Remove the --noconsole flag if it exists (though it shouldn't be added with console=True)
    if "--noconsole" in cmd:
        cmd.remove("--noconsole")

    # Add data files
    data_files = []
    if os.path.exists("db_config.json"):
        data_files.append(("db_config.json", "."))
    if os.path.exists("README.md"):
        data_files.append(("README.md", "."))
    if os.path.exists("LICENSE"):
        data_files.append(("LICENSE", "."))

    for src, dst in data_files:
        src_abs = os.path.join(os.getcwd(), src)
        cmd.extend(["--add-data", f"{src_abs}{os.pathsep}{dst}"])

    # Add the main script with absolute path
    main_script = os.path.join(os.getcwd(), "src", "core", "main.py")
    cmd.append(main_script)

    # Run PyInstaller
    success = run_command(" ".join(cmd), "Creating executable with PyInstaller")

    if success:
        exe_path = os.path.join("dist", exe_name)
        if os.path.exists(exe_path):
            print(f"\n✓ Executable created successfully: {exe_path}")
            print(f"File size: {os.path.getsize(exe_path)} bytes")
        else:
            print("\n✗ Executable not found in expected location")
    else:
        print("\n✗ Failed to create executable")

def create_wheel():
    """Create Python wheel distribution"""
    print("\nCreating Python wheel distribution...")
    success = run_command("python -m build --wheel", "Building wheel distribution")
    return success

def create_sdist():
    """Create source distribution"""
    print("\nCreating source distribution...")
    success = run_command("python -m build --sdist", "Building source distribution")
    return success

def install_locally():
    """Install the package locally for testing"""
    print("\nInstalling package locally...")
    success = run_command("pip install -e .", "Installing package in development mode")
    return success

def main():
    """Main build function"""
    print("Loula's SQLite Viewer Build Script")
    print("=" * 40)

    # Check if we're in the right directory
    if not os.path.exists("src/core/main.py"):
        print("Error: Please run this script from the project root directory")
        sys.exit(1)

    # Check if PyInstaller is installed
    try:
        import PyInstaller
        print(f"PyInstaller version: {PyInstaller.__version__}")
    except ImportError:
        print("PyInstaller not found. Installing...")
        run_command("pip install pyinstaller", "Installing PyInstaller")

    # Check if build is installed
    try:
        import build
        print("Build module available")
    except ImportError:
        print("Build not found. Installing...")
        run_command("pip install build", "Installing build")

    # Ask user what to build
    print("\nBuild options:")
    print("1. Create executable only")
    print("2. Create Python distributions (wheel + sdist)")
    print("3. Install locally for testing")
    print("4. Build everything")
    print("5. Clean build artifacts only")

    choice = input("\nEnter your choice (1-5): ").strip()

    if choice == "1":
        create_executable()
    elif choice == "2":
        create_wheel()
        create_sdist()
    elif choice == "3":
        install_locally()
    elif choice == "4":
        create_executable()
        create_wheel()
        create_sdist()
    elif choice == "5":
        cleanup_build_artifacts()
        print("Cleanup completed!")
    else:
        print("Invalid choice. Exiting.")
        sys.exit(1)

    print("\nBuild process completed!")

if __name__ == "__main__":
    main()