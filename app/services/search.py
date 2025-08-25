from rapidfuzz import fuzz
from app.db.queries import list_junk
from app.services.utils import extract_year, normalize_text

def strip_junk(text: str) -> str:
    txt = normalize_text(text or "")
    junk = list_junk()
    if junk:
        # remove whole-word junk; simple approach
        words = txt.split()
        filt = [w for w in words if w.lower() not in {j.lower() for j in junk}]
        txt = " ".join(filt)
    return txt

def build_query(filename: str, caption: str) -> dict:
    # Prefer caption first, fallback to filename
    base = " ".join(filter(None, [caption, filename]))
    base = strip_junk(base)
    year = extract_year(base)
    return {"query": base.strip(), "year": year}

def analyze_media_message(filename: str, caption: str) -> dict:
    info = build_query(filename, caption)
    return info

def best_fuzzy_score(candidate: str, title: str) -> float:
    if not candidate or not title:
        return 0.0
    # token_sort_ratio handles swapped word orders better
    return float(fuzz.token_sort_ratio(candidate.lower(), title.lower()))
