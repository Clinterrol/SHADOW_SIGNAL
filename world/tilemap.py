from ursina import *
from settings import *


TILE_FLOOR  = 0
TILE_WALL   = 1
TILE_DOOR   = 2
TILE_TOWER  = 3


class Tilemap:
    def __init__(self):
        self.grid     = self._load_test_map()
        self.rows     = len(self.grid)
        self.cols     = len(self.grid[0])
        self._entities = []

    def build(self):
        """Spawn all wall/floor/ceiling entities into the Ursina scene."""
        self._entities.clear()

        for row_idx, row in enumerate(self.grid):
            for col_idx, tile in enumerate(row):
                x = col_idx * TILE_SIZE
                z = row_idx * TILE_SIZE

                # Floor always
                self._spawn_floor(x, z)

                if tile == TILE_WALL:
                    self._spawn_wall(x, z)
                elif tile == TILE_DOOR:
                    self._spawn_door(x, z)
                elif tile == TILE_TOWER:
                    self._spawn_tower(x, z)

                # Ceiling always (except open areas Phase 5)
                self._spawn_ceiling(x, z)

    # ── Spawners ────────────────────────────────────
    def _spawn_floor(self, x, z):
        e = Entity(
            model    = 'plane',
            scale    = Vec3(TILE_SIZE, 1, TILE_SIZE),
            position = Vec3(x, 0, z),
            color    = COLOR_FLOOR,
            texture  = None,
            collider = 'box'
        )
        self._entities.append(e)

    def _spawn_ceiling(self, x, z):
        e = Entity(
            model    = 'plane',
            scale    = Vec3(TILE_SIZE, 1, TILE_SIZE),
            position = Vec3(x, TILE_SIZE, z),
            rotation = Vec3(180, 0, 0),
            color    = COLOR_CEILING,
        )
        self._entities.append(e)

    def _spawn_wall(self, x, z):
        e = Entity(
            model    = 'cube',
            scale    = Vec3(TILE_SIZE, TILE_SIZE, TILE_SIZE),
            position = Vec3(x, TILE_SIZE / 2, z),
            color    = COLOR_WALL,
            texture  = None,
            collider = 'box'
        )
        self._entities.append(e)

    def _spawn_door(self, x, z):
        e = Entity(
            model    = 'cube',
            scale    = Vec3(TILE_SIZE, TILE_SIZE, TILE_SIZE * 0.1),
            position = Vec3(x, TILE_SIZE / 2, z),
            color    = color.rgb(60, 30, 10),
            collider = 'box',
            name     = 'door'
        )
        self._entities.append(e)

    def _spawn_tower(self, x, z):
        # Base
        base = Entity(
            model    = 'cube',
            scale    = Vec3(0.4, 1.2, 0.4),
            position = Vec3(x, 0.6, z),
            color    = color.rgb(10, 40, 10),
            collider = 'box',
            name     = 'tower'
        )
        # Glow top
        top = Entity(
            model    = 'sphere',
            scale    = 0.25,
            position = Vec3(x, 1.4, z),
            color    = COLOR_GREEN,
        )
        self._entities.extend([base, top])

    # ── Map Data ────────────────────────────────────
    def _load_test_map(self):
        W = TILE_WALL
        F = TILE_FLOOR
        D = TILE_DOOR
        T = TILE_TOWER

        return [
            [W,W,W,W,W,W,W,W,W,W,W,W,W,W,W,W,W,W,W,W],
            [W,F,F,F,F,F,F,F,F,W,W,W,F,F,F,F,F,F,F,W],
            [W,F,F,T,F,F,F,F,F,W,W,W,F,F,F,F,F,F,F,W],
            [W,F,F,F,F,F,F,F,F,D,F,D,F,F,T,F,F,F,F,W],
            [W,F,F,F,F,F,F,F,F,W,W,W,F,F,F,F,F,F,F,W],
            [W,F,F,F,F,F,F,F,F,W,W,W,F,F,F,F,F,F,F,W],
            [W,W,W,W,D,W,W,W,W,W,W,W,W,W,D,W,W,W,W,W],
            [W,F,F,F,F,F,F,F,F,F,F,F,F,F,F,F,F,F,F,W],
            [W,F,F,F,F,F,F,F,F,F,F,F,F,F,F,F,F,F,F,W],
            [W,F,F,F,F,F,F,F,F,T,F,F,F,F,F,F,F,F,F,W],
            [W,F,F,F,F,F,F,F,F,F,F,F,F,F,F,F,F,F,F,W],
            [W,W,W,W,W,W,W,W,W,W,W,W,W,W,W,W,W,W,W,W],
        ]

    def get_tower_positions(self):
        towers = []
        for row_idx, row in enumerate(self.grid):
            for col_idx, tile in enumerate(row):
                if tile == TILE_TOWER:
                    towers.append((col_idx, row_idx))
        return towers

    def destroy_all(self):
        for e in self._entities:
            destroy(e)
        self._entities.clear()