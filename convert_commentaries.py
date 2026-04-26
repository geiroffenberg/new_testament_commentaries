#!/usr/bin/env python3
"""
Convert SWORD commentary modules to chapter-based JSON format.
Usage: python3 convert_commentaries.py
"""

import json
import os
import re
from pathlib import Path
from xml.etree import ElementTree as ET
from typing import Dict, List, Tuple

# Map SWORD module names to internal IDs
SWORD_MODULES = {
    'Clarke': 'clarke',
    'JFB': 'jfb',
    'RWP': 'rwp',
    'MHCC': 'mhcc',
}

# New Testament books in order
NT_BOOKS = [
    'Matthew', 'Mark', 'Luke', 'John',
    'Acts',
    'Romans', '1 Corinthians', '2 Corinthians', 'Galatians', 'Ephesians',
    'Philippians', 'Colossians', '1 Thessalonians', '2 Thessalonians',
    '1 Timothy', '2 Timothy', 'Titus', 'Philemon',
    'Hebrews',
    'James',
    '1 Peter', '2 Peter',
    '1 John', '2 John', '3 John',
    'Jude',
    'Revelation',
]

def parse_verse_reference(ref: str) -> Tuple[str, int, int, int]:
    """
    Parse a verse reference like 'Matthew 5:3' or 'Rom 8:1'
    Returns: (book_name, chapter, verse_start, verse_end)
    """
    # Normalize common abbreviations
    abbrev_map = {
        'Matt': 'Matthew', 'Mark': 'Mark', 'Lk': 'Luke', 'Jn': 'John',
        'Rom': 'Romans', '1 Cor': '1 Corinthians', '2 Cor': '2 Corinthians',
        'Gal': 'Galatians', 'Eph': 'Ephesians', 'Phil': 'Philippians',
        'Col': 'Colossians', '1 Thess': '1 Thessalonians', '2 Thess': '2 Thessalonians',
        '1 Tim': '1 Timothy', '2 Tim': '2 Timothy', 'Tit': 'Titus',
        'Phlm': 'Philemon', 'Heb': 'Hebrews', 'Jas': 'James',
        '1 Pet': '1 Peter', '2 Pet': '2 Peter',
        '1 Jn': '1 John', '2 Jn': '2 John', '3 Jn': '3 John',
        'Jude': 'Jude', 'Rev': 'Revelation',
    }

    # Try to extract book, chapter, verse
    match = re.match(r'(\d?\s*\w+(?:\s+\w+)?)\s+(\d+):(\d+)(?:-(\d+))?', ref.strip())
    if not match:
        return None

    book_part, chapter, verse_start, verse_end = match.groups()
    book_part = book_part.strip()

    # Normalize book name
    for abbrev, full_name in abbrev_map.items():
        if book_part.lower().startswith(abbrev.lower()):
            book_part = full_name
            break

    chapter = int(chapter)
    verse_start = int(verse_start)
    verse_end = int(verse_end) if verse_end else verse_start

    return (book_part, chapter, verse_start, verse_end)

def extract_text_from_osis(element) -> str:
    """
    Extract plain text from OSIS XML element, handling nested tags.
    """
    text_parts = []
    
    if element.text:
        text_parts.append(element.text)
    
    for child in element:
        text_parts.append(extract_text_from_osis(child))
        if child.tail:
            text_parts.append(child.tail)
    
    return ''.join(text_parts).strip()

def load_sword_module(module_dir: str) -> Dict:
    """
    Load a SWORD commentary module and extract verse entries.
    Returns dict: {verse_reference: commentary_text}
    """
    commentaries = {}
    
    # Look for .osis.xml or similar files
    osis_files = list(Path(module_dir).glob('*.osis.xml')) or \
                 list(Path(module_dir).glob('*.xml'))
    
    if not osis_files:
        print(f"  Warning: No OSIS XML files found in {module_dir}")
        return commentaries
    
    for osis_file in osis_files:
        print(f"  Parsing {osis_file.name}...")
        try:
            tree = ET.parse(osis_file)
            root = tree.getroot()
            
            # OSIS structure typically has osisText > div[type=book] > div[type=chapter] > verse
            # or osisText > div > div with osisID attributes
            
            for verse_elem in root.iter('verse'):
                osis_id = verse_elem.get('osisID')
                if not osis_id:
                    continue
                
                # Extract commentary text
                text = extract_text_from_osis(verse_elem)
                if text:
                    commentaries[osis_id] = text
        
        except Exception as e:
            print(f"  Error parsing {osis_file}: {e}")
    
    return commentaries

def organize_by_chapter(commentaries: Dict) -> Dict:
    """
    Reorganize commentary entries by book/chapter.
    Returns: {book: {chapter: {verse: text}}}
    """
    organized = {}
    
    for verse_ref, text in commentaries.items():
        parsed = parse_verse_reference(verse_ref)
        if not parsed:
            continue
        
        book, chapter, verse_start, verse_end = parsed
        
        if book not in organized:
            organized[book] = {}
        
        if chapter not in organized[book]:
            organized[book][chapter] = {}
        
        # Store with verse key (use verse_start for single verses)
        organized[book][chapter][verse_start] = text
    
    return organized

def save_json_structure(output_dir: str, module_id: str, commentaries: Dict):
    """
    Save commentary data as chapter-based JSON files.
    Structure: output_dir/{module_id}/{book}/{chapter}.json
    """
    module_dir = Path(output_dir) / module_id
    module_dir.mkdir(parents=True, exist_ok=True)
    
    for book, chapters in commentaries.items():
        book_dir = module_dir / book
        book_dir.mkdir(parents=True, exist_ok=True)
        
        for chapter, verses in chapters.items():
            chapter_file = book_dir / f"{chapter}.json"
            
            # Save as chapter-based JSON
            chapter_data = {
                'book': book,
                'chapter': chapter,
                'verses': verses,
            }
            
            with open(chapter_file, 'w', encoding='utf-8') as f:
                json.dump(chapter_data, f, indent=2, ensure_ascii=False)
            
            print(f"    Saved {book} Chapter {chapter}")

def main():
    project_dir = Path(__file__).parent
    assets_dir = project_dir / 'assets' / 'commentaries'
    output_dir = project_dir / 'assets' / 'commentaries_json'
    
    if not assets_dir.exists():
        print(f"Error: {assets_dir} does not exist.")
        print("Run download_commentaries.sh first.")
        return
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    for sword_name, internal_id in SWORD_MODULES.items():
        module_path = assets_dir / sword_name
        
        if not module_path.exists():
            print(f"Warning: {sword_name} module not found at {module_path}")
            continue
        
        print(f"\nProcessing {sword_name}...")
        commentaries = load_sword_module(str(module_path))
        
        if not commentaries:
            print(f"  No commentaries extracted from {sword_name}")
            continue
        
        print(f"  Found {len(commentaries)} commentary entries")
        
        organized = organize_by_chapter(commentaries)
        save_json_structure(str(output_dir), internal_id, organized)
        
        print(f"  ✓ Saved {sword_name} commentary data")
    
    print(f"\nDone! Commentary JSON files are in: {output_dir}")
    print("Update pubspec.yaml to include these as assets if needed.")

if __name__ == '__main__':
    main()
