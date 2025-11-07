#!/usr/bin/env python3
"""
pronunciation_trainer.py - Complete Portuguese pronunciation training system

Integrates:
1. Whisper speech recognition (speech → text)
2. eSpeak phoneme generation (text → eIPA)
3. Pronunciation comparison and feedback

Usage:
    # Practice a specific word
    python3 pronunciation_trainer.py casa recording.wav
    
    # Interactive mode (records from microphone)
    python3 pronunciation_trainer.py casa
    
    # Batch practice mode
    python3 pronunciation_trainer.py --batch words.txt
"""

import argparse
import subprocess
import sys
from pathlib import Path
from typing import Optional, Dict, Tuple

try:
    import whisper
    import sounddevice as sd
    import soundfile as sf
    import numpy as np
except ImportError as e:
    print(f"Error: {e}")
    print("\nPlease activate the virtual environment and install dependencies:")
    print("  source venv/bin/activate")
    print("  pip install -r requirements.txt")
    sys.exit(1)


class PronunciationTrainer:
    """Brazilian Portuguese pronunciation trainer with speech recognition"""
    
    def __init__(
        self,
        espeak_path: str = "./local/bin/run-espeak-ng",
        whisper_model: str = "base",
        voice: str = "pt-br"
    ):
        """
        Initialize the pronunciation trainer
        
        Args:
            espeak_path: Path to eSpeak executable
            whisper_model: Whisper model size (tiny, base, small, medium, large)
            voice: eSpeak voice (pt-br for Brazilian, pt for European)
        """
        self.espeak = Path(espeak_path)
        self.voice = voice
        
        print(f"Loading Whisper model '{whisper_model}'...")
        self.whisper = whisper.load_model(whisper_model)
        print("✓ Whisper model loaded\n")
        
        if not self.espeak.exists():
            print(f"Warning: eSpeak not found at {espeak_path}")
            print("Run ./configure-macos.sh && make && make install")
    
    def record_audio(
        self,
        duration: int = 3,
        samplerate: int = 16000,
        output_file: Optional[str] = None
    ) -> str:
        """
        Record audio from microphone
        
        Args:
            duration: Recording duration in seconds
            samplerate: Sample rate (Whisper uses 16kHz)
            output_file: Optional output file path
            
        Returns:
            Path to recorded audio file
        """
        print(f"\n🎤 Recording for {duration} seconds...")
        print("Speak now!")
        
        recording = sd.rec(
            int(duration * samplerate),
            samplerate=samplerate,
            channels=1,
            dtype='float32'
        )
        sd.wait()
        
        print("✓ Recording complete\n")
        
        if output_file is None:
            output_file = "temp_recording.wav"
        
        sf.write(output_file, recording, samplerate)
        return output_file
    
    def transcribe_audio(self, audio_file: str) -> Tuple[str, Dict]:
        """
        Transcribe audio to text using Whisper
        
        Args:
            audio_file: Path to audio file
            
        Returns:
            Tuple of (transcribed text, full result dict)
        """
        print("🎧 Transcribing audio...")
        result = self.whisper.transcribe(
            audio_file,
            language="pt",
            task="transcribe"
        )
        
        text = result["text"].strip().lower()
        print(f"✓ Recognized: \"{text}\"\n")
        
        return text, result
    
    def get_phonemes(self, text: str) -> str:
        """
        Get eSpeak phoneme codes (eIPA) for text
        
        Args:
            text: Portuguese text
            
        Returns:
            eSpeak phoneme codes
        """
        result = subprocess.run(
            [str(self.espeak), "-v", self.voice, "-x", "-q", text],
            capture_output=True,
            text=True
        )
        return result.stdout.strip()
    
    def speak_text(self, text: str, speed: int = 160, pitch: int = 40):
        """Speak Portuguese text"""
        subprocess.run([
            str(self.espeak),
            "-v", self.voice,
            "-s", str(speed),
            "-p", str(pitch),
            text
        ])
    
    def speak_phonemes(self, phonemes: str, speed: int = 160, pitch: int = 40):
        """Speak eSpeak phoneme codes"""
        subprocess.run([
            str(self.espeak),
            "-v", self.voice,
            "-s", str(speed),
            "-p", str(pitch),
            f"[[{phonemes}]]"
        ])
    
    def compare_phonemes(
        self,
        user_phonemes: str,
        correct_phonemes: str
    ) -> Tuple[bool, float]:
        """
        Compare user phonemes with correct phonemes
        
        Returns:
            Tuple of (exact_match, similarity_score)
        """
        exact_match = user_phonemes == correct_phonemes
        
        # Simple similarity: character-level matching
        if len(correct_phonemes) == 0:
            similarity = 0.0
        else:
            matches = sum(
                1 for a, b in zip(user_phonemes, correct_phonemes)
                if a == b
            )
            similarity = matches / max(len(user_phonemes), len(correct_phonemes))
        
        return exact_match, similarity
    
    def practice_word(
        self,
        target_word: str,
        audio_file: Optional[str] = None,
        duration: int = 3,
        speed: int = 140,
        pitch: int = 35
    ) -> Dict:
        """
        Complete practice workflow for a word
        
        Args:
            target_word: The word to practice
            audio_file: Audio file, or None to record
            duration: Recording duration if audio_file is None
            speed: Speech speed (80-450, default 140, lower is slower)
            pitch: Speech pitch (0-99, default 35)
            
        Returns:
            Practice result dictionary
        """
        print("=" * 70)
        print(f"🎯 Target word: {target_word}")
        print("=" * 70)
        
        # Get correct pronunciation
        correct_phonemes = self.get_phonemes(target_word)
        print(f"📝 Correct phonemes: {correct_phonemes}")
        
        print(f"\n🔊 Listen to correct pronunciation (speed={speed}, pitch={pitch}):")
        self.speak_text(target_word, speed=speed, pitch=pitch)
        
        # Get user's pronunciation
        if audio_file is None:
            input("\nPress Enter when ready to record...")
            audio_file = self.record_audio(duration=duration)
        
        # Recognize what user said
        recognized_text, whisper_result = self.transcribe_audio(audio_file)
        
        # Get phonemes of what they said
        user_phonemes = self.get_phonemes(recognized_text)
        print(f"📝 Your phonemes:    {user_phonemes}")
        
        # Compare
        exact_match, similarity = self.compare_phonemes(
            user_phonemes,
            correct_phonemes
        )
        
        print("\n" + "=" * 70)
        if exact_match:
            print("✅ PERFECT! Phonemes match exactly!")
        else:
            print(f"📊 Similarity: {similarity:.1%}")
            if similarity > 0.8:
                print("🟢 Very close! Minor differences only.")
            elif similarity > 0.6:
                print("🟡 Good attempt, but needs some work.")
            else:
                print("🔴 Keep practicing - significant differences.")
        print("=" * 70)
        
        # Speak comparison
        if not exact_match:
            print("\n🔊 Listen to the difference:")
            print(f"   Correct (speed={speed}, pitch={pitch}):")
            self.speak_phonemes(correct_phonemes, speed=speed, pitch=pitch)
            
            print("   Your version:")
            self.speak_phonemes(user_phonemes, speed=speed, pitch=pitch)
        
        # Clean up temp file
        if audio_file == "temp_recording.wav":
            Path(audio_file).unlink(missing_ok=True)
        
        return {
            "target": target_word,
            "recognized": recognized_text,
            "correct_phonemes": correct_phonemes,
            "user_phonemes": user_phonemes,
            "exact_match": exact_match,
            "similarity": similarity
        }
    
    def batch_practice(
        self,
        words_file: str,
        duration: int = 3,
        speed: int = 140,
        pitch: int = 35
    ):
        """
        Practice a list of words from a file
        
        Args:
            words_file: Path to file with one word per line
            duration: Recording duration per word
            speed: Speech speed (80-450, default 140)
            pitch: Speech pitch (0-99, default 35)
        """
        words = Path(words_file).read_text().strip().split('\n')
        words = [w.strip() for w in words if w.strip()]
        
        print(f"\n📚 Practicing {len(words)} words")
        print(f"⚙️  Settings: speed={speed}, pitch={pitch}\n")
        
        results = []
        for i, word in enumerate(words, 1):
            print(f"\n{'#' * 70}")
            print(f"Word {i}/{len(words)}")
            print(f"{'#' * 70}\n")
            
            result = self.practice_word(word, duration=duration, speed=speed, pitch=pitch)
            results.append(result)
            
            if i < len(words):
                input("\nPress Enter for next word...")
        
        # Summary
        print("\n" + "=" * 70)
        print("📊 PRACTICE SUMMARY")
        print("=" * 70)
        
        perfect = sum(1 for r in results if r["exact_match"])
        avg_similarity = sum(r["similarity"] for r in results) / len(results)
        
        print(f"\nPerfect: {perfect}/{len(results)} ({perfect/len(results):.1%})")
        print(f"Average similarity: {avg_similarity:.1%}\n")
        
        print("Detailed results:")
        for r in results:
            status = "✅" if r["exact_match"] else f"📊 {r['similarity']:.1%}"
            print(f"  {status}  {r['target']:15} → {r['recognized']}")


