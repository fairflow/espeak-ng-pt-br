# Practice App User Guide

## Overview

**practice_app.py** is an interactive terminal application for Brazilian Portuguese pronunciation practice with persistent settings, progress tracking, and session management.

## Features

### 🎯 Core Features
- **Persistent Settings**: Save your preferred speed, pitch, voice, and model
- **Progress Tracking**: Track all practice sessions with detailed statistics
- **Multiple Practice Modes**: Quick practice, sentences, or batch from files
- **Session History**: Review past sessions and replay results
- **Auto-Configuration**: Settings remembered between sessions

### 📊 Progress Features
- Session-by-session tracking
- Perfect match counter
- Average similarity scores
- Historical statistics
- Detailed practice logs

### ⚙️ Customization
- Adjustable speech speed (80-450 wpm)
- Adjustable pitch (0-99)
- Voice selection (pt-br, pt)
- Whisper model selection (tiny, base, small, medium, large)
- Recording duration settings

## Quick Start

```bash
# Activate virtual environment
source venv/bin/activate

# Run the app
./practice_app.py
```

## Menu Options

### 1. Quick Practice
Single word or phrase practice with immediate feedback.

**Flow:**
1. Enter word/phrase
2. Listen to pronunciation
3. Record your attempt
4. Get instant feedback with phoneme comparison
5. Result saved to session

**Example:**
```
Enter word or phrase to practice: casa
[eSpeak pronounces "casa"]
Recording... 3 seconds
[Analysis and feedback]
```

### 2. Sentence Practice
Automatic duration calculation based on sentence length.

**Features:**
- Auto-calculates recording time (≈2.5 words/second + 2s buffer)
- Handles full sentences naturally
- Results tracked in history

**Example:**
```
Enter sentence: minha mãe nasceu na Inglaterra em 1933
📏 8 words → 5 seconds recording time
[Practice begins]
```

### 3. Practice from File
Batch practice mode - import text file with multiple items.

**File Format:**
```
casa
minha mãe
o gato está no telhado
eu gosto de estudar português
```

**Process:**
1. Enter filename
2. App shows item count
3. Confirm to practice all
4. Goes through each item sequentially
5. Press Enter between items
6. All results saved to session

### 4. View Statistics
Comprehensive stats display:

**Current Session:**
- Number of practices
- Perfect matches count & percentage
- Average similarity score

**All Time:**
- Total practices across all sessions
- Total perfect matches
- Overall average similarity
- Number of sessions
- Last session date

**Example Output:**
```
📊 PRACTICE STATISTICS
====================================
🔵 Current Session:
  Practices: 8
  Perfect: 3 (37.5%)
  Avg Similarity: 82.3%

📈 All Time:
  Total Practices: 127
  Total Perfect: 45 (35.4%)
  Overall Avg: 78.9%
  
  Sessions: 12
  Last session: 2025-11-07
```

### 5. Review Session History
Browse and review past practice sessions.

**Features:**
- Shows last 10 sessions
- Date, practice count, perfect count
- Select session to view full details
- See exact phoneme comparisons for each practice

**Detail View Shows:**
- Target text
- Recognized text
- Correct phonemes (when not perfect)
- Your phonemes (when not perfect)
- Match status or similarity score

### 6. Settings
Interactive settings editor.

**Configurable Options:**

**Speed** (80-450, default 140):
- 80-100: Very slow, for careful learning
- 100-120: Slow, clear practice
- 140: Normal speech (default)
- 180+: Faster speech

**Pitch** (0-99, default 35):
- 0-25: Lower pitch
- 35: Normal (default)
- 50-99: Higher pitch

**Voice**:
- `pt-br`: Brazilian Portuguese (default)
- `pt`: European Portuguese

**Model** (Whisper):
- `tiny`: Fastest, least accurate
- `base`: Good balance (default)
- `small`: Better accuracy, slower
- `medium`: High accuracy, slower
- `large`: Best accuracy, slowest

**Duration** (seconds):
- Recording time for quick practice
- Default: 3 seconds
- Increase for longer phrases

**Settings Example:**
```
📝 Edit Settings
(Press Enter to keep current value)
Speed [140]: 100
Pitch [35]: 40
Voice [pt-br]: 
Model [base]: 
Recording duration [3]: 4

✓ Settings updated!
```

### 7. View Current Settings
Display current configuration without editing.

### 8. Save & Exit
Saves current session to history and all settings, then exits.

