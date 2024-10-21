#라이브러리 임포트
import pygame as pg
import pytweening as pt
import sys, math, random, Scripts.shake
from Scripts.utils import load_image, load_images, Animation, get_surface_center_to, ImageSets, load_images

#상수 설정
SCREEN_SCALE = (1000, 1000)
GAME_NAME = "DR.Mind"
TARGET_FPS = 60

#게임 클래스
class Game:
    def __init__(self):
        #init함수
        pg.init()
        pg.display.set_caption(GAME_NAME)
        self.camera = pg.display.set_mode(SCREEN_SCALE)
        self.screen = pg.surface.Surface(SCREEN_SCALE)
        self.clock = pg.time.Clock()
        
        self.game_paused = False

        self.screen_shake = Scripts.shake.Shake(self.clock)

        self.assets = {
            "main_title" : load_image("UI/MainTitle.png"),
            "spider_img" : ImageSets(load_images("Characters/Traumas/Spider")),
            "spider_bg" : load_image("Backgrounds/SpiderBackground.png"),
        }

        self.sfxs = {

        }

        self.fonts = {
            "main_title_font" : pg.font.Font('Assets/Fonts/Galmuri11-Bold.ttf', 12),
        }

        self.entities = {

        }

        self.state_title_screen()
    
    def state_title_screen(self):
        #start:
        start_key = pg.K_SPACE
        while(True):
            #update:
            if (self.game_paused): return

            press_to_start = pg.transform.scale2x(self.fonts["main_title_font"].render("스페이스바로 시작", False, "white"))
            self.screen.blit(press_to_start, get_surface_center_to(press_to_start, (600, SCREEN_SCALE[1] - 100)))
            self.screen.blit(pg.transform.scale2x(self.assets["main_title"]), get_surface_center_to(self.assets["main_title"], (SCREEN_SCALE[0] / 2, 200)))
            
            
            self.camera.blit(self.screen, (0, 0))

            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit()
                    sys.exit()
                if event.type == pg.KEYDOWN:
                    if event.key == start_key:
                        self.state_story_1()
                        return


            pg.display.flip()
            self.clock.tick(TARGET_FPS)

    def state_story_1(self):
        #start:

        while(True):
            #update:
            self.screen.fill("black")
            if (self.game_paused): return
            
            self.screen.blit(self.assets["spider_img"].img(2), (0, 0))
            self.camera.blit(self.screen, (0, 0))

            for event in pg.event.get():
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_ESCAPE:
                        self.state_main_game(0)
                if event.type == pg.QUIT:
                    pg.quit()
                    sys.exit()

            pg.display.flip()
            self.clock.tick(TARGET_FPS)

    def state_main_game(self, chapter : int):
        #start:

        while(True):
            #update:
            self.screen.fill("black")
            if (self.game_paused): return
            
            self.screen.blit(pg.transform.scale(self.assets["spider_bg"], (1000, 1000)), (0, 0))
            self.screen.blit(pg.transform.scale(self.assets["spider_img"].img(2)), (0, 0))
            self.camera.blit(self.screen, (0, 0))

            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit()
                    sys.exit()

            pg.display.flip()
            self.clock.tick(TARGET_FPS)

                
            
if __name__ == '__main__':
    game = Game()