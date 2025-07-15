# -*- coding: utf-8 -*-
"""
UI dialogs for Japanese Glossary Generator.
"""

from aqt import mw
from aqt.qt import (QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QPushButton, 
                    QComboBox, QLabel, QLineEdit, QTabWidget, QCheckBox, QSpinBox, 
                    QTextEdit, QDialogButtonBox, Qt, QTimer, QProgressDialog, QWidget, QFont)
from aqt.utils import showInfo, askUser

from .config import config, save_config, load_config
from .stats import global_stats
from .cache import start_periodic_cache_save_timer, clear_api_cache, get_cache_stats
from .logger import get_log_content, clear_log

class BatchGlossaryDialog(QDialog):
    """Main dialog for batch glossary generation."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Generate Glossary in Batch")
        self.setMinimumWidth(400)
        self.data = None
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        form = QFormLayout()
        
        # Deck selection
        self.deck_combo = QComboBox()
        self.deck_combo.addItems(sorted(mw.col.decks.all_names()))
        
        # Note type selection
        self.note_type_combo = QComboBox()
        self.note_type_combo.addItems(sorted(mw.col.models.all_names()))
        
        # Source field selection
        self.source_field_combo = QComboBox()
        
        # Target field selection
        self.target_field_combo = QComboBox()
        self.custom_target_field_edit = QLineEdit()
        self.custom_target_field_edit.hide()
        
        form.addRow("1. Deck:", self.deck_combo)
        form.addRow("2. Note Type:", self.note_type_combo)
        form.addRow("3. Source Field:", self.source_field_combo)
        form.addRow("4. Target Field:", self.target_field_combo)
        form.addRow("", self.custom_target_field_edit)
        
        layout.addLayout(form)
        
        # Connect signals
        self.note_type_combo.currentIndexChanged.connect(self.update_fields)
        self.target_field_combo.currentIndexChanged.connect(self.toggle_custom_target_field_input)
        
        # Initialize fields
        self.update_fields()
        
        # Buttons
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | 
                                 QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
    
    def update_fields(self):
        """Update field lists when note type changes."""
        model = mw.col.models.by_name(self.note_type_combo.currentText())
        if not model:
            return
            
        field_names = [f['name'] for f in model['flds']]
        
        # Update source field combo
        self.source_field_combo.clear()
        self.source_field_combo.addItems(field_names)
        
        # Update target field combo
        self.target_field_combo.clear()
        self.target_field_combo.addItems(field_names)
        self.target_field_combo.addItem("--Other--")
        
        # Try to select "Glossary" field if it exists
        glossary_index = self.target_field_combo.findText("Glossary")
        if glossary_index != -1:
            self.target_field_combo.setCurrentIndex(glossary_index)
        else:
            self.target_field_combo.setCurrentIndex(self.target_field_combo.findText("--Other--"))
        
        self.toggle_custom_target_field_input()
    
    def toggle_custom_target_field_input(self):
        """Show/hide custom target field input."""
        if self.target_field_combo.currentText() == "--Other--":
            self.custom_target_field_edit.show()
            self.custom_target_field_edit.setEnabled(True)
            self.custom_target_field_edit.setFocus()
        else:
            self.custom_target_field_edit.hide()
            self.custom_target_field_edit.setEnabled(False)
    
    def accept(self):
        """Validate and accept dialog."""
        # Get target field
        selected_target_field = self.target_field_combo.currentText()
        if selected_target_field == "--Other--":
            target_field = self.custom_target_field_edit.text().strip()
        else:
            target_field = selected_target_field
        
        # Validate all fields
        self.data = {
            "deck_name": self.deck_combo.currentText(),
            "note_type_name": self.note_type_combo.currentText(),
            "source_field": self.source_field_combo.currentText(),
            "target_field": target_field
        }
        
        if not all(self.data.values()):
            showInfo("All fields must be filled, including the target field name if 'Other' is selected.")
            return
        
        super().accept()

class SettingsDialog(QDialog):
    """Settings configuration dialog."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings - Japanese Glossary Generator")
        self.setMinimumWidth(500)
        self.config_data = load_config()
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        tabs = QTabWidget()
        layout.addWidget(tabs)
        
        # General settings tab
        self.create_general_tab(tabs)
        
        # Performance settings tab
        self.create_performance_tab(tabs)
        
        # Cache settings tab
        self.create_cache_tab(tabs)
        
        # Load current settings
        self.load_settings()
        
        # Buttons
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | 
                                 QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
    
    def create_general_tab(self, tabs):
        """Create the general settings tab."""
        general_tab = QWidget()
        form = QFormLayout(general_tab)
        
        self.cb_hira = QCheckBox("Include Hiragana")
        self.cb_kata = QCheckBox("Include Katakana")
        self.cb_kanji = QCheckBox("Include Kanji")
        self.cb_romaji = QCheckBox("Include Romaji for readings")
        self.cb_meanings = QCheckBox("Include Meanings for Kanji")
        self.cb_ignore_existing = QCheckBox("Ignore notes with existing glossary (if field is empty)")
        self.cb_overwrite_existing = QCheckBox("Force overwrite of existing glossary")
        
        form.addRow(self.cb_hira)
        form.addRow(self.cb_kata)
        form.addRow(self.cb_kanji)
        form.addRow(self.cb_romaji)
        form.addRow(self.cb_meanings)
        form.addRow(self.cb_ignore_existing)
        form.addRow(self.cb_overwrite_existing)
        
        tabs.addTab(general_tab, "General")
    
    def create_performance_tab(self, tabs):
        """Create the performance settings tab."""
        perf_tab = QWidget()
        form = QFormLayout(perf_tab)
        
        self.spin_workers = QSpinBox()
        self.spin_workers.setRange(1, 32)
        self.spin_workers.setToolTip("Number of notes processed simultaneously per batch")
        
        self.spin_api_call_workers = QSpinBox()
        self.spin_api_call_workers.setRange(1, 16)
        self.spin_api_call_workers.setToolTip("Number of API calls per note processed simultaneously")
        
        self.spin_batch_size = QSpinBox()
        self.spin_batch_size.setRange(1, 1000)
        self.spin_batch_size.setToolTip("Number of notes processed in each batch")
        
        self.spin_pause = QSpinBox()
        self.spin_pause.setRange(0, 10000)
        self.spin_pause.setSuffix(" ms")
        self.spin_pause.setToolTip("Pause between batches to prevent API overload")
        
        self.spin_pause_api_call = QSpinBox()
        self.spin_pause_api_call.setRange(0, 5000)
        self.spin_pause_api_call.setSuffix(" ms")
        self.spin_pause_api_call.setToolTip("Pause between individual API calls")
        
        form.addRow("Parallel Workers (Notes per Batch):", self.spin_workers)
        form.addRow("API Workers (per Note):", self.spin_api_call_workers)
        form.addRow("Batch Size (Notes):", self.spin_batch_size)
        form.addRow("Pause Between Batches:", self.spin_pause)
        form.addRow("Pause per API Call:", self.spin_pause_api_call)
        
        tabs.addTab(perf_tab, "Performance")
    
    def create_cache_tab(self, tabs):
        """Create the cache settings tab."""
        cache_tab = QWidget()
        layout = QVBoxLayout(cache_tab)
        form = QFormLayout()
        
        self.cb_cache_enabled = QCheckBox("Enable API Cache")
        self.cb_cache_enabled.setToolTip("Cache API responses to improve performance and reduce API calls")
        
        self.spin_cache_max_size = QSpinBox()
        self.spin_cache_max_size.setRange(0, 1000)
        self.spin_cache_max_size.setSuffix(" MB")
        self.spin_cache_max_size.setToolTip("Maximum cache file size (0 = no limit)")
        
        self.spin_cache_save_interval = QSpinBox()
        self.spin_cache_save_interval.setRange(0, 60)
        self.spin_cache_save_interval.setSuffix(" minutes")
        self.spin_cache_save_interval.setToolTip("How often to save cache (0 = only on close)")
        
        form.addRow(self.cb_cache_enabled)
        form.addRow("Maximum Cache Size:", self.spin_cache_max_size)
        form.addRow("Periodic Save Interval:", self.spin_cache_save_interval)
        
        layout.addLayout(form)
        
        # Cache management buttons
        cache_buttons = QHBoxLayout()
        
        clear_cache_btn = QPushButton("Clear Cache")
        clear_cache_btn.clicked.connect(self.clear_cache)
        cache_buttons.addWidget(clear_cache_btn)
        
        # Cache statistics
        self.cache_stats_label = QLabel()
        self.update_cache_stats()
        layout.addWidget(self.cache_stats_label)
        
        cache_buttons.addStretch()
        layout.addLayout(cache_buttons)
        
        tabs.addTab(cache_tab, "Cache")
    
    def update_cache_stats(self):
        """Update cache statistics display."""
        stats = get_cache_stats()
        stats_text = f"Cache Status: {'Enabled' if stats['enabled'] else 'Disabled'}\n"
        stats_text += f"Entries: {stats['entries']}\n"
        stats_text += f"File Size: {stats['file_size_mb']:.2f} MB"
        self.cache_stats_label.setText(stats_text)
    
    def clear_cache(self):
        """Clear the API cache."""
        if askUser("Are you sure you want to clear the API cache? This cannot be undone."):
            clear_api_cache()
            self.update_cache_stats()
            showInfo("Cache cleared successfully.")
    
    def load_settings(self):
        """Load current settings into the UI."""
        # General settings
        self.cb_hira.setChecked(config['general']['include_hiragana'])
        self.cb_kata.setChecked(config['general']['include_katakana'])
        self.cb_kanji.setChecked(config['general']['include_kanji'])
        self.cb_romaji.setChecked(config['general']['include_romaji'])
        self.cb_meanings.setChecked(config['general']['include_kanji_meanings'])
        self.cb_ignore_existing.setChecked(config['general']['ignore_existing_glossary_notes'])
        self.cb_overwrite_existing.setChecked(config['general']['overwrite_existing_glossary_notes'])
        
        # Performance settings
        self.spin_workers.setValue(config['performance']['max_workers'])
        self.spin_api_call_workers.setValue(config['performance']['api_call_workers'])
        self.spin_batch_size.setValue(config['performance']['batch_size'])
        self.spin_pause.setValue(config['performance']['pause_between_batches_ms'])
        self.spin_pause_api_call.setValue(config['performance']['pause_per_api_call_ms'])
        
        # Cache settings
        self.cb_cache_enabled.setChecked(config['cache']['cache_enabled'])
        self.spin_cache_max_size.setValue(config['cache']['cache_max_size_mb'])
        self.spin_cache_save_interval.setValue(config['cache']['cache_save_interval_minutes'])
    
    def accept(self):
        """Save settings and close dialog."""
        # Update config with new values
        config['general']['include_hiragana'] = self.cb_hira.isChecked()
        config['general']['include_katakana'] = self.cb_kata.isChecked()
        config['general']['include_kanji'] = self.cb_kanji.isChecked()
        config['general']['include_romaji'] = self.cb_romaji.isChecked()
        config['general']['include_kanji_meanings'] = self.cb_meanings.isChecked()
        config['general']['ignore_existing_glossary_notes'] = self.cb_ignore_existing.isChecked()
        config['general']['overwrite_existing_glossary_notes'] = self.cb_overwrite_existing.isChecked()
        
        config['performance']['max_workers'] = self.spin_workers.value()
        config['performance']['api_call_workers'] = self.spin_api_call_workers.value()
        config['performance']['batch_size'] = self.spin_batch_size.value()
        config['performance']['pause_between_batches_ms'] = self.spin_pause.value()
        config['performance']['pause_per_api_call_ms'] = self.spin_pause_api_call.value()
        
        config['cache']['cache_enabled'] = self.cb_cache_enabled.isChecked()
        config['cache']['cache_max_size_mb'] = self.spin_cache_max_size.value()
        config['cache']['cache_save_interval_minutes'] = self.spin_cache_save_interval.value()
        
        # Save configuration
        if save_config(config):
            showInfo("Settings saved successfully.")
            start_periodic_cache_save_timer()
        else:
            showInfo("Error saving settings.")
        
        super().accept()

