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
    def __init__(self, image : pg.Surface, pos : tuple, hover_audio : pg.mixer.Sound):
        self.image = image
        self.hovering = False
        self.pos = pos
        self.rect = pg.Rect(self.pos[0], self.pos[1], image.get_rect().width, image.get_rect().height)

        self.hover_audio = hover_audio

    def update(self):
        if self.rect.collidepoint(pg.mouse.get_pos()[0], pg.mouse.get_pos()[1]):
            if not self.hovering:
                self.on_hovered()
                
            self.hovering = True
        else:
            self.hovering = False

    def on_hovered(self):
        self.hover_audio.play()

    def render(self, surface):
        surface.blit(self.image, self.pos)