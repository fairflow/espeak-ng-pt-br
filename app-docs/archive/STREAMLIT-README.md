# Streamlit Web Interface for Portuguese Pronunciation Practice

## Quick Start

1. **Activate virtual environment:**
```bash
source venv/bin/activate
```

2. **Run the Streamlit app:**
```bash
streamlit run streamlit_app.py
```

3. **Access the app:**
- The app will automatically open in your browser at `http://localhost:8501`
- Or manually navigate to the URL shown in the terminal

## Features

### 🎯 Quick Practice
- Practice single words or short phrases
- Instant feedback with phoneme comparison
- Shows both eIPA (eSpeak notation) and IPA transcription

### 📝 Sentence Practice
- Practice longer sentences
- Auto-calculates recording duration based on word count
- Same detailed feedback as quick practice

### 📂 File Practice
- Upload a text file with multiple words/phrases
- One item per line
- Lines starting with `#` are treated as comments
- Practice all items sequentially with progress tracking

### 📊 Statistics
- **Current Session**: Track your ongoing practice
- **All Time**: View cumulative statistics across all sessions
- Metrics include: practice count, perfect matches, average similarity

### 📜 History
- Review all previous practice sessions
- Expand any session to see detailed results
- Compare target vs. recognized text
- View phoneme differences for non-perfect matches

### ⚙️ Settings (Sidebar)
- **Speed**: Adjust speech rate (80-450 wpm)
- **Pitch**: Modify voice pitch (0-99)
- **Voice**: Choose pt-br (Brazilian) or pt (European)
- **Whisper Model**: Select AI model (tiny, base, small, medium, large)
- **Recording Duration**: Set default recording length (1-10 seconds)
- Settings persist between sessions

### Session Management
- Current session shows unsaved practice count
- Manual "Save Session Now" button
- All data persists in JSON files (same as CLI app)

## Tips for Best Results

1. **Emphasize consonants** when speaking - this dramatically improves recognition
2. **Use base model** for single words (good balance of speed and accuracy)
3. **2-3 seconds** works well for short words, 5+ for sentences
4. **Speak clearly** and minimize background noise

## Files Used

- `practice_config.json` - Your saved settings
- `practice_history.json` - All practice sessions
- `practice_audio/` - Recorded audio files

## Stopping the App

Press `Ctrl+C` in the terminal where Streamlit is running.

## Advantages Over CLI App

- ✅ No need to press Enter between practices
- ✅ Visual progress bars for file practice
- ✅ Side-by-side comparison of results
- ✅ Expandable session history
- ✅ Real-time settings adjustment
- ✅ Works on any device with a browser
- ✅ Can be deployed to the cloud (Streamlit Cloud, Heroku, etc.)

## Deployment (Optional)

To make the app accessible from other devices or deploy to the cloud:

### Local Network Access
```bash
streamlit run streamlit_app.py --server.address 0.0.0.0
```
Then access from other devices using your computer's IP address.

### Streamlit Cloud (Free)
1. Push your code to GitHub
2. Go to https://share.streamlit.io
3. Connect your repository
4. Deploy!

Note: Make sure to test audio recording permissions work in your deployment environment.
