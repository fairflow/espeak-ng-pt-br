#!/bin/bash
# extract_miolingo.sh - Extract miolingo from espeak-ng-pt-br with git history

set -e  # Exit on error

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
TEMP_DIR="/tmp/miolingo-extraction-$$"
TARGET_DIR="$HOME/Software/working/miolingo"
SPLIT_COMMIT="f38c27bf"

echo "================================"
echo "Miolingo Extraction Script"
echo "================================"
echo ""
echo "This will:"
echo "1. Clone current repo to temp location"
echo "2. Extract only miolingo files with git history from $SPLIT_COMMIT onward"
echo "3. Reorganize into new structure"
echo "4. Place in $TARGET_DIR"
echo ""
read -p "Continue? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Aborted."
    exit 1
fi

# Step 1: Clone to temp directory
echo ""
echo "Step 1: Cloning repo to temp location..."
git clone "$SCRIPT_DIR" "$TEMP_DIR"
cd "$TEMP_DIR"

# Step 2: Create list of miolingo files for git-filter-repo
echo ""
echo "Step 2: Creating file list for extraction..."

cat > /tmp/miolingo-paths.txt << 'EOF'
# Core Python files
app.py
miolingo-admin.py
app_mysql.py
app_language_materials.py
api_usage_logger.py
cost_monitor.py
add_ipa_to_scenes.py
analyze_difficulty.py
analyze_difficulty_local.py
apply_translations.py
complete_all_story_translations.py
complete_story_translations.py
complete_story_translations_full.py
extract_french_words.py
extract_phrases.py
extract_story_phrases.py
fill_ipa_tags.py
generate_phrasebook_ipa.py
generate_story_scenes_ipa.py
populate_french_translations.py
practice_app.py
practice_sentences.py
process_story_scenes.py
pronunciation_trainer.py
record_audio.py
split_phrasebook.py
streamlit_app.py
streamlit_app_v2.py
test_audio.py
test_google_cloud_tts.py
test_gtts_simple.py
test_isso.py
translate_all_phrases.py
update_version.py
ccs_test_framework.py
ccs_test_integration.py

# Version management
bump_app.py
bump_admin.py
bump_admin_doc_files.txt
bump_admin_program_files.txt
bump_doc_files.txt
bump_program_files.txt

# eSpeak integration
speak_phonemes.py
ipa_to_espeak.py
configure-macos.sh

# Configuration
requirements.txt
requirements-wav2vec2.txt
runtime.txt
packages.txt
.gitignore
.python-version

# Streamlit
.streamlit/

# Documentation directories
app-docs/
admin-docs/
admin-sources/
articles/

# Language materials
language_materials/

# Testing logs
ccs_test_logs/

# VS Code / GitHub config
.vscode/
.github/

# Documentation files
README.md
APP_CHANGELOG.md
VERSION_WORKFLOW.md
VERSION_CHECKLIST.md
BUMP_GUIDE.md
AUTOMATION_REFERENCE.md
MIOLINGO_DESCRIPTION.md
IMPLEMENTATION_SUMMARY.md
MULTI_USER_IMPLEMENTATION_PLAN.md
PRACTICE_MODE_IMPLEMENTATION.md
LANGUAGE_MATERIALS_INTEGRATION_PLAN.md
JSON_FORMAT_STANDARDIZATION_PROPOSAL.md
PYTHON-SETUP.md
STREAMLIT-FIXES.md
STREAMLIT_CLOUD_DATABASE_ISSUE.md
KRYSTAL_DATABASE_SETUP_GUIDE.md
SECURITY_HARDENING.md
CCS_TESTING_README.md
CCS_USAGE_GUIDE.md
PROJECT_STATS.md
API_COST_TRACKING.md
AUDIO_TRACKING.md
PHRASE_LIST_FORMAT.md
APP-GUIDE.md
pronunciationVowels.md
CHAT_SUMMARY_2025-11-10.md
DOCUMENTATION_SUMMARY.md
NEW-APP-SUMMARY.md
LOCAL-BUILD.md
IPA-SOLUTION.md
AUDIO-NOTES.md
PHONEME-REFERENCE.md
QUICKSTART-SPEECH-RECOGNITION.md
ESPEAK_USAGE.md
SPEECH-RECOGNITION.md
RECOGNITION-TIPS.md
README-PT-BR.md

