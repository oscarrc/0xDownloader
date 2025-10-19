"""
Utility functions for the YouTube Downloader application.
"""

import json
import os
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
    import re
    return re.sub(r'[<>:"/\\|?*]', '_', filename)
