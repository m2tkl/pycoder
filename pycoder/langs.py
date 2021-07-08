from typing import List, Optional

lang_ids = {
    'python': 4006,
    'pypy': 4047,
}


def get_lang_id(lang_type: str) -> Optional[int]:
    if lang_type == 'p':
        return lang_ids['python']
    elif lang_type == 'pp':
        return lang_ids['pypy']
    return None
