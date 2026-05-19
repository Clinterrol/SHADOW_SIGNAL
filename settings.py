# settings.py

# ── Window ──────────────────────────────────────────
TITLE         = "SHADOW SIGNAL"
SCREEN_WIDTH  = 900
SCREEN_HEIGHT = 600
FPS           = 60
TILE_SIZE     = 32

# ── Colors ──────────────────────────────────────────
BLACK         = (0,   0,   0)
WHITE         = (255, 255, 255)
RED           = (200, 0,   0)
DARK_RED      = (100, 0,   0)
DIM_GRAY      = (20,  20,  20)
FLICKER_GRAY  = (40,  40,  40)
AMBER         = (255, 180, 0)
GREEN_SIGNAL  = (0,   220, 80)
DANGER_RED    = (220, 30,  30)

# ── Player ──────────────────────────────────────────
PLAYER_SPEED        = 160        # px/sec walking
PLAYER_SPRINT_SPEED = 280        # px/sec sprinting
PLAYER_CROUCH_SPEED = 70         # px/sec crouching
PLAYER_MAX_HEALTH   = 100

# ── Flashlight ──────────────────────────────────────
FLASHLIGHT_MAX_BATTERY  = 100.0
FLASHLIGHT_DRAIN_RATE   = 2.5    # per second (normal use)
FLASHLIGHT_OVERHEAT_MAX = 100.0
FLASHLIGHT_HEAT_RATE    = 15.0   # per second while ON
FLASHLIGHT_COOL_RATE    = 8.0    # per second while OFF
FLASHLIGHT_RADIUS       = 180    # px, cone light radius

# ── Signal System ───────────────────────────────────
SIGNAL_MAX          = 100.0
SIGNAL_DECAY_RATE   = 1.2        # per second passive decay
SIGNAL_CRIT_THRESH  = 25.0       # below this → danger state
SIGNAL_ZERO_THRESH  = 0.0        # total blackout

# ── Audio Detection ─────────────────────────────────
SOUND_RADIUS_WALK   = 80         # px
SOUND_RADIUS_SPRINT = 200        # px
SOUND_RADIUS_CROUCH = 20         # px
SOUND_RADIUS_DOOR   = 250        # px

# ── Enemy ───────────────────────────────────────────
WATCHER_SPEED_DARK    = 140      # px/sec full dark
WATCHER_SPEED_FLICKER = 55       # px/sec during flicker
WATCHER_SPEED_LIGHT   = 0        # frozen in light
WATCHER_DETECT_RANGE  = 220      # px

# ── Game States ─────────────────────────────────────
STATE_TITLE     = "title"
STATE_PLAYING   = "playing"
STATE_PAUSED    = "paused"
STATE_GAMEOVER  = "gameover"
STATE_WIN       = "win"

# ── Paths ───────────────────────────────────────────
ASSET_DIR   = "assets"
SPRITE_DIR  = f"{ASSET_DIR}/sprites"
SOUND_DIR   = f"{ASSET_DIR}/sounds"
FONT_DIR    = f"{ASSET_DIR}/fonts"
SAVE_FILE   = "saves/save_data.json"