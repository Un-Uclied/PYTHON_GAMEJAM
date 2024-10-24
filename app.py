#라이브러리 임포트
import pygame as pg
import sys, random, math

from Scripts.utils import load_image, load_images
from Scripts.Shadows import Shadow
from Scripts.Entities import Entity, MoveableEntity, Player
from Scripts.Animations import Animation
from Scripts.Particles import Spark, Particle
from Scripts.Ui import TextUi
from Scripts.Bullets import Bullet, PlayerBullet

#상수 설정
SCREEN_SCALE = (1600, 800)
GAME_NAME = "Break Away"
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
        self.outline = pg.surface.Surface(SCREEN_SCALE, pg.SRCALPHA)

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

            "projectiles" : {
                "bullet" : load_image("Projectiles/Bullet.png")
            },
            
            "entities" : {
                "player/run" : Animation(load_images("Characters/Player/Run"), 3, True),
                "player/jump" : Animation(load_images("Characters/Player/Jump"), 3, False),
                "player/fall" : Animation(load_images("Characters/Player/Fall"), 6, True),
                
                "worm/idle" : Animation(load_images("Characters/Worm"), 3, True)
            },

            "props" : {
                "player/gun" : load_image("Characters/Player/Gun.png")
            },

            "bg" : {
                "office" : load_image("Backgrounds/office.png")
            },

            "particles" : {
                "dusts" : Animation(load_images("Particles/Dusts"), 5, False),
                "deep_dusts_loop" : Animation(load_images("Particles/DeepDusts"), 5, True),
            }
        }

        #게임 효과음
        self.sfxs = {

        }

        #게임 폰트
        self.fonts = {
            "galmuri" : 'Assets/Fonts/Galmuri11-Bold.ttf',
        }

        self.physic_rects = []

        #스폰된 엔티티들
        self.entities = []

        #스폰된 스파크들
        self.sparks = []

        #스폰된 파티클들
        self.particles = []

        #스폰된 UI들
        self.uis = []

        #스폰된 탄들
        self.projectiles = []
    
    #타이틀 스크린
    def state_title_screen(self):
        #start:
        
        #스페이스바로 시작
        start_key = pg.K_SPACE
        self.uis.append(TextUi(f"{GAME_NAME} 메인 메뉴!", (50, 50), self.fonts["galmuri"], 30, "white"))
        
        while(True):
            #update:

            #화면 초기화
            self.screen.fill("black")

            self.manage_particle()
            self.manage_particle()
            self.manage_ui()

            #화면 렌더
            self.camera.blit(self.screen, (0, 0))

            #이벤트 리슨
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit()
                    sys.exit()
                if event.type == pg.KEYDOWN:
                    if event.key == start_key:
                        self.end_scene()
                        #메인 게임 시작
                        self.state_main_game()
                        return

            self.clock.tick(TARGET_FPS)
            #카메라 업데이트
            pg.display.update()
    
    def manage_spark(self):
        for spark in self.sparks.copy():
            kill = spark.update()
            spark.render(self.screen)
            if kill:
                self.sparks.remove(spark)

    def manage_particle(self):
        for particle in self.particles.copy():
            kill = particle.update()
            particle.render(self.screen)
            if kill:
                self.particles.remove(particle)
    
    def manage_ui(self):
        for ui in self.uis:
            if hasattr(ui, "update"):
                ui.update()
            if hasattr(ui, "render"):
                ui.render(self.screen)

    def manage_projectiles(self):
        for p in self.projectiles:
            p.timer -= 1
            if hasattr(p, "update"):
                p.update()
            if hasattr(p, "render"):
                p.render(self.screen)

            for rects in self.physic_rects: #벽 같은거
                if rects.collidepoint(p.pos):
                    p.destroy() # 벽에 맞음
                    self.projectiles.remove(p)
            if not p.tag == "player's bullet" and self.player.get_rect().collidepoint(p.pos[0], p.pos[1]):
                p.destroy() #플레이어에 맞음
                self.projectiles.remove(p)
            if p.timer <= 0:
                self.projectiles.remove(p) #시간이 지나고, 화면 밖으로 나간것으로 추정
    #메인 게임
    def state_main_game(self):
        #start:

        #플레이어 : game, name, pos, hit_box_size, anim_size, max health
        self.player = Player(self, "player", (350, 640), (70, 170), (170, 170), 100) #타일 하나 크기에 맞추기
        #총 주기
        self.player.give_gun(self.assets["props"]["player/gun"], 100, (75, 75))
        self.player.anim_offset = [0, 20]
        # [[좌, 우], [하, 상]]
        self.player_movement = [[False, False], [False, False]]

        #구렁이
        worm = Entity(self, "worm", (-100, 95), (610, 610), (610, 610))
        worm.set_action("idle")

        for i in range(8):
                self.particles.append(Particle(self, "deep_dusts_loop", (10, 80 + 90 * i + (random.random() * 5)), (125, 125),  (0, 0), frame=random.randint(0, 20)))
                self.particles.append(Particle(self, "deep_dusts_loop", (10, 80 + 90 * i + (random.random() * 5)), (125, 125),  (0, 0), frame=random.randint(0, 20)))
        #구렁이 끝

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
        self.physic_rects = [floor, ceil]

        #엔티티
        floor_spawn_pos = (SCREEN_SCALE, 640)
        ceil_spawn_pos = (SCREEN_SCALE, 100)

        #ui
        self.uis.append(TextUi("못밤 플레이어 | 못밤 체력 : 100 | 못밤 스코어 : 없음 ㅋ", (50, 30), self.fonts["galmuri"], 30, "white"))

        while(True):
            #update:

            #화면 초기화
            self.screen.fill("black")
            self.outline.fill("black")
            
            #배경 렌더
            bg_x1 -= bg_scroll_speed
            bg_x2 -= bg_scroll_speed

            if bg_x1 <= -bg_width:
                bg_x1 = bg_width
            if bg_x2 <= -bg_width:
                bg_x2 = bg_width

            self.screen.blit(background1, (bg_x1, 0))
            self.screen.blit(background2, (bg_x2, 0))

            self.screen.blit(pg.transform.scale(self.assets["ui"]["bottom_fade"], (SCREEN_SCALE[0], 150)), (0, 700))
            self.screen.blit(pg.transform.flip(pg.transform.scale(self.assets["ui"]["bottom_fade"], (SCREEN_SCALE[0], 150)), False, True), (0, 0))
            self.screen.blit(pg.transform.flip(pg.transform.rotate(self.assets["ui"]["bottom_fade"], 90), True, False), (0, 0))
            #배경 렌더 끝

            worm.update()
            worm.render(self.screen)

            #플레이어 업데이트 & 렌더
            self.player.update(self.physic_rects, self.player_movement)
            self.player.animation.update()
            self.player.render(self.screen)
            #플레이어 업데이트 & 렌더 끝

            self.manage_spark()
            self.manage_particle()
            self.manage_ui()
            self.manage_projectiles()

            #화면 렌더
            self.camera.blit(self.outline, (0, 0))
            self.camera.blit(self.screen, (0, 0))

            #이벤트 리슨
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit()
                    sys.exit()

                if event.type == pg.KEYDOWN:
                    if event.key == KEY_JUMP:
                        self.player.jump(22)

            mouse_click = pg.mouse.get_pressed(3) #(마우스 좌클릭, 마우스 휠클릭, 마우스 우클릭)
            mouse_pos = pg.mouse.get_pos()
            if mouse_click[0] == WEAPON_ATTACK:
                player_pos =  self.player.get_rect().center
                self.projectiles.append(
                    PlayerBullet(self, player_pos, pg.math.Vector2(mouse_pos[0] - player_pos[0], mouse_pos[1] - player_pos[1]), 25, self.assets["projectiles"]["bullet"], 500, "player's bullet")
                )

            self.clock.tick(TARGET_FPS)
            #카메라 업데이트
            pg.display.update()

    def end_scene(self):
        self.physic_rects.clear()
        self.particles.clear()
        self.sparks.clear()
        self.uis.clear()

                
#게임 실행
if __name__ == '__main__':
    game = Game()
    game.state_title_screen()