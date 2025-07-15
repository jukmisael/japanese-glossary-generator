# -*- coding: utf-8 -*-
"""
Core glossary generation functionality.
"""

from concurrent.futures import ThreadPoolExecutor, as_completed
from .config import config
from .api_client import get_romaji_for_text, get_kanji_info
from .text_utils import extract_unique_japanese_chars, is_hiragana, is_katakana, is_kanji
from .templates import get_glossary_templates

def generate_glossary_data(text):
    """Generate glossary HTML for the given Japanese text."""
    cfg_gen = config['general']
    templates = get_glossary_templates()
    
    # Extract unique characters
    unique_chars = extract_unique_japanese_chars(text)
    
    # Storage for entries
    hiragana_entries = []
    katakana_entries = []
    kanji_entries = []
    
    # Process characters with threading
    with ThreadPoolExecutor(max_workers=config['performance']['api_call_workers']) as executor:
        api_results = {}
        
        # Submit kana romaji conversion tasks
        kana_futures = {}
        if cfg_gen['include_hiragana'] or cfg_gen['include_katakana']:
            for char in unique_chars:
                if is_hiragana(char) or is_katakana(char):
                    future = executor.submit(get_romaji_for_text, char)
                    kana_futures[future] = char
        
        # Submit kanji info tasks
        kanji_futures = {}
        if cfg_gen['include_kanji']:
            for char in unique_chars:
                if is_kanji(char):
                    future = executor.submit(get_kanji_info, char)
                    kanji_futures[future] = char
        
        # Collect kana results
        for future in as_completed(kana_futures):
            char = kana_futures[future]
            api_results[char] = {"type": "kana", "romaji": future.result()}
        
        # Collect kanji results and submit reading conversion tasks
        reading_futures = {}
        for future in as_completed(kanji_futures):
            char = kanji_futures[future]
            kanji_info = future.result()
            api_results[char] = {"type": "kanji", "info": kanji_info}
            
            # Convert kanji readings to romaji if needed
            if kanji_info and cfg_gen['include_romaji']:
                for reading_type, readings in [("Kun", kanji_info.get("kun_readings", [])), 
                                              ("On", kanji_info.get("on_readings", []))]:
                    for reading in readings:
                        future = executor.submit(get_romaji_for_text, reading)
                        reading_futures[future] = (char, reading, reading_type)
        
        # Collect reading results
        reading_results = {}
        for future in as_completed(reading_futures):
            kanji_char, reading, reading_type = reading_futures[future]
            romaji = future.result()
            
            if kanji_char not in reading_results:
                reading_results[kanji_char] = []
            
            reading_results[kanji_char].append({
                "reading": reading,
                "type": reading_type,
                "romaji": romaji
            })
    
    # Generate entries for each character
    for char in unique_chars:
        result = api_results.get(char)
        if not result:
            continue
        
        if result['type'] == 'kana' and result.get('romaji'):
            _process_kana_character(char, result['romaji'], templates, 
                                  hiragana_entries, katakana_entries)
        elif result['type'] == 'kanji' and result.get('info'):
            _process_kanji_character(char, result['info'], 
                                   reading_results.get(char, []), 
                                   templates, kanji_entries)
    
    # Combine all entries into final HTML
    return _build_final_glossary_html(hiragana_entries, katakana_entries, 
                                     kanji_entries, templates)

def _process_kana_character(char, romaji, templates, hiragana_entries, katakana_entries):
    """Process a kana character and add it to the appropriate entries list."""
    cfg_gen = config['general']
    
    if is_hiragana(char) and cfg_gen['include_hiragana']:
        entry = templates['kana_entry'].format(kana=char, romaji=romaji)
        hiragana_entries.append(entry)
    elif is_katakana(char) and cfg_gen['include_katakana']:
        entry = templates['kana_entry'].format(kana=char, romaji=romaji)
        katakana_entries.append(entry)

def _process_kanji_character(char, kanji_info, reading_results, templates, kanji_entries):
    """Process a kanji character and add it to the entries list."""
    cfg_gen = config['general']
    
    if not kanji_info or 'meanings' not in kanji_info:
        return
    
    # Generate readings HTML
    readings_html = ""
    if reading_results:
        readings_for_char = sorted(reading_results, key=lambda x: (x['type'], x['reading']))
        for reading_data in readings_for_char:
            if reading_data['romaji']:
                readings_html += templates['kanji_reading'].format(**reading_data)
            else:
                readings_html += templates['kanji_reading_no_romaji'].format(**reading_data)
    
    # Generate meanings HTML
    meanings_html = ""
    if cfg_gen['include_kanji_meanings'] and kanji_info.get('meanings'):
        meanings_str = ", ".join(kanji_info['meanings'])
        meanings_html = templates['kanji_meanings'].format(meanings=meanings_str)
    
    # Create kanji entry
    entry = templates['kanji_entry'].format(
        kanji=char,
        readings_html=readings_html,
        meanings_html=meanings_html
    )
    kanji_entries.append(entry)

def _build_final_glossary_html(hiragana_entries, katakana_entries, kanji_entries, templates):
    """Build the final glossary HTML from all entries."""
    cfg_gen = config['general']
    final_glossary_html = []
    
    # Add hiragana section
    if hiragana_entries and cfg_gen['include_hiragana']:
        section = templates['hiragana_section'].format(
            entries="".join(hiragana_entries)
        )
        final_glossary_html.append(section)
    
    # Add katakana section
    if katakana_entries and cfg_gen['include_katakana']:
        section = templates['katakana_section'].format(
            entries="".join(katakana_entries)
        )
        final_glossary_html.append(section)
    
    # Add kanji section
    if kanji_entries and cfg_gen['include_kanji']:
        section = templates['kanji_section'].format(
            entries="".join(kanji_entries)
        )
        final_glossary_html.append(section)
    
    return "".join(final_glossary_html)