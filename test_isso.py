#!/usr/bin/env python3
"""
Quick test for "isso" recognition with various strategies
"""
import sys
sys.path.insert(0, '.')
from pronunciation_trainer import PronunciationTrainer

print("=" * 70)
print("Testing 'isso' recognition")
print("=" * 70)
print()
print("Tips for this test:")
print("1. Speak immediately after the beep/prompt")
print("2. Say 'isso' clearly: EE-soo")
print("3. Keep it short and clean")
print("4. No pauses between syllables")
print()
print("The system will try 3 times with:")
print("  - Prompt: 'isso' (to guide Whisper)")
print("  - Temperature: 0.0 (deterministic)")
print("  - 2 second recording (shorter = less hallucination)")
print()

trainer = PronunciationTrainer(voice='pt-br')

for attempt in range(3):
    print(f"\n{'=' * 70}")
    print(f"Attempt {attempt + 1}/3")
    print(f"{'=' * 70}\n")
    
    input("Press Enter when ready, then speak 'isso'...")
    
    # Record with shorter duration
    audio_file = trainer.record_audio(duration=2.0)
    
    # Transcribe with prompting
    recognized, result = trainer.transcribe_audio(
        audio_file,
        prompt="isso",
        temperature=0.0
    )
    
    # Check what we got
    correct_phonemes = trainer.get_phonemes("isso")
    user_phonemes = trainer.get_phonemes(recognized)
    
    print(f"Target phonemes:     {correct_phonemes}")
    print(f"Recognized text:     {recognized}")
    print(f"Recognized phonemes: {user_phonemes}")
    
    if recognized.strip() == "isso":
        print("✅ PERFECT TEXT MATCH!")
    elif "isso" in recognized:
        print("🟡 'isso' found in recognition (with extra words)")
    else:
        print("❌ Did not recognize 'isso'")
    
    if correct_phonemes == user_phonemes:
        print("✅ PERFECT PHONEME MATCH!")
        break

print(f"\n{'=' * 70}")
print("Test complete!")
print(f"{'=' * 70}")
