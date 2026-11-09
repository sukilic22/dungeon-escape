"""Generates every image and sound used by the game.

Run it once (the generated files are already included in the project):

    python tools/generate_assets.py            # images + sounds
    python tools/generate_assets.py --preview  # also writes docs/asset_preview.png

All sprites are drawn at 16 x 16 pixels from small ASCII-art tables and are
scaled x3 by the game (nearest-neighbour), which gives the "pixel art" look.
Because the art is made in code you can easily edit a colour or a sprite,
re-run this script and see the change in the game.
"""

import math
import os
import random
import sys
import wave
from array import array
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")
import pygame  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
IMAGES = ROOT / "assets" / "images"
SOUNDS = ROOT / "assets" / "sounds"

# One letter = one colour. '.' is transparent.
PALETTE = {
    "k": (20, 16, 28), "K": (52, 40, 72),
    "b": (58, 84, 176), "d": (36, 50, 120), "l": (110, 140, 230),
    "w": (255, 240, 170), "n": (112, 72, 42), "N": (70, 44, 28),
    "g": (240, 200, 60), "G": (178, 130, 30), "y": (255, 236, 130),
    "r": (214, 50, 60), "R": (140, 28, 44), "p": (255, 150, 160),
    "e": (92, 168, 64), "E": (56, 110, 50), "f": (150, 222, 100),
    "o": (228, 224, 208), "O": (150, 146, 148),
    "a": (140, 140, 162), "A": (82, 82, 104), "W": (255, 255, 255),
    "h": (255, 150, 40), "c": (150, 100, 56), "C": (96, 60, 34),
    "x": (255, 190, 90),
}


def sprite(rows, valign="bottom"):
    """Turn a list of strings into a 16x16 transparent surface."""
    surf = pygame.Surface((16, 16), pygame.SRCALPHA)
    assert len(rows) <= 16, "too many rows"
    if valign == "bottom":
        top = 16 - len(rows)
    elif valign == "middle":
        top = (16 - len(rows)) // 2
    else:
        top = 0
    for y, row in enumerate(rows):
        assert len(row) <= 16, "row too long: " + row
        left = (16 - len(row)) // 2
        for x, ch in enumerate(row):
            color = PALETTE.get(ch)
            if color:
                surf.set_at((left + x, top + y), color)
    return surf


def recolor(surf, mapping):
    """Return a copy of `surf` where some colours are swapped."""
    out = surf.copy()
    for x in range(out.get_width()):
        for y in range(out.get_height()):
            color = tuple(out.get_at((x, y)))
            if color[:3] in mapping:
                out.set_at((x, y), mapping[color[:3]] + (255,))
    return out


