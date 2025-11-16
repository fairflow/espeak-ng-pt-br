# Quick Reference: Automation Scripts

## Script Overview

### 1. generate_phrasebook_ipa.py
Generate IPA transcriptions for any supported language.

```bash
python3 generate_phrasebook_ipa.py <lang_code>
```

**Supported languages**: `fr`, `pt`, `es`, `it`, `de`

**Requirements**:

- `espeak` command (not `espeak-ng`)
- Run in venv: `source venv/bin/activate`
- Input: `language_materials/<lang>/phrasebook_complete.json`
- Output: Updates IPA field in same JSON file

**Example**:

```bash
source venv/bin/activate
python3 generate_phrasebook_ipa.py pt
```

### 2. split_phrasebook.py

Split phrasebook JSON into topic-based text files.

```bash
python3 split_phrasebook.py <lang_code>
```

**Supported languages**: `fr`, `pt`, `es`, `it`, `de`

**Input**: `language_materials/<lang>/phrasebook_complete.json`  
**Output**: `language_materials/<lang>/phrasebook-topics/*.txt` (12 files)

**Example**:

```bash
python3 split_phrasebook.py fr
```

### 3. update_version.py

Update version numbers across all project files.

```bash
./update_version.py <version>
```

**Updates**:

- `__version__` in `app.py` and `miolingo-admin.py`
- `Version:` in all markdown docs
- `Date:` to current date

**Example**:

```bash
./update_version.py 1.6.0
git diff                      # Review changes
git add -A
git commit -m "v1.6.0: ..."
git tag -a v1.6.0 -m "..."
git push myfork main --tags
```

## Common Workflows

### Adding a New Language

```bash
# 1. Create directory
mkdir -p language_materials/<lang>/phrasebook-topics

# 2. Create and populate phrasebook_complete.json
# (Translate 103 phrases from French, keep same structure)

# 3. Generate IPA
source venv/bin/activate
python3 generate_phrasebook_ipa.py <lang>

# 4. Split into topic files
python3 split_phrasebook.py <lang>

# 5. Test in app
python3 -c "from app_language_materials import get_language_structure; print(get_language_structure('<lang>'))"

# 6. Commit
git add language_materials/<lang>/
git commit -m "Add <Language> phrasebook with 103 phrases"
```

See `app-docs/ADD_LANGUAGE.md` for full details.

### Releasing a New Version

```bash
# 1. Update version numbers
./update_version.py 1.6.0

# 2. Review and commit
git diff
git add -A
git commit -m "v1.6.0: Brief description

- Change 1
- Change 2
- Change 3"

# 3. Tag and push
git tag -a v1.6.0 -m "v1.6.0: Brief description"
git push myfork main --tags
```

See `app-docs/VERSION_UPDATE.md` for full details.

## Language Configuration

All scripts use centralized language configuration:

```python
LANGUAGES = {
    'fr': {'name': 'French', 'key': 'french', 'voice': 'fr-fr'},
    'pt': {'name': 'Portuguese', 'key': 'portuguese', 'voice': 'pt-br'},
    'es': {'name': 'Spanish', 'key': 'spanish', 'voice': 'es'},
    'it': {'name': 'Italian', 'key': 'italian', 'voice': 'it'},
    'de': {'name': 'German', 'key': 'german', 'voice': 'de'},
}
```

To add a new language:

1. Add entry to `LANGUAGES` dict in both scripts
2. Follow "Adding a New Language" workflow above

## Troubleshooting

### espeak not found

```bash
brew install espeak   # macOS
```

### Module not found

```bash
source venv/bin/activate
pip install -r requirements.txt
```

### Phrasebook file not found

Ensure `phrasebook_complete.json` exists in `language_materials/<lang>/`

### Git push rejected

```bash
git pull myfork main
git push myfork main --tags
```

## File Structure

```
espeak-ng/
├── split_phrasebook.py              # Multi-lingual splitter
├── generate_phrasebook_ipa.py       # IPA generator
├── update_version.py                # Version updater
├── app-docs/
│   ├── ADD_LANGUAGE.md              # Language addition guide
│   └── VERSION_UPDATE.md            # Version management guide
└── language_materials/
    ├── fr/
    │   ├── phrasebook_complete.json # Master JSON
    │   └── phrasebook-topics/       # 12 topic files
    └── pt/
        ├── phrasebook_complete.json
        └── phrasebook-topics/
```

## Documentation

- **Full language guide**: `app-docs/ADD_LANGUAGE.md`
- **Version workflow**: `app-docs/VERSION_UPDATE.md`
- **User guide**: `app-docs/USER_GUIDE.md`
- **Developer guide**: `app-docs/DEVELOPER_GUIDE.md`

---

**Version**: 1.5.1  
**Last Updated**: 2025-11-16  
**Maintainer**: Matthew & Contributors
