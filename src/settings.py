import json
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
ASSETS_DIR = BASE_DIR / "assets"
IMAGES_DIR = ASSETS_DIR / "images"
SOUNDS_DIR = ASSETS_DIR / "sounds"
DATA_DIR = BASE_DIR / "data"
SCORES_FILE = DATA_DIR / "scores.json"
SETTINGS_FILE = DATA_DIR / "settings.json"

TILE_SIZE = 48
SPRITE_PIXELS = 16
SPRITE_SCALE = TILE_SIZE // SPRITE_PIXELS
GRID_COLS = 20
GRID_ROWS = 14
SCREEN_WIDTH = GRID_COLS * TILE_SIZE
SCREEN_HEIGHT = GRID_ROWS * TILE_SIZE
FPS = 60
TITLE = "Dungeon Escape: The Lost Key"

COLOR_TEXT = (232, 226, 210)
COLOR_GOLD = (244, 200, 70)
COLOR_RED = (222, 58, 58)
COLOR_GREEN = (110, 200, 90)
COLOR_OUTLINE = (16, 12, 24)
COLOR_PANEL = (52, 50, 68)
COLOR_PANEL_DARK = (30, 28, 42)

COIN_POINTS = 10
KEY_POINTS = 25
CHEST_POINTS = 50
LEVEL_BASE_BONUS = 100
HEALTH_BONUS = 25
TIME_BONUS_LIMIT = 60
TIME_BONUS_PER_SECOND = 2

TOTAL_LEVELS = 3
KEYS_REQUIRED = 1
MAX_NAME_LENGTH = 12

DIFFICULTIES = {
    "Easy": {"health": 4, "enemy_speed": 0.75},
    "Normal": {"health": 3, "enemy_speed": 1.0},
    "Hard": {"health": 2, "enemy_speed": 1.3},
}
DIFFICULTY_ORDER = ["Easy", "Normal", "Hard"]




class GameSettings:

    def __init__(self, filepath=SETTINGS_FILE):
        self.filepath = Path(filepath)
        self.music_volume = 0.5
        self.sfx_volume = 0.7
        self.difficulty = "Normal"

    @property
    def difficulty_config(self):
        return DIFFICULTIES[self.difficulty]

    def change_difficulty(self, step):
        new_index = DIFFICULTY_ORDER.index(self.difficulty) + step
        if 0 <= new_index < len(DIFFICULTY_ORDER):
            self.difficulty = DIFFICULTY_ORDER[new_index]

    def clamp(self, value):
        return max(0.0, min(1.0, float(value)))

    def load(self):
        try:
            with open(self.filepath, "r", encoding="utf-8") as file:
                data = json.load(file)
            self.music_volume = self.clamp(data.get("music_volume", 0.5))
            self.sfx_volume = self.clamp(data.get("sfx_volume", 0.7))
            if data.get("difficulty") in DIFFICULTIES:
                self.difficulty = data["difficulty"]
        except Exception:
            pass

    def save(self):
        data = {
            "music_volume": round(self.music_volume, 2),
            "sfx_volume": round(self.sfx_volume, 2),
            "difficulty": self.difficulty,
        }
        try:
            with open(self.filepath, "w", encoding="utf-8") as file:
                json.dump(data, file, indent=2)
            return True
        except Exception:
            return False