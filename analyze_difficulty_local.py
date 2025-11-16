#!/usr/bin/env python3
"""
Local Difficulty Analyzer for Miolingo Phrases

Analyzes French phrases using rule-based criteria (no API calls needed).
Grades phrases into levels A, B, C, D for language learners.

Usage:
    python3 analyze_difficulty_local.py extracted_phrases_fr.json --output graded_phrases_fr.json
"""

import json
import re
from pathlib import Path
from typing import List, Dict, Set
from datetime import datetime
import argparse

# French verb patterns by tense (for recognition)
VERB_PATTERNS = {
    'present': {
        'pattern': r'\b(suis|es|est|sommes|êtes|sont|ai|as|a|avons|avez|ont|vais|vas|va|allons|allez|vont|fais|fait|faisons|faites|font|peux|peut|pouvons|peuvent|veux|veut|voulons|voulez|veulent|dois|doit|devons|devez|doivent)\b',
        'score': 10
    },
    'futur_proche': {
        'pattern': r'\b(vais|vas|va|allons|allez|vont)\s+\w+er\b',
        'score': 25
    },
    'passe_compose': {
        'pattern': r'\b(ai|as|a|avons|avez|ont|suis|es|est|sommes|êtes|sont)\s+(été|eu|fait|allé|allée|allés|allées|vu|dit|pris|mis|venu|venue|venus|venues)\b',
        'score': 35
    },
    'imparfait': {
        'pattern': r'\b\w+(ais|ait|ions|iez|aient)\b',
        'score': 55
    },
    'conditionnel': {
        'pattern': r'\b\w+(rais|rait|rions|riez|raient)\b',
        'score': 65
    },
    'subjonctif': {
        'pattern': r'\b(que|qu\'|afin que|pour que|bien que|quoi que|pourvu que|jusqu\'à ce que|avant que|sans que|il faut que|il est nécessaire que|pour peu que)\s+\w+\s+(sois|soit|soyons|soyez|soient|aie|aies|ait|ayons|ayez|aient|fasse|fasses|fassions|fassiez|fassent|puisse|puisses|puissions|puissiez|puissent|veuille|veuilles|veuillions|veuilliez|veuillent|accepte|acceptent|inspire|survive|apprenne|apprennent|oublie|serve|faille|comprenne|comprît|eût|eussent|pût|pussent|fût|fussent|vécussent|tombât|connût|demeurât)\b',
        'score': 90
    }
}

# Common French words by frequency tier (simplified)
COMMON_WORDS_A = {
    'je', 'tu', 'il', 'elle', 'nous', 'vous', 'ils', 'elles',
    'le', 'la', 'les', 'un', 'une', 'des',
    'et', 'ou', 'mais', 'si', 'oui', 'non',
    'être', 'avoir', 'faire', 'aller', 'dire', 'pouvoir', 'vouloir', 'voir',
    'bon', 'grand', 'petit', 'jeune', 'vieux', 'nouveau',
    'bonjour', 'merci', 's\'il vous plaît', 'au revoir', 'salut',
    'café', 'pain', 'eau', 'maison', 'rue', 'jour', 'nuit',
    'combien', 'où', 'quand', 'comment', 'pourquoi', 'qui', 'quoi',
    'ça', 'va', 'bien', 'mal', 'très', 'trop', 'peu'
}

COMMON_WORDS_B = {
    'train', 'gare', 'voyage', 'billet', 'arriver', 'partir',
    'acheter', 'vendre', 'coûter', 'payer', 'prix',
    'demain', 'hier', 'aujourd\'hui', 'maintenant', 'bientôt',
    'parler', 'écouter', 'regarder', 'chercher', 'trouver',
    'voiture', 'vélo', 'métro', 'bus', 'avion',
    'restaurant', 'hôtel', 'magasin', 'marché', 'banque',
    'manger', 'boire', 'dormir', 'travailler', 'étudier'
}

IDIOMATIC_PHRASES = [
    r'ça va', r'n\'est-ce pas', r'il faut', r'd\'accord', r'bien sûr',
    r'en train de', r'avoir besoin', r'avoir envie', r'avoir peur',
    r'faire attention', r'faire beau', r'faire froid'
]

ACADEMIC_VOCABULARY = {
    'dialectique', 'ontologique', 'herméneutique', 'épistémologique',
    'archétypale', 'psychopompe', 'cosmologie', 'alchimique',
    'métaphore', 'parabole', 'littéraire', 'narrativité',
    'transcende', 'modalité', 'résonance', 'authentique',
    'existentiel', 'philosophique', 'abstraction', 'temporalité',
    'fragmentation', 'prolepse', 'intertextuel', 'sémantique',
    'prométhéenne', 'tellurique', 'chamane', 'paléolithique',
    'eucharistie', 'rituel', 'catalyseur', 'cristallisation',
    'symbolique', 'ambiguïté', 'merveilleux', 'rationnel',
    'mélancolique', 'millénaire', 'continuité', 'fragilité',
    'définitif', 'perpétuellement', 'libératrice', 'instabilité'
}

