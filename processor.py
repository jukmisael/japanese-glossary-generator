# -*- coding: utf-8 -*-
"""
Main processing logic for batch glossary generation.
"""

import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from aqt import mw
from aqt.utils import showInfo, askUser
from anki.utils import html_to_text_line

from .config import config
from .logger import write_log
from .glossary_generator import generate_glossary_data
from .stats import (global_stats, start_processing, increment_processed, 
                   increment_updated, increment_unchanged, increment_empty, 
                   increment_error, is_processing_cancelled)
from .cache import save_api_cache

def add_field_to_model(model_name, field_name):
    """Add a field to a note model if it doesn't exist."""
    model = mw.col.models.by_name(model_name)
    if not model:
        write_log(f"Model '{model_name}' not found.")
        return False
    
    existing_fields = [f['name'] for f in model['flds']]
    if field_name not in existing_fields:
        new_field = mw.col.models.new_field(field_name)
        mw.col.models.add_field(model, new_field)
        mw.col.models.save(model)
        write_log(f"Field '{field_name}' added to note type '{model_name}'.")
    
    return True

def _process_note_task(note_id, source_field, target_field):
    """Process a single note to generate glossary content."""
    try:
        note = mw.col.get_note(note_id)
        
        # Get source text
        source_text = ""
        if source_field in note:
            source_text = html_to_text_line(note[source_field])
        
        if not source_text.strip():
            increment_empty()
            return (note_id, None, "Empty")
        
        # Generate glossary
        glossary_html = generate_glossary_data(source_text)
        
        # Check if update is needed
        if glossary_html and note[target_field] != glossary_html:
            return (note_id, glossary_html, "Updated")
        
        increment_unchanged()
        return (note_id, None, "Unchanged")
        
    except Exception as e:
        increment_error()
        write_log(f"Error processing note {note_id}: {e}")
        return (note_id, None, f"Error: {e}")

def _run_batch_glossary_process_background(params):
    """Background task for batch glossary processing."""
    deck_name = params["deck_name"]
    note_type_name = params["note_type_name"]
    source_field = params["source_field"]
    target_field = params["target_field"]
    note_ids = params["note_ids"]
    
    # Clear log file for new session
    from .logger import log_file_mode
    log_file_mode = "w"
    
    # Get performance settings
    cfg_perf = config['performance']
    batch_size = cfg_perf['batch_size']
    pause_ms = cfg_perf['pause_between_batches_ms']
    
    # Split notes into batches
    batches = [note_ids[i:i + batch_size] for i in range(0, len(note_ids), batch_size)]
    
    # Initialize statistics
    start_processing(len(note_ids))
    
    try:
        for batch_index, batch_ids in enumerate(batches):
            if is_processing_cancelled():
                write_log("Processing cancelled by user.")
                break
            
            # Process batch
            results = []
            with ThreadPoolExecutor(max_workers=cfg_perf['max_workers']) as executor:
                future_to_nid = {
                    executor.submit(_process_note_task, nid, source_field, target_field): nid 
                    for nid in batch_ids
                }
                
                for future in as_completed(future_to_nid):
                    results.append(future.result())
            
            # Save updated notes
            for note_id, glossary_html, status in results:
                if status == "Updated":
                    try:
                        note = mw.col.get_note(note_id)
                        note[target_field] = glossary_html
                        note.flush()
                        increment_updated()
                    except Exception as e:
                        write_log(f"Error saving note {note_id}: {e}")
                        increment_error()
                
                increment_processed()
            
            # Save cache periodically
            save_api_cache()
            
            # Pause between batches if configured
            if batch_index < len(batches) - 1 and pause_ms > 0:
                time.sleep(pause_ms / 1000.0)
    
    except Exception as e:
        write_log(f"Unexpected error in batch processing: {e}")
        raise
    
    return global_stats["updated_notes"], global_stats["total_notes"]

def _on_batch_glossary_process_complete(future):
    """Handle completion of batch processing."""
    try:
        updated_count, total_notes = future.result()
        
        if not is_processing_cancelled():
            showInfo(f"Processing completed!\n{updated_count} of {total_notes} notes were updated.")
        else:
            showInfo(f"Processing cancelled.\n{updated_count} of {total_notes} notes were updated before cancellation.")
    
    except Exception as e:
        write_log(f"Unexpected error in batch processing: {e}")
        showInfo(f"An error occurred during processing: {e}")
    
    finally:
        # Clean up stats dialog
        if hasattr(mw, "glossary_stats_dialog") and mw.glossary_stats_dialog.isVisible():
            mw.glossary_stats_dialog.close()
            del mw.glossary_stats_dialog
        
        # Reset Anki interface
        mw.reset()

def run_batch_glossary_process(deck_name, note_type_name, source_field, target_field):
    """Run the batch glossary generation process."""
    # Validate note type
    model = mw.col.models.by_name(note_type_name)
    if not model:
        showInfo(f"Note type '{note_type_name}' not found.")
        return
    
    model_fields = [f['name'] for f in model['flds']]
    
    # Handle target field
    if target_field in model_fields:
        if not config['general']['overwrite_existing_glossary_notes']:
            if not askUser(f"The target field '{target_field}' already exists in this note type. "
                          f"Do you want to overwrite existing content?"):
                showInfo("Operation cancelled.")
                return
    else:
        if not askUser(f"The field '{target_field}' does not exist. "
                      f"Do you want to create it in note type '{note_type_name}'?"):
            showInfo("Operation cancelled.")
            return
        
        if not add_field_to_model(note_type_name, target_field):
            showInfo("Failed to add field to note type.")
            return
    
    # Build query
    query = f'deck:"{deck_name}" note:"{note_type_name}"'
    
    # Optionally ignore notes with existing glossary
    if config['general']['ignore_existing_glossary_notes']:
        query += f' {target_field}:'
    
    # Find notes
    note_ids = mw.col.find_notes(query)
    if not note_ids:
        showInfo("No notes found matching the selected criteria.")
        return
    
    # Reset cancellation flag
    global_stats["is_cancelled"] = False
    
    # Show progress dialog
    from .dialogs import ProcessingStatsDialog
    mw.glossary_stats_dialog = ProcessingStatsDialog(mw)
    mw.glossary_stats_dialog.show()
    
    # Prepare parameters
    params = {
        "deck_name": deck_name,
        "note_type_name": note_type_name,
        "source_field": source_field,
        "target_field": target_field,
        "note_ids": note_ids
    }
    
    # Run in background
    mw.taskman.run_in_background(
        lambda: _run_batch_glossary_process_background(params),
        _on_batch_glossary_process_complete
    )
