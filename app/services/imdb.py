# TMDB integration (kept as imdb.py to match your created file)
import requests
from app.config import TMDB_API_KEY
from app.services.search import best_fuzzy_score

def tmdb_search(query: str, year: str = "") -> list[dict]:
    if not TMDB_API_KEY or not query:
        return []
    params = {"api_key": TMDB_API_KEY, "query": query}
    if year and year.isdigit():
        params["primary_release_year"] = year
    r = requests.get("https://api.themoviedb.org/3/search/movie", params=params, timeout=15)
    data = r.json()
    results = []
    for m in data.get("results", []):
        results.append({
            "id": m.get("id"),
            "title": m.get("title") or m.get("name") or "",
            "year": (m.get("release_date") or "")[:4],
            "poster": f"https://image.tmdb.org/t/p/w500{m['poster_path']}" if m.get("poster_path") else None
        })
    return results

def tmdb_search_best(query: str, year: str = "") -> dict | None:
    candidates = tmdb_search(query, year)
    if not candidates:
        # try again without year
        candidates = tmdb_search(query, "")
        if not candidates:
            return None
    # Score each by fuzzy match
    best = None
    best_score = -1
    for c in candidates[:8]:
        score = best_fuzzy_score(query, c["title"])
        if score > best_score:
            best_score = score
            best = c
    if best is None:
        return None
    best["score"] = best_score
    return best
