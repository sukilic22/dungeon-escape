"""Tests for Player: movement, collision, health, score and keys."""

import pygame

from src.maze import Maze
from src.player import Player
from src.settings import TILE_SIZE

ROOM = [
    "#######",
    "#.....#",
    "#.....#",
    "#.....#",
    "#######",
]


class FakeKeys(dict):
    """Pretends to be pygame.key.get_pressed()."""

    def __getitem__(self, key):
        return self.get(key, False)


def test_player_starts_in_tile_center():
    player = Player(2, 1)
    assert player.rect.center == (2 * TILE_SIZE + TILE_SIZE // 2, 1 * TILE_SIZE + TILE_SIZE // 2)


def test_move_right_changes_position():
    maze = Maze(ROOM)
    player = Player(1, 1)
    start_x = player.rect.x
    player.move(1, 0, 0.1, maze)
    assert player.rect.x > start_x
    assert player.facing == "right"


def test_player_cannot_walk_through_wall():
    maze = Maze(ROOM)
    player = Player(1, 1)
    for _ in range(100):                   # walk left for a long time
        player.move(-1, 0, 0.05, maze)
    assert player.rect.left >= TILE_SIZE   # stopped at the wall tile


def test_player_cannot_leave_room_vertically():
    maze = Maze(ROOM)
    player = Player(1, 1)
    for _ in range(100):
        player.move(0, 1, 0.05, maze)
    assert player.rect.bottom <= 4 * TILE_SIZE


def test_diagonal_movement_is_not_faster():
    maze = Maze(ROOM)
    straight, diagonal = Player(1, 1), Player(1, 1)
    straight.move(1, 0, 0.1, maze)
    diagonal.move(1, 1, 0.1, maze)
    moved_straight = straight.x - 1 * TILE_SIZE
    moved_diagonal = ((diagonal.x - 1 * TILE_SIZE) ** 2 + (diagonal.y - 1 * TILE_SIZE) ** 2) ** 0.5
    assert moved_diagonal < moved_straight * 1.5 + 1


def test_direction_from_keys():
    assert Player.direction_from_keys(FakeKeys({pygame.K_d: True})) == (1, 0)
    assert Player.direction_from_keys(FakeKeys({pygame.K_LEFT: True})) == (-1, 0)
    assert Player.direction_from_keys(FakeKeys({pygame.K_w: True, pygame.K_a: True})) == (-1, -1)
    assert Player.direction_from_keys(FakeKeys()) == (0, 0)


def test_take_damage_reduces_health():
    player = Player(max_health=3)
    assert player.take_damage() is True
    assert player.health == 2


def test_invincibility_prevents_double_damage():
    player = Player(max_health=3)
    player.take_damage()
    assert player.take_damage() is False
    assert player.health == 2
    player.update(Player.INVINCIBLE_TIME + 0.1)     # protection runs out
    assert player.take_damage() is True
    assert player.health == 1


def test_health_never_below_zero():
    player = Player(max_health=1)
    player.take_damage(5)
    assert player.health == 0
    assert not player.is_alive


def test_heal_is_capped_at_max_health():
    player = Player(max_health=3)
    player.take_damage()
    player.heal(5)
    assert player.health == 3


def test_add_score():
    player = Player()
    player.add_score(10)
    player.add_score(25)
    assert player.score == 35


def test_has_key():
    player = Player()
    assert not player.has_key
    player.keys = 1
    assert player.has_key
