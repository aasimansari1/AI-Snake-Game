"""
hamilton.py
-----------
Hamilton-cycle AI for Snake.

A Hamilton cycle visits every cell of the grid exactly once and returns to
the starting cell. If the snake follows such a cycle, it can never collide
with itself or the wall — it will eventually fill the entire board and win.

Construction (requires GRID_HEIGHT to be even):
    1. Visit row 0 left-to-right:   (0,0) -> (W-1, 0)
    2. Snake through rows 1..H-1 across columns 1..W-1, alternating
       direction each row.
    3. Return up column 0:          (0, H-1) -> (0, 1)
    The cycle then closes by wrapping from (0, 1) back to (0, 0).

For our default grid (30 x 22) this builds a 660-cell cycle. The snake
follows the cycle in whichever direction (forward or backward) matches
its current heading; that lets the AI be enabled mid-game without
forcing a 180-degree reversal.

If the cycle's next cell is unreachable (e.g. the snake's body already
occupies it because we switched in from BFS-AI), the function falls back
to the supplied `fallback_choose` (typically the BFS-AI controller) so
that switching modes is always safe.
"""

from settings import GRID_WIDTH, GRID_HEIGHT


def build_cycle(W=GRID_WIDTH, H=GRID_HEIGHT):
    """Return an ordered list of (x, y) cells forming a Hamilton cycle."""
    if H % 2 != 0:
        raise ValueError(
            "Hamilton cycle construction requires an even GRID_HEIGHT "
            f"(got {H}). Adjust settings.py."
        )

    cycle = []

    # 1. Row 0, left-to-right
    for x in range(W):
        cycle.append((x, 0))

    # 2. Snake through rows 1..H-1, columns 1..W-1
    going_left = True   # row 1 starts on the right (W-1) and goes left
    for y in range(1, H):
        if going_left:
            for x in range(W - 1, 0, -1):
                cycle.append((x, y))
        else:
            for x in range(1, W):
                cycle.append((x, y))
        going_left = not going_left

    # 3. Return path up column 0 (rows H-1 down to 1)
    for y in range(H - 1, 0, -1):
        cycle.append((0, y))

    return cycle


def build_index(cycle):
    """Reverse map: cell -> position in the cycle (O(1) lookup)."""
    return {cell: i for i, cell in enumerate(cycle)}


def choose_direction_hamilton(snake, food, cycle, idx, fallback_choose):
    """
    Decide the snake's next direction by following the Hamilton cycle.

    Picks forward or backward traversal so the snake doesn't have to
    180-reverse. Falls back to `fallback_choose(snake, food)` (e.g. the
    BFS-AI) if the cycle's next cell is blocked by the snake's body —
    this can happen briefly after switching from BFS-AI mid-game.
    """
    head = snake.head
    head_i = idx[head]
    L = len(cycle)
    cur_dir = snake.direction
    reverse_of_cur = (-cur_dir[0], -cur_dir[1])

    forward_cell = cycle[(head_i + 1) % L]
    backward_cell = cycle[(head_i - 1) % L]

    forward_dir = (forward_cell[0] - head[0], forward_cell[1] - head[1])
    backward_dir = (backward_cell[0] - head[0], backward_cell[1] - head[1])

    # Body cells the snake cannot move into. Tail tip vacates next tick
    # unless the snake is growing.
    body = set(snake.body)
    if snake.grow_pending == 0 and len(snake.body) > 1:
        body.discard(snake.body[-1])

    # Prefer the cycle direction that doesn't reverse current heading and
    # doesn't immediately collide with the body.
    candidates = []
    if forward_dir != reverse_of_cur:
        candidates.append((forward_cell, forward_dir))
    if backward_dir != reverse_of_cur:
        candidates.append((backward_cell, backward_dir))

    for cell, d in candidates:
        if cell not in body:
            return d

    # Cycle traversal blocked (rare; only after mode switching) -> fallback
    return fallback_choose(snake, food)
