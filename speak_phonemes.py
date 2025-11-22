#!/usr/bin/env python3
"""
speak_phonemes.py - Speak eSpeak phoneme codes for Brazilian Portuguese pronunciation training

This tool is designed for speech recognition and pronunciation training:
1. Your speech recognizer produces phoneme codes (from your speech)
2. This tool speaks those phonemes back to you
3. Compare with correct Brazilian Portuguese pronunciation

Usage:
    python3 speak_phonemes.py "k'azV"              # Speak phoneme codes
    python3 speak_phonemes.py -c "casa"            # Get and speak correct phonemes for a word
    python3 speak_phonemes.py -C "k'azV" "casa"    # Compare your phonemes with correct
    python3 speak_phonemes.py -i input.txt         # Process file of phoneme codes
"""

import subprocess
import sys
import argparse
from pathlib import Path
import time

# Configuration
REPO_DIR = Path(__file__).parent
ESPEAK_CMD = REPO_DIR / "local/bin/run-espeak-ng"
DEFAULT_VOICE = "pt-br"  # Brazilian Portuguese by default

class BrazilianPortuguesePhonemes:
    def __init__(self, voice="pt-br", speed=160, pitch=40):
        self.voice = voice
        self.speed = speed
        self.pitch = pitch
    
    def speak_phonemes(self, phoneme_codes, label=None):
        """Speak eSpeak phoneme codes using [[ ]] notation"""
        if not phoneme_codes.strip():
            return
        
        # Wrap in [[ ]] if not already
        if not phoneme_codes.startswith("[["):
            phoneme_codes = f"[[{phoneme_codes}]]"
        
        if label:
            print(f"{label}: {phoneme_codes}")
        
        subprocess.run([
            str(ESPEAK_CMD), "-v", self.voice,
            "-s", str(self.speed), "-p", str(self.pitch),
            phoneme_codes
        ])
    
    def speak_text(self, text, label=None):
        """Speak Brazilian Portuguese text normally"""
        if label:
            print(f"{label}: {text}")
        
        subprocess.run([
            str(ESPEAK_CMD), "-v", self.voice,
            "-s", str(self.speed), "-p", str(self.pitch),
            text
        ])
    
    def get_phonemes(self, text):
        """Get eSpeak phoneme codes for Brazilian Portuguese text"""
        result = subprocess.run(
            [str(ESPEAK_CMD), "-v", self.voice, "-x", "-q", text],
            capture_output=True,
            text=True
        )
        return result.stdout.strip()
    
    def get_ipa(self, text):
        """Get IPA transcription for Brazilian Portuguese text"""
        result = subprocess.run(
            [str(ESPEAK_CMD), "-v", self.voice, "--ipa", "-q", text],
            capture_output=True,
            text=True
        )
        return result.stdout.strip()
    
    def compare_pronunciation(self, your_phonemes, correct_text):
        """
        Compare your phoneme pronunciation with correct Brazilian Portuguese
        
        Args:
            your_phonemes: Phoneme codes from your speech recognizer
            correct_text: The correct Portuguese word/phrase
        """
        correct_phonemes = self.get_phonemes(correct_text)
        correct_ipa = self.get_ipa(correct_text)
        
        # Clean up for comparison
        your_clean = your_phonemes.replace("[[", "").replace("]]", "").strip()
        correct_clean = correct_phonemes.strip()
        
        match = (your_clean == correct_clean)
        
        print(f"\n{'='*60}")
        print(f"Target word:      {correct_text}")
        print(f"{'='*60}")
        print(f"Correct IPA:      {correct_ipa}")
        print(f"Correct phonemes: {correct_phonemes}")
        print(f"Your phonemes:    {your_clean}")
        print(f"Match:            {'✓ YES' if match else '✗ NO'}")
        print(f"{'='*60}\n")
        
        # Speak correct version
        print("Speaking CORRECT pronunciation:")
        self.speak_text(correct_text)
        time.sleep(0.5)
        
        # Speak your version
        print("Speaking YOUR pronunciation:")
        self.speak_phonemes(your_clean)
        
        return match
    
    def text_to_audio(self, text, output_file):
        """Save Brazilian Portuguese text to WAV file"""
        subprocess.run([
            str(ESPEAK_CMD), "-v", self.voice,
            "-w", output_file, text
        ])
        print(f"Saved to: {output_file}")


