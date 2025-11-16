#!/usr/bin/env python3
"""
Difficulty Analyzer for Miolingo Phrases

Analyzes extracted French phrases for linguistic difficulty using multiple criteria.
Grades phrases into levels A, B, C, D suitable for language learners.

Requires: anthropic package for Claude API
Install: pip install anthropic

Usage:
    export ANTHROPIC_API_KEY=your_key_here
    python3 analyze_difficulty.py extracted_phrases_fr.json --output graded_phrases_fr.json
"""

import json
import sys
from pathlib import Path
from typing import List, Dict, Optional
import argparse
from datetime import datetime

try:
    import anthropic
except ImportError:
    print("❌ Error: anthropic package not installed")
    print("   Install with: pip install anthropic")
    sys.exit(1)

DIFFICULTY_CRITERIA = """
Analyze this French phrase for language learning difficulty using these criteria:

**SCORING FACTORS (0-100 scale):**

1. **Vocabulary Frequency (25%):**
   - 0-25: All words in top 500 most common
   - 26-50: Words in top 1500
   - 51-75: Words in top 3000
   - 76-100: Rare words, technical terms, idioms

2. **Grammar Complexity (20%):**
   - 0-25: Simple present, SVO order, no subordinates
   - 26-50: One subordinate clause, basic conjunctions
   - 51-75: Multiple clauses, relative pronouns
   - 76-100: Passive voice, complex subordination, indirect speech

3. **Sentence Length (15%):**
   - 0-25: 3-8 words
   - 26-50: 8-12 words
   - 51-75: 12-18 words
   - 76-100: 18+ words

4. **Verb Tense Difficulty (20%):**
   - 0-25: Present, near future (aller + infinitive)
   - 26-50: Passé composé, future simple
   - 51-75: Imparfait, conditional, pluperfect
   - 76-100: Subjunctive, literary tenses

5. **Phonetic Complexity (10%):**
   - 0-25: Basic sounds, no liaisons
   - 26-50: Simple nasal vowels, basic R sounds
   - 51-75: Complex liaisons, [œ], [y] sounds
   - 76-100: Consonant clusters, rapid speech patterns

6. **Idiomatic/Figurative Content (5%):**
   - 0-25: Literal, transparent meaning
   - 26-50: Common expressions
   - 51-75: Idioms, metaphors
   - 76-100: Abstract, culturally-specific

7. **Cultural Context Required (5%):**
   - 0-25: Universal concepts
   - 26-50: General French culture
   - 51-75: Regional/historical references
   - 76-100: Literary/specialized knowledge

**OUTPUT FORMAT:**
```json
{
  "phrase": "[the phrase]",
  "overall_score": [0-100],
  "difficulty_level": "[A/B/C/D]",
  "scores": {
    "vocabulary": [0-100],
    "grammar": [0-100],
    "length": [0-100],
    "verb_tense": [0-100],
    "phonetics": [0-100],
    "idiomatic": [0-100],
    "cultural": [0-100]
  },
  "analysis": {
    "key_challenges": ["list", "of", "challenging", "elements"],
    "recommended_prerequisites": ["concepts", "learner", "should", "know"],
    "practice_focus": "main skill to practice"
  }
}
```

**DIFFICULTY LEVEL MAPPING:**
- A: 0-25 (Beginner)
- B: 26-50 (Elementary)
- C: 51-75 (Intermediate)
- D: 76-100 (Advanced)
"""

