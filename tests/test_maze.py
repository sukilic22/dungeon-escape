"""Tests for Maze: solid tiles, collision rectangles, the door and path finding."""

import pygame

from src.levels_data import LEVELS
from src.maze import Maze
from src.settings import TILE_SIZE

SMALL_MAP = [
    "#####",
    "#.B.#",
    "#...E",
    "#####",
]


def test_wall_and_floor_tiles():
    maze = Maze(SMALL_MAP)
    assert maze.is_solid(0, 0)          # wall
    assert not maze.is_solid(1, 1)      # floor
    assert maze.is_solid(2, 1)          # barrel blocks movement


def test_outside_of_map_is_solid():
    maze = Maze(SMALL_MAP)
    assert maze.is_solid(-1, 0)
    assert maze.is_solid(10, 10)


def test_items_and_enemies_are_stored_as_floor():
    maze = Maze(["#####", "#PKC#", "#####"])
    assert maze.tile_at(1, 1) == "."
    assert maze.tile_at(2, 1) == "."


def test_blocking_rects_found_next_to_wall():
    maze = Maze(SMALL_MAP)
    # a rectangle that overlaps the wall on the left of tile (1, 1)
    rect = pygame.Rect(TILE_SIZE - 5, TILE_SIZE + 5, 20, 20)
    walls = maze.get_blocking_rects(rect)
    assert maze.tile_rect(0, 1) in walls
    assert maze.collides(rect)


def test_no_collision_in_open_floor():
    maze = Maze(SMALL_MAP)
    rect = pygame.Rect(TILE_SIZE + 10, 2 * TILE_SIZE + 10, 20, 20)
    assert not maze.collides(rect)


def test_locked_door_blocks_until_unlocked():
    maze = Maze(SMALL_MAP)
    assert maze.door_tile == (4, 2)
    assert maze.is_solid(4, 2)          # locked
    maze.unlock_door()
    assert not maze.is_solid(4, 2)      # open


def test_find_path_returns_connected_tiles():
    maze = Maze(SMALL_MAP)
    path = maze.find_path((1, 1), (3, 2))
    assert path[0] == (1, 1) and path[-1] == (3, 2)
    for (c1, r1), (c2, r2) in zip(path, path[1:]):
        assert abs(c1 - c2) + abs(r1 - r2) == 1      # each step is one tile


def test_find_path_goes_around_barrel():
    maze = Maze(SMALL_MAP)
    path = maze.find_path((1, 1), (3, 1))
    assert (2, 1) not in path


def test_find_path_none_when_blocked():
    maze = Maze(["#####", "#.#.#", "#####"])
    assert maze.find_path((1, 1), (3, 1)) is None


def test_find_path_can_avoid_tiles():
    maze = Maze(["#####", "#...#", "#####"])
    assert maze.find_path((1, 1), (3, 1), avoid={(2, 1)}) is None


def test_every_level_has_the_right_shape():
    for data in LEVELS:
        layout = data["layout"]
        assert len(layout) == 14
        assert all(len(row) == 20 for row in layout)
        joined = "".join(layout)
        assert joined.count("P") == 1       # one start
        assert joined.count("K") == 1       # one key
        assert joined.count("E") == 1       # one exit
        # outer border must be solid so nothing can leave the map
        assert set(layout[0]) <= set("#TE")
        assert set(layout[-1]) == {"#"}
        assert all(row[0] == "#" and row[-1] == "#" for row in layout)
