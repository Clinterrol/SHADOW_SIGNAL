import pygame
import json
import os
from settings import *

TILE_FLOOR = 0
TILE_WALL  = 1
TILE_DOOR  = 2
TILE_TOWER = 3


class Tilemap:
    def __init__(self, map_file="data/rooms.json"):
        self._wall_cache = {}
        self.lore_positions = {}

        print(f"[Tilemap] Looking for: {os.path.abspath(map_file)}")
        print(f"[Tilemap] File exists: {os.path.exists(map_file)}")

        if os.path.exists(map_file):
            self._load_from_json(map_file)
        else:
            print("[Tilemap] File not found, using fallback map")
            self.grid = self._fallback_map()

        self.rows = len(self.grid)
        self.cols = len(self.grid[0])
        print(f"[Tilemap] Grid size: {self.rows} rows x {self.cols} cols")
        print(f"[Tilemap] Row 0: {self.grid[0][:10]}")
        print(f"[Tilemap] Row 1: {self.grid[1][:10]}")
        self._build_wall_cache()

    def _load_from_json(self, filepath):
        print(f"[Tilemap] Loading: {os.path.abspath(filepath)}")
        with open(filepath, "r") as f:
            data = json.load(f)
        self.grid = data.get("grid", self._fallback_map())
        print(f"[Tilemap] Grid rows loaded: {len(self.grid)}")

        for note in data.get("lore_notes", []):
            key = (note["tile_x"], note["tile_y"])
            self.lore_positions[key] = note

    def _fallback_map(self):
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

    def _build_wall_cache(self):
        self._wall_cache = {}
        for row_idx, row in enumerate(self.grid):
            for col_idx, tile in enumerate(row):
                if tile == TILE_WALL:
                    self._wall_cache[(row_idx, col_idx)] = pygame.Rect(
                        col_idx * TILE_SIZE,
                        row_idx * TILE_SIZE,
                        TILE_SIZE, TILE_SIZE
                    )

    def get_wall_rects_near(self, rect):
        cx = rect.centerx // TILE_SIZE
        cy = rect.centery // TILE_SIZE
        nearby = []
        for row in range(cy - 2, cy + 3):
            for col in range(cx - 2, cx + 3):
                wall = self._wall_cache.get((row, col))
                if wall:
                    nearby.append(wall)
        return nearby

    def get_tile(self, col, row):
        if 0 <= row < self.rows and 0 <= col < self.cols:
            return self.grid[row][col]
        return TILE_WALL

    def get_tower_positions(self):
        towers = []
        for r, row in enumerate(self.grid):
            for c, tile in enumerate(row):
                if tile == TILE_TOWER:
                    towers.append((c, r))
        return towers

    def get_lore_at(self, tile_x, tile_y):
        return self.lore_positions.get((tile_x, tile_y))