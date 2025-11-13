# Changelog - Miolingo Multi-Language Pronunciation Trainer

All notable changes to the Miolingo pronunciation trainer application will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).


## [1.3.1] - 2025-11-13

### Added
- **SSH Tunnel Encryption**: All database traffic now encrypted via SSH tunnel
  - Port 722 SSH connection to miolingo.io
  - ED25519 key-based authentication
  - Automatic port selection to avoid conflicts
  - Connection persistence across Streamlit reruns using `st.session_state`
  - Dual-mode key support: file path (local) or direct content (Streamlit Cloud)

### Changed
- **Session Save Behavior**: Added `st.rerun()` after saving session for immediate UI sync
  - Eliminates double-click issue on "Save Session Now" button
  - Sidebar state updates immediately after save

### Fixed
- SSH tunnel lifecycle management to prevent duplicate tunnels on Streamlit reruns
- Port binding conflicts resolved by auto-selecting available ports
- SSH port configuration (722 instead of default 22 for Krystal hosting)
- Debug logging suppressed (paramiko, gtts, urllib3, fsevents now at WARNING level)

### Security
- Database connections now fully encrypted end-to-end via SSH tunnel
- Private SSH keys kept secure (never committed to git)
- Supports both local development (key file) and cloud deployment (key content in secrets)

### Technical
- New dependencies: `paramiko<3.0` (downgraded for sshtunnel compatibility), `sshtunnel>=0.4.0`
- SSH tunnel managed in `app_mysql.py` module
- Connection uses SSH key at `~/.ssh/miolingo/mysql_tunnel_key` (local) or secrets (cloud)
- Cleanup handler registered via `atexit` to properly close tunnel on shutdown

## [1.3.0] - 2025-11-13

### Added
- **Multi-User Authentication**: Complete user authentication system with secure login/registration
  - Argon2id password hashing (100MB memory, 4 iterations, 8 threads)
  - 32-byte secure session tokens with 24-hour expiration
  - Per-user, per-language settings and progress tracking
  - Rate limiting for abuse prevention (no CAPTCHA by design)
- **MySQL Database Integration**: External database on Krystal hosting (miolingo.io)
  - 6-table schema: users, sessions, user_settings, user_progress, rate_limits, activity_log
  - Modular architecture: `app_mysql.py` module keeps all database logic separate
  - Connection pooling optimized for Krystal Emerald plan (10 connections)
- **Per-User Progress**: Practice sessions saved per-user and per-language
  - Individual statistics for each user and language combination
  - Real-time database saving after each practice
  - Recent average (last 10 practices) tracking
- **Security Features**:
  - All SQL queries parameterized to prevent injection attacks
  - Session IP validation to detect hijacking
  - Activity logging with timestamps and IP addresses
  - Secure secrets management via Streamlit secrets.toml

### Changed
- **Statistics Display**: Now pulls from database instead of local JSON files
  - Shows per-language stats dynamically based on selected language
  - Real-time updates when switching languages
  - Current session stats + all-time stats from database
- **Punctuation Handling**: Removed punctuation before audio generation
  - Prevents comma/pause detection from affecting similarity scores
  - Cleaner transcription matching
- **UI Improvements**:
  - Normalized phonemes display changed from `st.code()` to `st.markdown()` for better mobile rendering
  - Sidebar shows username, email, and logout button when authenticated
  - Login/registration forms with validation

### Fixed
- Total Perfect statistic now uses correct `exact_match` key (was showing 0%)
- Compare Phoneme Sounds buttons reference fixed (deferred for later testing)

### Technical
- Branch: `feature/multi-user-auth-v1.3.0`
- Database: MariaDB 10.6.23 on miolingo.io:3306
- New dependencies: `mysql-connector-python==9.4.0`, `argon2-cffi==25.1.0`
- All credentials git-ignored via updated `.gitignore`

---

## [1.2.1] - 2025-11-13

### Changed
- **Documentation**: Updated all documentation to be language-agnostic instead of Portuguese-specific
  - Changed app name from "Portuguese Pronunciation Trainer" to "Miolingo - Multi-Language Pronunciation Trainer"
  - Updated README.md, USER_GUIDE.md, DEVELOPER_GUIDE.md, TESTING_GUIDE.md, and app-docs/README.md
  - Replaced Portuguese-specific language with generic "pronunciation practice" or "language learning"
  - Updated primary app URL to https://miolingo.io/ with backup https://miolingo.streamlit.app/
  - Emphasized multi-language support (Portuguese, French, Dutch, Flemish) throughout docs
  - Clarified wav2vec2 is Portuguese-only, Whisper supports all languages

