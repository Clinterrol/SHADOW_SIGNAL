from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
from settings import *


class Player:
    def __init__(self, game):
        self.game   = game
        self.health = PLAYER_MAX_HEALTH

        # Ursina first person controller
        self.controller = FirstPersonController(
            position    = Vec3(2, 1, 2),
            speed       = PLAYER_SPEED,
            jump_height = 0,              # no jumping in horror game
            gravity     = 0,              # flat facility floor
            mouse_sensitivity = Vec2(40, 40)
        )
        self.controller.cursor.visible = False

        # Movement state
        self.is_sprinting  = False
        self.is_crouching  = False
        self.sound_radius  = SOUND_RADIUS_WALK

        # Original height for crouch lerp
        self._stand_y      = self.controller.camera_pivot.y

    # ── Update ──────────────────────────────────────
    def update(self):
        self._handle_movement()
        self._handle_crouch()
        self._update_sound_radius()

    def _handle_movement(self):
        sprinting = held_keys['left shift'] or held_keys['right shift']
        crouching = held_keys['left control'] or held_keys['right control']

        if crouching:
            self.controller.speed = PLAYER_CROUCH_SPEED
        elif sprinting:
            self.controller.speed = PLAYER_SPRINT_SPEED
        else:
            self.controller.speed = PLAYER_SPEED

        self.is_sprinting = sprinting and not crouching
        self.is_crouching = crouching

    def _handle_crouch(self):
        target_y = self._stand_y * 0.5 if self.is_crouching else self._stand_y
        self.controller.camera_pivot.y = lerp(
            self.controller.camera_pivot.y, target_y, time.dt * 10
        )

    def _update_sound_radius(self):
        if self.is_crouching:
            self.sound_radius = SOUND_RADIUS_CROUCH
        elif self.is_sprinting:
            self.sound_radius = SOUND_RADIUS_SPRINT
        else:
            self.sound_radius = SOUND_RADIUS_WALK

    # ── Health ──────────────────────────────────────
    def take_damage(self, amount):
        self.health = max(0, self.health - amount)

    def heal(self, amount):
        self.health = min(PLAYER_MAX_HEALTH, self.health + amount)

    @property
    def position(self):
        return self.controller.position