"""Enemy: a monster that patrols back and forth until it hits a wall."""

import pygame

from src.settings import TILE_SIZE

# axis: the direction it walks in, speed: pixels per second
ENEMY_TYPES = {
    "goblin": {"axis": "x", "speed": 95},
    "skeleton": {"axis": "y", "speed": 80},
    "slime": {"axis": "x", "speed": 55},
}


class Enemy:
    SIZE = 30

    def __init__(self, kind, col, row, speed_multiplier=1.0):
        if kind not in ENEMY_TYPES:
            raise ValueError("Unknown enemy kind: " + kind)
        info = ENEMY_TYPES[kind]
        self.kind = kind
        self.axis = info["axis"]
        self.speed = info["speed"] * speed_multiplier
        self.direction = 1          # +1 = right/down, -1 = left/up
        self.timer = 0.0
        self.rect = pygame.Rect(0, 0, self.SIZE, self.SIZE)
        self.x = col * TILE_SIZE + (TILE_SIZE - self.SIZE) / 2
        self.y = row * TILE_SIZE + (TILE_SIZE - self.SIZE) / 2
        self.rect.topleft = (round(self.x), round(self.y))

    def update(self, dt, maze):
        """Walk forward. When a wall is hit, turn around (simple patrol AI)."""
        self.timer += dt
        step = self.speed * self.direction * dt
        if self.axis == "x":
            self.x += step
        else:
            self.y += step
        self.rect.topleft = (round(self.x), round(self.y))

        for wall in maze.get_blocking_rects(self.rect):
            if not self.rect.colliderect(wall):
                continue
            if self.axis == "x":
                if self.direction > 0:
                    self.rect.right = wall.left
                else:
                    self.rect.left = wall.right
                self.x = self.rect.x
            else:
                if self.direction > 0:
                    self.rect.bottom = wall.top
                else:
                    self.rect.top = wall.bottom
                self.y = self.rect.y
            self.direction *= -1
            break

    def touches(self, rect):
        """True if the enemy overlaps `rect` (used for hurting the player)."""
        return self.rect.colliderect(rect)

    def draw(self, surface, assets):
        image = assets.image(self.kind)
        if self.axis == "x":
            flip = self.direction < 0                 # face the walking direction
        else:
            flip = int(self.timer * 4) % 2 == 1       # waddle while walking up/down
        if flip:
            image = pygame.transform.flip(image, True, False)
        bob = 3 if int(self.timer * 6) % 2 else 0
        pos = (self.rect.centerx - image.get_width() // 2,
               self.rect.bottom - image.get_height() + 6 - bob)
        surface.blit(assets.shadow_oval, (self.rect.centerx - 16, self.rect.bottom - 8))
        surface.blit(image, pos)
