import pygame as pg, math, random
from Scripts.Particles import Spark


class Bullet:
    def __init__(self, game, spawn_pos : tuple, direction : pg.math.Vector2, speed : float, sprite : pg.Surface, timer : float, tag : str):
        self.pos = list(spawn_pos)
        self.direction = direction.normalize() * speed
        self.sprite = sprite
        self.timer = timer
        self.tag = tag
        self.rect = pg.Rect(spawn_pos[0] - sprite.get_size()[0], spawn_pos[1] - sprite.get_size()[1], sprite.get_size()[0], sprite.get_size()[1])

        self.game = game

    def destroy(self):
        pass

    def update(self):
        pass

    def render(self, surface : pg.Surface):
        surface.blit(self.sprite, self.pos)

class PlayerBullet(Bullet):

    def destroy(self):
        for i in range(10):
            self.game.sparks.append(Spark(self.pos, math.radians(360) * random.random(), 3.5, "yellow"))

    def update(self):
        self.pos[0] += self.direction.x
        self.pos[1] += self.direction.y
        