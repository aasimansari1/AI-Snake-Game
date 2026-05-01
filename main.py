"""
main.py
-------
Entry point for the AI Snake Game.

Responsibilities:
  * Initialize Pygame and the display window.
  * Show a start menu where the user picks Manual or AI mode.
  * Run the main game loop (input -> update -> draw).
  * Handle Game Over with restart and leaderboard display.
  * Manage difficulty (level / speed) progression.
  * Toggle AI on the fly with the `A` key.

Run with:
    python main.py
"""

import os
import sys
import pygame

from settings import (
    CELL_SIZE, HUD_HEIGHT,
    WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_TITLE,
    BASE_FPS, MAX_FPS, LEVEL_UP_EVERY, FPS_INCREMENT,
    COLOR_BG, COLOR_GRID, COLOR_HUD_BG, COLOR_HUD_TEXT,
    COLOR_SNAKE_HEAD, COLOR_SNAKE_BODY, COLOR_FOOD,
    COLOR_TITLE, COLOR_HINT, COLOR_ACCENT,
)
from snake import Snake, UP, DOWN, LEFT, RIGHT
from food import Food
from ai import choose_direction
from hamilton import build_cycle, build_index, choose_direction_hamilton
from leaderboard import add_score, get_top_scores


# =====================================================================
#                              SOUND
# =====================================================================
class SoundManager:
    """
    Lightweight wrapper around pygame.mixer that fails silently when no
    audio device or sound file is present (so the game still runs on
    headless / sound-less environments).
    """
    def __init__(self):
        self.enabled = False
        self.eat = None
        self.over = None
        try:
            pygame.mixer.init()
            self.enabled = True
        except pygame.error:
            return

        # Try to load optional sound files from an `assets/` folder.
        assets_dir = os.path.join(os.path.dirname(__file__), "assets")
        self.eat = self._safe_load(os.path.join(assets_dir, "eat.wav"))
        self.over = self._safe_load(os.path.join(assets_dir, "gameover.wav"))

    def _safe_load(self, path):
        if not os.path.exists(path):
            return None
        try:
            return pygame.mixer.Sound(path)
        except pygame.error:
            return None

    def play(self, sound):
        if self.enabled and sound is not None:
            try:
                sound.play()
            except pygame.error:
                pass


# =====================================================================
#                              DRAWING
# =====================================================================
def draw_grid(surface):
    """Subtle grid lines so the play area feels structured."""
    for x in range(0, WINDOW_WIDTH, CELL_SIZE):
        pygame.draw.line(surface, COLOR_GRID,
                         (x, HUD_HEIGHT), (x, WINDOW_HEIGHT))
    for y in range(HUD_HEIGHT, WINDOW_HEIGHT, CELL_SIZE):
        pygame.draw.line(surface, COLOR_GRID,
                         (0, y), (WINDOW_WIDTH, y))


def cell_rect(cx, cy, pad=1):
    """Convert a grid cell into a pixel rectangle (with a small padding)."""
    return pygame.Rect(
        cx * CELL_SIZE + pad,
        cy * CELL_SIZE + HUD_HEIGHT + pad,
        CELL_SIZE - 2 * pad,
        CELL_SIZE - 2 * pad,
    )


def draw_snake(surface, snake):
    for i, (cx, cy) in enumerate(snake.body):
        color = COLOR_SNAKE_HEAD if i == 0 else COLOR_SNAKE_BODY
        pygame.draw.rect(surface, color, cell_rect(cx, cy), border_radius=4)


def draw_food(surface, food):
    if food.position is None:
        return
    cx, cy = food.position
    pygame.draw.rect(surface, COLOR_FOOD, cell_rect(cx, cy), border_radius=8)


def draw_hud(surface, font, score, level, mode_label):
    pygame.draw.rect(surface, COLOR_HUD_BG, (0, 0, WINDOW_WIDTH, HUD_HEIGHT))
    score_text = font.render(f"Score: {score}", True, COLOR_HUD_TEXT)
    level_text = font.render(f"Level: {level}", True, COLOR_HUD_TEXT)
    is_ai = mode_label != "Manual"
    mode_color = COLOR_ACCENT if is_ai else COLOR_HUD_TEXT
    mode_text = font.render(f"Mode: {mode_label}", True, mode_color)
    hint_text = font.render("[A] AI on/off   [H] BFS<>Hamilton   [P] Pause   [Esc] Quit",
                            True, COLOR_HINT)
    surface.blit(score_text, (16, 8))
    surface.blit(level_text, (16, 32))
    surface.blit(mode_text, (180, 8))
    surface.blit(hint_text, (180, 32))


