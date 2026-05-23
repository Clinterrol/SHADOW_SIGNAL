import pygame
import random
from settings import *


class GlitchFX:
    def __init__(self, screen):
        self.screen       = screen
        self._scan_offset = 0
        self._noise_surf  = pygame.Surface(
            (SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA
        )

    def draw(self, signal_sys, event_sys):
        if signal_sys.is_critical:
            self._draw_scanlines(signal_sys)
            self._draw_chromatic_aberration(signal_sys)

        if event_sys.alarm_active:
            self._draw_alarm_flash()

        if event_sys.radio_visible:
            self._draw_radio_text(event_sys.current_radio)

        if signal_sys.is_blackout:
            self._draw_vhs_noise()

    def _draw_scanlines(self, sig):
        intensity = 1.0 - (sig.stability / SIGNAL_CRIT_THRESH)
        alpha     = int(intensity * 40)
        surf      = pygame.Surface(
            (SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA
        )
        for y in range(0, SCREEN_HEIGHT, 4):
            pygame.draw.line(surf, (0, 0, 0, alpha),
                             (0, y), (SCREEN_WIDTH, y))
        self.screen.blit(surf, (0, 0))

    def _draw_chromatic_aberration(self, sig):
        if random.random() > 0.08:
            return
        intensity = 1.0 - (sig.stability / SIGNAL_CRIT_THRESH)
        offset    = int(intensity * 6)
        if offset <= 0:
            return
        region = pygame.Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT)
        try:
            snap = self.screen.subsurface(region).copy()
            r_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            r_surf.blit(snap, (offset, 0))
            r_surf.fill((255, 0, 0, 30), special_flags=pygame.BLEND_RGBA_MULT)
            self.screen.blit(r_surf, (0, 0), special_flags=pygame.BLEND_ADD)
        except:
            pass

    def _draw_alarm_flash(self):
        surf = pygame.Surface(
            (SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA
        )
        alpha = random.randint(20, 60)
        surf.fill((180, 0, 0, alpha))
        self.screen.blit(surf, (0, 0))

        # Red border flash
        border_surf = pygame.Surface(
            (SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA
        )
        pygame.draw.rect(border_surf, (220, 0, 0, 120),
                         pygame.Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT), 20)
        self.screen.blit(border_surf, (0, 0))

    def _draw_radio_text(self, text):
        font = pygame.font.SysFont("consolas", 14)
        if random.random() > 0.1:
            surf = font.render(f"// RADIO: {text}", True, (0, 180, 60))
            x    = SCREEN_WIDTH  // 2 - surf.get_width()  // 2
            y    = SCREEN_HEIGHT - 60
            # Glitch offset
            offset = random.randint(-2, 2)
            self.screen.blit(surf, (x + offset, y))

    def _draw_vhs_noise(self):
        self._noise_surf.fill((0, 0, 0, 0))
        for _ in range(80):
            x = random.randint(0, SCREEN_WIDTH)
            y = random.randint(0, SCREEN_HEIGHT)
            w = random.randint(10, 80)
            h = random.randint(1, 3)
            alpha = random.randint(20, 80)
            pygame.draw.rect(
                self._noise_surf,
                (random.randint(100, 200),
                 random.randint(100, 200),
                 random.randint(100, 200), alpha),
                (x, y, w, h)
            )
        self.screen.blit(self._noise_surf, (0, 0))