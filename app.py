#라이브러리 임포트
import pygame as pg
import pytweening as pt
import sys, math, random, Scripts.shake
from Scripts.Entities import Enemy, Player
from Scripts.Tilemap import Tilemap
from Scripts.utils import load_image, load_images, Animation, get_surface_center_to, ImageSets, load_images, Tweener, UI

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
        self.delta_time = 0
        self.clock = pg.time.Clock()
        
        self.game_paused = False

        self.screen_shake = Scripts.shake.Shake(self.clock)

        self.ui_obejcts = []

        self.assets = {
            "main_title" : load_image("UI/MainTitle.png"),
            
            "viggnete" : load_image("UI/Vignette.png"),
            "bottom_fade" : load_image("UI/BottomFade.png"),

            "spider_img" : ImageSets(load_images("Characters/Traumas/Spider")),
            "spider_bg" : load_image("Backgrounds/SpiderBackground.png"),

            "doctor" : load_image("Characters/Doctor.png"),

            "black_heart" : load_image("UI/BlackHeart.png"),
            "yellow_heart" : load_image("UI/YellowHeart.png"),
            "blue_heart" : load_image("UI/BlueHeart.png"),
            "red_heart" : load_image("UI/RedHeart.png"),

            "floor" : load_images('Tiles/Floor'),
            "wall" : load_images('Tiles/Wall'),
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
            self.screen.fill("black")
            
            self.delta_time = self.clock.tick(TARGET_FPS) / 1000.0

            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit()
                    sys.exit()
                if event.type == pg.KEYDOWN:
                    if event.key == start_key:
                        self.state_main_game()
                        return

            pg.display.update()

    def state_main_game(self):
       #start:
        tilemap = Tilemap(self, 32)
        tilemap.load("new_map.json")
        pos = 0
        while(True):
            #update:
            self.screen.fill("black")
            
            self.delta_time = self.clock.tick(TARGET_FPS) / 1000.0
            tilemap.render(self.screen, (0, 0))
            pos += 1
            self.screen.blit(self.assets["doctor"], (pos, 0))
            self.camera.blit(self.screen, (0,0))

            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit()
                    sys.exit()

            pg.display.update()

                
            
if __name__ == '__main__':
    game = Game()