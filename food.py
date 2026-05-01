"""
food.py
-------
Food entity. Spawns at a random empty cell that is not occupied by the snake.
"""

import random
from settings import GRID_WIDTH, GRID_HEIGHT


class Food:
    def __init__(self, snake_body):
        self.position = (0, 0)
        self.respawn(snake_body)

    def respawn(self, snake_body):
        """
        Pick a random cell that is not part of the snake's body.
        We build the set of free cells and choose uniformly so that the snake
        cannot consume the entire board without food becoming unspawnable.
        """
        occupied = set(snake_body)
        free_cells = [
            (x, y)
            for x in range(GRID_WIDTH)
            for y in range(GRID_HEIGHT)
            if (x, y) not in occupied
        ]
        if not free_cells:
            self.position = None         # Board is full -> player won
            return
        self.position = random.choice(free_cells)
