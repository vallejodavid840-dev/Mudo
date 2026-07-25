"""Valores compartidos del juego: tamaño de pantalla, física, colores."""

SCREEN_W, SCREEN_H = 960, 540
FPS = 60

GRAVITY = 1400.0
MOVE_ACCEL = 2600.0
MOVE_FRICTION = 2200.0
MAX_RUN_SPEED = 320.0
JUMP_SPEED = -620.0
DASH_SPEED = 720.0
DASH_TIME = 0.16
DASH_COOLDOWN = 0.6
SHOOT_COOLDOWN = 0.22
BULLET_SPEED = 560.0
PLAYER_MAX_HP = 6
PLAYER_INVULN_TIME = 1.0

GROUND_Y = SCREEN_H - 80

PLAYER_COLORS = [
    (255, 210, 60),   # P1 amarillo
    (90, 200, 255),   # P2 celeste
    (255, 110, 160),  # P3 rosa
    (140, 255, 140),  # P4 verde
]

WHITE = (240, 240, 240)
BLACK = (15, 15, 20)
BG_SKY = (25, 20, 45)
BG_HILL = (40, 30, 70)
