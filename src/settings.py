"""
Settings module for DXF Viewer application.
Handles saving and loading application settings.
"""

import os
import json
from translations import Translations

class Settings:
    # Default settings
    DEFAULT_SETTINGS = {
        "language": Translations.DEFAULT_LANGUAGE,
        "window_state": {
            "maximized": True,
            "width": 1200,
            "height": 800
        }
    }
    
    def __init__(self):
        self.settings = self.DEFAULT_SETTINGS.copy()
        self.settings_file = self._get_settings_file_path()
        self.load()
    
    def _get_settings_file_path(self):
        """Get the path to the settings file"""
        # Get the directory where the script is located
        script_dir = os.path.dirname(os.path.abspath(__file__))
        # Settings file is in the parent directory
        return os.path.join(os.path.dirname(script_dir), "settings.json")
    
    def load(self):
        """Load settings from file"""
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    loaded_settings = json.load(f)
                    # Update settings with loaded values
                    self.settings.update(loaded_settings)
        except Exception as e:
            print(f"Error loading settings: {str(e)}")
    
    def save(self):
        """Save settings to file"""
        try:
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=4)
        except Exception as e:
            print(f"Error saving settings: {str(e)}")
    
    def get(self, key, default=None):
        """Get a setting value"""
        return self.settings.get(key, default)
    
    def set(self, key, value):
        """Set a setting value and save settings"""
        self.settings[key] = value
        self.save()
    
    @property
    def language(self):
        """Get current language"""
        return self.get("language", Translations.DEFAULT_LANGUAGE)
    
    @language.setter
    def language(self, value):
        """Set language and save settings"""
        self.set("language", value) 