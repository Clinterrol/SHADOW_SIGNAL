import pygame
from settings import *


class Item:
    def __init__(self, kind, tile_x, tile_y):
        self.kind   = kind    # "battery" | "medkit" | "keycard"
        self.active = True
        self.rect   = pygame.Rect(
            tile_x * TILE_SIZE + 8,
            tile_y * TILE_SIZE + 8,
            TILE_SIZE - 16,
            TILE_SIZE - 16
        )
        self._bob_timer = 0.0
        self._bob_y     = 0

    def update(self, dt):
        import math
        self._bob_timer += dt
        self._bob_y = int(math.sin(self._bob_timer * 3) * 2)

    @property
    def color(self):
        return {
            "battery": AMBER,
            "medkit":  (0, 180, 60),
            "keycard": (0, 100, 200),
        }.get(self.kind, WHITE)

    @property
    def label(self):
        return {
            "battery": "B",
            "medkit":  "+",
            "keycard": "K",
        }.get(self.kind, "?")
    