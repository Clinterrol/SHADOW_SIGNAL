
import pygame
import random
from settings import *


class HUD:
    def __init__(self, screen):
        self.screen     = screen
        self.font_small = pygame.font.SysFont("consolas", 13)
        self.font_med   = pygame.font.SysFont("consolas", 16, bold=True)
        self.font_large = pygame.font.SysFont("consolas", 22, bold=True)

    def draw(self, flashlight, signal_sys, player,
             sanity_sys=None, heartbeat=None, audio_det=None):
        self._draw_signal_bar(signal_sys)
        self._draw_battery_bar(flashlight)
        self._draw_health_bar(player)
        if sanity_sys:
            self._draw_sanity_bar(sanity_sys)
        self._draw_flashlight_status(flashlight)
        self._draw_tower_count(signal_sys)
        self._draw_signal_status(signal_sys)

        if audio_det and audio_det.is_alerted:
            self._draw_alert_indicator()

        if heartbeat and heartbeat.beat and heartbeat.intensity > 0.1:
            self._draw_heartbeat(heartbeat)

        if signal_sys.is_critical:
            self._draw_glitch_overlay(signal_sys)
        if signal_sys.is_blackout:
            self._draw_blackout_warning()

        if sanity_sys and sanity_sys.hallucinating:
            self._draw_hallucination(sanity_sys.current_halluc)

    def _draw_signal_bar(self, sig):
        label = self.font_small.render("SIGNAL", True, (100, 100, 100))
        self.screen.blit(label, (12, 12))
        bar_x, bar_y, bar_w, bar_h = 12, 28, 160, 12
        pygame.draw.rect(self.screen, (20, 20, 20),
                         (bar_x, bar_y, bar_w, bar_h))
        fill_w = int(bar_w * sig.stability_pct)
        if fill_w > 0:
            pygame.draw.rect(self.screen, sig.status_color,
                             (bar_x, bar_y, fill_w, bar_h))
        pygame.draw.rect(self.screen, (50, 50, 50),
                         (bar_x, bar_y, bar_w, bar_h), 1)
        pct = self.font_small.render(
            f"{int(sig.stability)}%", True, (80, 80, 80))
        self.screen.blit(pct, (bar_x + bar_w + 6, bar_y))

    def _draw_battery_bar(self, fl):
        label = self.font_small.render("BATTERY", True, (100, 100, 100))
        self.screen.blit(label, (12, 48))
        bar_x, bar_y, bar_w, bar_h = 12, 64, 160, 10
        pygame.draw.rect(self.screen, (20, 20, 20),
                         (bar_x, bar_y, bar_w, bar_h))
        fill_w = int(bar_w * fl.battery_pct)
        col    = AMBER if fl.battery_pct > 0.5 else DANGER_RED
        if fill_w > 0:
            pygame.draw.rect(self.screen, col,
                             (bar_x, bar_y, fill_w, bar_h))
        pygame.draw.rect(self.screen, (50, 50, 50),
                         (bar_x, bar_y, bar_w, bar_h), 1)
        pct = self.font_small.render(
            f"{int(fl.battery)}%", True, (80, 80, 80))
        self.screen.blit(pct, (bar_x + bar_w + 6, bar_y))

    def _draw_health_bar(self, player):
        label = self.font_small.render("HEALTH", True, (100, 100, 100))
        self.screen.blit(label, (12, 82))
        bar_x, bar_y, bar_w, bar_h = 12, 98, 160, 10
        pygame.draw.rect(self.screen, (20, 20, 20),
                         (bar_x, bar_y, bar_w, bar_h))
        hp_pct = player.health / PLAYER_MAX_HEALTH
        fill_w = int(bar_w * hp_pct)
        col    = (0, 180, 60) if hp_pct > 0.6 else \
                 AMBER if hp_pct > 0.3 else DANGER_RED
        if fill_w > 0:
            pygame.draw.rect(self.screen, col,
                             (bar_x, bar_y, fill_w, bar_h))
        pygame.draw.rect(self.screen, (50, 50, 50),
                         (bar_x, bar_y, bar_w, bar_h), 1)
        hp = self.font_small.render(str(player.health), True, (80, 80, 80))
        self.screen.blit(hp, (bar_x + bar_w + 6, bar_y))

    def _draw_sanity_bar(self, sanity):
        label = self.font_small.render("SANITY", True, (100, 100, 100))
        self.screen.blit(label, (12, 116))
        bar_x, bar_y, bar_w, bar_h = 12, 132, 160, 10
        pygame.draw.rect(self.screen, (20, 20, 20),
                         (bar_x, bar_y, bar_w, bar_h))
        fill_w = int(bar_w * sanity.sanity_pct)
        col    = (100, 0, 160) if sanity.is_critical else \
                 (140, 0, 200) if sanity.sanity < 50 else (80, 60, 120)
        if fill_w > 0:
            pygame.draw.rect(self.screen, col,
                             (bar_x, bar_y, fill_w, bar_h))
        pygame.draw.rect(self.screen, (50, 50, 50),
                         (bar_x, bar_y, bar_w, bar_h), 1)

    def _draw_flashlight_status(self, fl):
        color_map = {
            "ON":       (0, 200, 80),
            "OFF":      (60, 60, 60),
            "DEAD":     (100, 0, 0),
            "OVERHEAT": (220, 80, 0),
            "UNSTABLE": AMBER,
        }
        txt = self.font_small.render(
            f"[ F ] FLASHLIGHT: {fl.status_label}",
            True, color_map.get(fl.status_label, WHITE)
        )
        self.screen.blit(txt, (12, 150))

    def _draw_tower_count(self, sig):
        txt = self.font_small.render(
            f"TOWERS: {sig.towers_active} / {sig.total_towers}",
            True, (80, 80, 80)
        )
        self.screen.blit(txt, (12, 166))

    def _draw_signal_status(self, sig):
        txt = self.font_med.render(sig.status_label, True, sig.status_color)
        self.screen.blit(txt, (SCREEN_WIDTH - txt.get_width() - 12, 12))

    def _draw_alert_indicator(self):
        txt = self.font_small.render(
            "// SOUND DETECTED //", True, (180, 80, 0)
        )
        self.screen.blit(txt, (
            SCREEN_WIDTH - txt.get_width() - 12, 35
        ))

    def _draw_heartbeat(self, heartbeat):
        alpha  = int(heartbeat.intensity * 60)
        surf   = pygame.Surface(
            (SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA
        )
        pygame.draw.rect(
            surf, (180, 0, 0, alpha),
            pygame.Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT), 25
        )
        self.screen.blit(surf, (0, 0))

    def _draw_hallucination(self, message):
        if not message:
            return
        font = pygame.font.SysFont("consolas", 15)
        txt  = font.render(message, True, (120, 0, 160))
        x    = SCREEN_WIDTH  // 2 - txt.get_width()  // 2
        y    = SCREEN_HEIGHT // 2 + 80
        if random.random() > 0.05:
            offset = random.randint(-3, 3)
            self.screen.blit(txt, (x + offset, y))

    def _draw_glitch_overlay(self, sig):
        if random.random() > 0.15:
            return
        intensity = 1.0 - (sig.stability / SIGNAL_CRIT_THRESH)
        for _ in range(int(intensity * 6)):
            y = random.randint(0, SCREEN_HEIGHT)
            h = random.randint(1, 4)
            offset = random.randint(-8, 8)
            try:
                strip = self.screen.subsurface(
                    pygame.Rect(0, max(0, y), SCREEN_WIDTH,
                                min(h, SCREEN_HEIGHT - max(0, y)))
                ).copy()
                self.screen.blit(strip, (offset, y))
            except:
                pass

    def _draw_blackout_warning(self):
        txt = self.font_large.render(
            "// SIGNAL LOST //", True, DANGER_RED
        )
        x = SCREEN_WIDTH  // 2 - txt.get_width()  // 2
        y = SCREEN_HEIGHT // 2 - txt.get_height() // 2
        if random.random() > 0.3:
            self.screen.blit(txt, (x, y))