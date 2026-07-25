"""Jugador, proyectiles y jefes (Rey Rana / Espina) - diseño original."""

import math
import pygame

from . import constants as C


class Bullet:
    def __init__(self, x, y, vx, vy, owner, radius=6, color=(255, 240, 200), damage=1):
        self.x, self.y = x, y
        self.vx, self.vy = vx, vy
        self.owner = owner  # "player" o "boss"
        self.radius = radius
        self.color = color
        self.damage = damage
        self.alive = True

    def update(self, dt):
        self.x += self.vx * dt
        self.y += self.vy * dt
        if (self.x < -40 or self.x > C.SCREEN_W + 40 or
                self.y < -40 or self.y > C.SCREEN_H + 40):
            self.alive = False

    def rect(self):
        r = self.radius
        return pygame.Rect(self.x - r, self.y - r, r * 2, r * 2)

    def draw(self, surf):
        pygame.draw.circle(surf, self.color, (int(self.x), int(self.y)), self.radius)


class Player:
    WIDTH, HEIGHT = 28, 42

    def __init__(self, index, x):
        self.index = index
        self.color = C.PLAYER_COLORS[index % len(C.PLAYER_COLORS)]
        self.x = x
        self.y = C.GROUND_Y - self.HEIGHT
        self.vx = 0.0
        self.vy = 0.0
        self.on_ground = True
        self.facing = 1
        self.aim_y = 0
        self.hp = C.PLAYER_MAX_HP
        self.invuln_t = 0.0
        self.dash_t = 0.0
        self.dash_cd = 0.0
        self.shoot_cd = 0.0
        self.alive = True

    def rect(self):
        return pygame.Rect(int(self.x), int(self.y), self.WIDTH, self.HEIGHT)

    def take_hit(self, damage):
        if self.invuln_t > 0 or not self.alive:
            return
        self.hp -= damage
        self.invuln_t = C.PLAYER_INVULN_TIME
        if self.hp <= 0:
            self.hp = 0
            self.alive = False

    def update(self, dt, inp, bullets_out):
        if not self.alive:
            return
        if self.invuln_t > 0:
            self.invuln_t = max(0.0, self.invuln_t - dt)
        if self.dash_cd > 0:
            self.dash_cd = max(0.0, self.dash_cd - dt)
        if self.shoot_cd > 0:
            self.shoot_cd = max(0.0, self.shoot_cd - dt)

        if inp.move_x != 0:
            self.facing = 1 if inp.move_x > 0 else -1
        self.aim_y = inp.aim_y

        if self.dash_t > 0:
            self.dash_t = max(0.0, self.dash_t - dt)
            self.vx = self.facing * C.DASH_SPEED
        else:
            if inp.dash_pressed and self.dash_cd == 0:
                self.dash_t = C.DASH_TIME
                self.dash_cd = C.DASH_COOLDOWN
                self.invuln_t = max(self.invuln_t, C.DASH_TIME + 0.05)
            else:
                target = inp.move_x * C.MAX_RUN_SPEED
                if target != 0:
                    step = C.MOVE_ACCEL * dt
                    if self.vx < target:
                        self.vx = min(target, self.vx + step)
                    else:
                        self.vx = max(target, self.vx - step)
                else:
                    if self.vx > 0:
                        self.vx = max(0.0, self.vx - C.MOVE_FRICTION * dt)
                    else:
                        self.vx = min(0.0, self.vx + C.MOVE_FRICTION * dt)

        if inp.jump_pressed and self.on_ground:
            self.vy = C.JUMP_SPEED
            self.on_ground = False

        self.vy += C.GRAVITY * dt
        self.x += self.vx * dt
        self.y += self.vy * dt

        self.x = max(10, min(C.SCREEN_W - self.WIDTH - 10, self.x))

        floor = C.GROUND_Y - self.HEIGHT
        if self.y >= floor:
            self.y = floor
            self.vy = 0.0
            self.on_ground = True

        if inp.shoot and self.shoot_cd == 0:
            self.shoot_cd = C.SHOOT_COOLDOWN
            dirx, diry = self.facing, 0
            if self.aim_y != 0:
                dirx, diry = 0.35 * self.facing, self.aim_y
                norm = math.hypot(dirx, diry)
                dirx, diry = dirx / norm, diry / norm
            bx = self.x + self.WIDTH / 2 + dirx * 20
            by = self.y + self.HEIGHT / 2 + diry * 10
            bullets_out.append(Bullet(bx, by, dirx * C.BULLET_SPEED,
                                       diry * C.BULLET_SPEED, "player",
                                       color=self.color))

    def draw(self, surf):
        if self.invuln_t > 0 and int(self.invuln_t * 20) % 2 == 0:
            return
        r = self.rect()
        pygame.draw.ellipse(surf, self.color, r)
        eye_x = r.centerx + (6 if self.facing > 0 else -6)
        pygame.draw.circle(surf, C.BLACK, (eye_x, r.top + 12), 3)


class Boss:
    NAME = "Boss"
    MAX_HP = 40

    def __init__(self, x, y):
        self.x, self.y = x, y
        self.hp = self.MAX_HP
        self.phase = 1
        self.timer = 0.0
        self.attack_index = 0
        self.alive = True
        self.hit_flash = 0.0

    def take_hit(self, damage):
        if not self.alive:
            return
        self.hp -= damage
        self.hit_flash = 0.12
        if self.hp <= self.MAX_HP * 0.5 and self.phase == 1:
            self.phase = 2
        if self.hp <= 0:
            self.hp = 0
            self.alive = False

    def rect(self):
        return pygame.Rect(int(self.x - 60), int(self.y - 60), 120, 120)

    def update(self, dt, players, bullets_out):
        if self.hit_flash > 0:
            self.hit_flash = max(0.0, self.hit_flash - dt)


