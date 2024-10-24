import pygame as pg

class TextUi:
    def __init__(self, text : str, pos : tuple, font : str, text_size : int, color : pg.Color):
        self.text = text
        self.pos = pos
        self.text_size = text_size
        self.font = font

    def render(self, surface):
        surface.blit(pg.font.Font(self.font, self.text_size).render(self.text, True, "white"), self.pos)