import random
from settings import *


class SanitySystem:
    def __init__(self):
        self.sanity       = 100.0
        self.max_sanity   = 100.0
        self._drain_timer = 0.0

        # Hallucination state
        self.hallucinating    = False
        self._halluc_timer    = 0.0
        self._halluc_messages = [
            "...it knows you're here...",
            "...don't look behind you...",
            "...you can't escape...",
            "...the signal is dead...",
            "...run...",
            "...it's getting closer...",
        ]
        self.current_halluc = ""

    def update(self, dt, player, watchers, signal_sys, flashlight):
        self._drain(dt, player, watchers, signal_sys, flashlight)
        self._check_hallucination(dt)

    def _drain(self, dt, player, watchers, signal_sys, flashlight):
        drain = 0.0

        # Drain faster in darkness
        if not flashlight.is_on or flashlight.battery <= 0:
            drain += 3.0

        # Drain near watcher
        for watcher in watchers:
            if not watcher.alive:
                continue
            dx   = watcher.rect.centerx - player.rect.centerx
            dy   = watcher.rect.centery - player.rect.centery
            dist = max(1, (dx*dx + dy*dy) ** 0.5)
            if dist < WATCHER_DETECT_RANGE:
                proximity = 1.0 - (dist / WATCHER_DETECT_RANGE)
                drain    += proximity * 8.0

        # Drain in blackout
        if signal_sys.is_blackout:
            drain += 5.0

        # Recover slowly when safe and lit
        if drain == 0.0 and flashlight.is_on:
            self.sanity = min(self.max_sanity, self.sanity + 1.5 * dt)
        else:
            self.sanity = max(0.0, self.sanity - drain * dt)

    def _check_hallucination(self, dt):
        if self.sanity < 40.0:
            self._halluc_timer -= dt
            if self._halluc_timer <= 0:
                interval = max(3.0, self.sanity / 10.0)
                self._halluc_timer  = interval + random.uniform(-1.0, 1.0)
                self.hallucinating  = True
                self.current_halluc = random.choice(self._halluc_messages)
            else:
                self.hallucinating = False
        else:
            self.hallucinating  = False
            self.current_halluc = ""

    def take_hit(self, amount=20.0):
        self.sanity = max(0.0, self.sanity - amount)

    @property
    def sanity_pct(self):
        return self.sanity / self.max_sanity

    @property
    def is_critical(self):
        return self.sanity < 25.0
