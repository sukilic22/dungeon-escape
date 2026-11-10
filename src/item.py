import pygame

from src.settings import *

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
        self.points = ITEM_INFO[kind]["points"]
        self.sound = ITEM_INFO[kind]["sound"]
        self.collected = False
        self.rect = pygame.Rect(0, 0, self.SIZE, self.SIZE)
        self.rect.center = (col * TILE_SIZE + TILE_SIZE // 2,
                            row * TILE_SIZE + TILE_SIZE // 2)


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
            bob = 0
        elif not self.collected:
            name = self.kind
            bob = 2 if int(time * 3) % 2 else 0
        else:
            return

        image = assets.image(name)
        rect = image.get_rect(center=(self.rect.centerx, self.rect.centery - bob))
        surface.blit(image, rect)


class Trap:

    CYCLE_TIME = 3.0     # seconds for one up/down cycle for spikes
    SIZE = 28            # hit box

    def __init__(self, col, row, cycling=False):
        self.cycling = cycling
        self.timer = (col + row) % 3 
        self.rect = pygame.Rect(0, 0, self.SIZE, self.SIZE)
        self.rect.center = (col * TILE_SIZE + TILE_SIZE // 2,
                            row * TILE_SIZE + TILE_SIZE // 2)

    @property
    def is_active(self):
        """True while the spikes are up and can hurt the player."""
        if not self.cycling:
            return True
        return (self.timer % self.CYCLE_TIME) < self.CYCLE_TIME / 2 # 1.5 sec spikes up, 1.5 sec down

    def update(self, dt):
        self.timer += dt

    def hits(self, rect):
        return self.is_active and self.rect.colliderect(rect)

    def draw(self, surface, assets):
        name = "spikes_up" if self.is_active else "spikes_down"
        image = assets.image(name)
        surface.blit(image, image.get_rect(center=self.rect.center))
