import pygame

from src.settings import (COLOR_GOLD, COLOR_OUTLINE, COLOR_PANEL, COLOR_PANEL_DARK,
                          COLOR_TEXT, SCREEN_HEIGHT, SCREEN_WIDTH, TOTAL_LEVELS, TILE_SIZE)
from src.maze import SOLID_TILES

#text
_font_cache = {}
_text_cache = {}


def render_text(text, size=24, color=COLOR_TEXT, outline=None):
    if size not in _font_cache:
        _font_cache[size] = pygame.font.Font(None, size)
    return _font_cache[size].render(text, True, color)


def draw_text(surface, text, size, color, pos, anchor="center", outline=COLOR_OUTLINE):
    image = render_text(text, size, color, outline)
    rect = image.get_rect()
    setattr(rect, anchor, pos)
    surface.blit(image, rect)
    return rect


#panels
def draw_panel(surface, rect, frame=12):
    rect = pygame.Rect(rect)
    shadow = rect.move(6, 8)
    pygame.draw.rect(surface, (8, 6, 14), shadow)
    pygame.draw.rect(surface, COLOR_OUTLINE, rect)
    inner = rect.inflate(-6, -6)
    pygame.draw.rect(surface, (74, 70, 94), inner)
    # stone blocks along the four edges
    block = 18
    for i, x in enumerate(range(inner.left, inner.right, block)):
        w = min(block - 2, inner.right - x)
        shade = (104, 100, 128) if i % 2 == 0 else (88, 84, 110)
        pygame.draw.rect(surface, shade, (x, inner.top, w, frame))
        pygame.draw.rect(surface, shade, (x, inner.bottom - frame, w, frame))
    for i, y in enumerate(range(inner.top, inner.bottom, block)):
        h = min(block - 2, inner.bottom - y)
        shade = (104, 100, 128) if i % 2 == 0 else (88, 84, 110)
        pygame.draw.rect(surface, shade, (inner.left, y, frame, h))
        pygame.draw.rect(surface, shade, (inner.right - frame, y, frame, h))
    face = inner.inflate(-2 * frame, -2 * frame)
    pygame.draw.rect(surface, COLOR_OUTLINE, face.inflate(4, 4))
    pygame.draw.rect(surface, COLOR_PANEL_DARK, face)
    pygame.draw.rect(surface, COLOR_PANEL, face.inflate(-8, -8))
    for corner in (inner.topleft, inner.topright, inner.bottomleft, inner.bottomright):
        pygame.draw.rect(surface, COLOR_GOLD, (corner[0] - 4 + (4 if corner[0] == inner.left else 0),
                                               corner[1] - 4 + (4 if corner[1] == inner.top else 0), 8, 8))
    return face


#button
class Button:

    def __init__(self, text, rect, action=None, size=26, danger=False):
        self.text = text
        self.rect = pygame.Rect(rect)
        self.action = action
        self.size = size
        self.danger = danger
        self.pressed = False
        self.focused = False        
        self.enabled = True

    @property
    def hovered(self):
        return self.rect.collidepoint(pygame.mouse.get_pos())

    def handle_event(self, event):
        if not self.enabled:
            return False
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.pressed = True
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            was_pressed = self.pressed
            self.pressed = False
            if was_pressed and self.rect.collidepoint(event.pos):
                self.activate()
                return True
        return False

    def activate(self):
        if self.action is not None:
            self.action()

    def draw(self, surface):
        active = self.hovered or self.focused
        if self.danger:
            base, light, dark = ((150, 56, 62), (190, 84, 90), (96, 30, 38)) if active \
                else ((120, 46, 54), (160, 70, 76), (80, 26, 34))
        elif active:
            base, light, dark = (118, 112, 146), (156, 150, 184), (74, 70, 96)
        else:
            base, light, dark = (88, 84, 110), (124, 120, 150), (56, 52, 76)
        if self.pressed:
            base, light, dark = dark, dark, light
        rect = self.rect
        pygame.draw.rect(surface, (8, 6, 14), rect.move(0, 4))
        pygame.draw.rect(surface, COLOR_OUTLINE, rect)
        inner = rect.inflate(-6, -6)
        pygame.draw.rect(surface, base, inner)
        pygame.draw.rect(surface, light, (inner.x, inner.y, inner.w, 3))
        pygame.draw.rect(surface, light, (inner.x, inner.y, 3, inner.h))
        pygame.draw.rect(surface, dark, (inner.x, inner.bottom - 3, inner.w, 3))
        pygame.draw.rect(surface, dark, (inner.right - 3, inner.y, 3, inner.h))
        color = COLOR_GOLD if active else COLOR_TEXT
        offset = 2 if self.pressed else 0
        draw_text(surface, self.text, self.size, color,
                  (rect.centerx, rect.centery - 1 + offset))


