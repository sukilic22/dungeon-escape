# Dungeon Escape – The Lost Key 🗝️

A 2D retro desktop dungeon crawler developed in **Python** and **Pygame** for the *Advanced Programming with Python* university course.

---

## 📖 Project Overview

**Dungeon Escape: The Lost Key** is a desktop dungeon game where the player controls a hooded adventurer navigating through handcrafted dungeon floors, collecting keys, avoiding traps, evading patrolling monsters, and unlocking the exit door to advance.

The game features:
- **3 Handcrafted Levels** with progressive difficulty (Level 1: *The Cellar*, Level 2: *The Crypt*, Level 3: *The Lost Vault*).
- **Exact Visual Style** matching the provided pixel-art design (hooded blue hero, goblins, skeletons, slimes, stone masonry, torchlight glow, stone frame menus).
- **Smooth Movement & Sliding Collisions** against walls, barrels, and crates.
- **Dynamic Hazards & Items**: Fixed and cycling floor spikes, moving patrol enemies, coins, hearts, treasure chests, and keys.
- **Robust State-Machine Architecture**: Clean separation between screens (Main Menu, Gameplay, Pause Menu, Settings, High Scores, Level Complete, Game Over, Victory, Admin Login, Admin Panel).
- **Persistent JSON Score System**: Safe atomic file writes, corrupt JSON handling, and leaderboards sorted by score and level.
- **Secure In-Game Admin Panel**: Password-authenticated (`admin123` via SHA-256 hash check) with stats (games played, highest, average, best player) and score history reset with modal confirmation.
- **87 Automated Pytest Tests**: Comprehensive test suite verifying game logic, physics, path solvability (BFS), and data integrity.

---

## 🛠️ Project Structure

```text
dungeon_escape/
├── assets/                  # Game multimedia assets
│   ├── images/              # Pixel-art sprites (player, enemies, tiles, items, UI)
│   └── sounds/              # Synthesized 8-bit sound effects & looping dungeon music
├── data/                    # Persistent runtime data
│   ├── scores.json          # Player high score records
│   └── settings.json        # Audio volumes & difficulty settings
├── docs/                    # Screenshots and documentation artifacts
│   └── screenshots/         # Automated visual snapshots of all screens
├── src/                     # Core Python source code
│   ├── __init__.py
│   ├── asset_manager.py     # Asset caching, sound playback & lighting shaders
│   ├── enemy.py             # Enemy OOP entity with obstacle-rebounding patrol AI
│   ├── game.py              # Main Game controller & state machine coordinator
│   ├── item.py              # Item (Coin, Key, Chest, Heart) & Trap (Spikes) classes
│   ├── level.py             # Level parser, hazard updates & win condition checking
│   ├── levels_data.py       # Handcrafted 20x14 tile maps for Levels 1, 2, and 3
│   ├── maze.py              # 2D Grid collision system & BFS pathfinding solver
│   ├── player.py            # Player entity, movement vectors, health & i-frames
│   ├── score_manager.py     # JSON persistence, statistics & score calculations
│   ├── screens.py           # Screen state classes (Menu, Gameplay, Pause, Admin, etc.)
│   ├── settings.py          # Global constants, difficulty tuning & password hashing
│   └── ui.py                # Custom UI widgets (Button, Slider, TextInput, HUD, Minimap)
├── tests/                   # Pytest test suite (87 tests)
│   ├── test_enemy_trap.py   # AI patrol and trap timing tests
│   ├── test_game_flow.py    # End-to-end game state transitions and playthroughs
│   ├── test_level.py        # Item collection, door mechanics & BFS reachability
│   ├── test_maze.py         # Grid collisions, bounds & pathfinding
│   ├── test_player.py       # Player physics, health, invincibility & scoring
│   └── test_score_manager.py# JSON error handling, atomic saves & admin authentication
├── tools/                   # Developer helper scripts
│   ├── generate_assets.py   # Procedural pixel-art & sound synthesizer
│   ├── smoke_run.py         # Headless/windowed smoke test
│   └── take_screenshots.py  # Headless screenshot generator for documentation
├── conftest.py              # Pytest configuration (headless SDL dummy drivers)
├── main.py                  # Desktop application entry point
└── requirements.txt         # Project dependencies (pygame, pytest)
```

---

## 🚀 Quickstart Guide

### 1. Prerequisites
- Python 3.9+ installed on your system.

