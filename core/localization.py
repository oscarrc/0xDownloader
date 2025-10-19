"""
Localization and internationalization support for the YouTube Downloader application.
"""

import json
import os
import locale
from typing import Dict, Any


class LocalizationManager:
    """Manages application localization and translations."""
    
    def __init__(self, locales_dir: str = "locales"):
        self.locales_dir = locales_dir
        self.current_language = self._detect_system_language()
        self.translations = {}
        self._load_translations()
    
    def _detect_system_language(self) -> str:
        """Detect the system language and return appropriate language code."""
        try:
            system_lang = locale.getdefaultlocale()[0]
            if system_lang and system_lang.startswith('es'):
                return 'es'
            else:
                return 'en'  # Default to English
        except:
            return 'en'  # Fallback to English
    
    def _load_translations(self):
        """Load translations for the current language."""
        try:
            lang_file = os.path.join(self.locales_dir, f"{self.current_language}.json")
            with open(lang_file, 'r', encoding='utf-8') as f:
                self.translations = json.load(f)
        except FileNotFoundError:
            # Fallback to English if current language file not found
            if self.current_language != 'en':
                try:
                    en_file = os.path.join(self.locales_dir, "en.json")
                    with open(en_file, 'r', encoding='utf-8') as f:
                        self.translations = json.load(f)
                    self.current_language = 'en'
                except FileNotFoundError:
                    self.translations = {}
    
    def set_language(self, language_code: str):
        """Set the current language and reload translations."""
        if language_code in ['en', 'es']:
            self.current_language = language_code
            self._load_translations()
    
    def get(self, key: str, default: str = None) -> str:
        """
        Get a translated string by key.
        
        Args:
            key: Translation key in dot notation (e.g., 'app.title')
            default: Default value if key not found
            
        Returns:
            Translated string or default value
        """
        keys = key.split('.')
        value = self.translations
        
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default or key
    
    def get_available_languages(self) -> Dict[str, str]:
        """Get available languages with their display names."""
        return {
            'en': 'English',
            'es': 'Español'
        }
    
    def get_current_language(self) -> str:
        """Get the current language code."""
        return self.current_language


# Global localization manager instance
localization = LocalizationManager()