#slider
class Slider:

    def __init__(self, rect, value=0.5):
        self.rect = pygame.Rect(rect)
        self.value = value
        self.dragging = False

    def _set_from_mouse(self, x):
        self.value = max(0.0, min(1.0, (x - self.rect.left) / self.rect.width))

    def handle_event(self, event):
        """Returns True when the value changed."""
        grab_area = self.rect.inflate(16, 24)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if grab_area.collidepoint(event.pos):
                self.dragging = True
                self._set_from_mouse(event.pos[0])
                return True
        elif event.type == pygame.MOUSEMOTION and self.dragging:
            self._set_from_mouse(event.pos[0])
            return True
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.dragging = False
        return False

    def nudge(self, amount):
        self.value = max(0.0, min(1.0, self.value + amount))

    def draw(self, surface):
        track = pygame.Rect(self.rect.x, self.rect.centery - 6, self.rect.w, 12)
        pygame.draw.rect(surface, COLOR_OUTLINE, track.inflate(6, 6))
        pygame.draw.rect(surface, (60, 56, 78), track)
        fill = pygame.Rect(track.x, track.y, int(track.w * self.value), track.h)
        pygame.draw.rect(surface, (214, 150, 60), fill)
        pygame.draw.rect(surface, COLOR_GOLD, (fill.x, fill.y, fill.w, 4))
        knob = pygame.Rect(0, 0, 16, 30)
        knob.center = (self.rect.x + int(self.rect.w * self.value), self.rect.centery)
        pygame.draw.rect(surface, COLOR_OUTLINE, knob.inflate(4, 4))
        pygame.draw.rect(surface, (150, 146, 176) if not self.dragging else (190, 186, 214), knob)
        pygame.draw.rect(surface, (210, 206, 230), (knob.x, knob.y, knob.w, 4))


#text input
class TextInput:

    def __init__(self, rect, text="", max_length=12, masked=False, placeholder=""):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.max_length = max_length
        self.masked = masked
        self.placeholder = placeholder
        self.timer = 0.0

    def handle_event(self, event):
        """Returns True if the player pressed Enter."""
        if event.type != pygame.KEYDOWN:
            return False
        if event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
            return True
        if event.key == pygame.K_BACKSPACE:
            self.text = self.text[:-1]
        elif event.unicode and event.unicode.isprintable() and len(self.text) < self.max_length:
            self.text += event.unicode
        return False

    def update(self, dt):
        self.timer += dt

    def draw(self, surface):
        pygame.draw.rect(surface, COLOR_OUTLINE, self.rect.inflate(6, 6))
        pygame.draw.rect(surface, (30, 28, 42), self.rect)
        pygame.draw.rect(surface, (90, 86, 112), self.rect, 2)
        shown = "*" * len(self.text) if self.masked else self.text
        if shown:
            rect = draw_text(surface, shown, 26, COLOR_TEXT,
                             (self.rect.x + 12, self.rect.centery), "midleft")
            caret_x = rect.right + 4
        else:
            draw_text(surface, self.placeholder, 22, (120, 116, 140),
                      (self.rect.x + 12, self.rect.centery), "midleft", outline=None)
            caret_x = self.rect.x + 12
        if int(self.timer * 2) % 2 == 0:
            pygame.draw.rect(surface, COLOR_GOLD, (caret_x, self.rect.centery - 11, 4, 22))


