import pygame
import os
from settings import *


class MainMenu:
    def __init__(self, screen):
        self.screen    = screen
        self.selected  = 0
        self.font_big   = pygame.font.SysFont("consolas", 64, bold=True)
        self.font_med   = pygame.font.SysFont("consolas", 18)
        self.font_small = pygame.font.SysFont("consolas", 13)

        # Options depend on whether save exists
        has_save      = os.path.exists("saves/save_data.json")
        self.options  = (
            ['CONTINUE', 'NEW GAME', 'SETTINGS', 'QUIT']
            if has_save else
            ['NEW GAME', 'SETTINGS', 'QUIT']
        )
        self.has_save = has_save

    def handle_input(self, key):
        if key == pygame.K_w or key == pygame.K_UP:
            self.selected = (self.selected - 1) % len(self.options)
        elif key == pygame.K_s or key == pygame.K_DOWN:
            self.selected = (self.selected + 1) % len(self.options)

    def get_selected(self):
        return self.options[self.selected]

    def draw(self):
        self.screen.fill((5, 5, 5))

        pygame.draw.rect(self.screen, (120, 0, 0),
                         (60, SCREEN_HEIGHT//2 - 90,
                          SCREEN_WIDTH - 120, 2))

        title = self.font_big.render("SHADOW SIGNAL", True, (180, 0, 0))
        self.screen.blit(title, title.get_rect(
            center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 50)))

        sub = self.font_small.render(
            "UNDERGROUND RESEARCH FACILITY  //  SIGNAL LOST",
            True, (60, 60, 60)
        )
        self.screen.blit(sub, sub.get_rect(
            center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 10)))

        pygame.draw.rect(self.screen, (80, 0, 0),
                         (60, SCREEN_HEIGHT//2 + 28,
                          SCREEN_WIDTH - 120, 1))

        for i, option in enumerate(self.options):
            if i == self.selected:
                text  = f">  {option}"
                color = (200, 200, 200)
            else:
                text  = f"   {option}"
                color = (60, 60, 60)
            opt = self.font_med.render(text, True, color)
            self.screen.blit(opt, opt.get_rect(
                center=(SCREEN_WIDTH//2,
                        SCREEN_HEIGHT//2 + 60 + i * 35)))

        hint = self.font_small.render(
            "W/S  NAVIGATE        ENTER  SELECT",
            True, (35, 35, 35)
        )
        self.screen.blit(hint, hint.get_rect(
            center=(SCREEN_WIDTH//2, SCREEN_HEIGHT - 30)))

        ver = self.font_small.render(
            "BUILD 0.1  //  PHASE 6", True, (25, 25, 25)
        )
        self.screen.blit(ver, (SCREEN_WIDTH - 180, SCREEN_HEIGHT - 18))
