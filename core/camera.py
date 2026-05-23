import pygame
from settings import *


class Camera:
    def __init__(self, width, height):
        self.offset_x = 0
        self.offset_y = 0
        self.width    = width
        self.height   = height

    def update(self, target):
        self.offset_x = target.rect.centerx - self.width  // 2
        self.offset_y = target.rect.centery - self.height // 2

    def apply(self, rect):
        return pygame.Rect(
            rect.x - self.offset_x,
            rect.y - self.offset_y,
            rect.width,
            rect.height
        )

    def apply_point(self, x, y):
        return (x - self.offset_x, y - self.offset_y)

    def is_visible(self, rect):
        margin = TILE_SIZE
        return (
            rect.right  > -margin and
            rect.left   < self.width  + margin and
            rect.bottom > -margin and
            rect.top    < self.height + margin
        )