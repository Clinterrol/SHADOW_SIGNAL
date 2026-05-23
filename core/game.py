import pygame
from settings import *


class Game:
    def __init__(self, screen, clock):
        self.screen     = screen
        self.clock      = clock
        self.state      = STATE_TITLE
        self.running    = True
        self.dt         = 0.0

        self.player     = None
        self.tilemap    = None
        self.camera     = None
        self.renderer   = None
        self.flashlight = None
        self.signal_sys = None
        self.hud        = None
        self._menu      = None
        self.towers     = []
        self.items      = []
        self.watchers   = []
        self.event_sys  = None
        self.glitch_fx  = None

    def show_title(self):
        from ui.menu import MainMenu
        self.state = STATE_TITLE
        self._menu = MainMenu(self.screen)

    def new_game(self):
        from entities.player       import Player
        from entities.item         import Item
        from entities.watcher      import Watcher
        from world.tilemap         import Tilemap
        from world.signal_tower    import SignalTower
        from core.camera           import Camera
        from core.renderer         import Renderer
        from systems.flashlight    import Flashlight
        from systems.signal_system import SignalSystem
        from systems.event_system  import EventSystem
        from ui.hud                import HUD
        from ui.glitch_fx          import GlitchFX

        self.tilemap    = Tilemap()
        self.player     = Player(self, 3, 3)
        self.camera     = Camera(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.renderer   = Renderer(self.screen)
        self.flashlight = Flashlight()
        self.signal_sys = SignalSystem()
        self.event_sys  = EventSystem(self)
        self.hud        = HUD(self.screen)
        self.glitch_fx  = GlitchFX(self.screen)

        self.towers = [
            SignalTower(c, r)
            for c, r in self.tilemap.get_tower_positions()
        ]
        self.signal_sys.total_towers = len(self.towers)

        self.items = [
            Item("battery", 6,  2),
            Item("medkit",  10, 5),
            Item("battery", 18, 10),
            Item("medkit",  20, 3),
            Item("battery", 3,  11),
        ]

        self.watchers = [
            Watcher(20, 12),
            Watcher(22, 2),
        ]

        self.state = STATE_PLAYING

    def run(self):
        while self.running:
            self.dt = self.clock.tick(FPS) / 1000.0
            self._handle_events()
            self._update()
            self._draw()

    def _handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN:
                self._on_keydown(event.key)

    def _on_keydown(self, key):
        if self.state == STATE_TITLE:
            if key == pygame.K_ESCAPE:
                self.running = False
            elif key == pygame.K_RETURN:
                if self._menu.selected == 0:
                    self.new_game()
                elif self._menu.selected == 2:
                    self.running = False
            else:
                self._menu.handle_input(key)

        elif self.state == STATE_PLAYING:
            if key == pygame.K_ESCAPE:
                self.state = STATE_PAUSED
            if key == pygame.K_f:
                self.flashlight.toggle()
            if key == pygame.K_e:
                self._try_interact()

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

    def _try_interact(self):
        for tower in self.towers:
            if not tower.active and tower.is_near(self.player.rect):
                tower.activate()
                self.signal_sys.activate_tower(boost=25.0)
                if self.signal_sys.towers_active >= self.signal_sys.total_towers:
                    self.state = STATE_WIN
                return

    def _update(self):
        if self.state != STATE_PLAYING:
            return

        self.player.update(self.dt, self.tilemap)
        self.camera.update(self.player)
        self.flashlight.update(self.dt, self.signal_sys.stability)
        self.signal_sys.update(self.dt)
        self.event_sys.update(self.dt)

        for tower in self.towers:
            tower.update(self.dt)

        for watcher in self.watchers:
            watcher.update(
                self.dt, self.player,
                self.flashlight, self.signal_sys, self.tilemap
            )
            if watcher.touches_player(self.player):
                self.player.take_damage(1)

        self._check_items()

        if self.player.health <= 0:
            self.state = STATE_GAMEOVER

    def _check_items(self):
        for item in self.items[:]:
            if item.active and self.player.rect.colliderect(item.rect):
                if item.kind == "battery":
                    self.flashlight.add_battery(30)
                elif item.kind == "medkit":
                    self.player.heal(30)
                item.active = False
                self.items.remove(item)

    def _draw(self):
        self.screen.fill(BLACK)

        if self.state == STATE_TITLE:
            self._menu.draw()

        elif self.state == STATE_PLAYING:
            self.renderer.draw_map(self.tilemap, self.camera)
            self.renderer.draw_towers(self.towers, self.camera)
            self.renderer.draw_items(self.items, self.camera)
            self.renderer.draw_entities(self.watchers, self.camera)
            self.renderer.draw_player(self.player, self.camera)
            self.renderer.draw_flashlight(
                self.player, self.camera, self.flashlight
            )
            self.glitch_fx.draw(self.signal_sys, self.event_sys)
            self.hud.draw(self.flashlight, self.signal_sys, self.player)
            self._draw_interact_hint()
            self._draw_watcher_warning()

        elif self.state == STATE_PAUSED:
            self.renderer.draw_map(self.tilemap, self.camera)
            self.renderer.draw_towers(self.towers, self.camera)
            self.renderer.draw_items(self.items, self.camera)
            self.renderer.draw_entities(self.watchers, self.camera)
            self.renderer.draw_player(self.player, self.camera)
            self._draw_pause()

        elif self.state == STATE_GAMEOVER:
            self._draw_gameover()

        elif self.state == STATE_WIN:
            self._draw_win()

        pygame.display.flip()

    def _draw_interact_hint(self):
        for tower in self.towers:
            if not tower.active and tower.is_near(self.player.rect):
                font = pygame.font.SysFont("consolas", 13)
                txt  = font.render(
                    "[ E ] REPAIR SIGNAL TOWER", True, (0, 180, 60)
                )
                self.screen.blit(txt, (
                    SCREEN_WIDTH  // 2 - txt.get_width()  // 2,
                    SCREEN_HEIGHT - 40
                ))
                return

    def _draw_watcher_warning(self):
        for watcher in self.watchers:
            if not watcher.alive:
                continue
            dist = watcher._distance_to(self.player)
            if dist < WATCHER_DETECT_RANGE * 1.5:
                font  = pygame.font.SysFont("consolas", 12)
                alpha = int(255 * (1 - dist / (WATCHER_DETECT_RANGE * 1.5)))
                txt   = font.render("// PRESENCE DETECTED //", True, (180, 0, 0))
                surf  = pygame.Surface(txt.get_size(), pygame.SRCALPHA)
                surf.fill((0, 0, 0, 0))
                surf.blit(txt, (0, 0))
                surf.set_alpha(alpha)
                self.screen.blit(surf, (
                    SCREEN_WIDTH  // 2 - txt.get_width()  // 2,
                    SCREEN_HEIGHT - 60
                ))
                return

    def _draw_pause(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        self.screen.blit(overlay, (0, 0))
        font = pygame.font.SysFont("consolas", 36, bold=True)
        sub  = pygame.font.SysFont("consolas", 14)
        txt  = font.render("// PAUSED", True, (180, 0, 0))
        hint = sub.render("[ ESC ] RESUME        [ Q ] QUIT",
                          True, (60, 60, 60))
        self.screen.blit(txt, txt.get_rect(
            center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 20)))
        self.screen.blit(hint, hint.get_rect(
            center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 30)))

    def _draw_gameover(self):
        self.screen.fill((5, 0, 0))
        font = pygame.font.SysFont("consolas", 52, bold=True)
        sub  = pygame.font.SysFont("consolas", 14)
        txt  = font.render("YOU DIED", True, (180, 0, 0))
        hint = sub.render("[ R ] RETRY        [ ESC ] TITLE",
                          True, (60, 60, 60))
        self.screen.blit(txt, txt.get_rect(
            center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 20)))
        self.screen.blit(hint, hint.get_rect(
            center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 40)))

    def _draw_win(self):
        self.screen.fill((0, 5, 0))
        font = pygame.font.SysFont("consolas", 44, bold=True)
        sub  = pygame.font.SysFont("consolas", 14)
        txt  = font.render("SIGNAL RESTORED", True, (0, 180, 60))
        hint = sub.render("[ R ] PLAY AGAIN        [ ESC ] TITLE",
                          True, (60, 60, 60))
        self.screen.blit(txt, txt.get_rect(
            center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 20)))
        self.screen.blit(hint, hint.get_rect(
            center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 40)))