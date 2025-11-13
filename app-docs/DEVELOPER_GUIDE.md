# Developer Guide - Miolingo Multi-Language Pronunciation Trainer

**Version 1.2.1** | Last Updated: 13 November 2025

This guide is for developers who want to contribute to, modify, or understand the Miolingo pronunciation trainer codebase.

---

## 📋 Table of Contents

- [Project Overview](#project-overview)
- [Getting Started](#getting-started)
- [Architecture](#architecture)
- [Development Workflow](#development-workflow)
- [Testing](#testing)
- [Deployment](#deployment)
- [Contributing](#contributing)

---

## 🎯 Project Overview

### What Is This?

A Streamlit web application for practicing pronunciation in multiple languages (Portuguese, French, Dutch, Flemish) with real-time feedback using AI speech recognition. Users can select their language and voice/dialect in the sidebar; all practice features work identically for every supported language.

### Tech Stack

- **Frontend**: Streamlit (Python web framework)
- **Speech Recognition**: OpenAI Whisper (ML model)
- **Text-to-Speech**: eSpeak NG (formant synthesis)
- **Audio Processing**: ffmpeg, soundfile, numpy
- **Deployment**: Streamlit Cloud (can also run locally)

### Repository Structure

```
espeak-ng/
├── app.py                          # Main Streamlit application (v0.9.1)
├── app-docs/                       # App documentation (this folder)
│   ├── README.md                   # Documentation index
│   ├── USER_GUIDE.md               # User guide
│   ├── TESTING_GUIDE.md            # Testing guide
│   └── DEVELOPER_GUIDE.md          # This file
├── practice_config.json            # User settings (not in git)
├── practice_history.json           # Practice history (not in git)
├── APP_CHANGELOG.md                # App version history
├── VERSION_WORKFLOW.md             # Git workflow documentation
├── requirements.txt                # Python dependencies
├── ccs_test_framework.py           # CCS testing framework
├── ccs_test_integration.py         # CCS Streamlit integration
├── CCS_TESTING_README.md           # CCS testing docs
├── practice_phrases_with_translations.txt  # Sample phrases
├── phsource/                       # eSpeak phoneme source files
├── dictsource/                     # eSpeak dictionary sources
├── espeak-ng-data/                 # Compiled eSpeak data
├── src/                            # eSpeak NG C source code
├── docs/                           # eSpeak NG documentation
└── [other espeak-ng files]         # Original eSpeak NG project files
```

### Key Files

| File | Purpose |
|------|---------|
| `app.py` | Main Streamlit app (renamed from `streamlit_app_v2.py`) |
| `practice_config.json` | Persists user settings (created at runtime) |
| `practice_history.json` | Stores practice sessions (created at runtime) |
| `requirements.txt` | Python package dependencies |
| `APP_CHANGELOG.md` | App-specific version history |
| `VERSION_WORKFLOW.md` | Git branching and versioning guide |

---

## 🚀 Getting Started

### Prerequisites

- **Python 3.8+** (3.10+ recommended)
- **Git**
- **ffmpeg** (for audio conversion)
  - macOS: `brew install ffmpeg` or `port install ffmpeg`
  - Linux: `apt-get install ffmpeg`
  - Windows: Download from ffmpeg.org
- **portaudio** (for audio recording)
  - macOS: `brew install portaudio` or `port install portaudio`
  - Linux: `apt-get install portaudio19-dev`
  - Windows: Usually handled by pip packages
- **eSpeak NG** (included in repo, but may need compilation)
  - macOS: `brew install espeak-ng` or `port install espeak-ng`
  - Linux: `apt-get install espeak-ng`
  - Windows: Download from GitHub releases

### Initial Setup

#### 1. Clone the Repository

```bash
git clone https://github.com/fairflow/espeak-ng-pt-br.git
cd espeak-ng-pt-br
```

#### 2. Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

#### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

**Note**: First run will download Whisper model (~150MB for `base` model).

#### 4. Verify eSpeak NG

```bash
espeak-ng --version
```

If not found, you may need to build from source (see eSpeak NG docs).

#### 5. Run the App Locally

```bash
streamlit run app.py
```

App will open at `http://localhost:8501`

### Development Environment

Recommended tools:
- **IDE**: VS Code with Python extension
- **Linting**: Pylint or Ruff
- **Formatting**: Black
- **Type Checking**: mypy (optional)

#### VS Code Settings

Create `.vscode/settings.json`:

```json
{
  "python.linting.enabled": true,
  "python.formatting.provider": "black",
  "editor.formatOnSave": true
}
```

---

## 🏗️ Architecture

### Application Flow

```
User Input (Browser)
    ↓
Streamlit Interface (app.py)
    ↓
┌─────────────────────────────────────────────┐
│  Practice Session State                     │
│  - Current phrase                           │
│  - User recordings                          │
│  - Settings (language, voice/dialect, etc.) │
└─────────────────────────────────────────────┘
    ↓
Text-to-Speech (eSpeak NG, gTTS)
    ↓
Audio Generation (per selected language/voice)
    ↓
Optional: MP3→WAV Conversion (ffmpeg)
    ↓
User Records Audio
    ↓
Speech Recognition (Whisper)
    ↓
Phoneme Comparison (Edit Distance)
    ↓
Scoring & Feedback
    ↓
History Storage (JSON)
```

### Key Components

#### 1. Session State Management

Streamlit uses `st.session_state` to persist data across reruns:

```python
# Initialize session state
if 'settings' not in st.session_state:
    st.session_state.settings = load_settings()

if 'current_session' not in st.session_state:
    st.session_state.current_session = {
        "practices": [],
        "start_time": time.time()
    }
```

#### 2. Text-to-Speech Pipeline

```python
def speak_text_gtts(text: str, lang: str = "pt-br", use_wav: bool = False) -> tuple[bytes, str]:
    """
    Generate audio from text using gTTS.
    
    Args:
        text: Text to synthesize
        lang: Language code
        use_wav: Convert to WAV format (for iOS Safari)
        
    Returns:
        (audio_bytes, format) tuple
    """
    # Generate MP3 with gTTS
    tts = gTTS(text=text, lang=lang, slow=False)
    
    if use_wav:
        # Convert MP3→WAV with ffmpeg
        # CRITICAL: Use subprocess.DEVNULL to prevent deadlock
        result = subprocess.run(
            ['ffmpeg', '-i', mp3_path, '-acodec', 'pcm_s16le', 
             '-ar', '22050', '-y', wav_path],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        return wav_bytes, "wav"
    
    return mp3_bytes, "mp3"
```

**Important**: The `subprocess.DEVNULL` is critical to prevent pipe buffer deadlock with ffmpeg's verbose output.

#### 3. Speech Recognition

```python
def recognize_speech_whisper(audio_file: str, model_name: str = "base") -> str:
    """
    Transcribe audio using OpenAI Whisper.
    
    Args:
        audio_file: Path to audio file (WAV format)
        model_name: Whisper model size (tiny/base/small/medium/large)
        
    Returns:
        Transcribed text
    """
    model = whisper.load_model(model_name)
    result = model.transcribe(
        audio_file,
        language="pt",
        fp16=False  # Disable for CPU compatibility
    )
    return result["text"]
```

#### 4. Phoneme Comparison & Scoring

Two algorithms available:

**Edit Distance (Recommended)**:
```python
def levenshtein_distance(s1: str, s2: str) -> int:
    """
    Calculate Levenshtein distance between two strings.
    Handles insertions, deletions, substitutions.
    """
    # Dynamic programming implementation
    # Returns minimum number of edits needed
```

**Positional Matching (Deprecated)**:
```python
def compare_phonemes_positional(target: str, spoken: str) -> dict:
    """
    Character-by-character comparison.
    Less forgiving of minor errors.
    """
```

#### 5. Settings Persistence

```python
def save_settings(settings: Dict):
    """Save settings to practice_config.json"""
    with open("practice_config.json", 'w') as f:
        json.dump(settings, f, indent=2)

def load_settings() -> Dict:
    """Load settings with defaults"""
    default_settings = {
        "speed": 140,
        "pitch": 35,
        "voice": "pt-br",
        "whisper_model_size": "base",
        "duration": 3,
        "comparison_algorithm": "edit_distance",
        "silence_threshold": 0.01,
        "use_wav_audio": False
    }
    # Merge saved settings with defaults
    return merged_settings
```

---

## 🔄 Development Workflow

### Git Workflow

We follow the workflow documented in `VERSION_WORKFLOW.md`:

#### Branch Strategy

- **`main`**: Production-ready code only
- **`feature/feature-name`**: New features
- **`bugfix/bug-name`**: Bug fixes
- **`hotfix/critical-fix`**: Critical production fixes

#### Making Changes

1. **Create feature branch**:
```bash
git checkout main
git pull myfork main
git checkout -b feature/new-practice-mode
```

2. **Make changes and commit**:
```bash
git add app.py
git commit -m "Add spaced repetition practice mode"
```

3. **Push to remote**:
```bash
git push myfork feature/new-practice-mode
```

4. **Test thoroughly** before merging to main

5. **Merge to main** (with permission):
```bash
git checkout main
git merge feature/new-practice-mode
git push myfork main
```

### Versioning


Follow **Semantic Versioning** (MAJOR.MINOR.PATCH):

- **PATCH** (0.9.0 → 0.9.1): Bug fixes only
- **MINOR** (0.9.1 → 0.10.0): New features (backward compatible)
- **MAJOR** (0.9.9 → 1.0.0 → 1.0.1): Breaking changes or stable milestone

**Note**: 0.9.9 → 1.0.0 → 1.0.1 (NOT 0.10.0)

#### Releasing a New Version

1. **Update version in `app.py`**:
```python
__version__ = "0.9.2"
```

2. **Update `APP_CHANGELOG.md`**:
```markdown
## Version 0.9.2 (2025-11-XX)

### Added
- New spaced repetition mode

### Fixed
- Audio playback on Firefox
```

3. **Commit changes**:
```bash
git add app.py APP_CHANGELOG.md
git commit -m "Bump version to 0.9.2"
```

4. **Create git tag**:
```bash
git tag -a v0.9.2 -m "Version 0.9.2 - Spaced repetition mode"
```

5. **Push with tags**:
```bash
git push myfork main --follow-tags
```

### Code Style

Follow PEP 8:
- 4 spaces for indentation
- Max line length: 88 characters (Black default)
- Use type hints where helpful
- Document complex functions

### Testing Locally

Before pushing:

1. **Run the app**:
```bash
streamlit run app.py
```

2. **Test all practice modes**
3. **Test on different browsers** (if possible)
4. **Check console for errors** (F12 → Console tab)
5. **Verify settings persistence** (reload page, check settings)

---

## 🧪 Testing

### Manual Testing

See `app-docs/TESTING_GUIDE.md` for comprehensive testing checklist.

### Automated Testing (Future)

Currently no automated tests. Potential additions:
- Unit tests for scoring algorithms
- Integration tests for audio pipeline
- UI tests with Selenium/Playwright

### CCS Testing Framework

For advanced state-based testing, see `CCS_TESTING_README.md`.

Enables systematic testing of UI state consistency.

---

## 🚀 Deployment

### Streamlit Cloud (Recommended)

1. **Push code to GitHub**:
```bash
git push myfork main
```

2. **Go to** [share.streamlit.io](https://share.streamlit.io)

3. **Create new app**:
   - Repository: `fairflow/espeak-ng-pt-br`
   - Branch: `main`
   - Main file path: `app.py`

4. **Deploy**

5. **Configure settings** (if needed):
   - Python version: 3.10
   - Secrets: (none required for this app)

### Local Deployment

For development/testing:

```bash
source venv/bin/activate
streamlit run app.py
```

### Docker (Future)

No Docker configuration yet. Could be added for:
- Consistent development environment
- Easy deployment to other hosting platforms

---

## 🤝 Contributing

### Before You Start

1. Read this guide thoroughly
2. Check existing issues/feature requests
3. Discuss major changes first (create an issue)

### Contribution Types

#### Bug Fixes

1. Reproduce the bug
2. Create bugfix branch: `git checkout -b bugfix/fix-audio-playback`
3. Fix and test thoroughly
4. Update `APP_CHANGELOG.md` if user-facing
5. Submit for review

#### New Features

1. Discuss feature first (GitHub issue or direct contact)
2. Create feature branch: `git checkout -b feature/spaced-repetition`
3. Implement with tests
4. Update documentation (`USER_GUIDE.md`, etc.)
5. Update `APP_CHANGELOG.md`
6. Submit for review

#### Documentation

- Always welcome!
- Especially helpful: clarifying confusing sections
- Add examples, screenshots, troubleshooting tips

### Pull Request Guidelines

**Good PR**:
- Clear description of what changed and why
- References related issue (if exists)
- Tested on at least one device/browser
- Documentation updated (if user-facing)
- Commit messages are clear

**Example PR description**:
```
## Add spaced repetition practice mode

### Changes
- New "Smart Review" mode that prioritizes low-scoring words
- Stores difficulty ratings in practice history
- Shows recommended next practice time

### Testing
- Tested on Chrome (Mac) and Safari (iPhone)
- Verified settings persistence
- Checked backward compatibility with old history files

### Documentation
- Updated USER_GUIDE.md with new mode instructions
- Added section to TESTING_GUIDE.md
- Updated APP_CHANGELOG.md

Fixes #42
```

### Code Review Process

1. **Submit PR** to `main` branch
2. **Automated checks** (if configured)
3. **Manual review** by maintainer
4. **Address feedback**
5. **Merge** when approved

---

## 📚 Additional Resources

### Internal Documentation

- `VERSION_WORKFLOW.md` - Detailed git workflow
- `CCS_TESTING_README.md` - Advanced testing framework
- `APP_CHANGELOG.md` - Version history

### External Documentation

- [Streamlit docs](https://docs.streamlit.io/)
- [OpenAI Whisper](https://github.com/openai/whisper)
- [eSpeak NG](https://github.com/espeak-ng/espeak-ng)
- [gTTS](https://gtts.readthedocs.io/)

### Common Issues

#### Whisper Model Not Loading

```python
# Make sure model name is valid
valid_models = ["tiny", "base", "small", "medium", "large"]
```

#### Audio Format Issues

- iOS Safari requires WAV format
- Android/Desktop work with MP3
- Use `use_wav` parameter to toggle

#### ffmpeg Deadlock

```python
# ALWAYS use subprocess.DEVNULL with ffmpeg
subprocess.run(
    ffmpeg_command,
    stdout=subprocess.DEVNULL,  # Critical!
    stderr=subprocess.DEVNULL   # Critical!
)
```

---

## 📞 Contact

For questions or collaboration:

- GitHub Issues: [Create an issue](https://github.com/fairflow/espeak-ng-pt-br/issues)
- Email: [Add contact email]
- Maintainer: Matthew & Contributors

---

## 📄 License

GPL-3.0 (inherited from eSpeak NG)

---

**Happy coding! 🚀**

*Last updated: Version 1.0.1 (November 11, 2025)*
