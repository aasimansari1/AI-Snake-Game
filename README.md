# AI Snake Game

**B.Tech CSE Final Year Project**

A complete Snake game built in Python with Pygame that supports both
**manual play** and a **self-playing AI** powered by Breadth-First Search
(BFS) pathfinding with a flood-fill survival fallback.

---

## Features

- Three modes: **Manual** (arrow keys), **BFS-AI** (shortest-path), and **Hamilton-AI** (perfect, never-dies)
- BFS shortest-path AI with flood-fill survival fallback
- Hamilton-cycle AI that follows a precomputed grid-covering loop and is provably collision-free
- Score tracking and increasing difficulty (speed scales with level)
- Random food spawning that never overlaps the snake
- Pause, restart, and on-the-fly AI controls (`A` toggles AI on/off, `H` swaps BFS ↔ Hamilton)
- Local **leaderboard** (top 5 scores, persisted in `leaderboard.json`)
- Optional sound effects (drop `.wav` files into `assets/`)
- Clean, modular code structure — each concern in its own file

---

## Project Structure

```
AI Snake Game/
├── main.py            # Entry point: game loop, menu, HUD, screens
├── snake.py           # Snake entity (movement, growth, collisions)
├── food.py            # Food entity (random spawning)
├── ai.py              # BFS pathfinding + flood-fill survival logic
├── hamilton.py        # Hamilton-cycle construction + cycle-following AI
├── leaderboard.py     # Local JSON-backed top-score storage
├── settings.py        # All tunable constants (colors, sizes, speed)
├── requirements.txt   # Python dependencies
├── README.md          # This file
└── assets/            # (optional) eat.wav, gameover.wav
```

---

## How to Run

### 1. Install Python 3.8 or newer

Download from <https://www.python.org/downloads/>.

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Launch the game

```bash
python main.py
```

### 4. Controls

| Key             | Action                                       |
| --------------- | -------------------------------------------- |
| `1`             | Start Manual mode (from menu)                |
| `2`             | Start BFS-AI mode (from menu)                |
| `3`             | Start Hamilton-AI mode (from menu)           |
| `Arrow Keys`    | Move snake (manual mode only)                |
| `A`             | Toggle AI on/off mid-game                    |
| `H`             | Swap BFS-AI ↔ Hamilton-AI mid-game           |
| `P`             | Pause / resume                               |
| `R` / `Enter`   | Restart after Game Over                      |
| `Esc` / `Q`     | Quit                                         |

### 5. (Optional) Sound

Place WAV files at `assets/eat.wav` and `assets/gameover.wav`. The game
runs silently without them — no errors.

---

## How the AI Works

The project ships **two distinct AI strategies** so you can compare them
in the demo / viva.

### BFS-AI ([ai.py](ai.py))

Runs every game tick and picks the next direction in three stages:

**Stage 1 — BFS shortest path.** The grid is an unweighted graph; each
cell is a node, each non-blocked neighbour is an edge. The snake's body
is treated as obstacles (except the tail tip, which vacates next tick,
so the AI can chase its own tail through tight corridors). BFS gives the
*shortest* path from the head to the food in `O(V + E)`. The AI takes
the first step along that path.

**Stage 2 — Flood-fill survival fallback.** If no path to the food
exists (snake coiled around itself), the AI evaluates each safe
neighbour by running a flood fill and counts reachable open space. It
picks the neighbour with the **largest reachable area**, buying time
until a path opens.

**Stage 3 — Last-resort.** If no safe neighbour exists, the AI keeps
its current direction; Game Over is unavoidable that tick.

BFS-AI is fast and feels intelligent, but it can paint itself into a
corner late in the game.

### Hamilton-AI ([hamilton.py](hamilton.py))

A **Hamilton cycle** is a path through a graph that visits every node
exactly once and returns to the starting node. If we precompute one for
the entire grid and the snake just *follows* it, the snake can never
collide with itself or the wall — guaranteeing it eventually fills the
whole board (the ultimate Snake win condition).

The cycle is built once with a simple snake-pattern construction
(requires an even `GRID_HEIGHT`, which our default 22 satisfies):

1. Walk row 0 left-to-right.
2. Snake through rows 1..H-1 across columns 1..W-1, alternating
   direction each row.
3. Return up column 0.

The cycle index of every cell is stored in a hash map for O(1)
look-ups. Each tick the AI just steps to the next cell in the cycle —
choosing forward or backward traversal so it never has to 180-reverse
when the mode is toggled mid-game. If the cycle's next cell is briefly
blocked (only happens after switching from BFS-AI), the controller
falls back to BFS-AI for one step.

**Trade-off:** Hamilton-AI is *provably safe* but slow — it walks every
cell, so it never takes shortcuts. BFS-AI is fast but can die in the
endgame. A production-grade snake bot combines both (Hamilton with safe
BFS shortcuts); the codebase is structured so that extension is easy.

---

## Difficulty Scaling

- The game starts at **10 FPS** (`BASE_FPS` in `settings.py`).
- Every **5 points** scored advances the level by **1**.
- Each level adds **+1 FPS**, capped at **25 FPS** (`MAX_FPS`).

Tune any of these values in `settings.py` without touching game logic.

---

## Leaderboard

After Game Over, the score (with mode and timestamp) is appended to
`leaderboard.json`, sorted, and the top 5 are displayed on the
Game Over screen. The file is created automatically on first save.

---

## For Project Submission

Suggested talking points for a viva / report:

1. **Pathfinding choice.** BFS is optimal on unweighted grids and trivial
   to implement; A* would be overkill here since all moves cost 1.
2. **Tail-as-walkable trick.** The snake's tail vacates its cell each
   tick (unless growing), so treating it as walkable lets the AI follow
   itself through tight corridors.
3. **Survival heuristic.** Greedy shortest-path alone deadlocks the snake
   against its own body; the flood-fill fallback dramatically extends
   average AI score.
4. **Two algorithm classes compared.** BFS-AI demonstrates *informed
   shortest-path search*; Hamilton-AI demonstrates a *graph-construction*
   approach (build a structure that makes the problem trivially safe).
   The Hamilton cycle is a classical CS construct — a great viva talking
   point on graph theory.
5. **Mode swap is hot-reloadable.** You can switch between BFS and
   Hamilton mid-game (`H` key) without crashing because `hamilton.py`
   resolves the cycle's traversal direction lazily and falls back to
   BFS when the cycle is briefly blocked.
6. **Modularity.** Each subsystem (input, AI variants, rendering,
   persistence) is isolated, making it easy to extend — e.g. add A*,
   plug in a Hamilton-with-shortcuts hybrid, or add a multiplayer mode.

---

## License

Free to use for academic / personal purposes.
