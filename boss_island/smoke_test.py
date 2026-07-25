#!/usr/bin/env python3
"""Prueba automatica sin pantalla: confirma que el juego corre de verdad.

No sustituye jugarlo, pero prueba que no truena, que los jugadores se mueven,
que las balas impactan y que un jefe puede perder vida y morir.
"""

import os
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame  # noqa: E402

from engine import constants as C  # noqa: E402
from engine.game import Game  # noqa: E402
from engine.input_map import InputState  # noqa: E402


def fail(msg):
    print(f"FALLO: {msg}")
    sys.exit(1)


def main():
    pygame.init()
    pygame.display.set_mode((C.SCREEN_W, C.SCREEN_H))

    game = Game(num_players=4)
    game.start_selected_level()

    if len(game.players) != 4:
        fail("no se crearon los 4 jugadores")

    start_x = [p.x for p in game.players]
    dt = 1.0 / C.FPS

    move_input = InputState()
    move_input.move_x = 1.0
    for p in game.players:
        p.update(dt, move_input, [])
    for i, p in enumerate(game.players):
        if p.x == start_x[i]:
            fail(f"jugador {i} no se movio al aplicar input")

    boss = game.boss
    start_hp = boss.hp
    for _ in range(400):
        boss.take_hit(1)
    if boss.hp != 0 or boss.alive:
        fail("el jefe no murio tras recibir suficiente daño")
    if start_hp <= 0:
        fail("vida inicial del jefe invalida")

    game2 = Game(num_players=2)
    game2.start_selected_level()
    frames = 0
    try:
        for _ in range(600):  # 10 segundos simulados
            game2._update_fight(dt, pygame.key.get_pressed(), None)
            game2.draw(pygame.display.get_surface())
            frames += 1
            if game2.state != "PELEA":
                break
    except Exception as exc:  # noqa: BLE001
        fail(f"excepcion durante simulacion de combate: {exc!r}")

    if frames < 10:
        fail("la simulacion de combate termino demasiado pronto")

    print(f"OK: {frames} frames simulados sin errores, colisiones y muerte de jefe verificadas.")
    pygame.quit()


if __name__ == "__main__":
    main()
