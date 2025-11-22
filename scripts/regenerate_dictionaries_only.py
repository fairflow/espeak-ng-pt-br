#!/usr/bin/env python3
"""Regenerate only dictionaries for all languages (quick fix)."""

import os
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from generate_all_materials import generate_dictionary, LANGUAGE_CONFIGS
from openai import OpenAI

def main():
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("❌ Error: OPENAI_API_KEY not set")
        sys.exit(1)
    
    client = OpenAI(api_key=api_key)
    base_dir = Path(__file__).parent.parent
    
    print("="*60)
    print("📚 Regenerating Dictionaries Only")
    print("="*60)
    
    for lang_code, config in LANGUAGE_CONFIGS.items():
        print(f"\n{'='*60}")
        print(f"{config['name']} ({config['native']})")
        print(f"{'='*60}")
        
        materials_dir = base_dir / "language_materials" / lang_code
        generate_dictionary(lang_code, materials_dir, client)
    
    print(f"\n{'='*60}")
    print("✅ All Dictionaries Complete!")
    print(f"{'='*60}\n")

if __name__ == "__main__":
    main()
