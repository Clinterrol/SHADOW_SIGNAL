import pygame
import os
from settings import TILE_SIZE


class SpriteManager:
    def __init__(self):
        self.sprites = {}

    def load_all(self):
        self.load_player()
        self.load_tiles()
        self.load_enemies()

    def load_player(self, path="assets/sprites/player/player_sheet.png"):
        if not os.path.exists(path):
            print(f"[SpriteManager] Missing: {path}")
            return False

        sheet   = pygame.image.load(path).convert_alpha()
        frame_w = sheet.get_width()  // 4
        frame_h = sheet.get_height() // 4

        directions = ["up", "down", "left"]
        self.sprites["player"] = {}

        for row, direction in enumerate(directions):
            frames = []
            for col in range(4):
                frame = sheet.subsurface(pygame.Rect(
                    col * frame_w,
                    row * frame_h,
                    frame_w,
                    frame_h
                ))
                frame = pygame.transform.scale(frame, (48, 48))
                frame.set_colorkey((240, 240, 240))
                frames.append(frame)
            self.sprites["player"][direction] = frames

            if direction == "left":
                right_frames = [
                    pygame.transform.flip(f, True, False) for f in frames
                ]
                self.sprites["player"]["right"] = right_frames

        print("[SpriteManager] Player sprites loaded.")
        return True

    def load_tiles(self):
        tile_files = {
            "floor": "assets/sprites/tiles/floor.png",
            "wall":  "assets/sprites/tiles/wall.png",
            "door":  "assets/sprites/tiles/door.png",
        }
        self.sprites["tiles"] = {}
        for name, path in tile_files.items():
            if not os.path.exists(path):
                print(f"[SpriteManager] Missing tile: {path}")
                self.sprites["tiles"][name] = None
                continue
            img = pygame.image.load(path).convert_alpha()
            img = pygame.transform.scale(img, (TILE_SIZE, TILE_SIZE))
            self.sprites["tiles"][name] = img
            print(f"[SpriteManager] Tile loaded: {name}")

    def load_enemies(self):
        enemy_files = {
            "watcher": "assets/sprites/enemies/watcher.png",
            "crawler": "assets/sprites/enemies/crawler.png",
            "mimic":   "assets/sprites/enemies/mimic.png",
        }
        self.sprites["enemies"] = {}
        for name, path in enemy_files.items():
            if not os.path.exists(path):
                print(f"[SpriteManager] Missing enemy: {path}")
                self.sprites["enemies"][name] = None
                continue
            img = pygame.image.load(path).convert_alpha()
            img = pygame.transform.scale(img, (40, 40))
            self.sprites["enemies"][name] = img
            print(f"[SpriteManager] Enemy loaded: {name}")

    def get_player_frame(self, direction, frame_index):
        try:
            frames = self.sprites["player"][direction]
            return frames[frame_index % len(frames)]
        except:
            return None

    def get_tile(self, name):
        try:
            return self.sprites["tiles"].get(name)
        except:
            return None

    def get_enemy(self, name):
        try:
            return self.sprites["enemies"].get(name)
        except:
            return None

    def has_sprite(self, name):
        return name in self.sprites