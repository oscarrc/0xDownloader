"""
Utility functions for the YouTube Downloader application.
"""

import json
import os
import re
from urllib.parse import urlparse
from config import LANGUAGE_FILE, LOCALES_FILE


def load_language_names():
    """Load language names from the JSON file."""
    try:
        with open(LANGUAGE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}


def load_audio_locale_names():
    """Load display names for locales (locale -> "Language (Country)") from LOCALES_FILE."""
    try:
        with open(LOCALES_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}


def get_language_display_name(lang_or_locale_code: str) -> str:
    """Get the display name for a language or locale code.

    Preference order:
    1) Exact match in LANGUAGE_FILE (e.g., "en")
    2) Exact match in LOCALES_FILE (e.g., "en-US")
    3) Base language match in LANGUAGE_FILE (for codes like "en-US" -> "en")
    4) Fallback to original code
    """
    if not lang_or_locale_code:
        return lang_or_locale_code

    language_names = load_language_names()
    if lang_or_locale_code in language_names:
        return language_names[lang_or_locale_code]

    locale_names = load_audio_locale_names()
    if lang_or_locale_code in locale_names:
        return locale_names[lang_or_locale_code]

    if "-" in lang_or_locale_code:
        base = lang_or_locale_code.split("-", 1)[0]
        if base in language_names:
            return language_names[base]

    return lang_or_locale_code


## locale-specific display helper removed; use get_language_display_name


def find_language_code_by_name(display_name: str) -> str:
    """Find a code for a display name.

    Preference order:
    1) Match name in LANGUAGE_FILE -> return language code (e.g., "English" -> "en")
    2) Match name in LOCALES_FILE values -> return locale code (e.g., "English (United States)" -> "en-US")
    3) Fallback: return the original display_name
    """
    language_names = load_language_names()
    for code, name in language_names.items():
        if name == display_name:
            return code

    locale_names = load_audio_locale_names()
    for code, name in locale_names.items():
        if name == display_name:
            return code

    return display_name


## locale-specific reverse lookup removed; use find_language_code_by_name


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
