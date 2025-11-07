# Portuguese IPA to Speech - Working Solution

## The Problem

eSpeak-NG's `[[...]]` notation does **NOT** accept IPA directly - it expects eSpeak's internal phoneme codes. This is why you heard only clicks.

## The Solution

Since you're transliterating Portuguese to IPA, here are **practical workflows** that actually work:

### Option 1: Reverse Lookup (Recommended)

If your IPA transcriptions represent actual Portuguese words, find and speak the original words:

```bash
# Get IPA from Portuguese text
./local/bin/run-espeak-ng -v pt --ipa -q "casa"
# Output: kˈazɐ

# If your IPA matches, speak the original word
./local/bin/run-espeak-ng -v pt "casa"
```

**Using the helper script:**
```bash
# Compare your IPA with a Portuguese word
python3 ipa_to_espeak.py "kˈazɐ" --compare "casa"

# Get IPA for any Portuguese text
python3 ipa_to_espeak.py --text "Bom dia"
```

### Option 2: Create Portuguese Text from Your IPA

If you're generating IPA, you probably know the source Portuguese text. Use that:

```python
# Your transliterator probably does:
portuguese_text = "casa"
your_ipa = transliterate(portuguese_text)  # → "kˈazɐ"

# To hear it:
subprocess.run(["./local/bin/run-espeak-ng", "-v", "pt", portuguese_text])
```

### Option 3: Build IPA-to-Text Mapping

Create a reverse mapping from your IPA back to Portuguese orthography:

```python
#!/usr/bin/env python3
import subprocess

# Your IPA to Portuguese text mapping
ipa_to_text = {
    "kˈazɐ": "casa",
    "ʃˈuvɐ": "chuva",
    "pɔɾtuɣˈaɫ": "Portugal",
    # ... add your mappings
}

def speak_ipa(ipa, voice="pt"):
    """Speak IPA by looking up the Portuguese text"""
    if ipa in ipa_to_text:
        text = ipa_to_text[ipa]
        subprocess.run([
            "./local/bin/run-espeak-ng",
            "-v", voice, text
        ])
    else:
        print(f"Warning: No Portuguese text for IPA: {ipa}")

# Usage
speak_ipa("kˈazɐ")
```

### Option 4: Use eSpeak as IPA Reference

Use eSpeak to generate IPA, then speak the original text:

```bash
#!/bin/bash
# Process Portuguese text file

while read -r portuguese_text; do
    # Get IPA from eSpeak
    ipa=$(./local/bin/run-espeak-ng -v pt --ipa -q "$portuguese_text")
    
    echo "Text: $portuguese_text"
    echo "IPA:  $ipa"
    
    # Speak it
    ./local/bin/run-espeak-ng -v pt "$portuguese_text"
    
    # Save IPA for your records
    echo "$portuguese_text|$ipa" >> ipa_database.txt
done < portuguese_words.txt
```

## Why [[...]] Doesn't Work with IPA

The `[[...]]` syntax uses **eSpeak phoneme codes**, not IPA:

```bash
# This does NOT work (IPA):
./local/bin/run-espeak-ng "[[kˈazə]]"  # ❌ Just clicks

# This works (eSpeak phonemes):
./local/bin/run-espeak-ng -v pt -x "casa"  # Get codes: k'az&
./local/bin/run-espeak-ng "[[k'az&]]"      # ✓ Works!
```

eSpeak phoneme codes are different from IPA:
- IPA: `ɐ` → eSpeak code: `&`
- IPA: `ʃ` → eSpeak code: `S`  
- IPA: `ʒ` → eSpeak code: `Z`

## Practical Workflow for Your Use Case

Since you're transliterating Portuguese to IPA, here's what I recommend:

