import pygame
from settings import *


class Game:
    def __init__(self, screen, clock):
        self.screen  = screen
        self.clock   = clock
        self.state   = STATE_TITLE
        self.running = True
        self.dt      = 0.0        # delta time in seconds

        # These get initialized when game actually starts
        self.player   = None
        self.tilemap  = None
        self.camera   = None
        self.hud      = None
        self.flashlight  = None
        self.signal_sys  = None

    # ── Boot ────────────────────────────────────────
    def new_game(self):
        """Initialize all systems fresh for a new run."""
        from entities.player       import Player
        from world.tilemap         import Tilemap
        from core.camera           import Camera
        from core.renderer         import Renderer
        from systems.flashlight    import Flashlight
        from systems.signal_system import SignalSystem
        from ui.hud                import HUD

        self.tilemap     = Tilemap()
        self.player      = Player(self, 5, 5)        # tile coords
        self.camera      = Camera(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.renderer    = Renderer(self.screen)
        self.flashlight  = Flashlight()
        self.signal_sys  = SignalSystem()
        self.hud         = HUD(self.screen)

        self.state = STATE_PLAYING

    # ── Main Loop ───────────────────────────────────
    def run(self):
        while self.running:
            self.dt = self.clock.tick(FPS) / 1000.0   # seconds
            self._handle_events()
            self._update()
            self._draw()

    # ── Events ──────────────────────────────────────
    def _handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            if event.type == pygame.KEYDOWN:
                self._on_keydown(event.key)

    def _on_keydown(self, key):
        if self.state == STATE_TITLE:
            if key == pygame.K_RETURN:
                self.new_game()
            if key == pygame.K_ESCAPE:
                self.running = False

        elif self.state == STATE_PLAYING:
            if key == pygame.K_ESCAPE:
                self.state = STATE_PAUSED
            if key == pygame.K_f:
                self.flashlight.toggle()

        elif self.state == STATE_PAUSED:
            if key == pygame.K_ESCAPE:
                self.state = STATE_PLAYING
            if key == pygame.K_q:
                self.running = False

        elif self.state in (STATE_GAMEOVER, STATE_WIN):
            if key == pygame.K_r:
                self.new_game()
            if key == pygame.K_ESCAPE:
                self.state = STATE_TITLE

    # ── Update ──────────────────────────────────────
    def _update(self):
        if self.state != STATE_PLAYING:
            return

        # Core systems
        self.player.update(self.dt, self.tilemap)
        self.camera.update(self.player)
        self.flashlight.update(self.dt, self.signal_sys.stability)
        self.signal_sys.update(self.dt)

        # Death check
        if self.player.health <= 0:
            self.state = STATE_GAMEOVER

        # Total blackout check
        if self.signal_sys.stability <= SIGNAL_ZERO_THRESH:
            self._on_total_blackout()

    def _on_total_blackout(self):
        """Called when signal hits 0. Phase 4 will expand this."""
        # For now just crank up danger — enemies fully released
        # Placeholder until Watcher is wired in Phase 3
        pass

    # ── Draw ────────────────────────────────────────
    def _draw(self):
        self.screen.fill(BLACK)

        if self.state == STATE_TITLE:
            self._draw_title()

        elif self.state == STATE_PLAYING:
            self.renderer.draw_map(self.tilemap, self.camera)
            self.renderer.draw_player(self.player, self.camera)
            self.renderer.draw_flashlight(
                self.player, self.camera, self.flashlight
            )
            self.hud.draw(self.flashlight, self.signal_sys, self.player)

        elif self.state == STATE_PAUSED:
            self.renderer.draw_map(self.tilemap, self.camera)
            self.renderer.draw_player(self.player, self.camera)
            self._draw_pause()

        elif self.state == STATE_GAMEOVER:
            self._draw_gameover()

        elif self.state == STATE_WIN:
            self._draw_win()

        pygame.display.flip()

    # ── Static Screens ──────────────────────────────
    def _draw_title(self):
        font_big  = pygame.font.SysFont("consolas", 64, bold=True)
        font_small = pygame.font.SysFont("consolas", 18)

        title = font_big.render("SHADOW SIGNAL", True, (180, 0, 0))
        hint  = font_small.render("[ ENTER ] START    [ ESC ] QUIT", True, (80, 80, 80))

        self.screen.blit(title, title.get_rect(
            center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 40)))
        self.screen.blit(hint,  hint.get_rect(
            center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 40)))

    def _draw_pause(self):
        font = pygame.font.SysFont("consolas", 36, bold=True)
        sub  = pygame.font.SysFont("consolas", 16)

        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        self.screen.blit(overlay, (0, 0))

        txt = font.render("// PAUSED", True, (180, 0, 0))
        hint = sub.render("[ ESC ] RESUME    [ Q ] QUIT", True, (80, 80, 80))

        self.screen.blit(txt,  txt.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 20)))
        self.screen.blit(hint, hint.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 30)))

    def _draw_gameover(self):
        font = pygame.font.SysFont("consolas", 52, bold=True)
        sub  = pygame.font.SysFont("consolas", 16)

        txt  = font.render("YOU DIED", True, (180, 0, 0))
        hint = sub.render("[ R ] RETRY    [ ESC ] TITLE", True, (80, 80, 80))

        self.screen.blit(txt,  txt.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 20)))
        self.screen.blit(hint, hint.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 40)))

    def _draw_win(self):
        font = pygame.font.SysFont("consolas", 48, bold=True)
        sub  = pygame.font.SysFont("consolas", 16)

        txt  = font.render("SIGNAL RESTORED", True, (0, 200, 80))
        hint = sub.render("[ R ] PLAY AGAIN    [ ESC ] TITLE", True, (80, 80, 80))

        self.screen.blit(txt,  txt.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 20)))
        self.screen.blit(hint, hint.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 40)))
