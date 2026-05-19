import pygame
from settings import *


class Camera:
    def __init__(self, width, height):
        self.offset_x = 0
        self.offset_y = 0
        self.width    = width
        self.height   = height

    # ── Update ──────────────────────────────────────
    def update(self, target):
        """Center camera on target (player)."""
        self.offset_x = target.rect.centerx - self.width  // 2
        self.offset_y = target.rect.centery - self.height // 2

    # ── Helpers ─────────────────────────────────────
    def apply(self, rect):
        """Return a rect shifted by camera offset. Use this for drawing."""
        return pygame.Rect(
            rect.x - self.offset_x,
            rect.y - self.offset_y,
            rect.width,
            rect.height
        )

    def apply_point(self, x, y):
        """Shift a raw world point into screen space."""
        return (x - self.offset_x, y - self.offset_y)

    def world_to_screen(self, world_x, world_y):
        """Alias for apply_point — more readable in renderer."""
        return (world_x - self.offset_x, world_y - self.offset_y)

    def screen_to_world(self, screen_x, screen_y):
        """Convert a screen coordinate back to world space."""
        return (screen_x + self.offset_x, screen_y + self.offset_y)

    def is_visible(self, rect):
        """
        Quick cull check — skip drawing anything fully off screen.
        Adds a 1-tile buffer so nothing pops in at edges.
        """
        margin = TILE_SIZE
        return (
            rect.right  > -margin and
            rect.left   < self.width  + margin and
            rect.bottom > -margin and
            rect.top    < self.height + margin
        )