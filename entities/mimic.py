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
        self.alive              = True
        self.speed              = 0
        self.state              = "idle"
        self.vel_x              = 0.0
        self.vel_y              = 0.0
        self._frac_x            = 0.0   # sub-pixel accumulator
        self._frac_y            = 0.0
        self._lure_timer        = 0.0
        self._lure_interval     = random.uniform(10.0, 25.0)
        self._lure_active       = False
        self._lure_duration     = 0.0
        self._strike_timer      = 0.0
        self._damage_cooldown   = 0.0
        self._light_exposure    = 0.0
        self._light_kill_thresh = 4.0
        self.color              = (40, 40, 80)

        # Fade-out when killed by flashlight
        self.dying        = False
        self._fade_alpha  = 255
        self._fade_speed  = 180   # alpha per second

        self._lure_messages = [
            "Hello? Is someone there?",
            "Help me... please...",
            "I found a way out!",
            "The signal tower is this way!",
            "Don't worry, I'm friendly...",
        ]
        self.current_lure  = ""
        self.sound_manager = None

    def update(self, dt, player, signal_sys, tilemap):
        if not self.alive:
            return
        if self._damage_cooldown > 0:
            self._damage_cooldown = max(0.0, self._damage_cooldown - dt)
        dist = self._distance_to(player)
        self._update_state(dt, dist, signal_sys)
        self._update_speed(signal_sys)
        self._move(dt, player, tilemap)

    def update_with_light(self, dt, player, signal_sys, tilemap, flashlight):
        # While fading out — frozen in place, no damage
        if self.dying:
            self._fade_alpha -= self._fade_speed * dt
            if self._fade_alpha <= 0:
                self._fade_alpha = 0
                self.alive       = False
                self.dying       = False
            return

        if not self.alive:
            return

        if self._damage_cooldown > 0:
            self._damage_cooldown = max(0.0, self._damage_cooldown - dt)

        in_light = self._is_in_flashlight(player, flashlight)
        if in_light and flashlight.is_on and flashlight.battery > 0:
            self._light_exposure += dt
            if self._light_exposure >= self._light_kill_thresh:
                self.dying        = True
                self.state        = "idle"
                self._lure_active = False
                self.current_lure = ""
                return
        else:
            self._light_exposure = max(0.0, self._light_exposure - dt * 0.5)

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
        if self.sound_manager:
            sound_map = getattr(self.sound_manager, "mimic_sound_map", {})
            key = sound_map.get(self.current_lure)
            if key:
                self.sound_manager.play(key, volume=0.85)

    def _update_speed(self, signal_sys):
        if self.state in ("idle", "lure"):
            self.speed = PLAYER_SPEED * 0.3
        elif self.state == "chase":
            if signal_sys.is_blackout:
                self.speed = PLAYER_SPRINT_SPEED * 0.9
            else:
                self.speed = PLAYER_SPEED * 1.0
        elif self.state == "strike":
            self.speed = PLAYER_SPRINT_SPEED * 1.1

    def _move(self, dt, player, tilemap):
        if self.state == "idle":
            return

        if self.state in ("chase", "strike"):
            dx   = player.rect.centerx - self.rect.centerx
            dy   = player.rect.centery - self.rect.centery
            dist = max(1, (dx * dx + dy * dy) ** 0.5)
            self.vel_x = (dx / dist) * self.speed
            self.vel_y = (dy / dist) * self.speed

        elif self.state == "lure":
            dx   = player.rect.centerx - self.rect.centerx
            dy   = player.rect.centery - self.rect.centery
            dist = max(1, (dx * dx + dy * dy) ** 0.5)
            if dist > TILE_SIZE * 6:
                self.vel_x = (dx / dist) * self.speed
                self.vel_y = (dy / dist) * self.speed
            else:
                self.vel_x = 0.0
                self.vel_y = 0.0

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
                else:
                    if self.vel_y > 0:
                        self.rect.bottom = wall_rect.top
                    elif self.vel_y < 0:
                        self.rect.top    = wall_rect.bottom

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
        return self._damage_cooldown <= 0 and not self.dying

    def register_hit(self):
        self._damage_cooldown = 1.0

    def touches_player(self, player):
        return self.rect.colliderect(player.rect) and not self.dying