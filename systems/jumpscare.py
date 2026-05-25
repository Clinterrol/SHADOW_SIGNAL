import pygame
import random
from settings import *


class JumpscareSystem:
    def __init__(self, screen):
        self.screen         = screen
        self.active         = False
        self._timer         = 0.0
        self._duration      = 0.4
        self._cooldown      = 0.0
        self._cooldown_time = 30.0
        self._alpha         = 0
        self._phase         = "in"

        self._messages = [
            "IT SEES YOU",
            "RUN",
            "BEHIND YOU",
            "DON'T LOOK",
        ]
        self._current_msg = ""

        self.sound_manager = None  # injected from game._init_systems()

    def update(self, dt, player, watchers, signal_sys):
        self._cooldown = max(0.0, self._cooldown - dt)

        if self.active:
            self._timer += dt
            if self._phase == "in":
                self._alpha = min(255, int(255 * (self._timer / 0.1)))
                if self._timer >= 0.1:
                    self._phase = "hold"
                    self._timer = 0.0
            elif self._phase == "hold":
                if self._timer >= 0.15:
                    self._phase = "out"
                    self._timer = 0.0
            elif self._phase == "out":
                self._alpha = max(0, int(255 * (1 - self._timer / 0.15)))
                if self._timer >= 0.15:
                    self.active = False
                    self._phase = "in"
                    self._timer = 0.0
            return

        if self._cooldown > 0:
            return

        for watcher in watchers:
            if not watcher.alive:
                continue
            if watcher.touches_player(player):
                self._trigger()
                return

        if signal_sys.is_critical and random.random() < 0.001:
            self._trigger()

    def _trigger(self):
        self.active       = True
        self._timer       = 0.0
        self._phase       = "in"
        self._alpha       = 0
        self._cooldown    = self._cooldown_time
        self._current_msg = random.choice(self._messages)

        # --- JUMPSCARE STING SOUND ---
        # Each message maps to its own sting file in sound_manager.py
        # Files: assets/sounds/sfx/jumpscare_seesyou.wav
        #        assets/sounds/sfx/jumpscare_run.wav
        #        assets/sounds/sfx/jumpscare_behind.wav
        #        assets/sounds/sfx/jumpscare_dontlook.wav
        if self.sound_manager:
            key = self.sound_manager.jumpscare_sound_map.get(self._current_msg)
            if key:
                self.sound_manager.play(key, volume=1.0)

    def draw(self):
        if not self.active:
            return

        surf = pygame.Surface(
            (SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA
        )
        surf.fill((180, 0, 0, self._alpha))
        self.screen.blit(surf, (0, 0))

        if self._phase == "hold":
            font = pygame.font.SysFont("consolas", 72, bold=True)
            txt  = font.render(self._current_msg, True, (255, 255, 255))
            self.screen.blit(txt, txt.get_rect(
                center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2)
            ))