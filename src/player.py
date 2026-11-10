import pygame

from src.settings import TILE_SIZE


class Player:
    SIZE = 28               
    SPEED = 190              
    INVINCIBLE_TIME = 1.2    

    def __init__(self, col=1, row=1, max_health=3):
        self.max_health = max_health
        self.health = max_health
        self.score = 0
        self.keys = 0
        self.facing = "down"
        self.moving = False
        self.invincible_timer = 0.0
        self.walk_timer = 0.0
        self.rect = pygame.Rect(0, 0, self.SIZE, self.SIZE)
        self.set_tile_position(col, row)

    def set_tile_position(self, col, row):
        """Put the player in the middle of the given tile."""
        self.x = col * TILE_SIZE + (TILE_SIZE - self.SIZE) / 2
        self.y = row * TILE_SIZE + (TILE_SIZE - self.SIZE) / 2
        self.rect.topleft = (round(self.x), round(self.y))

    #input
    @staticmethod
    def direction_from_keys(pressed):
        dx = dy = 0
        if pressed[pygame.K_LEFT] or pressed[pygame.K_a]:
            dx -= 1
        if pressed[pygame.K_RIGHT] or pressed[pygame.K_d]:
            dx += 1
        if pressed[pygame.K_UP] or pressed[pygame.K_w]:
            dy -= 1
        if pressed[pygame.K_DOWN] or pressed[pygame.K_s]:
            dy += 1
        return dx, dy

    def move(self, dx, dy, dt, maze):
        self.moving = (dx != 0 or dy != 0)
        if not self.moving:
            return
        if dx != 0 and dy != 0:      
            dx *= 0.7071
            dy *= 0.7071
        self._move_axis(dx * self.SPEED * dt, 0, maze)
        self._move_axis(0, dy * self.SPEED * dt, maze)
        self.walk_timer += dt
        if dx > 0:
            self.facing = "right"
        elif dx < 0:
            self.facing = "left"
        elif dy > 0:
            self.facing = "down"
        elif dy < 0:
            self.facing = "up"

    def _move_axis(self, move_x, move_y, maze):
        self.x += move_x
        self.y += move_y
        self.rect.topleft = (round(self.x), round(self.y))
        for wall in maze.get_blocking_rects(self.rect):
            if not self.rect.colliderect(wall):
                continue
            if move_x > 0:
                self.rect.right = wall.left
                self.x = self.rect.x
            elif move_x < 0:
                self.rect.left = wall.right
                self.x = self.rect.x
            if move_y > 0:
                self.rect.bottom = wall.top
                self.y = self.rect.y
            elif move_y < 0:
                self.rect.top = wall.bottom
                self.y = self.rect.y

    #state
    def update(self, dt):
        if self.invincible_timer > 0:
            self.invincible_timer = max(0.0, self.invincible_timer - dt)

    @property
    def is_alive(self):
        return self.health > 0

    @property
    def is_invincible(self):
        return self.invincible_timer > 0

    @property
    def has_key(self):
        return self.keys > 0

    def take_damage(self, amount=1):
        if self.is_invincible or not self.is_alive:
            return False
        self.health = max(0, self.health - amount)
        self.invincible_timer = self.INVINCIBLE_TIME
        return True

    def heal(self, amount=1):
        self.health = min(self.max_health, self.health + amount)

    def add_score(self, points):
        self.score += points

    def draw(self, surface, assets):
        if self.is_invincible and int(self.invincible_timer * 12) % 2 == 0:
            return
        if self.facing in ("left", "right"):
            image = assets.image("player_side")
            if self.facing == "left":
                image = pygame.transform.flip(image, True, False)
        else:
            image = assets.image("player_" + self.facing)
        bob = 3 if (self.moving and int(self.walk_timer * 10) % 2) else 0
        pos = (self.rect.centerx - image.get_width() // 2,
               self.rect.bottom - image.get_height() + 6 - bob)
        surface.blit(assets.shadow_oval, (self.rect.centerx - 16, self.rect.bottom - 8))
        surface.blit(image, pos)
