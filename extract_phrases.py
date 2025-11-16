#!/usr/bin/env python3
"""
Phrase Extractor for Miolingo Language Materials

Extracts dialogue and narrative phrases from a French story for language learning.
Filters for appropriate length, grammatical completeness, and practical reusability.

Usage:
    python3 extract_phrases.py narrative_fr.txt --output extracted_phrases_fr.json
"""

import json
import re
import sys
from pathlib import Path
from typing import List, Dict, Optional
import argparse

class PhraseExtractor:
    def __init__(self, min_words=3, max_words=45):
        self.min_words = min_words
        self.max_words = max_words
        self.extracted = []
        
    def load_narrative(self, filepath: Path) -> str:
        """Load the narrative text file."""
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    
    def parse_scenes(self, text: str) -> List[Dict]:
        """
        Parse narrative into scenes with metadata.
        Expected format: ### SCENE X: Title or ### SCÈNE X: Title
        """
        scenes = []
        # Split by scene markers (handles SCENE or SCÈNE)
        scene_pattern = r'###\s*SC[EÈ]NE\s+(\d+):\s*(.+?)(?=###\s*SC[EÈ]NE|\Z)'
        matches = re.finditer(scene_pattern, text, re.DOTALL | re.IGNORECASE)
        
        for match in matches:
            scene_num = int(match.group(1))
            scene_title = match.group(2).strip().split('\n')[0]
            scene_content = match.group(2).strip()
            
            scenes.append({
                'number': scene_num,
                'title': scene_title,
                'content': scene_content
            })
        
        return scenes
    
    def extract_dialogue(self, text: str) -> List[str]:
        """Extract dialogue from text (text in quotes)."""
        # Match quoted text, handling both single and double quotes
        dialogue_pattern = r'[«"]([^»"]+)[»"]'
        dialogues = re.findall(dialogue_pattern, text)
        return [d.strip() for d in dialogues if d.strip()]
    
    def extract_sentences(self, text: str) -> List[str]:
        """Extract narrative sentences and meaningful phrases."""
        # Remove dialogue first
        no_dialogue = re.sub(r'[«"]([^»"]+)[»"]', '', text)
        
        # Split on sentence endings AND on semicolons, colons, em-dashes for phrase extraction
        sentences = re.split(r'[.!?;:—]+\s+', no_dialogue)
        return [s.strip() for s in sentences if s.strip() and not s.startswith('###')]
    
    def filter_phrase(self, phrase: str) -> bool:
        """Check if phrase meets criteria for extraction."""
        # Count words
        words = phrase.split()
        word_count = len(words)
        
        if word_count < self.min_words or word_count > self.max_words:
            return False
        
        # Must contain a verb (simple heuristic: common verb endings)
        verb_pattern = r'\b(est|sont|ai|as|a|avons|avez|ont|suis|es|était|vais|va|' \
                      r'voudrais|peux|dois|faut|fait|fais|veux|sais|peut|peuvent|' \
                      r'\w+er|é|ais|ait|ons|ez|ent|rai|ras|ra|rons|rez|ront)\b'
        
        if not re.search(verb_pattern, phrase, re.IGNORECASE):
            return False
        
        # Avoid scene markers, titles, etc.
        if phrase.startswith('SCENE') or phrase.startswith('ACT'):
            return False
            
        return True
    
    def extract_from_scene(self, scene: Dict) -> List[Dict]:
        """Extract phrases from a single scene."""
        content = scene['content']
        phrases = []
        
        # Extract dialogue
        dialogues = self.extract_dialogue(content)
        for dialogue in dialogues:
            if self.filter_phrase(dialogue):
                phrases.append({
                    'text': dialogue,
                    'type': 'dialogue',
                    'scene_number': scene['number'],
                    'scene_title': scene['title']
                })
        
        # Extract narrative sentences
        sentences = self.extract_sentences(content)
        for sentence in sentences:
            if self.filter_phrase(sentence):
                phrases.append({
                    'text': sentence,
                    'type': 'narrative',
                    'scene_number': scene['number'],
                    'scene_title': scene['title']
                })
        
        return phrases
    
    def extract_all(self, filepath: Path) -> List[Dict]:
        """Main extraction method."""
        print(f"📖 Loading narrative from {filepath}")
        narrative = self.load_narrative(filepath)
        
        print("🔍 Parsing scenes...")
        scenes = self.parse_scenes(narrative)
        print(f"   Found {len(scenes)} scenes")
        
        all_phrases = []
        for scene in scenes:
            print(f"   Extracting from Scene {scene['number']}: {scene['title']}")
            phrases = self.extract_from_scene(scene)
            all_phrases.extend(phrases)
            print(f"      → {len(phrases)} phrases extracted")
        
        self.extracted = all_phrases
        return all_phrases
    
    def save_json(self, output_path: Path):
        """Save extracted phrases to JSON."""
        output_data = {
            'metadata': {
                'total_phrases': len(self.extracted),
                'dialogue_count': sum(1 for p in self.extracted if p['type'] == 'dialogue'),
                'narrative_count': sum(1 for p in self.extracted if p['type'] == 'narrative'),
                'min_words': self.min_words,
                'max_words': self.max_words
            },
            'phrases': self.extracted
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)
        
        print(f"\n✅ Saved {len(self.extracted)} phrases to {output_path}")
        print(f"   Dialogue: {output_data['metadata']['dialogue_count']}")
        print(f"   Narrative: {output_data['metadata']['narrative_count']}")

def main():
    parser = argparse.ArgumentParser(
        description='Extract phrases from French narrative for language learning'
    )
    parser.add_argument(
        'input',
        type=Path,
        help='Input narrative text file'
    )
    parser.add_argument(
        '--output',
        type=Path,
        default=Path('extracted_phrases_fr.json'),
        help='Output JSON file (default: extracted_phrases_fr.json)'
    )
    parser.add_argument(
        '--min-words',
        type=int,
        default=3,
        help='Minimum words per phrase (default: 3)'
    )
    parser.add_argument(
        '--max-words',
        type=int,
        default=25,
        help='Maximum words per phrase (default: 25)'
    )
    
    args = parser.parse_args()
    
    if not args.input.exists():
        print(f"❌ Error: Input file not found: {args.input}")
        sys.exit(1)
    
    extractor = PhraseExtractor(
        min_words=args.min_words,
        max_words=args.max_words
    )
    
    phrases = extractor.extract_all(args.input)
    extractor.save_json(args.output)
    
    return 0

if __name__ == '__main__':
    sys.exit(main())
