
import pygame
import math
import random
from settings import *


class Renderer:
    def __init__(self, screen):
        self.screen        = screen
        self._dark_overlay = pygame.Surface(
            (SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA
        )

    def draw_map(self, tilemap, camera):
        for row_idx, row in enumerate(tilemap.grid):
            for col_idx, tile in enumerate(row):
                world_rect = pygame.Rect(
                    col_idx * TILE_SIZE,
                    row_idx * TILE_SIZE,
                    TILE_SIZE, TILE_SIZE
                )
                if not camera.is_visible(world_rect):
                    continue
                screen_rect = camera.apply(world_rect)
                if tile == 1:
                    self._draw_wall(screen_rect)
                elif tile == 0:
                    self._draw_floor(screen_rect)
                elif tile == 2:
                    self._draw_door(screen_rect)
                elif tile == 3:
                    self._draw_floor(screen_rect)

    def _draw_floor(self, rect):
        pygame.draw.rect(self.screen, (18, 18, 18), rect)
        pygame.draw.rect(self.screen, (28, 28, 28), rect, 1)

    def _draw_wall(self, rect):
        pygame.draw.rect(self.screen, (8, 8, 8), rect)
        inner = rect.inflate(-4, -4)
        pygame.draw.rect(self.screen, (14, 14, 14), inner)
        pygame.draw.rect(self.screen, (5, 5, 5), rect, 1)

    def _draw_door(self, rect):
        pygame.draw.rect(self.screen, (35, 20, 10), rect)
        pygame.draw.rect(self.screen, (80, 40, 10), rect, 2)
        pygame.draw.circle(self.screen, (120, 60, 10),
                           (rect.centerx + 6, rect.centery), 3)

    def draw_towers(self, towers, camera):
        for tower in towers:
            if not camera.is_visible(tower.rect):
                continue
            screen_rect = camera.apply(tower.rect)
            if tower.active:
                pygame.draw.rect(self.screen, (10, 40, 10), screen_rect)
                pygame.draw.rect(self.screen, (0, 180, 60), screen_rect, 2)
                pygame.draw.circle(
                    self.screen, (0, 220, 80), screen_rect.center, 6
                )
            else:
                pygame.draw.rect(self.screen, (10, 25, 10), screen_rect)
                pygame.draw.rect(self.screen, (0, 80, 30), screen_rect, 2)
                if tower.pulse_on:
                    pygame.draw.circle(
                        self.screen, (0, 100, 40), screen_rect.center, 4
                    )

    def draw_lore_notes(self, notes, camera):
        font = pygame.font.SysFont("consolas", 10, bold=True)
        for note in notes:
            if note.collected:
                continue
            if not camera.is_visible(note.rect):
                continue
            screen_rect = camera.apply(note.rect)
            pygame.draw.rect(self.screen, (40, 35, 5), screen_rect)
            pygame.draw.rect(self.screen, (180, 160, 0), screen_rect, 1)
            lbl = font.render("!", True, (200, 180, 0))
            self.screen.blit(lbl, (
                screen_rect.centerx - lbl.get_width()  // 2,
                screen_rect.centery - lbl.get_height() // 2
            ))

    def draw_items(self, items, camera):
        font = pygame.font.SysFont("consolas", 11, bold=True)
        for item in items:
            if not item.active:
                continue
            if not camera.is_visible(item.rect):
                continue
            screen_rect = camera.apply(item.rect)
            pygame.draw.rect(self.screen, (30, 30, 30), screen_rect)
            pygame.draw.rect(self.screen, item.color, screen_rect, 2)
            lbl = font.render(item.label, True, item.color)
            self.screen.blit(lbl, (
                screen_rect.centerx - lbl.get_width()  // 2,
                screen_rect.centery - lbl.get_height() // 2
            ))

    def draw_entities(self, entities, camera):
        for entity in entities:
            if not entity.alive:
                continue
            if not camera.is_visible(entity.rect):
                continue
            screen_rect = camera.apply(entity.rect)
            cx = screen_rect.centerx
            cy = screen_rect.centery

            entity_type = type(entity).__name__

            if entity_type == "Watcher":
                # Large dark purple circle
                pygame.draw.circle(self.screen, (60, 0, 80), (cx, cy), 11)
                pygame.draw.circle(self.screen, (120, 0, 160), (cx, cy), 11, 2)
                # Red eyes
                pygame.draw.circle(self.screen, (220, 0, 0), (cx-4, cy-2), 2)
                pygame.draw.circle(self.screen, (220, 0, 0), (cx+4, cy-2), 2)
                if entity.state == "frozen":
                    pygame.draw.circle(
                        self.screen, (0, 100, 220), (cx, cy), 13, 2
                    )
                elif entity.state == "chase":
                    pygame.draw.circle(
                        self.screen, (180, 0, 0), (cx, cy), 13, 1
                    )

            elif entity_type == "Crawler":
                # Small brown/orange — low to ground
                pygame.draw.ellipse(
                    self.screen, (80, 40, 0),
                    pygame.Rect(cx-8, cy-5, 16, 10)
                )
                pygame.draw.ellipse(
                    self.screen, (140, 70, 0),
                    pygame.Rect(cx-8, cy-5, 16, 10), 1
                )
                # Tiny eyes
                pygame.draw.circle(
                    self.screen, (255, 100, 0), (cx-3, cy-1), 1
                )
                pygame.draw.circle(
                    self.screen, (255, 100, 0), (cx+3, cy-1), 1
                )
                if entity.state == "hidden":
                    # Dotted outline — barely visible
                    pygame.draw.ellipse(
                        self.screen, (40, 20, 0),
                        pygame.Rect(cx-8, cy-5, 16, 10), 1
                    )

            elif entity_type == "Mimic":
                # Blue-grey humanoid shape
                pygame.draw.circle(self.screen, (40, 40, 80), (cx, cy), 10)
                pygame.draw.circle(self.screen, (80, 80, 160), (cx, cy), 10, 2)
                # White eyes — unsettling
                pygame.draw.circle(
                    self.screen, (220, 220, 255), (cx-3, cy-2), 2
                )
                pygame.draw.circle(
                    self.screen, (220, 220, 255), (cx+3, cy-2), 2
                )
                if entity.state == "lure":
                    # Glowing outline when luring
                    pygame.draw.circle(
                        self.screen, (100, 100, 200), (cx, cy), 13, 1
                    )
                elif entity.state in ("chase", "strike"):
                    pygame.draw.circle(
                        self.screen, (180, 0, 0), (cx, cy), 13, 1
                    )

    def draw_player(self, player, camera):
        screen_rect = camera.apply(player.rect)
        cx = screen_rect.centerx
        cy = screen_rect.centery

        pygame.draw.circle(self.screen, (50, 50, 55), (cx, cy), 10)
        pygame.draw.circle(self.screen, (90, 90, 100), (cx, cy), 10, 2)

        offset = 7
        facing_offsets = {
            "up":    (0,       -offset),
            "down":  (0,        offset),
            "left":  (-offset,  0),
            "right": ( offset,  0),
        }
        dx, dy = facing_offsets.get(player.facing, (offset, 0))
        pygame.draw.circle(
            self.screen, (200, 200, 220), (cx + dx, cy + dy), 3
        )

        if player.is_crouching:
            pygame.draw.circle(self.screen, (180, 140, 0), (cx, cy), 12, 1)
        elif player.is_sprinting:
            pygame.draw.circle(self.screen, (180, 180, 180), (cx, cy), 13, 1)

    def draw_flashlight(self, player, camera, flashlight):
        px, py = camera.apply_point(
            player.rect.centerx, player.rect.centery
        )

        if flashlight.is_on and flashlight.battery > 0 and not flashlight.overheated:
            darkness = 200
        else:
            darkness = 235

        self._dark_overlay.fill((0, 0, 0, darkness))

        ambient_radius = 80 if (
            flashlight.is_on and flashlight.battery > 0
            and not flashlight.overheated
        ) else 45
        self._punch_circle(px, py, ambient_radius)

        if flashlight.is_on and flashlight.battery > 0 and not flashlight.overheated:
            self._cut_flashlight_cone(px, py, player.facing, flashlight)

        self.screen.blit(self._dark_overlay, (0, 0))

        if flashlight.is_flickering:
            self._draw_flicker_edge()

    def _punch_circle(self, px, py, radius):
        for r in range(radius, 0, -5):
            progress = 1 - (r / radius)
            alpha    = int(220 * progress)
            pygame.draw.circle(
                self._dark_overlay, (0, 0, 0, alpha), (px, py), r
            )
        pygame.draw.circle(
            self._dark_overlay, (0, 0, 0, 0), (px, py), radius // 4
        )

    def _cut_flashlight_cone(self, px, py, facing, flashlight):
        angle_map    = {"right": 0, "down": 90, "left": 180, "up": 270}
        center_angle = math.radians(angle_map.get(facing, 0))
        spread       = math.radians(70)
        radius       = int(FLASHLIGHT_RADIUS * 1.3 * max(
            0.4, flashlight.battery / FLASHLIGHT_MAX_BATTERY
        ))

        steps  = 28
        points = [(px, py)]
        for i in range(steps + 1):
            a = center_angle - spread + (2 * spread * i / steps)
            points.append((
                px + math.cos(a) * radius,
                py + math.sin(a) * radius
            ))
        pygame.draw.polygon(self._dark_overlay, (0, 0, 0, 0), points)

        for r, alpha in [(60, 30), (40, 60), (20, 0)]:
            pygame.draw.circle(
                self._dark_overlay, (0, 0, 0, alpha), (px, py), r
            )

    def _draw_flicker_edge(self):
        flicker_surf = pygame.Surface(
            (SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA
        )
        alpha = random.randint(10, 50)
        pygame.draw.rect(
            flicker_surf, (120, 0, 0, alpha),
            pygame.Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT), 30
        )
        self.screen.blit(flicker_surf, (0, 0))