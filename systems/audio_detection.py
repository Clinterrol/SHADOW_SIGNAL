import math
from settings import *


class AudioDetection:
    def __init__(self):
        self.alert_level  = 0.0    # 0.0 - 1.0
        self._decay_rate  = 0.3

    def update(self, dt, player, watchers):
        # Decay alert over time
        self.alert_level = max(0.0, self.alert_level - self._decay_rate * dt)

        # Player movement generates sound
        if player.is_sprinting:
            self._emit_sound(player, SOUND_RADIUS_SPRINT, watchers)
        elif player.is_moving and not player.is_crouching:
            self._emit_sound(player, SOUND_RADIUS_WALK, watchers)
        elif player.is_crouching and player.is_moving:
            self._emit_sound(player, SOUND_RADIUS_CROUCH, watchers)

    def emit_door_sound(self, player, watchers):
        self._emit_sound(player, SOUND_RADIUS_DOOR, watchers)

    def _emit_sound(self, player, radius, watchers):
        for watcher in watchers:
            if not watcher.alive:
                continue
            dx   = watcher.rect.centerx - player.rect.centerx
            dy   = watcher.rect.centery - player.rect.centery
            dist = max(1, (dx*dx + dy*dy) ** 0.5)
            if dist <= radius:
                # Alert scales with proximity
                strength = 1.0 - (dist / radius)
                self.alert_level = min(1.0, self.alert_level + strength * 0.4)
                if watcher.state != "chase":
                    watcher.state          = "chase"
                    watcher._last_known_x  = player.rect.centerx
                    watcher._last_known_y  = player.rect.centery

    @property
    def is_alerted(self):
        return self.alert_level > 0.3