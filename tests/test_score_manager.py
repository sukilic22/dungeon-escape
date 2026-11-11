"""Tests for ScoreManager: JSON saving/loading, sorting, errors, statistics."""

import json

from src.score_manager import ScoreManager
from src.settings import GameSettings


def make_manager(tmp_path):
    return ScoreManager(tmp_path / "scores.json")


# ------------------------------------------------------- file handling
def test_missing_file_is_created_automatically(tmp_path):
    path = tmp_path / "data" / "scores.json"        # even the folder is missing
    manager = ScoreManager(path)
    assert path.exists()
    assert json.loads(path.read_text()) == []
    assert manager.scores == []


def test_empty_file_gives_empty_list(tmp_path):
    path = tmp_path / "scores.json"
    path.write_text("")
    assert ScoreManager(path).scores == []


def test_invalid_json_is_handled(tmp_path):
    path = tmp_path / "scores.json"
    path.write_text("{ this is not json")
    manager = ScoreManager(path)
    assert manager.scores == []
    assert manager.last_error != ""


def test_wrong_json_shape_is_handled(tmp_path):
    path = tmp_path / "scores.json"
    path.write_text(json.dumps({"hello": "world"}))
    manager = ScoreManager(path)
    assert manager.scores == []
    assert manager.last_error != ""


def test_broken_entries_are_skipped(tmp_path):
    path = tmp_path / "scores.json"
    good = {"name": "Ann", "score": 100, "level": 2, "date": "2025-01-01 10:00"}
    path.write_text(json.dumps([good, "junk", {"name": "NoScore"}, {"name": "X", "score": "abc", "level": 1}, 42]))
    manager = ScoreManager(path)
    assert len(manager.scores) == 1
    assert manager.scores[0]["name"] == "Ann"


def test_scores_survive_restart(tmp_path):
    first = make_manager(tmp_path)
    first.add_score("Ann", 300, 2)
    second = make_manager(tmp_path)               # "restart the game"
    assert len(second.scores) == 1
    assert second.scores[0]["name"] == "Ann"
    assert second.scores[0]["score"] == 300


def test_saved_entry_has_all_fields(tmp_path):
    manager = make_manager(tmp_path)
    manager.add_score("Ann", 300, 2)
    saved = json.loads((tmp_path / "scores.json").read_text())[0]
    assert set(saved) == {"name", "score", "level", "date"}
    assert saved["level"] == 2


def test_save_error_does_not_crash(tmp_path):
    # the "file" path is actually a folder -> writing is impossible
    folder = tmp_path / "scores.json"
    folder.mkdir()
    manager = ScoreManager(folder)
    assert manager.save_scores() is False
    assert manager.last_error != ""


# ------------------------------------------------------ adding / sorting
def test_name_is_cleaned_up(tmp_path):
    manager = make_manager(tmp_path)
    assert manager.add_score("   ", 1, 1)["name"] == "Player"
    assert len(manager.add_score("A" * 50, 1, 1)["name"]) <= 12


def test_scores_sorted_highest_first(tmp_path):
    manager = make_manager(tmp_path)
    for name, score in [("a", 50), ("b", 300), ("c", 120)]:
        manager.add_score(name, score, 1)
    assert [s["score"] for s in manager.get_sorted_scores()] == [300, 120, 50]


def test_sorted_scores_limit(tmp_path):
    manager = make_manager(tmp_path)
    for i in range(15):
        manager.add_score("p", i, 1)
    assert len(manager.get_sorted_scores(10)) == 10
    assert manager.get_sorted_scores(10)[0]["score"] == 14


def test_clear_scores(tmp_path):
    manager = make_manager(tmp_path)
    manager.add_score("Ann", 10, 1)
    assert manager.clear_scores() is True
    assert manager.scores == []
    assert json.loads((tmp_path / "scores.json").read_text()) == []


def test_statistics(tmp_path):
    manager = make_manager(tmp_path)
    assert manager.get_statistics()["games"] == 0
    manager.add_score("Ann", 100, 1)
    manager.add_score("Ben", 300, 3)
    stats = manager.get_statistics()
    assert stats["games"] == 2
    assert stats["highest"] == 300
    assert stats["average"] == 200
    assert stats["best_player"] == "Ben"


# ------------------------------------------------------ score calculation
def test_level_bonus_formula():
    # level 2: 200 + 3 hearts * 25 + (60 - 20) s * 2
    assert ScoreManager.calculate_level_bonus(2, 3, 20) == 200 + 75 + 80


def test_no_time_bonus_when_too_slow():
    assert ScoreManager.calculate_level_bonus(1, 0, 500) == 100


def test_bonus_parts_add_up():
    parts = ScoreManager.level_bonus_parts(3, 2, 30)
    assert parts == (300, 50, 60)
    assert sum(parts) == ScoreManager.calculate_level_bonus(3, 2, 30)


#settings / admin



def test_settings_roundtrip(tmp_path):
    path = tmp_path / "settings.json"
    settings = GameSettings(path)
    settings.music_volume = 0.2
    settings.difficulty = "Hard"
    assert settings.save()
    loaded = GameSettings(path)
    loaded.load()
    assert loaded.music_volume == 0.2
    assert loaded.difficulty == "Hard"


def test_settings_bad_file_uses_defaults(tmp_path):
    path = tmp_path / "settings.json"
    path.write_text("not json")
    settings = GameSettings(path)
    settings.load()
    assert settings.difficulty == "Normal"


def test_difficulty_change_stays_in_range():
    settings = GameSettings()
    for _ in range(5):
        settings.change_difficulty(1)
    assert settings.difficulty == "Hard"
    for _ in range(5):
        settings.change_difficulty(-1)
    assert settings.difficulty == "Easy"
