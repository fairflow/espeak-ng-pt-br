#!/usr/bin/env python3
"""
ipa_to_espeak.py - Convert IPA to eSpeak-NG speech for Portuguese

This script provides a workaround for speaking IPA transcriptions.
Since eSpeak-NG's [[...]] notation uses internal phoneme codes (not IPA),
we need to either:
1. Convert your IPA to Portuguese text (reverse transliteration)
2. Use eSpeak's own IPA output as a reference
3. Map IPA symbols to eSpeak phoneme codes

Usage:
    python3 ipa_to_espeak.py "kˈazə"
    python3 ipa_to_espeak.py -f ipa_words.txt
"""

import subprocess
import sys
import argparse
from pathlib import Path

# Path to espeak-ng
ESPEAK_CMD = Path(__file__).parent / "local/bin/run-espeak-ng"

def text_to_ipa(text, voice="pt"):
    """Get eSpeak's IPA for Portuguese text"""
    result = subprocess.run(
        [str(ESPEAK_CMD), "-v", voice, "--ipa", "-q", text],
        capture_output=True,
        text=True
    )
    return result.stdout.strip()

def speak_text(text, voice="pt", speed=160, pitch=40):
    """Speak Portuguese text"""
    subprocess.run([
        str(ESPEAK_CMD), "-v", voice,
        "-s", str(speed), "-p", str(pitch),
        text
    ])

def text_to_wav(text, output_file, voice="pt"):
    """Save Portuguese text to WAV"""
    subprocess.run([
        str(ESPEAK_CMD), "-v", voice,
        "-w", output_file, text
    ])

def compare_ipa(your_ipa, reference_text, voice="pt"):
    """Compare your IPA with eSpeak's IPA"""
    espeak_ipa = text_to_ipa(reference_text, voice)
    
    print(f"Reference text: {reference_text}")
    print(f"Your IPA:       {your_ipa}")
    print(f"eSpeak IPA:     {espeak_ipa}")
    print("\nSpeaking reference text:")
    speak_text(reference_text, voice)

def ipa_similarity_search(your_ipa, word_list, voice="pt"):
    """
    Find Portuguese words with similar IPA.
    This helps you find actual words that match your IPA transcription.
    """
    results = []
    for word in word_list:
        espeak_ipa = text_to_ipa(word, voice)
        # Simple similarity: remove spaces and stress marks for comparison
        clean_your = your_ipa.replace(" ", "").replace("ˈ", "").replace("ˌ", "")
        clean_espeak = espeak_ipa.replace(" ", "").replace("ˈ", "").replace("ˌ", "")
        
        if clean_your in clean_espeak or clean_espeak in clean_your:
            results.append((word, espeak_ipa))
    
    return results

# Common Portuguese words for testing
COMMON_WORDS = [
    "casa", "Portugal", "chuva", "água", "tempo", "pessoa",
    "dia", "noite", "manhã", "tarde", "sim", "não",
    "obrigado", "por favor", "olá", "adeus", "bom", "mau"
]

def main():
    parser = argparse.ArgumentParser(
        description="IPA to speech for Portuguese using eSpeak-NG"
    )
    parser.add_argument("ipa", nargs="?", help="IPA transcription to process")
    parser.add_argument("-v", "--voice", default="pt", 
                       choices=["pt", "pt-br"],
                       help="Voice to use (pt=Portugal, pt-br=Brazil)")
    parser.add_argument("-c", "--compare", metavar="TEXT",
                       help="Compare your IPA with this Portuguese text")
    parser.add_argument("-f", "--file", help="Read IPA from file")
    parser.add_argument("-t", "--text", metavar="TEXT",
                       help="Get IPA for Portuguese text")
    parser.add_argument("-s", "--search", action="store_true",
                       help="Search for words matching your IPA")
    parser.add_argument("-w", "--wav", metavar="OUTPUT",
                       help="Output WAV file")
    
    args = parser.parse_args()
    
    # Mode: Get IPA from text
    if args.text:
        ipa = text_to_ipa(args.text, args.voice)
        print(f"Text: {args.text}")
        print(f"IPA:  {ipa}")
        if not args.wav:
            print("\nSpeaking...")
            speak_text(args.text, args.voice)
        else:
            text_to_wav(args.text, args.wav, args.voice)
            print(f"Saved to {args.wav}")
        return
    
    # Mode: Compare IPA
    if args.compare and args.ipa:
        compare_ipa(args.ipa, args.compare, args.voice)
        return
    
    # Mode: Search for matching words
    if args.search and args.ipa:
        print(f"Searching for words matching IPA: {args.ipa}\n")
        results = ipa_similarity_search(args.ipa, COMMON_WORDS, args.voice)
        if results:
            for word, ipa in results:
                print(f"{word:15} → {ipa}")
                speak_text(word, args.voice)
        else:
            print("No matching words found in common word list.")
        return
    
    # Mode: Process IPA from file
    if args.file:
        with open(args.file) as f:
            for line in f:
                ipa = line.strip()
                if not ipa or ipa.startswith("#"):
                    continue
                print(f"IPA: {ipa}")
                # Try to find matching word
                results = ipa_similarity_search(ipa, COMMON_WORDS, args.voice)
                if results:
                    word, _ = results[0]
                    print(f"  → Closest match: {word}")
                    speak_text(word, args.voice)
                else:
                    print("  → No match found")
        return
    
    # Default: Process single IPA
    if args.ipa:
        print(f"Your IPA: {args.ipa}")
        print("\nSearching for matching Portuguese words...")
        results = ipa_similarity_search(args.ipa, COMMON_WORDS, args.voice)
        
        if results:
            print(f"\nFound {len(results)} potential match(es):\n")
            for word, espeak_ipa in results:
                print(f"Word:       {word}")
                print(f"eSpeak IPA: {espeak_ipa}")
                print("Speaking...")
                speak_text(word, args.voice)
                print()
        else:
            print("\nNo matches in common word list.")
            print("\nSuggestion: Use --compare with a Portuguese word:")
            print(f"  python3 {sys.argv[0]} \"{args.ipa}\" --compare \"casa\"")
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
