import pygame as pg

class Shadow:
    def __init__(self, pos, scale):
        self.pos = pos
        self.scale = scale

    def render(self, surface):
        pg.draw.ellipse(surface, (100, 100, 100, 50), pg.rect.Rect(self.pos[0], self.pos[1], self.scale[0], self.scale[1]))