class ProcessingStatsDialog(QDialog):
    """Dialog showing processing statistics and progress."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Glossary Generation Progress")
        self.setMinimumWidth(350)
        self.setWindowModality(Qt.WindowModality.ApplicationModal)
        
        self.timer = QTimer(self)
        self.init_ui()
        self.timer.timeout.connect(self.update_stats_display)
        self.timer.start(500)  # Update every 500ms
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Statistics labels
        self.labels = {}
        stats_order = [
            ("total_notes", "Total Notes:"),
            ("processed_notes", "Notes Processed:"),
            ("updated_notes", "Notes Updated:"),
            ("unchanged_notes", "Notes Unchanged:"),
            ("empty_notes", "Empty Notes:"),
            ("error_notes", "Error Notes:"),
            ("cache_hits", "Cache Hits:"),
            ("api_calls", "API Calls:"),
            ("elapsed_time", "Elapsed Time:"),
            ("eta", "ETA:"),
        ]
        
        for key, text in stats_order:
            h_layout = QHBoxLayout()
            label_name = QLabel(text)
            label_value = QLabel("0")
            label_value.setAlignment(Qt.AlignmentFlag.AlignRight)
            self.labels[key] = label_value
            
            h_layout.addWidget(label_name)
            h_layout.addStretch(1)
            h_layout.addWidget(label_value)
            layout.addLayout(h_layout)
        
        # Progress bar
        self.progress_bar = QProgressDialog("", "Cancel", 0, 100, self)
        self.progress_bar.setWindowModality(Qt.WindowModality.ApplicationModal)
        self.progress_bar.setAutoClose(False)
        self.progress_bar.setAutoReset(False)
        self.progress_bar.setCancelButtonText("Cancel")
        self.progress_bar.canceled.connect(self.cancel_process)
        layout.addWidget(self.progress_bar)
        
        # Cancel button
        self.cancel_button = QPushButton("Cancel Processing")
        self.cancel_button.clicked.connect(self.cancel_process)
        layout.addWidget(self.cancel_button)
        
        self.update_stats_display()
    
    def update_stats_display(self):
        """Update the statistics display."""
        # Update text labels
        self.labels["total_notes"].setText(str(global_stats["total_notes"]))
        self.labels["processed_notes"].setText(str(global_stats["processed_notes"]))
        self.labels["updated_notes"].setText(str(global_stats["updated_notes"]))
        self.labels["unchanged_notes"].setText(str(global_stats["unchanged_notes"]))
        self.labels["empty_notes"].setText(str(global_stats["empty_notes"]))
        self.labels["error_notes"].setText(str(global_stats["error_notes"]))
        self.labels["cache_hits"].setText(str(global_stats["cache_hits"]))
        self.labels["api_calls"].setText(str(global_stats["api_calls"]))
        
        # Format elapsed time
        elapsed_seconds = global_stats["elapsed_time"]
        self.labels["elapsed_time"].setText(f"{int(elapsed_seconds // 60)}m {int(elapsed_seconds % 60)}s")
        
        # ETA
        self.labels["eta"].setText(global_stats["eta"])
        
        # Update progress bar
        if global_stats["total_notes"] > 0:
            progress_percent = (global_stats["processed_notes"] / global_stats["total_notes"]) * 100
            self.progress_bar.setValue(int(progress_percent))
            self.progress_bar.setLabelText(
                f"Processing: {global_stats['processed_notes']}/{global_stats['total_notes']} "
                f"notes ({progress_percent:.2f}%)"
            )
        else:
            self.progress_bar.setValue(0)
            self.progress_bar.setLabelText("Starting...")
        
        # Check if processing is complete
        if (global_stats["processed_notes"] >= global_stats["total_notes"] and 
            global_stats["total_notes"] > 0) or global_stats["is_cancelled"]:
            self.timer.stop()
            self.progress_bar.setCancelButton(None)
            self.cancel_button.setEnabled(False)
            
            if not global_stats["is_cancelled"]:
                self.progress_bar.setLabelText("Processing Complete!")
    
    def cancel_process(self):
        """Cancel the processing."""
        if askUser("Are you sure you want to cancel the processing?"):
            from .stats import cancel_processing
            cancel_processing()
            from .logger import write_log
            write_log("User requested processing cancellation.")
            self.progress_bar.setLabelText("Cancellation requested. Finishing current batch...")
            self.cancel_button.setEnabled(False)
    
    def closeEvent(self, event):
        """Handle dialog close event."""
        if (not global_stats["is_cancelled"] and 
            global_stats["processed_notes"] < global_stats["total_notes"]):
            if askUser("Processing is still in progress. Do you really want to close and cancel?"):
                self.cancel_process()
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()

class AboutDialog(QDialog):
    """About dialog with add-on information."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("About - Japanese Glossary Generator")
        self.setMinimumWidth(500)
        self.setMinimumHeight(400)
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Add-on information
        from . import ADDON_NAME, ADDON_VERSION, ADDON_AUTHOR, ADDON_DESCRIPTION
        
        info_text = f"""
<h2>{ADDON_NAME}</h2>
<p><strong>Version:</strong> {ADDON_VERSION}</p>
<p><strong>Author:</strong> {ADDON_AUTHOR}</p>

<h3>Description</h3>
<p>{ADDON_DESCRIPTION}</p>

<h3>Features</h3>
<ul>
<li>Automatically generates glossaries for Japanese text</li>
<li>Supports Hiragana, Katakana, and Kanji characters</li>
<li>Provides readings and meanings for Kanji</li>
<li>Batch processing with customizable performance settings</li>
<li>API response caching for improved performance</li>
<li>Configurable HTML templates</li>
</ul>

<h3>APIs Used</h3>
<ul>
<li><strong>Romaji2Kana API:</strong> For character reading conversions</li>
<li><strong>KanjiAPI:</strong> For Kanji information and meanings</li>
</ul>

<h3>Support</h3>
<p>For issues, feature requests, or questions, please visit the add-on's page on AnkiWeb 
or contact the author.</p>

<h3>License</h3>
<p>This add-on is provided as-is under the terms specified in the license file.</p>
        """
        
        info_label = QLabel(info_text)
        info_label.setWordWrap(True)
        info_label.setTextFormat(Qt.TextFormat.RichText)
        info_label.setOpenExternalLinks(True)
        
        layout.addWidget(info_label)
        
        # Show log button
        log_button = QPushButton("View Log File")
        log_button.clicked.connect(self.show_log)
        layout.addWidget(log_button)
        
        # Close button
        close_button = QPushButton("Close")
        close_button.clicked.connect(self.accept)
        layout.addWidget(close_button)
    
    def show_log(self):
        """Show the log file content."""
        log_dialog = LogViewDialog(self)
        log_dialog.exec()

