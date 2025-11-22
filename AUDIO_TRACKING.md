# Audio Player Tracking in CCS Framework

## Problem Identified

The Streamlit app has **multiple audio players** active simultaneously, but the code reuses variable names (e.g., `audio_bytes`), making it difficult to track which audio source is which.

## Audio Types in the App

### During Practice Phase

1. **Target TTS (Practice Area)** - `AUDIO_PLAYER_TARGET_PRACTICE`
   - Location: Line ~809 in streamlit_app_v2.py
   - Purpose: User hears correct pronunciation before recording
   - Source: Google TTS of target text
   - Format: MP3

2. **User Live Recording** - `AUDIO_PLAYER_USER_LIVE`
   - Location: Line ~820
   - Purpose: Playback of just-recorded audio
   - Source: Streamlit audio_input widget
   - Format: WAV

### During Results Phase

3. **Target TTS (Results Panel)** - `AUDIO_PLAYER_TARGET_RESULTS`
   - Location: Line ~869
   - Purpose: Compare target pronunciation in results
   - Source: Google TTS (regenerated)
   - Format: MP3

4. **User Recording (Results Panel)** - `AUDIO_PLAYER_USER_RESULTS`
   - Location: Line ~960
   - Purpose: Review what was recorded
   - Source: Stored `result['user_audio_bytes']`
   - Format: WAV

5. **Recognized Text TTS** - `AUDIO_PLAYER_RECOGNIZED_TTS`
   - Location: Line ~966
   - Purpose: Hear what ASR system understood
   - Source: Google TTS of recognized text
   - Format: MP3
   - Condition: Only if recognized != target

### Phoneme Comparison (On-Demand)

6. **Correct Phonemes (eSpeak)** - `AUDIO_PLAYER_PHONEME_CORRECT`
   - Location: Line ~975 (button triggered)
   - Purpose: Hear correct phoneme pronunciation
   - Source: eSpeak TTS
   - Format: System audio (not stored)

7. **User Phonemes (eSpeak)** - `AUDIO_PLAYER_PHONEME_USER`
   - Location: Line ~982 (button triggered)
   - Purpose: Hear user's phoneme pronunciation
   - Source: eSpeak TTS of recognized text
   - Format: System audio (not stored)

## CCS Framework Enhancements

### Updated Enums

**UIElement** - Now tracks specific audio player types:
```python
AUDIO_PLAYER_TARGET_PRACTICE     # Target during practice
AUDIO_PLAYER_USER_LIVE           # Just recorded
AUDIO_PLAYER_TARGET_RESULTS      # Target in results
AUDIO_PLAYER_USER_RESULTS        # Recording in results
AUDIO_PLAYER_RECOGNIZED_TTS      # ASR recognized text
AUDIO_PLAYER_PHONEME_CORRECT     # Correct phonemes
AUDIO_PLAYER_PHONEME_USER        # User phonemes
```

**AppCapability** - Specific audio provision capabilities:
```python
PROVIDE_TARGET_AUDIO_PRACTICE
PROVIDE_USER_AUDIO_LIVE
PROVIDE_TARGET_AUDIO_RESULTS
PROVIDE_USER_AUDIO_RESULTS
PROVIDE_RECOGNIZED_AUDIO
PROVIDE_PHONEME_AUDIO_CORRECT
PROVIDE_PHONEME_AUDIO_USER
```

**UserIntent** - Specific audio listening intents:
```python
WANT_HEAR_TARGET_PRACTICE
WANT_HEAR_USER_LIVE
WANT_HEAR_TARGET_RESULTS
WANT_HEAR_USER_RESULTS
WANT_HEAR_RECOGNIZED
WANT_HEAR_PHONEME_CORRECT
WANT_HEAR_PHONEME_USER
```

## Port Matching Example

**Before** (ambiguous):
```python
UserIntent.WANT_HEAR_TARGET <-> AppCapability.PROVIDE_TARGET_AUDIO
# Which target? Practice or results?
```

**After** (explicit):
```python
UserIntent.WANT_HEAR_TARGET_PRACTICE <-> AppCapability.PROVIDE_TARGET_AUDIO_PRACTICE
UserIntent.WANT_HEAR_TARGET_RESULTS <-> AppCapability.PROVIDE_TARGET_AUDIO_RESULTS
# Clear distinction!
```

## Testing Implications

### Bug Detection Examples

**Bug Type 1: Wrong Audio Visible**
- User in practice phase
- Expects: `AUDIO_PLAYER_TARGET_PRACTICE`
- Sees: `AUDIO_PLAYER_TARGET_RESULTS`
- Diagnosis: Results panel showing prematurely

**Bug Type 2: Audio Type Confusion**
- User clicks "Hear Target" in results
- Expects: Target TTS
- Hears: Recognized text TTS (variable reused incorrectly)
- Diagnosis: `audio_bytes` variable collision

**Bug Type 3: Missing Audio**
- User has recorded audio
- Expects: `AUDIO_PLAYER_USER_LIVE` visible
- Sees: Nothing
- Diagnosis: Conditional logic broken

### State Validation

When testing, user validates:
1. **How many audio players are visible?**
2. **Which types are they?** (target, user, recognized, etc.)
3. **Do they play the correct audio source?**
4. **Are they in the expected location?** (practice area vs results panel)

## Architectural Recommendation

### Current Issue
```python
# Same variable name, different audio!
audio_bytes = speak_text_gtts(text, ...)        # Line 808
audio_bytes = speak_text_gtts(target, ...)      # Line 868 - OVERWRITE
audio_bytes = speak_text_gtts(recognized, ...)  # Line 965 - OVERWRITE AGAIN
```

### Suggested Improvement
```python
# Distinct variable names
target_practice_audio = speak_text_gtts(text, ...)
target_results_audio = speak_text_gtts(target, ...)
recognized_audio = speak_text_gtts(recognized, ...)
```

This would:
- Make code more readable
- Prevent accidental audio source confusion
- Make CCS tracking more accurate
- Facilitate debugging

### Threading/Concurrency

Streamlit doesn't have true threading issues with `st.audio()` because:
- Each `st.audio()` creates a separate HTML5 audio element
- Browsers handle concurrent audio playback
- No shared audio stream state

However, tracking **which audio is which** is still important for:
- User experience (knowing what they're hearing)
- Testing validation (confirming correct audio source)
- State management (knowing what audio is available)

## Integration with Testing

When using CCS framework:

1. **State Extraction**: Integration layer infers which audio players should be visible based on app state
2. **User Intent**: User specifies which audio they want to hear
3. **Port Matching**: Framework checks if desired audio type is available
4. **Validation**: User confirms they can see and play the correct audio type

Example test flow:
```
User in Results Phase
├─ Expected: AUDIO_PLAYER_TARGET_RESULTS visible
├─ Expected: AUDIO_PLAYER_USER_RESULTS visible
├─ Expected: AUDIO_PLAYER_RECOGNIZED_TTS visible (if recognized != target)
│
User validates:
├─ ✓ Can see target audio player
├─ ✓ Can see user recording player  
├─ ✗ Recognized audio player missing despite mismatch
│   → Bug recorded: "Recognized TTS not showing when target != recognized"
```

## Summary

By tracking audio players as **distinct types** rather than generic "audio players", the CCS framework can:
- Detect when wrong audio source is shown
- Validate correct audio in correct location
- Match user intent with specific audio type
- Document audio-related bugs precisely

This addresses the architectural concern about multiple simultaneous audio sources and ensures testing validates **what** audio is playing, not just **that** audio is playing.
