from ursina import *


class MainMenu:
    def __init__(self, game):
        self.game      = game
        self._buttons  = []
        self._entities = []
        self._build()

    def _build(self):
        mouse.locked  = False
        mouse.visible = True

        # Background
        self._add(Entity(
            parent  = camera.ui,
            model   = 'quad',
            scale   = (2, 2),
            color   = color.black,
            z       = 2
        ))

        # Title — centered
        self._add(Text(
            text     = 'SHADOW SIGNAL',
            parent   = camera.ui,
            origin   = (0, 0),
            position = Vec2(0, 0.30),
            scale    = 4.0,
            color    = color.rgb(200, 0, 0),
            z        = 1.5
        ))

        # Subtitle
        self._add(Text(
            text     = 'UNDERGROUND RESEARCH FACILITY  —  SIGNAL LOST',
            parent   = camera.ui,
            origin   = (0, 0),
            position = Vec2(0, 0.14),
            scale    = 0.65,
            color    = color.rgb(80, 80, 80),
            z        = 1.5
        ))

        # Divider
        self._add(Entity(
            parent   = camera.ui,
            model    = 'quad',
            scale    = (0.5, 0.002),
            position = Vec2(0, 0.08),
            color    = color.rgb(80, 0, 0),
            z        = 1.5
        ))

        # Buttons
        self._make_button('START GAME', Vec2(0, -0.05), self._on_start)
        self._make_button('SETTINGS',   Vec2(0, -0.17), self._on_settings)
        self._make_button('QUIT',       Vec2(0, -0.29), self._on_quit)

        # Version
        self._add(Text(
            text     = 'BUILD 0.1  //  PHASE 1',
            parent   = camera.ui,
            origin   = (0, 0),
            position = Vec2(0.60, -0.46),
            scale    = 0.40,
            color    = color.rgb(40, 40, 40),
            z        = 1.5
        ))

    def _add(self, e):
        self._entities.append(e)
        return e

    def _make_button(self, label, pos, action):
        btn = MenuButton(label, pos, action)
        self._buttons.append(btn)

    def update(self):
        pass

    def _on_start(self):
        self.game.new_game()

    def _on_settings(self):
        print("Settings — Phase 6")

    def _on_quit(self):
        application.quit()

    def destroy(self):
        for btn in self._buttons:
            btn.destroy()
        for e in self._entities:
            destroy(e)


class MenuButton:
    def __init__(self, label, pos, action):
        self.action = action

        # Dark background — invisible until hover
        self.bg = Entity(
            parent   = camera.ui,
            model    = 'quad',
            scale    = (0.46, 0.042),
            position = pos,
            color    = color.rgba(0, 0, 0, 0),
            z        = 1.45
        )

        # Label text
        self.txt = Text(
            text     = label,
            parent   = camera.ui,
            origin   = (0, 0),
            position = Vec2(pos.x, pos.y - 0.004),
            scale    = 1.2,
            color    = color.rgb(130, 130, 130),
            z        = 1.4
        )

        # Clickable area — no Ursina default colors
        self.btn = Button(
            parent          = camera.ui,
            model           = 'quad',
            scale           = (0.46, 0.042),
            position        = Vec2(pos.x, pos.y),
            color           = color.clear,
            highlight_color = color.clear,
            pressed_color   = color.clear,
            z               = 1.3,
            on_click        = self._clicked
        )
        self.btn.on_mouse_enter = self._hover_on
        self.btn.on_mouse_exit  = self._hover_off

    def _hover_on(self):
        self.bg.color  = color.rgb(180, 0, 0)
        self.txt.color = color.white

    def _hover_off(self):
        self.bg.color  = color.rgba(0, 0, 0, 0)
        self.txt.color = color.rgb(130, 130, 130)

    def _clicked(self):
        self.action()

    def destroy(self):
        destroy(self.bg)
        destroy(self.txt)
        destroy(self.btn)