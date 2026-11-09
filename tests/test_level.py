"""Tests for Item collection and the Level rules (key, locked door, hazards)."""

import pytest

from src.item import Item
from src.level import Level
from src.levels_data import LEVELS
from src.maze import Maze
from src.player import Player
from src.settings import COIN_POINTS, KEY_POINTS, CHEST_POINTS, TILE_SIZE, TOTAL_LEVELS


def put_player_on_tile(player, tile):
    player.set_tile_position(*tile)


def find_tile(level_number, char):
    for row, line in enumerate(LEVELS[level_number - 1]["layout"]):
        if char in line:
            return line.index(char), row
    raise AssertionError(char + " not found")


# ------------------------------------------------------------------ items
def test_coin_adds_score():
    player, coin = Player(), Item("coin", 1, 1)
    assert coin.collect(player)
    assert player.score == COIN_POINTS


def test_item_can_only_be_collected_once():
    player, coin = Player(), Item("coin", 1, 1)
    coin.collect(player)
    assert coin.collect(player) is False
    assert player.score == COIN_POINTS


def test_key_is_collected():
    player, key = Player(), Item("key", 1, 1)
    key.collect(player)
    assert player.keys == 1
    assert player.has_key
    assert player.score == KEY_POINTS


def test_chest_gives_bonus_points():
    player = Player()
    Item("chest", 1, 1).collect(player)
    assert player.score == CHEST_POINTS


def test_heart_restores_health_only_up_to_max():
    player = Player(max_health=3)
    player.take_damage()
    Item("heart", 1, 1).collect(player)
    assert player.health == 3
    Item("heart", 2, 1).collect(player)
    assert player.health == 3


def test_unknown_item_is_rejected():
    with pytest.raises(ValueError):
        Item("sword", 1, 1)


# -------------------------------------------------------- key & locked door
def test_level_collects_key_on_touch():
    level, player = Level(1), Player()
    put_player_on_tile(player, find_tile(1, "K"))
    events = level.update(0.01, player)
    assert "key" in events
    assert player.keys == 1


def test_door_stays_locked_without_key():
    level, player = Level(1), Player()
    door_col, door_row = level.maze.door_tile
    put_player_on_tile(player, (door_col, door_row + 1))     # right below the door
    events = level.update(0.01, player)
    assert level.maze.door_locked
    assert "door_locked" in events
    assert not level.completed


def test_door_opens_with_key():
    level, player = Level(1), Player()
    player.keys = 1
    door_col, door_row = level.maze.door_tile
    put_player_on_tile(player, (door_col, door_row + 1))
    events = level.update(0.01, player)
    assert "door_open" in events
    assert not level.maze.door_locked


def test_level_completes_when_player_enters_open_door():
    level, player = Level(1), Player()
    level.maze.unlock_door()
    put_player_on_tile(player, level.maze.door_tile)
    events = level.update(0.01, player)
    assert "level_complete" in events
    assert level.completed


def test_locked_door_blocks_the_player():
    level, player = Level(1), Player()
    door_col, door_row = level.maze.door_tile
    put_player_on_tile(player, (door_col, door_row + 1))
    for _ in range(60):
        player.move(0, -1, 0.02, level.maze)
    assert player.rect.top >= (door_row + 1) * TILE_SIZE


# ------------------------------------------------------------- hazards
def test_spikes_hurt_the_player():
    level, player = Level(1), Player(max_health=3)
    put_player_on_tile(player, find_tile(1, "^"))
    events = level.update(0.01, player)
    assert "hurt" in events
    assert player.health == 2


def test_enemy_touch_hurts_the_player():
    level, player = Level(2), Player(max_health=3)
    goblin = level.enemies[0]
    player.rect.center = goblin.rect.center
    events = level.update(0.001, player)
    assert "hurt" in events
    assert player.health == 2


def test_death_event_when_health_reaches_zero():
    level, player = Level(1), Player(max_health=1)
    put_player_on_tile(player, find_tile(1, "^"))
    events = level.update(0.01, player)
    assert "dead" in events
    assert not player.is_alive


# ----------------------------------------------------- the three levels
def test_level_difficulty_increases():
    enemies = [len(Level(n).enemies) for n in range(1, TOTAL_LEVELS + 1)]
    traps = [len(Level(n).traps) for n in range(1, TOTAL_LEVELS + 1)]
    assert enemies[0] == 0
    assert enemies[1] == 1
    assert enemies[2] > enemies[1]
    assert traps[0] < traps[1] <= traps[2] or traps[2] >= traps[0]


@pytest.mark.parametrize("number", range(1, TOTAL_LEVELS + 1))
def test_every_level_can_be_solved(number):
    """BFS proves there is a route start -> key -> door that avoids fixed spikes."""
    level = Level(number)
    maze: Maze = level.maze
    start = level.player_start
    key = find_tile(number, "K")
    door = maze.door_tile
    static_spikes = {(c, r) for r, line in enumerate(LEVELS[number - 1]["layout"])
                     for c, ch in enumerate(line) if ch == "^"}
    to_key = maze.find_path(start, key, avoid=static_spikes)
    to_door = maze.find_path(key, door, avoid=static_spikes)
    assert to_key is not None, "key cannot be reached"
    assert to_door is not None, "door cannot be reached from the key"


@pytest.mark.parametrize("number", range(1, TOTAL_LEVELS + 1))
def test_all_items_are_reachable(number):
    level = Level(number)
    for row, line in enumerate(LEVELS[number - 1]["layout"]):
        for col, ch in enumerate(line):
            if ch in "CH+K":
                assert level.maze.find_path(level.player_start, (col, row)) is not None


@pytest.mark.parametrize("number", range(1, TOTAL_LEVELS + 1))
def test_player_start_is_not_on_a_hazard(number):
    level = Level(number)
    player = Player()
    put_player_on_tile(player, level.player_start)
    assert not level.maze.collides(player.rect)
    assert all(not trap.hits(player.rect) for trap in level.traps)
    assert all(not enemy.touches(player.rect) for enemy in level.enemies)


def walk_path(level, player, path, max_frames=6000):
    """Steer the player along a list of tiles with the real movement code."""
    for col, row in path[1:]:
        target_x = col * TILE_SIZE + TILE_SIZE // 2
        target_y = row * TILE_SIZE + TILE_SIZE // 2
        for _ in range(max_frames):
            diff_x = target_x - player.rect.centerx
            diff_y = target_y - player.rect.centery
            if abs(diff_x) <= 3 and abs(diff_y) <= 3:
                break
            dx = 1 if diff_x > 3 else -1 if diff_x < -3 else 0
            dy = 1 if diff_y > 3 else -1 if diff_y < -3 else 0
            player.move(dx, dy, 1 / 60, level.maze)
            level.update(1 / 60, player)
        else:
            return False
    return True


@pytest.mark.parametrize("number", range(1, TOTAL_LEVELS + 1))
def test_level_can_be_finished_by_really_walking(number):
    """The player's hit box must fit through every corridor of every level."""
    level = Level(number)
    player = Player(max_health=999)         # we only test walking, not fighting
    put_player_on_tile(player, level.player_start)
    key = find_tile(number, "K")
    assert walk_path(level, player, level.maze.find_path(level.player_start, key))
    assert player.has_key
    door = level.maze.door_tile
    assert walk_path(level, player, level.maze.find_path(key, door))
    assert level.completed
