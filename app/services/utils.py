import re

YEAR_RE = re.compile(r"(19|20)\d{2}")

def extract_year(text: str) -> str:
    m = YEAR_RE.search(text or "")
    return m.group(0) if m else ""

CLEAN_RE = re.compile(r"[\.\_\-\[\]\(\)\{\}\|]+")
NON_ALNUM_RE = re.compile(r"[^0-9a-zA-Z\s]")

def normalize_text(s: str) -> str:
    s = s or ""
    s = CLEAN_RE.sub(" ", s)
    s = NON_ALNUM_RE.sub(" ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s
