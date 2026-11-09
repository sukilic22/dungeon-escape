"""Global constants and the persistent player settings.

Everything that is a "magic number" in the game lives here, so it is easy to
find and change when you want to tweak the game.
"""

import hashlib
import json
from pathlib import Path

# ---------------------------------------------------------------- paths
BASE_DIR = Path(__file__).resolve().parent.parent
ASSETS_DIR = BASE_DIR / "assets"
IMAGES_DIR = ASSETS_DIR / "images"
SOUNDS_DIR = ASSETS_DIR / "sounds"
DATA_DIR = BASE_DIR / "data"
SCORES_FILE = DATA_DIR / "scores.json"
SETTINGS_FILE = DATA_DIR / "settings.json"

# -------------------------------------------------------------- display
TILE_SIZE = 48            # one map tile is 48 x 48 pixels on screen
SPRITE_PIXELS = 16        # the pixel-art sprites are drawn at 16 x 16
SPRITE_SCALE = TILE_SIZE // SPRITE_PIXELS
GRID_COLS = 20
GRID_ROWS = 14
SCREEN_WIDTH = GRID_COLS * TILE_SIZE   # 960
SCREEN_HEIGHT = GRID_ROWS * TILE_SIZE  # 672
FPS = 60
TITLE = "Dungeon Escape: The Lost Key"

# --------------------------------------------------------------- colours
COLOR_TEXT = (232, 226, 210)
COLOR_GOLD = (244, 200, 70)
COLOR_RED = (222, 58, 58)
COLOR_GREEN = (110, 200, 90)
COLOR_OUTLINE = (16, 12, 24)
COLOR_PANEL = (52, 50, 68)
COLOR_PANEL_DARK = (30, 28, 42)
COLOR_PANEL_LIGHT = (104, 100, 128)

# ---------------------------------------------------------------- scoring
COIN_POINTS = 10
KEY_POINTS = 25
CHEST_POINTS = 50
LEVEL_BASE_BONUS = 100     # bonus per level number (level 2 -> 200)
HEALTH_BONUS = 25          # bonus per remaining heart
TIME_BONUS_LIMIT = 60      # seconds in which a time bonus can still be earned
TIME_BONUS_PER_SECOND = 2

# ------------------------------------------------------------- gameplay
TOTAL_LEVELS = 3
KEYS_REQUIRED = 1
MAX_NAME_LENGTH = 12

# Each difficulty changes how many hearts you start with and enemy speed.
DIFFICULTIES = {
    "Easy": {"health": 4, "enemy_speed": 0.75},
    "Normal": {"health": 3, "enemy_speed": 1.0},
    "Hard": {"health": 2, "enemy_speed": 1.3},
}
DIFFICULTY_ORDER = ["Easy", "Normal", "Hard"]

# ------------------------------------------------------------ admin panel
# We never store the password itself, only its SHA-256 hash.
# The default password is:  admin123
ADMIN_PASSWORD_HASH = "240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9"


def check_admin_password(password):
    """Return True if `password` matches the stored admin password hash."""
    entered_hash = hashlib.sha256(password.encode("utf-8")).hexdigest()
    return entered_hash == ADMIN_PASSWORD_HASH


class GameSettings:
    """Music volume, sound-effect volume and difficulty (saved to JSON)."""

    def __init__(self, filepath=SETTINGS_FILE):
        self.filepath = Path(filepath)
        self.music_volume = 0.5
        self.sfx_volume = 0.7
        self.difficulty = "Normal"

    @property
    def difficulty_config(self):
        return DIFFICULTIES[self.difficulty]

    def change_difficulty(self, step):
        """Move the difficulty up (+1) or down (-1) in the list."""
        index = DIFFICULTY_ORDER.index(self.difficulty)
        index = max(0, min(len(DIFFICULTY_ORDER) - 1, index + step))
        self.difficulty = DIFFICULTY_ORDER[index]

    def load(self):
        """Read the settings file. Falls back to defaults if it is bad."""
        try:
            with open(self.filepath, "r", encoding="utf-8") as file:
                data = json.load(file)
            self.music_volume = self._clamp(data.get("music_volume", 0.5))
            self.sfx_volume = self._clamp(data.get("sfx_volume", 0.7))
            if data.get("difficulty") in DIFFICULTIES:
                self.difficulty = data["difficulty"]
        except (OSError, ValueError, AttributeError, TypeError):
            pass  # missing or broken file -> keep the defaults

    def save(self):
        """Write the settings file. Returns True when it worked."""
        data = {
            "music_volume": round(self.music_volume, 2),
            "sfx_volume": round(self.sfx_volume, 2),
            "difficulty": self.difficulty,
        }
        try:
            self.filepath.parent.mkdir(parents=True, exist_ok=True)
            with open(self.filepath, "w", encoding="utf-8") as file:
                json.dump(data, file, indent=2)
            return True
        except OSError:
            return False

    @staticmethod
    def _clamp(value):
        return max(0.0, min(1.0, float(value)))
