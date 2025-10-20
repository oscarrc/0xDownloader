"""
Utility functions for the YouTube Downloader application.
"""

import json
import os
import re
from urllib.parse import urlparse
from config import LANGUAGE_FILE


def load_language_names():
    """Load language names from the JSON file."""
    try:
        with open(LANGUAGE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}


def get_language_display_name(lang_code):
    """Get the display name for a language code."""
    language_names = load_language_names()
    if lang_code in language_names:
        return language_names[lang_code]
    else:
        return lang_code


def find_language_code_by_name(language_name):
    """Find the language code that corresponds to a display name."""
    language_names = load_language_names()
    for code, name in language_names.items():
        if name == language_name:
            return code
    return language_name  # fallback to original


def sanitize_filename(filename):
    """Sanitize filename by removing invalid characters."""
    return re.sub(r'[<>:"/\\|?*]', '_', filename)


def is_valid_url(url):
    """
    Check if the provided string is a valid URL.
    
    Args:
        url (str): The URL to validate
        
    Returns:
        bool: True if valid URL, False otherwise
    """
    if not url or not isinstance(url, str):
        return False
    
    # Remove whitespace
    url = url.strip()
    
    if not url:
        return False
    
    try:
        # Parse the URL
        parsed = urlparse(url)
        
        # Check if it's a valid URL with scheme and netloc
        return bool(parsed.scheme and parsed.netloc)
        
    except Exception:
        return False
