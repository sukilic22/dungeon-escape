import pygame

from src.player import Player
from src.settings import *
from src.ui import HUD, Button, Slider, TextInput, draw_panel, draw_text

CX = SCREEN_WIDTH // 2
GREY = (190, 186, 200)


def draw_crown(surface, center, scale=1.0):
    cx, cy = center
    shape = [(-30, 16), (-36, -20), (-16, -2), (0, -28), (16, -2), (36, -20), (30, 16)]
    points = [(cx + x * scale, cy + y * scale) for x, y in shape]
    pygame.draw.polygon(surface, COLOR_OUTLINE, points, 0)
    inner = [(cx + x * 0.86 * scale, cy + y * 0.86 * scale) for x, y in shape]
    pygame.draw.polygon(surface, (244, 200, 70), inner, 0)
    band = pygame.Rect(cx - 30 * scale, cy + 12 * scale, 60 * scale, 14 * scale)
    pygame.draw.rect(surface, COLOR_OUTLINE, band.inflate(6, 6))
    pygame.draw.rect(surface, (200, 146, 40), band)
    for gx, color in ((-16, (220, 60, 70)), (0, (80, 150, 240)), (16, (220, 60, 70))):
        pygame.draw.circle(surface, color, (int(cx + gx * scale), int(cy + 19 * scale)), int(4 * scale))


class Screen:

    keyboard_nav = True     # Up/Down/Enter move between buttons

    def __init__(self, game):
        self.game = game
        self.buttons = []
        self.focus = -1

    def on_enter(self):
        self.set_focus(-1)

    def set_focus(self, index):
        self.focus = index
        for i, button in enumerate(self.buttons):
            button.focused = (i == index)

    def handle_event(self, event):
        self.handle_buttons(event)

    def handle_buttons(self, event):
        for button in self.buttons:
            if button.handle_event(event):
                self.game.assets.play("click")
                return True
        if self.keyboard_nav and self.buttons and event.type == pygame.KEYDOWN:
            if event.key == pygame.K_DOWN:
                self.set_focus((self.focus + 1) % len(self.buttons))
            elif event.key == pygame.K_UP:
                self.set_focus((self.focus - 1) % len(self.buttons))
            elif event.key in (pygame.K_RETURN, pygame.K_SPACE) and self.focus >= 0:
                self.game.assets.play("click")
                self.buttons[self.focus].activate()
                return True
        return False

    def update(self, dt):
        pass

    def draw(self, surface):
        pass

    def draw_buttons(self, surface):
        for button in self.buttons:
            button.draw(surface)