# ------------------------------------------------------------- characters
PLAYER_DOWN = [
    "kkkkkkkk",
    "kbbbbbbbbk",
    "kbbllllllbbk",
    "kbbkkkkkkbbk",
    "kbkkwkkwkkbk",
    "kbkkkkkkkkbk",
    "kbbkkkkkkbbk",
    "kkbbbddbbbkk",
    "kbbbbddbbbbk",
    "kbbbbddddbbbbk",
    "kbbbbbggbbbbbk",
    "kbbbbbbbbbbbbk",
    "kdbbbbbbbbbbdk",
    "kkddddddddddkk",
    "knnk....knnk",
    "kkkk....kkkk",
]
PLAYER_UP = [
    "kkkkkkkk",
    "kbbbbbbbbk",
    "kbbllllllbbk",
    "kbbbbbbbbbbk",
    "kbbbbbbbbbbk",
    "kbbbbbbbbbbk",
    "kbbbbddbbbbk",
    "kkbbbddbbbkk",
    "kbbbbddbbbbk",
    "kbbbbbddbbbbbk",
    "kbbbbbddbbbbbk",
    "kbbbbbbbbbbbbk",
    "kdbbbbbbbbbbdk",
    "kkddddddddddkk",
    "knnk....knnk",
    "kkkk....kkkk",
]
PLAYER_SIDE = [
    "kkkkkkkk",
    "kbbbbbbbbk",
    "kbbllllbbbbk",
    "kbbbbbbkkkkk",
    "kbbbbbkkkwkk",
    "kbbbbbkkkkkk",
    "kkbbbbbkkkk",
    "kbbbbddbbbbk",
    "kbbbbbddbbbbk",
    "kbbbbbbgggbbbk",
    "kbbbbbbbbbbbbk",
    "kdbbbbbbbbbbdk",
    "kkddddddddddkk",
    "knnk..knnk",
    "kkkk..kkkk",
]
GOBLIN = [
    "kk..kkkkkk..kk",
    "kek.keeeek.kek",
    "kEekeeeeeekeEk",
    ".kkkewkkwekkk.",
    "..keeeeeeeek..",
    "..keeoeeoeek..",
    "..kkkkkkkkkk..",
    "..knnnnnnnnk..",
    ".knnNnnnnNnnk.",
    "kekNnNNNNnNkek",
    "kekNnnnnnnNkek",
    ".kkkNnnnnNkkk.",
    "...kNNkkNNk...",
    "..kEEk..kEEk..",
    "..kkkk..kkkk..",
]
SKELETON = [
    "kkkkkkkk",
    "koooooook",
    "kooooooooook",
    "kooKKooKKook",
    "kooKrooKrook",
    "kooooKKooook",
    "kokokokokokk",
    "kooooooooook",
    "kookOoOoOook",
    "kokkOoOoOkok",
    "kokkoOoOokok",
    "kkkkoooookkk",
    "kook....kook",
    "kook....kook",
    "kkkk....kkkk",
]
SLIME = [
    "..kkkkkkkk..",
    ".keeffffeek.",
    "keeffffffeek",
    "keewkeewkeek",
    "keeeeeeeeeek",
    "keeekkkkeeek",
    "kEeeeeeeeeEk",
    "kEEEEEEEEEEk",
    ".kkkkkkkkkk.",
]

