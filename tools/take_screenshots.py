"""Saves a picture of every screen to docs/screenshots (no window needed).

    python tools/take_screenshots.py

Handy for the project report. It uses a temporary scores file, so your real
data/scores.json is not touched.
"""

import os
import sys
import tempfile
from pathlib import Path

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"
os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import pygame  # noqa: E402

from src.game import Game  # noqa: E402
from src.score_manager import ScoreManager  # noqa: E402

OUT = ROOT / "docs" / "screenshots"


def snap(game, name, frames=3):
    for _ in range(frames):
        game.state.update(0.016)
        game.state.draw(game.window)
    pygame.image.save(game.window, str(OUT / (name + ".png")))
    print("saved", name)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    game = Game()
    game.settings.filepath = Path(tempfile.mkdtemp()) / "settings.json"
    game.score_manager = ScoreManager(Path(tempfile.mkdtemp()) / "scores.json")
    for name, score, level in [("Anna", 1240, 3), ("Mehmet", 980, 3), ("Lea", 640, 2),
                               ("Sam", 410, 2), ("Zoe", 150, 1)]:
        game.score_manager.add_score(name, score, level)

    snap(game, "01_main_menu")

    game.start_new_game()
    game.screens["gameplay"].banner_timer = 0
    game.player.score = 120
    game.player.health = 2
    snap(game, "02_level1")
    game.load_level(2)
    game.screens["gameplay"].banner_timer = 0
    snap(game, "03_level2")
    game.load_level(3)
    game.screens["gameplay"].banner_timer = 0
    snap(game, "04_level3")

    game.change_state("pause")
    snap(game, "05_pause")
    game.change_state("settings")
    snap(game, "06_settings")
    game.change_state("high_scores")
    snap(game, "07_high_scores")

    game.player.score = 350
    game.level_number = 2
    game.change_state("game_over")
    snap(game, "08_game_over")
    game.last_bonus = (200, 75, 90)
    game.change_state("level_complete")
    snap(game, "09_level_complete")
    game.change_state("victory")
    snap(game, "10_victory")

    game.change_state("admin_login")
    game.screens["admin_login"].password_input.text = "secret"
    snap(game, "11_admin_login")
    game.change_state("admin_panel")
    snap(game, "12_admin_panel")
    game.screens["admin_panel"].confirming = True
    snap(game, "13_admin_confirm")
    pygame.quit()


if __name__ == "__main__":
    main()
