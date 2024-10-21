import pygame as pg
from Scripts.utils import ImageSets

class Entity:
    def __init__(self, imgs : ImageSets, position : tuple, size : tuple):
        self.is_turn = False
        self.pos = position
        self.scale = size
    def render(self, surface : pg.Surface):
        surface.blit(pg.transform.scale(self.imgs.img(self.current_level), self.scale), self.pos)

class Enemy(Entity):
    def __init__(self):
        self.current_level = 2

    


class Player(Entity):
    def __init__(self):
        pass