# ------------------------------------------------------------------ items
KEY = [
    "..kkkk..",
    ".kggyyk.",
    "kggkkggk",
    "kgk..kgk",
    "kggkkggk",
    ".kggggk.",
    "..kGgk..",
    "..kggkkk",
    "..kGgGGk",
    "..kggkkk",
    "..kGgGGk",
    "..kggkk.",
    "..kkkk..",
]
COIN = [
    "..kkkk..",
    ".kyyggk.",
    "kygggGgk",
    "kggGGGgk",
    "kggGGGgk",
    "kggggGgk",
    ".kgGGGk.",
    "..kkkk..",
]
HEART = [
    ".kkkk..kkkk.",
    "kpprrkkrrrrk",
    "kprrrrrrrrrk",
    "kprrrrrrrrRk",
    "krrrrrrrrrRk",
    ".krrrrrrrRk.",
    "..krrrrrRk..",
    "...krrrRk...",
    "....krRk....",
    ".....kk.....",
]
CHEST_CLOSED = [
    ".kkkkkkkkkkkk.",
    "knnnnnnnnnnnnk",
    "knnnnnnnnnnnnk",
    "kGGGGGGGGGGGGk",
    "kgggggkkgggggk",
    "kNNNNggggNNNNk",
    "knnnnngGnnnnnk",
    "knnnnnnnnnnnnk",
    "kNNNNNNNNNNNNk",
    "kkkkkkkkkkkkkk",
]
CHEST_OPEN = [
    ".kkkkkkkkkkkk.",
    "kNNNNNNNNNNNNk",
    "kNnnnnnnnnnnNk",
    "kkkkkkkkkkkkkk",
    "kgggyggggyyggk",
    "kggGggyggGgggk",
    "kGGGGGGGGGGGGk",
    "knnnnnnnnnnnnk",
    "kNNNNNNNNNNNNk",
    "kkkkkkkkkkkkkk",
]
BARREL = [
    "..kkkkkkkkkk..",
    ".knnnnnnnnnnk.",
    "kaaaaaaaaaaaak",
    "knnnNnnnnNnnnk",
    "knnnNnnnnNnnnk",
    "kAAAAAAAAAAAAk",
    "knnnNnnnnNnnnk",
    "knnnNnnnnNnnnk",
    "knnnNnnnnNnnnk",
    "kaaaaaaaaaaaak",
    ".knnnnNnnNnnk.",
    "..kkkkkkkkkk..",
]
CRATE = [
    "kkkkkkkkkkkkkk",
    "kcccccccccccck",
    "kCccccccccccCk",
    "kcCccccccccCck",
    "kccCccccccCcck",
    "kcccCccccCccck",
    "kccccCccCcccck",
    "kcccccCCccccck",
    "kccccCccCcccck",
    "kcccCccccCccck",
    "kccCccccccCcck",
    "kcCccccccccCck",
    "kCccccccccccCk",
    "kcccccccccccck",
    "kkkkkkkkkkkkkk",
]
SPIKES_UP = [
    ".W.....W.....W.",
    ".a.....a.....a.",
    ".a.....a.....a.",
    "aaA...aaA...aaA",
    "AAA...AAA...AAA",
    "...............",
    "...W.....W.....",
    "...a.....a.....",
    "...a.....a.....",
    "..aaA...aaA....",
    "..AAA...AAA....",
]
SPIKES_DOWN = [
    "kkkkkkkkkkkkkk",
    "kAAAAAAAAAAAAk",
    "kAkAAAkAAAkAAk",
    "kAAAAAAAAAAAAk",
    "kkkkkkkkkkkkkk",
]
SKULL = [
    "..kkkkkkkk..",
    ".kooooooook.",
    "kooooooooook",
    "kooKKooKKook",
    "kooKKooKKook",
    "kooooKKooook",
    ".kooooooook.",
    "..kokokoko..",
    "...kkkkkk...",
]
TORCH_A = [
    "...h....",
    "..hhh...",
    "..hyhh..",
    ".hhyyhh.",
    ".hyyyyh.",
    ".hhyyhh.",
    "..hhhh..",
    "..kaak..",
    "..kAAk..",
    "...kk...",
    "...nn...",
    "...nn...",
    "...Nn...",
]
TORCH_B = [
    "....h...",
    "..hhh...",
    "..hhyh..",
    ".hhyyhh.",
    ".hyyyyh.",
    ".hhyyhh.",
    "..hhhh..",
    "..kaak..",
    "..kAAk..",
    "...kk...",
    "...nn...",
    "...nn...",
    "...Nn...",
]
DOOR_CLOSED = [
    "....kkkkkkkk....",
    "..kkaaaaaaaakk..",
    ".kaaaaAAAAaaaak.",
    ".kaakkkkkkkkaak.",
    "kaakNNNNNNNNkaak",
    "kaakNnnNNnnNkaak",
    "kaakNnnNNnnNkaak",
    "kaakNnnNNnnNkaak",
    "kaakNnnggnnNkaak",
    "kaakNnngkgnNkaak",
    "kaakNnnnnnnNkaak",
    "kaakNnnNNnnNkaak",
    "kaakNnnNNnnNkaak",
    "kaakNnnNNnnNkaak",
    "kaakNnnNNnnNkaak",
    "kAAAAAAAAAAAAAAk",
]
DOOR_OPEN = [
    "....kkkkkkkk....",
    "..kkaaaaaaaakk..",
    ".kaaaaAAAAaaaak.",
    ".kaakkkkkkkkaak.",
    "kaakKKKKKKKKkaak",
    "kaakKKKKKKKKkaak",
    "kaakKKKKKKKKkaak",
    "kaakKKKKKKKKkaak",
    "kaakKKKKKKKKkaak",
    "kaakKKKKKKKKkaak",
    "kaakKKKKKKKKkaak",
    "kaakKKKxxKKKkaak",
    "kaakKKxxxxKKkaak",
    "kaakKxxxxxxKkaak",
    "kaakxxxxxxxxkaak",
    "kAAAAAAAAAAAAAAk",
]


# ------------------------------------------------------------------ tiles
def make_wall(seed):
    rnd = random.Random(seed)
    surf = pygame.Surface((16, 16))
    surf.fill((24, 20, 34))
    for row in range(2):
        y = row * 8
        x = 0 if row == 0 else -4
        while x < 16:
            rect = pygame.Rect(x + 1, y + 1, 7, 7)
            shade = rnd.randint(-8, 8)
            base = (58 + shade, 55 + shade, 82 + shade)
            surf.fill(base, rect)
            surf.fill((min(255, base[0] + 30),) + (min(255, base[1] + 30), min(255, base[2] + 32)),
                      (rect.x, rect.y, rect.w, 1))
            surf.fill((base[0] - 22, base[1] - 22, base[2] - 24),
                      (rect.x, rect.bottom - 1, rect.w, 1))
            for _ in range(3):
                px, py = rnd.randint(rect.x, rect.right - 1), rnd.randint(rect.y + 1, rect.bottom - 2)
                if 0 <= px < 16 and 0 <= py < 16:
                    surf.set_at((px, py), (base[0] - 12, base[1] - 12, base[2] - 12))
            x += 8
    return surf


