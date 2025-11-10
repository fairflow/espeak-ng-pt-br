# Portuguese Pronunciation Trainer - User Guide

**Version 0.9.2** | Last Updated: November 2025

Welcome! This guide will help you practice Brazilian Portuguese pronunciation using speech recognition and instant feedback.

---

## 📱 Quick Start

### How to Access the App

**Online (Recommended):**

- Open your web browser (Safari, Chrome, Firefox, etc.)
- Visit: **https://miolingo.streamlit.app/**
- 💡 **Tip:** Bookmark this page or add to home screen!

**Running Locally:**

- Open terminal in the project directory
- Run: `streamlit run app.py`
- Opens at `http://localhost:8501`

---

## 🎯 How to Practice

The app has **three main tabs**: Quick Practice, Statistics, and History.

### Tab 1: 🎯 Quick Practice

This is where you practice! The app supports two modes:

#### Mode A: Free Practice (Type Anything)

Perfect for beginners or casual practice.

**Steps:**

1. Go to the **🎯 Quick Practice** tab
2. **Type a word or phrase** in the text box
   - Example: `Bom dia` (Good morning)
   - Example: `Como você está?` (How are you?)
3. **Listen to target pronunciation** 🎯
   - Click the play button under "Target pronunciation"
   - You can replay as many times as you need
4. **Record yourself** 🎙️
   - Click the "Click to record" button
   - **Wait for the recording icon to turn RED** before speaking
   - Speak the phrase clearly into your microphone
   - Recording stops automatically after detecting silence
5. **Check your result** ✅
   - Click "Check Pronunciation" button
   - Wait a few seconds for AI processing
   - See your score and detailed feedback!
6. **Practice again**
   - Click "🔄 Clear Recording" to try the same phrase again
   - Or type a new phrase to practice something different

---

#### Mode B: Guided Practice (With a Phrase List)

Structured practice with a prepared list of phrases. Perfect for systematic learning!

**Creating Your Own List:**

1. **Prepare a text file** (`.txt` format):
   - One phrase per line
   - Simple format: `Bom dia`
   - Enhanced format: `Bom dia | Good morning` (with translation)
   - Advanced format: `Bom dia | Good morning | [bõ ˈd͡ʒi.ɐ]` (with IPA)

2. **Import your list:**
   - In the Quick Practice tab, expand **"📁 Import Phrase List"**
   - Click "Choose a text file"
   - Select your `.txt` file
   - The app shows how many phrases were loaded

**Try a Sample List:**

