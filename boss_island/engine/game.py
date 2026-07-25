"""Maquina de estados: MENU -> ISLA (hub) -> PELEA -> ISLA ..."""

import pygame

from . import constants as C
from .entities import Player, RanaBoss, EspinaBoss
from .input_map import PlayerController

BOSS_TYPES = [RanaBoss, EspinaBoss]


class Game:
    def __init__(self, num_players=1, joysticks=None):
        self.num_players = max(1, min(4, num_players))
        self.controllers = [PlayerController(i, joysticks[i] if joysticks and i < len(joysticks) else None)
                             for i in range(self.num_players)]
        self.state = "ISLA"
        self.selected = 0
        self.defeated = [False] * len(BOSS_TYPES)
        self.players = []
        self.boss = None
        self.bullets = []
        self.message_t = 0.0
        self.message = ""

    def _spawn_level(self):
        self.players = []
        spacing = 60
        start_x = C.SCREEN_W / 2 - (self.num_players - 1) * spacing / 2
        for i in range(self.num_players):
            self.players.append(Player(i, start_x + i * spacing - Player.WIDTH / 2))
        boss_cls = BOSS_TYPES[self.selected]
        self.boss = boss_cls(C.SCREEN_W / 2, C.GROUND_Y)
        self.bullets = []

    def start_selected_level(self):
        self._spawn_level()
        self.state = "PELEA"

    def update(self, dt, keys, joystick_snapshots=None):
        if self.state == "ISLA":
            self._update_hub(dt, keys)
        elif self.state == "PELEA":
            self._update_fight(dt, keys, joystick_snapshots)
        elif self.state in ("GANASTE", "PERDISTE"):
            self.message_t -= dt
            if self.message_t <= 0:
                self.state = "ISLA"

    def _update_hub(self, dt, keys):
        pass  # navegacion se maneja por eventos discretos en main.py

    def _update_fight(self, dt, keys, joystick_snapshots):
        new_bullets = []
        for i, p in enumerate(self.players):
            snap = joystick_snapshots[i] if joystick_snapshots and i < len(joystick_snapshots) else None
            inp = self.controllers[i].read(keys, snap)
            p.update(dt, inp, new_bullets)

        self.boss.update(dt, self.players, new_bullets)
        self.bullets.extend(new_bullets)

        for b in self.bullets:
            b.update(dt)

        for b in self.bullets:
            if not b.alive:
                continue
            if b.owner == "player" and self.boss.alive:
                if b.rect().colliderect(self.boss.rect()):
                    self.boss.take_hit(1)
                    b.alive = False
            elif b.owner == "boss":
                for p in self.players:
                    if p.alive and b.rect().colliderect(p.rect()):
                        p.take_hit(1)
                        b.alive = False
                        break

        if hasattr(self.boss, "spike_rects"):
            for rect in self.boss.spike_rects():
                for p in self.players:
                    if p.alive and rect.colliderect(p.rect()):
                        p.take_hit(1)

        self.bullets = [b for b in self.bullets if b.alive]

        if not self.boss.alive:
            self.defeated[self.selected] = True
            self.state = "GANASTE"
            self.message = f"{self.boss.NAME} derrotado!"
            self.message_t = 2.5
        elif all(not p.alive for p in self.players):
            self.state = "PERDISTE"
            self.message = "El grupo cayo... vuelvan a intentar"
            self.message_t = 2.5

    def draw(self, surf):
        surf.fill(C.BG_SKY)
        pygame.draw.rect(surf, C.BG_HILL, (0, C.GROUND_Y, C.SCREEN_W, C.SCREEN_H - C.GROUND_Y))

        if self.state == "ISLA":
            self._draw_hub(surf)
        elif self.state == "PELEA":
            for b in self.bullets:
                b.draw(surf)
            self.boss.draw(surf)
            for p in self.players:
                p.draw(surf)
            self._draw_hud(surf)
        else:
            font = pygame.font.SysFont(None, 48)
            text = font.render(self.message, True, C.WHITE)
            surf.blit(text, text.get_rect(center=(C.SCREEN_W / 2, C.SCREEN_H / 2)))

    def _draw_hub(self, surf):
        font = pygame.font.SysFont(None, 40)
        title = font.render("ISLA - elige un jefe (<-/-> y ENTER)", True, C.WHITE)
        surf.blit(title, (30, 30))
        positions = [(C.SCREEN_W * 0.3, C.GROUND_Y - 40), (C.SCREEN_W * 0.7, C.GROUND_Y - 40)]
        small = pygame.font.SysFont(None, 28)
        for i, boss_cls in enumerate(BOSS_TYPES):
            x, y = positions[i]
            color = (255, 220, 60) if i == self.selected else (150, 150, 170)
            pygame.draw.circle(surf, color, (int(x), int(y)), 50, 0 if i == self.selected else 3)
            label = small.render(boss_cls.NAME, True, C.WHITE)
            surf.blit(label, label.get_rect(center=(x, y + 80)))
            if self.defeated[i]:
                done = small.render("DERROTADO", True, (120, 255, 120))
                surf.blit(done, done.get_rect(center=(x, y - 80)))

    def _draw_hud(self, surf):
        font = pygame.font.SysFont(None, 26)
        for i, p in enumerate(self.players):
            hp_text = font.render(f"P{i+1}: {'*' * max(0, p.hp)}", True, p.color)
            surf.blit(hp_text, (16, 16 + i * 24))
        pygame.draw.rect(surf, (60, 20, 30), (C.SCREEN_W - 220, 16, 200, 18))
        ratio = max(0.0, self.boss.hp / self.boss.MAX_HP)
        pygame.draw.rect(surf, (220, 60, 70), (C.SCREEN_W - 220, 16, int(200 * ratio), 18))
        name = font.render(self.boss.NAME, True, C.WHITE)
        surf.blit(name, (C.SCREEN_W - 220, 38))