# Practice/data files
practice_flemish_phrases_A.txt
practice_french_phrases_A.txt
practice_phrases_with_translations.txt
practice_phrases1.txt
practice_phrases2.txt
practice_words.txt
practice_words2.txt
sample_phrases.txt
sample_practice.txt
sample_practice2.txt
sample_practice2_english.txt
extracted_phrases_fr.json
graded_phrases_fr.json
narrative_fr.txt
narrative_generation_prompts.md
phrases_organized_fr.json
phrases_with_translations_fr.json
story_framework_fr.md
scene-13-les-secours-translated.json
scene-14-la-reflexion-de-sophie-translated.json
scene-15-la-decouverte-translated.json
scene-16-la-reunion-translated.json
training_set.txt

# Setup scripts
setup.sh
setup-french-v2.sh

# SQL files
check_active_sessions.sql

# Extraction plan
MIOLINGO_EXTRACTION_PLAN.md
EOF

# Step 3: Run git-filter-repo to extract only these paths
echo ""
echo "Step 3: Running git-filter-repo to extract miolingo files..."
echo "This will take a few minutes..."

# MacPorts installs git-filter-repo in git's libexec dir
# Use as git subcommand: git filter-repo (note the space)
git filter-repo \
    --paths-from-file /tmp/miolingo-paths.txt \
    --force

echo ""
echo "✓ Extraction complete!"

# Step 4: Reorganize into new structure
echo ""
echo "Step 4: Reorganizing into new structure..."

# Create new directory structure
mkdir -p src
mkdir -p scripts
mkdir -p config
mkdir -p docs

# Move Python files to src/
echo "Moving Python files to src/..."
for file in *.py; do
    if [ -f "$file" ]; then
        git mv "$file" src/
    fi
done

# Move scripts
echo "Moving scripts..."
git mv src/bump_app.py scripts/ 2>/dev/null || true
git mv src/bump_admin.py scripts/ 2>/dev/null || true
git mv src/speak_phonemes.py scripts/ 2>/dev/null || true
git mv src/ipa_to_espeak.py scripts/ 2>/dev/null || true
git mv configure-macos.sh scripts/ 2>/dev/null || true
git mv setup.sh scripts/ 2>/dev/null || true
git mv setup-french-v2.sh scripts/ 2>/dev/null || true
mv bump_*.txt scripts/ 2>/dev/null || true

# Move documentation
echo "Moving documentation..."
git mv app-docs docs/ 2>/dev/null || true
git mv admin-docs docs/ 2>/dev/null || true
git mv admin-sources docs/admin-docs/sources 2>/dev/null || true

# Move config files
echo "Moving configuration..."
mv .python-version config/ 2>/dev/null || true
mv check_active_sessions.sql config/ 2>/dev/null || true

# Commit reorganization
echo "Committing reorganization..."
git add -A
git commit -m "Reorganize miolingo into standard structure with src/, docs/, scripts/, config/" || true

# Step 5: Create new files for miolingo
echo ""
echo "Step 5: Creating miolingo-specific files..."

# Create .miolingo.config template
cat > config/.miolingo.config << 'CONFIGEOF'
# Miolingo Configuration
# Copy this to ~/.miolingo.config or ./.miolingo.config and customize

[espeak-ng]
# Path to espeak-ng installation
# Default: tries to find via 'which espeak-ng' or standard locations
# Uncomment and set if you have a custom installation:
# path = /Users/username/Software/working/espeak-ng/local/bin/espeak-ng
# data_path = /Users/username/Software/working/espeak-ng/local/share/espeak-ng-data

[database]
# Database connection (if not using Streamlit secrets)
# For local development, use .streamlit/secrets.toml instead
# host = localhost
# port = 3306
# user = miolingo
# password = (use secrets.toml)
# database = miolingo

[audio]
# Audio settings
# sample_rate = 16000
# channels = 1
CONFIGEOF

# Create configure script
cat > configure << 'CONFEOF'
#!/bin/bash
# Configure script for Miolingo

echo "Configuring Miolingo..."
echo ""

# Check Python version
echo "Checking Python version..."
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo "  Found: Python $PYTHON_VERSION"

REQUIRED_MAJOR=3
REQUIRED_MINOR=8

MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)

if [ "$MAJOR" -lt "$REQUIRED_MAJOR" ] || ([ "$MAJOR" -eq "$REQUIRED_MAJOR" ] && [ "$MINOR" -lt "$REQUIRED_MINOR" ]); then
    echo "  ✗ Error: Python 3.8+ required"
    exit 1
fi
echo "  ✓ OK"

# Check for venv
echo ""
echo "Checking for virtual environment..."
if [ -d "venv" ]; then
    echo "  ✓ Found existing venv/"
else
    echo "  Creating virtual environment..."
    python3 -m venv venv
    echo "  ✓ Created venv/"
fi