Want to get started quickly? Download this sample file with translations:
- **[practice_phrases_with_translations.txt](https://github.com/fairflow/espeak-ng-pt-br/raw/main/practice_phrases_with_translations.txt)** (21 phrases with English translations and IPA)
- Right-click → Save As, then import it in the app
- *Note: This file has some unusual phrases—we're working on a better beginner list!* 😊
**Practicing with Guided Mode:**

Once a phrase list is loaded, the interface changes:

- **Progress bar** shows your position (e.g., "Phrase 3 of 20")
- **Current phrase** displays in large, bold text
- **Navigation buttons:**
  - ⬅️ **Previous** - Go back to previous phrase
  - **Next** ➡️ - Move to next phrase
  - ✏️ **Edit** - Temporarily modify or replace the current phrase
- **Translation/IPA** (if provided in your file) - Expand to see
- **Clear Phrase List** button (in the import section) - Removes the list

**Practice workflow:**

1. Read the displayed phrase
2. Click translation/IPA expander if you need help
3. Listen to target pronunciation (same as free mode)
4. Record yourself
5. Check pronunciation
6. Review feedback
7. Use **Next ➡️** to move to the next phrase
8. Use **⬅️ Previous** if you want to repeat a phrase

**Edit Mode:**

- Click ✏️ **Edit** button to temporarily type your own phrase
- Practice that custom phrase
- Click **📚 Back to List Mode** to return to guided practice
- Note: Navigation buttons are disabled in edit mode to prevent confusion

---

### Tab 2: 📊 Statistics

View your practice performance and track progress.

**Current Session:**

- **Practices** - How many times you've practiced in this session
- **Perfect** - How many got 100% match
- **Avg Similarity** - Your average score

**All Time:**

- **Total Practices** - All-time practice count across all sessions
- **Total Perfect** - All-time perfect matches
- **Overall Avg** - Average score across all sessions
- **Sessions** - Number of saved practice sessions

---

### Tab 3: 📜 History

Review your past practice sessions (last 10 sessions shown).

Each session shows:

- Date
- Number of practices
- Number of perfect matches
- Expand to see details of each practice:
  - Target phrase vs what you said
  - Target phonemes (eIPA) vs your phonemes
  - Score percentage

---

## ⚙️ Settings (Sidebar)

All settings are in the left sidebar.

### Voice Settings

**Speed (wpm):** 80-450

- Lower = slower speech (easier for beginners)
- Higher = faster, natural speech
- Default: 140

**Pitch:** 0-99

- Adjusts voice pitch
- Default: 35

**Voice:**

- `pt-br` = Brazilian Portuguese (default)
- `pt` = European Portuguese

### 🎙️ Speech Recognition

**ASR Engine:**

- **Whisper** (default) - Multilingual model, supports 99 languages
- **wav2vec2** - Portuguese-specific model, may be more accurate for Portuguese

**Whisper Model Size** (only visible when Whisper is selected):

- **tiny** - Fastest, least accurate
- **base** - Good balance (default)
- **small** - More accurate, slower
- **medium** - Very accurate, much slower
- **large** - Most accurate, very slow

**Scoring Algorithm:**

- **edit_distance** (recommended) - Handles insertions/deletions/substitutions intelligently
- **positional** - Simple character-by-character matching (legacy)

### 🎚️ Audio Processing

**Silence Trim Threshold:** 0.001-0.1

- Controls how aggressively silence is removed from recordings
- **Lower values** (e.g., 0.001) = more aggressive trimming (may cut end of speech)
- **Higher values** (e.g., 0.05) = keep more audio (may include background noise)
- Default: 0.01
- 💡 If the app is cutting off your words, increase this value

**Use WAV audio format:**

- Check this if audio doesn't play on your device
- Specifically needed for iOS Safari compatibility
- Converts MP3 to WAV (slightly larger files, better compatibility)
- Setting is auto-saved when you toggle the checkbox

**💾 Save Settings button:**

- Click this to permanently save your other settings
- WAV audio setting saves automatically

### 📊 Current Session

Shows your current practice statistics:

- **Practices** - Number of practices in current session
- **Perfect** - Number of perfect matches
- **Warning** - Shows if you have unsaved practices
- **💾 Save Session Now** button - Manually save your current session

### 🧪 CCS Testing (Advanced)

For keen users who want to help test the app:

- Toggle to enable testing mode
- Allows validation of app behavior and state
- See [Testing Guide](TESTING_GUIDE.md) for details
- No coding required!

---

## 📊 Understanding Your Results

After checking your pronunciation, you'll see:

### Score Display

- **Perfect Match** 🎉 - Text and phonemes are identical! Well done!
- **Score: XX%** 📊 - Similarity percentage (higher is better)
- **Edit Distance: X** - Number of character edits needed to match target (lower is better)

### Target vs Your Pronunciation

**Left column (Target):**

- Text - The phrase you're practicing
- eIPA - Phonetic transcription using eSpeak notation
- IPA - International Phonetic Alphabet (if available)
- 🔊 Audio - Play target pronunciation (Google TTS)

**Right column (Your Pronunciation):**

- Recognized - What the AI heard you say
- eIPA - Phonetic transcription of your pronunciation
- IPA - Your pronunciation in IPA (if available)
- Status messages:
  - ✅ "Phonemes match perfectly" - Excellent!
  - ⚠️ "Different words recognized" - Try speaking more clearly
  - ℹ️ "Excellent pronunciation!" - High score, minor differences only

### 🔍 Detailed Phoneme Analysis

Check the "Show detailed phoneme analysis" box to see:

- Which algorithm was used (edit_distance or positional)
- Edit distance count
- Normalized phonemes (spaces removed for comparison)
- Visual comparison showing exactly what differs:
  - Matches
  - Substitutions (wrong character)
  - Insertions (extra character)
  - Deletions (missing character)

### 🔊 Compare Phoneme Sounds

Below the results, you can:

- Play eSpeak audio for individual phonemes
- Compare target phonemes vs your phonemes side-by-side
- Hear exactly which sounds you need to work on

---

## 💡 Tips for Best Results

### Recording Tips

1. **Wait for RED** - Don't start speaking until the recording icon turns red
2. **Speak clearly** - Enunciate each word
3. **Quiet environment** - Background noise affects recognition
4. **Good microphone** - Use earbuds/headset mic if available
5. **Normal pace** - Don't speak too fast or too slow
6. **One phrase per recording** - Don't practice multiple phrases in one recording

### Learning Tips

1. **Start simple** - Begin with short phrases like "Bom dia", "Obrigado"
2. **Listen multiple times** - Play target audio 2-3 times before recording
3. **Focus on phonemes** - Use the detailed analysis to identify specific sounds to improve
4. **Repeat imperfect scores** - If you get <90%, try again immediately
5. **Use guided mode** - Create a phrase list to practice systematically
6. **Track progress** - Check Statistics tab regularly to see improvement
7. **Adjust settings** - Slow down speech speed if you're struggling

### Troubleshooting

**Audio doesn't play:**

- ✅ Enable "Use WAV audio format" in settings (iOS Safari)
- Check device volume and browser permissions

**Recording not working:**

- Grant microphone permissions to your browser
- Try refreshing the page
- Check browser console for errors

**Recognition is inaccurate:**

- Speak more clearly and slowly
- Reduce background noise
- Try different microphone (earbuds often work better)
- Increase silence threshold if words are being cut off
- Try wav2vec2 engine for Portuguese-specific recognition

**App is slow:**

- Use smaller Whisper model (tiny or base)
- Close other browser tabs
- Wait for model to load on first use (can take 30 seconds)

**Different words recognized:**

- Slow down your speech
- Emphasize each syllable
- Check if you're pronouncing nasal vowels correctly (ã, õ, etc.)
- Listen to target audio more carefully

---

## 🔒 Privacy & Data

- **All processing happens locally** when using Whisper (default)
- Recordings are not saved or uploaded anywhere
- Practice history is stored locally in your browser
- wav2vec2 engine may use HuggingFace servers for model inference

---

## 🐛 Found a Bug or Have Feedback?

We'd love to hear from you!

**Email:** matthew@fairflow.co.uk

**Discord:** [Link will be added soon]

**GitHub Issues:** For technical users

See the [Testing Guide](TESTING_GUIDE.md) for how to report bugs effectively.

---

## 📚 Additional Resources

- **[Testing Guide](TESTING_GUIDE.md)** - Help us test the app and report issues
- **[Developer Guide](DEVELOPER_GUIDE.md)** - Technical documentation for contributors
- **[Main README](../README.md)** - Project overview and setup

---

**Happy practicing! 🇧🇷 Boa sorte!**
