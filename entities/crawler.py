import pygame
import math
import random
from settings import *


class Crawler:
    def __init__(self, tile_x, tile_y):
        self.rect = pygame.Rect(
            tile_x * TILE_SIZE + 4,
            tile_y * TILE_SIZE + 4,
            TILE_SIZE - 10,
            TILE_SIZE - 10
        )
        self.alive         = True
        self.speed         = 0
        self.state         = "hidden"   # hidden, crawling, chase, attack
        self.vel_x         = 0.0
        self.vel_y         = 0.0
        self._last_known_x = None
        self._last_known_y = None
        self._hide_timer   = random.uniform(5.0, 15.0)
        self._attack_timer = 0.0
        self._roam_timer   = 0.0
        self._roam_dx      = 0.0
        self._roam_dy      = 0.0
        self.color         = (80, 40, 0)

    def update(self, dt, player, flashlight, signal_sys, tilemap):
        if not self.alive:
            return

        dist = self._distance_to(player)
        self._update_state(dt, dist, signal_sys)
        self._update_speed(signal_sys)
        self._move(dt, player, tilemap)

    def _update_state(self, dt, dist, signal_sys):
        if self.state == "hidden":
            self._hide_timer -= dt
            if self._hide_timer <= 0:
                self.state       = "crawling"
                self._roam_timer = 0.0

        elif self.state == "crawling":
            if dist <= TILE_SIZE * 6:
                self.state = "chase"
            # Re-hide randomly
            if random.random() < 0.001:
                self.state       = "hidden"
                self._hide_timer = random.uniform(3.0, 10.0)

        elif self.state == "chase":
            if dist > TILE_SIZE * 10:
                self.state = "crawling"
            self._last_known_x = None
            self._last_known_y = None

        elif self.state == "attack":
            self._attack_timer -= dt
            if self._attack_timer <= 0:
                self.state = "chase"

    def _update_speed(self, signal_sys):
        if self.state == "hidden":
            self.speed = 0
        elif self.state == "crawling":
            self.speed = PLAYER_CROUCH_SPEED * 0.8
        elif self.state == "chase":
            if signal_sys.is_blackout:
                self.speed = PLAYER_SPRINT_SPEED * 1.2
            elif signal_sys.is_critical:
                self.speed = PLAYER_SPRINT_SPEED * 0.9
            else:
                self.speed = PLAYER_SPEED * 1.1
        else:
            self.speed = 0

    def _move(self, dt, player, tilemap):
        if self.state in ("hidden", "attack"):
            return

        if self.state == "chase":
            dx   = player.rect.centerx - self.rect.centerx
            dy   = player.rect.centery - self.rect.centery
            dist = max(1, (dx*dx + dy*dy) ** 0.5)
            self.vel_x = (dx / dist) * self.speed
            self.vel_y = (dy / dist) * self.speed

        elif self.state == "crawling":
            self._roam_timer -= dt
            if self._roam_timer <= 0:
                self._roam_timer = random.uniform(1.0, 3.0)
                angle            = random.uniform(0, 2 * math.pi)
                self._roam_dx    = math.cos(angle)
                self._roam_dy    = math.sin(angle)
            self.vel_x = self._roam_dx * self.speed
            self.vel_y = self._roam_dy * self.speed

        self.rect.x += int(self.vel_x * dt)
        self._resolve_collisions(tilemap, "x")
        self.rect.y += int(self.vel_y * dt)
        self._resolve_collisions(tilemap, "y")

    def _resolve_collisions(self, tilemap, axis):
        for wall_rect in tilemap.get_wall_rects_near(self.rect):
            if self.rect.colliderect(wall_rect):
                if axis == "x":
                    if self.vel_x > 0:
                        self.rect.right = wall_rect.left
                    elif self.vel_x < 0:
                        self.rect.left  = wall_rect.right
                    self._roam_dx *= -1
                else:
                    if self.vel_y > 0:
                        self.rect.bottom = wall_rect.top
                    elif self.vel_y < 0:
                        self.rect.top    = wall_rect.bottom
                    self._roam_dy *= -1

    def _distance_to(self, player):
        dx = self.rect.centerx - player.rect.centerx
        dy = self.rect.centery - player.rect.centery
        return (dx*dx + dy*dy) ** 0.5

    def touches_player(self, player):
        return self.rect.colliderect(player.rect)