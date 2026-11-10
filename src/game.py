import pygame

from src.asset_manager import AssetManager
from src.level import Level
from src.player import Player
from src.score_manager import ScoreManager
from src.screens import (AdminLoginScreen, AdminPanelScreen, GameOverScreen, GameplayScreen, HighScoresScreen, LevelCompleteScreen, MenuScreen, PauseScreen, SettingsScreen, VictoryScreen)
from src.settings import *


class Game:
    def __init__(self):
        pygame.mixer.pre_init(22050, -16, 1, 512)
        pygame.init()
        pygame.display.set_caption(TITLE)
        self.window = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()
        self.running = True

        # shared helpers
        self.settings = GameSettings()
        self.settings.load()
        self.assets = AssetManager()
        self.assets.set_sfx_volume(self.settings.sfx_volume)
        self.assets.start_music(self.settings.music_volume)
        self.score_manager = ScoreManager()
        pygame.display.set_icon(self.assets.image("player_down", 2))

        self.player = None
        self.level = None
        self.level_number = 1
        self.player_name = "Player"
        self.last_bonus = (0, 0, 0)

        #one object per screen
        self.screens = {
            "menu": MenuScreen(self),
            "gameplay": GameplayScreen(self),
            "pause": PauseScreen(self),
            "settings": SettingsScreen(self),
            "high_scores": HighScoresScreen(self),
            "game_over": GameOverScreen(self),
            "victory": VictoryScreen(self),
            "level_complete": LevelCompleteScreen(self),
            "admin_login": AdminLoginScreen(self),
            "admin_panel": AdminPanelScreen(self),
        }
        self.state = None
        self.change_state("menu")

    def change_state(self, name):
        self.state = self.screens[name]
        self.state.on_enter()

    def start_new_game(self):
        config = self.settings.difficulty_config
        self.player = Player(max_health=config["health"])
        self.load_level(1)
        self.change_state("gameplay")

    def load_level(self, number):
        self.level_number = number
        self.level = Level(number, self.settings.difficulty_config["enemy_speed"])
        col, row = self.level.player_start
        self.player.set_tile_position(col, row)
        self.player.keys = 0
        self.player.invincible_timer = 0.0
        self.screens["gameplay"].reset_effects()

    def level_finished(self):
        self.last_bonus = ScoreManager.level_bonus_parts(self.level_number, self.player.health, self.level.elapsed)
        self.player.add_score(sum(self.last_bonus))
        self.assets.play("win")
        if self.level_number >= TOTAL_LEVELS:
            self.change_state("victory")
        else:
            self.change_state("level_complete")

    def next_level(self):
        self.player.heal(1)
        self.load_level(self.level_number + 1)
        self.change_state("gameplay")

    def game_over(self):
        self.assets.play("gameover")
        self.change_state("game_over")

    def save_result(self, name):
        self.player_name = name.strip() or "Player"
        self.score_manager.add_score(self.player_name, self.player.score, self.level_number)

    def quit(self):
        self.running = False

    #main loop
    def run(self):
        while self.running:
            # dt = seconds since last frame (limited, so a lag cannot make the player jump through a wall)
            dt = min(self.clock.tick(FPS) / 1000.0, 0.05)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.quit()
                else:
                    self.state.handle_event(event)
            self.state.update(dt)
            self.state.draw(self.window)
            pygame.display.flip()
        pygame.quit()
