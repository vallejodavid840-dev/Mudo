"""Mapeo de entradas para hasta 4 jugadores: mando si hay, teclado si no."""

import pygame

KEYBOARD_SCHEMES = [
    {"left": pygame.K_a, "right": pygame.K_d, "jump": pygame.K_w,
     "dash": pygame.K_LSHIFT, "shoot": pygame.K_f,
     "aim_up": pygame.K_UP, "aim_down": pygame.K_DOWN},
    {"left": pygame.K_LEFT, "right": pygame.K_RIGHT, "jump": pygame.K_UP,
     "dash": pygame.K_RSHIFT, "shoot": pygame.K_RETURN,
     "aim_up": pygame.K_PAGEUP, "aim_down": pygame.K_PAGEDOWN},
    {"left": pygame.K_j, "right": pygame.K_l, "jump": pygame.K_i,
     "dash": pygame.K_o, "shoot": pygame.K_k,
     "aim_up": pygame.K_u, "aim_down": pygame.K_m},
    {"left": pygame.K_KP4, "right": pygame.K_KP6, "jump": pygame.K_KP8,
     "dash": pygame.K_KP_PLUS, "shoot": pygame.K_KP5,
     "aim_up": pygame.K_KP7, "aim_down": pygame.K_KP1},
]


class InputState:
    __slots__ = ("move_x", "jump", "jump_pressed", "dash", "dash_pressed",
                 "shoot", "aim_y")

    def __init__(self):
        self.move_x = 0.0
        self.jump = False
        self.jump_pressed = False
        self.dash = False
        self.dash_pressed = False
        self.shoot = False
        self.aim_y = 0


class PlayerController:
    """Lee un joystick si existe para este índice, si no cae a teclado."""

    def __init__(self, player_index, joystick=None):
        self.index = player_index
        self.joystick = joystick
        self.scheme = KEYBOARD_SCHEMES[player_index % len(KEYBOARD_SCHEMES)]
        self._prev_jump = False
        self._prev_dash = False

    def read(self, keys, joystick_snapshot=None):
        state = InputState()
        if self.joystick is not None and joystick_snapshot is not None:
            axis_x = joystick_snapshot.get("axis0", 0.0)
            state.move_x = axis_x if abs(axis_x) > 0.25 else 0.0
            state.jump = joystick_snapshot.get("button0", False)
            state.dash = joystick_snapshot.get("button1", False)
            state.shoot = joystick_snapshot.get("button2", False)
            axis_y = joystick_snapshot.get("axis1", 0.0)
            state.aim_y = -1 if axis_y < -0.4 else (1 if axis_y > 0.4 else 0)
        else:
            s = self.scheme
            if keys[s["left"]]:
                state.move_x -= 1.0
            if keys[s["right"]]:
                state.move_x += 1.0
            state.jump = keys[s["jump"]]
            state.dash = keys[s["dash"]]
            state.shoot = keys[s["shoot"]]
            if keys[s["aim_up"]]:
                state.aim_y = -1
            elif keys[s["aim_down"]]:
                state.aim_y = 1

        state.jump_pressed = state.jump and not self._prev_jump
        state.dash_pressed = state.dash and not self._prev_dash
        self._prev_jump = state.jump
        self._prev_dash = state.dash
        return state
