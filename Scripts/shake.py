import pygame as pg

class Shake:
    def __init__(self, clock : pg.time.Clock):
        self.current_shake_gain = 0
        self.clock = clock
    
    def add_shake(self, gain : float, duration : float):
        pass

    def update(self):
        pass