from ursina import *
from settings import *
import random


class HUD:
    def __init__(self, game):
        self.game     = game
        self._visible = True
        self._entities = []

        self._build()

    # ── Build ───────────────────────────────────────
    def _build(self):
        # ── Signal Bar ──────────────────────────────
        self.signal_bg = self._bar_bg((-0.85, 0.45))
        self.signal_fill = self._bar_fill((-0.85, 0.45), COLOR_GREEN)
        self.signal_label = self._label("SIGNAL", (-0.85, 0.48), scale=0.7)
        self.signal_pct   = self._label("100%",   (-0.62, 0.45), scale=0.7)

        # ── Battery Bar ─────────────────────────────
        self.battery_bg   = self._bar_bg((-0.85, 0.38))
        self.battery_fill = self._bar_fill((-0.85, 0.38), COLOR_AMBER)
        self.battery_label = self._label("BATTERY", (-0.85, 0.41), scale=0.7)
        self.battery_pct   = self._label("100%",    (-0.62, 0.38), scale=0.7)

        # ── Heat Bar ────────────────────────────────
        self.heat_bg   = self._bar_bg((-0.85, 0.31))
        self.heat_fill = self._bar_fill((-0.85, 0.31), color.rgb(200, 60, 0))
        self.heat_label = self._label("HEAT", (-0.85, 0.34), scale=0.7)

        # ── Health Bar ──────────────────────────────
        self.health_bg   = self._bar_bg((-0.85, 0.24))
        self.health_fill = self._bar_fill((-0.85, 0.24), color.rgb(0, 180, 60))
        self.health_label = self._label("HEALTH", (-0.85, 0.27), scale=0.7)
        self.health_val   = self._label("100",    (-0.62, 0.24), scale=0.7)

        # ── Flashlight Status ───────────────────────
        self.flash_status = self._label(
            "[ F ] FLASHLIGHT: ON",
            (-0.85, 0.17),
            scale=0.7,
            col=color.rgb(0, 200, 80)
        )

        # ── Tower Count ─────────────────────────────
        self.tower_txt = self._label(
            "TOWERS: 0 / 3",
            (-0.85, 0.10),
            scale=0.7,
            col=color.rgb(80, 80, 80)
        )

        # ── Signal Status (top right) ────────────────
        self.signal_status = self._label(
            "STABLE",
            (0.6, 0.45),
            scale=1.0,
            col=COLOR_GREEN
        )

        # ── Crosshair ───────────────────────────────
        self.crosshair_h = Entity(
            parent   = camera.ui,
            model    = 'quad',
            scale    = (0.02, 0.002),
            color    = color.rgba(200, 200, 200, 100),
            position = (0, 0)
        )
        self.crosshair_v = Entity(
            parent   = camera.ui,
            model    = 'quad',
            scale    = (0.002, 0.02),
            color    = color.rgba(200, 200, 200, 100),
            position = (0, 0)
        )

        # ── Vignette (edge darkening) ────────────────
        self.vignette = Entity(
            parent   = camera.ui,
            model    = 'quad',
            scale    = (2, 2),
            color    = color.rgba(0, 0, 0, 80),
            texture  = 'vignette' if os.path.exists('assets/vignette.png') else None,
            z        = 1
        )

        # ── Critical Overlay ─────────────────────────
        self.critical_overlay = Entity(
            parent   = camera.ui,
            model    = 'quad',
            scale    = (2, 2),
            color    = color.rgba(120, 0, 0, 0),
            z        = 0.9
        )

        # ── Blackout Warning ─────────────────────────
        self.blackout_txt = Text(
            text     = '// SIGNAL LOST //',
            parent   = camera.ui,
            position = (0, 0),
            origin   = (0, 0),
            scale    = 2.5,
            color    = COLOR_DANGER,
            enabled  = False
        )

        # ── Gameover / Win ───────────────────────────
        self.end_txt = Text(
            text     = '',
            parent   = camera.ui,
            position = (0, 0.05),
            origin   = (0, 0),
            scale    = 3,
            color    = COLOR_DANGER,
            enabled  = False
        )
        self.end_hint = Text(
            text     = '',
            parent   = camera.ui,
            position = (0, -0.05),
            origin   = (0, 0),
            scale    = 1.2,
            color    = color.rgb(80, 80, 80),
            enabled  = False
        )

    # ── Update ──────────────────────────────────────
    def update(self):
        if not self.game.flashlight or not self.game.signal_sys:
            return

        fl  = self.game.flashlight
        sig = self.game.signal_sys
        pl  = self.game.player

        self._update_signal_bar(sig)
        self._update_battery_bar(fl)
        self._update_heat_bar(fl)
        self._update_health_bar(pl)
        self._update_flash_status(fl)
        self._update_tower_count(sig)
        self._update_critical_overlay(sig)
        self._update_blackout(sig)

    # ── Bar Updates ─────────────────────────────────
    def _update_signal_bar(self, sig):
        self.signal_fill.scale_x = max(0.001, 0.2 * sig.stability_pct)
        self.signal_fill.x       = -0.85 + (0.2 * sig.stability_pct) / 2
        self.signal_fill.color   = sig.status_color
        self.signal_pct.text     = f"{int(sig.stability)}%"
        self.signal_status.text  = sig.status_label
        self.signal_status.color = sig.status_color

        # Flicker the bar
        if sig.lights_flickering and random.random() > 0.5:
            self.signal_fill.color = color.white

    def _update_battery_bar(self, fl):
        self.battery_fill.scale_x = max(0.001, 0.2 * fl.battery_pct)
        self.battery_fill.x       = -0.85 + (0.2 * fl.battery_pct) / 2
        self.battery_fill.color   = self._battery_color(fl.battery_pct)
        self.battery_pct.text     = f"{int(fl.battery)}%"

    def _update_heat_bar(self, fl):
        self.heat_fill.scale_x = max(0.001, 0.2 * fl.heat_pct)
        self.heat_fill.x       = -0.85 + (0.2 * fl.heat_pct) / 2
        r = int(255 * fl.heat_pct)
        g = int(60  * (1 - fl.heat_pct))
        self.heat_fill.color   = color.rgb(r, g, 0)
        self.heat_bg.enabled   = fl.heat_pct > 0.05
        self.heat_fill.enabled = fl.heat_pct > 0.05
        self.heat_label.enabled = fl.heat_pct > 0.05

    def _update_health_bar(self, pl):
        if not pl:
            return
        hp_pct = pl.health / PLAYER_MAX_HEALTH
        self.health_fill.scale_x = max(0.001, 0.2 * hp_pct)
        self.health_fill.x       = -0.85 + (0.2 * hp_pct) / 2
        self.health_fill.color   = self._health_color(hp_pct)
        self.health_val.text     = str(pl.health)

    def _update_flash_status(self, fl):
        color_map = {
            "ON":       color.rgb(0, 200, 80),
            "OFF":      color.rgb(60, 60, 60),
            "DEAD":     COLOR_DANGER,
            "OVERHEAT": color.rgb(220, 80, 0),
            "UNSTABLE": COLOR_AMBER,
        }
        self.flash_status.text  = f"[ F ] FLASHLIGHT: {fl.status_label}"
        self.flash_status.color = color_map.get(fl.status_label, color.white)

    def _update_tower_count(self, sig):
        self.tower_txt.text = f"TOWERS: {sig.towers_active} / {sig.total_towers}"

    def _update_critical_overlay(self, sig):
        if sig.is_critical:
            alpha = int((1.0 - sig.stability_pct) * 80)
            if sig.lights_flickering:
                alpha = random.randint(20, 80)
            self.critical_overlay.color = color.rgba(120, 0, 0, alpha)
        else:
            self.critical_overlay.color = color.rgba(0, 0, 0, 0)

    def _update_blackout(self, sig):
        self.blackout_txt.enabled = sig.is_blackout
        if sig.is_blackout:
            self.blackout_txt.enabled = random.random() > 0.3

    # ── End Screens ─────────────────────────────────
    def show_gameover(self):
        mouse.locked = False
        self.end_txt.text    = 'YOU DIED'
        self.end_txt.color   = COLOR_DANGER
        self.end_txt.enabled = True
        self.end_hint.text   = '[ R ] RETRY       [ ESC ] TITLE'
        self.end_hint.enabled = True

    def show_win(self):
        mouse.locked = False
        self.end_txt.text    = 'SIGNAL RESTORED'
        self.end_txt.color   = COLOR_GREEN
        self.end_txt.enabled = True
        self.end_hint.text   = '[ R ] PLAY AGAIN       [ ESC ] TITLE'
        self.end_hint.enabled = True

    # ── Helpers ─────────────────────────────────────
    def _bar_bg(self, pos):
        return Entity(
            parent   = camera.ui,
            model    = 'quad',
            scale    = (0.2, 0.012),
            position = Vec2(pos[0] + 0.1, pos[1]),
            color    = color.rgba(20, 20, 20, 180)
        )

    def _bar_fill(self, pos, col):
        e = Entity(
            parent   = camera.ui,
            model    = 'quad',
            scale    = (0.2, 0.010),
            position = Vec2(pos[0] + 0.1, pos[1]),
            color    = col
        )
        return e

    def _label(self, txt, pos, scale=0.8, col=color.rgb(100, 100, 100)):
        return Text(
            text     = txt,
            parent   = camera.ui,
            position = Vec2(pos[0], pos[1]),
            scale    = scale,
            color    = col
        )

    def _battery_color(self, pct):
        if pct > 0.5:
            return COLOR_AMBER
        elif pct > 0.25:
            return color.rgb(200, 120, 0)
        return COLOR_DANGER

    def _health_color(self, pct):
        if pct > 0.6:
            return color.rgb(0, 180, 60)
        elif pct > 0.3:
            return COLOR_AMBER
        return COLOR_DANGER

    def destroy(self):
        for e in self._entities:
            destroy(e)