**What Gets Saved:**
- Current session practices (if any)
- All settings changes
- Appended to history file

### 9. Exit without Saving
Exits without saving current session (settings already auto-saved when changed).

## Data Files

The app creates and manages several files:

### `practice_config.json`
Your saved settings:
```json
{
  "speed": 100,
  "pitch": 40,
  "voice": "pt-br",
  "model": "base",
  "duration": 4
}
```

### `practice_history.json`
Complete session history:
```json
[
  {
    "date": "2025-11-07T14:30:00",
    "practices": [
      {
        "time": "2025-11-07T14:31:15",
        "target": "casa",
        "recognized": "casa",
        "correct_phonemes": "k'az&",
        "user_phonemes": "k'az&",
        "match": true,
        "similarity": 1.0
      }
    ]
  }
]
```

### `practice_audio/`
Directory for audio recordings (future feature).

## Usage Tips

### For Beginners
1. Start with **Settings** (option 6):
   - Set speed to 100
   - Set pitch to 40
   - Keep pt-br voice
2. Use **Quick Practice** (option 1) for single words
3. Review **Statistics** (option 4) to track improvement

### For Advanced Practice
1. Create word lists in text files
2. Use **Practice from File** (option 3) for batch training
3. Use **Sentence Practice** (option 2) with complex sentences
4. Gradually increase speed as you improve

### Progress Tracking Strategy
1. Practice daily with consistent settings
2. Review **Statistics** after each session
3. Use **Session History** to identify difficult words
4. Aim to increase your perfect match percentage over time

## Keyboard Shortcuts

- **Ctrl+C**: Cancel current operation (returns to menu)
- **Enter**: Confirm choices or skip to defaults
- **Type number + Enter**: Select menu option

## Troubleshooting

### "Run from espeak-ng directory with venv activated"
```bash
cd /path/to/espeak-ng
source venv/bin/activate
./practice_app.py
```

### Settings Not Saving
- Check write permissions in current directory
- Look for `practice_config.json` file creation
- Settings auto-save when edited, but session only saves on option 8

### Audio Not Working
- Ensure espeak-ng is built and in PATH
- Check microphone permissions
- Test with `./record_audio.py --test`

### Poor Recognition
- Try increasing recording duration (Settings → Duration)
- Speak clearly into microphone
- Check microphone input level
- Consider upgrading Whisper model (tiny → base → small)

## Example Workflow

**Session 1: Initial Setup**
```
1. Run app
2. Edit Settings (option 6):
   - Speed: 100
   - Pitch: 40
3. Quick Practice (option 1): "casa"
4. Quick Practice (option 1): "gato"
5. View Statistics (option 4)
6. Save & Exit (option 8)
```

**Session 2: Word List Practice**
```
1. Create words.txt:
   casa
   gato
   água
   pão

2. Run app (settings loaded automatically)
3. Practice from File (option 3): words.txt
4. View Statistics (option 4)
5. Review Session History (option 5)
6. Save & Exit (option 8)
```

**Session 3: Sentence Practice**
```
1. Run app
2. Sentence Practice (option 2):
   "minha mãe gosta de café"
3. Sentence Practice (option 2):
   "o gato está dormindo"
4. View Statistics (option 4) - see improvement
5. Save & Exit (option 8)
```

## Advanced Features (Coming Soon)

- Audio export/replay of your recordings
- Visual waveform comparison
- Pronunciation difficulty rating
- Custom practice plans
- Spaced repetition algorithm
- Export progress reports

## Tips for Best Results

1. **Consistent Environment**: Practice in a quiet space
2. **Regular Sessions**: Daily 10-15 minute sessions better than long irregular ones
3. **Progressive Difficulty**: Start with words, advance to sentences
4. **Review History**: Learn from past mistakes
5. **Adjust Speed**: Slow down for learning, speed up as you improve
6. **Track Progress**: Watch your similarity scores increase over time

## Data Privacy

All data is stored locally:
- `practice_config.json` - Your settings
- `practice_history.json` - Your practice history
- `practice_audio/` - Your recordings (future)

Nothing is uploaded or shared externally.

## Support

For issues or questions:
1. Check this guide
2. Review other documentation (QUICKSTART-SPEECH-RECOGNITION.md)
3. Test components individually (pronunciation_trainer.py)
4. Check microphone with record_audio.py

---

**Happy practicing! 🇧🇷 Boa sorte com seus estudos!**