#main menu
class MenuScreen(Screen):
    def __init__(self, game):
        super().__init__(game)
        g = game
        labels = [("Play", g.start_new_game),
                  ("High Scores", lambda: g.change_state("high_scores")),
                  ("Settings", lambda: g.change_state("settings")),
                  ("Admin Panel", lambda: g.change_state("admin_login")),
                  ("Quit", g.quit)]
        for i, (text, action) in enumerate(labels):
            self.buttons.append(Button(text, (CX - 140, 306 + i * 56, 280, 46), action))
        self.backdrop = None
        self.time = 0.0

    def _build_backdrop(self):
        assets = self.game.assets
        back = assets.background.copy()
        arch_center = (CX, 250)
        pygame.draw.circle(back, (58, 54, 78), arch_center, 262)
        pygame.draw.rect(back, (58, 54, 78), (CX - 262, 250, 524, SCREEN_HEIGHT))
        pygame.draw.circle(back, (22, 18, 34), arch_center, 236)
        pygame.draw.rect(back, (22, 18, 34), (CX - 236, 250, 472, SCREEN_HEIGHT))
        for angle_x in range(CX - 262, CX + 263, 40):         
            pygame.draw.line(back, (40, 36, 56), (angle_x, 270), (angle_x, SCREEN_HEIGHT), 2)
        for base_x in (60, 100, SCREEN_WIDTH - 60, SCREEN_WIDTH - 100):
            for i, y in enumerate(range(-10, 150 + (base_x % 3) * 20, 18)):
                width = 12 if i % 2 == 0 else 6
                pygame.draw.ellipse(back, (90, 88, 104), (base_x - width // 2, y, width, 20), 3)
        back.blit(assets.image("chest_closed", 6), (24, SCREEN_HEIGHT - 150))
        back.blit(assets.image("skull", 5), (SCREEN_WIDTH - 150, SCREEN_HEIGHT - 110))
        back.blit(assets.image("skull", 4), (SCREEN_WIDTH - 220, SCREEN_HEIGHT - 80))
        back.blit(assets.vignette, (0, 0))
        return back

    def on_enter(self):
        super().on_enter()
        if self.backdrop is None:
            self.backdrop = self._build_backdrop()

    def handle_event(self, event):
        if not self.handle_buttons(event):
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.game.quit()

    def update(self, dt):
        self.time += dt

    def draw(self, surface):
        assets = self.game.assets
        surface.blit(self.backdrop, (0, 0))

        frame = int(self.time * 6) % 2
        if frame == 0:
            glow = assets.glow(1.0)
        else:
            glow = assets.glow(0.85)
        torch = assets.image(f"torch_{frame}", 7)

        for x in (150, SCREEN_WIDTH - 150):
            surface.blit(glow, glow.get_rect(center=(x, 330)), special_flags=pygame.BLEND_RGB_ADD)
            surface.blit(torch, torch.get_rect(center=(x, 360)))

        draw_text(surface, "DUNGEON", 96, (226, 218, 198), (CX, 96))
        draw_text(surface, "ESCAPE", 96, (226, 218, 198), (CX, 176))
        draw_text(surface, "The Lost Key", 38, COLOR_GOLD, (CX, 246))
        for side in (-1, 1):                       # little gold arrows
            x = CX + side * 150
            pygame.draw.line(surface, COLOR_GOLD, (x, 246), (x + side * 40, 246), 3)
            pygame.draw.polygon(surface, COLOR_GOLD, [(x, 246), (x + side * 10, 240), (x + side * 10, 252)])
        self.draw_buttons(surface)
        draw_text(surface, "WASD / Arrows: move   ESC: pause", 20, (130, 126, 150),
                  (CX, SCREEN_HEIGHT - 18))



class GameplayScreen(Screen):
    SOUND_FOR_EVENT = {"coin": "coin", "key": "key", "chest": "chest", "heart": "heart",
                       "hurt": "hurt", "door_open": "door_open", "door_locked": "locked"}

    def __init__(self, game):
        super().__init__(game)
        self.hud = HUD()
        self.flash_timer = 0.0
        self.banner_timer = 0.0

    def reset_effects(self):
        """Called whenever a level starts."""
        self.flash_timer = 0.0
        self.banner_timer = 3.0

    def pause(self):
        self.game.change_state("pause")

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN and event.key in (pygame.K_ESCAPE, pygame.K_p):
            self.pause()
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if HUD.PAUSE_RECT.collidepoint(event.pos):
                self.game.assets.play("click")
                self.pause()
        elif event.type == getattr(pygame, "WINDOWFOCUSLOST", -1):
            self.pause()    

    def update(self, dt):
        game = self.game
        player, level = game.player, game.level
        dx, dy = Player.direction_from_keys(pygame.key.get_pressed())
        player.move(dx, dy, dt, level.maze)
        player.update(dt)
        events = level.update(dt, player)
        self.flash_timer = max(0.0, self.flash_timer - dt)
        self.banner_timer = max(0.0, self.banner_timer - dt)

        for event in events:
            if event == "hurt":
                self.flash_timer = 0.3
            if event in self.SOUND_FOR_EVENT:
                game.assets.play(self.SOUND_FOR_EVENT[event])
        if "dead" in events:
            game.game_over()
        elif "level_complete" in events:
            game.level_finished()

    def draw(self, surface):
        game = self.game
        assets = game.assets
        game.level.draw(surface, assets)
        game.player.draw(surface, assets)
        surface.blit(assets.vignette, (0, 0))

        if self.flash_timer > 0:
            flash = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            flash.fill((200, 20, 30, int(self.flash_timer * 500)))
            surface.blit(flash, (0, 0))

        self.hud.draw(surface, assets, game.player, game.level, KEYS_REQUIRED)
        self.hud.draw_pause_button(surface)

        if game.level.locked_hint_timer > 0:
            draw_text(surface, "The door is locked. Find the key!", 30, COLOR_GOLD, (CX, 130))

        if self.banner_timer > 0:
            rect = pygame.Rect(0, 0, 520, 70)
            rect.center = (CX, SCREEN_HEIGHT // 2 - 90)
            pygame.draw.rect(surface, (10, 8, 18), rect)
            pygame.draw.rect(surface, (120, 116, 146), rect, 3)
            draw_text(surface, f"Level {game.level.number}: {game.level.name}", 40, COLOR_GOLD, rect.center)


#pause menu
class PauseScreen(Screen):
    def __init__(self, game):
        super().__init__(game)
        self.buttons = [
            Button("Resume", (CX - 130, 270, 260, 46), lambda: game.change_state("gameplay")),
            Button("Main Menu", (CX - 130, 334, 260, 46), lambda: game.change_state("menu")),
            Button("Quit", (CX - 130, 398, 260, 46), game.quit, danger=True),
        ]

    def handle_event(self, event):
        if not self.handle_buttons(event):
            if event.type == pygame.KEYDOWN and event.key in (pygame.K_ESCAPE, pygame.K_p):
                self.game.change_state("gameplay")

    def draw(self, surface):
        self.game.screens["gameplay"].draw(surface)      # frozen game behind the menu
        dim = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        dim.fill((0, 0, 0, 150))
        surface.blit(dim, (0, 0))
        draw_panel(surface, (CX - 200, 150, 400, 340))
        draw_text(surface, "PAUSED", 60, COLOR_GOLD, (CX, 214))
        self.draw_buttons(surface)


#settings
class SettingsScreen(Screen):
    def __init__(self, game):
        super().__init__(game)
        self.music_slider = Slider((CX - 90, 246, 240, 24), 0.5)
        self.sfx_slider = Slider((CX - 90, 316, 240, 24), 0.7)
        self.left = Button("<", (CX - 110, 370, 44, 42), lambda: self.change_difficulty(-1), 30)
        self.right = Button(">", (CX + 106, 370, 44, 42), lambda: self.change_difficulty(1), 30)
        self.back = Button("Back", (CX - 110, 486, 220, 46), self.go_back)
        self.buttons = [self.left, self.right, self.back]

    def on_enter(self):
        super().on_enter()
        settings = self.game.settings
        self.music_slider.value = settings.music_volume
        self.sfx_slider.value = settings.sfx_volume

    def change_difficulty(self, step):
        self.game.settings.change_difficulty(step)

    def go_back(self):
        self.game.settings.save()
        self.game.change_state("menu")

    def handle_event(self, event):
        settings, assets = self.game.settings, self.game.assets
        if self.music_slider.handle_event(event):
            settings.music_volume = self.music_slider.value
            assets.set_music_volume(settings.music_volume)
        was_dragging = self.sfx_slider.dragging
        if self.sfx_slider.handle_event(event):
            settings.sfx_volume = self.sfx_slider.value
            assets.set_sfx_volume(settings.sfx_volume)
        if was_dragging and not self.sfx_slider.dragging:
            assets.play("coin")                     # let the player hear the new volume
        if not self.handle_buttons(event) and event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.go_back()
            elif event.key == pygame.K_LEFT:
                self.change_difficulty(-1)
            elif event.key == pygame.K_RIGHT:
                self.change_difficulty(1)

    def draw(self, surface):
        surface.blit(self.game.assets.background, (0, 0))
        draw_panel(surface, (CX - 300, 110, 600, 450))
        draw_text(surface, "SETTINGS", 60, COLOR_TEXT, (CX, 168))
        settings = self.game.settings
        for label, y, slider in (("Music", 258, self.music_slider), ("SFX", 328, self.sfx_slider)):
            draw_text(surface, label, 30, COLOR_TEXT, (CX - 240, y), "midleft")
            slider.draw(surface)
            draw_text(surface, "%d%%" % round(slider.value * 100), 26, GREY,
                      (CX + 210, y), "midleft")
        draw_text(surface, "Difficulty", 30, COLOR_TEXT, (CX - 240, 391), "midleft")
        draw_text(surface, settings.difficulty, 30, COLOR_GOLD, (CX + 34, 391))
        self.left.draw(surface)
        self.right.draw(surface)
        config = DIFFICULTIES[settings.difficulty]
        draw_text(surface, "Hearts: %d    Enemy speed: x%.2f" % (config["health"], config["enemy_speed"]),
                  22, GREY, (CX, 444))
        self.back.draw(surface)


#high scores
class HighScoresScreen(Screen):
    def __init__(self, game):
        super().__init__(game)
        self.buttons = [Button("Back", (CX - 110, 556, 220, 46), lambda: game.change_state("menu"))]

    def on_enter(self):
        super().on_enter()
        self.game.score_manager.load_scores()

    def handle_event(self, event):
        if not self.handle_buttons(event):
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.game.change_state("menu")

    def draw(self, surface):
        manager = self.game.score_manager
        surface.blit(self.game.assets.background, (0, 0))
        draw_panel(surface, (CX - 400, 40, 800, 600))
        draw_text(surface, "HIGH SCORES", 60, COLOR_GOLD, (CX, 100))
        draw_score_table(surface, manager.get_sorted_scores(10), 10, 160, 34)
        if manager.last_error:
            draw_text(surface, manager.last_error[:70], 20, COLOR_RED, (CX, 530))
        self.draw_buttons(surface)


def draw_score_table(surface, scores, max_rows, top, row_height):
    columns = [("Rank", CX - 355, "midleft"), ("Name", CX - 290, "midleft"),
               ("Score", CX + 20, "midright"), ("Level", CX + 90, "center"),
               ("Date", CX + 150, "midleft")]
    for title, x, anchor in columns:
        draw_text(surface, title, 24, GREY, (x, top), anchor)
    pygame.draw.line(surface, (120, 116, 146), (CX - 360, top + 18), (CX + 360, top + 18), 3)
    if not scores:
        draw_text(surface, "No scores yet - go play a game!", 28, GREY, (CX, top + 120))
        return
    medal = [COLOR_GOLD, (210, 214, 224), (205, 130, 80)]
    for i, score in enumerate(scores[:max_rows]):
        y = top + 40 + i * row_height
        color = medal[i] if i < 3 else COLOR_TEXT
        draw_text(surface, "%d." % (i + 1), 26, color, (columns[0][1], y), "midleft")
        draw_text(surface, score["name"], 26, color, (columns[1][1], y), "midleft")
        draw_text(surface, str(score["score"]), 26, color, (columns[2][1], y), "midright")
        draw_text(surface, str(score["level"]), 26, color, (columns[3][1], y), "center")
        draw_text(surface, score["date"], 22, GREY, (columns[4][1], y), "midleft")


#end-of-game base
class EndScreen(Screen):

    keyboard_nav = False   
    title = ""
    title_color = COLOR_TEXT
    again_text = "Try Again"

    def __init__(self, game):
        super().__init__(game)
        self.name_input = TextInput((CX - 130, 380, 260, 44), "Player", MAX_NAME_LENGTH,
                                    placeholder="Your name")
        self.buttons = [
            Button(self.again_text, (CX - 130, 446, 260, 46), self.play_again),
            Button("Main Menu", (CX - 130, 506, 260, 46), self.main_menu),
        ]
        self.saved = False

    def on_enter(self):
        super().on_enter()
        self.saved = False
        self.name_input.text = self.game.player_name

    def save_score(self):
        if not self.saved:
            self.game.save_result(self.name_input.text)
            self.saved = True

    def play_again(self):
        self.save_score()
        self.game.start_new_game()

    def main_menu(self):
        self.save_score()
        self.game.change_state("menu")

    def handle_event(self, event):
        if self.name_input.handle_event(event):
            self.play_again()
        else:
            self.handle_buttons(event)

    def update(self, dt):
        self.name_input.update(dt)

    def draw_common(self, surface, subtitle_lines):
        surface.blit(self.game.assets.background, (0, 0))
        draw_panel(surface, (CX - 260, 150, 520, 440))
        draw_text(surface, self.title, 64, self.title_color, (CX, 214))
        for i, line in enumerate(subtitle_lines):
            draw_text(surface, line, 30 if i == 0 else 24, COLOR_TEXT if i == 0 else GREY,
                      (CX, 270 + i * 34))
        draw_text(surface, "Enter your name:", 22, GREY, (CX, 360))
        self.name_input.draw(surface)
        self.draw_buttons(surface)


class GameOverScreen(EndScreen):
    title = "GAME OVER"
    title_color = (232, 56, 56)

    def draw(self, surface):
        game = self.game
        self.draw_common(surface, ["Your score: %d" % game.player.score,
                                   "Level reached: %d / %d" % (game.level_number, TOTAL_LEVELS)])
        surface.blit(game.assets.image("skull", 6), (CX - 48, 62))


class VictoryScreen(EndScreen):
    title = "VICTORY!"
    title_color = COLOR_GOLD
    again_text = "Play Again"

    def draw(self, surface):
        game = self.game
        self.draw_common(surface, ["You escaped the dungeon!",
                                   "Final score: %d" % game.player.score])
        draw_crown(surface, (CX, 110), 1.9)


#level complete
class LevelCompleteScreen(Screen):
    def __init__(self, game):
        super().__init__(game)
        self.buttons = [Button("Continue", (CX - 110, 486, 220, 46), game.next_level)]

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN and event.key in (pygame.K_RETURN, pygame.K_SPACE):
            self.game.assets.play("click")
            self.game.next_level()
        else:
            self.handle_buttons(event)

    def draw(self, surface):
        game = self.game
        base, health, time_bonus = game.last_bonus
        surface.blit(game.assets.background, (0, 0))
        draw_panel(surface, (CX - 250, 150, 500, 430))
        draw_text(surface, "LEVEL COMPLETE!", 54, COLOR_GOLD, (CX, 222))
        rows = [("Level bonus", base), ("Health bonus", health), ("Time bonus", time_bonus)]
        for i, (label, value) in enumerate(rows):
            y = 285 + i * 34
            draw_text(surface, label, 26, GREY, (CX - 170, y), "midleft")
            draw_text(surface, "+%d" % value, 26, COLOR_GREEN, (CX + 170, y), "midright")
        pygame.draw.line(surface, (120, 116, 146), (CX - 180, 388), (CX + 180, 388), 3)
        draw_text(surface, "Score: %d" % game.player.score, 40, COLOR_TEXT, (CX, 424))
        draw_text(surface, "Next Level?", 26, GREY, (CX, 462))
        self.draw_buttons(surface)
        draw_crown(surface, (CX, 120), 1.9)


#admin panel
class AdminLoginScreen(Screen):
    keyboard_nav = False

    def __init__(self, game):
        super().__init__(game)
        self.password_input = TextInput((CX - 170, 300, 340, 46), "", 20, masked=True,
                                        placeholder="password")
        self.buttons = [
            Button("Login", (CX - 170, 410, 160, 46), self.try_login),
            Button("Back", (CX + 10, 410, 160, 46), lambda: game.change_state("menu")),
        ]
        self.message = ""

    def on_enter(self):
        super().on_enter()
        self.password_input.text = ""
        self.message = ""

    def try_login(self):
        if check_admin_password(self.password_input.text):
            self.game.change_state("admin_panel")
        else:
            self.message = "Wrong password!"
            self.password_input.text = ""
            self.game.assets.play("locked")

    def handle_event(self, event):
        if self.password_input.handle_event(event):
            self.try_login()
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.game.change_state("menu")
        else:
            self.handle_buttons(event)

    def update(self, dt):
        self.password_input.update(dt)

    def draw(self, surface):
        surface.blit(self.game.assets.background, (0, 0))
        draw_panel(surface, (CX - 280, 150, 560, 400))
        draw_text(surface, "ADMIN LOGIN", 60, COLOR_GOLD, (CX, 214))
        draw_text(surface, "Enter the admin password:", 26, COLOR_TEXT, (CX, 268))
        self.password_input.draw(surface)
        if self.message:
            draw_text(surface, self.message, 26, COLOR_RED, (CX, 372))
        self.draw_buttons(surface)


class AdminPanelScreen(Screen):
    VISIBLE_ROWS = 7

    def __init__(self, game):
        super().__init__(game)
        self.clear_button = Button("Clear History", (CX - 280, 566, 260, 46), self.ask_confirmation,
                                   danger=True)
        self.back_button = Button("Back", (CX + 20, 566, 260, 46), lambda: game.change_state("menu"))
        self.yes_button = Button("Yes, delete", (CX - 210, 396, 200, 46), self.confirm_clear, danger=True)
        self.no_button = Button("Cancel", (CX + 10, 396, 200, 46), self.cancel_clear)
        self.buttons = [self.clear_button, self.back_button]
        self.confirming = False
        self.scroll = 0
        self.message = ""

    def on_enter(self):
        super().on_enter()
        self.game.score_manager.load_scores()
        self.confirming = False
        self.scroll = 0
        self.message = ""

    def ask_confirmation(self):
        if self.game.score_manager.scores:
            self.confirming = True
        else:
            self.message = "There is nothing to clear."

    def confirm_clear(self):
        if self.game.score_manager.clear_scores():
            self.message = "Score history cleared."
        else:
            self.message = "Could not clear the scores file!"
        self.confirming = False
        self.scroll = 0

    def cancel_clear(self):
        self.confirming = False
        self.message = "Cancelled - nothing was deleted."

    def handle_event(self, event):
        if self.confirming:          
            for button in (self.yes_button, self.no_button):
                if button.handle_event(event):
                    self.game.assets.play("click")
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.cancel_clear()
            return
        if self.handle_buttons(event):
            return
        total = len(self.game.score_manager.scores)
        max_scroll = max(0, total - self.VISIBLE_ROWS)
        if event.type == pygame.MOUSEWHEEL:
            self.scroll = max(0, min(max_scroll, self.scroll - event.y))
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.game.change_state("menu")

    def draw(self, surface):
        manager = self.game.score_manager
        surface.blit(self.game.assets.background, (0, 0))
        draw_panel(surface, (CX - 420, 24, 840, 630))
        draw_text(surface, "ADMIN PANEL", 56, COLOR_GOLD, (CX, 78))

        stats = manager.get_statistics()
        boxes = [("Games played", str(stats["games"])), ("Highest score", str(stats["highest"])),
                 ("Average score", str(stats["average"])), ("Best player", stats["best_player"])]
        for i, (label, value) in enumerate(boxes):
            rect = pygame.Rect(CX - 372 + i * 188, 112, 176, 62)
            pygame.draw.rect(surface, COLOR_OUTLINE, rect.inflate(6, 6))
            pygame.draw.rect(surface, (38, 34, 54), rect)
            draw_text(surface, label, 20, GREY, (rect.centerx, rect.y + 16))
            draw_text(surface, value, 28, COLOR_GOLD, (rect.centerx, rect.y + 42))

        rows = manager.get_sorted_scores()[self.scroll:self.scroll + self.VISIBLE_ROWS]
        draw_score_table(surface, rows, self.VISIBLE_ROWS, 212, 34)
        if len(manager.scores) > self.VISIBLE_ROWS:
            draw_text(surface, "Mouse wheel: scroll (%d-%d of %d)" % (
                self.scroll + 1, self.scroll + len(rows), len(manager.scores)),
                20, GREY, (CX, 520))
        if self.message:
            draw_text(surface, self.message, 24, COLOR_GREEN, (CX, 544))
        self.draw_buttons(surface)

        if self.confirming:
            dim = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            dim.fill((0, 0, 0, 180))
            surface.blit(dim, (0, 0))
            draw_panel(surface, (CX - 300, 220, 600, 250))
            draw_text(surface, "Delete ALL scores?", 44, COLOR_RED, (CX, 280))
            draw_text(surface, "%d saved games will be removed." % len(manager.scores),
                      26, COLOR_TEXT, (CX, 334))
            draw_text(surface, "This cannot be undone.", 24, GREY, (CX, 364))
            self.yes_button.draw(surface)
            self.no_button.draw(surface)