def main():
    parser = argparse.ArgumentParser(
        description="Portuguese pronunciation trainer with speech recognition",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Practice a word (records from microphone)
  python3 pronunciation_trainer.py casa
  
  # Practice with pre-recorded audio
  python3 pronunciation_trainer.py casa recording.wav
  
  # Batch practice from word list
  python3 pronunciation_trainer.py --batch words.txt
  
  # Use different Whisper model
  python3 pronunciation_trainer.py --model small casa
  
  # Longer recording time
  python3 pronunciation_trainer.py --duration 5 "boa noite"
        """
    )
    
    parser.add_argument(
        "target",
        nargs="?",
        help="Target word or phrase to practice"
    )
    parser.add_argument(
        "audio",
        nargs="?",
        help="Audio file (optional, will record if not provided)"
    )
    parser.add_argument(
        "--batch",
        "-b",
        help="Practice words from file (one per line)"
    )
    parser.add_argument(
        "--model",
        "-m",
        default="base",
        choices=["tiny", "base", "small", "medium", "large"],
        help="Whisper model size (default: base)"
    )
    parser.add_argument(
        "--voice",
        "-v",
        default="pt-br",
        help="eSpeak voice (default: pt-br)"
    )
    parser.add_argument(
        "--duration",
        "-d",
        type=int,
        default=3,
        help="Recording duration in seconds (default: 3)"
    )
    parser.add_argument(
        "--speed",
        "-s",
        type=int,
        default=140,
        help="Speech speed in words/min (80-450, default: 140, lower is slower)"
    )
    parser.add_argument(
        "--pitch",
        "-p",
        type=int,
        default=35,
        help="Speech pitch (0-99, default: 35)"
    )
    parser.add_argument(
        "--espeak",
        default="./local/bin/run-espeak-ng",
        help="Path to eSpeak executable"
    )
    
    args = parser.parse_args()
    
    # Validate arguments
    if args.batch:
        if not Path(args.batch).exists():
            print(f"Error: File not found: {args.batch}")
            sys.exit(1)
    elif not args.target:
        parser.print_help()
        sys.exit(1)
    
    # Initialize trainer
    trainer = PronunciationTrainer(
        espeak_path=args.espeak,
        whisper_model=args.model,
        voice=args.voice
    )
    
    # Run training
    try:
        if args.batch:
            trainer.batch_practice(
                args.batch,
                duration=args.duration,
                speed=args.speed,
                pitch=args.pitch
            )
        else:
            trainer.practice_word(
                args.target,
                audio_file=args.audio,
                duration=args.duration,
                speed=args.speed,
                pitch=args.pitch
            )
    except KeyboardInterrupt:
        print("\n\n👋 Practice session ended")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
