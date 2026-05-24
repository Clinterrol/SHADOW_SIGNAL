import math
from settings import *


class HeartbeatSystem:
    def __init__(self):
        self._timer    = 0.0
        self._bpm      = 60.0
        self.beat      = False
        self._beat_dur = 0.1

    def update(self, dt, player, watchers, sanity_sys):
        # BPM increases with danger
        base_bpm = 60.0

        # Near watcher
        for watcher in watchers:
            if not watcher.alive:
                continue
            dx   = watcher.rect.centerx - player.rect.centerx
            dy   = watcher.rect.centery - player.rect.centery
            dist = max(1, (dx*dx + dy*dy) ** 0.5)
            if dist < WATCHER_DETECT_RANGE * 1.5:
                proximity  = 1.0 - (dist / (WATCHER_DETECT_RANGE * 1.5))
                base_bpm  += proximity * 80.0

        # Low sanity
        if sanity_sys.sanity < 50:
            base_bpm += (50 - sanity_sys.sanity) * 1.2

        self._bpm = min(160.0, base_bpm)

        interval    = 60.0 / self._bpm
        self._timer += dt

        if self._timer >= interval:
            self._timer = 0.0
            self.beat   = True
        elif self._timer > self._beat_dur:
            self.beat = False

    @property
    def intensity(self):
        return min(1.0, (self._bpm - 60.0) / 100.0)