class LogViewDialog(QDialog):
    """Dialog for viewing log file content."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Log File Viewer")
        self.setMinimumWidth(600)
        self.setMinimumHeight(400)
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Log text area
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setFont(QFont("Courier", 9))
        layout.addWidget(self.log_text)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        refresh_button = QPushButton("Refresh")
        refresh_button.clicked.connect(self.refresh_log)
        button_layout.addWidget(refresh_button)
        
        clear_button = QPushButton("Clear Log")
        clear_button.clicked.connect(self.clear_log)
        button_layout.addWidget(clear_button)
        
        button_layout.addStretch()
        
        close_button = QPushButton("Close")
        close_button.clicked.connect(self.accept)
        button_layout.addWidget(close_button)
        
        layout.addLayout(button_layout)
        
        # Load initial content
        self.refresh_log()
    
    def refresh_log(self):
        """Refresh the log content."""
        content = get_log_content()
        self.log_text.setPlainText(content)
        
        # Scroll to bottom
        cursor = self.log_text.textCursor()
        cursor.movePosition(cursor.MoveOperation.End)
        self.log_text.setTextCursor(cursor)
    
    def clear_log(self):
        """Clear the log file."""
        if askUser("Are you sure you want to clear the log file? This cannot be undone."):
            clear_log()
            self.refresh_log()
            showInfo("Log file cleared.")