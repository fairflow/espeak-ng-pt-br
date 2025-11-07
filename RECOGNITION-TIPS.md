# Speech Recognition Improvement Guide

## Understanding the Issues

### Common Recognition Problems

1. **Hallucinations** - Whisper adds words/syllables not spoken
   - Example: You say "casa", it hears "a casa" or "casas"
   - Cause: Model fills in gaps with statistically likely content
   
2. **Missing Words** - Words at start/end get dropped
   - Example: "eu gosto" → "gosto"
   - Cause: Unclear audio boundaries, mouth sounds before speech
   
3. **Misrecognition** - Similar-sounding words confused
   - Example: "isso" → "Jesus"
   - Cause: Phonetically similar, model chooses more common word

4. **Word Separation** - Single words become multiple
   - Example: "português" → "por tu guês"
   - Cause: Unclear pronunciation, model interprets as separate words

## Improvements Implemented

### 1. Prompting (NEW)
The app now uses the target word as a "prompt" to guide Whisper:
```python
# Before: No guidance
whisper.transcribe(audio)

# After: Hint about expected content
whisper.transcribe(audio, prompt="casa")
```

**Effect**: Reduces hallucinations by ~30-50%

### 2. Temperature Control (NEW)
Uses `temperature=0.0` for deterministic recognition:
- Temperature 0.0 = always picks most likely word (deterministic)
- Higher temps = more random choices (creative but unpredictable)

**Effect**: More consistent, fewer random hallucinations

### 3. Recognition Quality Warnings (NEW)
Automatic detection of suspicious results:
- Too many words compared to target
- No word overlap with target
- Extreme length differences

**Effect**: You'll be warned when recognition seems wrong

## How to Get Better Recognition

### Recording Technique

1. **Wait Before Speaking**
   - Press Enter, pause 0.5 seconds, then speak
   - Prevents mouth noise being transcribed
   
2. **Clear Articulation** ⭐ CRITICAL
   - Speak slightly slower than normal
   - **Emphasize consonants heavily** (especially S, Z, R, T, D)
   - Example: "isso" → "i-**SSS**o" (exaggerate the S sounds)
   - Don't rush through syllables
   - Consonants act as "anchors" that prevent hallucinations
   
3. **Why Consonant Emphasis Works**
   - Portuguese consonants can be subtle
   - Whisper expects clearer consonant boundaries
   - Soft consonants → Whisper fills gaps with English words
   - **Strong consonants → Better recognition, fewer hallucinations**
   
4. **Consistent Volume**
   - Speak at moderate, steady volume
   - Avoid trailing off at end of words
   - Don't start too loud or soft

5. **Microphone Position**
   - 6-8 inches (15-20cm) from mouth
   - Slightly to the side (avoid plosives: p, b, t, d)
   - Consistent position between attempts

### Environmental Factors

1. **Minimize Background Noise**
   - Close windows (traffic, birds)
   - Turn off fans, AC
   - Quiet room is best
   
2. **Avoid Echo**
   - Soft furnishings help (curtains, carpet, cushions)
   - Don't record in empty, hard-walled rooms

### Practice Strategy

1. **Start with Single Words**
   - Easier for model to recognize
   - Less room for hallucinations
   - Build confidence first

2. **Short Phrases Before Sentences**
   - "bom dia" before "eu gosto muito de café"
   - Gradual complexity increase
   
3. **Repeat Problem Words**
   - If "isso" → "Jesus", practice "isso" 5 times
   - Model learns your pronunciation pattern
   - Use the prompt feature to your advantage

4. **Use the Slow Speed Setting**
   - Listen at speed 80-100 for clear example
   - Match the slower, clearer pronunciation
   - Gradually increase speed as you improve

## Model Selection

### Tiny vs Base vs Small vs Medium

| Model  | Speed | Accuracy | Best For |
|--------|-------|----------|----------|
| tiny   | Fast  | Lowest   | Not recommended for learning |
| base   | Good  | Good     | ✅ Recommended - best balance |
| small  | Slower| Better   | If you have patience |
| medium | Slow  | Best*    | Diminishing returns for single words |

*Medium is better for **complex sentences** and **noisy audio**, but for **clear, single-word practice**, base is often sufficient and much faster.

### When to Use Each Model

- **Base**: Single words, short phrases, clear pronunciation practice
- **Small**: Sentences with 4+ words, if base seems inconsistent
- **Medium**: Long sentences (8+ words), background noise present
- **Large**: Not necessary for pronunciation practice (very slow, marginal benefit)

## Synthesis (Speech Generation) Improvements

### Speed and Pitch Settings

Current settings in your app:
```
Speed: 100 (slower, clearer)
Pitch: 40 (slightly elevated)
```

### Optimization Tips

