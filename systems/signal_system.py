import random
from settings import *


class SignalSystem:
    def __init__(self):
        self.stability         = SIGNAL_MAX
        self.towers_active     = 0
        self.total_towers      = 3
        self.is_critical       = False
        self.is_blackout       = False
        self.lights_flickering = False
        self._pulse_timer      = 0.0
        self._pulse_interval   = random.uniform(8.0, 20.0)
        self._pulse_active     = False
        self._pulse_duration   = 0.0
        self._flicker_timer    = 0.0

    def update(self, dt):
        tower_bonus    = self.towers_active * 0.35
        effective_rate = max(0.0, SIGNAL_DECAY_RATE - tower_bonus)
        self.stability = max(0.0, self.stability - effective_rate * dt)

        self._pulse_timer += dt
        if self._pulse_active:
            self._pulse_duration -= dt
            self.stability = max(0.0, self.stability - 12.0 * dt)
            if self._pulse_duration <= 0:
                self._pulse_active = False
        elif self._pulse_timer >= self._pulse_interval:
            self._pulse_timer    = 0.0
            self._pulse_interval = random.uniform(8.0, 20.0)
            if self.stability > SIGNAL_CRIT_THRESH:
                self._pulse_active   = True
                self._pulse_duration = random.uniform(0.5, 1.5)

        self.is_critical = self.stability <= SIGNAL_CRIT_THRESH
        self.is_blackout = self.stability <= SIGNAL_ZERO_THRESH

        if self.is_critical:
            self._flicker_timer += dt
            if self._flicker_timer >= 0.1:
                self._flicker_timer = 0.0
                chance = 1.0 - (self.stability / SIGNAL_CRIT_THRESH)
                self.lights_flickering = random.random() < chance
        else:
            self.lights_flickering = False

    def activate_tower(self, boost=25.0):
        if self.towers_active < self.total_towers:
            self.towers_active += 1
        self.stability = min(SIGNAL_MAX, self.stability + boost)

    @property
    def stability_pct(self):
        return self.stability / SIGNAL_MAX

    @property
    def status_label(self):
        if self.is_blackout:    return "BLACKOUT"
        if self.is_critical:    return "CRITICAL"
        if self.stability < 60: return "UNSTABLE"
        return "STABLE"

    @property
    def status_color(self):
        if self.is_blackout:    return (80, 0, 0)
        if self.is_critical:    return DANGER_RED
        if self.stability < 60: return AMBER
        return GREEN_SIGNAL