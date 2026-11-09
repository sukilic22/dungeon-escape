"""Level: builds one dungeon from its layout and runs its game rules."""

from src.enemy import Enemy
from src.item import Item, Trap
from src.levels_data import LEVELS
from src.maze import Maze
from src.settings import KEYS_REQUIRED

ITEM_CHARS = {"K": "key", "C": "coin", "H": "chest", "+": "heart"}
ENEMY_CHARS = {"G": "goblin", "S": "skeleton", "L": "slime"}


class Level:
    def __init__(self, number, enemy_speed=1.0):
        """Create level `number` (1, 2 or 3)."""
        data = LEVELS[number - 1]
        self.number = number
        self.name = data["name"]
        self.maze = Maze(data["layout"])
        self.player_start = (1, 1)
        self.items = []
        self.enemies = []
        self.traps = []
        self.elapsed = 0.0          # seconds spent in this level
        self.completed = False
        self.locked_hint_timer = 0.0
        self._parse_layout(data["layout"], enemy_speed)

    def _parse_layout(self, layout, enemy_speed):
        """Walk over the text map and create an object for every symbol."""
        for row, line in enumerate(layout):
            for col, ch in enumerate(line):
                if ch == "P":
                    self.player_start = (col, row)
                elif ch in ITEM_CHARS:
                    self.items.append(Item(ITEM_CHARS[ch], col, row))
                elif ch in ENEMY_CHARS:
                    self.enemies.append(Enemy(ENEMY_CHARS[ch], col, row, enemy_speed))
                elif ch == "^":
                    self.traps.append(Trap(col, row, cycling=False))
                elif ch == "v":
                    self.traps.append(Trap(col, row, cycling=True))

    # --------------------------------------------------------------- rules
    def update(self, dt, player):
        """Advance the level by `dt` seconds.

        Returns a list of event names ("coin", "hurt", "door_open"...) so the
        screen can play the right sounds without the Level knowing about audio.
        """
        events = []
        self.elapsed += dt
        self.locked_hint_timer = max(0.0, self.locked_hint_timer - dt)
        for trap in self.traps:
            trap.update(dt)
        for enemy in self.enemies:
            enemy.update(dt, self.maze)

        events += self.check_items(player)
        events += self.check_hazards(player)
        events += self.check_door(player)
        if not player.is_alive:
            events.append("dead")
        return events

    def check_items(self, player):
        """Collect every item the player is touching."""
        events = []
        for item in self.items:
            if not item.collected and item.rect.colliderect(player.rect):
                if item.collect(player):
                    events.append(item.sound)
        return events

    def check_hazards(self, player):
        """Enemies and active traps take one health point from the player."""
        for enemy in self.enemies:
            if enemy.touches(player.rect) and player.take_damage(1):
                return ["hurt"]
        for trap in self.traps:
            if trap.hits(player.rect) and player.take_damage(1):
                return ["hurt"]
        return []

    def check_door(self, player):
        """Locked door: opens only with the key. Open door: finishes the level."""
        door = self.maze.door_rect()
        if door is None:
            return []
        if self.maze.door_locked:
            # "near the door" = within about 12 pixels of it
            if player.rect.inflate(24, 24).colliderect(door):
                if player.keys >= KEYS_REQUIRED:
                    self.maze.unlock_door()
                    return ["door_open"]
                if self.locked_hint_timer <= 0:
                    self.locked_hint_timer = 2.0
                    return ["door_locked"]
            return []
        if player.rect.colliderect(door):
            self.completed = True
            return ["level_complete"]
        return []

    # ------------------------------------------------------------- drawing
    def draw(self, surface, assets):
        self.maze.draw(surface, assets, self.elapsed)
        for trap in self.traps:
            trap.draw(surface, assets)
        for item in self.items:
            item.draw(surface, assets, self.elapsed)
        for enemy in self.enemies:
            enemy.draw(surface, assets)
