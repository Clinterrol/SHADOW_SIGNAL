import pygame
from settings import *


class SignalTower:
    def __init__(self, tile_x, tile_y):
        self.tile_x    = tile_x
        self.tile_y    = tile_y
        self.rect      = pygame.Rect(
            tile_x * TILE_SIZE,
            tile_y * TILE_SIZE,
            TILE_SIZE, TILE_SIZE
        )
        self.active        = False
        self.interact_range = TILE_SIZE * 1.5
        self._pulse_timer  = 0.0
        self._pulse_on     = True

    def update(self, dt):
        self._pulse_timer += dt
        if self._pulse_timer >= 0.6:
            self._pulse_timer = 0.0
            self._pulse_on    = not self._pulse_on

    def is_near(self, player_rect):
        dx = self.rect.centerx - player_rect.centerx
        dy = self.rect.centery - player_rect.centery
        return (dx*dx + dy*dy) ** 0.5 <= self.interact_range

    def activate(self):
        self.active = True

    @property
    def pulse_on(self):
        return self._pulse_on