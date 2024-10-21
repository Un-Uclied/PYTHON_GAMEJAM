import pygame as pg
import pytweening as pt
from Scripts.utils import ImageSets

ENEMY_BOB_SPEED = 0.01
ENEMY_BOB_RANGE = 20

class Entity:
    def __init__(self, position : list, size : tuple):
        self.is_turn = False
        self.pos = position
        self.scale = size
        self.start_position = position

    
        

class Enemy(Entity):
    def __init__(self, imgs : ImageSets, position : list, size : tuple):
        self.imgs = imgs
        super().__init__(position, size)
        self.current_level = 2
        
        #bob
        self.bob_offs = 0
        self.bob_step = 0

    def update(self):
        self.bob_step += ENEMY_BOB_SPEED + (self.current_level * 0.01)
        self.bob_offs = (pt.easeInOutSine(self.bob_step) * ENEMY_BOB_RANGE)
        self.pos = [self.start_position[0], self.start_position[1] + self.bob_offs]

    def render(self, surface : pg.Surface):
        surface.blit(pg.transform.scale(self.imgs.img(self.current_level), self.scale), self.pos)

    


class Player(Entity):
    def __init__(self, img, position : list, size : tuple):
        self.img = img
        super().__init__(position, size)

        #bob
        self.bob_offs = 0
        self.bob_step = 0

    def update(self):
        self.bob_step += 0.01
        self.bob_offs = (pt.easeInOutSine(self.bob_step) * 10)
        self.pos = [self.start_position[0], self.start_position[1] + self.bob_offs]

    def render(self, surface : pg.Surface):
        surface.blit(pg.transform.scale(self.img, self.scale), self.pos)