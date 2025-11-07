# Brazilian Portuguese Phoneme Reference for Speech Recognition

## Quick Start

```bash
# Speak phoneme codes (from your speech recognizer)
python3 speak_phonemes.py "k'az&"

# Get correct phonemes for a word
python3 speak_phonemes.py -c "casa"

# Compare your pronunciation with correct
python3 speak_phonemes.py "k'az&" -C "casa"

# Process multiple words
python3 speak_phonemes.py -c "água tempo pessoa"
```

## eSpeak Phoneme Codes for Brazilian Portuguese

### Vowels

| Phoneme | IPA | Example Word | eSpeak Code | Example |
|---------|-----|--------------|-------------|---------|
| a       | a, ɐ | c**a**sa | `&` | `k'az&` |
| e (open)| ɛ   | p**é** | `E` | `p'E` |
| e (closed)| e | t**e**mpo | `e` | `t'eImpU` |
| i       | i   | f**i**lho | `i` | `f'iL|U` |
| o (open)| ɔ   | av**ó** | `O` | `av'O` |
| o (closed)| o | b**o**m | `o` | `b'om` |
| u       | u   | t**u**do | `U` | `t'UdU` |

### Diphthongs

| Phoneme | IPA | Example | eSpeak Code |
|---------|-----|---------|-------------|
| ai      | aj  | pai | `aI` |
| ei      | ej  | lei | `eI` |
| oi      | oj  | boi | `oI` |
| ui      | uj  | fui | `uI` |
| au      | aw  | mau | `aU` |
| eu      | ew  | meu | `eU` |

### Nasalized Vowels

| Phoneme | IPA | Example | eSpeak Code |
|---------|-----|---------|-------------|
| ã       | ɐ̃   | maçã | `&~` |
| ẽ       | ẽ   | bem | `e~` |
| õ       | õ   | bom | `o~` |

### Consonants

| Phoneme | IPA | Example | eSpeak Code |
|---------|-----|---------|-------------|
| p       | p   | **p**ai | `p` |
| b       | b   | **b**ola | `b` |
| t       | t   | **t**udo | `t` |
| d       | d   | **d**ia | `d` |
| k       | k   | **c**asa | `k` |
| g       | ɡ   | **g**ato | `g` |
| f       | f   | **f**azer | `f` |
| v       | v   | **v**er | `v` |
| s       | s   | **s**im | `s` |
| z       | z   | ca**s**a | `z` |
| ʃ       | ʃ   | **ch**á | `S` |
| ʒ       | ʒ   | **j**á | `Z` |
| m       | m   | **m**ãe | `m` |
| n       | n   | **n**ão | `n` |
| ɲ       | ɲ   | **nh**o | `J` |
| l       | l   | **l**ua | `l` |
| ʎ       | ʎ   | fi**lh**o | `L|` |
| ɾ       | ɾ   | ca**r**o | `R` |
| h/x     | h, x | **r**ato | `h` or `x` |
| w       | w   | q**u**atro | `w` |
| j       | j   | ma**i**o | `j` |

### Special Markers

- `'` = Primary stress (before stressed syllable)
- `,` = Secondary stress
- `_:` = Pause/syllable break

## Example Phoneme Codes

```python
# Common Brazilian Portuguese words with phoneme codes
words_phonemes = {
    "casa":      "k'az&",
    "água":      "'agw&",
    "tempo":     "t'eImpU",
    "pessoa":    "p,es'o&",
    "obrigado":  ",obRig'adU",
    "por favor": "por fav'or",
    "sim":       "s'i~",
    "não":       "n'&~U~",
    "bom dia":   "b'o~ dZ'i&",
    "boa noite": "b'o& n'oItSI",
}
```

## Workflow for Speech Recognition Training

### Step 1: Get Target Phonemes

```bash
# Get correct phonemes for word you want to practice
python3 speak_phonemes.py -c "obrigado" --ipa

# Output:
# Word:     obrigado
# Phonemes: ,obRig'adU
# IPA:      ˌobɾiɡˈadu
```

### Step 2: Practice Speaking

Record yourself saying "obrigado" and your speech recognizer produces phoneme codes.

### Step 3: Compare Your Pronunciation

```bash
# Your speech recognizer output: "obRig'adU" (example)
python3 speak_phonemes.py "obRig'adU" -C "obrigado"

# This will:
# 1. Show correct vs your phonemes
# 2. Speak the correct version
# 3. Speak your version
# 4. Tell you if they match
```

### Step 4: Hear Your Pronunciation

```bash
# Speak your phoneme codes back to you
python3 speak_phonemes.py "obRig'adU"

# Adjust and try again until it matches
```