### Setup
```python
#!/usr/bin/env python3
"""
portuguese_ipa_speaker.py - Speak Portuguese IPA transcriptions
"""

import subprocess
from pathlib import Path

ESPEAK = Path(__file__).parent / "local/bin/run-espeak-ng"

class PortugueseIPASpeaker:
    def __init__(self, voice="pt"):
        self.voice = voice
        self.cache = {}  # Cache Portuguese text → IPA mappings
    
    def get_ipa(self, portuguese_text):
        """Get eSpeak's IPA for Portuguese text"""
        if portuguese_text not in self.cache:
            result = subprocess.run(
                [str(ESPEAK), "-v", self.voice, "--ipa", "-q", portuguese_text],
                capture_output=True, text=True
            )
            self.cache[portuguese_text] = result.stdout.strip()
        return self.cache[portuguese_text]
    
    def speak(self, portuguese_text, speed=160, pitch=40):
        """Speak Portuguese text"""
        subprocess.run([
            str(ESPEAK), "-v", self.voice,
            "-s", str(speed), "-p", str(pitch),
            portuguese_text
        ])
    
    def speak_with_ipa_display(self, portuguese_text):
        """Speak and show IPA"""
        ipa = self.get_ipa(portuguese_text)
        print(f"{portuguese_text:20} → {ipa}")
        self.speak(portuguese_text)
        return ipa
    
    def validate_ipa(self, your_ipa, portuguese_text):
        """Compare your IPA with eSpeak's"""
        espeak_ipa = self.get_ipa(portuguese_text)
        match = (your_ipa.replace(" ", "") == espeak_ipa.replace(" ", ""))
        return match, espeak_ipa

# Usage example
if __name__ == "__main__":
    speaker = PortugueseIPASpeaker(voice="pt")
    
    # Example 1: Speak Portuguese and show IPA
    speaker.speak_with_ipa_display("casa")
    speaker.speak_with_ipa_display("Portugal")
    
    # Example 2: Validate your IPA
    your_ipa = "kˈazɐ"
    match, espeak_ipa = speaker.validate_ipa(your_ipa, "casa")
    print(f"\nYour IPA:    {your_ipa}")
    print(f"eSpeak IPA:  {espeak_ipa}")
    print(f"Match:       {match}")
    
    # Example 3: Process a list
    words = ["água", "tempo", "pessoa", "obrigado"]
    for word in words:
        speaker.speak_with_ipa_display(word)
```

### Integration with Your Transliterator

```python
# Your existing transliterator
def portuguese_to_ipa(text):
    # Your transliteration logic
    return ipa_result

# Add speech capability
from portuguese_ipa_speaker import PortugueseIPASpeaker

speaker = PortugueseIPASpeaker()

portuguese_text = "casa"
your_ipa = portuguese_to_ipa(portuguese_text)  # Your IPA
espeak_ipa = speaker.get_ipa(portuguese_text)   # eSpeak's IPA

# Compare
if your_ipa == espeak_ipa:
    print("✓ IPA matches eSpeak")
else:
    print(f"⚠ Difference:")
    print(f"  Yours:   {your_ipa}")
    print(f"  eSpeak:  {espeak_ipa}")

# Speak it
speaker.speak(portuguese_text)
```

## Save Audio Files

If you want to save audio for your IPA transcriptions:

```bash
# Create audio files for a word list
while read portuguese_word; do
    # Get IPA
    ipa=$(./local/bin/run-espeak-ng -v pt --ipa -q "$portuguese_word")
    
    # Save audio
    filename="${portuguese_word}.wav"
    ./local/bin/run-espeak-ng -v pt -w "$filename" "$portuguese_word"
    
    # Log it
    echo "$portuguese_word|$ipa|$filename" >> audio_log.txt
    
    echo "Created: $filename → IPA: $ipa"
done < words.txt
```

## Key Takeaway

**You cannot directly speak IPA with eSpeak-NG** using the `[[...]]` notation. Instead:

1. ✓ **Keep the Portuguese text** alongside your IPA
2. ✓ **Speak the Portuguese text** (which sounds perfect)
3. ✓ **Display the IPA** for your users/documentation
4. ✓ **Use eSpeak's IPA** as a reference/validation for your transliterator

This way you get:
- Correct pronunciation (from Portuguese text)
- IPA transcription (from your transliterator or eSpeak)
- Audio output (from eSpeak speaking Portuguese text)

## Quick Commands

```bash
# Get IPA for Portuguese words
./local/bin/run-espeak-ng -v pt --ipa -q "palavra"

# Speak Portuguese (sounds good)
./local/bin/run-espeak-ng -v pt "palavra"

# Batch process with helper script
python3 ipa_to_espeak.py --text "Olá mundo"
python3 ipa_to_espeak.py "kˈazɐ" --compare "casa"

# Save to file
./local/bin/run-espeak-ng -v pt -w output.wav "Bom dia"
```
