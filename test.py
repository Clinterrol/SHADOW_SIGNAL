from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController

app = Ursina()

# Simple floor
floor = Entity(
    model    = 'plane',
    scale    = 20,
    color    = color.gray,
    collider = 'box'
)

# Simple wall to walk toward
wall = Entity(
    model    = 'cube',
    position = Vec3(0, 1, 5),
    color    = color.dark_gray,
    collider = 'box'
)

# Player
player = FirstPersonController(
    position = Vec3(0, 2, 0),
    gravity  = 1
)

app.run()