import pygame as pg, math, random
from Scripts.Particles import Spark


class Bullet:
    def __init__(self, game, spawn_pos : tuple, direction : pg.math.Vector2, speed : float, sprite : pg.Surface, timer : float, tag : str, shoot_by, damage : int):
        self.pos = pg.math.Vector2(spawn_pos[0], spawn_pos[1])
        self.speed = speed
        self.direction = direction.normalize() * speed
        self.sprite = sprite
        self.max_timer = timer
        self.timer = timer
        self.tag = tag
        self.rect = pg.Rect(self.pos.x - sprite.get_size()[0], spawn_pos.y - sprite.get_size()[1], sprite.get_size()[0], sprite.get_size()[1])
        self.shoot_by = shoot_by

        self.damage = damage

        self.game = game

    def destroy(self):
        for i in range(10):
            self.game.sparks.append(Spark(self.pos, math.radians(360) * random.random(), 3.5, "black"))

    def update(self):
        self.pos.x += self.direction.x
        self.pos.y += self.direction.y

    def render(self, surface : pg.Surface):
        surface.blit(self.sprite, self.pos)

class PlayerBullet(Bullet):

    def destroy(self):
        for i in range(10):
            self.game.sparks.append(Spark(self.pos, math.radians(360) * random.random(), 3.5, "yellow"))

class BossBullet(Bullet):
    def destroy(self):
        for i in range(10):
            self.game.sparks.append(Spark(self.pos, math.radians(360) * random.random(), 3.5, "green"))
        