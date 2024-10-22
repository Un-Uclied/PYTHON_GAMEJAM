#라이브러리 임포트
import pygame as pg
import sys
from Scripts.Tilemap import Tilemap
from Scripts.utils import load_image, load_images
from Scripts.Entities import Entity, MoveableEntity
from Scripts.Animations import Animation

#상수 설정
SCREEN_SCALE = (1000, 1000)
GAME_NAME = "DR.Mind"
TARGET_FPS = 60

#입력 설정
MOVE_UP = pg.K_w
MOVE_DOWN = pg.K_s
MOVE_LEFT = pg.K_a
MOVE_RIGHT = pg.K_d

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
                "player/idle" : Animation(load_images("Characters/Player"), 5, True)
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

        #타일맵 로드
        tilemap = Tilemap(self, 32)
        tilemap.load("new_map.json")
        
        #플레이어 : game, name, pos, hit_box_size, anim_size
        self.player = MoveableEntity(self, "player", (0, 0), (64, 64), (64, 64))
        # [[좌, 우], [하, 상]]
        self.player_movement = [[False, False], [False, False]]
        player_movespeed = 3.5

        #카메라 플레이어 추적
        scroll = [0, 0]
        scroll_speed = 25

        while(True):
            #update:

            #화면 초기화
            self.screen.fill("black")

            scroll[0] += (self.player.get_rect().centerx - self.screen.get_width() / 2 - scroll[0]) / scroll_speed
            scroll[1] += (self.player.get_rect().centery - self.screen.get_width() / 2 - scroll[1]) / scroll_speed
            render_scroll = (int(scroll[0]), int(scroll[1]))

            print(render_scroll)
            #타일 맵 렌더
            tilemap.render(self.screen, render_scroll)

            #플레이어 업데이트 & 렌더
            self.player.update(tilemap, self.player_movement, player_movespeed)
            self.player.animation.update()
            self.player.render(self.screen, render_scroll)
            
            #render_scroll = (self.scroll[0] / -16,self.scroll[1] / -16)

            #화면 렌더
            self.camera.blit(self.screen, (0, 0))

            #이벤트 리슨
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit()
                    sys.exit()

                if event.type == pg.KEYDOWN:
                    if event.key == MOVE_UP:
                        self.player_movement[1][1] = True
                    if event.key == MOVE_DOWN:
                        self.player_movement[1][0] = True
                    if event.key == MOVE_LEFT:
                        self.player_movement[0][1] = True
                    if event.key == MOVE_RIGHT:
                        self.player_movement[0][0] = True
                if event.type == pg.KEYUP:
                    if event.key == MOVE_UP:
                        self.player_movement[1][1] = False
                    if event.key == MOVE_DOWN:
                        self.player_movement[1][0] = False
                    if event.key == MOVE_LEFT:
                        self.player_movement[0][1] = False
                    if event.key == MOVE_RIGHT:
                        self.player_movement[0][0] = False

            self.clock.tick(TARGET_FPS)
            #카메라 업데이트
            pg.display.update()

                
#게임 실행
if __name__ == '__main__':
    game = Game()
    game.state_title_screen()