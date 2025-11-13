#!/usr/bin/env python3
"""
Extract unique French words from phrase files and populate word lists.

For each phrase file in phrases-{level}/, extract all unique French words
and create a corresponding word list in words-{level}/ with translations and IPA.
"""

import re
from pathlib import Path
from collections import defaultdict

# Simple word translations (will be automated later)
# This is a basic dictionary for common French words
WORD_TRANSLATIONS = {
    # A-level common words
    "oui": "yes",
    "non": "no",
    "merci": "thank you",
    "bonjour": "hello / good day",
    "bonsoir": "good evening",
    "au": "to the / at the",
    "revoir": "goodbye",
    "salut": "hi / bye (informal)",
    "s'il": "if",
    "vous": "you (formal/plural)",
    "plaît": "please",
    "excusez": "excuse",
    "moi": "me",
    "pardon": "sorry / pardon",
    "ça": "that / it",
    "va": "goes / is going",
    "et": "and",
    "toi": "you (informal)",
    "de": "of / from",
    "rien": "nothing",
    "bonne": "good (f)",
    "journée": "day",
    "soirée": "evening",
    "nuit": "night",
    "à": "to / at",
    "bientôt": "soon",
    "demain": "tomorrow",
    "d'accord": "okay / agreed",
    "bien": "good / well",
    "très": "very",
    "pas": "not",
    "mal": "bad",
    "comme": "like / as",
    "ci": "here",
    "sa": "his / her / its",
    "je": "I",
    "ne": "not (negation particle)",
    "sais": "know",
    "peut": "can / maybe",
    "être": "maybe",
    "voilà": "there it is / there you go",
    "allons": "let's go / we go",
    "y": "there",
    "attention": "watch out / careful",
    "bienvenue": "welcome",
    "félicitations": "congratulations",
    "bon": "good",
    "appétit": "appetite",
    "santé": "health / cheers",
    "joyeux": "merry / joyful",
    "noël": "christmas",
    "année": "year",
    "anniversaire": "birthday",
    "courage": "courage",
    "voyage": "trip / journey",
    "enchanté": "delighted / nice to meet you (m)",
    "enchantée": "delighted / nice to meet you (f)",
    "avec": "with",
    "plaisir": "pleasure",
    "volontiers": "gladly / willingly",
    "j'arrive": "i'm coming",
    "une": "a / one (f)",
    "seconde": "second",
    "un": "a / one (m)",
    "moment": "moment",
    "c'est": "it is / this is",
    "tout": "all / everything",
    "tant": "so much",
    "pis": "worse / too bad",
    "mieux": "better",
}

def get_translation(word):
    """Get English translation for a French word."""
    # Try exact match first
    if word in WORD_TRANSLATIONS:
        return WORD_TRANSLATIONS[word]
    
    # Return placeholder for words without translations
    return "[translation needed]"

def get_ipa(word):
    """Get IPA pronunciation for a French word."""
    # Placeholder - will be automated with eSpeak later
    return "[ipa]"

def extract_words_from_phrase(phrase):
    """Extract individual words from a French phrase."""
    # Remove punctuation and split on whitespace
    # Keep apostrophes as they're part of French words (l', d', etc.)
    phrase = phrase.strip()
    
    # Split on spaces and hyphens, but keep words with apostrophes together
    words = re.findall(r"[a-zàâäæçéèêëïîôùûüÿœA-ZÀÂÄÆÇÉÈÊËÏÎÔÙÛÜŸŒ']+", phrase, re.UNICODE)
    
    return [w.strip() for w in words if w.strip()]

def process_phrase_file(phrase_file):
    """Extract unique words from a phrase file."""
    words = set()
    
    with open(phrase_file, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            
            # Skip comments and empty lines
            if not line or line.startswith('#'):
                continue
            
            # Extract the French phrase (before the first |)
            if '|' in line:
                french_phrase = line.split('|')[0].strip()
                phrase_words = extract_words_from_phrase(french_phrase)
                # Convert all words to lowercase to avoid duplicates
                words.update(w.lower() for w in phrase_words)
    
    return sorted(words)

def main():
    base_dir = Path(__file__).parent / "language_materials" / "fr"
    
    if not base_dir.exists():
        print(f"Error: {base_dir} not found")
        return
    
    # Process each level (A, B, C, D instead of A1, A2, etc.)
    levels = ['A', 'B', 'C', 'D']
    
    for level in levels:
        phrases_dir = base_dir / f"phrases-{level}"
        words_dir = base_dir / f"words-{level}"
        
        if not phrases_dir.exists():
            print(f"⚠ Skipping {level}: {phrases_dir} not found")
            continue
        
        if not words_dir.exists():
            print(f"Creating {words_dir}")
            words_dir.mkdir(parents=True, exist_ok=True)
        
        # Find all phrase files
        phrase_files = sorted(phrases_dir.glob("*.txt"))
        
        if not phrase_files:
            print(f"⚠ No phrase files found in {phrases_dir}")
            continue
        
        print(f"\n{level} Level:")
        print("-" * 50)
        
        for phrase_file in phrase_files:
            # Extract words from this phrase file
            words = process_phrase_file(phrase_file)
            
            if not words:
                print(f"  ⚠ {phrase_file.name}: No words found (empty or all placeholders)")
                continue
            
            # Create corresponding word file with unique name (words-01.txt, etc.)
            word_file_name = phrase_file.name.replace('phr-', 'words-')
            word_file = words_dir / word_file_name
            
            # Write words to file with translations and IPA
            with open(word_file, 'w', encoding='utf-8') as f:
                f.write(f"# French words from {phrase_file.name}\n")
                f.write(f"# Level: {level}\n")
                f.write(f"# Total unique words: {len(words)}\n")
                f.write("#\n")
                f.write("# Format: word | translation | [ipa]\n")
                f.write("# One word per line\n")
                f.write("#\n\n")
                
                for word in words:
                    translation = get_translation(word)
                    ipa = get_ipa(word)
                    f.write(f"{word} | {translation} | {ipa}\n")
            
            print(f"  ✓ {phrase_file.name} → {word_file.name} ({len(words)} words)")
    
    print("\n" + "=" * 50)
    print("✓ Word extraction complete!")

if __name__ == "__main__":
    main()