#HUD
class HUD:

    PAUSE_RECT = pygame.Rect(SCREEN_WIDTH - 44, SCREEN_HEIGHT - 44, 36, 36)

    def draw(self, surface, assets, player, level, keys_required):
        self._draw_stats(surface, assets, player, keys_required)
        self._draw_minimap(surface, level, player)
        label = "Level %d/%d - %s" % (level.number, TOTAL_LEVELS, level.name)
        draw_text(surface, label, 26, COLOR_GOLD, (SCREEN_WIDTH // 2, SCREEN_HEIGHT - 24))

    def _draw_stats(self, surface, assets, player, keys_required):
        panel = pygame.Rect(8, 8, 176, 88)
        back = pygame.Surface(panel.size, pygame.SRCALPHA)
        back.fill((14, 10, 22, 200))
        surface.blit(back, panel)
        pygame.draw.rect(surface, (120, 116, 146), panel, 3)
        pygame.draw.rect(surface, COLOR_OUTLINE, panel.inflate(6, 6), 3)
        heart_full = assets.image("heart", 2)
        heart_empty = assets.image("heart_empty", 2)
        for i in range(player.max_health):
            image = heart_full if i < player.health else heart_empty
            surface.blit(image, (panel.x + 8 + i * 32, panel.y + 1))
        surface.blit(assets.image("coin", 2), (panel.x + 8, panel.y + 30))
        draw_text(surface, str(player.score), 26, COLOR_TEXT, (panel.x + 52, panel.y + 46), "midleft")
        surface.blit(assets.image("key", 2), (panel.x + 8, panel.y + 54))
        color = COLOR_GOLD if player.keys >= keys_required else COLOR_TEXT
        draw_text(surface, "%d/%d" % (player.keys, keys_required), 26, color,
                  (panel.x + 52, panel.y + 70), "midleft")

    def _draw_minimap(self, surface, level, player):
        maze = level.maze
        cell = 4
        width, height = maze.cols * cell, maze.rows * cell
        box = pygame.Rect(SCREEN_WIDTH - width - 16, 12, width, height)
        pygame.draw.rect(surface, COLOR_OUTLINE, box.inflate(10, 10))
        pygame.draw.rect(surface, (120, 116, 146), box.inflate(6, 6), 2)
        pygame.draw.rect(surface, (18, 14, 28), box)
        for row in range(maze.rows):
            for col in range(maze.cols):
                tile = maze.tile_at(col, row)
                if tile in SOLID_TILES:
                    color = (96, 92, 120)
                elif tile == "E":
                    color = (214, 150, 60)
                else:
                    continue
                pygame.draw.rect(surface, color, (box.x + col * cell, box.y + row * cell, cell, cell))
        for item in level.items:
            if item.kind == "key" and not item.collected:
                x, y = item.rect.centerx * cell // TILE_SIZE, item.rect.centery * cell // TILE_SIZE
                pygame.draw.rect(surface, COLOR_GOLD, (box.x + x - 1, box.y + y - 1, 4, 4))
        px, py = player.rect.centerx * cell // TILE_SIZE, player.rect.centery * cell // TILE_SIZE
        pygame.draw.rect(surface, (110, 160, 255), (box.x + px - 1, box.y + py - 1, 4, 4))

    def draw_pause_button(self, surface):
        hovered = self.PAUSE_RECT.collidepoint(pygame.mouse.get_pos())
        rect = self.PAUSE_RECT
        pygame.draw.rect(surface, COLOR_OUTLINE, rect.inflate(4, 4), border_radius=6)
        pygame.draw.rect(surface, (118, 112, 146) if hovered else (84, 80, 106), rect, border_radius=6)
        bar = (240, 236, 224)
        pygame.draw.rect(surface, bar, (rect.x + 11, rect.y + 9, 5, 18))
        pygame.draw.rect(surface, bar, (rect.x + 20, rect.y + 9, 5, 18))
