import pygame as pg

class TextUi:
    def __init__(self, text : str, pos : tuple, font : str, text_size : int, color : pg.Color):
        self.text = text
        self.pos = pos
        self.text_size = text_size
        self.font = font

    def render(self, surface):
        surface.blit(pg.font.Font(self.font, self.text_size).render(self.text, True, "white"), self.pos)

class ButtonUi:
    def __init__(self, image : pg.Surface, pos : tuple):
        self.image = image
        self.rect = image.get_rect()
        self.hovering = False
        self.pos = pos

    def update(self):
        if self.rect.collidepoint(pg.mouse.get_pos()[0], pg.mouse.get_pos()[1]):
            self.hovering = True

    def render(self, surface):
        surface.blit(self.image, self.pos)