class RanaBoss(Boss):
    """Rey Rana: salto-embestida y lengua a distancia."""
    NAME = "Rey Rana"
    MAX_HP = 50

    def __init__(self, x, y):
        super().__init__(x, y)
        self.base_y = y
        self.vy = 0.0
        self.state = "idle"
        self.crouch = 0.0

    def update(self, dt, players, bullets_out):
        super().update(dt, players, bullets_out)
        if not self.alive:
            return
        self.timer -= dt
        speed_mult = 1.6 if self.phase == 2 else 1.0

        if self.state == "idle":
            self.crouch = min(1.0, self.crouch + dt * 2)
            if self.timer <= 0:
                self.timer = 1.1 / speed_mult
                self.attack_index = (self.attack_index + 1) % 2
                self.state = "jump" if self.attack_index == 0 else "lick"
                self.crouch = 0.0
                if self.state == "jump":
                    self.vy = -520
                    target = min(players, key=lambda p: p.x, default=None)
        elif self.state == "jump":
            self.vy += C.GRAVITY * dt * 0.9
            self.y += self.vy * dt
            if self.y >= self.base_y:
                self.y = self.base_y
                self.vy = 0.0
                self.state = "idle"
                self.timer = 0.9 / speed_mult
                for dxsign in (-1, 1):
                    bullets_out.append(Bullet(self.x, self.y, dxsign * 260, -160,
                                               "boss", radius=8,
                                               color=(120, 220, 90)))
        elif self.state == "lick":
            self.timer_total = getattr(self, "timer_total", 0.35)
            if self.timer <= 0:
                bullets_out.append(Bullet(self.x, self.y - 20,
                                           -420 * speed_mult, 0, "boss",
                                           radius=10, color=(255, 150, 180)))
                self.state = "idle"
                self.timer = 1.0 / speed_mult

    def draw(self, surf):
        color = (255, 255, 255) if self.hit_flash > 0 else (70, 190, 90)
        squash = 1.0 - 0.25 * self.crouch if self.state == "idle" else 1.0
        w, h = 120, int(90 * squash)
        rect = pygame.Rect(int(self.x - w / 2), int(self.y - h), w, h)
        pygame.draw.ellipse(surf, color, rect)
        pygame.draw.circle(surf, color, (int(self.x - 30), int(self.y - h)), 18)
        pygame.draw.circle(surf, color, (int(self.x + 30), int(self.y - h)), 18)
        pygame.draw.circle(surf, C.BLACK, (int(self.x - 30), int(self.y - h - 5)), 5)
        pygame.draw.circle(surf, C.BLACK, (int(self.x + 30), int(self.y - h - 5)), 5)


class EspinaBoss(Boss):
    """Espina: latigazo de enredadera y espinas que brotan del suelo."""
    NAME = "Espina"
    MAX_HP = 55

    def __init__(self, x, y):
        super().__init__(x, y)
        self.spikes = []  # list of [x, telegraph_t, active_t]

    def update(self, dt, players, bullets_out):
        super().update(dt, players, bullets_out)
        if not self.alive:
            return
        self.timer -= dt
        speed_mult = 1.5 if self.phase == 2 else 1.0

        for spike in self.spikes:
            spike[1] -= dt
            if spike[1] <= 0 and spike[2] > 0:
                spike[2] -= dt

        self.spikes = [s for s in self.spikes if s[1] > -0.5]

        if self.timer <= 0:
            self.timer = 1.3 / speed_mult
            self.attack_index = (self.attack_index + 1) % 2
            if self.attack_index == 0 or self.phase == 1:
                for ang_deg in (-20, 0, 20):
                    ang = math.radians(ang_deg)
                    bullets_out.append(Bullet(
                        self.x, self.y - 30,
                        math.sin(ang) * -300 * speed_mult,
                        math.cos(ang) * -260,
                        "boss", radius=7, color=(210, 90, 200)))
            if self.phase == 2 and self.attack_index == 1:
                import random
                for _ in range(3):
                    sx = random.uniform(80, C.SCREEN_W - 80)
                    self.spikes.append([sx, 0.7, 0.4])

    def spike_rects(self):
        rects = []
        for sx, tele, active in self.spikes:
            if tele <= 0 < active:
                rects.append(pygame.Rect(int(sx - 12), C.GROUND_Y - 40, 24, 40))
        return rects

    def draw(self, surf):
        color = (255, 255, 255) if self.hit_flash > 0 else (60, 150, 70)
        pygame.draw.rect(surf, (90, 60, 40), (int(self.x - 10), int(self.y - 20), 20, 40))
        pygame.draw.circle(surf, color, (int(self.x), int(self.y - 60)), 45)
        pygame.draw.circle(surf, (230, 80, 90), (int(self.x), int(self.y - 60)), 20)
        for sx, tele, active in self.spikes:
            base = pygame.Rect(int(sx - 12), C.GROUND_Y - 8, 24, 8)
            if tele > 0:
                pygame.draw.rect(surf, (200, 60, 60), base, 2)
            elif active > 0:
                pygame.draw.polygon(surf, (170, 60, 50), [
                    (sx - 12, C.GROUND_Y), (sx + 12, C.GROUND_Y), (sx, C.GROUND_Y - 40)])
