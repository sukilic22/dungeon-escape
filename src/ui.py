
import pygame

from src.settings import *
from src.maze import SOLID_TILES

_font_cache = {}


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


def draw_panel(surface, rect):
    rect = pygame.Rect(rect)
    pygame.draw.rect(surface, (8, 6, 14), rect.move(6, 8), border_radius=8)
    pygame.draw.rect(surface, (74, 70, 94), rect, border_radius=8)
    pygame.draw.rect(surface, COLOR_OUTLINE, rect, 4, border_radius=8)
    inner = rect.inflate(-16, -16)
    pygame.draw.rect(surface, COLOR_PANEL_DARK, inner, border_radius=4)
    pygame.draw.rect(surface, COLOR_PANEL, inner.inflate(-6, -6), border_radius=4)


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
            btn_color = (180, 60, 70) if active else (130, 40, 50)
        else:
            btn_color = (125, 120, 150) if active else (85, 80, 105)

        pygame.draw.rect(surface, (10, 8, 16), self.rect.move(0, 4), border_radius=6)
        pygame.draw.rect(surface, btn_color, self.rect, border_radius=6)
        pygame.draw.rect(surface, COLOR_OUTLINE, self.rect, 3, border_radius=6)

        text_color = COLOR_GOLD if active else COLOR_TEXT
        draw_text(surface, self.text, self.size, text_color, self.rect.center)


class Slider:

    def __init__(self, rect, value=0.5):
        self.rect = pygame.Rect(rect)
        self.value = value
        self.dragging = False

    def _set_from_mouse(self, x):
        self.value = max(0.0, min(1.0, (x - self.rect.left) / self.rect.width))

    def handle_event(self, event):
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

    def draw(self, surface):
        track = pygame.Rect(self.rect.x, self.rect.centery - 4, self.rect.w, 8)
        pygame.draw.rect(surface, (50, 46, 65), track, border_radius=4)

        fill_w = int(self.rect.w * self.value)
        fill = pygame.Rect(self.rect.x, self.rect.centery - 4, fill_w, 8)
        pygame.draw.rect(surface, COLOR_GOLD, fill, border_radius=4)

        knob_x = self.rect.x + fill_w
        pygame.draw.circle(surface, (220, 220, 230), (knob_x, self.rect.centery), 10)
        pygame.draw.circle(surface, COLOR_OUTLINE, (knob_x, self.rect.centery), 10, 2)


class TextInput:

    def __init__(self, rect, text="", max_length=12, masked=False, placeholder=""):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.max_length = max_length
        self.masked = masked
        self.placeholder = placeholder
        self.timer = 0.0

    def handle_event(self, event):
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
        pygame.draw.rect(surface, (30, 28, 42), self.rect, border_radius=4)
        pygame.draw.rect(surface, (100, 95, 120), self.rect, 2, border_radius=4)

        shown = "*" * len(self.text) if self.masked else self.text
        if shown:
            rect = draw_text(surface, shown, 26, COLOR_TEXT, (self.rect.x + 10, self.rect.centery), "midleft")
            cursor_x = rect.right + 2
        else:
            draw_text(surface, self.placeholder, 22, (120, 116, 140), (self.rect.x + 10, self.rect.centery), "midleft")
            cursor_x = self.rect.x + 10

        if int(self.timer * 2) % 2 == 0:
            pygame.draw.rect(surface, COLOR_GOLD, (cursor_x, self.rect.centery - 10, 3, 20))


class HUD:

    PAUSE_RECT = pygame.Rect(SCREEN_WIDTH - 44, SCREEN_HEIGHT - 44, 36, 36)

    def draw(self, surface, assets, player, level, keys_required):
        self._draw_stats(surface, assets, player, keys_required)
        label = f"Level {level.number}/{TOTAL_LEVELS} - {level.name}"
        draw_text(surface, label, 26, COLOR_GOLD, (SCREEN_WIDTH // 2, SCREEN_HEIGHT - 24))

    def _draw_stats(self, surface, assets, player, keys_required):
        panel = pygame.Rect(8, 8, 176, 88)
        pygame.draw.rect(surface, (14, 10, 22), panel, border_radius=6)
        pygame.draw.rect(surface, (120, 116, 146), panel, 2, border_radius=6)

        for i in range(player.max_health):
            img = assets.image("heart" if i < player.health else "heart_empty", 2)
            surface.blit(img, (panel.x + 8 + i * 32, panel.y + 2))

        surface.blit(assets.image("coin", 2), (panel.x + 8, panel.y + 30))
        draw_text(surface, str(player.score), 26, COLOR_TEXT, (panel.x + 52, panel.y + 46), "midleft")

        surface.blit(assets.image("key", 2), (panel.x + 8, panel.y + 54))
        key_color = COLOR_GOLD if player.keys >= keys_required else COLOR_TEXT
        draw_text(surface, f"{player.keys}/{keys_required}", 26, key_color, (panel.x + 52, panel.y + 70), "midleft")

   

    def draw_pause_button(self, surface):
        color = (118, 112, 146) if self.PAUSE_RECT.collidepoint(pygame.mouse.get_pos()) else (84, 80, 106)
        pygame.draw.rect(surface, color, self.PAUSE_RECT, border_radius=6)
        pygame.draw.rect(surface, COLOR_OUTLINE, self.PAUSE_RECT, 2, border_radius=6)
        pygame.draw.rect(surface, (240, 236, 224), (self.PAUSE_RECT.x + 11, self.PAUSE_RECT.y + 9, 5, 18))
        pygame.draw.rect(surface, (240, 236, 224), (self.PAUSE_RECT.x + 20, self.PAUSE_RECT.y + 9, 5, 18))