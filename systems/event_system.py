import random
import pygame
from settings import *


class EventSystem:
    def __init__(self, game):
        self.game          = game
        self._event_timer  = 0.0
        self._event_interval = random.uniform(15.0, 40.0)
        self._active_event   = None
        self._event_duration = 0.0

        # Whisper radio lines
        self._radio_lines = [
            "...they are still in here...",
            "...signal lost on floor 3...",
            "...do not enter sector B...",
            "...it can hear you breathing...",
            "...run...",
            "...the lights won't save you...",
        ]
        self.current_radio  = ""
        self._radio_timer   = 0.0
        self._radio_visible = False

    def update(self, dt):
        self._event_timer += dt

        if self._active_event:
            self._event_duration -= dt
            if self._event_duration <= 0:
                self._active_event = None

        elif self._event_timer >= self._event_interval:
            self._event_timer    = 0.0
            self._event_interval = random.uniform(15.0, 40.0)
            self._trigger_random_event()

        # Radio whisper timer
        if self._radio_visible:
            self._radio_timer -= dt
            if self._radio_timer <= 0:
                self._radio_visible = False
                self.current_radio  = ""

    def _trigger_random_event(self):
        events = [
            self._event_radio_whisper,
            self._event_signal_spike,
            self._event_alarm,
        ]
        random.choice(events)()

    def _event_radio_whisper(self):
        self._active_event   = "radio"
        self._event_duration = 3.0
        self.current_radio   = random.choice(self._radio_lines)
        self._radio_visible  = True
        self._radio_timer    = 4.0

    def _event_signal_spike(self):
        self._active_event   = "spike"
        self._event_duration = 2.0
        if self.game.signal_sys:
            self.game.signal_sys.force_interference(2.0)

    def _event_alarm(self):
        self._active_event   = "alarm"
        self._event_duration = 3.0

    @property
    def alarm_active(self):
        return self._active_event == "alarm"

    @property
    def radio_visible(self):
        return self._radio_visible