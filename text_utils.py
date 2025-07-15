# -*- coding: utf-8 -*-
"""
Text processing utilities for Japanese character recognition and handling.
"""

import re

# Regular expressions for Japanese character types
KANJI_REGEX = re.compile(r'[一-龯𠀀-𪛟]')
HIRAGANA_REGEX = re.compile(r'[\u3040-\u309Fー]')
KATAKANA_REGEX = re.compile(r'[\u30A0-\u30FFー]')

def is_hiragana(char):
    """Check if a character is hiragana."""
    return bool(HIRAGANA_REGEX.fullmatch(char))

def is_katakana(char):
    """Check if a character is katakana."""
    return bool(KATAKANA_REGEX.fullmatch(char))

def is_kanji(char):
    """Check if a character is kanji."""
    return bool(KANJI_REGEX.fullmatch(char))

def is_japanese_char(char):
    """Check if a character is Japanese (hiragana, katakana, or kanji)."""
    return is_hiragana(char) or is_katakana(char) or is_kanji(char)

def extract_unique_japanese_chars(text):
    """Extract unique Japanese characters from text, preserving order of first appearance."""
    return sorted(set(c for c in text if is_japanese_char(c) and not c.isspace()), 
                 key=text.find)

def categorize_characters(text):
    """Categorize characters in text by type."""
    unique_chars = extract_unique_japanese_chars(text)
    
    categories = {
        'hiragana': [],
        'katakana': [],
        'kanji': []
    }
    
    for char in unique_chars:
        if is_hiragana(char):
            categories['hiragana'].append(char)
        elif is_katakana(char):
            categories['katakana'].append(char)
        elif is_kanji(char):
            categories['kanji'].append(char)
    
    return categories

def clean_text(text):
    """Clean text by removing extra whitespace and normalizing."""
    if not text:
        return ""
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text.strip())
    
    return text

def has_japanese_content(text):
    """Check if text contains any Japanese characters."""
    return any(is_japanese_char(char) for char in text)

def get_character_info(char):
    """Get basic information about a character."""
    info = {
        'character': char,
        'is_hiragana': is_hiragana(char),
        'is_katakana': is_katakana(char),
        'is_kanji': is_kanji(char),
        'is_japanese': is_japanese_char(char),
        'unicode_code': ord(char),
        'unicode_name': f"U+{ord(char):04X}"
    }
    
    if info['is_hiragana']:
        info['type'] = 'hiragana'
    elif info['is_katakana']:
        info['type'] = 'katakana'
    elif info['is_kanji']:
        info['type'] = 'kanji'
    else:
        info['type'] = 'other'
    
    return info
