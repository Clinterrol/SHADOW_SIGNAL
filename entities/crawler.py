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
        self.alive              = True
        self.speed              = 0
        self.state              = "hidden"
        self.vel_x              = 0.0
        self.vel_y              = 0.0
        self._frac_x            = 0.0   # sub-pixel accumulator
        self._frac_y            = 0.0
        self._last_known_x      = None
        self._last_known_y      = None
        self._hide_timer        = random.uniform(5.0, 15.0)
        self._attack_timer      = 0.0
        self._roam_timer        = 0.0
        self._roam_dx           = 1.0
        self._roam_dy           = 0.0
        self._damage_cooldown   = 0.0
        self._light_exposure    = 0.0
        self._light_kill_thresh = 2.5
        self.color              = (80, 40, 0)
        self._prev_state        = "hidden"
        self.sound_manager      = None

    def update(self, dt, player, flashlight, signal_sys, tilemap):
        if not self.alive:
            return

        if self._damage_cooldown > 0:
            self._damage_cooldown = max(0.0, self._damage_cooldown - dt)

        in_light = self._is_in_flashlight(player, flashlight)
        if in_light and flashlight.is_on and flashlight.battery > 0:
            self._light_exposure += dt
            if self._light_exposure >= self._light_kill_thresh:
                self.alive = False
                return
        else:
            self._light_exposure = max(0.0, self._light_exposure - dt * 0.5)

        dist = self._distance_to(player)
        self._update_state(dt, dist, signal_sys)
        self._update_speed(signal_sys)
        self._move(dt, player, tilemap)

    def _update_state(self, dt, dist, signal_sys):
        prev = self.state

        if self.state == "hidden":
            self._hide_timer -= dt
            if self._hide_timer <= 0:
                self.state       = "crawling"
                self._roam_timer = 0.0
                if self.sound_manager:
                    self.sound_manager.play("crawler_skitter", volume=0.7)

        elif self.state == "crawling":
            if dist <= TILE_SIZE * 6:
                self.state = "chase"
                if self.sound_manager:
                    self.sound_manager.play("crawler_skitter", volume=1.0)
            elif random.random() < 0.001:
                self.state       = "hidden"
                self._hide_timer = random.uniform(3.0, 10.0)

        elif self.state == "chase":
            if dist > TILE_SIZE * 10:
                self.state = "crawling"

        elif self.state == "attack":
            self._attack_timer -= dt
            if self._attack_timer <= 0:
                self.state = "chase"

        self._prev_state = prev

    def _update_speed(self, signal_sys):
        if self.state == "hidden":
            self.speed = 0
        elif self.state == "crawling":
            self.speed = PLAYER_CROUCH_SPEED * 0.65
        elif self.state == "chase":
            if signal_sys.is_blackout:
                self.speed = PLAYER_SPRINT_SPEED * 0.85
            elif signal_sys.is_critical:
                self.speed = PLAYER_SPEED * 1.0
            else:
                self.speed = PLAYER_SPEED * 0.9
        else:
            self.speed = 0

    def _move(self, dt, player, tilemap):
        if self.state in ("hidden", "attack"):
            return

        if self.state == "chase":
            dx   = player.rect.centerx - self.rect.centerx
            dy   = player.rect.centery - self.rect.centery
            dist = max(1, (dx * dx + dy * dy) ** 0.5)
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

        # Sub-pixel accumulation
        self._frac_x += self.vel_x * dt
        self._frac_y += self.vel_y * dt
        move_x = int(self._frac_x)
        move_y = int(self._frac_y)
        self._frac_x -= move_x
        self._frac_y -= move_y

        self.rect.x += move_x
        self._resolve_collisions(tilemap, "x")
        self.rect.y += move_y
        self._resolve_collisions(tilemap, "y")

    def _resolve_collisions(self, tilemap, axis):
        for wall_rect in tilemap.get_wall_rects_near(self.rect):
            if self.rect.colliderect(wall_rect):
                if axis == "x":
                    if self.vel_x > 0:
                        self.rect.right = wall_rect.left
                    elif self.vel_x < 0:
                        self.rect.left  = wall_rect.right
                    angle = random.uniform(0, 2 * math.pi)
                    self._roam_dx = math.cos(angle)
                    self._roam_dy = math.sin(angle)
                else:
                    if self.vel_y > 0:
                        self.rect.bottom = wall_rect.top
                    elif self.vel_y < 0:
                        self.rect.top    = wall_rect.bottom
                    angle = random.uniform(0, 2 * math.pi)
                    self._roam_dx = math.cos(angle)
                    self._roam_dy = math.sin(angle)

    def _is_in_flashlight(self, player, flashlight):
        if not flashlight.is_on or flashlight.battery <= 0:
            return False
        angle_map    = {"right": 0, "down": 90, "left": 180, "up": 270}
        center_angle = math.radians(angle_map.get(player.facing, 0))
        spread       = math.radians(70)
        dx           = self.rect.centerx - player.rect.centerx
        dy           = self.rect.centery - player.rect.centery
        dist         = max(1, (dx * dx + dy * dy) ** 0.5)
        if dist > FLASHLIGHT_RADIUS * 1.3:
            return False
        angle_to_enemy = math.atan2(dy, dx)
        angle_diff     = abs(angle_to_enemy - center_angle)
        if angle_diff > math.pi:
            angle_diff = 2 * math.pi - angle_diff
        return angle_diff <= spread

    def _distance_to(self, player):
        dx = self.rect.centerx - player.rect.centerx
        dy = self.rect.centery - player.rect.centery
        return (dx * dx + dy * dy) ** 0.5

    def can_damage(self):
        return self._damage_cooldown <= 0

    def register_hit(self):
        self._damage_cooldown = 1.0

    def touches_player(self, player):
        return self.rect.colliderect(player.rect)