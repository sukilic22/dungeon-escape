from collections import deque

import pygame

from src.settings import TILE_SIZE

# Characters in a level layout that block movement.
WALL = "#"
TORCH_WALL = "T"   
BARREL = "B"
CRATE = "X"
DOOR = "E"         # the exit door (blocks movement while it is locked)
SOLID_TILES = {WALL, TORCH_WALL, BARREL, CRATE}
TERRAIN_TILES = SOLID_TILES | {DOOR}


class Maze:
    def __init__(self, layout):
        self.rows = len(layout)
        self.cols = len(layout[0])
        self.grid = [
            [ch if ch in TERRAIN_TILES else "." for ch in row] for row in layout
        ]
        self.door_locked = True
        self.door_tile = None
        for row in range(self.rows):
            for col in range(self.cols):
                if self.grid[row][col] == DOOR:
                    self.door_tile = (col, row)

    #queries
    def in_bounds(self, col, row):
        return 0 <= col < self.cols and 0 <= row < self.rows

    def tile_at(self, col, row):
        return self.grid[row][col] if self.in_bounds(col, row) else WALL

    def is_solid(self, col, row):
        tile = self.tile_at(col, row)
        if tile == DOOR:
            return self.door_locked
        return tile in SOLID_TILES

    @staticmethod
    def tile_rect(col, row):
        return pygame.Rect(col * TILE_SIZE, row * TILE_SIZE, TILE_SIZE, TILE_SIZE)

    @staticmethod
    def pixel_to_tile(x, y):
        return int(x // TILE_SIZE), int(y // TILE_SIZE)

    def get_blocking_rects(self, rect):
        
        first_col, first_row = self.pixel_to_tile(rect.left, rect.top)
        last_col, last_row = self.pixel_to_tile(rect.right - 1, rect.bottom - 1)
        blocking = []
        for row in range(first_row, last_row + 1):
            for col in range(first_col, last_col + 1):
                if self.is_solid(col, row):
                    blocking.append(self.tile_rect(col, row))
        return blocking

    def collides(self, rect):
        """True if `rect` overlaps any solid tile."""
        return any(rect.colliderect(wall) for wall in self.get_blocking_rects(rect))

    #door
    def door_rect(self):
        if self.door_tile is None:
            return None
        return self.tile_rect(*self.door_tile)

    def unlock_door(self):
        self.door_locked = False

    #path finding (BFS)
    def find_path(self, start, goal, avoid=()):
        
        avoid = set(avoid)
        queue = deque([start])
        came_from = {start: None}
        while queue:
            current = queue.popleft()
            if current == goal:
                path = []
                while current is not None:
                    path.append(current)
                    current = came_from[current]
                return path[::-1]
            col, row = current
            for step in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                nxt = (col + step[0], row + step[1])
                if nxt in came_from or not self.in_bounds(*nxt):
                    continue
                tile = self.tile_at(*nxt)
                walkable = tile not in SOLID_TILES and tile != DOOR and nxt not in avoid
                if walkable or nxt == goal:
                    came_from[nxt] = current
                    queue.append(nxt)
        return None

    #drawing
    def draw(self, surface, assets, time):
        torch_frame = int(time * 6) % 2
        for row in range(self.rows):
            for col in range(self.cols):
                x, y = col * TILE_SIZE, row * TILE_SIZE
                tile = self.grid[row][col]
                if tile in (WALL, TORCH_WALL):
                    surface.blit(assets.image("wall_%d" % ((col + row) % 2)), (x, y))
                    if tile == TORCH_WALL:
                        surface.blit(assets.image("torch_%d" % torch_frame), (x, y))
                elif tile == DOOR:
                    surface.blit(assets.image("wall_0"), (x, y))
                    name = "door_closed" if self.door_locked else "door_open"
                    surface.blit(assets.image(name), (x, y))
                else:
                    self._draw_floor(surface, assets, col, row, x, y)
                    if tile == BARREL:
                        surface.blit(assets.image("barrel"), (x, y))
                    elif tile == CRATE:
                        surface.blit(assets.image("crate"), (x, y))
        self._draw_torch_glow(surface, assets, time)

    def _draw_floor(self, surface, assets, col, row, x, y):
        variant = 2 if (col * 7 + row * 13) % 23 == 0 else (col + row * 3) % 2
        surface.blit(assets.image("floor_%d" % variant), (x, y))
        if self.tile_at(col, row - 1) in (WALL, TORCH_WALL, DOOR):
            surface.blit(assets.shadow, (x, y))

    def _draw_torch_glow(self, surface, assets, time):
        flicker = 0.85 + 0.15 * ((int(time * 9) % 3) / 2)
        glow = assets.glow(flicker)
        for row in range(self.rows):
            for col in range(self.cols):
                if self.grid[row][col] == TORCH_WALL:
                    center = (col * TILE_SIZE + TILE_SIZE // 2, row * TILE_SIZE + TILE_SIZE // 2)
                    surface.blit(glow, glow.get_rect(center=center),
                                 special_flags=pygame.BLEND_RGB_ADD)
