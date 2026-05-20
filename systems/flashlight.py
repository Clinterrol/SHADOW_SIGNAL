import random
from settings import *


class Flashlight:
    def __init__(self):
        self.is_on      = True
        self.battery    = FLASHLIGHT_MAX_BATTERY
        self.heat       = 0.0
        self.overheated = False

        # Flicker state
        self.is_flickering    = False
        self._flicker_timer   = 0.0
        self._flicker_interval = random.uniform(0.08, 0.2)

    # ── Update ──────────────────────────────────────
    def update(self, dt, signal_stability):
        if self.is_on and not self.overheated:
            self._drain_battery(dt)
            self._build_heat(dt)
        else:
            self._cool_down(dt)

        self._check_overheat()
        self._check_flicker(dt, signal_stability)
        self._auto_off_on_empty()

    # ── Battery ─────────────────────────────────────
    def _drain_battery(self, dt):
        self.battery = max(0.0, self.battery - FLASHLIGHT_DRAIN_RATE * dt)

    def _auto_off_on_empty(self):
        if self.battery <= 0:
            self.is_on  = False
            self.battery = 0.0

    def add_battery(self, amount):
        """Called when player picks up a battery item."""
        self.battery = min(FLASHLIGHT_MAX_BATTERY, self.battery + amount)

    # ── Heat / Overheat ─────────────────────────────
    def _build_heat(self, dt):
        self.heat = min(
            FLASHLIGHT_OVERHEAT_MAX,
            self.heat + FLASHLIGHT_HEAT_RATE * dt
        )

    def _cool_down(self, dt):
        self.heat = max(0.0, self.heat - FLASHLIGHT_COOL_RATE * dt)
        if self.heat <= 0:
            self.overheated = False

    def _check_overheat(self):
        if self.heat >= FLASHLIGHT_OVERHEAT_MAX:
            self.overheated = True
            self.is_on      = False   # force off to cool

    # ── Flicker ─────────────────────────────────────
    def _check_flicker(self, dt, signal_stability):
        """
        Flicker chance scales with signal decay.
        Below SIGNAL_CRIT_THRESH flashlight becomes very unstable.
        """
        if not self.is_on or self.battery <= 0:
            self.is_flickering = False
            return

        flicker_chance = self._flicker_chance(signal_stability)

        self._flicker_timer += dt
        if self._flicker_timer >= self._flicker_interval:
            self._flicker_timer    = 0.0
            self._flicker_interval = random.uniform(0.08, 0.25)
            self.is_flickering     = random.random() < flicker_chance

    def _flicker_chance(self, signal_stability):
        if signal_stability > SIGNAL_CRIT_THRESH:
            # Stable — very rare flicker
            return 0.05
        elif signal_stability > 10.0:
            # Warning zone — moderate flicker
            t = 1.0 - (signal_stability - 10.0) / (SIGNAL_CRIT_THRESH - 10.0)
            return 0.05 + t * 0.45    # 0.05 → 0.50
        else:
            # Critical — constant flicker
            return 0.80

    # ── Toggle ──────────────────────────────────────
    def toggle(self):
        if self.overheated or self.battery <= 0:
            return    # can't turn on
        self.is_on = not self.is_on

    # ── Properties for HUD ──────────────────────────
    @property
    def battery_pct(self):
        return self.battery / FLASHLIGHT_MAX_BATTERY

    @property
    def heat_pct(self):
        return self.heat / FLASHLIGHT_OVERHEAT_MAX

    @property
    def status_label(self):
        if self.battery <= 0:
            return "DEAD"
        if self.overheated:
            return "OVERHEAT"
        if self.is_flickering:
            return "UNSTABLE"
        if not self.is_on:
            return "OFF"
        return "ON"