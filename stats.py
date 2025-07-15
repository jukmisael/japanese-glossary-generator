# -*- coding: utf-8 -*-
"""
Statistics tracking for Japanese Glossary Generator.
"""

import time

# Global statistics dictionary
global_stats = {
    "total_notes": 0,
    "processed_notes": 0,
    "updated_notes": 0,
    "unchanged_notes": 0,
    "empty_notes": 0,
    "error_notes": 0,
    "cache_hits": 0,
    "api_calls": 0,
    "start_time": 0.0,
    "elapsed_time": 0.0,
    "eta": "N/A",
    "is_cancelled": False,
}

def reset_stats():
    """Reset all statistics to initial values."""
    global global_stats
    global_stats.update({
        "total_notes": 0,
        "processed_notes": 0,
        "updated_notes": 0,
        "unchanged_notes": 0,
        "empty_notes": 0,
        "error_notes": 0,
        "cache_hits": 0,
        "api_calls": 0,
        "start_time": 0.0,
        "elapsed_time": 0.0,
        "eta": "N/A",
        "is_cancelled": False,
    })

def start_processing(total_notes):
    """Initialize statistics for a new processing session."""
    reset_stats()
    global_stats["total_notes"] = total_notes
    global_stats["start_time"] = time.time()

def update_progress():
    """Update time-based statistics."""
    global_stats["elapsed_time"] = time.time() - global_stats["start_time"]
    
    if global_stats["processed_notes"] > 0:
        notes_remaining = global_stats["total_notes"] - global_stats["processed_notes"]
        time_per_note = global_stats["elapsed_time"] / global_stats["processed_notes"]
        eta_seconds = notes_remaining * time_per_note
        global_stats["eta"] = f"{int(eta_seconds // 60)}m {int(eta_seconds % 60)}s"
    else:
        global_stats["eta"] = "Calculating..."

def increment_processed():
    """Increment processed notes counter."""
    global_stats["processed_notes"] += 1
    update_progress()

def increment_updated():
    """Increment updated notes counter."""
    global_stats["updated_notes"] += 1

def increment_unchanged():
    """Increment unchanged notes counter."""
    global_stats["unchanged_notes"] += 1

def increment_empty():
    """Increment empty notes counter."""
    global_stats["empty_notes"] += 1

def increment_error():
    """Increment error notes counter."""
    global_stats["error_notes"] += 1

def cancel_processing():
    """Mark processing as cancelled."""
    global_stats["is_cancelled"] = True

def is_processing_cancelled():
    """Check if processing has been cancelled."""
    return global_stats["is_cancelled"]

def get_progress_percentage():
    """Get the current progress as a percentage."""
    if global_stats["total_notes"] > 0:
        return (global_stats["processed_notes"] / global_stats["total_notes"]) * 100
    return 0

def get_processing_summary():
    """Get a summary of the processing results."""
    return {
        "total": global_stats["total_notes"],
        "processed": global_stats["processed_notes"],
        "updated": global_stats["updated_notes"],
        "unchanged": global_stats["unchanged_notes"],
        "empty": global_stats["empty_notes"],
        "errors": global_stats["error_notes"],
        "cache_hits": global_stats["cache_hits"],
        "api_calls": global_stats["api_calls"],
        "elapsed_time": global_stats["elapsed_time"],
        "cancelled": global_stats["is_cancelled"]
    }
