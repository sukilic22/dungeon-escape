
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
    for _ in range(100):                  
        player.move(-1, 0, 0.05, maze)
    assert player.rect.left >= TILE_SIZE   


def test_player_cannot_leave_room_vertically():
    maze = Maze(ROOM)
    player = Player(1, 1)
    for _ in range(100):
        player.move(0, 1, 0.05, maze)
    assert player.rect.bottom <= 4 * TILE_SIZE


def test_take_damage_reduces_health():
    player = Player(max_health=3)
    assert player.take_damage() is True
    assert player.health == 2


def test_invincibility_prevents_double_damage():
    player = Player(max_health=3)
    player.take_damage()
    assert player.take_damage() is False
    assert player.health == 2
    player.update(Player.INVINCIBLE_TIME + 0.1)     
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
