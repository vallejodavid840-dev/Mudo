#!/usr/bin/env python3
"""Isla de Jefes - prototipo run & gun original (no PS3 todavia, ver README).

Controles P1: A/D mover, W saltar, F disparar, LShift dash, flechas arriba/abajo apuntar.
Controles P2: flechas mover/saltar, ENTER disparar, RShift dash.
Controles P3: J/L mover, I saltar, K disparar, O dash.
Controles P4: teclado numerico 4/6 mover, 8 saltar, 5 disparar, + dash.
Si conectas mandos (joysticks), se detectan automaticamente en orden.
"""

import sys
import pygame

from engine import constants as C
from engine.game import Game, BOSS_TYPES


def read_joystick_snapshot(joy):
    return {
        "axis0": joy.get_axis(0) if joy.get_numaxes() > 0 else 0.0,
        "axis1": joy.get_axis(1) if joy.get_numaxes() > 1 else 0.0,
        "button0": joy.get_button(0) if joy.get_numbuttons() > 0 else False,
        "button1": joy.get_button(1) if joy.get_numbuttons() > 1 else False,
        "button2": joy.get_button(2) if joy.get_numbuttons() > 2 else False,
    }


def main():
    pygame.init()
    pygame.joystick.init()
    joysticks = []
    for i in range(pygame.joystick.get_count()):
        j = pygame.joystick.Joystick(i)
        j.init()
        joysticks.append(j)

    num_players = max(1, min(4, len(joysticks) if joysticks else 1))
    if len(sys.argv) > 1:
        try:
            num_players = max(1, min(4, int(sys.argv[1])))
        except ValueError:
            pass

    screen = pygame.display.set_mode((C.SCREEN_W, C.SCREEN_H))
    pygame.display.set_caption("Isla de Jefes - prototipo")
    clock = pygame.time.Clock()

    game = Game(num_players=num_players, joysticks=joysticks)

    running = True
    while running:
        dt = clock.tick(C.FPS) / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                if game.state == "ISLA":
                    if event.key in (pygame.K_LEFT, pygame.K_a):
                        game.selected = (game.selected - 1) % len(BOSS_TYPES)
                    elif event.key in (pygame.K_RIGHT, pygame.K_d):
                        game.selected = (game.selected + 1) % len(BOSS_TYPES)
                    elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                        game.start_selected_level()

        keys = pygame.key.get_pressed()
        joystick_snapshots = [read_joystick_snapshot(j) for j in joysticks] if joysticks else None

        game.update(dt, keys, joystick_snapshots)
        game.draw(screen)
        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
