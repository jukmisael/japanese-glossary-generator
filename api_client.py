# -*- coding: utf-8 -*-
"""
API client for external Japanese language services.
"""

import time
import requests
from .config import config
from .cache import global_api_cache
from .logger import write_log
from .stats import global_stats

def _call_romaji2kana_api_direct(endpoint, text):
    """Call the Romaji2Kana API with caching support."""
    cache_key = f"romaji2kana_{endpoint}_{text}"

    if config['cache']['cache_enabled'] and cache_key in global_api_cache:
        global_stats["cache_hits"] += 1
        return global_api_cache[cache_key]

    global_stats["api_calls"] += 1
    result = _call_romaji2kana_api_no_cache(endpoint, text)
    
    if result is not None and config['cache']['cache_enabled']:
        global_api_cache[cache_key] = result
    
    return result

def _call_romaji2kana_api_no_cache(endpoint, text):
    """Call the Romaji2Kana API without caching."""
    base_url = "https://api.romaji2kana.com"
    url = f"{base_url}{endpoint}"
    params = {"q": text}
    
    try:
        # Apply API call delay if configured
        if config['performance']['pause_per_api_call_ms'] > 0:
            time.sleep(config['performance']['pause_per_api_call_ms'] / 1000.0)
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        result = response.json().get("a")
        return result
    except Exception as e:
        write_log(f"Error calling Romaji2Kana API for '{text}': {e}")
    
    return None

def get_kanji_info(kanji_char):
    """Get information about a kanji character with caching support."""
    cache_key = f"kanji_{kanji_char}"

    if config['cache']['cache_enabled'] and cache_key in global_api_cache:
        global_stats["cache_hits"] += 1
        return global_api_cache[cache_key]

    global_stats["api_calls"] += 1
    result = _get_kanji_info_no_cache(kanji_char)
    
    if result is not None and config['cache']['cache_enabled']:
        global_api_cache[cache_key] = result
    
    return result

def _get_kanji_info_no_cache(kanji_char):
    """Get kanji information from KanjiAPI without caching."""
    base_url = "https://kanjiapi.dev/v1"
    url = f"{base_url}/kanji/{kanji_char}"
    
    try:
        # Apply API call delay if configured
        if config['performance']['pause_per_api_call_ms'] > 0:
            time.sleep(config['performance']['pause_per_api_call_ms'] / 1000.0)
        
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        result = response.json()
        return result
    except Exception as e:
        write_log(f"Error calling KanjiAPI for '{kanji_char}': {e}")
    
    return None

def get_romaji_for_text(text):
    """Get romaji reading for Japanese text."""
    return _call_romaji2kana_api_direct("/v1/to/romaji", text)

def get_hiragana_for_text(text):
    """Get hiragana reading for Japanese text."""
    return _call_romaji2kana_api_direct("/v1/to/hiragana", text)

def get_katakana_for_text(text):
    """Get katakana reading for Japanese text."""
    return _call_romaji2kana_api_direct("/v1/to/katakana", text)