def main():
    parser = argparse.ArgumentParser(
        description="Speak eSpeak phoneme codes for Brazilian Portuguese pronunciation training",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Speak phoneme codes from your speech recognizer
  %(prog)s "k'azV"
  
  # Get correct phonemes for a word
  %(prog)s -c "casa"
  
  # Compare your pronunciation with correct
  %(prog)s -C "k'azV" "casa"
  
  # Process multiple words
  %(prog)s -c "água tempo pessoa obrigado"
  
  # Change voice to European Portuguese
  %(prog)s -v pt "k'azV"
  
  # Process file of phoneme codes (one per line)
  %(prog)s -i phonemes.txt
        """
    )
    
    parser.add_argument("phonemes", nargs="?",
                       help="eSpeak phoneme codes to speak")
    parser.add_argument("-v", "--voice", default=DEFAULT_VOICE,
                       choices=["pt-br", "pt"],
                       help=f"Voice to use (default: {DEFAULT_VOICE})")
    parser.add_argument("-s", "--speed", type=int, default=160,
                       help="Speaking speed in WPM (default: 160)")
    parser.add_argument("-p", "--pitch", type=int, default=40,
                       help="Pitch 0-99 (default: 40)")
    parser.add_argument("-c", "--correct", metavar="TEXT",
                       help="Get and speak correct phonemes for Portuguese text")
    parser.add_argument("-C", "--compare", metavar="TEXT",
                       help="Compare your phonemes with correct pronunciation of TEXT")
    parser.add_argument("-i", "--input-file", metavar="FILE",
                       help="Read phoneme codes from file (one per line)")
    parser.add_argument("-w", "--wav", metavar="OUTPUT",
                       help="Save to WAV file instead of speaking")
    parser.add_argument("--ipa", action="store_true",
                       help="Also show IPA transcription")
    
    args = parser.parse_args()
    
    speaker = BrazilianPortuguesePhonemes(
        voice=args.voice,
        speed=args.speed,
        pitch=args.pitch
    )
    
    # Mode: Get correct phonemes for text
    if args.correct:
        words = args.correct.split()
        for word in words:
            phonemes = speaker.get_phonemes(word)
            ipa = speaker.get_ipa(word) if args.ipa else ""
            
            print(f"\nWord:     {word}")
            print(f"Phonemes: {phonemes}")
            if args.ipa:
                print(f"IPA:      {ipa}")
            
            if args.wav:
                output = f"{word}.wav"
                speaker.text_to_audio(word, output)
            else:
                print("Speaking...")
                speaker.speak_text(word)
                time.sleep(0.3)
        return
    
    # Mode: Compare pronunciation
    if args.compare:
        if not args.phonemes:
            print("Error: Provide your phoneme codes to compare")
            print(f"Usage: {sys.argv[0]} -C <your_phonemes> <correct_word>")
            sys.exit(1)
        
        speaker.compare_pronunciation(args.phonemes, args.compare)
        return
    
    # Mode: Process file
    if args.input_file:
        with open(args.input_file) as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                
                print(f"Phonemes: {line}")
                speaker.speak_phonemes(line)
                time.sleep(0.3)
        return
    
    # Mode: Speak phoneme codes
    if args.phonemes:
        if args.wav:
            # For WAV output, we need text not phonemes
            print("Note: WAV output works best with Portuguese text")
            print(f"Phonemes: {args.phonemes}")
        
        speaker.speak_phonemes(args.phonemes, "Speaking")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
