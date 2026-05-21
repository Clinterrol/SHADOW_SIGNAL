from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
from settings import *


class Game:
    def __init__(self, app):
        self.app    = app
        self.state  = STATE_TITLE

        # Systems — initialized on new_game()
        self.player      = None
        self.tilemap     = None
        self.flashlight  = None
        self.signal_sys  = None
        self.hud         = None
        self.watcher     = None

        # Scene containers
        self.world_entities = []

        # Lighting
        self.ambient_light   = None
        self.flash_light     = None

        # Title/UI entities cleared on game start
        self._title_entities = []

    # ── Title ───────────────────────────────────────
    def show_title(self):
        self.state = STATE_TITLE
        self._clear_title()
        # Menu built in ui/menu.py — Phase next
        # Placeholder direct start for now
        from ui.menu import MainMenu
        self._menu = MainMenu(self)

    # ── New Game ────────────────────────────────────
    def new_game(self):
        self._clear_title()
        self._setup_scene()
        self._setup_systems()
        self._setup_player()
        self._setup_lighting()
        self.state = STATE_PLAYING

    def _clear_title(self):
        if hasattr(self, '_menu') and self._menu:
            self._menu.destroy()
            self._menu = None

    # ── Scene ───────────────────────────────────────
    def _setup_scene(self):
        from world.tilemap import Tilemap
        self.tilemap = Tilemap()
        self.tilemap.build()

    # ── Systems ─────────────────────────────────────
    def _setup_systems(self):
        from systems.flashlight    import Flashlight
        from systems.signal_system import SignalSystem
        from ui.hud                import HUD

        self.flashlight  = Flashlight()
        self.signal_sys  = SignalSystem()
        self.hud         = HUD(self)

    # ── Player ──────────────────────────────────────
    def _setup_player(self):
        from entities.player import Player
        self.player = Player(self)

    # ── Lighting ────────────────────────────────────
    def _setup_lighting(self):
        # Near-total darkness ambient
        self.ambient_light = AmbientLight(
            color=color.rgb(8, 8, 12)
        )

        # Flashlight as a spotlight on the player
        self.flash_light = SpotLight(
            parent    = camera,
            position  = Vec3(0, 0, 0),
            color     = color.rgb(220, 210, 180),
            shadows   = True
        )
        self.flash_light.look_at(Vec3(0, 0, 1))

    # ── Update ──────────────────────────────────────
    def update(self):
        if self.state != STATE_PLAYING:
            return

        dt = time.dt

        self.flashlight.update(dt, self.signal_sys.stability)
        self.signal_sys.update(dt)

        # Sync spotlight to flashlight state
        self._sync_flashlight()

        # Ambient flicker with signal
        self._update_ambient()

        # Death / blackout checks
        if self.player and self.player.health <= 0:
            self._trigger_gameover()

        if self.signal_sys.is_blackout:
            self._on_blackout()

    def _sync_flashlight(self):
        if not self.flash_light:
            return
        if self.flashlight.is_on and not self.flashlight.overheated:
            self.flash_light.color = color.rgb(220, 210, 180)
        else:
            self.flash_light.color = color.rgb(0, 0, 0)

        # Flicker
        if self.flashlight.is_flickering:
            import random
            self.flash_light.color = color.rgb(
                random.randint(100, 220),
                random.randint(80,  200),
                random.randint(60,  160)
            )

    def _update_ambient(self):
        if not self.ambient_light:
            return
        if self.signal_sys.is_critical:
            import random
            flicker = random.randint(4, 14)
            self.ambient_light.color = color.rgb(flicker, 4, 4)
        else:
            self.ambient_light.color = color.rgb(8, 8, 12)

    # ── End States ──────────────────────────────────
    def _trigger_gameover(self):
        self.state = STATE_GAMEOVER
        self.hud.show_gameover()

    def _on_blackout(self):
        # Phase 3 — enemies fully released
        # Phase 4 — horror events trigger
        pass

    def _trigger_win(self):
        self.state = STATE_WIN
        self.hud.show_win()

    # ── Input ───────────────────────────────────────
    def input(self, key):
        if self.state == STATE_PLAYING:
            if key == 'f':
                self.flashlight.toggle()
            if key == 'escape':
                self._toggle_pause()
            if key == 'e':
                self._try_interact()

        elif self.state == STATE_PAUSED:
            if key == 'escape':
                self._toggle_pause()

        elif self.state in (STATE_GAMEOVER, STATE_WIN):
            if key == 'r':
                self.new_game()
            if key == 'escape':
                self.show_title()

    def _toggle_pause(self):
        if self.state == STATE_PLAYING:
            self.state = STATE_PAUSED
            mouse.locked = False
            if self.player:
                self.player.controller.enabled = False
        else:
            self.state = STATE_PLAYING
            mouse.locked = True
            if self.player:
                self.player.controller.enabled = True

    def _try_interact(self):
        # Phase 5 — signal towers, doors, lore notes
        pass