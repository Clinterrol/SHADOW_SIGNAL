import pygame
import math
import random
from settings import *


class Renderer:
    def __init__(self, screen):
        self.screen      = screen
        self._dark_overlay  = pygame.Surface(
            (SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA
        )
        self._light_surface = pygame.Surface(
            (SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA
        )

    # ── Map ─────────────────────────────────────────
    def draw_map(self, tilemap, camera):
        for row_idx, row in enumerate(tilemap.grid):
            for col_idx, tile in enumerate(row):
                world_rect = pygame.Rect(
                    col_idx * TILE_SIZE,
                    row_idx * TILE_SIZE,
                    TILE_SIZE,
                    TILE_SIZE
                )

                if not camera.is_visible(world_rect):
                    continue

                screen_rect = camera.apply(world_rect)

                if tile == 1:       # wall
                    self._draw_wall(screen_rect)
                elif tile == 0:     # floor
                    self._draw_floor(screen_rect)
                elif tile == 2:     # door
                    self._draw_door(screen_rect)
                elif tile == 3:     # signal tower
                    self._draw_tower(screen_rect)

    def _draw_floor(self, rect):
        pygame.draw.rect(self.screen, (18, 18, 18), rect)
        # subtle grid lines for industrial look
        pygame.draw.rect(self.screen, (28, 28, 28), rect, 1)

    def _draw_wall(self, rect):
        pygame.draw.rect(self.screen, (8, 8, 8), rect)
        # darker inner shadow
        inner = rect.inflate(-4, -4)
        pygame.draw.rect(self.screen, (14, 14, 14), inner)
        pygame.draw.rect(self.screen, (5, 5, 5), rect, 1)

    def _draw_door(self, rect):
        pygame.draw.rect(self.screen, (35, 20, 10), rect)
        pygame.draw.rect(self.screen, (80, 40, 10), rect, 2)
        # door handle dot
        cx = rect.centerx
        cy = rect.centery
        pygame.draw.circle(self.screen, (120, 60, 10), (cx + 6, cy), 3)

    def _draw_tower(self, rect):
        pygame.draw.rect(self.screen, (10, 30, 10), rect)
        pygame.draw.rect(self.screen, (0, 180, 60), rect, 2)
        # pulsing dot center — static for now, Phase 2 animates it
        pygame.draw.circle(
            self.screen, (0, 220, 80),
            rect.center, 5
        )

    # ── Player ──────────────────────────────────────
    def draw_player(self, player, camera):
        screen_rect = camera.apply(player.rect)

        # Body
        pygame.draw.rect(self.screen, (60, 60, 60), screen_rect)

        # Direction indicator — small triangle showing facing
        self._draw_facing_indicator(screen_rect, player.facing)

        # Crouch visual — squish the rect
        if player.is_crouching:
            crouch_rect = pygame.Rect(
                screen_rect.x + 4,
                screen_rect.y + 8,
                screen_rect.width - 8,
                screen_rect.height - 8
            )
            pygame.draw.rect(self.screen, (80, 80, 80), crouch_rect)

    def _draw_facing_indicator(self, rect, facing):
        cx, cy = rect.centerx, rect.centery
        size = 6
        dirs = {
            "up":    [(cx, cy - size), (cx - 4, cy + 3), (cx + 4, cy + 3)],
            "down":  [(cx, cy + size), (cx - 4, cy - 3), (cx + 4, cy - 3)],
            "left":  [(cx - size, cy), (cx + 3, cy - 4), (cx + 3, cy + 4)],
            "right": [(cx + size, cy), (cx - 3, cy - 4), (cx - 3, cy + 4)],
        }
        points = dirs.get(facing)
        if points:
            pygame.draw.polygon(self.screen, (180, 180, 180), points)

    # ── Flashlight ──────────────────────────────────
    def draw_flashlight(self, player, camera, flashlight):
        """
        Darkness overlay with a cone cut out around the player.
        Cone direction follows player.facing.
        """
        # Full darkness base
        darkness_alpha = self._get_darkness_alpha(flashlight)
        self._dark_overlay.fill((0, 0, 0, darkness_alpha))

        if flashlight.is_on and flashlight.battery > 0 and not flashlight.overheated:
            px, py = camera.apply_point(
                player.rect.centerx, player.rect.centery
            )
            self._cut_flashlight_cone(px, py, player.facing, flashlight)

        self.screen.blit(self._dark_overlay, (0, 0))

        # Ambient flicker edge when signal is low
        if flashlight.is_flickering:
            self._draw_flicker_edge()

    def _get_darkness_alpha(self, flashlight):
        """Darkness gets heavier as battery dies or flashlight is off."""
        if not flashlight.is_on or flashlight.battery <= 0:
            return 230   # near total dark
        if flashlight.overheated:
            return 200
        return 180       # always some darkness outside cone

    def _cut_flashlight_cone(self, px, py, facing, flashlight):
        """
        Punch a cone-shaped hole in the darkness overlay
        using a radial polygon in the direction the player faces.
        """
        angle_map = {
            "right": 0,
            "down":  90,
            "left":  180,
            "up":    270,
        }
        center_angle = math.radians(angle_map.get(facing, 0))
        spread       = math.radians(55)     # cone half-width
        radius       = FLASHLIGHT_RADIUS

        # Battery affects radius
        battery_ratio = flashlight.battery / FLASHLIGHT_MAX_BATTERY
        radius = int(radius * max(0.3, battery_ratio))

        # Build cone polygon
        steps  = 20
        points = [(px, py)]
        for i in range(steps + 1):
            a = center_angle - spread + (2 * spread * i / steps)
            points.append((
                px + math.cos(a) * radius,
                py + math.sin(a) * radius
            ))

        # Draw transparent hole — SRCALPHA 0 = fully clear
        pygame.draw.polygon(self._dark_overlay, (0, 0, 0, 0), points)

        # Soft glow halo at player center
        for r, alpha in [(40, 60), (25, 90), (12, 0)]:
            pygame.draw.circle(
                self._dark_overlay, (0, 0, 0, alpha), (px, py), r
            )

    def _draw_flicker_edge(self):
        """Red vignette pulse when signal is critically low."""
        flicker_surf = pygame.Surface(
            (SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA
        )
        alpha = random.randint(10, 50)
        pygame.draw.rect(
            flicker_surf, (120, 0, 0, alpha),
            pygame.Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT), 30
        )
        self.screen.blit(flicker_surf, (0, 0))

    # ── Entities (Phase 3 hook) ──────────────────────
    def draw_entities(self, entities, camera):
        """
        Generic entity draw pass. Phase 3 wires enemies here.
        Each entity needs a .rect and .color attribute.
        """
        for entity in entities:
            screen_rect = camera.apply(entity.rect)
            if camera.is_visible(entity.rect):
                pygame.draw.rect(self.screen, entity.color, screen_rect)

    # ── Debug ───────────────────────────────────────
    def draw_debug(self, player, camera, tilemap):
        """Toggle with D key in Phase 2+. Shows collision rects, coords."""
        font = pygame.font.SysFont("consolas", 12)

        # Player world position
        pos_txt = font.render(
            f"POS: {player.rect.x}, {player.rect.y}  "
            f"TILE: {player.rect.x // TILE_SIZE}, {player.rect.y // TILE_SIZE}",
            True, (0, 200, 80)
        )
        self.screen.blit(pos_txt, (8, 8))

        # Camera offset
        cam_txt = font.render(
            f"CAM OFFSET: {camera.offset_x}, {camera.offset_y}",
            True, (0, 200, 80)
        )
        self.screen.blit(cam_txt, (8, 22))

        # Collision rects outline
        for row_idx, row in enumerate(tilemap.grid):
            for col_idx, tile in enumerate(row):
                if tile == 1:
                    world_rect  = pygame.Rect(
                        col_idx * TILE_SIZE,
                        row_idx * TILE_SIZE,
                        TILE_SIZE, TILE_SIZE
                    )
                    screen_rect = camera.apply(world_rect)
                    if camera.is_visible(world_rect):
                        pygame.draw.rect(
                            self.screen, (200, 0, 0), screen_rect, 1
                        )