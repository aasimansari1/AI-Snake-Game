"""
leaderboard.py
--------------
Persistent local leaderboard backed by a small JSON file.
Stores the top N scores along with the mode (Manual / AI) and a timestamp.
"""

import json
import os
from datetime import datetime
from settings import LEADERBOARD_FILE, MAX_LEADERBOARD_ENTRIES


def _load():
    if not os.path.exists(LEADERBOARD_FILE):
        return []
    try:
        with open(LEADERBOARD_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, list):
                return data
    except (json.JSONDecodeError, OSError):
        pass
    return []


def _save(entries):
    try:
        with open(LEADERBOARD_FILE, "w", encoding="utf-8") as f:
            json.dump(entries, f, indent=2)
    except OSError:
        # Persistence is best-effort; never crash the game over disk issues.
        pass


def get_top_scores():
    entries = _load()
    entries.sort(key=lambda e: e.get("score", 0), reverse=True)
    return entries[:MAX_LEADERBOARD_ENTRIES]


def add_score(score, mode):
    entries = _load()
    entries.append({
        "score": int(score),
        "mode": mode,
        "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
    })
    entries.sort(key=lambda e: e.get("score", 0), reverse=True)
    entries = entries[:MAX_LEADERBOARD_ENTRIES]
    _save(entries)
    return entries
