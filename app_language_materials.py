"""
Language materials discovery and loading.

This module provides functionality to browse and load built-in language
learning materials (phrases and words) organized by language and difficulty level.
"""

from pathlib import Path
from typing import Dict, List
import streamlit as st

DATA_DIR = Path(__file__).parent / "language_materials"


@st.cache_data
def get_available_languages() -> List[str]:
    """Get list of languages with available materials.
    
    Returns:
        List of language codes (e.g., ['fr', 'pt', 'nl'])
    """
    if not DATA_DIR.exists():
        return []
    
    return sorted([d.name for d in DATA_DIR.iterdir() if d.is_dir() and not d.name.startswith('.')])


@st.cache_data
def get_language_structure(language: str) -> Dict[str, List[str]]:
    """Get complete directory structure for a language.
    
    Args:
        language: Language code (e.g., 'fr', 'pt')
    
    Returns:
        Dictionary mapping category names to lists of filenames:
        {
            'phrases-A': ['phr-01.txt', 'phr-02.txt'],
            'words-A': ['words-01.txt'],
            ...
        }
    """
    lang_dir = DATA_DIR / language
    if not lang_dir.exists():
        return {}
    
    structure = {}
    for category_dir in sorted(lang_dir.iterdir()):
        if category_dir.is_dir() and not category_dir.name.startswith('.'):
            files = sorted([f.name for f in category_dir.glob("*.txt")])
            if files:
                structure[category_dir.name] = files
    
    return structure


@st.cache_data
def get_file_metadata(language: str, category: str, filename: str) -> Dict:
    """Get metadata about a phrase/word file.
    
    Args:
        language: Language code (e.g., 'fr', 'pt')
        category: Category name (e.g., 'phrases-A', 'words-B')
        filename: File name (e.g., 'phr-01.txt')
    
    Returns:
        Dictionary with file metadata:
        {
            'path': Path object,
            'line_count': 50,
            'has_translations': True,
            'has_ipa': True,
            'preview': ['first', 'few', 'lines']
        }
    """
    file_path = DATA_DIR / language / category / filename
    
    if not file_path.exists():
        return {}
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            all_lines = f.readlines()
        
        # Filter out comments and empty lines for analysis
        content_lines = [
            line.strip() for line in all_lines 
            if line.strip() and not line.strip().startswith('#')
        ]
        
        if not content_lines:
            return {
                'path': file_path,
                'line_count': 0,
                'has_translations': False,
                'has_ipa': False,
                'preview': []
            }
        
        # Analyze format from first content line
        sample = content_lines[0]
        has_translations = '|' in sample
        has_ipa = '[' in sample and ']' in sample
        
        # Get preview (first 3 content lines)
        preview = content_lines[:3]
        
        return {
            'path': file_path,
            'line_count': len(content_lines),
            'has_translations': has_translations,
            'has_ipa': has_ipa,
            'preview': preview
        }
    except Exception as e:
        return {
            'path': file_path,
            'line_count': 0,
            'has_translations': False,
            'has_ipa': False,
            'preview': [],
            'error': str(e)
        }


@st.cache_data
def load_phrase_file(file_path_str: str) -> List[Dict]:
    """Load and parse a phrase/word file.
    
    Args:
        file_path_str: String representation of file path (for caching)
    
    Returns:
        List of phrase dictionaries:
        [
            {'text': 'bonjour', 'translation': 'hello', 'ipa': '[bɔ̃ʒuʁ]'},
            ...
        ]
    """
    file_path = Path(file_path_str)
    
    # Security: Ensure path is within DATA_DIR
    try:
        file_path_resolved = file_path.resolve()
        data_dir_resolved = DATA_DIR.resolve()
        
        if not str(file_path_resolved).startswith(str(data_dir_resolved)):
            raise ValueError("Invalid file path: outside language materials directory")
    except Exception as e:
        raise ValueError(f"Invalid file path: {e}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    phrases = []
    for line in content.split('\n'):
        line = line.strip()
        
        # Skip comments and empty lines
        if not line or line.startswith('#'):
            continue
        
        # Parse format: "phrase | translation | [ipa]"
        if '|' in line:
            parts = [p.strip() for p in line.split('|')]
            phrases.append({
                'text': parts[0],
                'translation': parts[1] if len(parts) > 1 else None,
                'ipa': parts[2] if len(parts) > 2 else None
            })
        else:
            # Simple format: just the text
            phrases.append({
                'text': line,
                'translation': None,
                'ipa': None
            })
    
    return phrases


def format_category_name(category: str) -> str:
    """Format category name for display.
    
    Args:
        category: Raw category name (e.g., 'phrases-A', 'words-C')
    
    Returns:
        Formatted display name (e.g., '📝 Phrases - Level A (Beginner)')
    """
    category_map = {
        'phrases-A': '📝 Phrases - Level A (Beginner)',
        'phrases-B': '📝 Phrases - Level B (Intermediate)',
        'phrases-C': '📝 Phrases - Level C (Advanced)',
        'phrases-D': '📝 Phrases - Level D (Expert)',
        'words-A': '📖 Words - Level A (Beginner)',
        'words-B': '📖 Words - Level B (Intermediate)',
        'words-C': '📖 Words - Level C (Advanced)',
        'words-D': '📖 Words - Level D (Expert)',
    }
    
    return category_map.get(category, category)


def format_language_name(lang_code: str) -> str:
    """Format language code for display.
    
    Args:
        lang_code: Language code (e.g., 'fr', 'pt')
    
    Returns:
        Formatted display name with flag (e.g., '🇫🇷 French')
    """
    language_map = {
        'fr': '🇫🇷 French',
        'pt': '🇵🇹 Portuguese',
        'nl': '🇳🇱 Dutch',
    }
    
    return language_map.get(lang_code, lang_code.upper())
