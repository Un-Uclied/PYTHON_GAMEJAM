#라이브러리 임포트
import pygame as pg
import sys
from Scripts.Tilemap import Tilemap
from Scripts.utils import load_image, load_images
from Scripts.Entities import Entity

#상수 설정
SCREEN_SCALE = (1000, 1000)
GAME_NAME = "DR.Mind"
TARGET_FPS = 60

#게임 클래스
class Game:
    #게임 생성자
    def __init__(self):
        #init함수
        pg.init()
        pg.display.set_caption(GAME_NAME)

        self.camera = pg.display.set_mode(SCREEN_SCALE)
        self.screen = pg.surface.Surface(SCREEN_SCALE)

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
                "floor" : load_images('Tiles/Floor'),
                "wall" : load_images('Tiles/Wall'),
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

            #카메라 초기화
            self.camera.fill("black")

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

        self.player = 

        while(True):
            #update:

            #카메라 초기화
            self.camera.fill("black")
            
            #타일 맵 렌더
            tilemap.render(self.screen, (0, 0))

            #화면 렌더
            self.camera.blit(self.screen, (0,0))

            #이벤트 리슨
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit()
                    sys.exit()

            self.clock.tick(TARGET_FPS)
            #카메라 업데이트
            pg.display.update()

                
#게임 실행
if __name__ == '__main__':
    game = Game()
    game.state_title_screen()