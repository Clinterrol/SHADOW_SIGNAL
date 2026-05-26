import pygame
import math
import random
from settings import *


class Watcher:
    def __init__(self, tile_x, tile_y):
        self.rect = pygame.Rect(
            tile_x * TILE_SIZE,
            tile_y * TILE_SIZE,
            TILE_SIZE - 6,
            TILE_SIZE - 6
        )
        self.alive              = True
        self.speed              = 0
        self.state              = "roam"
        self.vel_x              = 0.0
        self.vel_y              = 0.0
        self._frac_x            = 0.0   # sub-pixel accumulator
        self._frac_y            = 0.0
        self._last_known_x      = None
        self._last_known_y      = None
        self._freeze_timer      = 0.0
        self._roam_timer        = 0.0   # starts at 0 so it picks direction immediately
        self._roam_dx           = 1.0
        self._roam_dy           = 0.0
        self._damage_cooldown   = 0.0
        self._light_exposure    = 0.0
        self._light_kill_thresh = 3.0
        self.color              = (60, 0, 80)
        self._prev_state        = "roam"
        self.sound_manager      = None

    def update(self, dt, player, flashlight, signal_sys, tilemap):
        if not self.alive:
            return

        if self._damage_cooldown > 0:
            self._damage_cooldown = max(0.0, self._damage_cooldown - dt)

        dist     = self._distance_to(player)
        in_light = self._is_in_flashlight(player, flashlight)

        if in_light and flashlight.is_on and flashlight.battery > 0:
            self._light_exposure += dt
            if self._light_exposure >= self._light_kill_thresh:
                self.alive = False
                return
        else:
            self._light_exposure = max(0.0, self._light_exposure - dt * 0.5)

        self._update_state(dt, dist, in_light, flashlight, signal_sys)
        self._update_speed(signal_sys)
        self._move(dt, player, tilemap)

    def _update_state(self, dt, dist, in_light, flashlight, signal_sys):
        prev = self.state

        if self._freeze_timer > 0:
            self._freeze_timer -= dt
            self.state = "frozen"
            self._prev_state = prev
            return

        if in_light and flashlight.is_on and flashlight.battery > 0:
            self._freeze_timer = 0.8
            self.state         = "frozen"
        elif dist <= WATCHER_DETECT_RANGE or signal_sys.is_blackout:
            if prev != "chase" and self.sound_manager:
                self.sound_manager.play("watcher_growl", volume=0.8)
            self._last_known_x = None
            self._last_known_y = None
            self.state         = "chase"
        else:
            self.state = "roam"

        self._prev_state = prev

    def _update_speed(self, signal_sys):
        if self.state == "frozen":
            self.speed = 0
        elif self.state == "roam":
            self.speed = WATCHER_SPEED_DARK * 0.55
        elif signal_sys.lights_flickering:
            self.speed = WATCHER_SPEED_FLICKER
        elif signal_sys.is_blackout:
            self.speed = WATCHER_SPEED_DARK * 1.1
        else:
            self.speed = WATCHER_SPEED_DARK * 0.75

    def _move(self, dt, player, tilemap):
        if self.state == "frozen":
            return

        if self.state == "chase":
            self._last_known_x = player.rect.centerx
            self._last_known_y = player.rect.centery
            dx   = self._last_known_x - self.rect.centerx
            dy   = self._last_known_y - self.rect.centery
            dist = max(1, (dx * dx + dy * dy) ** 0.5)
            self.vel_x = (dx / dist) * self.speed
            self.vel_y = (dy / dist) * self.speed

        elif self.state == "roam":
            self._roam_timer -= dt
            if self._roam_timer <= 0:
                self._roam_timer = random.uniform(1.5, 4.0)
                angle            = random.uniform(0, 2 * math.pi)
                self._roam_dx    = math.cos(angle)
                self._roam_dy    = math.sin(angle)
            self.vel_x = self._roam_dx * self.speed
            self.vel_y = self._roam_dy * self.speed

        # Sub-pixel accumulation so slow speeds are never lost to int() truncation
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