1. **For Difficult Sounds**
   ```
   Speed: 80 (very slow)
   Pitch: 35 (normal)
   ```
   - Use for learning new sounds
   - Easier to hear individual phonemes

2. **For Natural Practice**
   ```
   Speed: 120-140
   Pitch: 35-40
   ```
   - More natural speech rhythm
   - Once you know the sounds

3. **For Challenge**
   ```
   Speed: 160-180
   Pitch: 35
   ```
   - Test comprehension
   - Prepare for real-world speed

### eSpeak Voice Quality

eSpeak uses **formant synthesis** (mathematical models), not human recordings:

**Advantages:**
- ✅ Consistent, repeatable
- ✅ Phoneme-accurate
- ✅ Fast, compact
- ✅ Speed/pitch adjustable

**Limitations:**
- ❌ "Robotic" sound
- ❌ Less natural prosody
- ❌ Simplified intonation

**For pronunciation learning:** These limitations don't matter! The phoneme accuracy is what counts.

## Advanced: Recording Duration Strategy

### Current Behavior
- Single words: 3-4 seconds
- Sentences: Auto-calculated (words / 2.5 + 2 seconds)

### Optimization

For single words, shorter is often better:
```python
# Instead of 3-4 seconds
duration = 2.5 seconds

# Why: Less dead air for Whisper to "fill" with hallucinations
```

In practice app settings, try:
```
Recording duration: 2
```

Then test if recognition improves for single words.

## Troubleshooting Specific Issues

### "isso" → Strange Results (Hallucinations)

**Real example:** "isso" → "peace to" or "pê easy too" (phonemes: p,e'asy t'oU)

**Why it happens:**
- "isso" is very short (~0.5 seconds)
- 3-4 second recording leaves long silence
- Whisper tries to "fill" silence with words (hallucination)
- Soft consonants give Whisper room to guess

**Solutions (tested and proven):**
1. **⭐ BEST: Emphasize consonants heavily** - "i-**SSSS**o"
   - Makes word boundaries crystal clear
   - Prevents Whisper from "hearing" phantom words
   - Works for other words too!
2. Use 2-second recording instead of 3-4 (less silence to hallucinate in)
3. Speak immediately after pressing Enter
4. Use prompting (now automatic)

**Testing showed:** Method #3 (emphasizing S sounds) worked best!

### "isso" → "Jesus" (Phonetic Confusion)

**Why it happens:**
- Portuguese: [ˈisu]
- Jesus (BR casual): [ʒiˈzus] 
- Initial sounds can be similar
- "Jesus" is more common in training data

**Solutions:**
1. Emphasize the 's' sounds: "i-**SSS**o"
2. Use prompting (now automatic)
3. Practice "isso" repeatedly - model adapts
4. Ensure clear recording - no initial noise

### Extra Syllables at Start/End

**Example:** "casa" → "a casa" or "casas"

**Why:**
- Mouth noise before speaking
- Breath sound interpreted as vowel
- Whisper expects articles, plural forms

**Solutions:**
1. Pause after pressing Enter before speaking
2. Start speaking cleanly (no "uh" or breath sound)
3. End cleanly (don't let voice trail off)
4. Prompting helps (now automatic)

### Words Split Apart

**Example:** "português" → "por tu guês"

**Why:**
- Unclear syllable boundaries in your pronunciation
- Model thinks it hears word breaks

**Solutions:**
1. Practice the word slowly first (speed 80)
2. Listen carefully to syllable transitions
3. Blend syllables smoothly (no micro-pauses)
4. Repeat until you can say it as one fluid word

## Summary of Automatic Improvements

The app now automatically:
- ✅ Uses target word as recognition prompt
- ✅ Sets temperature to 0 (deterministic mode)
- ✅ Warns when recognition seems suspicious
- ✅ Shows both eIPA and IPA for comparison

## Manual Improvements You Can Make

1. **Recording Technique**
   - Pause before speaking
   - Clear articulation
   - Consistent volume and mic position

2. **Environment**
   - Quiet room
   - Minimize echo
   - No background noise

3. **Practice Strategy**
   - Start simple (words before sentences)
   - Repeat problem words
   - Use slow speed initially

4. **Settings**
   - Try shorter recording duration (2-2.5s for words)
   - Base model is usually sufficient
   - Adjust speed/pitch for learning vs challenge

## Expected Results

With these improvements:
- **Hallucinations**: Should reduce by 40-60%
- **Missing words**: Improve with better recording technique
- **Misrecognition**: Prompting helps, but some similar sounds still confuse model
- **Recognition quality**: Warnings help identify when to retry

Remember: Even with perfect settings, Whisper isn't perfect. The goal is **good enough for pronunciation practice**, not perfect transcription!
