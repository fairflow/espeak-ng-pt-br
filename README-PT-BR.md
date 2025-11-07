# eSpeak NG - Brazilian Portuguese Pronunciation Training

This fork contains a complete pronunciation training system for Brazilian Portuguese with speech recognition capabilities.

## 🚀 Quick Start

```bash
# 1. Activate the virtual environment
source venv/bin/activate

# 2. Run the practice app
./practice_app.py
```

That's it! The app will guide you through everything.

## 📱 Practice App Features

The **practice_app.py** provides a complete interactive practice system:

- ✅ **Persistent Settings** - Your preferences (speed, pitch, voice) are saved automatically
- ✅ **Progress Tracking** - Every practice session is logged with detailed statistics
- ✅ **Multiple Practice Modes** - Quick words, full sentences, or batch from files
- ✅ **Session History** - Review past sessions and track improvement over time
- ✅ **Smart Duration** - Automatically calculates recording time for sentences
- ✅ **Instant Feedback** - See phoneme-level comparison after each attempt

### Practice Modes

1. **Quick Practice**: Single word/phrase with immediate feedback
2. **Sentence Practice**: Full sentences with auto-duration calculation
3. **Practice from File**: Import text files for batch training
4. **Statistics**: View your progress and improvement trends
5. **Session History**: Review and replay past practice sessions

### Example Workflow

```bash
# First time setup
source venv/bin/activate
./practice_app.py

# In the app:
# 1. Choose "6. Settings"
# 2. Set speed to 100 (slower, clearer)
# 3. Set pitch to 40
# 4. Choose "1. Quick Practice"
# 5. Practice: "casa"
# 6. Listen → Record → Get feedback
# 7. Keep practicing!
```

### Sample Practice File

A `sample_practice.txt` file is included with common words and phrases:

```bash
# In the app:
# Choose "3. Practice from File"
# Enter: sample_practice.txt
# Confirm: y
# Practice each item one by one
```

## 📊 Progress Tracking

All your practice data is saved locally:

- **practice_config.json** - Your settings (speed, pitch, voice, model)
- **practice_history.json** - Complete history of all practice sessions
- **Statistics** - Perfect match rate, average similarity, improvement trends

### Example Stats Display

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
```

## 🎯 Command Line Tools

For more control, use the individual tools:

### pronunciation_trainer.py
Speech recognition with Whisper AI:

```bash
source venv/bin/activate

# Practice a word
python3 pronunciation_trainer.py "casa"

# Slow, clear speech
python3 pronunciation_trainer.py --speed 100 --pitch 40 "minha mãe"

# Practice a sentence
python3 pronunciation_trainer.py -s 100 "o gato está dormindo"
```

### practice_sentences.py
Sentence practice with smart features:

```bash
# Auto-duration calculation
python3 practice_sentences.py "minha mãe nasceu na Inglaterra"

# Format numbers to Portuguese words
python3 practice_sentences.py --format "ele nasceu em 1933"
# Speaks: "ele nasceu em mil novecentos e trinta e três"

# Slow, clear pronunciation
python3 practice_sentences.py -s 100 -p 40 "eu gosto de estudar português"
```

### speak_phonemes.py
Direct phoneme practice (no venv needed):

```bash
# Practice specific phonemes
./speak_phonemes.py "k'az&"

# Compare word to phonemes
./speak_phonemes.py -c "casa"
```

## 🔧 Settings Guide

### Speed Control
- **80-100**: Very slow, for careful learning
- **100-120**: Slow, clear practice (recommended for beginners)
- **140**: Normal speech (default)
- **180+**: Faster speech

### Pitch Control
- **0-25**: Lower pitch
- **35**: Normal (default)
- **50-99**: Higher pitch

### Whisper Models
- **tiny**: Fastest, least accurate
- **base**: Good balance (default, recommended)
- **small**: Better accuracy, slower
- **medium**: High accuracy, slower
- **large**: Best accuracy, slowest

## 📚 Documentation

- **[APP-GUIDE.md](APP-GUIDE.md)** - Complete practice app guide
- **[QUICKSTART-SPEECH-RECOGNITION.md](QUICKSTART-SPEECH-RECOGNITION.md)** - Speech recognition setup
- **[SPEECH-RECOGNITION.md](SPEECH-RECOGNITION.md)** - Detailed usage guide
- **[PHONEME-REFERENCE.md](PHONEME-REFERENCE.md)** - eSpeak phoneme codes
- **[IPA-SOLUTION.md](IPA-SOLUTION.md)** - Understanding eSpeak's phoneme system
- **[LOCAL-BUILD.md](LOCAL-BUILD.md)** - Build instructions for macOS

## 🎓 Learning Tips

1. **Start Slow**: Use speed 100 until comfortable
2. **Daily Practice**: 10-15 minutes daily is better than long irregular sessions
3. **Track Progress**: Review statistics regularly to see improvement
4. **Progressive Difficulty**: Words → Phrases → Sentences
5. **Use History**: Review past mistakes in Session History
6. **Batch Practice**: Use text files for systematic vocabulary building

## 🛠️ Technical Details

### Built With
- **eSpeak NG 1.52-dev**: Text-to-speech engine with Brazilian Portuguese voice
- **Whisper AI**: OpenAI's speech recognition model
- **pcaudiolib**: Audio output library
- **sonic**: Audio speed adjustment
- **sounddevice/soundfile**: Python audio recording

### Requirements
- macOS (built with MacPorts libraries)
- Python 3.9+ with virtual environment
- ffmpeg (for Whisper audio processing)
- Microphone for speech recognition

### Installation
See [LOCAL-BUILD.md](LOCAL-BUILD.md) for complete build instructions.

## 🌟 Features Highlight

### What Makes This Special

1. **Phoneme-Level Feedback**: See exactly which sounds you got right/wrong
2. **Brazilian Portuguese Focus**: Default voice is pt-br, optimized for Brazilian pronunciation
3. **Smart Duration**: Auto-calculates recording time based on text length
4. **Persistent Everything**: Settings, history, progress - all saved automatically
5. **Multiple Interfaces**: Interactive app or individual command-line tools
6. **Complete Privacy**: All data stored locally, nothing uploaded

### The [[brackets]] Secret

eSpeak requires special `[[phoneme]]` notation for direct phoneme input. The tools handle this automatically, but if you're curious, see [IPA-SOLUTION.md](IPA-SOLUTION.md).

## 🎉 Success Stories

> "I just achieved 100% phoneme match with a short sentence!" - Original developer

The system provides immediate, accurate feedback that helps you improve quickly. Track your progress from first attempts to perfect matches!

## 📖 Example Session

```
$ ./practice_app.py

🇧🇷 BRAZILIAN PORTUGUESE PRONUNCIATION PRACTICE

1. Quick Practice (word/phrase)
Choose option: 1

Enter word or phrase to practice: casa
[eSpeak speaks: "casa"]
Recording... 3 seconds
[You speak: "casa"]

✅ Target:     casa
✅ Recognized: casa
✅ Phonemes:   k'az& = k'az&

🎉 PERFECT MATCH! Well done!

Choose option: 4

📊 PRACTICE STATISTICS
🔵 Current Session:
  Practices: 1
  Perfect: 1 (100.0%)
  Avg Similarity: 100.0%
```

## 🤝 Contributing

This is a personal learning project focused on Brazilian Portuguese pronunciation training. The main eSpeak NG project is at https://github.com/espeak-ng/espeak-ng.

## 📄 License

eSpeak NG is licensed under GPL v3+. See the original [README](README.original.md) for full eSpeak NG documentation.

---

**🇧🇷 Boa sorte com seus estudos de português!**
