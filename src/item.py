
import pygame

from src.settings import (CHEST_POINTS, COIN_POINTS, KEY_POINTS, TILE_SIZE)

# What each kind of item is worth and which sound it plays.
ITEM_INFO = {
    "coin": {"points": COIN_POINTS, "sound": "coin"},
    "key": {"points": KEY_POINTS, "sound": "key"},
    "chest": {"points": CHEST_POINTS, "sound": "chest"},
    "heart": {"points": 0, "sound": "heart"},
}


class Item:

    SIZE = 30

    def __init__(self, kind, col, row):
        if kind not in ITEM_INFO:
            raise ValueError("Unknown item kind: " + kind)
        self.kind = kind
        self.collected = False
        self.rect = pygame.Rect(0, 0, self.SIZE, self.SIZE)
        self.rect.center = (col * TILE_SIZE + TILE_SIZE // 2,
                            row * TILE_SIZE + TILE_SIZE // 2)

    @property
    def points(self):
        return ITEM_INFO[self.kind]["points"]

    @property
    def sound(self):
        return ITEM_INFO[self.kind]["sound"]

    def collect(self, player):
        if self.collected:
            return False
        self.collected = True
        player.add_score(self.points)
        if self.kind == "key":
            player.keys += 1
        elif self.kind == "heart":
            player.heal(1)
        return True

    def draw(self, surface, assets, time):
        if self.kind == "chest":
            name = "chest_open" if self.collected else "chest_closed"
            surface.blit(assets.image(name), self._image_pos(assets, name, 0))
        elif not self.collected:
            # Small up-and-down bobbing so items catch the eye.
            bob = 2 if int(time * 3) % 2 else 0
            surface.blit(assets.image(self.kind), self._image_pos(assets, self.kind, bob))

    def _image_pos(self, assets, name, bob):
        image = assets.image(name)
        return (self.rect.centerx - image.get_width() // 2,
                self.rect.centery - image.get_height() // 2 - bob)


class Trap:

    CYCLE_TIME = 3.0     # seconds for one up/down cycle
    SIZE = 28            # hit box is a bit smaller than the tile

    def __init__(self, col, row, cycling=False):
        self.cycling = cycling
        self.timer = ((col * 3 + row * 5) % 6) * 0.5
        self.rect = pygame.Rect(0, 0, self.SIZE, self.SIZE)
        self.rect.center = (col * TILE_SIZE + TILE_SIZE // 2,
                            row * TILE_SIZE + TILE_SIZE // 2)

    @property
    def is_active(self):
        """True while the spikes are up and can hurt the player."""
        if not self.cycling:
            return True
        return (self.timer % self.CYCLE_TIME) < self.CYCLE_TIME / 2

    def update(self, dt):
        self.timer += dt

    def hits(self, rect):
        return self.is_active and self.rect.colliderect(rect)

    def draw(self, surface, assets):
        name = "spikes_up" if self.is_active else "spikes_down"
        image = assets.image(name)
        surface.blit(image, image.get_rect(center=self.rect.center))
