import random
from settings import *


class Flashlight:
    def __init__(self):
        self.is_on             = True
        self.battery           = FLASHLIGHT_MAX_BATTERY
        self.heat              = 0.0
        self.overheated        = False
        self.is_flickering     = False
        self._flicker_timer    = 0.0
        self._flicker_interval = random.uniform(0.08, 0.2)

    def update(self, dt, signal_stability):
        if self.is_on and not self.overheated:
            self.battery = max(0.0, self.battery - FLASHLIGHT_DRAIN_RATE * dt)
            self.heat    = min(FLASHLIGHT_OVERHEAT_MAX,
                               self.heat + FLASHLIGHT_HEAT_RATE * dt)
        else:
            self.heat = max(0.0, self.heat - FLASHLIGHT_COOL_RATE * dt)
            if self.heat <= 0:
                self.overheated = False

        if self.heat >= FLASHLIGHT_OVERHEAT_MAX:
            self.overheated = True
            self.is_on      = False

        if self.battery <= 0:
            self.is_on   = False
            self.battery = 0.0

        self._flicker_timer += dt
        if self._flicker_timer >= self._flicker_interval:
            self._flicker_timer    = 0.0
            self._flicker_interval = random.uniform(0.08, 0.25)
            if self.is_on and self.battery > 0:
                if signal_stability > SIGNAL_CRIT_THRESH:
                    self.is_flickering = random.random() < 0.05
                elif signal_stability > 10.0:
                    self.is_flickering = random.random() < 0.40
                else:
                    self.is_flickering = random.random() < 0.80
            else:
                self.is_flickering = False

    def toggle(self):
        if self.overheated or self.battery <= 0:
            return
        self.is_on = not self.is_on

    def add_battery(self, amount):
        self.battery = min(FLASHLIGHT_MAX_BATTERY, self.battery + amount)

    @property
    def battery_pct(self):
        return self.battery / FLASHLIGHT_MAX_BATTERY

    @property
    def heat_pct(self):
        return self.heat / FLASHLIGHT_OVERHEAT_MAX

    @property
    def status_label(self):
        if self.battery <= 0:  return "DEAD"
        if self.overheated:    return "OVERHEAT"
        if self.is_flickering: return "UNSTABLE"
        if not self.is_on:     return "OFF"
        return "ON"
    
    