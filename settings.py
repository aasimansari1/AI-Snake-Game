"""
settings.py
-----------
Central configuration for the AI Snake Game.
All tunable constants (window size, colors, speed, levels) live here so that
gameplay can be adjusted without touching the core logic files.
"""

# ---------- Grid / Window ----------
CELL_SIZE = 20                       # Size (in pixels) of one grid cell
GRID_WIDTH = 30                      # Number of cells horizontally
GRID_HEIGHT = 22                     # Number of cells vertically
HUD_HEIGHT = 60                      # Top bar height for score / mode display

WINDOW_WIDTH = CELL_SIZE * GRID_WIDTH
WINDOW_HEIGHT = CELL_SIZE * GRID_HEIGHT + HUD_HEIGHT

WINDOW_TITLE = "AI Snake Game  -  B.Tech CSE Final Year Project"

# ---------- Speed / Levels ----------
BASE_FPS = 10                        # Starting speed (frames/moves per second)
MAX_FPS = 25                         # Cap on speed so it stays playable
LEVEL_UP_EVERY = 5                   # Score points needed for next level
FPS_INCREMENT = 1                    # FPS gained per level

# ---------- Colors (R, G, B) ----------
COLOR_BG = (15, 18, 25)
COLOR_GRID = (28, 32, 42)
COLOR_HUD_BG = (10, 12, 18)
COLOR_HUD_TEXT = (235, 235, 235)
COLOR_SNAKE_HEAD = (0, 200, 120)
COLOR_SNAKE_BODY = (0, 160, 90)
COLOR_FOOD = (230, 70, 70)
COLOR_OVERLAY = (0, 0, 0, 180)       # Semi-transparent black
COLOR_TITLE = (255, 215, 0)
COLOR_HINT = (180, 180, 180)
COLOR_ACCENT = (90, 170, 255)

# ---------- Files ----------
LEADERBOARD_FILE = "leaderboard.json"
MAX_LEADERBOARD_ENTRIES = 5
