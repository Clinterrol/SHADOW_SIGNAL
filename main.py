import pygame
import sys
from settings import *
from core.game import Game


def main():
    pygame.init()
    pygame.mixer.init()
    pygame.display.set_caption(TITLE)

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock  = pygame.time.Clock()

    game = Game(screen, clock)
    game.show_title()
    game.run()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
