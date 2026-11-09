
import pygame

from src.settings import (IMAGES_DIR, SCREEN_HEIGHT, SCREEN_WIDTH, SOUNDS_DIR,
                          SPRITE_SCALE, TILE_SIZE)

IMAGE_NAMES = [
    "player_down", "player_up", "player_side", "goblin", "skeleton", "slime",
    "key", "coin", "heart", "heart_empty", "chest_closed", "chest_open",
    "barrel", "crate", "spikes_up", "spikes_down", "skull", "torch_0",
    "torch_1", "door_closed", "door_open", "wall_0", "wall_1", "floor_0",
    "floor_1", "floor_2",
]
SOUND_NAMES = ["click", "coin", "key", "chest", "heart", "hurt", "locked",
               "door_open", "win", "gameover"]


class AssetManager:
    def __init__(self):
        self._originals = {}
        self._scaled = {}
        self.sounds = {}
        self.sfx_volume = 0.7
        self.audio_ok = pygame.mixer.get_init() is not None
        self._load_images()
        self._load_sounds()
        self._make_effects()

    #loading
    def _load_images(self):
        for name in IMAGE_NAMES:
            path = IMAGES_DIR / (name + ".png")
            try:
                self._originals[name] = pygame.image.load(str(path)).convert_alpha()
            except (pygame.error, FileNotFoundError):
                placeholder = pygame.Surface((16, 16))
                placeholder.fill((200, 0, 200))
                self._originals[name] = placeholder

    def _load_sounds(self):
        if not self.audio_ok:
            return
        for name in SOUND_NAMES:
            try:
                self.sounds[name] = pygame.mixer.Sound(str(SOUNDS_DIR / (name + ".wav")))
            except (pygame.error, FileNotFoundError):
                pass

    def _make_effects(self):
        self.shadow = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
        for y in range(16):
            alpha = int(120 * (1 - y / 16) ** 2)
            pygame.draw.line(self.shadow, (10, 6, 20, alpha), (0, y), (TILE_SIZE, y))
        self.shadow_oval = pygame.Surface((32, 12), pygame.SRCALPHA)
        pygame.draw.ellipse(self.shadow_oval, (0, 0, 0, 90), self.shadow_oval.get_rect())
        self._glows = [self._make_glow(strength) for strength in (0.7, 0.85, 1.0)]
        self.background = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        for row in range(SCREEN_HEIGHT // TILE_SIZE):
            for col in range(SCREEN_WIDTH // TILE_SIZE):
                self.background.blit(self.image("wall_%d" % ((col + row) % 2)),
                                     (col * TILE_SIZE, row * TILE_SIZE))
        self.background.fill((105, 95, 130), special_flags=pygame.BLEND_RGB_MULT)
        self.vignette = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        for i in range(0, 140, 4):
            alpha = int(150 * (1 - i / 140) ** 2)
            pygame.draw.rect(self.vignette, (6, 4, 14, alpha),
                             (i, i, SCREEN_WIDTH - 2 * i, SCREEN_HEIGHT - 2 * i), 4)

    @staticmethod
    def _make_glow(strength, radius=110):
        glow = pygame.Surface((radius * 2, radius * 2))
        for r in range(radius, 0, -2):
            level = (1 - r / radius) ** 2 * strength
            pygame.draw.circle(glow, (int(95 * level), int(52 * level), int(14 * level)),
                               (radius, radius), r)
        return glow

    def glow(self, flicker):
        """Pick a glow surface. `flicker` is between 0.85 and 1.0."""
        index = min(2, max(0, int((flicker - 0.85) / 0.075 + 0.5)))
        return self._glows[index]

    #images
    def image(self, name, scale=SPRITE_SCALE):
        key = (name, scale)
        if key not in self._scaled:
            original = self._originals[name]
            size = (original.get_width() * scale, original.get_height() * scale)
            self._scaled[key] = pygame.transform.scale(original, size)
        return self._scaled[key]

    #sounds
    def play(self, name):
        sound = self.sounds.get(name)
        if sound is not None:
            sound.set_volume(self.sfx_volume)
            sound.play()

    def set_sfx_volume(self, volume):
        self.sfx_volume = volume

    def start_music(self, volume):
        if not self.audio_ok:
            return
        try:
            pygame.mixer.music.load(str(SOUNDS_DIR / "music.wav"))
            pygame.mixer.music.set_volume(volume)
            pygame.mixer.music.play(-1)
        except (pygame.error, FileNotFoundError):
            pass

    def set_music_volume(self, volume):
        if self.audio_ok:
            pygame.mixer.music.set_volume(volume)
