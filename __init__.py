# -*- coding: utf-8 -*-
"""
Japanese Glossary Generator for Anki
Automatically generates glossaries for Japanese text with hiragana, katakana, and kanji information.
"""

import os
from aqt import mw, gui_hooks
from aqt.qt import QAction
from aqt.utils import showInfo

from .config import config, load_config, save_config
from .cache import load_api_cache, save_api_cache, start_periodic_cache_save_timer, stop_periodic_cache_save_timer
from .dialogs import BatchGlossaryDialog, SettingsDialog, AboutDialog
from .logger import write_log

ADDON_NAME = "Japanese Glossary Generator"
ADDON_VERSION = "2.1.1"
ADDON_AUTHOR = "Misael FIlho"
ADDON_DESCRIPTION = "Automatically generates comprehensive glossaries for Japanese text with hiragana, katakana, and kanji information using external APIs."

def show_batch_glossary_dialog():
    """Show the main batch glossary generation dialog."""
    dialog = BatchGlossaryDialog(mw)
    if dialog.exec():
        from .processor import run_batch_glossary_process
        run_batch_glossary_process(**dialog.data)

def open_settings_dialog():
    """Open the settings configuration dialog."""
    dialog = SettingsDialog(mw)
    dialog.exec()

def show_about_dialog():
    """Show the about dialog with add-on information."""
    dialog = AboutDialog(mw)
    dialog.exec()

def setup_menu():
    """Set up the add-on menu in Anki's Tools menu."""
    glossary_menu = mw.form.menuTools.addMenu(ADDON_NAME)
    
    # Main functionality
    action_run = QAction("Generate Glossary in Batch...", mw)
    action_run.triggered.connect(show_batch_glossary_dialog)
    glossary_menu.addAction(action_run)
    
    glossary_menu.addSeparator()
    
    # Settings
    action_settings = QAction("Settings...", mw)
    action_settings.triggered.connect(open_settings_dialog)
    glossary_menu.addAction(action_settings)
    
    # About
    action_about = QAction("About...", mw)
    action_about.triggered.connect(show_about_dialog)
    glossary_menu.addAction(action_about)

def on_profile_opened():
    """Initialize add-on when profile is opened."""
    load_api_cache()
    start_periodic_cache_save_timer()
    write_log(f"Add-on '{ADDON_NAME}' v{ADDON_VERSION} loaded successfully.")

def on_profile_closing():
    """Clean up when profile is closing."""
    save_api_cache()
    stop_periodic_cache_save_timer()
    write_log(f"Add-on '{ADDON_NAME}' cleanup completed.")

# Register hooks
gui_hooks.profile_did_open.append(setup_menu)
gui_hooks.profile_did_open.append(on_profile_opened)
gui_hooks.profile_will_close.append(on_profile_closing)
