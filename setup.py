#!/usr/bin/env python3
"""
Setup script for CRAB Tracker package.
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8")

# Read requirements
requirements = []
with open("requirements.txt", "r", encoding="utf-8") as f:
    for line in f:
        line = line.strip()
        if line and not line.startswith("#"):
            requirements.append(line)

setup(
    name="crab-tracker",
    version="1.0.0",
    description="EVE Online Log Reader and Beacon Analysis Tool",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="WildGear",
    author_email="WildGear@example.com",
    url="https://github.com/yourusername/crab-tracker",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Games/Entertainment",
        "Topic :: Utilities",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pyinstaller>=5.0.0",
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=22.0.0",
            "flake8>=5.0.0",
            "mypy>=1.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "crab-tracker=crab_tracker.main:main",
        ],
    },
    include_package_data=True,
    package_data={
        "crab_tracker": [
            "resources/config/*.json",
            "resources/build/*.txt",
        ],
    },
    zip_safe=False,
)
