#!/usr/bin/env python3
"""
Extract a SWORD commentary module (zCom/zCom4) to chapter JSON files for the app.

Example:
  python3 extract_sword_commentary.py \
    --zip assets/commentaries/JFB.zip \
    --module JFB \
    --source-id jfb
"""

import argparse
import json
import re
import shutil
import subprocess
from pathlib import Path

BOOK_MAP = [
    ('Matthew', 'Matt', 28),
    ('Mark', 'Mark', 16),
    ('Luke', 'Luke', 24),
    ('John', 'John', 21),
    ('Acts', 'Acts', 28),
    ('Romans', 'Rom', 16),
    ('1 Corinthians', '1Cor', 16),
    ('2 Corinthians', '2Cor', 13),
    ('Galatians', 'Gal', 6),
    ('Ephesians', 'Eph', 6),
    ('Philippians', 'Phil', 4),
    ('Colossians', 'Col', 4),
    ('1 Thessalonians', '1Thess', 5),
    ('2 Thessalonians', '2Thess', 3),
    ('1 Timothy', '1Tim', 6),
    ('2 Timothy', '2Tim', 4),
    ('Titus', 'Titus', 3),
    ('Philemon', 'Phlm', 1),
    ('Hebrews', 'Heb', 13),
    ('James', 'Jas', 5),
    ('1 Peter', '1Pet', 5),
    ('2 Peter', '2Pet', 3),
    ('1 John', '1John', 5),
    ('2 John', '2John', 1),
    ('3 John', '3John', 1),
    ('Jude', 'Jude', 1),
    ('Revelation', 'Rev', 22),
]


def strip_osis(text: str, module_name: str) -> str:
    text = re.sub(r'<reference[^>]*>([^<]*)</reference>', r'\1', text)
    text = re.sub(r'<[^>]+>', '', text)
    text = re.sub(rf'\({re.escape(module_name)}\)\s*$', '', text, flags=re.IGNORECASE)
    text = re.sub(r'[ \t]+', ' ', text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()


def extract_chapter(module_name: str, sword_path: str, abbrev: str, chapter: int) -> dict[str, str]:
    range_key = f'{abbrev} {chapter}:1-200'
    result = subprocess.run(
        ['diatheke', '-b', module_name, '-k', range_key],
        capture_output=True,
        text=True,
        env={'SWORD_PATH': sword_path, 'PATH': '/usr/bin:/bin'},
        check=False,
    )

    verses: dict[str, str] = {}
    current_verse: str | None = None
    current_lines: list[str] = []

    for line in result.stdout.splitlines():
        match = re.match(r'^.+? (\d+):(\d+): (.*)', line)
        if match:
            ch, vnum, content = int(match.group(1)), match.group(2), match.group(3)
            if ch != chapter:
                if current_verse and current_lines:
                    text = strip_osis(' '.join(current_lines), module_name)
                    if text:
                        verses[current_verse] = text
                break
            if current_verse and current_lines:
                text = strip_osis(' '.join(current_lines), module_name)
                if text:
                    verses[current_verse] = text
            current_verse = vnum
            current_lines = [content]
        elif current_verse is not None:
            current_lines.append(line)

    if current_verse and current_lines:
        text = strip_osis(' '.join(current_lines), module_name)
        if text:
            verses[current_verse] = text

    return verses


def main() -> None:
    parser = argparse.ArgumentParser(description='Extract a SWORD commentary module to JSON.')
    parser.add_argument('--zip', dest='zip_path', required=True, help='Path to module zip file')
    parser.add_argument('--module', dest='module_name', required=True, help='SWORD module key, e.g. JFB')
    parser.add_argument('--source-id', dest='source_id', required=True, help='Output source id folder, e.g. jfb')
    parser.add_argument('--tmp', dest='tmp_path', default='/tmp/sword_module_extract', help='Temporary extraction folder')
    args = parser.parse_args()

    zip_path = Path(args.zip_path)
    if not zip_path.exists():
        raise FileNotFoundError(f'Zip not found: {zip_path}')

    tmp_dir = Path(args.tmp_path)
    if tmp_dir.exists():
        shutil.rmtree(tmp_dir)
    tmp_dir.mkdir(parents=True, exist_ok=True)

    unzip_result = subprocess.run(
        ['unzip', '-q', str(zip_path), '-d', str(tmp_dir)],
        capture_output=True,
        text=True,
        check=False,
    )
    if unzip_result.returncode != 0:
        raise RuntimeError(f'Failed to unzip module: {unzip_result.stderr.strip()}')

    output_dir = Path('assets/commentaries_json') / args.source_id
    output_dir.mkdir(parents=True, exist_ok=True)

    total_entries = 0
    for book_name, abbrev, chapter_count in BOOK_MAP:
        book_dir = output_dir / book_name
        book_dir.mkdir(parents=True, exist_ok=True)
        print(f'\n{book_name} ({chapter_count} chapters)...')

        for chapter in range(1, chapter_count + 1):
            verses = extract_chapter(args.module_name, str(tmp_dir), abbrev, chapter)
            chapter_data = {
                'book': book_name,
                'chapter': chapter,
                'verses': verses,
            }
            out_file = book_dir / f'{chapter}.json'
            with out_file.open('w', encoding='utf-8') as f:
                json.dump(chapter_data, f, indent=2, ensure_ascii=False)

            count = len(verses)
            total_entries += count
            print(f'  Chapter {chapter}: {count} verse entries')

    print(f'\nDone. Total verse entries written: {total_entries}')
    print(f'Output: {output_dir.resolve()}')


if __name__ == '__main__':
    main()
