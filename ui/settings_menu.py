import pygame
from settings import *


class SettingsMenu:
    def __init__(self, screen):
        self.screen   = screen
        self.active   = False
        self.selected = 0

        self.font_title = pygame.font.SysFont("consolas", 20, bold=True)
        self.font_opt   = pygame.font.SysFont("consolas", 16)
        self.font_small = pygame.font.SysFont("consolas", 13)

        # Settings values
        self.settings = {
            "Flashlight Drain": ["Slow", "Normal", "Fast"],
            "Signal Decay":     ["Slow", "Normal", "Fast"],
            "Enemy Speed":      ["Slow", "Normal", "Fast"],
            "Darkness":         ["Low",  "Medium", "High"],
        }
        self.values = {k: 1 for k in self.settings}  # default Normal/Medium
        self.keys   = list(self.settings.keys())

    def handle_input(self, key):
        if key == pygame.K_ESCAPE:
            self.active = False
        elif key == pygame.K_w or key == pygame.K_UP:
            self.selected = (self.selected - 1) % len(self.keys)
        elif key == pygame.K_s or key == pygame.K_DOWN:
            self.selected = (self.selected + 1) % len(self.keys)
        elif key == pygame.K_a or key == pygame.K_LEFT:
            k = self.keys[self.selected]
            self.values[k] = max(0, self.values[k] - 1)
            self._apply()
        elif key == pygame.K_d or key == pygame.K_RIGHT:
            k = self.keys[self.selected]
            self.values[k] = min(
                len(self.settings[k]) - 1, self.values[k] + 1
            )
            self._apply()

    def _apply(self):
        global FLASHLIGHT_DRAIN_RATE, SIGNAL_DECAY_RATE
        global WATCHER_SPEED_DARK, WATCHER_SPEED_FLICKER

        import settings as s

        drain_map = {"Slow": 1.0, "Normal": 2.5, "Fast": 5.0}
        decay_map = {"Slow": 0.5, "Normal": 1.2, "Fast": 2.5}
        speed_map = {"Slow": 80,  "Normal": 140, "Fast": 200}

        s.FLASHLIGHT_DRAIN_RATE  = drain_map[
            self.settings["Flashlight Drain"][self.values["Flashlight Drain"]]
        ]
        s.SIGNAL_DECAY_RATE      = decay_map[
            self.settings["Signal Decay"][self.values["Signal Decay"]]
        ]
        s.WATCHER_SPEED_DARK     = speed_map[
            self.settings["Enemy Speed"][self.values["Enemy Speed"]]
        ]
        s.WATCHER_SPEED_FLICKER  = s.WATCHER_SPEED_DARK * 0.4

    def draw(self):
        # Dark overlay
        overlay = pygame.Surface(
            (SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA
        )
        overlay.fill((0, 0, 0, 200))
        self.screen.blit(overlay, (0, 0))

        # Panel
        panel_w = 420
        panel_h = 280
        panel_x = SCREEN_WIDTH  // 2 - panel_w // 2
        panel_y = SCREEN_HEIGHT // 2 - panel_h // 2

        pygame.draw.rect(self.screen, (10, 10, 10),
                         (panel_x, panel_y, panel_w, panel_h))
        pygame.draw.rect(self.screen, (80, 0, 0),
                         (panel_x, panel_y, panel_w, panel_h), 1)

        # Title
        title = self.font_title.render("// SETTINGS //", True, (180, 0, 0))
        self.screen.blit(title, (
            panel_x + panel_w // 2 - title.get_width() // 2,
            panel_y + 15
        ))

        # Options
        y = panel_y + 55
        for i, key in enumerate(self.keys):
            val_idx  = self.values[key]
            val_str  = self.settings[key][val_idx]
            selected = i == self.selected

            name_color = (200, 200, 200) if selected else (80, 80, 80)
            val_color  = (0, 200, 80)    if selected else (60, 60, 60)

            prefix = ">  " if selected else "   "
            name   = self.font_opt.render(f"{prefix}{key}", True, name_color)
            val    = self.font_opt.render(
                f"< {val_str} >", True, val_color
            )

            self.screen.blit(name, (panel_x + 20, y))
            self.screen.blit(val,  (
                panel_x + panel_w - val.get_width() - 20, y
            ))
            y += 40

        # Hint
        hint = self.font_small.render(
            "A/D  change        ESC  close", True, (40, 40, 40)
        )
        self.screen.blit(hint, (
            panel_x + panel_w // 2 - hint.get_width() // 2,
            panel_y + panel_h - 25
        ))