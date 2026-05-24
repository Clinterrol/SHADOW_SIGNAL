import pygame
from settings import *


class LoreDisplay:
    def __init__(self, screen):
        self.screen   = screen
        self.active   = False
        self.title    = ""
        self.content  = ""
        self._timer   = 0.0
        self._duration = 6.0

        self.font_title   = pygame.font.SysFont("consolas", 16, bold=True)
        self.font_content = pygame.font.SysFont("consolas", 13)
        self.font_hint    = pygame.font.SysFont("consolas", 11)

    def show(self, title, content):
        self.active  = True
        self.title   = title
        self.content = content
        self._timer  = 0.0

    def update(self, dt):
        if not self.active:
            return
        self._timer += dt
        if self._timer >= self._duration:
            self.active = False

    def draw(self):
        if not self.active:
            return

        # Fade in/out
        if self._timer < 0.5:
            alpha = int(255 * (self._timer / 0.5))
        elif self._timer > self._duration - 0.5:
            alpha = int(255 * (
                (self._duration - self._timer) / 0.5
            ))
        else:
            alpha = 255

        # Panel
        panel_w = 500
        panel_h = 120
        panel_x = SCREEN_WIDTH  // 2 - panel_w // 2
        panel_y = SCREEN_HEIGHT - panel_h - 20

        panel = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
        panel.fill((5, 5, 5, 200))
        pygame.draw.rect(panel, (100, 80, 0, alpha), (0, 0, panel_w, panel_h), 1)

        # Title
        title_surf = self.font_title.render(
            f"// {self.title} //", True, (200, 160, 0)
        )
        panel.blit(title_surf, (12, 10))

        # Content — word wrap
        words   = self.content.split()
        lines   = []
        current = ""
        for word in words:
            test = current + word + " "
            if self.font_content.size(test)[0] > panel_w - 24:
                lines.append(current)
                current = word + " "
            else:
                current = test
        lines.append(current)

        y_offset = 35
        for line in lines[:4]:
            line_surf = self.font_content.render(
                line.strip(), True, (160, 140, 100)
            )
            panel.blit(line_surf, (12, y_offset))
            y_offset += 18

        # Hint
        hint = self.font_hint.render(
            "[ reading... ]", True, (60, 60, 60)
        )
        panel.blit(hint, (panel_w - hint.get_width() - 12, panel_h - 18))

        panel.set_alpha(alpha)
        self.screen.blit(panel, (panel_x, panel_y))