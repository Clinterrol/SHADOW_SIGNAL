import pygame
from settings import *


class LoreNote:
    def __init__(self, note_data, tile_x, tile_y):
        self.note_id  = note_data.get("id", "unknown")
        self.title    = note_data.get("title", "Unknown")
        self.content  = note_data.get("content", "")
        self.tile_x   = tile_x
        self.tile_y   = tile_y
        self.rect     = pygame.Rect(
            tile_x * TILE_SIZE + 6,
            tile_y * TILE_SIZE + 6,
            TILE_SIZE - 12,
            TILE_SIZE - 12
        )
        self.collected = False
        self._bob_timer = 0.0

    def update(self, dt):
        self._bob_timer += dt

    @property
    def color(self):
        return (180, 160, 0)