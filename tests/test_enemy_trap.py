"""Tests for Enemy patrol movement and Trap timing."""

from src.enemy import Enemy
from src.item import Trap
from src.maze import Maze
from src.settings import TILE_SIZE

CORRIDOR = [
    "#######",
    "#.....#",
    "#######",
]


def test_enemy_moves_along_its_axis():
    maze = Maze(CORRIDOR)
    goblin = Enemy("goblin", 1, 1)
    start = goblin.rect.x
    goblin.update(0.1, maze)
    assert goblin.rect.x > start


def test_enemy_turns_around_at_wall():
    maze = Maze(CORRIDOR)
    goblin = Enemy("goblin", 1, 1)
    assert goblin.direction == 1
    for _ in range(300):
        goblin.update(0.02, maze)
        assert goblin.rect.right <= 6 * TILE_SIZE      # never inside the right wall
        assert goblin.rect.left >= TILE_SIZE           # never inside the left wall
    # after 6 seconds it must have bounced at least once
    assert goblin.direction in (1, -1)


def test_enemy_reverses_direction_on_collision():
    maze = Maze(CORRIDOR)
    goblin = Enemy("goblin", 5, 1)
    for _ in range(100):
        goblin.update(0.02, maze)
        if goblin.direction == -1:
            break
    assert goblin.direction == -1


def test_skeleton_walks_vertically():
    maze = Maze(["###", "#.#", "#.#", "#.#", "###"])
    skeleton = Enemy("skeleton", 1, 1)
    x, y = skeleton.rect.topleft
    skeleton.update(0.1, maze)
    assert skeleton.rect.x == x and skeleton.rect.y > y


def test_difficulty_speed_multiplier():
    slow, fast = Enemy("goblin", 1, 1, 0.75), Enemy("goblin", 1, 1, 1.3)
    assert slow.speed < fast.speed


def test_enemy_touch_detection():
    goblin = Enemy("goblin", 1, 1)
    assert goblin.touches(goblin.rect.copy())
    far = goblin.rect.move(500, 0)
    assert not goblin.touches(far)


def test_unknown_enemy_kind_is_rejected():
    import pytest
    with pytest.raises(ValueError):
        Enemy("dragon", 1, 1)


def test_static_trap_is_always_active():
    trap = Trap(1, 1, cycling=False)
    for _ in range(10):
        assert trap.is_active
        trap.update(0.7)


def test_cycling_trap_goes_up_and_down():
    trap = Trap(0, 0, cycling=True)
    states = set()
    for _ in range(60):
        states.add(trap.is_active)
        trap.update(0.1)
    assert states == {True, False}


def test_inactive_trap_does_not_hurt():
    trap = Trap(0, 0, cycling=True)
    trap.timer = Trap.CYCLE_TIME * 0.75           # second half = spikes are down
    assert not trap.is_active
    assert not trap.hits(trap.rect)
