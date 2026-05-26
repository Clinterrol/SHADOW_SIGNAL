import pygame
import math
import random
import os
from settings import *


class Renderer:
    def __init__(self, screen):
        self.screen = screen
        self._dark_overlay = pygame.Surface(
            (SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA
        )

        map_path = "assets/sprites/tiles/map.png"
        if os.path.exists(map_path):
            self._map_img = pygame.image.load(map_path).convert()
        else:
            self._map_img = None
        self._map_surface = None

        self._tower_img = self._load_img("assets/images/towers.png", (32, 32))
        self._medkit_img = self._load_img("assets/images/medical_kit.png", (28, 28))
        self._battery_img = self._load_img("assets/images/battery.png", (28, 28))

    def _load_img(self, path, size):
        if not os.path.exists(path):
            return None
        try:
            img = pygame.image.load(path).convert_alpha()
            return pygame.transform.scale(img, size)
        except Exception:
            return None

    # ------------------------------------------------------------------
    # Map
    # ------------------------------------------------------------------

    def draw_map(self, tilemap, camera, sprite_manager=None):
        world_w = tilemap.cols * TILE_SIZE
        world_h = tilemap.rows * TILE_SIZE

        if self._map_img:
            if self._map_surface is None:
                self._map_surface = pygame.transform.scale(
                    self._map_img, (world_w, world_h)
                )
            cam_x = int(camera.offset_x)
            cam_y = int(camera.offset_y)
            visible_rect = pygame.Rect(cam_x, cam_y, SCREEN_WIDTH, SCREEN_HEIGHT)
            clipped = visible_rect.clip(pygame.Rect(0, 0, world_w, world_h))

            if clipped.width > 0 and clipped.height > 0:
                sub = self._map_surface.subsurface(clipped)
                self.screen.blit(sub, (clipped.x - cam_x, clipped.y - cam_y))

            # Semi-transparent wall overlay so collisions are visible
            wall_surf = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
            wall_surf.fill((0, 0, 0, 200))
            for row_idx, row in enumerate(tilemap.grid):
                for col_idx, tile in enumerate(row):
                    if tile != 1:
                        continue
                    world_rect = pygame.Rect(
                        col_idx * TILE_SIZE, row_idx * TILE_SIZE,
                        TILE_SIZE, TILE_SIZE
                    )
                    if not camera.is_visible(world_rect):
                        continue
                    self.screen.blit(wall_surf, camera.apply(world_rect))
            return

        # Fallback: plain colored tiles
        for row_idx, row in enumerate(tilemap.grid):
            for col_idx, tile in enumerate(row):
                world_rect = pygame.Rect(
                    col_idx * TILE_SIZE, row_idx * TILE_SIZE,
                    TILE_SIZE, TILE_SIZE
                )
                if not camera.is_visible(world_rect):
                    continue
                screen_rect = camera.apply(world_rect)
                if tile == 1:
                    self._draw_wall(screen_rect, sprite_manager)
                elif tile == 0:
                    self._draw_floor(screen_rect, sprite_manager)
                elif tile == 2:
                    self._draw_door(screen_rect, sprite_manager)
                elif tile == 3:
                    self._draw_floor(screen_rect, sprite_manager)

    def _draw_floor(self, rect, sprite_manager=None):
        if sprite_manager:
            tile = sprite_manager.get_tile("floor")
            if tile:
                self.screen.blit(tile, rect)
                return
        pygame.draw.rect(self.screen, (18, 18, 18), rect)
        pygame.draw.rect(self.screen, (28, 28, 28), rect, 1)

    def _draw_wall(self, rect, sprite_manager=None):
        if sprite_manager:
            tile = sprite_manager.get_tile("wall")
            if tile:
                self.screen.blit(tile, rect)
                return
        pygame.draw.rect(self.screen, (8, 8, 8), rect)
        pygame.draw.rect(self.screen, (14, 14, 14), rect.inflate(-4, -4))
        pygame.draw.rect(self.screen, (5, 5, 5), rect, 1)

    def _draw_door(self, rect, sprite_manager=None):
        if sprite_manager:
            tile = sprite_manager.get_tile("door")
            if tile:
                self.screen.blit(tile, rect)
                return
        pygame.draw.rect(self.screen, (35, 20, 10), rect)
        pygame.draw.rect(self.screen, (80, 40, 10), rect, 2)
        pygame.draw.circle(self.screen, (120, 60, 10),
                           (rect.centerx + 6, rect.centery), 3)

    # ------------------------------------------------------------------
    # Towers
    # ------------------------------------------------------------------

    def draw_towers(self, towers, camera):
        for tower in towers:
            if not camera.is_visible(tower.rect):
                continue
            screen_rect = camera.apply(tower.rect)

            if self._tower_img:
                bx = screen_rect.centerx - self._tower_img.get_width() // 2
                by = screen_rect.centery - self._tower_img.get_height() // 2
                self.screen.blit(self._tower_img, (bx, by))
                tint = pygame.Surface(self._tower_img.get_size(), pygame.SRCALPHA)
                if tower.active:
                    tint.fill((0, 200, 80, 60))
                elif tower.pulse_on:
                    tint.fill((0, 80, 30, 40))
                self.screen.blit(tint, (bx, by))
            else:
                if tower.active:
                    pygame.draw.rect(self.screen, (10, 40, 10), screen_rect)
                    pygame.draw.rect(self.screen, (0, 180, 60), screen_rect, 2)
                    pygame.draw.circle(self.screen, (0, 220, 80), screen_rect.center, 6)
                else:
                    pygame.draw.rect(self.screen, (10, 25, 10), screen_rect)
                    pygame.draw.rect(self.screen, (0, 80, 30), screen_rect, 2)
                    if tower.pulse_on:
                        pygame.draw.circle(self.screen, (0, 100, 40), screen_rect.center, 4)

    # ------------------------------------------------------------------
    # Exit tile
    # ------------------------------------------------------------------

    def draw_exit(self, exit_rect, camera):
        if not camera.is_visible(exit_rect):
            return
        screen_rect = camera.apply(exit_rect)
        t = pygame.time.get_ticks() / 1000.0
        pulse = int(180 + 75 * math.sin(t * 4))

        glow = pygame.Surface((TILE_SIZE + 12, TILE_SIZE + 12), pygame.SRCALPHA)
        pygame.draw.rect(
            glow, (0, pulse, 80, 80),
            pygame.Rect(0, 0, TILE_SIZE + 12, TILE_SIZE + 12),
            border_radius=6
        )
        self.screen.blit(glow, (screen_rect.x - 6, screen_rect.y - 6))

        pygame.draw.rect(self.screen, (0, 60, 20), screen_rect, border_radius=4)
        pygame.draw.rect(self.screen, (0, pulse, 80), screen_rect, 2, border_radius=4)

        font = pygame.font.SysFont("consolas", 9, bold=True)
        lbl = font.render("EXIT", True, (0, 255, 100))
        self.screen.blit(lbl, (
            screen_rect.centerx - lbl.get_width() // 2,
            screen_rect.centery - lbl.get_height() // 2
        ))

    # ------------------------------------------------------------------
    # Lore notes
    # ------------------------------------------------------------------

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
                screen_rect.centerx - lbl.get_width() // 2,
                screen_rect.centery - lbl.get_height() // 2
            ))

    # ------------------------------------------------------------------
    # Items
    # ------------------------------------------------------------------

    def draw_items(self, items, camera):
        font = pygame.font.SysFont("consolas", 11, bold=True)
        for item in items:
            if not item.active:
                continue
            if not camera.is_visible(item.rect):
                continue
            screen_rect = camera.apply(item.rect)
            kind = getattr(item, "kind", "")
            img = (self._medkit_img if kind == "medkit" else
                    self._battery_img if kind == "battery" else None)

            if img:
                bx = screen_rect.centerx - img.get_width() // 2
                by = screen_rect.centery - img.get_height() // 2
                self.screen.blit(img, (bx, by))
            else:
                pygame.draw.rect(self.screen, (30, 30, 30), screen_rect)
                pygame.draw.rect(self.screen, item.color, screen_rect, 2)
                lbl = font.render(item.label, True, item.color)
                self.screen.blit(lbl, (
                    screen_rect.centerx - lbl.get_width() // 2,
                    screen_rect.centery - lbl.get_height() // 2
                ))

    # ------------------------------------------------------------------
    # Entities (enemies)
    # ------------------------------------------------------------------

    def draw_entities(self, entities, camera, sprite_manager=None):
        for entity in entities:
            is_fading = getattr(entity, "dying", False)
            if not entity.alive and not is_fading:
                continue
            if not camera.is_visible(entity.rect):
                continue

            screen_rect = camera.apply(entity.rect)
            cx = screen_rect.centerx
            cy = screen_rect.centery
            entity_type = type(entity).__name__.lower()
            r = ENEMY_DRAW_RADIUS
            fade_alpha = int(getattr(entity, "_fade_alpha", 255))

            if sprite_manager:
                img = sprite_manager.get_enemy(entity_type)
                if img:
                    if is_fading and fade_alpha < 255:
                        img = img.copy()
                        img.set_alpha(fade_alpha)
                    self.screen.blit(img, (
                        cx - img.get_width() // 2,
                        cy - img.get_height() // 2
                    ))
                    continue

            # Fallback shapes per enemy type
            if entity_type == "watcher":
                pygame.draw.circle(self.screen, (60, 0, 80), (cx, cy), r)
                pygame.draw.circle(self.screen, (120, 0, 160), (cx, cy), r, 2)
                pygame.draw.circle(self.screen, (220, 0, 0), (cx - 5, cy - 3), 3)
                pygame.draw.circle(self.screen, (220, 0, 0), (cx + 5, cy - 3), 3)
                if entity.state == "frozen":
                    pygame.draw.circle(self.screen, (0, 100, 220), (cx, cy), r + 3, 2)
                elif entity.state == "chase":
                    pygame.draw.circle(self.screen, (180, 0, 0), (cx, cy), r + 3, 1)

            elif entity_type == "crawler":
                pygame.draw.ellipse(
                    self.screen, (80, 40, 0),
                    pygame.Rect(cx - r, cy - int(r * 0.6), r * 2, int(r * 1.2))
                )
                pygame.draw.ellipse(
                    self.screen, (140, 70, 0),
                    pygame.Rect(cx - r, cy - int(r * 0.6), r * 2, int(r * 1.2)), 1
                )

            elif entity_type == "mimic":
                if is_fading and fade_alpha < 255:
                    surf = pygame.Surface((r * 2 + 4, r * 2 + 4), pygame.SRCALPHA)
                    pygame.draw.circle(surf, (40, 40, 80, fade_alpha), (r + 2, r + 2), r)
                    pygame.draw.circle(surf, (80, 80, 160, fade_alpha), (r + 2, r + 2), r, 2)
                    self.screen.blit(surf, (cx - r - 2, cy - r - 2))
                else:
                    pygame.draw.circle(self.screen, (40, 40, 80), (cx, cy), r)
                    pygame.draw.circle(self.screen, (80, 80, 160), (cx, cy), r, 2)

    # ------------------------------------------------------------------
    # Player
    # ------------------------------------------------------------------

    def draw_player(self, player, camera, sprite_manager=None):
        screen_rect = camera.apply(player.rect)
        cx = screen_rect.centerx
        cy = screen_rect.centery

        if sprite_manager and sprite_manager.has_sprite("player"):
            frame = sprite_manager.get_player_frame(player.facing, player._frame_index)
            if frame:
                self.screen.blit(frame, (
                    cx - frame.get_width() // 2,
                    cy - frame.get_height() // 2
                ))
                return

        # Fallback
        pygame.draw.circle(self.screen, (50, 50, 55), (cx, cy), 10)
        pygame.draw.circle(self.screen, (90, 90, 100), (cx, cy), 10, 2)
        offset = 7
        facing_offsets = {
            "up": (0, -offset),
            "down": (0, offset),
            "left": (-offset, 0),
            "right": ( offset, 0),
        }
        dx, dy = facing_offsets.get(player.facing, (offset, 0))
        pygame.draw.circle(self.screen, (200, 200, 220), (cx + dx, cy + dy), 3)
        if player.is_crouching:
            pygame.draw.circle(self.screen, (180, 140, 0), (cx, cy), 12, 1)
        elif player.is_sprinting:
            pygame.draw.circle(self.screen, (180, 180, 180), (cx, cy), 13, 1)

    # ------------------------------------------------------------------
    # Flashlight
    # ------------------------------------------------------------------

    def draw_flashlight(self, player, camera, flashlight, entities=None):
        px, py = camera.apply_point(player.rect.centerx, player.rect.centery)

        self._dark_overlay.fill((0, 0, 0, 255))
        self._punch_circle(px, py, 45)

        if flashlight.is_on and flashlight.battery > 0 and not flashlight.overheated:
            self._cut_flashlight_cone(px, py, player.facing, flashlight)

        if entities and flashlight.is_on and flashlight.battery > 0:
            angle_map = {"right": 0, "down": 90, "left": 180, "up": 270}
            ca = math.radians(angle_map.get(player.facing, 0))
            sp = math.radians(75)
            for entity in entities:
                if not entity.alive:
                    continue
                dx = entity.rect.centerx - player.rect.centerx
                dy = entity.rect.centery - player.rect.centery
                dist = (dx * dx + dy * dy) ** 0.5
                if dist > FLASHLIGHT_RADIUS * 1.3:
                    continue
                at = math.atan2(dy, dx)
                df = abs(at - ca)
                if df > math.pi:
                    df = 2 * math.pi - df
                if df <= sp:
                    ex, ey = camera.apply_point(entity.rect.centerx, entity.rect.centery)
                    pygame.draw.circle(self._dark_overlay, (0, 0, 0, 0), (ex, ey), 35)

        self.screen.blit(self._dark_overlay, (0, 0))

        if flashlight.is_flickering:
            self._draw_flicker_edge()

    def _punch_circle(self, px, py, radius):
        for r in range(radius, 0, -5):
            progress = 1 - (r / radius)
            alpha = int(220 * progress)
            pygame.draw.circle(self._dark_overlay, (0, 0, 0, alpha), (px, py), r)
        pygame.draw.circle(self._dark_overlay, (0, 0, 0, 0), (px, py), radius // 4)

    def _cut_flashlight_cone(self, px, py, facing, flashlight):
        angle_map = {"right": 0, "down": 90, "left": 180, "up": 270}
        center_angle = math.radians(angle_map.get(facing, 0))
        spread = math.radians(70)
        radius = int(FLASHLIGHT_RADIUS * 1.3 * max(
            0.4, flashlight.battery / FLASHLIGHT_MAX_BATTERY
        ))
        steps = 28
        points = [(px, py)]
        for i in range(steps + 1):
            a = center_angle - spread + (2 * spread * i / steps)
            points.append((
                px + math.cos(a) * radius,
                py + math.sin(a) * radius
            ))
        pygame.draw.polygon(self._dark_overlay, (0, 0, 0, 0), points)
        for r, alpha in [(60, 30), (40, 60), (20, 0)]:
            pygame.draw.circle(self._dark_overlay, (0, 0, 0, alpha), (px, py), r)

    def _draw_flicker_edge(self):
        flicker_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        alpha = random.randint(10, 50)
        pygame.draw.rect(
            flicker_surf, (120, 0, 0, alpha),
            pygame.Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT), 30
        )
        self.screen.blit(flicker_surf, (0, 0))