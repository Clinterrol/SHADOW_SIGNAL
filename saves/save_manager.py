import json
import os


SAVE_PATH = "saves/save_data.json"


class SaveManager:
    def __init__(self):
        os.makedirs("saves", exist_ok=True)

    def save(self, game):
        data = {
            "player": {
                "health":   game.player.health,
                "tile_x":   game.player.rect.x // 32,
                "tile_y":   game.player.rect.y // 32,
            },
            "flashlight": {
                "battery":    game.flashlight.battery,
                "is_on":      game.flashlight.is_on,
            },
            "signal": {
                "stability":     game.signal_sys.stability,
                "towers_active": game.signal_sys.towers_active,
            },
            "towers": [
                {"active": t.active, "tile_x": t.tile_x, "tile_y": t.tile_y}
                for t in game.towers
            ],
            "items": [
                {
                    "kind":   item.kind,
                    "tile_x": item.rect.x // 32,
                    "tile_y": item.rect.y // 32,
                    "active": item.active
                }
                for item in game.items
            ],
            "lore_notes": [
                {
                    "id":        note.note_id,
                    "collected": note.collected
                }
                for note in game.lore_notes
            ],
            "sanity": {
                "sanity": game.sanity_sys.sanity
            }
        }

        with open(SAVE_PATH, "w") as f:
            json.dump(data, f, indent=2)
        print("[SaveManager] Game saved.")

    def load(self, game):
        if not os.path.exists(SAVE_PATH):
            print("[SaveManager] No save file found.")
            return False

        with open(SAVE_PATH, "r") as f:
            data = json.load(f)

        # Player
        game.player.health  = data["player"]["health"]
        game.player.rect.x  = data["player"]["tile_x"] * 32
        game.player.rect.y  = data["player"]["tile_y"] * 32

        # Flashlight
        game.flashlight.battery = data["flashlight"]["battery"]
        game.flashlight.is_on   = data["flashlight"]["is_on"]

        # Signal
        game.signal_sys.stability     = data["signal"]["stability"]
        game.signal_sys.towers_active = data["signal"]["towers_active"]

        # Towers
        for i, t_data in enumerate(data["towers"]):
            if i < len(game.towers):
                game.towers[i].active = t_data["active"]

        # Items
        for i, i_data in enumerate(data["items"]):
            if i < len(game.items):
                game.items[i].active = i_data["active"]

        # Lore notes
        collected_ids = {
            n["id"] for n in data["lore_notes"] if n["collected"]
        }
        for note in game.lore_notes:
            if note.note_id in collected_ids:
                note.collected = True

        # Sanity
        game.sanity_sys.sanity = data["sanity"]["sanity"]

        print("[SaveManager] Game loaded.")
        return True

    def has_save(self):
        return os.path.exists(SAVE_PATH)

    def delete_save(self):
        if os.path.exists(SAVE_PATH):
            os.remove(SAVE_PATH)