def make_floor(seed, cracked=False):
    rnd = random.Random(seed)
    surf = pygame.Surface((16, 16))
    surf.fill((74, 68, 94))
    for gy in range(2):
        for gx in range(2):
            rect = pygame.Rect(gx * 8 + 1, gy * 8 + 1, 7, 7)
            shade = rnd.randint(-6, 6)
            base = (112 + shade, 104 + shade, 132 + shade)
            surf.fill(base, rect)
            surf.fill((base[0] + 14, base[1] + 14, base[2] + 16), (rect.x, rect.y, rect.w, 1))
            for _ in range(3):
                px, py = rnd.randint(rect.x, rect.right - 1), rnd.randint(rect.y, rect.bottom - 1)
                surf.set_at((px, py), (base[0] - 14, base[1] - 14, base[2] - 14))
    if cracked:
        x, y = 3, 3
        for _ in range(9):
            surf.set_at((x, y), (62, 56, 80))
            x += rnd.choice([0, 1, 1])
            y += rnd.choice([1, 1, 0])
    return surf


# ----------------------------------------------------------------- sounds
RATE = 22050


def tone(freq, dur, vol=0.4, shape="square", decay=3.0, slide=0.0):
    count = int(RATE * dur)
    out, phase = [], 0.0
    for i in range(count):
        t = i / RATE
        phase += (freq + slide * t) / RATE
        p = phase % 1.0
        if shape == "square":
            v = 1.0 if p < 0.5 else -1.0
        elif shape == "tri":
            v = 4 * abs(p - 0.5) - 1
        elif shape == "saw":
            v = 2 * p - 1
        else:
            v = math.sin(2 * math.pi * phase)
        out.append(v * vol * math.exp(-decay * i / count))
    return out


def noise(dur, vol=0.4, decay=4.0):
    count = int(RATE * dur)
    rnd = random.Random(1)
    return [rnd.uniform(-1, 1) * vol * math.exp(-decay * i / count) for i in range(count)]


def mix(*tracks):
    length = max(len(t) for t in tracks)
    return [sum(t[i] for t in tracks if i < len(t)) for i in range(length)]


