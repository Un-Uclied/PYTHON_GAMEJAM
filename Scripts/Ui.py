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
        self.render_surf = self.render_surf.convert_alpha()

    def render(self, surface):
        surface.blit(self.render_surf, self.pos)

class VanishingTextUi(TextUi):
    def __init__(self, game, text, pos, font, text_size, color, static_time, vanish_speed):
        super().__init__(text, pos, font, text_size, color)
        self.game = game
        self.static_time = static_time
        self.current_static_time = static_time
        self.vanish_spd = vanish_speed
        self.alpha = 255

    def update(self):
        if self.current_static_time > 0:
            self.current_static_time -= 1
        if self.current_static_time <= 0:
            self.alpha -= self.vanish_spd
            self.render_surf.set_alpha(self.alpha)
        if self.alpha < 0:
            self.game.uis.remove(self)

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
        self.rect = pg.Rect(self.pos[0], self.pos[1], self.render_surface.get_rect().width, self.render_surface.get_rect().height)
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
    def __init__(self, pos, scale, font, font_size, text_color, bg_color, is_private = False, max_len = -1):
        self.rect = pg.Rect(pos[0], pos[1], scale[0], scale[1])
        self.text_color = text_color
        self.color = bg_color
        self.font = font
        self.text = ""
        self.hidden_text = ""
        self.font_size = font_size
        self.active = False
        self.is_private = is_private
        self.max_len = max_len

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
                if self.max_len == -1:
                    self.text += event.unicode
                    if (event.unicode.isalnum() or event.unicode in "-=_+[]{};:'\",.<>/?|\\!@#$%^&*()") and not event.key in (pg.K_LSHIFT, pg.K_RSHIFT, pg.K_LCTRL, pg.K_RCTRL, pg.K_LALT, pg.K_RALT):
                        self.hidden_text += "*"
                else:
                    if len(self.text) < self.max_len:
                        self.text += event.unicode
                        if (event.unicode.isalnum() or event.unicode in "-=_+[]{};:'\",.<>/?|\\!@#$%^&*()") and not event.key in (pg.K_LSHIFT, pg.K_RSHIFT, pg.K_LCTRL, pg.K_RCTRL, pg.K_LALT, pg.K_RALT):
                            self.hidden_text += "*"

    def render(self, surface):
        pg.draw.rect(surface, self.color, self.rect)
        txt_surface = pg.font.Font(self.font, self.font_size).render(self.hidden_text if self.is_private else self.text, True, self.text_color)
        surface.blit(txt_surface, (self.rect.x + 5, self.rect.y + 2))
        pg.draw.rect(surface, self.text_color, self.rect, 2)

class KeyInputField:
    def __init__(self, name, pos, scale, font, font_size, text_color, bg_color, name_pos, max_len = 1):
        self.rect = pg.Rect(pos[0], pos[1], scale[0], scale[1])
        self.name = name
        self.text_color = text_color
        self.color = bg_color
        self.font = font
        self.text = ""
        self.key = 0
        self.font_size = font_size
        self.active = False
        self.max_len = max_len
        self.name_pos = name_pos

    def get_event(self, event : pg.event.Event):
        if event.type == pg.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(event.pos)

        if event.type == pg.KEYDOWN and self.active:
            self.key = event.key
            self.text = pg.key.name(event.key)
            self.active = False

    def render(self, surface):
        pg.draw.rect(surface, self.color, self.rect)
        txt_surface = pg.font.Font(self.font, self.font_size).render("듣는중.." if self.active else self.text, True, self.text_color)
        surface.blit(txt_surface, (self.rect.x + 5, self.rect.y + 2))
        surface.blit(pg.font.Font(self.font, self.font_size).render(self.name, True, self.text_color), self.name_pos)
        pg.draw.rect(surface, self.text_color, self.rect, 2)

class Slider:
    def __init__(self, pos : tuple, size : tuple, init_val, min_val, max_val):
        self.pos = pg.math.Vector2(pos)
        self.size = pg.math.Vector2(size)

        self.center_left = self.pos.x - (self.size.x // 2)
        self.center_right = self.pos.x + (self.size.x // 2)
        self.top = self.pos.y - (self.pos.y // 2)

        self.min = min_val
        self.max = max_val
        self.init_val = (self.center_right - self.center_left) * init_val

        self.btn_size = pg.math.Vector2(30, self.size.y + 10)

        self.bg = pg.Rect(self.center_left, self.top, self.size.x, self.size.y)
        self.btn = pg.Rect(self.center_left + self.init_val, self.top - 5, self.btn_size.x, self.btn_size.y)

        

    def update(self):
        mouse_pos = pg.mouse.get_pos()
        mouse_pressed = pg.mouse.get_pressed()[0]
        if self.bg.collidepoint(mouse_pos) and mouse_pressed:
            self.btn.centerx = mouse_pos[0]
    
    def get_val(self):
        val_range = self.center_right - self.center_left - 10
        btn_val = self.btn.centerx - self.center_left

        return min(max((btn_val / val_range) * (self.max - self.min) + self.min, self.min), self.max)
        

    def render(self, surface):
        pg.draw.rect(surface, "grey", self.bg)
        pg.draw.rect(surface, "white", self.btn)
