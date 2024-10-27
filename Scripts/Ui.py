import pygame as pg
import pytweening as pt, math
from Scripts.utils import open_site

class TextUi:
    def __init__(self, text : str, pos : tuple, font : str, text_size : int, color : pg.Color):
        self.text = text
        self.pos = pos
        self.text_size = text_size
        self.font = font

        self.render_surf = pg.font.Font(self.font, self.text_size).render(self.text, True, "white")

    def render(self, surface):
        surface.blit(self.render_surf, self.pos)

class LinkUi(TextUi):
    def __init__(self, text, pos, font, text_size, color, hover_color, hover_audio : pg.mixer.Sound, link : str):
        super().__init__(text, pos, font, text_size, color)

        self.rect = pg.Rect(self.pos[0], self.pos[1], self.render_surf.get_rect().width, self.render_surf.get_rect().height)

        self.hovering = False
        self.hover_audio = hover_audio
        self.link = link

        self.current_color = color
        self.hover_color = hover_color
        self.color = color

    def update(self):
        mouse_click = pg.mouse.get_pressed(3)[0]
        if self.rect.collidepoint(pg.mouse.get_pos()[0], pg.mouse.get_pos()[1]):
            if not self.hovering:
                self.on_hovered()
                
            self.hovering = True
            if mouse_click:
                open_site(self.link)
                
        else:
            self.current_color = self.color
            self.hovering = False

        self.render_surf = pg.font.Font(self.font, self.text_size).render(self.text, True, self.current_color)

    def on_hovered(self):
        self.current_color = self.hover_color
        self.hover_audio.play()


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

class WiggleButtonUi(ButtonUi):
    def __init__(self, image, pos, hover_audio, wiggle_speed, wiggle_amount):
        super().__init__(image, pos, hover_audio)
        self.elapsed_time = 0
        self.wiggle_speed = wiggle_speed
        self.wiggle_amount = wiggle_amount

        self.render_offset = [0, 0]

    def update(self):
        super().update()
        self.elapsed_time += .01 * self.wiggle_speed

    def wiggle(self):
        tween_value = pt.easeInOutSine((self.elapsed_time % 2) / 2)
        self.render_offset[0] = math.sin(tween_value * math.pi * 2) * self.wiggle_amount

    def render(self, surface):
        surface.blit(self.image, (self.pos[0] + self.render_offset[0], self.pos[1] + self.render_offset[1]))