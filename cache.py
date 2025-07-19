# -*- coding: utf-8 -*-
"""
API cache management for Japanese Glossary Generator.
"""

import os
import json
from aqt.qt import QTimer
from .config import config
from .logger import write_log

ADDON_PATH = os.path.dirname(__file__)
CACHE_FILE_PATH = os.path.join(ADDON_PATH, "api_cache.json")

# Global cache variables
global_api_cache = {}
global_cache_timer = None

def load_api_cache():
    """Load API cache from file."""
    global global_api_cache
    
    if not config['cache']['cache_enabled']:
        write_log("API cache disabled in settings. Not loading cache.")
        global_api_cache = {}
        return

    if os.path.exists(CACHE_FILE_PATH):
        try:
            with open(CACHE_FILE_PATH, "r", encoding="utf-8") as f:
                global_api_cache = json.load(f)
            write_log("API cache loaded successfully.")
        except json.JSONDecodeError:
            write_log("Error reading api_cache.json. Starting with empty cache.")
            global_api_cache = {}
        except Exception as e:
            write_log(f"Error loading api_cache.json: {e}. Starting with empty cache.")
            global_api_cache = {}
    else:
        write_log("API cache file not found. Starting with empty cache.")
        global_api_cache = {}

def save_api_cache():
    """Save API cache to file."""
    if not config['cache']['cache_enabled']:
        write_log("API cache disabled in settings. Not saving cache.")
        return

    try:
        with open(CACHE_FILE_PATH, "w", encoding="utf-8") as f:
            json.dump(global_api_cache, f, indent=4)
        write_log("API cache saved successfully.")

        # Check cache file size and warn if it exceeds the limit
        if os.path.exists(CACHE_FILE_PATH):
            file_size_bytes = os.path.getsize(CACHE_FILE_PATH)
            file_size_mb = file_size_bytes / (1024 * 1024)
            max_size_mb = config['cache']['cache_max_size_mb']
            
            if max_size_mb > 0 and file_size_mb > max_size_mb:
                write_log(f"Warning: API cache file ({file_size_mb:.2f} MB) exceeds "
                         f"configured maximum size ({max_size_mb} MB). "
                         f"Consider clearing the cache or increasing the limit.")

    except Exception as e:
        write_log(f"Error saving api_cache.json: {e}")

def clear_api_cache():
    """Clear the API cache."""
    global global_api_cache
    global_api_cache = {}
    
    try:
        if os.path.exists(CACHE_FILE_PATH):
            os.remove(CACHE_FILE_PATH)
        write_log("API cache cleared successfully.")
    except Exception as e:
        write_log(f"Error clearing API cache: {e}")

def start_periodic_cache_save_timer():
    """Start the periodic cache save timer."""
    global global_cache_timer
    
    if not config['cache']['cache_enabled'] or config['cache']['cache_save_interval_minutes'] <= 0:
        if global_cache_timer and global_cache_timer.isActive():
            global_cache_timer.stop()
            write_log("Cache save timer stopped (cache disabled or interval is zero).")
        return

    interval_ms = config['cache']['cache_save_interval_minutes'] * 60 * 1000
    
    if global_cache_timer is None:
        global_cache_timer = QTimer()
        global_cache_timer.timeout.connect(save_api_cache)

    if not global_cache_timer.isActive() or global_cache_timer.interval() != interval_ms:
        global_cache_timer.start(interval_ms)
        write_log(f"Cache save timer started/adjusted to: {config['cache']['cache_save_interval_minutes']} minutes.")

def stop_periodic_cache_save_timer():
    """Stop the periodic cache save timer."""
    global global_cache_timer
    if global_cache_timer and global_cache_timer.isActive():
        global_cache_timer.stop()
        write_log("Cache save timer stopped on profile close.")

def get_cache_stats():
    """Get statistics about the cache."""
    cache_size = len(global_api_cache)
    cache_file_size = 0
    
    if os.path.exists(CACHE_FILE_PATH):
        cache_file_size = os.path.getsize(CACHE_FILE_PATH) / (1024 * 1024)  # MB
    
    return {
        "entries": cache_size,
        "file_size_mb": cache_file_size,
        "enabled": config['cache']['cache_enabled']
    }
