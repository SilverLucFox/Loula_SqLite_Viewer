#!/usr/bin/env python3
"""
Setup script for Loula's SQLite Viewer
"""

from setuptools import setup, find_packages
import sys
import os

# Read the README file
def read_readme():
    with open("README.md", "r", encoding="utf-8") as fh:
        return fh.read()

# Read requirements
def read_requirements():
    requirements = []
    if os.path.exists("requirements.txt"):
        with open("requirements.txt", "r", encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if line and not line.startswith("#"):
                    requirements.append(line)
    return requirements

# Windows-specific dependencies
windows_deps = ["windows-curses>=2.3.0"] if sys.platform == "win32" else []

setup(
    name="loula-sqlite-viewer",
    version="2.2.3",
    author="SilverFox",
    author_email="jawadc444@gmail.com",
    description="A professional console-based SQLite database viewer and editor with enhanced TUI interface",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/SilverLucFox/Loula_SqLite_Viewer",
    packages=find_packages(where=".", include=["src*"]),
    package_dir={"": "."},
    include_package_data=True,
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Topic :: Database",
        "Topic :: Utilities",
    ],
    keywords="sqlite database viewer editor tui cli terminal",
    python_requires=">=3.6",
    install_requires=read_requirements() + windows_deps,
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=21.0",
            "flake8>=3.9",
            "mypy>=0.800",
        ],
        "build": [
            "build>=0.7",
            "twine>=3.0",
            "pyinstaller>=4.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "sqlite-viewer=src.core.main:main",
            "loula-sqlite=src.core.main:main",
        ],
    },
    project_urls={
        "Homepage": "https://github.com/SilverLucFox/Loula_SqLite_Viewer",
        "Repository": "https://github.com/SilverLucFox/Loula_SqLite_Viewer.git",
        "Issues": "https://github.com/SilverLucFox/Loula_SqLite_Viewer/issues",
        "Changelog": "https://github.com/SilverLucFox/Loula_SqLite_Viewer/blob/main/README.md",
    },
)