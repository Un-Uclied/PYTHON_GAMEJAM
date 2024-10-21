import pygame as pg
import sys, math, random, Scripts.shake

SCREEN_SCALE = (1920 / 2 - 100, 1080 / 2 + 400 - 100)
GAME_NAME = "DR.Mind"
TARGET_FPS = 60

class Game:
    def __init__(self):
        pg.init()
        pg.display.set_caption(GAME_NAME)
        self.camera = pg.display.set_mode(SCREEN_SCALE)
        self.screen = pg.surface.Surface(SCREEN_SCALE)
        self.clock = pg.time.Clock()
        
        self.game_paused = False

        self.screen_shake = Scripts.shake.Shake(self.clock)

        self.assets = {
            
        }

        self.sfxs = {

        }

        self.fonts = {

        }

        self.entities = {

        }

        self.start()

    def start(self):
        while(True):
            self.update()

    def update(self):
        if (self.game_paused): return

        
        pg.draw.rect(self.screen, "blue", (100, 100, 100, 100))
        #shake_random = (random.random() * self.screen_shake_gain - self.screen_shake_gain / 2, random.random() * self.screen_shake_gain - self.screen_shake_gain / 2)
        #self.screen_shake_gain = max(0, self.screen_shake_gain - .1)
        pg.Surface.blit(self.camera, self.screen, (0, 0))

        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()

        pg.display.update()
        self.clock.tick(TARGET_FPS)
                
            
if __name__ == '__main__':
    game = Game()