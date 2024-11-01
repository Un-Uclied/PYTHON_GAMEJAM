import pygame as pg
import pytweening as pt, math
from Scripts.utils import open_site

class TextUi:
    def __init__(self, text : str, pos : tuple, font : str, text_size : int, color : pg.Color):
        self.text = text
        self.pos = pos
        self.text_size = text_size
        self.font = font
        self.color = color
        self.render_surf = pg.font.Font(self.font, self.text_size).render(self.text, True, color)

    def update(self):
        self.render_surf = pg.font.Font(self.font, self.text_size).render(self.text, True, self.color)

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

class ClickableUi:
    def __init__(self, surface : pg.Surface, pos : tuple, hover_audio : pg.mixer.Sound):
        self.render_surface = surface
        self.hovering = False
        self.pos = pg.math.Vector2(pos[0], pos[1])
        self.rect = pg.Rect(self.pos[0], self.pos[1], surface.get_rect().width, surface.get_rect().height)

        self.hover_audio = hover_audio

    def update(self):
        self.rect = pg.Rect(self.pos[0], self.pos[1], surface.get_rect().width, surface.get_rect().height)
        if self.rect.collidepoint(pg.mouse.get_pos()[0], pg.mouse.get_pos()[1]):
            if not self.hovering:
                self.on_hovered()
                
            self.hovering = True
        else:
            self.hovering = False

    def on_hovered(self):
        self.hover_audio.play()

    def render(self, surface):
        surface.blit(self.render_surface, self.pos)

class ButtonUi(ClickableUi):
    def __init__(self, image : pg.Surface, pos : tuple, hover_audio : pg.mixer.Sound):
        self.image = image
        super().__init__(image, pos, hover_audio)

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
        surface.blit(self.render_surface, (self.pos[0] + self.render_offset[0], self.pos[1] + self.render_offset[1]))

class TextButton(ClickableUi):
    def __init__(self, text, font : pg.font.Font, text_size, pos, hover_audio, color, hovered_color):
        super().__init__(pg.font.Font(font, text_size).render(text, True, color), pos, hover_audio)

        self.un_hover_color = color
        self.hovered_color = hovered_color
        self.current_color = self.un_hover_color

        self.font = font
        self.text_size = text_size
        self.text = text

        self.render_surface = pg.font.Font(self.font, self.text_size).render(self.text, True, self.current_color)

    def update(self):
        super().update()
        if self.hovering:
            self.current_color = self.hovered_color
        else:
            self.current_color = self.un_hover_color

        self.render_surface = pg.font.Font(self.font, self.text_size).render(self.text, True, self.current_color)

class InputField:
    def __init__(self, pos, scale, font, font_size, text_color, bg_color, is_private = False):
        self.rect = pg.Rect(pos[0], pos[1], scale[0], scale[1])
        self.text_color = text_color
        self.color = bg_color
        self.font = font
        self.text = ""
        self.hidden_text = ""
        self.font_size = font_size
        self.active = False
        self.is_private = is_private

    def get_event(self, event):
        if event.type == pg.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(event.pos)

        if event.type == pg.KEYDOWN and self.active:
            if event.key == pg.K_BACKSPACE:
                self.text = self.text[:-1]
                self.hidden_text = self.hidden_text[:-1]
            elif event.key == pg.K_RETURN:
                self.active = False
            else:
                self.text += event.unicode
                if (event.unicode.isalnum() or event.unicode in "-=_+[]{};:'\",.<>/?|\\!@#$%^&*()") and not event.key in (pg.K_LSHIFT, pg.K_RSHIFT, pg.K_LCTRL, pg.K_RCTRL, pg.K_LALT, pg.K_RALT):
                    self.hidden_text += "*"

    def render(self, surface):
        pg.draw.rect(surface, self.color, self.rect)
        txt_surface = pg.font.Font(self.font, self.font_size).render(self.hidden_text if self.is_private else self.text, True, self.text_color)
        surface.blit(txt_surface, (self.rect.x + 5, self.rect.y + 5))
        pg.draw.rect(surface, self.text_color, self.rect, 2)