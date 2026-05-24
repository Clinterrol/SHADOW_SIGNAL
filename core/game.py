import pygame
from settings import *


class Game:
    def __init__(self, screen, clock):
        self.screen = screen
        self.clock = clock
        self.state = STATE_TITLE
        self.running = True
        self.dt = 0.0

        self.player = None
        self.tilemap = None
        self.camera = None
        self.renderer = None
        self.flashlight = None
        self.signal_sys = None
        self.hud = None
        self._menu = None
        self.towers = []
        self.items = []
        self.watchers = []
        self.crawlers = []
        self.mimics = []
        self.lore_notes = []
        self.event_sys = None
        self.glitch_fx = None
        self.sanity_sys = None
        self.heartbeat = None
        self.audio_det = None
        self.jumpscare = None
        self.lore_display = None
        self.settings_menu = None
        self.save_manager = None
        self.sprite_manager = None

    def show_title(self):
        from ui.menu import MainMenu
        from saves.save_manager import SaveManager
        self.state = STATE_TITLE
        self._menu = MainMenu(self.screen)
        self.save_manager = SaveManager()

    def new_game(self):
        self._init_systems()
        self.state = STATE_PLAYING

    def continue_game(self):
        self._init_systems()
        if self.save_manager.load(self):
            self.state = STATE_PLAYING
        else:
            self.state = STATE_PLAYING

    def _init_systems(self):
        from entities.player import Player
        from entities.item import Item
        from entities.watcher import Watcher
        from entities.crawler import Crawler
        from entities.mimic import Mimic
        from world.tilemap import Tilemap
        from world.signal_tower import SignalTower
        from world.lore_note import LoreNote
        from world.room import MapLoader
        from core.camera import Camera
        from core.renderer import Renderer
        from systems.flashlight import Flashlight
        from systems.signal_system import SignalSystem
        from systems.event_system import EventSystem
        from systems.audio_detection import AudioDetection
        from systems.sanity import SanitySystem
        from systems.heartbeat import HeartbeatSystem
        from systems.jumpscare import JumpscareSystem
        from ui.hud import HUD
        from ui.glitch_fx import GlitchFX
        from ui.lore_display import LoreDisplay
        from ui.settings_menu import SettingsMenu
        from saves.save_manager import SaveManager
        from core.sprite_manager import SpriteManager

        map_loader = MapLoader("data/rooms.json")

        self.tilemap = Tilemap("data/rooms.json")
        self.camera = Camera(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.renderer = Renderer(self.screen)
        self.sprite_manager = SpriteManager()
        self.sprite_manager.load_all()
        self.flashlight = Flashlight()
        self.signal_sys = SignalSystem()
        self.event_sys = EventSystem(self)
        self.audio_det = AudioDetection()
        self.sanity_sys = SanitySystem()
        self.heartbeat = HeartbeatSystem()
        self.jumpscare = JumpscareSystem(self.screen)
        self.hud = HUD(self.screen)
        self.glitch_fx = GlitchFX(self.screen)
        self.lore_display = LoreDisplay(self.screen)
        self.settings_menu = SettingsMenu(self.screen)
        self.save_manager = SaveManager()
    

        px, py = map_loader.player_spawn
        self.player = Player(self, px, py)

        self.towers = [
            SignalTower(c, r)
            for c, r in self.tilemap.get_tower_positions()
        ]
        self.signal_sys.total_towers = len(self.towers)

        self.items = [
            Item(s["kind"], s["tile_x"], s["tile_y"])
            for s in map_loader.item_spawns
        ]

        self.watchers = [
            Watcher(s["tile_x"], s["tile_y"])
            for s in map_loader.enemy_spawns
        ]

        # Crawlers — spawn in corners
        self.crawlers = [
            Crawler(36, 19),
            Crawler(2, 19),
        ]

        # Mimic — spawns in middle corridor
        self.mimics = [
            Mimic(19, 11),
        ]

        self.lore_notes = [
            LoreNote(note, note["tile_x"], note["tile_y"])
            for note in map_loader.lore_notes
        ]

    def _save_game(self):
        if self.save_manager:
            self.save_manager.save(self)

    def run(self):
        while self.running:
            self.dt = self.clock.tick(FPS) / 1000.0
            self._handle_events()
            self._update()
            self._draw()

    def _handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                if self.state == STATE_PLAYING:
                    self._save_game()
                self.running = False
            if event.type == pygame.KEYDOWN:
                self._on_keydown(event.key)

    def _on_keydown(self, key):
        # Settings menu intercepts input
        if self.settings_menu and self.settings_menu.active:
            self.settings_menu.handle_input(key)
            return

        if self.state == STATE_TITLE:
            if key == pygame.K_ESCAPE:
                self.running = False
            elif key == pygame.K_RETURN:
                selected = self._menu.get_selected()
                if selected == 'CONTINUE':
                    self.continue_game()
                elif selected == 'NEW GAME':
                    self.new_game()
                elif selected == 'SETTINGS':
                    self.settings_menu = __import__(
                        'ui.settings_menu', fromlist=['SettingsMenu']
                    ).SettingsMenu(self.screen)
                    self.settings_menu.active = True
                elif selected == 'QUIT':
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
            if key == pygame.K_F5:
                self._save_game()

        elif self.state == STATE_PAUSED:
            if key == pygame.K_ESCAPE:
                self.state = STATE_PLAYING
            if key == pygame.K_q:
                self._save_game()
                self.running = False
            if key == pygame.K_F5:
                self._save_game()

        elif self.state in (STATE_GAMEOVER, STATE_WIN):
            if key == pygame.K_r:
                self.new_game()
            if key == pygame.K_ESCAPE:
                self.show_title()

    def _try_interact(self):
        for tower in self.towers:
            if not tower.active and tower.is_near(self.player.rect):
                tower.activate()
                self.signal_sys.activate_tower(boost=25.0)
                if self.signal_sys.towers_active >= self.signal_sys.total_towers:
                    self._save_game()
                    self.state = STATE_WIN
                return

        for note in self.lore_notes:
            if not note.collected and self.player.rect.colliderect(note.rect):
                note.collected = True
                self.lore_display.show(note.title, note.content)
                return

    def _update(self):
        if self.state != STATE_PLAYING:
            return

        self.player.update(self.dt, self.tilemap)
        self.camera.update(self.player)
        self.flashlight.update(self.dt, self.signal_sys.stability)
        self.signal_sys.update(self.dt)
        self.event_sys.update(self.dt)
        self.lore_display.update(self.dt)

        self.audio_det.update(
            self.dt, self.player,
            self.watchers + self.crawlers
        )
        self.sanity_sys.update(
            self.dt, self.player,
            self.watchers + self.crawlers + self.mimics,
            self.signal_sys, self.flashlight
        )
        self.heartbeat.update(
            self.dt, self.player,
            self.watchers + self.crawlers + self.mimics,
            self.sanity_sys
        )
        self.jumpscare.update(
            self.dt, self.player,
            self.watchers + self.crawlers + self.mimics,
            self.signal_sys
        )

        for tower in self.towers:
            tower.update(self.dt)

        for note in self.lore_notes:
            note.update(self.dt)

        for watcher in self.watchers:
            watcher.update(
                self.dt, self.player,
                self.flashlight, self.signal_sys, self.tilemap
            )
            if watcher.touches_player(self.player):
                self.player.take_damage(1)
                self.sanity_sys.take_hit(15.0)

        for crawler in self.crawlers:
            crawler.update(
                self.dt, self.player,
                self.flashlight, self.signal_sys, self.tilemap
            )
            if crawler.touches_player(self.player):
                self.player.take_damage(2)
                self.sanity_sys.take_hit(10.0)

        for mimic in self.mimics:
            mimic.update(
                self.dt, self.player,
                self.signal_sys, self.tilemap
            )
            if mimic.touches_player(self.player):
                self.player.take_damage(3)
                self.sanity_sys.take_hit(25.0)

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
            if self.settings_menu and self.settings_menu.active:
                self.settings_menu.draw()

        elif self.state == STATE_PLAYING:
            self.renderer.draw_map(self.tilemap, self.camera, self.sprite_manager)
            self.renderer.draw_towers(self.towers, self.camera)
            self.renderer.draw_lore_notes(self.lore_notes, self.camera)
            self.renderer.draw_items(self.items, self.camera)
            self.renderer.draw_entities(
                self.watchers + self.crawlers + self.mimics,
                self.camera
            )
            self.renderer.draw_player(self.player, self.camera, self.sprite_manager)
            self.renderer.draw_flashlight(
                self.player, self.camera, self.flashlight
            )
            self.glitch_fx.draw(self.signal_sys, self.event_sys)
            self.hud.draw(
                self.flashlight, self.signal_sys, self.player,
                self.sanity_sys, self.heartbeat, self.audio_det
            )
            self.lore_display.draw()
            self.jumpscare.draw()
            self._draw_interact_hint()
            self._draw_enemy_warning()
            self._draw_mimic_lure()
            self._draw_save_hint()

        elif self.state == STATE_PAUSED:
            self.renderer.draw_map(self.tilemap, self.camera, self.sprite_manager)
            self.renderer.draw_towers(self.towers, self.camera)
            self.renderer.draw_lore_notes(self.lore_notes, self.camera)
            self.renderer.draw_items(self.items, self.camera)
            self.renderer.draw_entities(
                self.watchers + self.crawlers + self.mimics,
                self.camera
            )
            self.renderer.draw_player(self.player, self.camera, self.sprite_manager)
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
                txt = font.render(
                    "[ E ] REPAIR SIGNAL TOWER", True, (0, 180, 60)
                )
                self.screen.blit(txt, (
                    SCREEN_WIDTH // 2 - txt.get_width() // 2,
                    SCREEN_HEIGHT - 40
                ))
                return

        for note in self.lore_notes:
            if not note.collected and self.player.rect.colliderect(note.rect):
                font = pygame.font.SysFont("consolas", 13)
                txt = font.render(
                    "[ E ] READ NOTE", True, (180, 160, 0)
                )
                self.screen.blit(txt, (
                    SCREEN_WIDTH // 2 - txt.get_width() // 2,
                    SCREEN_HEIGHT - 40
                ))
                return

    def _draw_enemy_warning(self):
        all_enemies = self.watchers + self.crawlers + self.mimics
        closest = None
        closest_dist = float('inf')

        for enemy in all_enemies:
            if not enemy.alive:
                continue
            dx = enemy.rect.centerx - self.player.rect.centerx
            dy = enemy.rect.centery - self.player.rect.centery
            dist = (dx*dx + dy*dy) ** 0.5
            if dist < closest_dist:
                closest_dist = dist
                closest = enemy

        if closest and closest_dist < WATCHER_DETECT_RANGE * 1.5:
            font = pygame.font.SysFont("consolas", 12)
            alpha = int(255 * (
                1 - closest_dist / (WATCHER_DETECT_RANGE * 1.5)
            ))
            txt = font.render(
                "// PRESENCE DETECTED //", True, (180, 0, 0)
            )
            surf = pygame.Surface(txt.get_size(), pygame.SRCALPHA)
            surf.fill((0, 0, 0, 0))
            surf.blit(txt, (0, 0))
            surf.set_alpha(alpha)
            self.screen.blit(surf, (
                SCREEN_WIDTH // 2 - txt.get_width() // 2,
                SCREEN_HEIGHT - 60
            ))

    def _draw_mimic_lure(self):
        for mimic in self.mimics:
            if mimic._lure_active and mimic.current_lure:
                import random
                font = pygame.font.SysFont("consolas", 14)
                if random.random() > 0.05:
                    offset = random.randint(-2, 2)
                    txt = font.render(
                        f'"{mimic.current_lure}"', True, (160, 160, 200)
                    )
                    self.screen.blit(txt, (
                        SCREEN_WIDTH // 2 - txt.get_width() // 2 + offset,
                        SCREEN_HEIGHT // 2 - 80
                    ))

    def _draw_save_hint(self):
        font = pygame.font.SysFont("consolas", 11)
        txt = font.render("[ F5 ] SAVE", True, (30, 30, 30))
        self.screen.blit(txt, (SCREEN_WIDTH - txt.get_width() - 8,
                               SCREEN_HEIGHT - 16))

    def _draw_pause(self):
        overlay = pygame.Surface(
            (SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA
        )
        overlay.fill((0, 0, 0, 160))
        self.screen.blit(overlay, (0, 0))
        font = pygame.font.SysFont("consolas", 36, bold=True)
        sub = pygame.font.SysFont("consolas", 14)
        small = pygame.font.SysFont("consolas", 13)
        txt = font.render("// PAUSED", True, (180, 0, 0))
        hint = sub.render(
            "[ ESC ] RESUME [ Q ] QUIT", True, (60, 60, 60)
        )
        save_hint = small.render(
            "[ F5 ] SAVE GAME", True, (40, 40, 40)
        )
        self.screen.blit(txt, txt.get_rect(
            center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 30)))
        self.screen.blit(hint, hint.get_rect(
            center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 20)))
        self.screen.blit(save_hint, save_hint.get_rect(
            center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 45)))

    def _draw_gameover(self):
        self.screen.fill((5, 0, 0))
        font = pygame.font.SysFont("consolas", 52, bold=True)
        sub = pygame.font.SysFont("consolas", 14)
        txt = font.render("YOU DIED", True, (180, 0, 0))
        hint = sub.render(
            "[ R ] RETRY [ ESC ] TITLE", True, (60, 60, 60)
        )
        self.screen.blit(txt, txt.get_rect(
            center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 20)))
        self.screen.blit(hint, hint.get_rect(
            center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 40)))

    def _draw_win(self):
        self.screen.fill((0, 5, 0))
        font = pygame.font.SysFont("consolas", 44, bold=True)
        sub = pygame.font.SysFont("consolas", 14)
        txt = font.render("SIGNAL RESTORED", True, (0, 180, 60))
        hint = sub.render(
            "[ R ] PLAY AGAIN [ ESC ] TITLE", True, (60, 60, 60)
        )
        self.screen.blit(txt, txt.get_rect(
            center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 20)))
        self.screen.blit(hint, hint.get_rect(
            center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 40)))