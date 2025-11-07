# Quick Start: Brazilian Portuguese Speech Recognition Training

## Your Use Case

You're building a tool that:
1. Recognizes your attempts to speak Brazilian Portuguese
2. Transcribes to eSpeak phoneme codes
3. Speaks it back to you
4. Compares with correct pronunciation

## Setup Complete ✓

- Brazilian Portuguese (`pt-br`) is now the **default voice**
- eSpeak phoneme codes work with `[[...]]` notation
- Helper tools ready to use

## Basic Usage

### 1. Speak Phoneme Codes (from your speech recognizer)

```bash
# Your speech recognizer outputs: k'az&
python3 speak_phonemes.py "k'az&"
```

### 2. Get Correct Phonemes for a Word

```bash
python3 speak_phonemes.py -c "casa"

# Output:
# Word:     casa
# Phonemes: k'az&
# IPA:      kˈazɐ
# [Speaks the word]
```

### 3. Compare Your Pronunciation

```bash
# Your attempt (phonemes from speech recognizer): k'az&
# Correct word: casa

python3 speak_phonemes.py "k'az&" -C "casa"

# This will:
# - Show correct vs your phonemes
# - Speak correct version
# - Speak your version
# - Tell you if they match
```

## Workflow Example

```bash
# Step 1: Get target phonemes
python3 speak_phonemes.py -c "obrigado"
# Output: ,obRig'adU

# Step 2: You speak "obrigado" → your speech recognizer outputs phonemes

# Step 3: Compare
python3 speak_phonemes.py "obRig'adU" -C "obrigado"

# Step 4: Practice until match!
```

## Common Commands

```bash
# Speak phoneme codes directly
python3 speak_phonemes.py "k'az&"

# Get phonemes for multiple words
python3 speak_phonemes.py -c "casa água tempo"

# Compare your pronunciation
python3 speak_phonemes.py "YOUR_PHONEMES" -C "target_word"

# Use European Portuguese instead
python3 speak_phonemes.py -v pt "k'az&"

# Slower, clearer pronunciation
python3 speak_phonemes.py -s 140 -p 35 "k'az&"

# Show IPA alongside phonemes
python3 speak_phonemes.py -c "casa" --ipa
```

## Direct eSpeak Usage

```bash
# Speak Portuguese text (Brazilian by default)
./local/bin/run-espeak-ng "Bom dia"

# Get phoneme codes
./local/bin/run-espeak-ng -x "casa"
# Output: k'az&

# Speak phoneme codes
./local/bin/run-espeak-ng "[[k'az&]]"

# Override default voice
./local/bin/run-espeak-ng -v pt "Olá"  # European Portuguese

# Or set environment variable
export ESPEAK_DEFAULT_VOICE=pt
./local/bin/run-espeak-ng "Olá"
```

## Integration Example

```python
#!/usr/bin/env python3
import subprocess

def get_correct_phonemes(word, voice="pt-br"):
    """Get eSpeak phonemes for a Brazilian Portuguese word"""
    result = subprocess.run(
        ["./local/bin/run-espeak-ng", "-v", voice, "-x", "-q", word],
        capture_output=True, text=True
    )
    return result.stdout.strip()

def speak_phonemes(phoneme_codes, voice="pt-br"):
    """Speak eSpeak phoneme codes"""
    subprocess.run([
        "./local/bin/run-espeak-ng",
        "-v", voice,
        f"[[{phoneme_codes}]]"
    ])

def compare_pronunciation(user_phonemes, correct_word, voice="pt-br"):
    """Compare user pronunciation with correct"""
    correct_phonemes = get_correct_phonemes(correct_word, voice)
    
    print(f"Target: {correct_word}")
    print(f"Correct phonemes: {correct_phonemes}")
    print(f"Your phonemes:    {user_phonemes}")
    print(f"Match: {user_phonemes == correct_phonemes}")
    
    # Speak both
    print("\nCorrect:")
    subprocess.run(["./local/bin/run-espeak-ng", "-v", voice, correct_word])
    
    print("Your version:")
    speak_phonemes(user_phonemes, voice)

# Usage in your speech recognition tool:
user_phonemes_from_recognizer = "k'az&"  # Your speech recognizer output
compare_pronunciation(user_phonemes_from_recognizer, "casa")
```

## Phoneme Reference

See `PHONEME-REFERENCE.md` for complete phoneme codes.

### Common Brazilian Portuguese Phonemes

```python
# Vowels
'&'   # a/ɐ  - casa
'E'   # ɛ    - pé
'e'   # e    - tempo
'i'   # i    - filho
'O'   # ɔ    - avó
'o'   # o    - bom
'U'   # u    - tudo

# Consonants
'k'   # k    - casa
'z'   # z    - casa (s between vowels)
'S'   # ʃ    - chá
'Z'   # ʒ    - já
'R'   # ɾ    - caro (tap)
'h'   # h/x  - rato (r at start)
'J'   # ɲ    - ninho
'L|'  # ʎ    - filho

# Stress
"'"   # Primary stress (before syllable)
","   # Secondary stress
```

### Example Words

```bash
casa      → k'az&
água      → 'agw&
tempo     → t'eImpU
pessoa    → p,es'o&
obrigado  → ,obRig'adU
sim       → s'i~
não       → n'&~U~
```

## Files Created

- **speak_phonemes.py** - Main tool for speaking and comparing phonemes
- **PHONEME-REFERENCE.md** - Complete phoneme code reference
- **local/bin/run-espeak-ng** - Wrapper with pt-br default
- **IPA-SOLUTION.md** - Background on IPA vs phoneme codes

## Tips

1. **For speech recognition**: Capture audio, convert to phoneme codes, use `speak_phonemes.py` to hear and compare

2. **Phoneme tolerance**: You may want to ignore stress markers (`'` and `,`) for basic matching

3. **Pronunciation feedback**: Use `-s` and `-p` flags to adjust speed and pitch for clearer practice

4. **Save audio files**: Use `./local/bin/run-espeak-ng -w output.wav "text"` to save reference pronunciations

## Next Steps

1. Integrate `speak_phonemes.py` with your speech recognizer
2. Build vocabulary list with correct phonemes
3. Create practice sessions with immediate feedback
4. Track progress (% correct phonemes over time)

Good luck with your Brazilian Portuguese pronunciation training! 🇧🇷
