#!/usr/bin/env python3
"""
practice_sentences.py - Practice Portuguese sentence pronunciation

Helps estimate recording duration and format sentences properly.
"""

import sys
from pathlib import Path

# Add parent dir to path for imports
sys.path.insert(0, str(Path(__file__).parent))

try:
    from pronunciation_trainer import PronunciationTrainer
except ImportError:
    print("Error: Run from espeak-ng directory with venv activated")
    sys.exit(1)


def estimate_duration(text, words_per_second=2.5):
    """
    Estimate speaking duration for text
    
    Args:
        text: Portuguese text
        words_per_second: Average speaking rate (2-3 for practice)
    
    Returns:
        Recommended recording duration in seconds
    """
    words = len(text.split())
    duration = int((words / words_per_second) + 2)  # Add 2 second buffer
    return max(5, duration)  # Minimum 5 seconds


def practice_sentence(sentence, voice="pt-br", model="base"):
    """Practice a Portuguese sentence with auto-duration"""
    
    # Estimate duration
    duration = estimate_duration(sentence)
    
    print(f"\n📏 Sentence length: {len(sentence.split())} words")
    print(f"⏱️  Recording duration: {duration} seconds")
    print(f"💡 Tip: Speak at a comfortable, clear pace\n")
    
    # Initialize trainer
    trainer = PronunciationTrainer(
        whisper_model=model,
        voice=voice
    )
    
    # Practice
    result = trainer.practice_word(
        sentence,
        duration=duration
    )
    
    return result


def format_sentence_for_speech(text):
    """
    Format text for better speech recognition
    
    - Converts numbers to words
    - Normalizes punctuation
    """
    # Basic number to Portuguese words (extend as needed)
    numbers = {
        '1933': 'mil novecentos e trinta e três',
        '2024': 'dois mil e vinte e quatro',
        '2025': 'dois mil e vinte e cinco',
    }
    
    formatted = text
    for num, words in numbers.items():
        formatted = formatted.replace(num, words)
    
    return formatted.strip()


def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Practice Portuguese sentence pronunciation"
    )
    parser.add_argument(
        "sentence",
        help="Portuguese sentence to practice"
    )
    parser.add_argument(
        "--duration", "-d",
        type=int,
        help="Recording duration (auto-calculated if not specified)"
    )
    parser.add_argument(
        "--voice", "-v",
        default="pt-br",
        help="Voice (default: pt-br)"
    )
    parser.add_argument(
        "--model", "-m",
        default="base",
        choices=["tiny", "base", "small", "medium"],
        help="Whisper model (default: base)"
    )
    parser.add_argument(
        "--format",
        action="store_true",
        help="Auto-format sentence (convert numbers to words)"
    )
    
    args = parser.parse_args()
    
    # Format if requested
    sentence = args.sentence
    if args.format:
        formatted = format_sentence_for_speech(sentence)
        if formatted != sentence:
            print(f"\n📝 Formatted: {formatted}\n")
            sentence = formatted
    
    # Practice
    if args.duration:
        trainer = PronunciationTrainer(
            whisper_model=args.model,
            voice=args.voice
        )
        trainer.practice_word(sentence, duration=args.duration)
    else:
        practice_sentence(sentence, voice=args.voice, model=args.model)


if __name__ == "__main__":
    main()