---

## [1.1.3] - 2025-11-13

### Fixed
- Mobile UX: removed separator line between audio and recording sections for more compact layout
- Recording instructions now dynamically display the selected language (Portuguese/French/Dutch) instead of hardcoded "Portuguese"

---

## [1.1.2] - 2025-11-13

### Fixed
- Mobile UX: reduced phrase heading size further (h3 → h4) for better screen space on phones
- Mobile UX: moved recording instructions info box below the recording widget to maximize phrase visibility
- Removed redundant "automatically selected phrase" caption that consumed screen space

---

## [1.1.1] - 2025-11-13

### Fixed
- eSpeak TTS auto-play bug: now uses `--stdout` to capture audio bytes instead of auto-playing
- Mobile UX improvements: changed phrase heading from h1 to h3 for better visibility
- Mobile layout: moved emoji inline with phrase and translation above phrase for better recording visibility

### Added
- French language materials infrastructure (phrases A-D levels)
- Helper script for French phrase setup

---

## [1.0.0] - 2025-11-11

### Added
- Multi-language support: Portuguese, French, Dutch, Flemish
- Language and voice/dialect selection in sidebar
- Dynamic phrase lists and session tracking per language
- All practice modes, scoring, and feedback now work for every supported language

### Changed
- Updated documentation for language/voice selection
- Phrase files reorganized for multi-language support

---

## [0.9.0] - 2025-11-10

### Added
- iOS Safari audio compatibility with WAV conversion feature
- User-configurable WAV audio format toggle in settings
- Edit distance (Levenshtein) scoring algorithm for pronunciation comparison
- User-selectable scoring algorithm (edit distance vs positional matching)
- User-adjustable silence trimming threshold slider (0.001-0.1)
- Version number display in sidebar
- Comprehensive version management system
- Git tags synchronized with version numbers
- CCS testing framework integration improvements

### Fixed
- Audio generation deadlock caused by ffmpeg pipe buffer overflow
- Used `subprocess.DEVNULL` to prevent ffmpeg output buffering issues
- iOS Safari "Error" on MP3 audio playback (grey player, no sound)
- Silence trimming potentially cutting off speech ends
- 0% scoring issue with pronunciation misalignment

### Changed
- Renamed application file from `streamlit_app_v2.py` to `app.py`
- Enhanced phoneme analysis to work with edit distance algorithm
- Improved results display with edit distance metrics

### Technical Details
- ffmpeg MP3→WAV conversion for iOS compatibility
- PCM 16-bit WAV format at 22050Hz sample rate
- Spinner + subprocess deadlock resolution via `DEVNULL`
- Levenshtein distance algorithm for flexible scoring

---

## Version History Summary

- **0.9.0** (2025-11-10) - iOS audio fix, edit distance scoring, version system
- Future versions will be documented here as they are released
- Version 1.0.0 will mark the first stable production release

---

## Versioning Scheme

This project uses [Semantic Versioning](https://semver.org/):
- **MAJOR.MINOR.PATCH** (e.g., `0.9.0`)
- Version progression: `0.9.0` → `0.9.1` → ... → `0.9.9` → `1.0.0`
- **PATCH**: Bug fixes only
- **MINOR**: New features (backward compatible)
- **MAJOR**: Breaking changes or stable release milestone (0.x.x → 1.0.0)

Git tags match version numbers: `v0.9.0`, `v0.9.1`, `v1.0.0`, etc.

## How to Update Version

1. Update `__version__` in `app.py`
2. Update this CHANGELOG.md with changes
3. Commit changes: `git commit -m "Bump version to X.Y.Z"`
4. Create matching git tag: `git tag -a vX.Y.Z -m "Version X.Y.Z"`
5. Push with tags: `git push myfork main --tags`

## Version 0.9.1 (2025-11-10)

### Bug Fixes
- **WAV Audio Setting Persistence**: Fixed issue where "Use WAV audio format" checkbox setting would not persist after page reload
  - Setting now auto-saves immediately when toggled
  - Added visual confirmation message when saved
  - Ensures iOS Safari users don't lose their audio format preference

