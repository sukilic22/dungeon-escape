"""An end-to-end test that plays through the whole game without a window."""

import pytest

from src.game import Game
from src.score_manager import ScoreManager
from src.settings import TOTAL_LEVELS


@pytest.fixture
def game(tmp_path):
    game = Game()
    game.score_manager = ScoreManager(tmp_path / "scores.json")
    yield game
    import pygame
    pygame.quit()


def solve_current_level(game):
    """Teleport the player: key tile -> tile under the door -> into the door."""
    level, player = game.level, game.player
    key = next(item for item in level.items if item.kind == "key")
    player.rect.center = key.rect.center
    player.x, player.y = player.rect.topleft
    game.state.update(0.01)
    assert player.has_key
    col, row = level.maze.door_tile
    player.set_tile_position(col, row + 1)
    game.state.update(0.01)                       # door opens
    assert not level.maze.door_locked
    player.set_tile_position(col, row)
    game.state.update(0.01)                       # walks through the door


def test_game_starts_in_menu(game):
    assert game.state is game.screens["menu"]


def test_play_button_starts_level_one(game):
    game.start_new_game()
    assert game.state is game.screens["gameplay"]
    assert game.level_number == 1
    assert game.player.health == game.settings.difficulty_config["health"]


def test_complete_all_three_levels_reaches_victory(game):
    game.start_new_game()
    for number in range(1, TOTAL_LEVELS):
        solve_current_level(game)
        assert game.state is game.screens["level_complete"]
        game.next_level()
        assert game.level_number == number + 1
        assert game.player.keys == 0                # key is used up per level
    solve_current_level(game)
    assert game.state is game.screens["victory"]
    assert game.player.score > 0


def test_losing_all_health_shows_game_over(game):
    game.start_new_game()
    game.player.health = 1
    game.player.invincible_timer = 0
    spike = game.level.traps[0]
    game.player.rect.center = spike.rect.center
    game.state.update(0.01)
    assert game.state is game.screens["game_over"]


def test_result_is_saved_to_json(game):
    game.start_new_game()
    game.player.score = 420
    game.save_result("Tester")
    assert game.score_manager.scores[-1]["name"] == "Tester"
    assert game.score_manager.scores[-1]["score"] == 420


def test_pause_and_resume_keep_the_game(game):
    game.start_new_game()
    game.player.score = 77
    game.change_state("pause")
    game.change_state("gameplay")
    assert game.player.score == 77


def test_difficulty_changes_hearts(game):
    game.settings.difficulty = "Hard"
    game.start_new_game()
    assert game.player.max_health == 2
    game.settings.difficulty = "Easy"
    game.start_new_game()
    assert game.player.max_health == 4
