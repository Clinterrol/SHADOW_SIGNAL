import random
import time
from settings import *


class SignalSystem:
    def __init__(self):
        self.stability      = SIGNAL_MAX
        self.towers_active  = 0
        self.total_towers   = 3       # matches test map tower count
        self.is_critical    = False
        self.is_blackout    = False

        # Interference pulse — random signal drops
        self._pulse_timer    = 0.0
        self._pulse_interval = random.uniform(8.0, 20.0)
        self._pulse_active   = False
        self._pulse_duration = 0.0

        # Flicker timing for lights
        self._flicker_timer    = 0.0
        self._flicker_interval = random.uniform(0.05, 0.15)
        self.lights_flickering = False

    # ── Update ──────────────────────────────────────
    def update(self, dt):
        self._decay(dt)
        self._pulse_interference(dt)
        self._update_flicker(dt)
        self._check_states()

    # ── Decay ───────────────────────────────────────
    def _decay(self, dt):
        """
        Passive signal decay every frame.
        Active towers slow the decay.
        """
        tower_bonus   = self.towers_active * 0.35
        effective_rate = max(0.0, SIGNAL_DECAY_RATE - tower_bonus)
        self.stability = max(0.0, self.stability - effective_rate * dt)

    # ── Interference Pulses ─────────────────────────
    def _pulse_interference(self, dt):
        """
        Random signal interference bursts — drops stability fast
        for a short window then eases off.
        Phase 4 event system will trigger these manually too.
        """
        self._pulse_timer += dt

        if self._pulse_active:
            self._pulse_duration -= dt
            self.stability = max(
                0.0, self.stability - 12.0 * dt
            )
            if self._pulse_duration <= 0:
                self._pulse_active = False

        elif self._pulse_timer >= self._pulse_interval:
            self._pulse_timer    = 0.0
            self._pulse_interval = random.uniform(8.0, 20.0)
            # Only pulse if not already critical
            if self.stability > SIGNAL_CRIT_THRESH:
                self._pulse_active   = True
                self._pulse_duration = random.uniform(0.5, 1.5)

    # ── Flicker ─────────────────────────────────────
    def _update_flicker(self, dt):
        if not self.is_critical:
            self.lights_flickering = False
            return

        self._flicker_timer += dt
        if self._flicker_timer >= self._flicker_interval:
            self._flicker_timer    = 0.0
            self._flicker_interval = random.uniform(0.05, 0.2)
            flicker_chance = 1.0 - (self.stability / SIGNAL_CRIT_THRESH)
            self.lights_flickering = random.random() < flicker_chance

    # ── State Checks ────────────────────────────────
    def _check_states(self):
        self.is_critical = self.stability <= SIGNAL_CRIT_THRESH
        self.is_blackout = self.stability <= SIGNAL_ZERO_THRESH

    # ── Tower Interaction ───────────────────────────
    def activate_tower(self, boost=25.0):
        """
        Called when player repairs a signal tower.
        Boosts stability and counts active tower.
        """
        if self.towers_active < self.total_towers:
            self.towers_active += 1
        self.stability = min(SIGNAL_MAX, self.stability + boost)

    def deactivate_tower(self):
        """Called if a tower gets damaged — Phase 4 event hook."""
        self.towers_active = max(0, self.towers_active - 1)

    def force_interference(self, duration=2.0):
        """
        Manual trigger from event system Phase 4.
        Scary moments — sudden signal drop.
        """
        self._pulse_active   = True
        self._pulse_duration = duration

    # ── Properties for HUD ──────────────────────────
    @property
    def stability_pct(self):
        return self.stability / SIGNAL_MAX

    @property
    def status_label(self):
        if self.is_blackout:
            return "BLACKOUT"
        if self.is_critical:
            return "CRITICAL"
        if self.stability < 60:
            return "UNSTABLE"
        return "STABLE"

    @property
    def status_color(self):
        if self.is_blackout:
            return (80, 0, 0)
        if self.is_critical:
            return DANGER_RED
        if self.stability < 60:
            return AMBER
        return GREEN_SIGNAL