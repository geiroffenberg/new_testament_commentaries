#!/usr/bin/env python3
"""
Generate sample commentary JSON files for testing.
This creates realistic sample data that matches the final structure.
Later, you can replace these with real downloaded data.
"""

import json
from pathlib import Path

SAMPLE_DATA = {
    'clarke': {
        'Matthew': {
            5: {
                1: 'Blessed are the poor in spirit - Adam Clarke explains: This phrase points to those who recognize their spiritual poverty and complete dependence on God\'s grace. The "kingdom of heaven" belongs to those who have abandoned all trust in their own righteousness.',
                2: 'Blessed are those who mourn - Clarke comments: True mourning in a spiritual sense is sorrow for sin, both personal and universal. Those who grieve over the state of the world and their own failings shall receive divine comfort.',
                3: 'Blessed are the meek - Clarke defines meekness as humility combined with strength, not weakness. The meek inherit the earth because they submit to God\'s will and live at peace with others.',
            },
            6: {
                1: 'Beware of practicing your righteousness before others - Clarke warns against hypocrisy in religious observance. True righteousness must flow from a sincere heart, not from desire for human approval.',
            }
        },
        'John': {
            1: {
                1: 'In the beginning was the Word - Clarke explains the pre-existence of Christ. "The Word" (Logos) denotes Christ\'s eternal nature as God\'s spoken revelation and divine reason.',
                2: 'This one was in the beginning with God - Clarke emphasizes the intimate relationship between the Word and God the Father from eternity past.',
            }
        }
    },
    'jfb': {
        'Matthew': {
            5: {
                1: 'Blessed are the poor in spirit - Jamieson-Fausset-Brown note: The first beatitude establishes the foundation of all true religion: awareness of spiritual need and humble dependence on God.',
                2: 'Blessed are those who mourn - JFB: Genuine spiritual sorrow produces comfort. Those who deeply feel their inadequacy in light of God\'s holiness will find peace in Christ.',
                3: 'Blessed are the meek - JFB: True meekness is not passivity but controlled strength submitted to God. The meek shall inherit the earth because they trust God\'s purposes.',
            },
            6: {
                1: 'Beware of practicing your righteousness before men - JFB warns: Religious works performed for human approval have no eternal value. Only deeds done for God\'s glory receive His reward.',
            }
        },
        'Romans': {
            8: {
                1: 'There is therefore now no condemnation for those who are in Christ Jesus - JFB: This is the triumphant conclusion of chapters 6-7. Believers are delivered from guilt and judgment through their union with Christ.',
            }
        }
    },
    'rwp': {
        'John': {
            1: {
                1: 'In the beginning was the Word - A.T. Robertson notes: The imperfect "was" (ēn) indicates continuous existence. The Word already existed when the beginning came to be.',
                2: 'The same was in the beginning with God - Robertson: The Word\'s intimate association with God is emphasized. Their relationship is both personal and eternal.',
            }
        },
        'Romans': {
            8: {
                1: 'No condemnation now in Christ Jesus - Robertson explains: Christ\'s work on the cross permanently removed the sentence of judgment for those united with Him by faith.',
            }
        }
    },
    'mhcc': {
        'Matthew': {
            5: {
                1: 'Blessed are the poor in spirit - Matthew Henry Concise: Those lowly in their own eyes are blessed. Genuine humility before God opens the door to His kingdom.',
                2: 'Blessed are those who mourn - MHCC: Godly sorrow over sin leads to comfort and restoration. Mourning in this sense brings spiritual healing.',
                3: 'Blessed are the meek - MHCC: Gentleness and meekness are not weakness but strength under control. God rewards those who submit peacefully to His will.',
            },
            6: {
                1: 'Avoid ostentation in almsgiving - MHCC: Religious deeds done to be seen by others have already received their reward: human praise. God sees and rewards only what is done in secret.',
            }
        },
        'Romans': {
            8: {
                1: 'No condemnation for believers - MHCC: Those in Christ are freed from guilt and judgment. Their standing is secure because of Christ\'s finished work.',
            }
        }
    }
}

def generate_sample_commentaries():
    """Generate sample JSON files for all 4 commentaries."""
    assets_dir = Path(__file__).parent / 'assets' / 'commentaries_json'
    assets_dir.mkdir(parents=True, exist_ok=True)
    
    for commentary_id, books in SAMPLE_DATA.items():
        commentary_dir = assets_dir / commentary_id
        commentary_dir.mkdir(parents=True, exist_ok=True)
        
        for book, chapters in books.items():
            book_dir = commentary_dir / book
            book_dir.mkdir(parents=True, exist_ok=True)
            
            for chapter_num, verses in chapters.items():
                chapter_file = book_dir / f'{chapter_num}.json'
                
                chapter_data = {
                    'book': book,
                    'chapter': chapter_num,
                    'verses': {str(k): v for k, v in verses.items()}
                }
                
                with open(chapter_file, 'w', encoding='utf-8') as f:
                    json.dump(chapter_data, f, indent=2, ensure_ascii=False)
                
                print(f'Created {commentary_id}/{book}/{chapter_num}.json')
    
    print(f'\n✓ Sample commentary data created in {assets_dir}')

if __name__ == '__main__':
    generate_sample_commentaries()
