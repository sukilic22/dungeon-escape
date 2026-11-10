import json
import os
from datetime import datetime
from pathlib import Path

from src.settings import *


class ScoreManager:

    def __init__(self, filepath=SCORES_FILE):
        self.filepath = Path(filepath)
        self.scores = []
        self.last_error = ""        
        self.load_scores()

    #score calculation
    @staticmethod
    def level_bonus_parts(level_number, health, seconds):
        """The three parts of the bonus for finishing a level.
        level bonus : 100 x level number
        health bonus: 25 per remaining heart
        time bonus  : 2 per second that was left of a 60 second time limit
        """
        base = LEVEL_BASE_BONUS * level_number
        health_part = HEALTH_BONUS * max(0, health)
        time_part = max(0, int(TIME_BONUS_LIMIT - seconds)) * TIME_BONUS_PER_SECOND
        return base, health_part, time_part

    @staticmethod
    def calculate_level_bonus(level_number, health, seconds):
        return sum(ScoreManager.level_bonus_parts(level_number, health, seconds))

    #file I/O
    def load_scores(self):
        self.last_error = ""
        self.scores = []
        if not self.filepath.exists():
            self.save_scores()      
            return self.scores
        try:
            with open(self.filepath, "r", encoding="utf-8") as file:
                text = file.read()
            if not text.strip():
                return self.scores  # empty file
            data = json.loads(text)
        except (OSError, ValueError) as error:
            self.last_error = "Could not read scores file: %s" % error
            return self.scores
        if not isinstance(data, list):
            self.last_error = "Scores file has an unexpected format."
            return self.scores
        for entry in data:
            clean = self._clean_entry(entry)
            if clean is not None:
                self.scores.append(clean)
        return self.scores

    def save_scores(self):
        try:
            self.filepath.parent.mkdir(parents=True, exist_ok=True)
            temp_path = self.filepath.with_suffix(".tmp")
            with open(temp_path, "w", encoding="utf-8") as file:
                json.dump(self.scores, file, indent=2)
            os.replace(temp_path, self.filepath)
            return True
        except OSError as error:
            self.last_error = "Could not save scores: %s" % error
            return False

    @staticmethod
    def _clean_entry(entry):
        if not isinstance(entry, dict):
            return None
        try:
            return {
                "name": str(entry["name"])[:MAX_NAME_LENGTH] or "Player",
                "score": int(entry["score"]),
                "level": int(entry["level"]),
                "date": str(entry.get("date", "")),
            }
        except (KeyError, TypeError, ValueError):
            return None

    #changing data
    def add_score(self, name, score, level):
        name = name.strip()[:MAX_NAME_LENGTH] or "Player"
        entry = {
            "name": name,
            "score": int(score),
            "level": int(level),
            "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
        }
        self.scores.append(entry)
        self.save_scores()
        return entry

    def clear_scores(self):
        self.scores = []
        return self.save_scores()

    #queries
    def get_sorted_scores(self, limit=None):
        ordered = sorted(self.scores, key=lambda s: (s["score"], s["level"]), reverse=True)
        return ordered if limit is None else ordered[:limit]

    def get_statistics(self):
        if not self.scores:
            return {"games": 0, "highest": 0, "average": 0, "best_player": "-"}
        best = self.get_sorted_scores(1)[0]
        total = sum(s["score"] for s in self.scores)
        return {
            "games": len(self.scores),
            "highest": best["score"],
            "average": round(total / len(self.scores)),
            "best_player": best["name"],
        }