# Check for espeak-ng
echo ""
echo "Checking for espeak-ng..."
if which espeak-ng > /dev/null 2>&1; then
    ESPEAK_PATH=$(which espeak-ng)
    ESPEAK_VERSION=$(espeak-ng --version 2>&1 | head -1)
    echo "  ✓ Found: $ESPEAK_PATH"
    echo "    Version: $ESPEAK_VERSION"
else
    echo "  ⚠ Warning: espeak-ng not found in PATH"
    echo "    You can:"
    echo "    1. Install: brew install espeak-ng  OR  port install espeak-ng"
    echo "    2. Build locally in ../espeak-ng/"
    echo "    3. Configure path in config/.miolingo.config"
fi

# Check for ffmpeg (needed for audio)
echo ""
echo "Checking for ffmpeg..."
if which ffmpeg > /dev/null 2>&1; then
    FFMPEG_VERSION=$(ffmpeg -version 2>&1 | head -1 | awk '{print $3}')
    echo "  ✓ Found: ffmpeg $FFMPEG_VERSION"
else
    echo "  ⚠ Warning: ffmpeg not found"
    echo "    Install: brew install ffmpeg  OR  port install ffmpeg"
fi

# Check for portaudio (needed for audio recording)
echo ""
echo "Checking for portaudio..."
if [ -f "/opt/local/lib/libportaudio.dylib" ] || [ -f "/usr/local/lib/libportaudio.dylib" ]; then
    echo "  ✓ Found portaudio"
else
    echo "  ⚠ Warning: portaudio not found"
    echo "    Install: brew install portaudio  OR  port install portaudio"
fi

echo ""
echo "Configuration complete!"
echo ""
echo "Next steps:"
echo "  1. source venv/bin/activate"
echo "  2. make install"
echo "  3. Copy .streamlit/secrets_template.toml to .streamlit/secrets.toml"
echo "  4. Configure your secrets (database, API keys, email)"
echo "  5. make run          # Start the app"
echo "  6. make run-admin    # Start admin dashboard"
echo ""
CONFEOF

chmod +x configure

# Create Makefile
cat > Makefile << 'MAKEEOF'
# Miolingo Makefile

.PHONY: help install install-dev run run-admin test clean

help:
	@echo "Miolingo - Multi-language Pronunciation Trainer"
	@echo ""
	@echo "Available targets:"
	@echo "  make install      - Install dependencies"
	@echo "  make install-dev  - Install with development dependencies"
	@echo "  make run          - Run the main app (port 8501)"
	@echo "  make run-admin    - Run admin dashboard (port 8505)"
	@echo "  make test         - Run tests"
	@echo "  make clean        - Clean temporary files"
	@echo ""
	@echo "First time setup:"
	@echo "  ./configure"
	@echo "  source venv/bin/activate"
	@echo "  make install"
	@echo ""

install:
	pip install --upgrade pip
	pip install -r requirements.txt

install-dev:
	pip install --upgrade pip
	pip install -r requirements.txt
	pip install -r requirements-wav2vec2.txt

run:
	streamlit run src/app.py --server.port 8501

run-admin:
	streamlit run src/miolingo-admin.py --server.port 8505

test:
	python -m pytest tests/ -v

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name ".DS_Store" -delete
	rm -f temp_streamlit_recording.wav
MAKEEOF

# Create streamlit secrets template
mkdir -p .streamlit
cat > .streamlit/secrets_template.toml << 'SECRETEOF'
# Miolingo Secrets Template
# Copy this to .streamlit/secrets.toml and fill in your credentials
# NEVER commit secrets.toml to git!

[database]
host = "your-ssh-tunnel-host-or-direct-host"
port = 3306
user = "your_database_user"
password = "your_database_password"
database = "miolingo"

[database.ssh]
# If using SSH tunnel
enabled = true
host = "your-server.com"
port = 22
user = "your_ssh_user"
# Use SSH key authentication (recommended)
# key_file = "~/.ssh/id_rsa"

[openai]
api_key = "sk-your-openai-api-key"

[email]
# For admin dashboard email monitoring
imap_server = "mail.your-provider.com"
imap_port = 993
email_address = "io@miolingo.io"
email_password = "your_email_password"

[google_cloud]
# If using Google Cloud TTS (optional)
# credentials_json = '''
# {your service account JSON here}
# '''
SECRETEOF

# Update README.md
cat > README.md << 'READMEEOF'
# Miolingo

Multi-language pronunciation trainer with real-time AI feedback.

## Features

- **Multi-language support**: Portuguese (PT-BR, PT-PT), French, Dutch, Flemish
- **Real-time feedback**: AI-powered pronunciation analysis using Whisper ASR
- **Text-to-Speech**: High-quality pronunciation examples using eSpeak NG and gTTS
- **Progress tracking**: Database-backed user progress and history
- **Admin dashboard**: Monitor usage, manage users, track costs
- **Practice modes**: Words, phrases, conversations, and stories

