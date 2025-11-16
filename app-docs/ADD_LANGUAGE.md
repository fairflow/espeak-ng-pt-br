# Adding a New Language to Miolingo

This guide documents the complete workflow for adding a new language to the Miolingo pronunciation trainer.

## Prerequisites

- **Environment**: Activate venv before running any Python scripts
  ```bash
  source venv/bin/activate
  ```

- **Required tools**:
  - `espeak` command (NOT `espeak-ng`) for IPA generation
  - Python 3.8+ with libraries: `deep_translator`, `streamlit`, etc.
  - Git for version control

- **Source material**: French phrasebook as reference
  - Located in `language_materials/fr/`
  - Contains `phrasebook_complete.json` and `phrasebook-topics/*.txt`

## Supported Languages

Currently supported language codes:
- `fr` - French (fr-fr voice)
- `pt` - Portuguese (pt-br voice)
- `es` - Spanish (es voice)
- `it` - Italian (it voice)
- `de` - German (de voice)
- `nl` - Dutch (nl voice)

## Complete Workflow

### Step 1: Create Base Directory Structure

```bash
cd language_materials
mkdir -p <lang_code>/phrasebook-topics
```

Example: `mkdir -p es/phrasebook-topics`

### Step 2: Create phrasebook_complete.json

Create `language_materials/<lang_code>/phrasebook_complete.json` based on French version:

```json
{
  "metadata": {
    "source": "Translated from French phrasebook using AI assistance",
    "organization": "by situation/context",
    "levels": {
      "A": "Beginner - basic greetings, simple questions",
      "B": "Elementary - common situations, basic conversations",
      "C": "Intermediate - complex situations, nuanced expressions",
      "D": "Advanced - idiomatic, literary, formal"
    }
  },
  "phrases": [
    {
      "<language_key>": "Hello",
      "situation": "greetings",
      "level": "A",
      "id": 1,
      "english": "Hello",
      "ipa": ""
    }
  ]
}
```

**Language key mapping**:
- French: `"french"`
- Portuguese: `"portuguese"`
- Spanish: `"spanish"`
- Italian: `"italian"`
- German: `"german"`
- Dutch: `"dutch"`

**Important**: Translate ALL 103 French phrases from `language_materials/fr/phrasebook_complete.json`

### Step 3: Translate Phrases

Translate all phrases from French to target language:
1. Keep the same `situation`, `level`, and `id` fields
2. Translate the language-specific field (e.g., `"french"` → `"spanish"`)
3. Keep `english` translations as-is initially (crosscheck later)
4. Leave `ipa` field empty (will be generated in next step)

### Step 4: Generate IPA Transcriptions

**Important**: Use `espeak` command, not `espeak-ng`

```bash
# Activate venv first!
source venv/bin/activate

# Generate IPA for target language
python3 generate_phrasebook_ipa.py <lang_code>
```

Example:
```bash
python3 generate_phrasebook_ipa.py es
```

This script will:
- Read `phrasebook_complete.json`
- Generate IPA for each phrase using eSpeak
- Update the `ipa` field in the JSON
- Save the updated file

**Expected output**: "✅ Complete! 103/103 phrases processed"

### Step 5: Split into Topic Files

```bash
# Still in venv
python3 split_phrasebook.py <lang_code>
```

Example:
```bash
python3 split_phrasebook.py es
```

This creates 12 topic files in `language_materials/<lang_code>/phrasebook-topics/`:
- `01-greetings.txt`
- `02-farewells.txt`
- `03-courtesy-basics.txt`
- `04-introductions.txt`
- `05-asking-for-help.txt`
- `06-directions.txt`
- `07-shopping.txt`
- `08-restaurant.txt`
- `09-conversation.txt`
- `10-feelings-emotions.txt`
- `11-exclamations.txt`
- `basics.txt`

**Format**: `<language> | english | [ipa]`

### Step 6: Update Language Configuration

Add language to `split_phrasebook.py` and `generate_phrasebook_ipa.py`:

