#!/usr/bin/env python3
"""
Extract Clarke's Commentary from SWORD zCom module and save as chapter-based JSON.

Usage:
    python3 extract_clarke.py

Reads:  assets/commentaries/Clarke.zip
Writes: assets/commentaries_json/clarke/{BookName}/{chapter}.json
"""

import json
import re
import struct
import subprocess
import zipfile
from pathlib import Path

# Maps WEB book names → diatheke abbreviations (Clarke uses KJV book naming)
BOOK_MAP = [
    ('Matthew',          'Matt',   28),
    ('Mark',             'Mark',   16),
    ('Luke',             'Luke',   24),
    ('John',             'John',   21),
    ('Acts',             'Acts',   28),
    ('Romans',           'Rom',    16),
    ('1 Corinthians',    '1Cor',   16),
    ('2 Corinthians',    '2Cor',   13),
    ('Galatians',        'Gal',     6),
    ('Ephesians',        'Eph',     6),
    ('Philippians',      'Phil',    4),
    ('Colossians',       'Col',     4),
    ('1 Thessalonians',  '1Thess',  5),
    ('2 Thessalonians',  '2Thess',  3),
    ('1 Timothy',        '1Tim',    6),
    ('2 Timothy',        '2Tim',    4),
    ('Titus',            'Titus',   3),
    ('Philemon',         'Phlm',    1),
    ('Hebrews',          'Heb',    13),
    ('James',            'Jas',     5),
    ('1 Peter',          '1Pet',    5),
    ('2 Peter',          '2Pet',    3),
    ('1 John',           '1John',   5),
    ('2 John',           '2John',   1),
    ('3 John',           '3John',   1),
    ('Jude',             'Jude',    1),
    ('Revelation',       'Rev',    22),
]

SWORD_PATH = '/tmp/sword_test'
OUTPUT_DIR = Path('assets/commentaries_json/clarke')


def strip_osis(text: str) -> str:
    """Strip OSIS/XML markup and clean up whitespace."""
    # Remove <reference ...>text</reference> but keep text
    text = re.sub(r'<reference[^>]*>([^<]*)</reference>', r'\1', text)
    # Remove all remaining XML/HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    # Remove trailing "(Clarke)" attribution
    text = re.sub(r'\(Clarke\)\s*$', '', text)
    # Collapse multiple whitespace
    text = re.sub(r'[ \t]+', ' ', text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()


def get_chapter_verse_count(abbrev: str, chapter: int) -> int:
    """Ask diatheke how many verses exist in a chapter by trying the last known count."""
    # Try up to verse 50 to find how many verses exist
    for v in range(50, 0, -1):
        result = subprocess.run(
            ['diatheke', '-b', 'Clarke', '-k', f'{abbrev} {chapter}:{v}'],
            capture_output=True, text=True, env={'SWORD_PATH': SWORD_PATH}
        )
        if result.stdout.strip() and not result.stdout.startswith(f'{abbrev} {chapter}:{v}: \n'):
            return v
    return 0


def extract_chapter(abbrev: str, book_name: str, chapter: int) -> dict[str, str]:
    """Extract all verse commentaries for a single chapter using diatheke."""
    # Use range query: e.g. "Matt 5:1-48"
    # We'll try up to 200 verses to catch any chapter
    range_key = f'{abbrev} {chapter}:1-200'
    result = subprocess.run(
        ['diatheke', '-b', 'Clarke', '-k', range_key],
        capture_output=True, text=True,
        env={'SWORD_PATH': SWORD_PATH, 'PATH': '/usr/bin:/bin'}
    )

    verses: dict[str, str] = {}
    current_verse: str | None = None
    current_lines: list[str] = []

    for line in result.stdout.splitlines():
        # Each verse entry starts with "BookName Chapter:Verse: ..."
        # e.g. "Matthew 5:3: <content>"
        match = re.match(r'^.+? (\d+):(\d+): (.*)', line)
        if match:
            ch, vnum, content = match.group(1), match.group(2), match.group(3)
            if int(ch) != chapter:
                # diatheke may wrap to next chapter if we overshoot — stop
                if current_verse and current_lines:
                    text = strip_osis(' '.join(current_lines))
                    if text:
                        verses[current_verse] = text
                break
            # Save previous verse
            if current_verse and current_lines:
                text = strip_osis(' '.join(current_lines))
                if text:
                    verses[current_verse] = text
            current_verse = vnum
            current_lines = [content]
        else:
            if current_verse is not None:
                current_lines.append(line)

    # Save last verse
    if current_verse and current_lines:
        text = strip_osis(' '.join(current_lines))
        if text:
            verses[current_verse] = text

    return verses


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    total_verses = 0
    for book_name, abbrev, num_chapters in BOOK_MAP:
        book_dir = OUTPUT_DIR / book_name
        book_dir.mkdir(parents=True, exist_ok=True)
        print(f'\n{book_name} ({num_chapters} chapters)...')

        for chapter in range(1, num_chapters + 1):
            verses = extract_chapter(abbrev, book_name, chapter)
            chapter_data = {
                'book': book_name,
                'chapter': chapter,
                'verses': verses,
            }
            out_file = book_dir / f'{chapter}.json'
            with open(out_file, 'w', encoding='utf-8') as f:
                json.dump(chapter_data, f, indent=2, ensure_ascii=False)

            count = len(verses)
            total_verses += count
            print(f'  Chapter {chapter}: {count} verse entries', flush=True)

    print(f'\n✓ Done. Total verse entries written: {total_verses}')
    print(f'  Output: {OUTPUT_DIR.resolve()}')


if __name__ == '__main__':
    main()
