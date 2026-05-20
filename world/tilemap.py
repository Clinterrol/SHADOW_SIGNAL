import pygame
from settings import *


# ── Tile Constants ──────────────────────────────────
TILE_FLOOR  = 0
TILE_WALL   = 1
TILE_DOOR   = 2
TILE_TOWER  = 3


class Tilemap:
    def __init__(self):
        self.grid = self._load_test_map()
        self.rows = len(self.grid)
        self.cols = len(self.grid[0])

        # Cache wall rects once — rebuilt only if map changes
        self._wall_cache = {}
        self._build_wall_cache()

    # ── Map Data ────────────────────────────────────
    def _load_test_map(self):
        """
        Hardcoded test map for Phase 1.
        0 = floor  1 = wall  2 = door  3 = signal tower
        Phase 5 replaces this with rooms.json loader.
        """
        W = TILE_WALL
        F = TILE_FLOOR
        D = TILE_DOOR
        T = TILE_TOWER

        return [
            [W,W,W,W,W,W,W,W,W,W,W,W,W,W,W,W,W,W,W,W,W,W,W,W,W],
            [W,F,F,F,F,F,F,F,F,W,W,W,W,W,W,W,F,F,F,F,F,F,F,F,W],
            [W,F,F,F,F,F,F,F,F,W,W,W,W,W,W,W,F,F,F,F,F,F,F,F,W],
            [W,F,F,T,F,F,F,F,F,W,W,W,W,W,W,W,F,F,F,F,F,F,F,F,W],
            [W,F,F,F,F,F,F,F,F,D,F,F,F,F,F,D,F,F,F,T,F,F,F,F,W],
            [W,F,F,F,F,F,F,F,F,W,W,W,W,W,W,W,F,F,F,F,F,F,F,F,W],
            [W,F,F,F,F,F,F,F,F,W,W,W,W,W,W,W,F,F,F,F,F,F,F,F,W],
            [W,F,F,F,F,F,F,F,F,W,W,W,W,W,W,W,F,F,F,F,F,F,F,F,W],
            [W,W,W,W,D,W,W,W,W,W,W,W,W,W,W,W,W,W,W,D,W,W,W,W,W],
            [W,F,F,F,F,F,F,F,F,F,F,F,F,F,F,F,F,F,F,F,F,F,F,F,W],
            [W,F,F,F,F,F,F,F,F,F,F,F,F,F,F,F,F,F,F,F,F,F,F,F,W],
            [W,F,F,F,F,F,F,F,F,F,F,F,T,F,F,F,F,F,F,F,F,F,F,F,W],
            [W,F,F,F,F,F,F,F,F,F,F,F,F,F,F,F,F,F,F,F,F,F,F,F,W],
            [W,F,F,F,F,F,F,F,F,F,F,F,F,F,F,F,F,F,F,F,F,F,F,F,W],
            [W,W,W,W,W,W,W,W,W,W,W,W,W,W,W,W,W,W,W,W,W,W,W,W,W],
        ]

    # ── Wall Cache ──────────────────────────────────
    def _build_wall_cache(self):
        """
        Pre-build wall rects indexed by (row, col).
        Collision checks query nearby cells only — not the full grid.
        """
        self._wall_cache = {}
        for row_idx, row in enumerate(self.grid):
            for col_idx, tile in enumerate(row):
                if tile == TILE_WALL:
                    self._wall_cache[(row_idx, col_idx)] = pygame.Rect(
                        col_idx * TILE_SIZE,
                        row_idx * TILE_SIZE,
                        TILE_SIZE,
                        TILE_SIZE
                    )

    def get_wall_rects_near(self, rect):
        """
        Return wall rects in a 3x3 tile radius around rect.
        Called every frame by player collision — must be fast.
        """
        center_col = rect.centerx // TILE_SIZE
        center_row = rect.centery // TILE_SIZE

        nearby = []
        for row in range(center_row - 2, center_row + 3):
            for col in range(center_col - 2, center_col + 3):
                wall = self._wall_cache.get((row, col))
                if wall:
                    nearby.append(wall)
        return nearby

    # ── Tile Queries ────────────────────────────────
    def get_tile(self, col, row):
        """Safe tile read — returns WALL for out-of-bounds."""
        if 0 <= row < self.rows and 0 <= col < self.cols:
            return self.grid[row][col]
        return TILE_WALL

    def set_tile(self, col, row, tile_type):
        """Modify a tile at runtime — used for door open/close, Phase 5."""
        if 0 <= row < self.rows and 0 <= col < self.cols:
            self.grid[row][col] = tile_type
            # Rebuild wall cache if wall state changed
            if tile_type == TILE_WALL:
                self._wall_cache[(row, col)] = pygame.Rect(
                    col * TILE_SIZE,
                    row * TILE_SIZE,
                    TILE_SIZE,
                    TILE_SIZE
                )
            else:
                self._wall_cache.pop((row, col), None)

    def is_walkable(self, col, row):
        tile = self.get_tile(col, row)
        return tile in (TILE_FLOOR, TILE_DOOR, TILE_TOWER)

    def get_tile_rect(self, col, row):
        return pygame.Rect(
            col * TILE_SIZE,
            row * TILE_SIZE,
            TILE_SIZE,
            TILE_SIZE
        )

    # ── Tower Locations ─────────────────────────────
    def get_tower_positions(self):
        """
        Returns list of (col, row) for all signal towers.
        Phase 2 signal system reads this.
        """
        towers = []
        for row_idx, row in enumerate(self.grid):
            for col_idx, tile in enumerate(row):
                if tile == TILE_TOWER:
                    towers.append((col_idx, row_idx))
        return towers