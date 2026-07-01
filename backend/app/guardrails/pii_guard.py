import re
from typing import Tuple

EMAIL_RE = re.compile(r'[\w\.-]+@[\w\.-]+\.\w+')
PHONE_RE = re.compile(r'(?:(?:\+?84|0)\d{9,10})')
ID_RE = re.compile(r'\b\d{9,12}\b')

def mask_pii(text: str) -> Tuple[str, bool]:
    if not text:
        return text, False

    original = text
    text = EMAIL_RE.sub("[EMAIL_MASKED]", text)
    text = PHONE_RE.sub("[PHONE_MASKED]", text)
    text = ID_RE.sub("[ID_MASKED]", text)

    return text, text != original