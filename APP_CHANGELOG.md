# Changelog - Portuguese Pronunciation Trainer

All notable changes to the Portuguese Pronunciation Trainer application will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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