## Quick Start

### Prerequisites

- Python 3.8+ (3.10+ recommended)
- eSpeak NG (for text-to-speech)
- ffmpeg (for audio conversion)
- portaudio (for audio recording)
- MySQL database (local or remote)

### Installation

```bash
# 1. Configure environment
./configure

# 2. Activate virtual environment
source venv/bin/activate

# 3. Install dependencies
make install

# 4. Configure secrets
cp .streamlit/secrets_template.toml .streamlit/secrets.toml
# Edit .streamlit/secrets.toml with your credentials

# 5. Run the app
make run
```

### Admin Dashboard

```bash
make run-admin
```

Visit http://localhost:8505

## Documentation

- [User Guide](docs/app-docs/USER_GUIDE.md) - How to use the app
- [Developer Guide](docs/app-docs/DEVELOPER_GUIDE.md) - Development setup
- [Admin Guide](docs/admin-docs/ADMIN_GUIDE.md) - Admin dashboard
- [Version Workflow](VERSION_WORKFLOW.md) - Versioning and releases
- [Local Build Guide](LOCAL-BUILD.md) - Building eSpeak NG locally

## eSpeak NG Integration

Miolingo uses eSpeak NG for text-to-speech. You can:

1. Use system-installed eSpeak NG: `brew install espeak-ng` or `port install espeak-ng`
2. Build eSpeak NG locally (see [LOCAL-BUILD.md](LOCAL-BUILD.md))
3. Point to custom installation in `config/.miolingo.config`

See [ESPEAK_USAGE.md](ESPEAK_USAGE.md) for detailed integration guide.

## Development

```bash
# Install with development dependencies
make install-dev

# Run tests
make test

# Version management
source venv/bin/activate
python scripts/bump_app.py minor tag push
python scripts/bump_admin.py patch tag push
```

See [BUMP_GUIDE.md](BUMP_GUIDE.md) for version management details.

## Architecture

```
miolingo/
├── src/              # Python source code
├── docs/             # Documentation
│   ├── app-docs/     # App documentation
│   └── admin-docs/   # Admin documentation
├── scripts/          # Utility scripts
├── config/           # Configuration templates
├── language_materials/  # Language content
├── .streamlit/       # Streamlit configuration
└── tests/            # Test suite
```

## Technology Stack

- **Framework**: Streamlit
- **Speech Recognition**: OpenAI Whisper
- **Text-to-Speech**: eSpeak NG, gTTS
- **Database**: MySQL
- **Audio Processing**: ffmpeg, soundfile, numpy
- **Deployment**: Streamlit Cloud, local

## License

See [COPYING](COPYING) files for license information.

## Contributing

See [DEVELOPER_GUIDE.md](docs/app-docs/DEVELOPER_GUIDE.md) for contribution guidelines.

## Support

- Documentation: See `docs/` directory
- Issues: GitHub Issues
- Email: io@miolingo.io
READMEEOF

# Commit all new files
git add -A
git commit -m "Add miolingo build system (configure, Makefile) and configuration templates"

echo ""
echo "✓ Reorganization complete!"

# Step 6: Copy to target location
echo ""
echo "Step 6: Copying to target location..."

if [ -d "$TARGET_DIR" ]; then
    echo "⚠ Warning: $TARGET_DIR already exists"
    read -p "Remove existing directory? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm -rf "$TARGET_DIR"
    else
        echo "Aborted. Please remove $TARGET_DIR manually and run again."
        exit 1
    fi
fi

cp -R "$TEMP_DIR" "$TARGET_DIR"

echo "✓ Copied to $TARGET_DIR"

# Cleanup temp directory
echo ""
echo "Cleaning up temporary directory..."
rm -rf "$TEMP_DIR"
rm -f /tmp/miolingo-paths.txt

echo ""
echo "================================"
echo "✓ EXTRACTION COMPLETE!"
echo "================================"
echo ""
echo "Miolingo repository created at:"
echo "  $TARGET_DIR"
echo ""
echo "Next steps:"
echo "  1. cd $TARGET_DIR"
echo "  2. Review git log to verify history"
echo "  3. Test locally: ./configure && make install && make run"
echo "  4. Create GitHub repo: gh repo create fairflow/miolingo --public"
echo "  5. Push: git remote add origin git@github.com:fairflow/miolingo.git"
echo "           git push -u origin main --tags"
echo ""
echo "Don't forget to copy your secrets:"
echo "  cp /path/to/old/.streamlit/secrets.toml $TARGET_DIR/.streamlit/"
echo ""
