import pygame
import math
import random
from settings import *


class Mimic:
    def __init__(self, tile_x, tile_y):
        self.rect = pygame.Rect(
            tile_x * TILE_SIZE,
            tile_y * TILE_SIZE,
            TILE_SIZE - 4,
            TILE_SIZE - 4
        )
        self.alive          = True
        self.speed          = 0
        self.state          = "idle"   # idle, lure, chase, strike
        self.vel_x          = 0.0
        self.vel_y          = 0.0
        self._lure_timer    = 0.0
        self._lure_interval = random.uniform(10.0, 25.0)
        self._lure_active   = False
        self._lure_duration = 0.0
        self._strike_timer  = 0.0
        self.color          = (40, 40, 80)

        # Lure messages — fake human voices
        self._lure_messages = [
            "Hello? Is someone there?",
            "Help me... please...",
            "I found a way out!",
            "The signal tower is this way!",
            "Don't worry, I'm friendly...",
        ]
        self.current_lure = ""

    def update(self, dt, player, signal_sys, tilemap):
        if not self.alive:
            return

        dist = self._distance_to(player)
        self._update_state(dt, dist, signal_sys)
        self._update_speed(signal_sys)
        self._move(dt, player, tilemap)

    def _update_state(self, dt, dist, signal_sys):
        self._lure_timer += dt

        if self.state == "idle":
            if self._lure_timer >= self._lure_interval:
                self._lure_timer    = 0.0
                self._lure_interval = random.uniform(10.0, 25.0)
                self._start_lure()

        elif self.state == "lure":
            self._lure_duration -= dt
            if self._lure_duration <= 0:
                self._lure_active = False
                self.current_lure = ""
                if dist < TILE_SIZE * 8:
                    self.state = "chase"
                else:
                    self.state = "idle"

        elif self.state == "chase":
            if dist < TILE_SIZE * 2:
                self.state         = "strike"
                self._strike_timer = 0.5
            elif dist > TILE_SIZE * 12:
                self.state = "idle"

        elif self.state == "strike":
            self._strike_timer -= dt
            if self._strike_timer <= 0:
                self.state = "chase"

    def _start_lure(self):
        self.state          = "lure"
        self._lure_active   = True
        self._lure_duration = random.uniform(4.0, 8.0)
        self.current_lure   = random.choice(self._lure_messages)

    def _update_speed(self, signal_sys):
        if self.state in ("idle", "lure"):
            self.speed = PLAYER_SPEED * 0.3
        elif self.state == "chase":
            if signal_sys.is_blackout:
                self.speed = PLAYER_SPRINT_SPEED * 1.3
            else:
                self.speed = PLAYER_SPRINT_SPEED * 0.85
        elif self.state == "strike":
            self.speed = PLAYER_SPRINT_SPEED * 1.5

    def _move(self, dt, player, tilemap):
        if self.state == "idle":
            return

        if self.state in ("chase", "strike"):
            dx   = player.rect.centerx - self.rect.centerx
            dy   = player.rect.centery - self.rect.centery
            dist = max(1, (dx*dx + dy*dy) ** 0.5)
            self.vel_x = (dx / dist) * self.speed
            self.vel_y = (dy / dist) * self.speed
        elif self.state == "lure":
            # Move slowly toward player to lure
            dx   = player.rect.centerx - self.rect.centerx
            dy   = player.rect.centery - self.rect.centery
            dist = max(1, (dx*dx + dy*dy) ** 0.5)
            # Only move if far enough
            if dist > TILE_SIZE * 6:
                self.vel_x = (dx / dist) * self.speed
                self.vel_y = (dy / dist) * self.speed
            else:
                self.vel_x = 0
                self.vel_y = 0

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
                else:
                    if self.vel_y > 0:
                        self.rect.bottom = wall_rect.top
                    elif self.vel_y < 0:
                        self.rect.top    = wall_rect.bottom

    def _distance_to(self, player):
        dx = self.rect.centerx - player.rect.centerx
        dy = self.rect.centery - player.rect.centery
        return (dx*dx + dy*dy) ** 0.5

    def touches_player(self, player):
        return self.rect.colliderect(player.rect)