### 2. Setup Virtual Environment & Install Dependencies
Open a terminal in the project directory:
```bash
# Create virtual environment
python3 -m venv .venv

# Activate virtual environment
# On macOS / Linux:
source .venv/bin/activate
# On Windows:
.venv\Scripts\activate

# Install required packages
pip install -r requirements.txt
```

### 3. Running the Game
To launch the desktop game window:
```bash
python main.py
```
Or run directly from **VS Code**: press `F5` or select **"Run Dungeon Escape"** in the Run & Debug tab.

### 4. Running the Tests
To verify all 87 automated tests:
```bash
pytest -v
```

---

## 🎮 Controls & Gameplay Guide

| Action | Controls |
| :--- | :--- |
| **Move Hero** | `W`, `A`, `S`, `D` or `Arrow Keys` (diagonal movement supported) |
| **Pause Game** | `ESC` or `P` (or click the bottom-right pause icon) |
| **Menu Navigation** | `Mouse Click` or `Up` / `Down` arrows + `Enter` |
| **Text Fields** | Keyboard typing + `Enter` to submit |

### Rules & Mechanics:
- **Objective**: Collect the **golden key** (`K`) in each level to unlock the dungeon door (`E`), then enter the doorway.
- **Health**: Starting hearts depend on selected difficulty (`Normal = 3`, `Easy = 4`, `Hard = 2`).
- **Damage & Invincibility**: Touching an active spike trap or enemy deducts 1 heart. After taking damage, the player gains 1.2 seconds of invulnerability (indicated by blinking).
- **Items**:
  - 🪙 **Coin**: +10 points
  - 🗝️ **Key**: +25 points and unlocks the level exit
  - 📦 **Treasure Chest**: +50 bonus points
  - ❤️ **Heart**: Restores 1 lost health point (up to maximum)
- **Score Bonus upon Level Completion**:
  $$\text{Bonus} = (100 \times \text{Level}) + (25 \times \text{Remaining Hearts}) + \max(0, 60 - \text{Seconds Taken}) \times 2$$

---

## 🔐 Admin Panel

Access the **Admin Panel** from the Main Menu:
- **Default Password**: `admin123`
- **Security**: The password is never stored in plaintext; authentication validates against an SHA-256 cryptographic digest.
- **Features**:
  - Live statistics display: total games recorded, highest score, average score, and top player.
  - Scrollable leaderboard table with rankings, player names, scores, level reached, and date timestamps.
  - Safe **"Clear History"** function with a modal confirmation dialog preventing accidental deletion.

---

## 🏛️ Object-Oriented Architecture (OOP)

The project adheres to clean OOP principles designed for academic presentation:

1. **`Game`**: Central coordinator. Manages Pygame's display surface, framerate clock, global settings, asset manager, and delegates execution to the current active state.
2. **`Screen` (State Pattern)**: Abstract base class implemented by 10 specialized screens (`MenuScreen`, `GameplayScreen`, `PauseScreen`, `SettingsScreen`, `HighScoresScreen`, `LevelCompleteScreen`, `GameOverScreen`, `VictoryScreen`, `AdminLoginScreen`, `AdminPanelScreen`).
3. **`Maze`**: Responsible strictly for static environment geometry, tile queries, and 2-axis AABB collision resolution.
4. **`Player`**: Encapsulates position vectors, independent horizontal/vertical collision sliding, health management, and i-frame timers.
5. **`Enemy`**: Implements obstacle-rebounding patrol movement (`goblin` and `slime` move horizontally, `skeleton` moves vertically).
6. **`Item` & `Trap`**: Discrete game entities handling pickups and cyclical environmental hazards.
7. **`ScoreManager`**: Handles persistent JSON file I/O using atomic temp-file replacement (`os.replace`) to protect against corruption during power loss or abrupt exit.

---

## 🧪 Testing Highlights

The test suite in `tests/` covers:
- **Grid & Collision Logic**: Tile lookups, out-of-bounds safety, and boundary collision.
- **BFS Level Solvability**: Algorithmic proof using Breadth-First Search that all 3 levels have guaranteed reachable paths from Start $\to$ Key $\to$ Exit avoiding all static traps.
- **Simulated Real Walking**: Player hitbox clearance verification through every maze corridor under actual physical velocity vectors.
- **JSON File Resilience**: Safe recovery from missing files, empty files, malformed JSON structures, and bad record formats.
- **Admin Authentication**: Hash validation testing for matching and incorrect passwords.
