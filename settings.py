from ursina import color, Vec3, Vec2

# ── Window ──────────────────────────────────────────
TITLE          = "SHADOW SIGNAL"
SCREEN_WIDTH   = 1280
SCREEN_HEIGHT  = 720
FPS            = 60
TILE_SIZE      = 2          # Ursina world units (not pixels)

# ── Player ──────────────────────────────────────────
PLAYER_SPEED         = 5
PLAYER_SPRINT_SPEED  = 9
PLAYER_CROUCH_SPEED  = 2
PLAYER_HEIGHT        = 2
PLAYER_MAX_HEALTH    = 100
PLAYER_GRAVITY       = 1

# ── Flashlight ──────────────────────────────────────
FLASHLIGHT_MAX_BATTERY  = 100.0
FLASHLIGHT_DRAIN_RATE   = 2.5
FLASHLIGHT_OVERHEAT_MAX = 100.0
FLASHLIGHT_HEAT_RATE    = 15.0
FLASHLIGHT_COOL_RATE    = 8.0
FLASHLIGHT_RANGE        = 20       # world units
FLASHLIGHT_FOV          = 45       # spotlight cone degrees

# ── Signal System ───────────────────────────────────
SIGNAL_MAX          = 100.0
SIGNAL_DECAY_RATE   = 1.2
SIGNAL_CRIT_THRESH  = 25.0
SIGNAL_ZERO_THRESH  = 0.0

# ── Audio Detection ─────────────────────────────────
SOUND_RADIUS_WALK   = 5
SOUND_RADIUS_SPRINT = 12
SOUND_RADIUS_CROUCH = 1
SOUND_RADIUS_DOOR   = 15

# ── Enemy ───────────────────────────────────────────
WATCHER_SPEED_DARK    = 4
WATCHER_SPEED_FLICKER = 1.5
WATCHER_SPEED_LIGHT   = 0
WATCHER_DETECT_RANGE  = 14

# ── Colors (Ursina) ─────────────────────────────────
COLOR_BLACK       = color.black
COLOR_RED         = color.rgb(200, 0, 0)
COLOR_DARK_RED    = color.rgb(100, 0, 0)
COLOR_AMBER       = color.rgb(255, 180, 0)
COLOR_GREEN       = color.rgb(0, 220, 80)
COLOR_DANGER      = color.rgb(220, 30, 30)
COLOR_WALL        = color.rgb(15, 15, 15)
COLOR_FLOOR       = color.rgb(20, 20, 20)
COLOR_CEILING     = color.rgb(10, 10, 10)

# ── Game States ─────────────────────────────────────
STATE_TITLE    = "title"
STATE_PLAYING  = "playing"
STATE_PAUSED   = "paused"
STATE_GAMEOVER = "gameover"
STATE_WIN      = "win"

# ── Paths ───────────────────────────────────────────
ASSET_DIR  = "assets"
SPRITE_DIR = f"{ASSET_DIR}/sprites"
SOUND_DIR  = f"{ASSET_DIR}/sounds"
FONT_DIR   = f"{ASSET_DIR}/fonts"
SAVE_FILE  = "saves/save_data.json"
from ursina import color, Vec3, Vec2

# ── Window ──────────────────────────────────────────
TITLE          = "SHADOW SIGNAL"
SCREEN_WIDTH   = 1280
SCREEN_HEIGHT  = 720
FPS            = 60
TILE_SIZE      = 2          # Ursina world units (not pixels)

# ── Player ──────────────────────────────────────────
PLAYER_SPEED         = 5
PLAYER_SPRINT_SPEED  = 9
PLAYER_CROUCH_SPEED  = 2
PLAYER_HEIGHT        = 2
PLAYER_MAX_HEALTH    = 100
PLAYER_GRAVITY       = 1

# ── Flashlight ──────────────────────────────────────
FLASHLIGHT_MAX_BATTERY  = 100.0
FLASHLIGHT_DRAIN_RATE   = 2.5
FLASHLIGHT_OVERHEAT_MAX = 100.0
FLASHLIGHT_HEAT_RATE    = 15.0
FLASHLIGHT_COOL_RATE    = 8.0
FLASHLIGHT_RANGE        = 20       # world units
FLASHLIGHT_FOV          = 45       # spotlight cone degrees

# ── Signal System ───────────────────────────────────
SIGNAL_MAX          = 100.0
SIGNAL_DECAY_RATE   = 1.2
SIGNAL_CRIT_THRESH  = 25.0
SIGNAL_ZERO_THRESH  = 0.0

# ── Audio Detection ─────────────────────────────────
SOUND_RADIUS_WALK   = 5
SOUND_RADIUS_SPRINT = 12
SOUND_RADIUS_CROUCH = 1
SOUND_RADIUS_DOOR   = 15

# ── Enemy ───────────────────────────────────────────
WATCHER_SPEED_DARK    = 4
WATCHER_SPEED_FLICKER = 1.5
WATCHER_SPEED_LIGHT   = 0
WATCHER_DETECT_RANGE  = 14

# ── Colors (Ursina) ─────────────────────────────────
COLOR_BLACK       = color.black
COLOR_RED         = color.rgb(200, 0, 0)
COLOR_DARK_RED    = color.rgb(100, 0, 0)
COLOR_AMBER       = color.rgb(255, 180, 0)
COLOR_GREEN       = color.rgb(0, 220, 80)
COLOR_DANGER      = color.rgb(220, 30, 30)
COLOR_WALL        = color.rgb(15, 15, 15)
COLOR_FLOOR       = color.rgb(20, 20, 20)
COLOR_CEILING     = color.rgb(10, 10, 10)

# ── Game States ─────────────────────────────────────
STATE_TITLE    = "title"
STATE_PLAYING  = "playing"
STATE_PAUSED   = "paused"
STATE_GAMEOVER = "gameover"
STATE_WIN      = "win"

# ── Paths ───────────────────────────────────────────
ASSET_DIR  = "assets"
SPRITE_DIR = f"{ASSET_DIR}/sprites"
SOUND_DIR  = f"{ASSET_DIR}/sounds"
FONT_DIR   = f"{ASSET_DIR}/fonts"
SAVE_FILE  = "saves/save_data.json"