# Japanese Glossary Generator

An Anki add-on that automatically generates comprehensive glossaries for Japanese text with hiragana, katakana, and kanji information.

## Features

- **Automatic Glossary Generation**: Processes Japanese text and creates detailed glossaries
- **Multi-Character Support**: Handles hiragana, katakana, and kanji characters
- **Comprehensive Information**: Provides readings, romaji, and meanings for each character
- **Batch Processing**: Process multiple notes efficiently with customizable performance settings
- **API Caching**: Intelligent caching system to improve performance and reduce API calls
- **Customizable Templates**: Flexible HTML templates for glossary formatting
- **Progress Tracking**: Real-time progress monitoring with detailed statistics

## Installation

1. Download the add-on from AnkiWeb or install manually
2. Restart Anki
3. The add-on will appear in the Tools menu as "Japanese Glossary Generator"

## Usage

### Basic Usage

1. Go to **Tools → Japanese Glossary Generator → Generate Glossary in Batch...**
2. Select your deck and note type
3. Choose the source field containing Japanese text
4. Select or create a target field for the glossary
5. Click OK to start processing

### Settings

Access settings via **Tools → Japanese Glossary Generator → Settings...**

#### General Settings
- **Include Hiragana**: Include hiragana characters in glossary
- **Include Katakana**: Include katakana characters in glossary
- **Include Kanji**: Include kanji characters in glossary
- **Include Romaji**: Add romaji readings for characters
- **Include Meanings**: Add English meanings for kanji
- **Ignore Existing**: Skip notes that already have glossary content
- **Force Overwrite**: Overwrite existing glossary content

#### Performance Settings
- **Parallel Workers**: Number of notes processed simultaneously per batch
- **API Workers**: Number of API calls per note processed simultaneously
- **Batch Size**: Number of notes processed in each batch
- **Pause Between Batches**: Delay between batches (in milliseconds)
- **Pause per API Call**: Delay between individual API calls (in milliseconds)

#### Cache Settings
- **Enable Cache**: Use local caching for API responses
- **Maximum Cache Size**: Limit for cache file size (in MB)
- **Save Interval**: How often to save cache to disk (in minutes)

## API Services

This add-on uses the following external APIs:

- **Romaji2Kana API** (https://api.romaji2kana.com): For character reading conversions
- **KanjiAPI** (https://kanjiapi.dev): For kanji information and meanings

## File Structure

```
japanese_glossary_generator/
├── __init__.py              # Main entry point
├── config.py               # Configuration management
├── logger.py               # Logging utilities
├── cache.py                # API cache management
├── api_client.py           # API communication
├── stats.py                # Statistics tracking
├── text_utils.py           # Text processing utilities
├── glossary_generator.py   # Core glossary generation
├── templates.py            # HTML templates
├── processor.py            # Main processing logic
├── dialogs.py              # UI dialogs
├── manifest.json           # Add-on manifest
├── meta.json              # Add-on metadata
└── README.md              # This file
```

## Configuration Files

The add-on creates several files in its directory:

- `config.json`: User settings and configuration
- `api_cache.json`: Cached API responses
- `japanese_glossary_log.txt`: Activity log file

## Example Output

The generated glossary includes sections for each character type:

### Hiragana
- あ: a
- い: i
- う: u

### Katakana
- ア: a
- イ: i
- ウ: u

### Kanji
| Kanji | 人 |
|-------|-----|
| **Readings** | **On:** ジン (jin), ニン (nin)<br>**Kun:** ひと (hito) |
| **Meanings** | person, human being |

## Troubleshooting

### Common Issues

1. **No glossaries generated**: Check that the source field contains Japanese text
2. **API errors**: Verify internet connection and check the log file
3. **Performance issues**: Adjust worker counts and batch sizes in settings
4. **Cache issues**: Clear cache in settings if experiencing problems

### Log File

View the log file via **Tools → Japanese Glossary Generator → About... → View Log File** to diagnose issues.

## Performance Tips

- Start with smaller batch sizes and increase gradually
- Use caching to reduce API calls on repeated processing
- Adjust worker counts based on your system's capabilities
- Monitor the log file for any API rate limiting issues

## Support

For issues, feature requests, or questions:

1. Check the log file for error details
2. Try adjusting performance settings
3. Clear the cache if experiencing persistent issues
4. Contact the add-on author with specific error messages

## License

This add-on is provided as-is. See the license file for full terms.

## Changelog

### Version 2.0.0
- Complete rewrite with modular architecture
- Improved error handling and logging
- Enhanced caching system
- Better progress tracking
- Configurable templates
- Multiple API service support

### Version 1.x
- Initial implementation
- Basic glossary generation
- Simple UI