## Integration with Your Speech Recognizer

```python
#!/usr/bin/env python3
"""
Example: Integrate with your speech recognition system
"""

import subprocess
from pathlib import Path

SPEAK_PHONEMES = Path(__file__).parent / "speak_phonemes.py"

def practice_word(target_word, voice="pt-br"):
    """
    Practice pronunciation of a Brazilian Portuguese word
    
    Args:
        target_word: The Portuguese word to practice
        voice: pt-br (Brazilian) or pt (European)
    """
    # Get correct phonemes
    result = subprocess.run(
        ["python3", str(SPEAK_PHONEMES), "-c", target_word, "-v", voice],
        capture_output=True, text=True
    )
    
    # Extract phoneme codes from output
    for line in result.stdout.split('\n'):
        if line.startswith("Phonemes:"):
            correct_phonemes = line.split(":", 1)[1].strip()
            break
    
    print(f"Practice saying: {target_word}")
    print(f"Target phonemes: {correct_phonemes}")
    
    # Here: Your speech recognizer captures audio and produces phonemes
    # For demo, let's simulate:
    user_phonemes = input("Your phonemes (from speech recognizer): ").strip()
    
    if not user_phonemes:
        print("No input, playing correct pronunciation...")
        subprocess.run(["python3", str(SPEAK_PHONEMES), "-c", target_word, "-v", voice])
        return
    
    # Compare
    subprocess.run([
        "python3", str(SPEAK_PHONEMES),
        user_phonemes, "-C", target_word,
        "-v", voice
    ])

# Example usage
if __name__ == "__main__":
    words_to_practice = ["casa", "água", "obrigado", "por favor"]
    
    for word in words_to_practice:
        practice_word(word, voice="pt-br")
        print("\n" + "="*60 + "\n")
```

## Batch Processing

### Create Training Set

```bash
# Create a file with words to practice
cat > practice_words.txt << EOF
casa
água
tempo
pessoa
obrigado
por favor
bom dia
boa noite
sim
não
EOF

# Get phonemes for all words
while read word; do
    echo "$word"
    python3 speak_phonemes.py -c "$word" --ipa
    echo ""
done < practice_words.txt > training_set.txt
```

### Save Audio Files

```bash
# Create audio files for each word
while read word; do
    python3 speak_phonemes.py -c "$word" -w "${word// /_}.wav"
done < practice_words.txt
```

## Tips for Speech Recognition

### 1. Phoneme Granularity

eSpeak phoneme codes are more detailed than you might need. You can:
- Ignore stress markers (`'` and `,`) for basic matching
- Group similar phonemes (e.g., `&` and `a` both represent 'a' sounds)

### 2. Tolerance for Variation

Brazilian Portuguese has dialectal variation:
```python
def phonemes_similar(phonemes1, phonemes2, ignore_stress=True):
    """Check if two phoneme strings are similar enough"""
    if ignore_stress:
        phonemes1 = phonemes1.replace("'", "").replace(",", "")
        phonemes2 = phonemes2.replace("'", "").replace(",", "")
    
    return phonemes1 == phonemes2
```

### 3. Syllable-by-Syllable Feedback

Break phonemes into syllables for detailed feedback:
```python
def compare_syllables(user_phonemes, correct_phonemes):
    """Compare syllable by syllable"""
    # Split on stress markers as syllable boundaries
    import re
    user_syllables = re.split(r"[',]", user_phonemes)
    correct_syllables = re.split(r"[',]", correct_phonemes)
    
    for i, (user, correct) in enumerate(zip(user_syllables, correct_syllables)):
        if user != correct:
            print(f"Syllable {i+1}: '{user}' should be '{correct}'")
```

## Quick Reference Commands

```bash
# Speak phoneme code
python3 speak_phonemes.py "k'az&"

# Get correct phonemes
python3 speak_phonemes.py -c "casa"

# Compare pronunciation
python3 speak_phonemes.py "k'az&" -C "casa"

# Batch process
python3 speak_phonemes.py -c "casa água tempo"

# Use European Portuguese instead
python3 speak_phonemes.py -v pt -c "casa"

# Adjust speed and pitch
python3 speak_phonemes.py -s 140 -p 35 "k'az&"

# Show IPA alongside phonemes
python3 speak_phonemes.py -c "casa" --ipa
```

## Resources

- eSpeak phoneme definitions: `phsource/phonemes` in this repo
- Brazilian Portuguese phonemes: Look at output of `-x` flag
- This tool: `speak_phonemes.py`
- Wrapper: `local/bin/run-espeak-ng`
