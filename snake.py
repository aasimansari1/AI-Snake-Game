"""
snake.py
--------
Snake entity: position, movement, growth, and self-collision check.

The snake's body is stored as a list of (x, y) grid coordinates where index 0
is the head. Movement is performed one cell per game tick along `direction`.
"""

from settings import GRID_WIDTH, GRID_HEIGHT

# Direction vectors as (dx, dy) on the grid
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)


class Snake:
    def __init__(self):
        # Start in the middle of the grid, length 3, moving right
        cx, cy = GRID_WIDTH // 2, GRID_HEIGHT // 2
        self.body = [(cx, cy), (cx - 1, cy), (cx - 2, cy)]
        self.direction = RIGHT
        self.pending_direction = RIGHT   # Buffered input for next tick
        self.grow_pending = 0            # Cells still to add (grow without trim)

    # ---------- Properties ----------
    @property
    def head(self):
        return self.body[0]

    def __len__(self):
        return len(self.body)

    # ---------- Input ----------
    def set_direction(self, new_dir):
        """
        Queue a direction change. Reject 180-degree reversals which would
        cause the snake to immediately collide with its own neck.
        """
        dx, dy = new_dir
        cdx, cdy = self.direction
        if (dx, dy) == (-cdx, -cdy):
            return
        self.pending_direction = new_dir

    # ---------- Movement ----------
    def move(self):
        """Advance one cell in the current direction. Returns the new head."""
        self.direction = self.pending_direction
        hx, hy = self.head
        dx, dy = self.direction
        new_head = (hx + dx, hy + dy)
        self.body.insert(0, new_head)

        if self.grow_pending > 0:
            self.grow_pending -= 1            # Skip trimming -> snake grows
        else:
            self.body.pop()
        return new_head

    def grow(self, n=1):
        """Add `n` cells on the next moves (used when food is eaten)."""
        self.grow_pending += n

    # ---------- Collision ----------
    def hits_wall(self, pos=None):
        x, y = pos if pos else self.head
        return x < 0 or x >= GRID_WIDTH or y < 0 or y >= GRID_HEIGHT

    def hits_self(self, pos=None):
        """
        Check head-vs-body collision.
        When `pos` is None we check the current head against the rest of the
        body (skip index 0 which is the head itself).
        """
        if pos is None:
            return self.head in self.body[1:]
        return pos in self.body