def draw_center_text(surface, lines, base_font, title_font):
    """Render an overlay with a title and a list of lines centered on screen."""
    overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    surface.blit(overlay, (0, 0))

    y = WINDOW_HEIGHT // 2 - (len(lines) * 20) - 40
    for i, (text, is_title) in enumerate(lines):
        font = title_font if is_title else base_font
        color = COLOR_TITLE if is_title else COLOR_HUD_TEXT
        rendered = font.render(text, True, color)
        rect = rendered.get_rect(center=(WINDOW_WIDTH // 2, y))
        surface.blit(rendered, rect)
        y += rendered.get_height() + 8


# =====================================================================
#                              SCREENS
# =====================================================================
def start_menu(surface, base_font, title_font):
    """
    Block until user picks a mode.
    Returns one of: "Manual", "BFS-AI", "Hamilton-AI".
    """
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    return "Manual"
                if event.key == pygame.K_2:
                    return "BFS-AI"
                if event.key == pygame.K_3:
                    return "Hamilton-AI"
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

        surface.fill(COLOR_BG)
        lines = [
            ("AI SNAKE GAME", True),
            ("B.Tech CSE Final Year Project", False),
            ("", False),
            ("Press  1  for  MANUAL  MODE", False),
            ("Press  2  for  BFS  AI  MODE     (shortest-path)", False),
            ("Press  3  for  HAMILTON  AI MODE (perfect, never dies)", False),
            ("", False),
            ("In game:  A toggles AI on/off   |   H swaps BFS <> Hamilton", False),
            ("Arrow Keys to move (manual)   |   P pauses   |   Esc quits", False),
        ]
        draw_center_text(surface, lines, base_font, title_font)
        pygame.display.flip()


def game_over_screen(surface, base_font, title_font, score, level, mode):
    """Show final score + leaderboard. Returns True to play again, False to quit."""
    add_score(score, mode)
    top = get_top_scores()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_r, pygame.K_RETURN, pygame.K_SPACE):
                    return True
                if event.key in (pygame.K_q, pygame.K_ESCAPE):
                    return False

        surface.fill(COLOR_BG)
        lines = [
            ("GAME OVER", True),
            (f"Score: {score}    Level: {level}    Mode: {mode}", False),
            ("", False),
            ("-- Top Scores --", False),
        ]
        for i, entry in enumerate(top, start=1):
            lines.append((
                f"{i}.  {entry['score']:>3}   {entry['mode']:<12}   {entry['date']}",
                False,
            ))
        lines.append(("", False))
        lines.append(("Press  R  to Restart      Q / Esc to Quit", False))
        draw_center_text(surface, lines, base_font, title_font)
        pygame.display.flip()


# =====================================================================
#                              MAIN LOOP
# =====================================================================
# Movement bindings — arrow keys only.
# `A` is reserved as the AI toggle (per project spec), so we deliberately
# do NOT map WASD; otherwise pressing `A` to toggle AI would also turn
# the snake left in the same frame.
KEY_TO_DIR = {
    pygame.K_UP: UP,
    pygame.K_DOWN: DOWN,
    pygame.K_LEFT: LEFT,
    pygame.K_RIGHT: RIGHT,
}


def run_game(surface, base_font, title_font, sounds, mode):
    """
    Run one playthrough.
    `mode` is one of: "Manual", "BFS-AI", "Hamilton-AI".
    Returns (final_score, level, final_mode).
    """
    snake = Snake()
    food = Food(snake.body)
    score = 0
    level = 1
    fps = BASE_FPS
    paused = False
    clock = pygame.time.Clock()

    # Hamilton cycle is fixed for the grid; build once and reuse.
    cycle = build_cycle()
    cycle_index = build_index(cycle)

    while True:
        # ---------- Event handling ----------
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return score, level, mode
                if event.key == pygame.K_p:
                    paused = not paused
                if event.key == pygame.K_a:        # AI on/off
                    mode = "Manual" if mode != "Manual" else "BFS-AI"
                if event.key == pygame.K_h:        # Swap BFS <-> Hamilton
                    if mode == "BFS-AI":
                        mode = "Hamilton-AI"
                    elif mode == "Hamilton-AI":
                        mode = "BFS-AI"
                # Arrow keys honoured only in manual mode
                if mode == "Manual" and event.key in KEY_TO_DIR:
                    snake.set_direction(KEY_TO_DIR[event.key])

        if paused:
            _render_frame(surface, base_font, title_font, snake, food,
                          score, level, mode, paused=True)
            clock.tick(15)
            continue

        # ---------- AI decision ----------
        if mode == "BFS-AI":
            snake.set_direction(choose_direction(snake, food))
        elif mode == "Hamilton-AI":
            snake.set_direction(
                choose_direction_hamilton(
                    snake, food, cycle, cycle_index, choose_direction
                )
            )

        # ---------- Update ----------
        snake.move()

        if snake.hits_wall() or snake.hits_self():
            sounds.play(sounds.over)
            return score, level, mode

        if snake.head == food.position:
            snake.grow()
            score += 1
            sounds.play(sounds.eat)
            new_level = 1 + score // LEVEL_UP_EVERY
            if new_level != level:
                level = new_level
                fps = min(MAX_FPS, BASE_FPS + (level - 1) * FPS_INCREMENT)
            food.respawn(snake.body)
            if food.position is None:
                # Board fully covered - ultimate win.
                return score, level, mode

        _render_frame(surface, base_font, title_font, snake, food,
                      score, level, mode, paused=False)
        clock.tick(fps)


def _render_frame(surface, base_font, title_font, snake, food,
                  score, level, mode, paused):
    surface.fill(COLOR_BG)
    draw_grid(surface)
    draw_food(surface, food)
    draw_snake(surface, snake)
    draw_hud(surface, base_font, score, level, mode)
    if paused:
        draw_center_text(surface,
                         [("PAUSED", True),
                          ("Press P to resume", False)],
                         base_font, title_font)
    pygame.display.flip()


def main():
    pygame.init()
    pygame.display.set_caption(WINDOW_TITLE)
    surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))

    base_font = pygame.font.SysFont("consolas", 18, bold=True)
    title_font = pygame.font.SysFont("consolas", 36, bold=True)

    sounds = SoundManager()

    # Initial mode pick: "Manual", "BFS-AI", or "Hamilton-AI".
    mode = start_menu(surface, base_font, title_font)

    while True:
        score, level, mode = run_game(
            surface, base_font, title_font, sounds, mode
        )
        play_again = game_over_screen(
            surface, base_font, title_font, score, level, mode
        )
        if not play_again:
            break
        # On restart, keep the player's last-played mode.

    pygame.quit()


if __name__ == "__main__":
    main()
