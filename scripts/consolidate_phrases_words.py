#!/usr/bin/env python3
"""
Consolidate phrases-A/B/C/D and words-A/B/C/D into single directories.
Renumbers files sequentially to avoid duplicates.

Example:
  phrases-A/phr-01.txt → phrases/phr-001.txt
  phrases-A/phr-02.txt → phrases/phr-002.txt
  phrases-B/phr-01.txt → phrases/phr-051.txt (if A had 50 files)
"""

import shutil
from pathlib import Path
from typing import List, Tuple

# Base directory
BASE_DIR = Path(__file__).parent.parent / "language_materials"

def get_files_sorted(directory: Path) -> List[Path]:
    """Get all .txt and .json files from directory, sorted."""
    if not directory.exists():
        return []
    
    txt_files = sorted(directory.glob("*.txt"))
    json_files = sorted(directory.glob("*.json"))
    return txt_files + json_files

def consolidate_category(lang_dir: Path, category_prefix: str, levels: List[str] = ['A', 'B', 'C', 'D']) -> None:
    """
    Consolidate category-A/B/C/D into single category directory.
    
    Args:
        lang_dir: Language directory (e.g., language_materials/pt/)
        category_prefix: 'phrases' or 'words'
        levels: List of level suffixes (default: ['A', 'B', 'C', 'D'])
    """
    print(f"\n📁 Consolidating {category_prefix} in {lang_dir.name}/")
    
    # Create target directory
    target_dir = lang_dir / category_prefix
    target_dir.mkdir(exist_ok=True)
    
    # Collect all files from level subdirectories
    all_files: List[Tuple[Path, str]] = []  # [(source_path, level)]
    
    for level in levels:
        source_dir = lang_dir / f"{category_prefix}-{level}"
        if not source_dir.exists():
            print(f"  ⚠️  {source_dir.name}/ not found, skipping")
            continue
        
        files = get_files_sorted(source_dir)
        print(f"  📂 {source_dir.name}/: {len(files)} files")
        
        for f in files:
            all_files.append((f, level))
    
    if not all_files:
        print(f"  ℹ️  No files found to consolidate")
        return
    
    # Renumber and copy files
    counter = 1
    for source_file, level in all_files:
        # Determine file extension
        ext = source_file.suffix
        
        # Generate new filename with zero-padded number
        new_name = f"{category_prefix}-{counter:03d}{ext}"
        target_file = target_dir / new_name
        
        # Copy file (don't delete originals yet for safety)
        shutil.copy2(source_file, target_file)
        print(f"  ✓ {source_file.parent.name}/{source_file.name} → {target_dir.name}/{new_name}")
        
        counter += 1
    
    print(f"  ✅ Consolidated {counter - 1} files into {target_dir.name}/")

def consolidate_language(lang_code: str) -> None:
    """Consolidate phrases and words for a language."""
    lang_dir = BASE_DIR / lang_code
    
    if not lang_dir.exists():
        print(f"⚠️  Language directory not found: {lang_dir}")
        return
    
    print(f"\n{'='*60}")
    print(f"🌍 Processing language: {lang_code.upper()}")
    print(f"{'='*60}")
    
    # Consolidate phrases
    consolidate_category(lang_dir, 'phrases')
    
    # Consolidate words
    consolidate_category(lang_dir, 'words')

def main():
    """Main consolidation process."""
    print("=" * 60)
    print("📦 Phrase & Word File Consolidation")
    print("=" * 60)
    print("\nThis script will:")
    print("  1. Create phrases/ and words/ directories")
    print("  2. Copy files from -A/B/C/D subdirectories")
    print("  3. Renumber sequentially (001, 002, 003...)")
    print("  4. Keep originals intact for safety")
    print("\n⚠️  Review output before deleting old directories!")
    
    response = input("\nProceed? (y/n): ")
    if response.lower() != 'y':
        print("❌ Cancelled")
        return
    
    # Process each language
    languages = ['pt', 'fr']  # Add more as needed
    
    for lang in languages:
        consolidate_language(lang)
    
    print("\n" + "=" * 60)
    print("✅ Consolidation complete!")
    print("=" * 60)
    print("\n📋 Next steps:")
    print("  1. Test the app with new structure")
    print("  2. Verify all files work correctly")
    print("  3. Manually delete old -A/B/C/D directories:")
    print("     rm -rf language_materials/*/phrases-[A-D]")
    print("     rm -rf language_materials/*/words-[A-D]")
    print("  4. Commit changes")

if __name__ == '__main__':
    main()
