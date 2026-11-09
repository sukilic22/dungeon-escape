"""Opens the real game window for 2 seconds and closes it again (smoke test)."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pygame  # noqa: E402

from src.game import Game  # noqa: E402

game = Game()
pygame.time.set_timer(pygame.QUIT, 2000)
game.run()
print("The game window opened and closed normally.")
