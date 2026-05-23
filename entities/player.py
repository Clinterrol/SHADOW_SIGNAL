import pygame
from settings import *


class Player:
    def __init__(self, game, tile_x, tile_y):
        self.game   = game
        self.rect   = pygame.Rect(
            tile_x * TILE_SIZE,
            tile_y * TILE_SIZE,
            TILE_SIZE - 4,
            TILE_SIZE - 4
        )
        self.health       = PLAYER_MAX_HEALTH
        self.facing       = "right"
        self.is_crouching = False
        self.is_sprinting = False
        self.is_moving    = False
        self.vel_x        = 0.0
        self.vel_y        = 0.0
        self.sound_radius = SOUND_RADIUS_WALK

    def update(self, dt, tilemap):
        self._handle_input()
        self._move(dt, tilemap)
        self._update_sound_radius()

    def _handle_input(self):
        keys = pygame.key.get_pressed()
        self.vel_x = 0.0
        self.vel_y = 0.0

        self.is_crouching = keys[pygame.K_LCTRL] or keys[pygame.K_RCTRL]
        self.is_sprinting = (
            (keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT])
            and not self.is_crouching
        )

        if self.is_crouching:
            speed = PLAYER_CROUCH_SPEED
        elif self.is_sprinting:
            speed = PLAYER_SPRINT_SPEED
        else:
            speed = PLAYER_SPEED

        if keys[pygame.K_w] or keys[pygame.K_UP]:
            self.vel_y  = -speed
            self.facing = "up"
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            self.vel_y  = speed
            self.facing = "down"
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            self.vel_x  = -speed
            self.facing = "left"
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            self.vel_x  = speed
            self.facing = "right"

        if self.vel_x != 0 and self.vel_y != 0:
            self.vel_x *= 0.7071
            self.vel_y *= 0.7071

        self.is_moving = self.vel_x != 0 or self.vel_y != 0

    def _move(self, dt, tilemap):
        self.rect.x += int(self.vel_x * dt)
        self._resolve_collisions(tilemap, "x")
        self.rect.y += int(self.vel_y * dt)
        self._resolve_collisions(tilemap, "y")

        world_w = tilemap.cols * TILE_SIZE
        world_h = tilemap.rows * TILE_SIZE
        self.rect.clamp_ip(pygame.Rect(0, 0, world_w, world_h))

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

    def _update_sound_radius(self):
        if self.is_crouching:
            self.sound_radius = SOUND_RADIUS_CROUCH
        elif self.is_sprinting:
            self.sound_radius = SOUND_RADIUS_SPRINT
        else:
            self.sound_radius = SOUND_RADIUS_WALK

    def take_damage(self, amount):
        self.health = max(0, self.health - amount)

    def heal(self, amount):
        self.health = min(PLAYER_MAX_HEALTH, self.health + amount)