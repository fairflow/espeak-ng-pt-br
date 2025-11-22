# Speech Recognition Pronunciation Trainer - Quick Start

## Prerequisites

**Required:** ffmpeg

```bash
sudo port install ffmpeg
```

## Setup (One Time)

```bash
# Run the setup script
./setup.sh

# Or manually:
source venv/bin/activate
pip install -r requirements.txt
```

## Usage

### Quick Test

```bash
# Activate venv first
source venv/bin/activate

# Test your microphone
python3 record_audio.py --test

# Practice a single word (will record from mic)
python3 pronunciation_trainer.py casa
```

### Practice Workflow

**1. Single Word Practice**
```bash
source venv/bin/activate
python3 pronunciation_trainer.py casa
```

This will:
- Show you the correct phonemes
- Play the correct pronunciation
- Record you saying the word (3 seconds)
- Transcribe what you said
- Compare phonemes
- Give you feedback

**2. Pre-recorded Audio**
```bash
# Record first
python3 record_audio.py -o my_casa.wav -d 3

# Then practice
python3 pronunciation_trainer.py casa my_casa.wav
```

**3. Batch Practice**
```bash
# Create a word list (one per line)
cat > my_words.txt << EOF
casa
água
pessoa
EOF

# Practice all words
python3 pronunciation_trainer.py --batch my_words.txt
```

### Advanced Options

```bash
# Use better Whisper model (more accurate, slower)
python3 pronunciation_trainer.py --model small casa

# Longer recording time
python3 pronunciation_trainer.py --duration 5 "por favor"

# European Portuguese instead of Brazilian
python3 pronunciation_trainer.py --voice pt casa
```

## Tools Reference

### pronunciation_trainer.py
Main tool that combines speech recognition + phoneme comparison.

```bash
# Basic
python3 pronunciation_trainer.py WORD

# With audio file
python3 pronunciation_trainer.py WORD audio.wav

# Batch mode
python3 pronunciation_trainer.py --batch words.txt

# Options
  --model, -m      Whisper model: tiny/base/small/medium/large
  --voice, -v      Voice: pt-br (default) or pt
  --duration, -d   Recording seconds (default: 3)
```

### record_audio.py
Simple audio recorder for practice sessions.

```bash
# Record 3 seconds
python3 record_audio.py -o recording.wav

# Record 5 seconds
python3 record_audio.py -o recording.wav -d 5

# Test microphone (record + playback)
python3 record_audio.py --test

# List audio devices
python3 record_audio.py --list
```

### speak_phonemes.py
Original tool - works WITHOUT venv (no speech recognition).

```bash
# No venv needed!
./speak_phonemes.py "k'az&"
./speak_phonemes.py -c "casa"
./speak_phonemes.py "k'az&" -C "casa"
```

## Example Session

```bash
# 1. Activate venv
source venv/bin/activate

# 2. Test everything works
python3 record_audio.py --test

# 3. Practice a word
python3 pronunciation_trainer.py casa
# (Record when prompted, get feedback)

# 4. Practice multiple words
python3 pronunciation_trainer.py --batch practice_words.txt

# 5. Done - deactivate venv
deactivate
```

## Understanding the Output

```
🎯 Target word: casa
📝 Correct phonemes: k'az&

🔊 Listen to correct pronunciation:
[plays audio]

🎤 Recording for 3 seconds...
Speak now!
✓ Recording complete

🎧 Transcribing audio...
✓ Recognized: "casa"

📝 Your phonemes: k'az&

======================================================================
✅ PERFECT! Phonemes match exactly!
======================================================================
```

If not perfect:
```
======================================================================
📊 Similarity: 85.0%
🟡 Good attempt, but needs some work.
======================================================================

🔊 Listen to the difference:
   Correct:
   [plays correct]
   Your version:
   [plays your version]
```

## Troubleshooting

### "Import error" messages
```bash
# Make sure venv is activated
source venv/bin/activate

# Check Python location
which python3  # Should show: .../espeak-ng/venv/bin/python3
```

### Microphone not working
```bash
# List available devices
python3 record_audio.py --list

# Test microphone
python3 record_audio.py --test
```

### Whisper loading slowly
First run downloads the model (~140MB for 'base'). Use smaller:
```bash
python3 pronunciation_trainer.py --model tiny casa
```

### Low recognition accuracy
- Speak clearly and closer to microphone
- Use a better Whisper model: `--model small` or `--model medium`
- Reduce background noise

## Tips

1. **Start with 'tiny' or 'base' model** - Fast enough for practice
2. **Use --model small** - If recognition seems off
3. **Practice consistently** - Short sessions (5-10 words) daily
4. **Record multiple attempts** - Save your progress
5. **Focus on problem sounds** - Brazilian Portuguese ɐ, ʃ, ʒ, etc.

## Files

- `pronunciation_trainer.py` - Main training tool (needs venv)
- `record_audio.py` - Audio recorder (needs venv)
- `speak_phonemes.py` - Phoneme speaker (no venv needed)
- `practice_words.txt` - Example word list
- `requirements.txt` - Python dependencies
- `setup.sh` - One-command setup
