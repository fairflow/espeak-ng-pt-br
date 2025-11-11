# Copilot Instructions for Portuguese Pronunciation Trainer (espeak-ng-pt-br)

## Project Overview
- This is a Streamlit web app for multi-language pronunciation practice (Portuguese, French, Dutch, Flemish) with real-time AI feedback.
- Core tech: Python (Streamlit), eSpeak NG (TTS), OpenAI Whisper (ASR), ffmpeg (audio), soundfile/numpy (processing).
- App logic is in `app.py`. Documentation and guides are in `app-docs/`.

## Architecture & Data Flow
- User interacts via Streamlit UI (`app.py`).
- Practice session state: current phrase, user recordings, settings (language, voice/dialect).
- TTS: eSpeak NG (formant synthesis) and optionally gTTS.
- Audio is generated, possibly converted (MP3→WAV via ffmpeg), then played back.
- User records audio; recognition is performed using Whisper.
- Results and history are stored in `practice_history.json` (runtime, not in git).

## Key Files & Directories
- `app.py`: Main app logic, language/voice config, session state, UI.
- `app-docs/`: Contains `USER_GUIDE.md`, `TESTING_GUIDE.md`, `DEVELOPER_GUIDE.md`.
- `practice_config.json`, `practice_history.json`: User/session data (runtime only).
- `requirements.txt`: Python dependencies.
- `phsource/`, `dictsource/`, `espeak-ng-data/`: eSpeak NG data and sources.
- `APP_CHANGELOG.md`, `VERSION_WORKFLOW.md`: Versioning and workflow docs.

## Developer Workflow
- Use Python 3.8+ (3.10+ recommended), ffmpeg, portaudio, eSpeak NG (see DEVELOPER_GUIDE.md for install).
- Create a virtual environment and install dependencies with `pip install -r requirements.txt`.
- Run locally: `streamlit run app.py`.
- First run downloads Whisper model (base).
- Use VS Code with Python extension, Black for formatting, Pylint/Ruff for linting.
- Versioning follows semantic versioning; see `VERSION_WORKFLOW.md` for branch/tag conventions.

## Project-Specific Patterns
- Language/voice selection is dynamic; config is in `app.py`.
- Phrase files are organized per language.
- All user/session data is runtime-only and not committed.
- CCS testing framework is available for advanced UI state testing (`ccs_test_framework.py`).
- Documentation is kept in `app-docs/` and referenced from the UI and guides.

## Integration Points
- eSpeak NG binaries and data must be available; may require local build/install.
- Whisper model is downloaded at runtime.
- ffmpeg is required for audio conversion.
- App can be deployed on Streamlit Cloud or run locally.

## Example Commands
- Local run: `streamlit run app.py`
- Install dependencies: `pip install -r requirements.txt`
- Check eSpeak NG: `espeak-ng --version`

## References
- For user, tester, and developer guides, see `app-docs/`.
- For versioning and workflow, see `VERSION_WORKFLOW.md` and `APP_CHANGELOG.md`.
- For eSpeak NG details, see `docs/` and upstream eSpeak NG documentation.

---
If any section is unclear or missing, please provide feedback for further refinement.
