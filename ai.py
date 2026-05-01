"""
ai.py
-----
AI controller for the snake.

Strategy
--------
1. Run BFS from the snake's head to the food, treating the snake's body
   (except the tail tip, which will move out of the way) as obstacles. BFS
   on an unweighted grid yields the shortest path in O(V + E) time.
2. If a path exists, take the first step toward the food.
3. If no path exists, fall back to a *survival* move: pick the neighbouring
   cell that maximises reachable free space (flood fill area). This keeps
   the snake alive until a path opens up.
4. If even survival fails, return any non-immediately-fatal move.
"""

from collections import deque
from snake import UP, DOWN, LEFT, RIGHT
from settings import GRID_WIDTH, GRID_HEIGHT

DIRECTIONS = [UP, DOWN, LEFT, RIGHT]


def _in_bounds(pos):
    x, y = pos
    return 0 <= x < GRID_WIDTH and 0 <= y < GRID_HEIGHT


def _neighbors(pos):
    x, y = pos
    for dx, dy in DIRECTIONS:
        np = (x + dx, y + dy)
        if _in_bounds(np):
            yield np, (dx, dy)


def bfs_path(start, goal, blocked):
    """
    Standard BFS on the grid.
    `blocked` is a set of cells the snake cannot enter.
    Returns a list of cells from `start` (exclusive) to `goal` (inclusive),
    or None if `goal` is unreachable.
    """
    if start == goal:
        return []
    queue = deque([start])
    came_from = {start: None}
    while queue:
        current = queue.popleft()
        for np, _ in _neighbors(current):
            if np in came_from or np in blocked:
                continue
            came_from[np] = current
            if np == goal:
                # Reconstruct path by walking back through came_from
                path = [np]
                while came_from[path[-1]] != start:
                    path.append(came_from[path[-1]])
                path.reverse()
                return path
            queue.append(np)
    return None


def _flood_fill_area(start, blocked):
    """Count cells reachable from `start` without entering `blocked`."""
    if start in blocked or not _in_bounds(start):
        return 0
    seen = {start}
    queue = deque([start])
    while queue:
        cur = queue.popleft()
        for np, _ in _neighbors(cur):
            if np in seen or np in blocked:
                continue
            seen.add(np)
            queue.append(np)
    return len(seen)


def _direction_from(a, b):
    """Direction tuple needed to step from `a` to `b`."""
    return (b[0] - a[0], b[1] - a[1])


def choose_direction(snake, food):
    """
    Decide the next direction for the AI snake.

    The snake's tail will move out of its current cell on the next tick
    (unless the snake is about to eat), so we can treat the tail tip as
    walkable. This is a small but important optimization that lets the AI
    follow itself in tight spaces.
    """
    head = snake.head
    body = set(snake.body)

    # Tail will vacate next tick (unless the snake is growing this tick).
    will_grow = snake.grow_pending > 0
    if not will_grow and len(snake.body) > 1:
        body.discard(snake.body[-1])

    # ---- 1. Try shortest path to food via BFS ----
    if food.position is not None:
        path = bfs_path(head, food.position, body)
        if path:
            next_cell = path[0]
            return _direction_from(head, next_cell)

    # ---- 2. Survival mode: pick the safest neighbouring cell ----
    best_dir = None
    best_area = -1
    cur_dir = snake.direction
    reverse = (-cur_dir[0], -cur_dir[1])

    for d in DIRECTIONS:
        if d == reverse:                    # Cannot reverse into own neck
            continue
        np = (head[0] + d[0], head[1] + d[1])
        if not _in_bounds(np) or np in body:
            continue
        # Estimate "open space" reachable after moving here
        area = _flood_fill_area(np, body)
        if area > best_area:
            best_area = area
            best_dir = d

    if best_dir is not None:
        return best_dir

    # ---- 3. No good move; keep direction and let collision happen ----
    return snake.direction
