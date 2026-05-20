import pygame
import random
from settings import *


class HUD:
    def __init__(self, screen):
        self.screen     = screen
        self.font_small = pygame.font.SysFont("consolas", 13)
        self.font_med   = pygame.font.SysFont("consolas", 16, bold=True)
        self.font_large = pygame.font.SysFont("consolas", 22, bold=True)

        # Glitch effect state
        self._glitch_timer    = 0.0
        self._glitch_active   = False
        self._glitch_offset   = 0

    # ── Main Draw ───────────────────────────────────
    def draw(self, flashlight, signal_sys, player):
        self._draw_signal_bar(signal_sys)
        self._draw_battery_bar(flashlight)
        self._draw_health_bar(player)
        self._draw_flashlight_status(flashlight)
        self._draw_tower_count(signal_sys)
        self._draw_signal_status(signal_sys)

        # Glitch overlay when critical
        if signal_sys.is_critical:
            self._draw_glitch_overlay(signal_sys)

        # Blackout warning
        if signal_sys.is_blackout:
            self._draw_blackout_warning()

    # ── Signal Bar ──────────────────────────────────
    def _draw_signal_bar(self, signal_sys):
        label = self.font_small.render("SIGNAL", True, (100, 100, 100))
        self.screen.blit(label, (12, 12))

        bar_x, bar_y = 12, 28
        bar_w, bar_h = 160, 12

        # Background
        pygame.draw.rect(self.screen, (20, 20, 20),
                         (bar_x, bar_y, bar_w, bar_h))

        # Fill
        fill_w = int(bar_w * signal_sys.stability_pct)
        color  = signal_sys.status_color
        if fill_w > 0:
            pygame.draw.rect(self.screen, color,
                             (bar_x, bar_y, fill_w, bar_h))

        # Flicker effect on bar when unstable
        if signal_sys.lights_flickering:
            flicker_surf = pygame.Surface((fill_w, bar_h), pygame.SRCALPHA)
            flicker_surf.fill((255, 255, 255, random.randint(10, 40)))
            self.screen.blit(flicker_surf, (bar_x, bar_y))

        # Border
        pygame.draw.rect(self.screen, (50, 50, 50),
                         (bar_x, bar_y, bar_w, bar_h), 1)

        # Percentage text
        pct_txt = self.font_small.render(
            f"{int(signal_sys.stability)}%", True, (80, 80, 80)
        )
        self.screen.blit(pct_txt, (bar_x + bar_w + 6, bar_y))

    # ── Battery Bar ─────────────────────────────────
    def _draw_battery_bar(self, flashlight):
        label = self.font_small.render("BATTERY", True, (100, 100, 100))
        self.screen.blit(label, (12, 48))

        bar_x, bar_y = 12, 64
        bar_w, bar_h = 160, 10

        pygame.draw.rect(self.screen, (20, 20, 20),
                         (bar_x, bar_y, bar_w, bar_h))

        fill_w = int(bar_w * flashlight.battery_pct)
        color  = self._battery_color(flashlight.battery_pct)
        if fill_w > 0:
            pygame.draw.rect(self.screen, color,
                             (bar_x, bar_y, fill_w, bar_h))

        pygame.draw.rect(self.screen, (50, 50, 50),
                         (bar_x, bar_y, bar_w, bar_h), 1)

        pct_txt = self.font_small.render(
            f"{int(flashlight.battery)}%", True, (80, 80, 80)
        )
        self.screen.blit(pct_txt, (bar_x + bar_w + 6, bar_y))

        # Heat warning bar
        if flashlight.heat_pct > 0.1:
            self._draw_heat_bar(flashlight)

    def _battery_color(self, pct):
        if pct > 0.5:
            return AMBER
        elif pct > 0.25:
            return (200, 120, 0)
        else:
            return DANGER_RED

    def _draw_heat_bar(self, flashlight):
        label = self.font_small.render("HEAT", True, (100, 50, 50))
        self.screen.blit(label, (12, 80))

        bar_x, bar_y = 12, 94
        bar_w, bar_h = 160, 6

        pygame.draw.rect(self.screen, (20, 20, 20),
                         (bar_x, bar_y, bar_w, bar_h))

        fill_w = int(bar_w * flashlight.heat_pct)
        heat_color = (
            int(255 * flashlight.heat_pct),
            int(60 * (1 - flashlight.heat_pct)),
            0
        )
        if fill_w > 0:
            pygame.draw.rect(self.screen, heat_color,
                             (bar_x, bar_y, fill_w, bar_h))

        pygame.draw.rect(self.screen, (50, 50, 50),
                         (bar_x, bar_y, bar_w, bar_h), 1)

    # ── Health Bar ──────────────────────────────────
    def _draw_health_bar(self, player):
        label = self.font_small.render("HEALTH", True, (100, 100, 100))
        self.screen.blit(label, (12, 108))

        bar_x, bar_y = 12, 124
        bar_w, bar_h = 160, 10

        pygame.draw.rect(self.screen, (20, 20, 20),
                         (bar_x, bar_y, bar_w, bar_h))

        hp_pct = player.health / PLAYER_MAX_HEALTH
        fill_w = int(bar_w * hp_pct)
        color  = self._health_color(hp_pct)

        if fill_w > 0:
            pygame.draw.rect(self.screen, color,
                             (bar_x, bar_y, fill_w, bar_h))

        pygame.draw.rect(self.screen, (50, 50, 50),
                         (bar_x, bar_y, bar_w, bar_h), 1)

        hp_txt = self.font_small.render(
            f"{player.health}", True, (80, 80, 80)
        )
        self.screen.blit(hp_txt, (bar_x + bar_w + 6, bar_y))

    def _health_color(self, pct):
        if pct > 0.6:
            return (0, 180, 60)
        elif pct > 0.3:
            return AMBER
        else:
            return DANGER_RED

    # ── Flashlight Status ───────────────────────────
    def _draw_flashlight_status(self, flashlight):
        color_map = {
            "ON":       (0, 200, 80),
            "OFF":      (60, 60, 60),
            "DEAD":     (100, 0, 0),
            "OVERHEAT": (220, 80, 0),
            "UNSTABLE": AMBER,
        }
        label  = flashlight.status_label
        color  = color_map.get(label, WHITE)
        txt    = self.font_small.render(
            f"[ F ] FLASHLIGHT: {label}", True, color
        )
        self.screen.blit(txt, (12, 145))

    # ── Tower Count ─────────────────────────────────
    def _draw_tower_count(self, signal_sys):
        txt = self.font_small.render(
            f"TOWERS: {signal_sys.towers_active} / {signal_sys.total_towers}",
            True, (80, 80, 80)
        )
        self.screen.blit(txt, (12, 162))

    # ── Signal Status Label ─────────────────────────
    def _draw_signal_status(self, signal_sys):
        label = signal_sys.status_label
        color = signal_sys.status_color
        txt   = self.font_med.render(label, True, color)
        # Top right corner
        x = SCREEN_WIDTH - txt.get_width() - 12
        self.screen.blit(txt, (x, 12))

    # ── Glitch Overlay ──────────────────────────────
    def _draw_glitch_overlay(self, signal_sys):
        """
        Horizontal scanline displacement when signal is critical.
        Intensity scales with how low signal is.
        """
        if random.random() > 0.15:
            return

        intensity = 1.0 - (signal_sys.stability / SIGNAL_CRIT_THRESH)
        num_lines = int(intensity * 6)

        for _ in range(num_lines):
            y      = random.randint(0, SCREEN_HEIGHT)
            h      = random.randint(1, 4)
            offset = random.randint(-8, 8)
            strip  = self.screen.subsurface(
                pygame.Rect(0, max(0, y), SCREEN_WIDTH, min(h, SCREEN_HEIGHT - y))
            ).copy()
            self.screen.blit(strip, (offset, y))

    # ── Blackout Warning ────────────────────────────
    def _draw_blackout_warning(self):
        txt = self.font_large.render(
            "// SIGNAL LOST //", True, DANGER_RED
        )
        x = SCREEN_WIDTH  // 2 - txt.get_width()  // 2
        y = SCREEN_HEIGHT // 2 - txt.get_height() // 2
        # Flicker the warning
        if random.random() > 0.3:
            self.screen.blit(txt, (x, y))

    # ── Controls Hint ───────────────────────────────
    def draw_controls(self):
        """Optional — toggle in settings later."""
        hints = [
            "WASD  move",
            "SHIFT sprint",
            "CTRL  crouch",
            "F     flashlight",
            "E     interact",
            "ESC   pause",
        ]
        y = SCREEN_HEIGHT - (len(hints) * 16) - 10
        for hint in hints:
            txt = self.font_small.render(hint, True, (45, 45, 45))
            self.screen.blit(txt, (12, y))
            y += 16