```python
LANGUAGES = {
    'fr': {'name': 'French', 'key': 'french', 'voice': 'fr-fr'},
    'pt': {'name': 'Portuguese', 'key': 'portuguese', 'voice': 'pt-br'},
    'es': {'name': 'Spanish', 'key': 'spanish', 'voice': 'es'},
    'it': {'name': 'Italian', 'key': 'italian', 'voice': 'it'},
    'de': {'name': 'German', 'key': 'german', 'voice': 'de'},
    'nl': {'name': 'Dutch', 'key': 'dutch', 'voice': 'nl'},
    # Add new language here
}
```

### Step 7: Test Integration

Test that the app recognizes the new language:

```bash
python3 -c "
from app_language_materials import get_available_languages, get_language_structure

# Check languages
langs = get_available_languages()
print(f'Available: {langs}')

# Check structure
if '<lang_code>' in langs:
    structure = get_language_structure('<lang_code>')
    print(f'Categories: {list(structure.keys())}')
    
    if 'phrasebook-topics' in structure:
        print(f'✓ Phrasebook found with {len(structure[\"phrasebook-topics\"])} files')
"
```

### Step 8: Test in Application

1. Run the app: `streamlit run app.py`
2. Select the new language from the dropdown
3. Check that "💬 Phrasebook by Topic" category appears
4. Load a few topic files to verify:
   - IPA transcriptions display correctly
   - English translations appear
   - Audio playback works

### Step 9: Commit to Git

```bash
# Add all new files
git add language_materials/<lang_code>/

# Commit with descriptive message
git commit -m "Add <Language> phrasebook with 103 phrases (12 topics)

- Translated all 103 French phrases to <Language>
- Generated IPA transcriptions using eSpeak <voice>
- Created 12 topic-based phrasebook files
- Files: phrasebook_complete.json and phrasebook-topics/*.txt

TODO: Crosscheck English translations"

# Tag if this is a version release
git tag -a v1.X.Y -m "v1.X.Y: Add <Language> support"

# Push to remote
git push myfork main --tags
```

## Troubleshooting

### IPA generation fails
- **Problem**: "espeak command not found"
- **Solution**: Install espeak (not espeak-ng): `brew install espeak` (macOS)

### Missing translations
- **Problem**: Phrases show "[translation needed]"
- **Solution**: Manually translate in `phrasebook_complete.json`, then re-run split script

### Wrong voice
- **Problem**: IPA sounds incorrect
- **Solution**: Check voice code in `generate_phrasebook_ipa.py` LANGUAGES dict
- **Available voices**: Run `espeak --voices` to list all

### Topic files not appearing
- **Problem**: Category doesn't show in app
- **Solution**: Check directory structure matches: `language_materials/<lang_code>/phrasebook-topics/*.txt`

### Python import errors
- **Problem**: "No module named 'deep_translator'"
- **Solution**: Activate venv and install dependencies: `pip install -r requirements.txt`

## Required Libraries

If adding new functionality, document library requirements:

```bash
# For translation
pip install deep-translator

# For TTS
pip install gtts google-cloud-texttospeech

# For audio processing
pip install soundfile pydub

# For speech recognition
pip install openai-whisper
```

## Future Tasks

After adding a language:
- [ ] Crosscheck English translations for accuracy
- [ ] Native speaker review of target language phrases
- [ ] Add more advanced phrases (levels C and D)
- [ ] Create word lists from phrases (using `populate_language_materials.py`)
- [ ] Add language-specific pronunciation tips

## Summary Checklist

- [ ] Create directory: `language_materials/<lang_code>/phrasebook-topics/`
- [ ] Create `phrasebook_complete.json` with 103 translated phrases
- [ ] Run `generate_phrasebook_ipa.py <lang_code>` (in venv, using espeak)
- [ ] Run `split_phrasebook.py <lang_code>` to create topic files
- [ ] Test in Python: verify language appears and has phrasebook-topics
- [ ] Test in app: verify category appears and phrases load correctly
- [ ] Commit to Git with descriptive message
- [ ] Tag version if appropriate
- [ ] Push to GitHub

---

**Version**: 1.5.1  
**Last Updated**: 2025-11-16  
**Maintainer**: Matthew & Contributors
