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

        # Fake glitch jumpscare messages
        self._messages = [
            "IT SEES YOU",
            "RUN",
            "BEHIND YOU",
            "DON'T LOOK",
        ]
        self._current_msg = ""

    def update(self, dt, player, watchers, signal_sys):
        self._cooldown = max(0.0, self._cooldown - dt)

        if self.active:
            self._timer += dt
            # Fade in
            if self._phase == "in":
                self._alpha = min(255, int(255 * (self._timer / 0.1)))
                if self._timer >= 0.1:
                    self._phase = "hold"
                    self._timer = 0.0
            # Hold
            elif self._phase == "hold":
                if self._timer >= 0.15:
                    self._phase = "out"
                    self._timer = 0.0
            # Fade out
            elif self._phase == "out":
                self._alpha = max(0, int(255 * (1 - self._timer / 0.15)))
                if self._timer >= 0.15:
                    self.active = False
                    self._phase = "in"
                    self._timer = 0.0
            return

        # Trigger conditions
        if self._cooldown > 0:
            return

        for watcher in watchers:
            if not watcher.alive:
                continue
            if watcher.touches_player(player):
                self._trigger()
                return

        # Random scare at low signal
        if signal_sys.is_critical and random.random() < 0.001:
            self._trigger()

    def _trigger(self):
        self.active       = True
        self._timer       = 0.0
        self._phase       = "in"
        self._alpha       = 0
        self._cooldown    = self._cooldown_time
        self._current_msg = random.choice(self._messages)

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