class DifficultyAnalyzer:
    def __init__(self, api_key: str):
        self.client = anthropic.Anthropic(api_key=api_key)
        self.analyzed_phrases = []
        
    def analyze_phrase(self, phrase_data: Dict) -> Dict:
        """Analyze a single phrase using Claude API."""
        phrase = phrase_data['text']
        context = f"Scene: {phrase_data['scene_title']}, Type: {phrase_data['type']}"
        
        prompt = f"{DIFFICULTY_CRITERIA}\n\nPHRASE TO ANALYZE:\n\"{phrase}\"\n\nCONTEXT: {context}\n\nProvide your analysis in JSON format as specified above."
        
        try:
            message = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=1024,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            # Extract JSON from response
            response_text = message.content[0].text
            
            # Try to find JSON in response
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            
            if json_start == -1 or json_end == 0:
                raise ValueError("No JSON found in response")
            
            json_str = response_text[json_start:json_end]
            analysis = json.loads(json_str)
            
            # Add original metadata
            analysis['original_scene'] = phrase_data['scene_number']
            analysis['original_type'] = phrase_data['type']
            
            return analysis
            
        except Exception as e:
            print(f"   ⚠️  Error analyzing phrase '{phrase[:40]}...': {e}")
            # Return default analysis
            return {
                'phrase': phrase,
                'overall_score': 50,
                'difficulty_level': 'B',
                'error': str(e),
                'original_scene': phrase_data['scene_number'],
                'original_type': phrase_data['type']
            }
    
    def analyze_batch(self, phrases: List[Dict], batch_size: int = 10) -> List[Dict]:
        """Analyze a batch of phrases."""
        total = len(phrases)
        
        for i, phrase_data in enumerate(phrases, 1):
            print(f"   [{i}/{total}] Analyzing: {phrase_data['text'][:50]}...")
            
            analysis = self.analyze_phrase(phrase_data)
            self.analyzed_phrases.append(analysis)
            
            # Progress indicator
            if i % batch_size == 0:
                print(f"   ✓ Completed {i}/{total} phrases")
        
        return self.analyzed_phrases
    
    def save_results(self, output_path: Path):
        """Save analyzed phrases to JSON."""
        # Calculate statistics
        level_counts = {
            'A': sum(1 for p in self.analyzed_phrases if p.get('difficulty_level') == 'A'),
            'B': sum(1 for p in self.analyzed_phrases if p.get('difficulty_level') == 'B'),
            'C': sum(1 for p in self.analyzed_phrases if p.get('difficulty_level') == 'C'),
            'D': sum(1 for p in self.analyzed_phrases if p.get('difficulty_level') == 'D'),
        }
        
        avg_score = sum(p.get('overall_score', 0) for p in self.analyzed_phrases) / len(self.analyzed_phrases) if self.analyzed_phrases else 0
        
        output_data = {
            'metadata': {
                'total_phrases': len(self.analyzed_phrases),
                'analyzed_date': datetime.now().isoformat(),
                'average_difficulty_score': round(avg_score, 2),
                'distribution': level_counts
            },
            'phrases': self.analyzed_phrases
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)
        
        print(f"\n✅ Analysis complete!")
        print(f"   Total phrases: {len(self.analyzed_phrases)}")
        print(f"   Level A: {level_counts['A']}")
        print(f"   Level B: {level_counts['B']}")
        print(f"   Level C: {level_counts['C']}")
        print(f"   Level D: {level_counts['D']}")
        print(f"   Average score: {round(avg_score, 2)}")
        print(f"\n💾 Results saved to: {output_path}")

def main():
    parser = argparse.ArgumentParser(
        description='Analyze difficulty of extracted French phrases using Claude API'
    )
    parser.add_argument(
        'input',
        type=Path,
        help='Input JSON file with extracted phrases'
    )
    parser.add_argument(
        '--output',
        type=Path,
        default=Path('graded_phrases_fr.json'),
        help='Output JSON file (default: graded_phrases_fr.json)'
    )
    parser.add_argument(
        '--api-key',
        help='Anthropic API key (or set ANTHROPIC_API_KEY environment variable)'
    )
    parser.add_argument(
        '--limit',
        type=int,
        help='Limit number of phrases to analyze (for testing)'
    )
    
    args = parser.parse_args()
    
    if not args.input.exists():
        print(f"❌ Error: Input file not found: {args.input}")
        sys.exit(1)
    
    # Get API key
    api_key = args.api_key or os.environ.get('ANTHROPIC_API_KEY')
    if not api_key:
        print("❌ Error: No API key provided")
        print("   Set ANTHROPIC_API_KEY environment variable or use --api-key")
        sys.exit(1)
    
    # Load phrases
    print(f"📖 Loading phrases from {args.input}")
    with open(args.input, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    phrases = data['phrases']
    
    if args.limit:
        phrases = phrases[:args.limit]
        print(f"   ⚠️  Limited to first {args.limit} phrases for testing")
    
    print(f"   Found {len(phrases)} phrases to analyze\n")
    
    # Analyze
    analyzer = DifficultyAnalyzer(api_key)
    print("🔬 Starting analysis with Claude API...")
    
    analyzer.analyze_batch(phrases)
    analyzer.save_results(args.output)
    
    return 0

if __name__ == '__main__':
    import os
    sys.exit(main())
