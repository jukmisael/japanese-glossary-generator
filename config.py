# -*- coding: utf-8 -*-
"""
Configuration management for Japanese Glossary Generator.
"""

import os
import json
from .logger import write_log

ADDON_PATH = os.path.dirname(__file__)
CONFIG_FILE_PATH = os.path.join(ADDON_PATH, "config.json")

def get_default_config():
    """Get the default configuration settings."""
    return {
        "general": {
            "include_hiragana": True,
            "include_katakana": True,
            "include_kanji": True,
            "include_romaji": True,
            "include_kanji_meanings": True,
            "ignore_existing_glossary_notes": False,
            "overwrite_existing_glossary_notes": False,
        },
        "performance": {
            "max_workers": 4,
            "api_call_workers": 2,
            "batch_size": 50,
            "pause_between_batches_ms": 500,
            "pause_per_api_call_ms": 50,
        },
        "cache": {
            "cache_enabled": True,
            "cache_max_size_mb": 10,
            "cache_save_interval_minutes": 15
        }
    }

def load_config():
    """Load configuration from file, using defaults if file doesn't exist."""
    config = get_default_config()
    
    if os.path.exists(CONFIG_FILE_PATH):
        try:
            with open(CONFIG_FILE_PATH, "r", encoding="utf-8") as f:
                user_config = json.load(f)
            
            # Merge user config with defaults
            for main_key, main_value in config.items():
                if main_key in user_config:
                    if isinstance(main_value, dict):
                        main_value.update(user_config[main_key])
                    else:
                        config[main_key] = user_config[main_key]
        except json.JSONDecodeError:
            write_log("Error reading config.json. Using default configuration.")
        except Exception as e:
            write_log(f"Error loading config.json: {e}. Using default configuration.")
    
    return config

def save_config(config_data):
    """Save configuration to file."""
    try:
        with open(CONFIG_FILE_PATH, "w", encoding="utf-8") as f:
            json.dump(config_data, f, indent=4)
        
        global config
        config = config_data
        write_log("Configuration saved successfully.")
        return True
    except Exception as e:
        write_log(f"Error saving config.json: {e}")
        return False

# Initialize global config
config = load_config()
