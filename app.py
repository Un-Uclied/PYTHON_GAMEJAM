#라이브러리 임포트
import pygame as pg
import pytweening as pt
import sys, math, random, Scripts.shake
from Scripts.Entities import Enemy, Player
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
            print(self.clock.get_fps())
            if (self.game_paused): return
            self.screen.fill("black")
            
            self.delta_time = self.clock.tick(TARGET_FPS) / 1000.0

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

    def state_story_1(self):
        #start:

        while(True):
            #update:
            if (self.game_paused): return
            self.screen.fill("black")

            self.delta_time = self.clock.tick(TARGET_FPS) / 1000.0

            self.screen.blit(self.assets["spider_img"].img(2), (0, 0))
            self.camera.blit(self.screen, (0, 0))
            for event in pg.event.get():
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_ESCAPE:
                        self.state_main_game(0, "spider")
                if event.type == pg.QUIT:
                    pg.quit()
                    sys.exit()

            pg.display.update()

    def state_main_game(self, chapter : int, enemy_name : str):
        #start:

        rand_heart_spawn_speed = (5, 12)
        heart_move_speed = 2

        #enemy
        #enemy = Enemy(self.assets[f"{enemy_name}_img"], [300, 250], (400, 400))
        enemy = UI(pg.transform.scale(self.assets[f"{enemy_name}_img"], (400, 400)), (300, 250))
        self.ui_obejcts.append(enemy)
        player = Player(self.assets["doctor"], [750, 750], (200, 200))
        bg = pg.transform.scale(self.assets["spider_bg"], (1000, 1000))

        enemy.is_turn = True
        is_heart_gaming = False

        bottom_fade = UI(self.assets["bottom_fade"], (0, 1000))
        black_heart = UI(pg.transform.scale(self.assets["black_heart"], (180, 180)), (420, 1000))

        self.ui_obejcts.append(bottom_fade)
        self.ui_obejcts.append(black_heart)

        img_vignette = pg.transform.scale(self.assets["viggnete"], (1000, 1000))

        heart_spawn_timer = random.randrange(rand_heart_spawn_speed[0], rand_heart_spawn_speed[1]) / 10  
        while(True):
            #update:
            
            if (self.game_paused): return
            self.screen.fill("black")

            self.delta_time = self.clock.tick(TARGET_FPS) / 1000.0

            enemy.update()
            player.update()
            for obj in self.ui_obejcts:
                obj.update(self.delta_time)
            
            #bg
            self.screen.blit(bg, (0, 0))

            enemy.render(self.screen)
            player.render(self.screen)

            for obj in self.ui_obejcts:
                obj.render(self.screen)

            if enemy.is_turn:
                if not is_heart_gaming:
                    is_heart_gaming = True
                    bottom_fade.tween_to((0, 500), 3)
                    black_heart.tween_to((420, 800), 5)
                new_timer -= self.delta_time
                if (new_timer <= 0):
                    new_timer = random.randrange(rand_heart_spawn_speed[0], rand_heart_spawn_speed[1]) / 10
                    left_or_right = random.randint(0, 1)
                    new_half_heart = None
                    if left_or_right == 0:
                        new_half_heart = UI(pg.transform.scale(self.assets["blue_heart"], (180, 180)), (-200, 800))
                    elif left_or_right == 1:
                        new_half_heart = UI(pg.transform.scale(self.assets["red_heart"], (180, 180)), (1200, 800))

                    new_half_heart.tween_to((420, 800), heart_move_speed, "linear")

                    self.ui_obejcts.append(new_half_heart)
   
            #ui
            self.screen.blit(vignette, (0, 0))

            self.camera.blit(self.screen, (0, 0))

            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit()
                    sys.exit()

            pg.display.update()

                
            
if __name__ == '__main__':
    game = Game()