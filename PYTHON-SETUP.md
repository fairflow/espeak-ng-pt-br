# Python Environment Setup

## Why Virtual Environment?

This project uses a Python virtual environment to:
- **Isolate dependencies** - Avoid conflicts with system packages
- **Reproducibility** - Same versions across different machines
- **Clean installation** - Easy to remove without affecting system

## Quick Setup

```bash
# One-time setup
./setup.sh

# Every time you work on the project
source venv/bin/activate

# When done
deactivate
```

## Manual Setup

If you prefer to set up manually:

```bash
# Create virtual environment
python3 -m venv venv

# Activate it (do this every time you work on the project)
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Verify installation
python3 -c "import whisper; print('Whisper installed!')"
```

## Checking Your Environment

```bash
# Make sure venv is activated (should see (venv) in prompt)
which python3
# Should show: /path/to/espeak-ng/venv/bin/python3

# Check installed packages
pip list
```

## Using the Tools

### Current Tools (no venv needed)
```bash
# These work without venv
./speak_phonemes.py "k'az&"
./local/bin/run-espeak-ng "casa"
```

### New Speech Recognition Tools (requires venv)
```bash
# Must activate venv first!
source venv/bin/activate

# Then use
python3 pronunciation_trainer.py
python3 record_audio.py
```

## Dependencies Explained

- **openai-whisper** - Speech-to-text (supports Portuguese)
- **sounddevice** - Record audio from microphone
- **soundfile** - Save/load audio files
- **numpy** - Array processing (required by audio tools)
- **librosa** (optional) - Advanced audio processing

## Troubleshooting

### "command not found: python3"
Make sure venv is activated: `source venv/bin/activate`

### "No module named 'whisper'"
```bash
source venv/bin/activate
pip install -r requirements.txt
```

### Deactivate and start fresh
```bash
deactivate
rm -rf venv
./setup.sh
```

## Integration with Existing Tools

The existing tools (`speak_phonemes.py`, `run-espeak-ng`) work **without** the venv because they only use standard library + subprocess.

The **new** speech recognition tools need the venv because they use external packages (Whisper, sounddevice, etc.).

## Workflow

```bash
# Start work session
cd /path/to/espeak-ng
source venv/bin/activate

# Record your pronunciation
python3 record_audio.py -o recording.wav

# Train with it
python3 pronunciation_trainer.py casa recording.wav

# Done for the day
deactivate
```
