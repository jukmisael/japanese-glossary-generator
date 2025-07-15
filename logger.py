# -*- coding: utf-8 -*-
"""
Logging utilities for Japanese Glossary Generator.
"""

import os
from datetime import datetime

ADDON_PATH = os.path.dirname(__file__)
LOG_FILE_PATH = os.path.join(ADDON_PATH, "japanese_glossary_log.txt")

# Global log file mode
log_file_mode = "a"

def write_log(message: str):
    """Write a message to the log file with timestamp."""
    global log_file_mode
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] {message}\n"
    
    try:
        with open(LOG_FILE_PATH, log_file_mode, encoding="utf-8") as f:
            f.write(log_entry)
        
        # After first write, switch to append mode
        if log_file_mode == "w":
            log_file_mode = "a"
    except Exception as e:
        print(f"Error writing to log file: {e}")

def clear_log():
    """Clear the log file."""
    global log_file_mode
    log_file_mode = "w"
    try:
        with open(LOG_FILE_PATH, "w", encoding="utf-8") as f:
            f.write("")
        write_log("Log file cleared.")
    except Exception as e:
        print(f"Error clearing log file: {e}")

def get_log_content():
    """Get the current log file content."""
    try:
        if os.path.exists(LOG_FILE_PATH):
            with open(LOG_FILE_PATH, "r", encoding="utf-8") as f:
                return f.read()
        return "Log file not found."
    except Exception as e:
        return f"Error reading log file: {e}"
