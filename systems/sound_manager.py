import pygame
import os


class SoundManager:
    def __init__(self):
        pygame.mixer.init()

        self._sfx_files = {
            # --- MENU ---
            "menu_hover":           "assets/sounds/sfx/menu_hover.wav",

            # --- FLASHLIGHT ---
            "flashlight_on":        "assets/sounds/sfx/flashlight_on.wav",
            "flashlight_off":       "assets/sounds/sfx/flashlight_off.wav",
            "flashlight_overheat":  "assets/sounds/sfx/flashlight_overheat.wav",

            # --- JUMPSCARE STINGS ---
            # jumpscare_dontlook, jumpscare_run, jumpscare_seesyou are MP3
            # jumpscare_behind is WAV
            "jumpscare_seesyou":    "assets/sounds/sfx/jumpscare_seesyou.mp3",
            "jumpscare_run":        "assets/sounds/sfx/jumpscare_run.mp3",
            "jumpscare_behind":     "assets/sounds/sfx/jumpscare_behind.wav",
            "jumpscare_dontlook":   "assets/sounds/sfx/jumpscare_dontlook.mp3",

            # --- ENEMY SOUNDS ---
            "watcher_growl":        "assets/sounds/sfx/watcher_growl.wav",   # watcher enters chase state
            "crawler_skitter":        "assets/sounds/sfx/crawler_skitter.wav",   # crawler emerges or chases
            "enemy_footstep":      "assets/sounds/sfx/enemy_footstep.wav", # enemy footstep when nearby

            # --- PLAYER ACTIONS ---
            "player_footstep":      "assets/sounds/sfx/player_footstep.wav",
            "item_pickup":          "assets/sounds/sfx/item_pickup.wav",
            "heal":                 "assets/sounds/sfx/heal.wav",
            "tower_repair":         "assets/sounds/sfx/tower_repair.wav",

            # --- GAME STATE ---
            "player_death":         "assets/sounds/sfx/player_death.wav",
            "win":                  "assets/sounds/sfx/win.wav",
            "cry":                  "assets/sounds/sfx/cry.wav",
        }

        self._music_files = {
            "menu_music":           "assets/sounds/ambient/menu_music.wav",
            "game_ambient":         "assets/sounds/ambient/game_ambient.wav",
        }

        # Jumpscare message to sound key map
        self.jumpscare_sound_map = {
            "IT SEES YOU": "jumpscare_seesyou",
            "RUN":         "jumpscare_run",
            "BEHIND YOU":  "jumpscare_behind",
            "DON'T LOOK":  "jumpscare_dontlook",
        }

        self._sounds = {}
        self._load_all()

    def _load_all(self):
        for key, path in self._sfx_files.items():
            if os.path.exists(path):
                self._sounds[key] = pygame.mixer.Sound(path)
            else:
                # File not yet in place — will be skipped silently
                self._sounds[key] = None

    def play(self, key, volume=1.0):
        sound = self._sounds.get(key)
        if sound:
            sound.set_volume(volume)
            sound.play()

    def stop(self, key):
        sound = self._sounds.get(key)
        if sound:
            sound.stop()

    def play_music(self, key, volume=0.4, loops=-1):
        path = self._music_files.get(key)
        if path and os.path.exists(path):
            pygame.mixer.music.load(path)
            pygame.mixer.music.set_volume(volume)
            pygame.mixer.music.play(loops)

    def stop_music(self):
        pygame.mixer.music.stop()

    def set_volume(self, key, volume):
        sound = self._sounds.get(key)
        if sound:
            sound.set_volume(volume)