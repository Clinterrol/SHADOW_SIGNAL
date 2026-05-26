import pygame
import os
from settings import *


class MainMenu:
    def __init__(self, screen, sound_manager=None):
        self.screen        = screen
        self.selected      = 0
        self.font_big      = pygame.font.SysFont("consolas", 52, bold=True)
        self.font_med      = pygame.font.SysFont("consolas", 20)
        self.font_small    = pygame.font.SysFont("consolas", 13)
        self.sound_manager = sound_manager

        has_save     = os.path.exists("saves/save_data.json")
        self.options = (
            ['CONTINUE', 'NEW GAME', 'SETTINGS', 'QUIT']
            if has_save else
            ['NEW GAME', 'SETTINGS', 'QUIT']
        )
        self.has_save = has_save

        # Load background image
        # File: assets/images/menu_bg.png
        bg_path = "assets/images/menu_bg.png"
        if os.path.exists(bg_path):
            raw      = pygame.image.load(bg_path).convert()
            self._bg = pygame.transform.scale(raw, (SCREEN_WIDTH, SCREEN_HEIGHT))
        else:
            self._bg = None

        # Subtle dark overlay — keeps background visible
        self._overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        self._overlay.fill((0, 0, 0, 100))

        if self.sound_manager:
            self.sound_manager.play_music("menu_music", volume=0.4)

    def handle_input(self, key):
        if key in (pygame.K_w, pygame.K_UP):
            self.selected = (self.selected - 1) % len(self.options)
            if self.sound_manager:
                self.sound_manager.play("menu_hover", volume=0.6)
        elif key in (pygame.K_s, pygame.K_DOWN):
            self.selected = (self.selected + 1) % len(self.options)
            if self.sound_manager:
                self.sound_manager.play("menu_hover", volume=0.6)

    def on_select(self):
        if self.sound_manager:
            self.sound_manager.play("menu_hover", volume=0.8)

    def get_selected(self):
        return self.options[self.selected]

    def draw(self):
        # Background
        if self._bg:
            self.screen.blit(self._bg, (0, 0))
        else:
            self.screen.fill((5, 5, 5))

        # Subtle overlay
        self.screen.blit(self._overlay, (0, 0))

        # Title
        shadow = self.font_big.render("SHADOW SIGNAL", True, (60, 0, 0))
        self.screen.blit(shadow, shadow.get_rect(
            center=(SCREEN_WIDTH // 2 + 2, SCREEN_HEIGHT // 2 - 48 + 2)))

        title = self.font_big.render("SHADOW SIGNAL", True, (140, 0, 0))
        self.screen.blit(title, title.get_rect(
            center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 48)))

        # Subtitle
        sub = self.font_small.render(
            "UNDERGROUND RESEARCH FACILITY  -  SIGNAL LOST",
            True, (80, 60, 60)
        )
        self.screen.blit(sub, sub.get_rect(
            center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 5)))

        # Menu options
        for i, option in enumerate(self.options):
            if i == self.selected:
                text  = f">  {option}"
                color = (220, 220, 220)
                bar   = pygame.Surface((300, 30), pygame.SRCALPHA)
                bar.fill((120, 0, 0, 60))
                self.screen.blit(bar, bar.get_rect(
                    center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 60 + i * 38)))
            else:
                text  = f"   {option}"
                color = (100, 80, 80)
            opt = self.font_med.render(text, True, color)
            self.screen.blit(opt, opt.get_rect(
                center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 60 + i * 38)))

        # Controls hint
        hint = self.font_small.render(
            "W / S   NAVIGATE        ENTER   SELECT",
            True, (40, 30, 30)
        )
        self.screen.blit(hint, hint.get_rect(
            center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 28)))

        # Version
        ver = self.font_small.render("BUILD 0.1", True, (30, 20, 20))
        self.screen.blit(ver, (SCREEN_WIDTH - 90, SCREEN_HEIGHT - 18))