class LocalDifficultyAnalyzer:
    def __init__(self):
        self.analyzed_phrases = []
        
    def count_words(self, text: str) -> int:
        """Count words in text."""
        words = re.findall(r'\b\w+\b', text.lower())
        return len(words)
    
    def analyze_vocabulary(self, text: str) -> Dict:
        """Analyze vocabulary difficulty."""
        words = set(re.findall(r'\b\w+\b', text.lower()))
        
        common_a = len(words & COMMON_WORDS_A)
        common_b = len(words & COMMON_WORDS_B)
        academic = len(words & ACADEMIC_VOCABULARY)
        total_words = len(words)
        
        if total_words == 0:
            return {'score': 50, 'common_ratio': 0}
        
        common_ratio = (common_a + common_b) / total_words
        
        # High common word ratio = lower difficulty
        if common_ratio > 0.8:
            score = 15
        elif common_ratio > 0.6:
            score = 30
        elif common_ratio > 0.4:
            score = 50
        else:
            score = 70
        
        # Boost score for academic vocabulary
        if academic > 0:
            score = min(score + (academic * 15), 95)
            
        return {
            'score': score,
            'common_ratio': round(common_ratio, 2),
            'total_words': total_words,
            'common_a': common_a,
            'common_b': common_b,
            'academic': academic
        }
    
    def analyze_grammar(self, text: str) -> Dict:
        """Analyze grammatical complexity."""
        score = 20  # Base score
        features = []
        
        # Count subordinate clauses
        subordinates = len(re.findall(r'\b(que|qui|où|dont|quand|si|parce que|bien que|pour que)\b', text.lower()))
        if subordinates > 0:
            score += subordinates * 15
            features.append(f'{subordinates} subordinate clause(s)')
        
        # Check for negation (slightly complex)
        if re.search(r'\bne\b.*\b(pas|jamais|plus|rien|personne)\b', text.lower()):
            score += 10
            features.append('negation')
        
        # Check for relative pronouns
        if re.search(r'\b(lequel|laquelle|lesquels|lesquelles|auquel|duquel)\b', text.lower()):
            score += 20
            features.append('complex relative pronouns')
        
        return {
            'score': min(score, 100),
            'features': features
        }
    
    def analyze_verb_tense(self, text: str) -> Dict:
        """Analyze verb tense difficulty."""
        max_score = 10
        tense_found = 'present'
        
        for tense, info in VERB_PATTERNS.items():
            if re.search(info['pattern'], text.lower(), re.IGNORECASE):
                if info['score'] > max_score:
                    max_score = info['score']
                    tense_found = tense
        
        # Subjunctive is D-level - boost score
        if tense_found == 'subjonctif':
            max_score = 95
        
        return {
            'score': max_score,
            'tense': tense_found
        }
    
    def analyze_length(self, text: str) -> Dict:
        """Analyze sentence length difficulty."""
        word_count = self.count_words(text)
        
        if word_count <= 8:
            score = 15
            category = 'short'
        elif word_count <= 12:
            score = 35
            category = 'medium'
        elif word_count <= 18:
            score = 60
            category = 'long'
        elif word_count <= 25:
            score = 75
            category = 'very long'
        else:
            score = 95  # Extra long sentences are D-level
            category = 'extra long'
        
        return {
            'score': score,
            'word_count': word_count,
            'category': category
        }
    
    def analyze_idioms(self, text: str) -> Dict:
        """Check for idiomatic expressions."""
        score = 0
        found = []
        
        for pattern in IDIOMATIC_PHRASES:
            if re.search(pattern, text.lower()):
                score += 30
                found.append(pattern)
        
        return {
            'score': min(score, 70),
            'found': found
        }
    
    def analyze_phonetics(self, text: str) -> Dict:
        """Estimate phonetic difficulty (simplified)."""
        score = 20  # Base score
        features = []
        
        # Check for nasals
        nasals = len(re.findall(r'[aeiou]n[^aeiou]|[aeiou]m[^aeiou]', text.lower()))
        if nasals > 0:
            score += min(nasals * 5, 20)
            features.append(f'{nasals} nasal(s)')
        
        # Check for R sounds
        r_sounds = len(re.findall(r'r', text.lower()))
        if r_sounds > 2:
            score += 10
            features.append('multiple R sounds')
        
        # Check for liaison contexts (simplified)
        if re.search(r'\w+[st]\s+[aeiou]', text.lower()):
            score += 10
            features.append('liaison context')
        
        return {
            'score': min(score, 100),
            'features': features
        }
    
    def calculate_overall_score(self, analyses: Dict) -> int:
        """Calculate weighted overall difficulty score."""
        weights = {
            'vocabulary': 0.35,  # Increased for rare/academic words
            'grammar': 0.15,
            'length': 0.25,      # Increased for long complex sentences
            'verb_tense': 0.15,
            'phonetics': 0.05,
            'idioms': 0.05
        }
        
        overall = 0
        for factor, weight in weights.items():
            if factor in analyses:
                overall += analyses[factor]['score'] * weight
        
        return round(overall)
    
    def assign_difficulty_level(self, score: int, verb_tense: str = '') -> str:
        """Assign A/B/C/D level based on score."""
        # OVERRIDE: Any subjunctive = automatic D-level
        if verb_tense == 'subjonctif':
            return 'D'
        
        if score <= 35:
            return 'A'
        elif score <= 55:
            return 'B'
        elif score <= 65:
            return 'C'
        else:
            return 'D'
    
    def analyze_phrase(self, phrase_data: Dict) -> Dict:
        """Analyze a single phrase."""
        phrase = phrase_data['text']
        
        # Run all analyses
        vocab = self.analyze_vocabulary(phrase)
        grammar = self.analyze_grammar(phrase)
        verb_tense = self.analyze_verb_tense(phrase)
        length = self.analyze_length(phrase)
        idioms = self.analyze_idioms(phrase)
        phonetics = self.analyze_phonetics(phrase)
        
        # Calculate overall score
        analyses = {
            'vocabulary': vocab,
            'grammar': grammar,
            'verb_tense': verb_tense,
            'length': length,
            'idioms': idioms,
            'phonetics': phonetics
        }
        
        overall_score = self.calculate_overall_score(analyses)
        detected_tense = verb_tense.get('tense', '')
        difficulty_level = self.assign_difficulty_level(overall_score, detected_tense)
        
        return {
            'phrase': phrase,
            'overall_score': overall_score,
            'difficulty_level': difficulty_level,
            'scores': {
                'vocabulary': vocab['score'],
                'grammar': grammar['score'],
                'length': length['score'],
                'verb_tense': verb_tense['score'],
                'phonetics': phonetics['score'],
                'idiomatic': idioms['score']
            },
            'analysis': {
                'word_count': length['word_count'],
                'common_words_ratio': vocab.get('common_ratio', 0),
                'verb_tense': verb_tense.get('tense', 'unknown'),
                'grammar_features': grammar.get('features', []),
                'phonetic_features': phonetics.get('features', []),
                'idioms_found': idioms.get('found', [])
            },
            'original_scene': phrase_data['scene_number'],
            'original_type': phrase_data['type']
        }
    
    def analyze_batch(self, phrases: List[Dict]) -> List[Dict]:
        """Analyze a batch of phrases."""
        total = len(phrases)
        
        for i, phrase_data in enumerate(phrases, 1):
            if i % 50 == 0 or i == 1:
                print(f"   [{i}/{total}] Analyzing phrases...")
            
            analysis = self.analyze_phrase(phrase_data)
            self.analyzed_phrases.append(analysis)
        
        return self.analyzed_phrases
    
    def save_results(self, output_path: Path):
        """Save analyzed phrases to JSON."""
        # Calculate statistics
        level_counts = {
            'A': sum(1 for p in self.analyzed_phrases if p['difficulty_level'] == 'A'),
            'B': sum(1 for p in self.analyzed_phrases if p['difficulty_level'] == 'B'),
            'C': sum(1 for p in self.analyzed_phrases if p['difficulty_level'] == 'C'),
            'D': sum(1 for p in self.analyzed_phrases if p['difficulty_level'] == 'D'),
        }
        
        avg_score = sum(p['overall_score'] for p in self.analyzed_phrases) / len(self.analyzed_phrases) if self.analyzed_phrases else 0
        
        output_data = {
            'metadata': {
                'total_phrases': len(self.analyzed_phrases),
                'analyzed_date': datetime.now().isoformat(),
                'average_difficulty_score': round(avg_score, 2),
                'distribution': level_counts,
                'analysis_method': 'rule-based (local, no API)'
            },
            'phrases': self.analyzed_phrases
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)
        
        print(f"\n✅ Analysis complete!")
        print(f"   Total phrases: {len(self.analyzed_phrases)}")
        print(f"   Level A: {level_counts['A']} ({level_counts['A']/len(self.analyzed_phrases)*100:.1f}%)")
        print(f"   Level B: {level_counts['B']} ({level_counts['B']/len(self.analyzed_phrases)*100:.1f}%)")
        print(f"   Level C: {level_counts['C']} ({level_counts['C']/len(self.analyzed_phrases)*100:.1f}%)")
        print(f"   Level D: {level_counts['D']} ({level_counts['D']/len(self.analyzed_phrases)*100:.1f}%)")
        print(f"   Average score: {round(avg_score, 2)}")
        print(f"\n💾 Results saved to: {output_path}")

def main():
    parser = argparse.ArgumentParser(
        description='Analyze difficulty of French phrases using rule-based criteria (no API calls)'
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
    
    args = parser.parse_args()
    
    if not args.input.exists():
        print(f"❌ Error: Input file not found: {args.input}")
        return 1
    
    # Load phrases
    print(f"📖 Loading phrases from {args.input}")
    with open(args.input, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    phrases = data['phrases']
    print(f"   Found {len(phrases)} phrases to analyze\n")
    
    # Analyze
    analyzer = LocalDifficultyAnalyzer()
    print("🔬 Starting rule-based analysis...")
    
    analyzer.analyze_batch(phrases)
    analyzer.save_results(args.output)
    
    return 0

if __name__ == '__main__':
    import sys
    sys.exit(main())
