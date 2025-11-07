# 🎉 Practice App Quick Start

Congratulations on your progress! Here's your new interactive practice app.

## Launch the App

```bash
source venv/bin/activate
./practice_app.py
```

## First Time Setup

1. When the menu appears, choose **6. Settings**
2. Recommended settings for beginners:
   - Speed: `100` (slower, clearer)
   - Pitch: `40` (slightly higher)
   - Voice: `pt-br` (Brazilian Portuguese - default)
   - Model: `base` (good balance - default)
   - Duration: `4` or `5` (recording time in seconds)

3. Settings are saved automatically - you won't need to do this again!

## Quick Practice Session

1. Choose **1. Quick Practice**
2. Enter a word: `casa`
3. Listen to the pronunciation
4. Press Enter when ready
5. Speak into your microphone
6. Get instant feedback!

## Your Progress is Tracked

Every practice session is saved with:
- ✅ What you practised
- ✅ What you said
- ✅ Phoneme comparison
- ✅ Match percentage
- ✅ Timestamp

View your statistics anytime with **4. View Statistics**

## Practice Modes

### Quick Practice (Option 1)
Perfect for single words or short phrases:
```
casa
gato
bom dia
muito obrigado
```

### Sentence Practice (Option 2)
Automatically calculates recording time:
```
minha mãe nasceu na Inglaterra
o gato está dormindo na cama
eu gosto muito de estudar português
```

### Practice from File (Option 3)
Use the included `sample_practice.txt` or create your own:
```
# My word list
casa
gato
água
pão
café
```

## Reviewing Your Progress

### View Statistics (Option 4)
See your improvement over time:
- Perfect match count
- Average similarity scores
- Session history

### Session History (Option 5)
Review past practices:
- See exactly what you practiced
- Review your phoneme attempts
- Identify patterns and problem areas

## Tips for Success

1. **Practice Daily**: 10-15 minutes is better than long irregular sessions
2. **Start Slow**: Use speed 100 until comfortable
3. **Track Progress**: Check your stats regularly to see improvement
4. **Use Word Lists**: Create text files for systematic vocabulary building
5. **Review History**: Learn from past mistakes

## Example First Session

```
$ ./practice_app.py

Choose option: 6
Speed [140]: 100
Pitch [35]: 40
[other settings: just press Enter]

Choose option: 1
Enter word: casa
[Listen → Speak → Get feedback]

Choose option: 1
Enter word: gato
[Practice again]

Choose option: 4
[View your statistics]

Choose option: 8
[Save and exit]
```

## Your Data Files

Created automatically in the espeak-ng directory:

- **practice_config.json** - Your saved settings
- **practice_history.json** - All your practice sessions
- **practice_audio/** - Audio recordings (future feature)

These files are NOT tracked in git (they're personal to you).

## Command Line Alternatives

If you prefer the command line:

```bash
# Quick word practice
python3 pronunciation_trainer.py --speed 100 --pitch 40 "casa"

# Sentence practice with auto-duration
python3 practice_sentences.py -s 100 -p 40 "minha mãe nasceu"

# Direct phoneme practice (no venv needed)
./speak_phonemes.py "k'az&"
```

## Complete Documentation

- **[APP-GUIDE.md](APP-GUIDE.md)** - Full app guide
- **[README-PT-BR.md](README-PT-BR.md)** - Project overview
- **[SPEECH-RECOGNITION.md](SPEECH-RECOGNITION.md)** - Detailed usage guide

---

## 🎊 Celebrate Your Success!

You achieved a 100% phoneme match! The practice app will help you:
- Build on that success consistently
- Track your improvement over time
- Practice efficiently with saved settings
- Review and learn from every session

**Boa sorte e divirta-se praticando! 🇧🇷**
