from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
from settings import *
from core.game import Game

game = None

def update():
    game.update()
    if game.state == STATE_PLAYING and game.hud:
        game.hud.update()
    if game.state == STATE_TITLE and hasattr(game, '_menu') and game._menu:
        game._menu.update()
    if game.state == STATE_PLAYING and game.player:
        game.player.update()

def input(key):
    game.input(key)

def main():
    global game
    app = Ursina(
        title          = TITLE,
        borderless     = False,
        fullscreen     = False,
        size           = (SCREEN_WIDTH, SCREEN_HEIGHT),
        vsync          = True,
        development_mode = False  # ← removes debug numbers
    )

    Text.default_font = 'times.ttf'  # ← clean font, copy times.ttf to project folder

    window.fps_counter.enabled = False  # ← hides FPS
    window.exit_button.visible = False

    game = Game(app)
    game.show_title()

    app.run()

if __name__ == '__main__':
    main()