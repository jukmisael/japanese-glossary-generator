# -*- coding: utf-8 -*-
"""
HTML templates for glossary generation.
"""

def get_glossary_templates():
    """Get all HTML templates for glossary generation."""
    return {
        # Kana entry template
        'kana_entry': '<li><span>{kana}</span>: <span>{romaji}</span></li>',
        
        # Kanji entry template
        'kanji_entry': '''<table>
<tr>
<th>Kanji</th>
<td>{kanji}</td>
</tr>
<tr>
<th>Readings</th>
<td>
<ul>
{readings_html}
</ul>
</td>
</tr>
<tr>
<th>Meanings</th>
<td>{meanings_html}</td>
</tr>
</table>''',
        
        # Kanji reading templates
        'kanji_reading': '<li><strong>{type}:</strong> {reading} <span>({romaji})</span></li>',
        'kanji_reading_no_romaji': '<li><strong>{type}:</strong> {reading}</li>',
        
        # Kanji meanings template
        'kanji_meanings': '{meanings}',
        
        # Section templates
        'hiragana_section': '<h3>Hiragana</h3><ul>{entries}</ul>',
        'katakana_section': '<h3>Katakana</h3><ul>{entries}</ul>',
        'kanji_section': '<h3>Kanji</h3>{entries}',
    }

def get_custom_templates():
    """Get customizable templates that users can modify."""
    return {
        'kana_entry': {
            'default': '<li><span>{kana}</span>: <span>{romaji}</span></li>',
            'description': 'Template for individual kana entries. Variables: {kana}, {romaji}',
            'example': '<li><span>あ</span>: <span>a</span></li>'
        },
        
        'kanji_entry': {
            'default': '''<table>
<tr>
<th>Kanji</th>
<td>{kanji}</td>
</tr>
<tr>
<th>Readings</th>
<td>
<ul>
{readings_html}
</ul>
</td>
</tr>
<tr>
<th>Meanings</th>
<td>{meanings_html}</td>
</tr>
</table>''',
            'description': 'Template for kanji entries. Variables: {kanji}, {readings_html}, {meanings_html}',
            'example': 'Full table with kanji, readings, and meanings'
        },
        
        'kanji_reading': {
            'default': '<li><strong>{type}:</strong> {reading} <span>({romaji})</span></li>',
            'description': 'Template for kanji readings with romaji. Variables: {type}, {reading}, {romaji}',
            'example': '<li><strong>On:</strong> じん <span>(jin)</span></li>'
        },
        
        'section_headers': {
            'hiragana': 'Hiragana',
            'katakana': 'Katakana',
            'kanji': 'Kanji'
        }
    }

def validate_template(template_string, required_vars):
    """Validate that a template string contains all required variables."""
    try:
        # Test format with dummy data
        dummy_data = {var: f"test_{var}" for var in required_vars}
        template_string.format(**dummy_data)
        return True, "Template is valid"
    except KeyError as e:
        return False, f"Missing required variable: {e}"
    except Exception as e:
        return False, f"Template error: {e}"

def get_template_variables():
    """Get information about available template variables."""
    return {
        'kana_entry': ['kana', 'romaji'],
        'kanji_entry': ['kanji', 'readings_html', 'meanings_html'],
        'kanji_reading': ['type', 'reading', 'romaji'],
        'kanji_reading_no_romaji': ['type', 'reading'],
        'kanji_meanings': ['meanings'],
        'hiragana_section': ['entries'],
        'katakana_section': ['entries'],
        'kanji_section': ['entries']
    }