def write_wav(name, samples):
    data = array("h", [int(max(-1.0, min(1.0, s)) * 32000) for s in samples])
    with wave.open(str(SOUNDS / name), "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(RATE)
        wav.writeframes(data.tobytes())


def arpeggio(notes, step=0.09, shape="tri", vol=0.35):
    out = []
    for f in notes:
        out += tone(f, step * 2.2, vol, shape, decay=4)[: int(RATE * step * 2.2)]
    return out


def make_music():
    """A slow, spooky 16-second loop: bass + arpeggio + soft pad."""
    chords = [  # (bass, [arpeggio notes])
        (110.0, [220.0, 261.6, 329.6, 261.6]),    # A minor
        (87.3, [174.6, 220.0, 261.6, 220.0]),     # F major
        (98.0, [196.0, 246.9, 293.7, 246.9]),     # G major
        (82.4, [164.8, 207.7, 246.9, 207.7]),     # E major
    ]
    track = []
    for bass, notes in chords:
        length = 4.0
        bass_t = tone(bass, length, 0.30, "sine", decay=0.8)
        pad = mix(tone(notes[0] * 0.5, length, 0.07, "sine", decay=0.3),
                  tone(notes[0] * 0.5 * 1.005, length, 0.07, "sine", decay=0.3))
        arp = []
        for i in range(16):
            arp += tone(notes[i % 4], 0.25, 0.13, "tri", decay=5)
        track += mix(bass_t, pad, arp)
    return track


def make_sounds():
    SOUNDS.mkdir(parents=True, exist_ok=True)
    write_wav("click.wav", tone(660, 0.06, 0.35, "square", 6))
    write_wav("coin.wav", tone(988, 0.07, 0.28, "square", 2) + tone(1319, 0.22, 0.28, "square", 5))
    write_wav("key.wav", arpeggio([523, 659, 784, 1047]))
    write_wav("chest.wav", arpeggio([392, 523, 659, 784, 1047], 0.08, "square", 0.25))
    write_wav("heart.wav", tone(440, 0.3, 0.4, "sine", 3, slide=600))
    write_wav("hurt.wav", mix(noise(0.25, 0.5, 5), tone(180, 0.25, 0.4, "saw", 4, slide=-300)))
    write_wav("locked.wav", tone(130, 0.1, 0.4, "square", 2) + tone(100, 0.18, 0.4, "square", 4))
    write_wav("door_open.wav", mix(noise(0.5, 0.25, 3), tone(120, 0.5, 0.3, "saw", 2, slide=300)))
    write_wav("win.wav", arpeggio([523, 659, 784, 1047, 1319], 0.12, "tri", 0.4)
              + tone(1047, 0.5, 0.35, "tri", 3))
    write_wav("gameover.wav", arpeggio([392, 330, 262, 196], 0.22, "saw", 0.3)
              + tone(130, 0.8, 0.3, "saw", 3))
    write_wav("music.wav", make_music())


# ------------------------------------------------------------------- main
def save(name, surf):
    IMAGES.mkdir(parents=True, exist_ok=True)
    pygame.image.save(surf, str(IMAGES / (name + ".png")))


def make_images():
    images = {
        "player_down": sprite(PLAYER_DOWN),
        "player_up": sprite(PLAYER_UP),
        "player_side": sprite(PLAYER_SIDE),
        "goblin": sprite(GOBLIN),
        "skeleton": sprite(SKELETON),
        "slime": sprite(SLIME),
        "key": sprite(KEY, "middle"),
        "coin": sprite(COIN, "middle"),
        "heart": sprite(HEART, "middle"),
        "chest_closed": sprite(CHEST_CLOSED, "middle"),
        "chest_open": sprite(CHEST_OPEN, "middle"),
        "barrel": sprite(BARREL, "middle"),
        "crate": sprite(CRATE, "middle"),
        "spikes_up": sprite(SPIKES_UP, "middle"),
        "spikes_down": sprite(SPIKES_DOWN, "middle"),
        "skull": sprite(SKULL),
        "torch_0": sprite(TORCH_A, "middle"),
        "torch_1": sprite(TORCH_B, "middle"),
        "door_closed": sprite(DOOR_CLOSED, "top"),
        "door_open": sprite(DOOR_OPEN, "top"),
        "wall_0": make_wall(1),
        "wall_1": make_wall(2),
        "floor_0": make_floor(3),
        "floor_1": make_floor(4),
        "floor_2": make_floor(5, cracked=True),
    }
    images["heart_empty"] = recolor(images["heart"], {
        PALETTE["r"]: (60, 56, 72), PALETTE["R"]: (44, 40, 56), PALETTE["p"]: (84, 80, 100)})
    for name, surf in images.items():
        save(name, surf)
    return images


def make_preview(images):
    scale = 4
    names = list(images)
    cols = 8
    rows = (len(names) + cols - 1) // cols
    sheet = pygame.Surface((cols * 16 * scale + 16, rows * 16 * scale + 16))
    sheet.fill((40, 36, 52))
    for i, name in enumerate(names):
        big = pygame.transform.scale(images[name], (16 * scale, 16 * scale))
        sheet.blit(big, (8 + (i % cols) * 16 * scale, 8 + (i // cols) * 16 * scale))
    out = ROOT / "docs"
    out.mkdir(exist_ok=True)
    pygame.image.save(sheet, str(out / "asset_preview.png"))


if __name__ == "__main__":
    pygame.init()
    pygame.display.set_mode((1, 1))
    imgs = make_images()
    print("images written to", IMAGES)
    make_sounds()
    print("sounds written to", SOUNDS)
    if "--preview" in sys.argv:
        make_preview(imgs)
        print("preview written to docs/asset_preview.png")
