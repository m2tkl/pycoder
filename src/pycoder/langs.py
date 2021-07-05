from typing import List

lang_ids = {
    'python': 4006,
    'pypy': 4047,
}


def get_lang_ids(lang_type: str) -> List[int]:
    if lang_type == 'p':
        return lang_ids['python']
    elif lang_type == 'pp':
        return lang_ids['pypy']
    else:
        return None
