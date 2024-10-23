#라이브러리 임포트
import pygame as pg
import sys
from Scripts.utils import load_image, load_images
from Scripts.Shadows import Shadow
from Scripts.Entities import Entity, MoveableEntity, Player
from Scripts.Animations import Animation

#상수 설정
SCREEN_SCALE = (1800, 800)
GAME_NAME = "Game"
TARGET_FPS = 60
#TARGET_TILE = 40

#입력 설정
KEY_JUMP = pg.K_SPACE
#마우스 입력 설정
WEAPON_ATTACK = 1

#게임 클래스
class Game:
    #게임 생성자
    def __init__(self):
        #init함수
        pg.init()
        pg.display.set_caption(GAME_NAME)

        self.camera = pg.display.set_mode(SCREEN_SCALE)
        self.screen = pg.surface.Surface(SCREEN_SCALE, pg.SRCALPHA)
        self.ui = pg.surface.Surface(SCREEN_SCALE, pg.SRCALPHA)

        self.clock = pg.time.Clock()

        #게임 에셋
        self.assets = {
            #UI에셋
            "ui" : { 
                "viggnete" : load_image("UI/Vignette.png"),
                "bottom_fade" : load_image("UI/BottomFade.png")
            },
            
            #타일맵 이미지 에셋
            "tiles" : {
                "floor" : load_images("Tiles/Floor"),
                "wall" : load_images("Tiles/Wall"),
            },
            
            "entities" : {
                "player/idle" : Animation(load_images("Characters/Player"), 3, True)
            },

            "bg" : {
                "office" : load_image("Backgrounds/office.png")
            }
        }

        #게임 효과음
        self.sfxs = {

        }

        #게임 폰트
        self.fonts = {
            "main_title_font" : pg.font.Font('Assets/Fonts/Galmuri11-Bold.ttf', 12),
        }

        #스폰된 엔티티들
        self.entities = []
    
    #타이틀 스크린
    def state_title_screen(self):
        #start:

        #스페이스바로 시작
        start_key = pg.K_SPACE
        while(True):
            #update:

            #화면 초기화
            self.screen.fill("black")

            #이벤트 리슨
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit()
                    sys.exit()
                if event.type == pg.KEYDOWN:
                    if event.key == start_key:
                        #메인 게임 시작
                        self.state_main_game()
                        return

            self.clock.tick(TARGET_FPS)
            #카메라 업데이트
            pg.display.update()
    
    #메인 게임
    def state_main_game(self):
        #start:

        #플레이어 : game, name, pos, hit_box_size, anim_size
        self.player = Player(self, "player", (500, 640), (80, 160), (160, 160), 100) #타일 하나 크기에 맞추기
        self.player.anim_offset = [0, 20]
        # [[좌, 우], [하, 상]]
        self.player_movement = [[False, False], [False, False]]

        #백그라운드 스크롤
        background1 = self.assets["bg"]["office"]
        background2 = self.assets["bg"]["office"]
        bg_width = background1.get_width()
        bg_scroll_speed = 20

        bg_x1 = 0
        bg_x2 = bg_width

        #천장 & 바닥 & 배경
        floor = pg.rect.Rect(200, 700, SCREEN_SCALE[0], 100)
        ceil = pg.rect.Rect(200, 0, SCREEN_SCALE[0], 100)
        physic_rects = [floor, ceil]
        ui_background = pg.rect.Rect(0, 0, 300, SCREEN_SCALE[1])

        #엔티티
        floor_spawn_pos = (SCREEN_SCALE, 640)
        ceil_spawn_pos = (SCREEN_SCALE, 100)

        while(True):
            #update:

            #화면 초기화
            self.screen.fill("black")
            
            #배경 렌더
            bg_x1 -= bg_scroll_speed
            bg_x2 -= bg_scroll_speed

            if bg_x1 <= -bg_width:
                bg_x1 = bg_width
            if bg_x2 <= -bg_width:
                bg_x2 = bg_width

            self.screen.blit(background1, (bg_x1, 0))
            self.screen.blit(background2, (bg_x2, 0))

            self.screen.blit(pg.transform.scale(self.assets["ui"]["bottom_fade"], (SCREEN_SCALE[0], 100)), (0, 700))
            self.screen.blit(pg.transform.flip(pg.transform.scale(self.assets["ui"]["bottom_fade"], (SCREEN_SCALE[0], 100)), False, True), (0, 0))
            #배경 렌더 끝


            #플레이어 업데이트 & 렌더
            self.player.update(physic_rects, self.player_movement)
            self.player.animation.update()
            self.player.render(self.screen)
            #플레이어 업데이트 & 렌더 끝
            pg.draw.rect(self.ui, "black", ui_background)

            #화면 렌더
            self.camera.blit(self.screen, (0, 0))
            self.camera.blit(self.ui, (0, 0))

            #이벤트 리슨
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit()
                    sys.exit()

                if event.type == pg.KEYDOWN:
                    if event.key == KEY_JUMP:
                        self.player.jump(25)

            self.clock.tick(TARGET_FPS)
            #카메라 업데이트
            pg.display.update()

                
#게임 실행
if __name__ == '__main__':
    game = Game()
    game.state_title_screen()