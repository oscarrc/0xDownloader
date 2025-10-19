"""
Configuration and constants for the YouTube Downloader application.
"""

import os

# App Configuration
APP_TITLE = "YouTube Downloader"
APP_GEOMETRY = "1000x700"

# CustomTkinter Configuration
APPEARANCE_MODE = "dark"
COLOR_THEME = "blue"

# Default paths
DEFAULT_OUTPUT_DIR = os.getcwd()

# UI Configuration
THUMBNAIL_HEIGHT = 110
THUMBNAIL_WIDTH = int(THUMBNAIL_HEIGHT * 16 / 9)  # Maintain 16:9 aspect ratio

# Video list frame configuration
VIDEO_LIST_WIDTH = 980
VIDEO_LIST_HEIGHT = 550

# Language file path
LANGUAGE_FILE = "lang.json"

# Links
OSCAR_WEBSITE = "https://oscarrc.me"
KO_FI_LINK = "https://ko-fi.com/oscarrc"
