import json
import os


class Room:
    def __init__(self, room_id, name, description):
        self.room_id     = room_id
        self.name        = name
        self.description = description


class MapLoader:
    def __init__(self, filepath="data/rooms.json"):
        self.filepath  = filepath
        self.grid      = []
        self.lore_notes = []
        self.enemy_spawns = []
        self.item_spawns  = []
        self.player_spawn = (3, 3)
        self._load()

    def _load(self):
        if not os.path.exists(self.filepath):
            print(f"[MapLoader] File not found: {self.filepath}")
            return

        with open(self.filepath, "r") as f:
            data = json.load(f)

        self.grid         = data.get("grid", [])
        self.lore_notes   = data.get("lore_notes", [])
        self.enemy_spawns = data.get("enemy_spawns", [])
        self.item_spawns  = data.get("item_spawns", [])

        spawn = data.get("player_spawn", {"tile_x": 3, "tile_y": 3})
        self.player_spawn = (spawn["tile_x"], spawn["tile_y"])