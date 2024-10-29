#라이브러리 임포트
import pygame as pg
import sys, random, math, pytweening as pt
import requests

from Scripts.utils import load_image, load_images, load_data
from Scripts.Shadows import Shadow
from Scripts.Entities import Player, Entity, KillableEnemy, Obstacle, Ratbit, Helli, Brook, BlugLogger, Medicine, Ammo
from Scripts.Animations import Animation
from Scripts.Particles import Spark, Particle
from Scripts.Ui import TextUi, ButtonUi, WiggleButtonUi, LinkUi, TextButton, InputField
from Scripts.Bullets import Bullet, PlayerBullet

import firebase_admin
from firebase_admin import credentials, firestore, auth


#firebase 연동
cred = credentials.Certificate("firebase/firebase-python-key.json")
app = firebase_admin.initialize_app(cred)

db = firestore.client()

#상수 설정
SCREEN_SCALE = (1600, 800)
GAME_NAME = "Break Away"
TARGET_FPS = 60

#입력 설정
KEY_JUMP = pg.K_SPACE
#마우스 입력 설정
MOUSE_ATTACK = 0
MOUSE_BLOCK = 2

#엔티티 스폰 위치
CEIL_SPAWN_POS = (SCREEN_SCALE[0], 100)
FLOOR_SPAWN_POS = (SCREEN_SCALE[0], 540)
MID_SPAWN_POS = (SCREEN_SCALE[0], 300)

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
        self.current_time = pg.time.get_ticks()

        self.camera_shake_gain = 0
        self.camera_shrink_speed = .6
        self.shake = (self.camera_shake_gain * random.random(), self.camera_shake_gain * random.random())

        #게임 에셋
        self.assets = {
            #UI에셋
            "ui" : { 
                "bottom_fade" : load_image("UI/BottomFade.png"),

                "title" : load_image("UI/Title.png"),

                "world" : load_image("UI/World.png"),
                "endless" : load_image("UI/Endless.png"),
                "credits" : load_image("UI/Credits.png"),
                "records" : load_image("UI/Record.png"),
                "quit" : load_image("UI/Quit.png"),
                "escape" : load_image("UI/Escape.png"),

                "motbam" : load_image("UI/Motbam.png"),
                "motbam2" : load_image("UI/Motbam2.png"),
                "me" : load_image("UI/Me.png"),

                "credits_서준범_icon" : load_image("서준범.png"),
                "credits_이준영_icon" : load_image("못밤.png"),

                "node" : load_image("UI/Node.png"),
                "exit_node" : load_image("UI/ExitNode.png"),
                "locked_node" : load_image("UI/Locked.png")

            },

            "projectiles" : {
                "bullet" : load_image("Projectiles/Bullet.png"),
                "helli_fire_bullet" : load_image("Projectiles/FireBullet.png")
            },
            
            "entities" : {
                "player/run" : Animation(load_images("Characters/Player/Run"), 3, True),
                "player/jump" : Animation(load_images("Characters/Player/Jump"), 3, False),
                "player/fall" : Animation(load_images("Characters/Player/Fall"), 6, True),
                
                "worm/idle" : Animation(load_images("Characters/Worm"), 3, True),

                "ratbit/idle" : Animation(load_images("Characters/Ratbit/Idle"), 3, True),
                "ratbit/attack" : Animation(load_images("Characters/Ratbit/Attack"), 8, True),
            
                "strucker/idle" : Animation(load_images("Characters/Strucker"), 4, True),

                "helli/idle" : Animation(load_images("Characters/Helli/Idle"), 5, True),

                "brook/idle" : Animation(load_images("Characters/Brook/Idle"), 8, True),
                "brook/triggered" : Animation(load_images("Characters/Brook/Explode"), 5, True),

                "bluglogger/idle" : Animation(load_images("Characters/Bluglogger/Idle"), 5, True),
                "bluglogger/attack" : Animation(load_images("Characters/Bluglogger/Attack"), 5, True),
                "beam" : load_image("Characters/Bluglogger/Beam.png"),

                "stalker/idle" : Animation(load_images("Characters/Stalker/Idle"), 5, True),
            },

            "props" : {
                "player/arm_gun" : load_image("Characters/Player/Arm.png"),
                "player/arm_shield" : load_image("Characters/Player/ArmShield.png")
            },

            "bg" : {
                "office/0" : load_image("Backgrounds/office_0.png"),
                "office/1" : load_image("Backgrounds/office_1.png"),
                "steam_room/0" : load_image("Backgrounds/steam_room_0.png"),
                "steam_room/1" : load_image("Backgrounds/steam_room_1.png"),
            },

            "particles" : {
                "dusts" : Animation(load_images("Particles/Dusts"), 5, False),
                "blood" : Animation(load_images("Particles/Blood"), 5, False),
                "deep_dusts_loop" : Animation(load_images("Particles/DeepDusts"), 5, True),
                "flame" : Animation(load_images("Particles/Flame"), 3, False),
            },

            "items" : {
                "medicine/idle" : Animation(load_images("Items/Medicine/Idle"), 5, True),
                "medicine/use" : Animation(load_images("Items/Medicine/Use"), 2, False),

                "ammo/idle" : Animation(load_images("Items/Ammo/Idle"), 5, True),
                "ammo/use" : Animation(load_images("Items/Ammo/Use"), 2, False),
            },

            "level_world" : load_image("background.png")
        }

        #게임 효과음
        self.sfxs = {
            "gun_fire" : pg.mixer.Sound('Assets/Sfxs/GunFire.wav'),
            "enemy_dying" : pg.mixer.Sound('Assets/Sfxs/EnemyDying.wav'),
            "enemy_hit" : pg.mixer.Sound('Assets/Sfxs/EnemyHit.wav'),
            "parry" : pg.mixer.Sound('Assets/Sfxs/Parry.wav'),
            "swoosh" : pg.mixer.Sound('Assets/Sfxs/Swing.wav'),
            "jump" : pg.mixer.Sound('Assets/Sfxs/Jump.wav'),
            "ui_hover" : pg.mixer.Sound('Assets/Sfxs/Hover.wav'),
            "heal" : pg.mixer.Sound('Assets/Sfxs/Heal.wav'),
            "reload" : pg.mixer.Sound('Assets/Sfxs/Reload.wav'),
            "player_hurt" : pg.mixer.Sound('Assets/Sfxs/PlayerHurt.wav'),
            "gameover" : pg.mixer.Sound('Assets/Sfxs/Gameover.wav'),
            "explosion" : pg.mixer.Sound("Assets/Sfxs/Explosion.wav"),
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

        self.score = 0
        self.current_level_data = {}
        self.status = load_data("Status.json")
    
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
        fps_ui = TextUi(f"FPS : {int(self.clock.get_fps())}", (1540, 0), self.fonts["galmuri"], 12, "white")
        fps_ui.render(self.screen)

        for ui in self.uis:
            if hasattr(ui, "update"):
                ui.update()
            if hasattr(ui, "render"):
                ui.render(self.screen)
            if hasattr(ui, "wiggle"):
                    ui.wiggle()

    def manage_projectiles(self):
        for projectile in self.projectiles:
            #헬적화 경고 ㅠㅠ
            projectile.timer -= 1

            #벽 충돌 감지
            for rects in self.physic_rects:
                if projectile.tag == "player's bullet" and rects.collidepoint(projectile.pos) and projectile in self.projectiles:
                    projectile.destroy()
                    self.projectiles.remove(projectile)

            #적 감지
            for enemy in self.entities:
                if projectile.tag == "player's bullet" and enemy.get_rect().collidepoint(projectile.pos) and projectile in self.projectiles and isinstance(enemy, KillableEnemy):
                    enemy.take_damage(projectile.damage)
                    self.projectiles.remove(projectile)
                        
                    
            #플레이어 감지
            if not projectile.tag == "player's bullet" and self.player.get_rect().collidepoint(projectile.pos[0], projectile.pos[1]) and projectile in self.projectiles:
                #패링 : 적 탄막 => 플레이어 탄막으로 변경
                if self.player.blocking:
                    projectile.direction = pg.math.Vector2(1, 0).normalize() * projectile.speed
                    self.on_player_blocked()
                    projectile.timer = projectile.max_timer
                    projectile.tag = "player's bullet"
                else:
                    projectile.destroy() #플레이어에 맞음
                    self.projectiles.remove(projectile)
                    self.on_player_damaged(projectile.damage)
            if projectile.timer <= 0:
                self.projectiles.remove(projectile) #시간이 지나고, 화면 밖으로 나간것으로 추정

            if hasattr(projectile, "update"):
                projectile.update()
            if hasattr(projectile, "render"):
                projectile.render(self.screen)
    
    def manage_camera_shake(self):
        self.camera_shake_gain = max(self.camera_shake_gain - self.camera_shrink_speed, 0)
        self.shake = (self.camera_shake_gain * random.random(), self.camera_shake_gain * random.random())

    def manage_entity(self):
        for entity in self.entities:
            entity.can_interact()
            entity.update()
            entity.render(self.screen)

    def spawn_entity(self):
        #스포닝 에너미
        #RATBIT
        if self.current_level_data["entities"]["ratbit"] and random.randint(1, self.current_level_data["spawn_rates"]["ratbit_spawn_rate"]) == 1:
            self.entities.append(Ratbit(self, "ratbit",
                                        pos=CEIL_SPAWN_POS if random.random() > .5 else FLOOR_SPAWN_POS,
                                        size=(150, 150), anim_size=(150, 150), 
                                        following_speed=30, 
                                        health=1, damage=self.current_level_data["damages"]["ratbit_damage"], attack_range=100))
        #STRUCKER
        if self.current_level_data["entities"]["strucker"] and random.randint(1, self.current_level_data["spawn_rates"]["strucker_spawn_rate"]) == 1:
            self.entities.append(Obstacle(self, "strucker", 
                                        pos=(FLOOR_SPAWN_POS[0], FLOOR_SPAWN_POS[1] + 40),
                                        size=(100, 150), anim_size=(150, 150), 
                                        speed=20, damage=self.current_level_data["damages"]["strucker_damage"]))
        #STALKER
        if self.current_level_data["entities"]["stalker"] and random.randint(1, self.current_level_data["spawn_rates"]["stalker_spawn_rate"]) == 1:
            self.entities.append(Obstacle(self, "stalker", 
                                        pos=(CEIL_SPAWN_POS[0], CEIL_SPAWN_POS[1] - 100),
                                        size=(150, 400), anim_size=(150, 400), 
                                        speed=20, damage=self.current_level_data["damages"]["stalker_damage"]))
        #HELLI
        if self.current_level_data["entities"]["helli"] and random.randint(1, self.current_level_data["spawn_rates"]["helli_spawn_rate"]) == 1:
            self.entities.append(Helli(self, "helli", 
                                        pos=(FLOOR_SPAWN_POS[0], FLOOR_SPAWN_POS[1]),
                                        size=(200, 200), anim_size=(150, 150), speed=5, health=self.current_level_data["healths"]["helli_health"], damage=self.current_level_data["damages"]["helli_damage"], 
                                        up=(CEIL_SPAWN_POS[0] - 200, CEIL_SPAWN_POS[1] - 100), 
                                        down=(FLOOR_SPAWN_POS[0] - 200, FLOOR_SPAWN_POS[1] + 100),
                                        attack_chance=90, bullet_speed=30))
        #BROOK
        if self.current_level_data["entities"]["brook"] and random.randint(1, self.current_level_data["spawn_rates"]["brook_spawn_rate"]) == 1:
            self.entities.append(Brook(self, "brook", 
                                       pos=(CEIL_SPAWN_POS[0] + 100, 350), 
                                       size=(200, 200), anim_size=(150, 150),
                                       start_following_speed = 3,
                                       following_speed=55, max_health=1, damage=self.current_level_data["damages"]["brook_damage"], speed_change_speed = 5))
        #BLUGLOGGER
        if self.current_level_data["entities"]["bluglogger"] and random.randint(1, self.current_level_data["spawn_rates"]["bluglogger_spawn_rate"]) == 1:
            #블러그로거는 한 장면에 하나만 나옴
            if not any(isinstance(entity, BlugLogger) for entity in self.entities):
                self.entities.append(BlugLogger(self, "bluglogger", 
                                                pos= (FLOOR_SPAWN_POS[0], FLOOR_SPAWN_POS[1] + 35), size=(150, 150), anim_size=(150, 150), 
                                                following_speed=10, max_health=self.current_level_data["healths"]["bluglogger_health"], damage=self.current_level_data["damages"]["bluglogger_damage"], 
                                                wait_time=90, attack_rate=50))

        #스포닝 에너미 끝
        if self.current_level_data["entities"]["medicine"] and random.randint(1, self.current_level_data["spawn_rates"]["medicine_spawn_rate"]) == 1:
            self.entities.append(
                Medicine(self, "medicine", FLOOR_SPAWN_POS, (130 , 130), (130, 130), 20, self.current_level_data["amount"]["heal_amount"])
            )
        #추가 탄약은 플레이어가 최대 탄약이 아닐때 생김
        if self.player.ammo != self.player.max_ammo and self.current_level_data["entities"]["ammo"] and random.randint(1, self.current_level_data["spawn_rates"]["ammo_spawn_rate"]) == 1:
            self.entities.append(
                Ammo(self, "ammo", FLOOR_SPAWN_POS, (130 , 130), (130, 130), 20, self.current_level_data["amount"]["ammo_amount"])
            )

    #타이틀 스크린
    def state_title_screen(self):
        #start:

        margin = 50
        map_btn = WiggleButtonUi(pg.transform.scale(self.assets["ui"]["world"], (200, 100)), (500, 50), self.sfxs["ui_hover"], 1, 20)
        endless_btn = WiggleButtonUi(pg.transform.scale(self.assets["ui"]["endless"], (200, 100)), (500, 150 + margin), self.sfxs["ui_hover"], 1, 20)
        records_btn = WiggleButtonUi(pg.transform.scale(self.assets["ui"]["records"], (200, 100)), (500, 250 + margin * 2), self.sfxs["ui_hover"], 1, 20)
        credits_btn = WiggleButtonUi(pg.transform.scale(self.assets["ui"]["credits"], (200, 100)), (500, 350 + margin * 3), self.sfxs["ui_hover"], 1, 20)
        quit_btn = WiggleButtonUi(pg.transform.scale(self.assets["ui"]["quit"], (200, 100)), (500, 450 + margin * 4), self.sfxs["ui_hover"], 1, 20)

        login_btn = TextButton("<로그인해주세요 현재 : 익명", self.fonts["galmuri"], 30, (30, 560), self.sfxs["ui_hover"], "yellow", "blue")

        self.uis.append(map_btn)
        self.uis.append(endless_btn)
        self.uis.append(records_btn)
        self.uis.append(credits_btn)
        self.uis.append(quit_btn)
        self.uis.append(login_btn)

        hover_image = pg.Surface((100, 100))

        elapsed_time = 0

        while(True):
            #update:
            self.current_time = pg.time.get_ticks()

            #화면 초기화
            self.screen.fill("black")
            self.camera.fill("black")

            #pg.draw.rect(self.screen, "white", (0, 0, 1600, 800))
            self.screen.blit(hover_image, (600, 0))
            self.screen.blit(pg.transform.rotate(self.assets["ui"]["bottom_fade"], -90), (800, 0))
            pg.draw.rect(self.screen, "black", (0, 0, 800, 800))
        
            mouse_click = pg.mouse.get_pressed(3)[0]
            #지도 버튼
            if map_btn.hovering:
                hover_image = self.assets["ui"]["motbam"]
                if mouse_click:
                    print("맵 버튼 누름")
                    self.end_scene()
                    self.state_main_world()
            #엔드레스 게임으로
            if endless_btn.hovering:
                hover_image = self.assets["ui"]["motbam2"]
                if mouse_click:
                    self.end_scene()
                    self.current_level_data = load_data("Assets/BigBreakout.json")
                    self.state_main_game()
            #리코드 볼수 있음
            if records_btn.hovering:
                hover_image = self.assets["ui"]["me"]
                if mouse_click:
                    print("리코드 버튼 누름")
            #크레딧
            if credits_btn.hovering:
                hover_image = self.assets["ui"]["motbam"]
                if mouse_click:
                    self.end_scene()
                    self.state_credits()
                    print("크레딧 버튼 누름")
            #나가기
            if quit_btn.hovering:
                hover_image = self.assets["ui"]["me"]
                if mouse_click:
                    pg.quit()
                    sys.exit()

            #로그인
            if login_btn.hovering:
                hover_image = self.assets["ui"]["me"]
                if mouse_click:
                    self.end_scene()
                    self.state_login_menu()

            self.manage_spark()
            self.manage_particle()
            self.manage_ui()
            self.manage_camera_shake()

            self.screen.blit(self.assets["ui"]["title"], (0, 0))

            #화면 렌더
            self.camera.blit(self.screen, (0, 0))

            #이벤트 리슨
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit()
                    sys.exit()

            dt = self.clock.tick(TARGET_FPS) / 1000
            elapsed_time += dt
            #카메라 업데이트
            pg.display.flip()

    #메인 게임
    def state_main_game(self):
        #start:
        PAUSED = False #상수는 아니지만 그래도 중요하니까 ^^ 아시져?

        #플레이어 : game, name, pos, hit_box_size, anim_size, max health
        self.player = Player(self, "player", 
                            pos=(400, 640), size=(70, 170), anim_size=(170, 170),
                            max_health=100, 
                            gun_img=self.assets["props"]["player/arm_gun"], shield_img=self.assets["props"]["player/arm_shield"],
                            max_rotation=100,
                            max_block_time=15, attack_damage=20, bullet_speed=45, 
                            offset=(55, 75))
        self.player.anim_offset = [-25, 20]
        #총 세팅
        gun_cooltime = 300 #.3초
        gun_fire_shake = 4.5
        last_fire_time = pg.time.get_ticks()
        last_block_time = pg.time.get_ticks()
        block_cooltime = 800
        # [[좌, 우], [하, 상]]
        self.player_movement = [[False, False], [False, False]]

        #구렁이
        worm = Entity(self, "worm", (-100, 95), (300, 610), (610, 610))
        worm.set_action("idle")

        for i in range(8):
                self.particles.append(Particle(self, "deep_dusts_loop", (10, 80 + 90 * i + (random.random() * 5)), (125, 125),  (0, 0), frame=random.randint(0, 20)))
                self.particles.append(Particle(self, "deep_dusts_loop", (10, 80 + 90 * i + (random.random() * 5)), (125, 125),  (0, 0), frame=random.randint(0, 20)))
        #구렁이 끝

        #백그라운드 스크롤
        background1 = self.assets["bg"][f"{self.current_level_data['bg_name']}/0"]
        background2 = self.assets["bg"][f"{self.current_level_data['bg_name']}/1"]
        bg_width = background1.get_width()
        bg_scroll_speed = 20

        bg_x1 = 0
        bg_x2 = bg_width

        #천장 & 바닥 & 배경
        floor = pg.rect.Rect(200, 700, SCREEN_SCALE[0], 100)
        ceil = pg.rect.Rect(200, 0, SCREEN_SCALE[0], 100)
        self.physic_rects = [floor, ceil]

        #ui
        stat_ui = TextUi("98세 못밤할아버지의 마지막 물 한모금", (50, 30), self.fonts["galmuri"], 30, "white")
        self.uis.append(stat_ui)

        #일시 정지 UI
        pause_bg = self.assets["bg"]["office/1"]
        pause_rect_surface = pg.Surface(pause_bg.get_size(), pg.SRCALPHA)
        pause_rect_surface.fill((0, 0, 0, 200))

        while(True):
            #update:
            #화면 초기화
            self.screen.fill("black")
            self.camera.fill("black")
            
            #일시 정지에 영향을 받음
            if not PAUSED:
                self.current_time = pg.time.get_ticks()

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

                stat_ui.text = f"남은 탄: {self.player.ammo} | {self.score} | 거대 괴물로부터 남은 거리 : {self.player.health}m"
                
                #플레이어 업데이트 & 렌더
                self.player.update(self.physic_rects, self.player_movement)
                self.player.render(self.screen)
                #플레이어 업데이트 & 렌더 끝

                self.spawn_entity()

                #매니징
                self.manage_projectiles()
                self.manage_camera_shake()
                self.manage_entity()
                #매니징 끝

                #구렁이 업데이트 ㅋㅋ
                worm.pos.x = -self.player.health * 2
                worm.update()
                worm.render(self.screen)
                #구렁이 ㅋㅋ 끝

                #매니징
                self.manage_particle()
                self.manage_spark()
                self.manage_ui()
                #매니징 끝 

                #화면 렌더
                
                self.camera.blit(self.screen, self.shake)
                #화면 렌더 끝

                #플레이어 행동
                mouse_click = pg.mouse.get_pressed(3) #(마우스 좌클릭, 마우스 휠클릭, 마우스 우클릭)
                mouse_pos = pg.mouse.get_pos()
                #플레이어 공격
                if mouse_click[MOUSE_ATTACK] and self.current_time - last_fire_time >= gun_cooltime:
                    if self.player.gun_fire(mouse_pos):
                        self.sfxs["gun_fire"].play()
                        self.camera_shake_gain += gun_fire_shake
                        last_fire_time = self.current_time
                #플레이어 블록
                if mouse_click[MOUSE_BLOCK] and self.current_time - last_block_time >= block_cooltime:
                    self.sfxs["swoosh"].play()
                    self.player.use_shield()
                    last_block_time = self.current_time
                #플레이어 행동 끝
            #일시 정지에 영향을 받음 끝
            
            if PAUSED:
                self.screen.blit(pause_bg, (0, 0))
                self.screen.blit(pause_rect_surface, (0, 0))

                pg.draw.rect(self.screen, "black", (0, 0, 300, SCREEN_SCALE[1]))
                self.screen.blit(pg.transform.rotate(self.assets["ui"]["bottom_fade"], -90), (300, 0))

                paused_txt = TextUi("일시정지", (100, 300), self.fonts["galmuri"], 100, "white")
                paused_txt.update()
                paused_txt.render(self.screen)
                paused_txt = TextUi("ESC로 게임으로 돌아가기", (100, 420), self.fonts["galmuri"], 30, "white")
                paused_txt.update()
                paused_txt.render(self.screen)

                self.camera.blit(self.screen, (0, 0))

            #이벤트 리슨
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit()
                    sys.exit()

                if event.type == pg.KEYDOWN:
                    if event.key == KEY_JUMP:
                        if self.player.jump(20):
                            self.sfxs["jump"].play()
                    if event.key == pg.K_ESCAPE:
                        PAUSED = not PAUSED
                
                #마우스가 창밖에 나가면 PAUSE
                if event.type == pg.ACTIVEEVENT:
                    if event.gain == 0:
                        PAUSED = True
            #이벤트 리슨 끝

            self.clock.tick(TARGET_FPS)
            #카메라 업데이트
            pg.display.flip()
    
    #지도
    def state_main_world(self):

        quit_btn = WiggleButtonUi(pg.transform.scale(self.assets["ui"]["quit"], (200, 100)), (70, 650), self.sfxs["ui_hover"], 1, 20)
        self.uis.append(quit_btn)

        bg = self.assets["level_world"]

        button_pos = [(390, 40), (500, 200), (920, 340), (1250, 450), (1070, 580), (1200, 700), (1500, 680)]
        buttons = []
        for i in range(6):
            btn = ButtonUi(pg.transform.scale(self.assets["ui"]["node"] if i < self.status["level"] + 1 else self.assets["ui"]["locked_node"], (50, 50)), button_pos[i], self.sfxs["ui_hover"])
            buttons.append(btn)
            self.uis.append(btn)

        boss_btn = ButtonUi(pg.transform.scale(self.assets["ui"]["exit_node"], (50, 50)), button_pos[6], self.sfxs["ui_hover"])
        self.uis.append(boss_btn)

        selected_level = 0
        text = TextUi("", (10, 10), self.fonts["galmuri"], 40, "white")
        self.uis.append(text)
        escape_btn = WiggleButtonUi(pg.transform.scale(self.assets["ui"]["escape"], (200, 100)), (70, 500), self.sfxs["ui_hover"], 1, 20)
        self.uis.append(escape_btn)


        while True:
            self.screen.fill("black")
            self.camera.fill("black")

            self.screen.blit(bg, (-200, 0))

            pg.draw.rect(self.screen, "black", (0, 0, 300, SCREEN_SCALE[1]))
            self.screen.blit(pg.transform.rotate(self.assets["ui"]["bottom_fade"], -90), (300, 0))
            
            pg.draw.lines(self.screen, "red", False, button_pos, 5)

            mouse_click = pg.mouse.get_pressed(3)[0]
            if quit_btn.hovering and mouse_click:
                self.end_scene()
                self.state_title_screen()

            #레벨 선택
            for btn in buttons:
                if btn.hovering and mouse_click:
                    selected_level = buttons.index(btn) + 1
                    text.text = f"{selected_level} 레벨"
            if boss_btn.hovering and mouse_click:
                selected_level = "Boss"
                text.text = f"{selected_level} 레벨"
            
            #게임 시작
            if escape_btn.hovering and mouse_click:
                self.end_scene()
                self.current_level_data = load_data(f"Assets/Levels/{selected_level}.json")
                self.state_main_game()

            self.manage_spark()
            self.manage_particle()
            self.manage_ui()
            self.manage_camera_shake()

            self.camera.blit(self.screen, self.shake)

            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit()
                    sys.exit()
    
            self.clock.tick(TARGET_FPS)
            pg.display.flip()

    #게임 종료
    def state_game_result(self):
        died = TextUi("님 쥬금 ㅋ", (500, 300), self.fonts["galmuri"], 200, "white")
        self.uis.append(died)
        self.sfxs["gameover"].play()
        while True:
            self.screen.fill("black")
            self.camera.fill("black")

            #매니징
            self.manage_projectiles()
            self.manage_camera_shake()
            self.manage_entity()
            self.manage_particle()
            self.manage_spark()
            self.manage_ui()
            #매니징 끝 
            
            self.camera.blit(self.screen, (0, 0))

            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit()
                    sys.exit()

            self.clock.tick(TARGET_FPS)
            pg.display.flip()

    #크레딧
    def state_credits(self):

        quit_btn = WiggleButtonUi(pg.transform.scale(self.assets["ui"]["quit"], (200, 100)), (70, 650), self.sfxs["ui_hover"], 1, 20)
        self.uis.append(quit_btn)

        self.uis.append(TextUi("98세 못밤할아버지의 마지막 물 한모금 팀", (600, 50), self.fonts["galmuri"], 50, "white"))

        self.uis.append(TextUi("서준범", (830, 220), self.fonts["galmuri"], 50, "white"))
        self.uis.append(LinkUi("깃허브", (850, 520), self.fonts["galmuri"], 40, "white", "blue", self.sfxs["ui_hover"], "https://github.com/Un-Uclied"))
        self.uis.append(LinkUi("유튜브", (850, 600), self.fonts["galmuri"], 40, "white", "blue", self.sfxs["ui_hover"], "https://www.youtube.com/@null_plr/featured"))

        self.uis.append(TextUi("이준영", (1130, 220), self.fonts["galmuri"], 50, "white"))
        self.uis.append(LinkUi("깃허브", (1150, 520), self.fonts["galmuri"], 40, "white", "blue", self.sfxs["ui_hover"], ""))

        bg = self.assets["bg"]["office/1"]
        rect_surface = pg.Surface(bg.get_size(), pg.SRCALPHA)
        rect_surface.fill((0, 0, 0, 200)) 

        while True:
            self.screen.fill("black")
            self.camera.fill("black")

            self.screen.blit(bg, (0, 0))
            self.screen.blit(rect_surface, (0, 0))

            pg.draw.rect(self.screen, "black", (0, 0, 300, SCREEN_SCALE[1]))
            self.screen.blit(pg.transform.rotate(self.assets["ui"]["bottom_fade"], -90), (300, 0))

            self.screen.blit(self.assets["ui"]["credits_서준범_icon"], (800, 300))
            self.screen.blit(self.assets["ui"]["credits_이준영_icon"], (1100, 300))

            mouse_click = pg.mouse.get_pressed(3)[0]
            if quit_btn.hovering and mouse_click:
                self.end_scene()
                self.state_title_screen()

            self.manage_spark()
            self.manage_particle()
            self.manage_ui()
            self.manage_camera_shake()

            self.camera.blit(self.screen, self.shake)

            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit()
                    sys.exit()
    
            self.clock.tick(TARGET_FPS)
            pg.display.flip()

    #로그인
    def state_login_menu(self):
        quit_btn = WiggleButtonUi(pg.transform.scale(self.assets["ui"]["quit"], (200, 100)), (70, 650), self.sfxs["ui_hover"], 1, 20)
        self.uis.append(quit_btn)

        email = InputField((750, 200), (500, 50), self.fonts["galmuri"], 30, "black", "white")
        self.uis.append(email)
        password = InputField((750, 300), (500, 50), self.fonts["galmuri"], 30, "black", "white", True)
        self.uis.append(password)

        self.uis.append(TextUi("로그인", (500, 50), self.fonts["galmuri"], 60, "white"))
        self.uis.append(TextUi("이메일 : ", (500, 200), self.fonts["galmuri"], 40, "white"))
        self.uis.append(TextUi("비밀번호 : ", (500, 300), self.fonts["galmuri"], 40, "white"))

        send_btn = TextButton("로그인!", self.fonts["galmuri"], 35, (500, 500), self.sfxs["ui_hover"], "yellow", "blue")
        self.uis.append(send_btn)
        create_btn = TextButton("전 계정이 없어요!", self.fonts["galmuri"], 35, (500, 600), self.sfxs["ui_hover"], "yellow", "blue")
        self.uis.append(create_btn)

        bg = self.assets["bg"]["office/1"]
        rect_surface = pg.Surface(bg.get_size(), pg.SRCALPHA)
        rect_surface.fill((0, 0, 0, 200)) 

        while True:
            self.screen.fill("black")
            self.camera.fill("black")

            self.screen.blit(bg, (0, 0))
            self.screen.blit(rect_surface, (0, 0))

            pg.draw.rect(self.screen, "black", (0, 0, 300, SCREEN_SCALE[1]))
            self.screen.blit(pg.transform.rotate(self.assets["ui"]["bottom_fade"], -90), (300, 0))

            mouse_click = pg.mouse.get_pressed(3)[0]
            if quit_btn.hovering and mouse_click:
                self.end_scene()
                self.state_title_screen()
            if send_btn.hovering and mouse_click:
                print(f"{email.text}, {password.text}")
            if create_btn.hovering and mouse_click:
                self.end_scene()
                self.state_make_account()

            self.manage_spark()
            self.manage_particle()
            self.manage_ui()
            self.manage_camera_shake()

            self.camera.blit(self.screen, self.shake)

            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit()
                    sys.exit()
                
                #tlqkf 왜 안됨?
                email.get_event(event)
                password.get_event(event)
    
            self.clock.tick(TARGET_FPS)
            pg.display.flip()

    #계정 생성
    def state_make_account(self):
        quit_btn = WiggleButtonUi(pg.transform.scale(self.assets["ui"]["quit"], (200, 100)), (70, 650), self.sfxs["ui_hover"], 1, 20)
        self.uis.append(quit_btn)

        account_id = InputField((750, 200), (500, 50), self.fonts["galmuri"], 30, "black", "white")
        self.uis.append(account_id)
        email = InputField((750, 300), (500, 50), self.fonts["galmuri"], 30, "black", "white")
        self.uis.append(email)
        password = InputField((750, 400), (500, 50), self.fonts["galmuri"], 30, "black", "white", True)
        self.uis.append(password)

        self.uis.append(TextUi("계정 생성", (500, 50), self.fonts["galmuri"], 60, "white"))
        self.uis.append(TextUi("아이디 : ", (500, 200), self.fonts["galmuri"], 40, "white"))
        self.uis.append(TextUi("이메일 : ", (500, 300), self.fonts["galmuri"], 40, "white"))
        self.uis.append(TextUi("비밀번호 : ", (500, 400), self.fonts["galmuri"], 40, "white"))

        send_btn = TextButton("계정 만들기", self.fonts["galmuri"], 35, (500, 500), self.sfxs["ui_hover"], "yellow", "blue")
        self.uis.append(send_btn)

        bg = self.assets["bg"]["office/1"]
        rect_surface = pg.Surface(bg.get_size(), pg.SRCALPHA)
        rect_surface.fill((0, 0, 0, 200)) 

        while True:
            self.screen.fill("black")
            self.camera.fill("black")

            self.screen.blit(bg, (0, 0))
            self.screen.blit(rect_surface, (0, 0))

            pg.draw.rect(self.screen, "black", (0, 0, 300, SCREEN_SCALE[1]))
            self.screen.blit(pg.transform.rotate(self.assets["ui"]["bottom_fade"], -90), (300, 0))

            mouse_click = pg.mouse.get_pressed(3)[0]
            if quit_btn.hovering and mouse_click:
                self.end_scene()
                self.state_login_menu()
            if send_btn.hovering and mouse_click:
                #계정 만들기 로직
                url = f"https://identitytoolkit.googleapis.com/v1/accounts:signUp?key=AIzaSyDGpmnNcJ2ZOShNz371uqmV3647ct7i4KE"
                payload = {
                    "email": email.text,
                    "password": password.text,
                    "returnSecureToken": True
                }
                response = requests.post(url, json=payload)
                if response.status_code == 200:
                    # 회원가입 성공 시 사용자 ID 토큰 반환
                    id_token = response.json().get('idToken')
                    print(f"User signed up successfully, ID Token: {id_token}")
                else:
                    print("Failed to sign up:", response.json())
                
                self.end_scene()
                self.state_title_screen()

            self.manage_spark()
            self.manage_particle()
            self.manage_ui()
            self.manage_camera_shake()

            self.camera.blit(self.screen, self.shake)

            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit()
                    sys.exit()
                
                #tlqkf 왜 안됨?
                email.get_event(event)
                password.get_event(event)
                account_id.get_event(event)
    
            self.clock.tick(TARGET_FPS)
            pg.display.flip()

    #스테이트 종료를 위한 클린업
    def end_scene(self):
        self.physic_rects.clear()
        self.particles.clear()
        self.sparks.clear()
        self.uis.clear()
        self.projectiles.clear()
        self.entities.clear()

    def on_player_kill(self, killed_entity : Entity):
        self.camera_shake_gain += 5
        print(f"killed : {killed_entity.name}")
        self.score += self.current_level_data["scores"][f"{killed_entity.name}_add_score"]

    def on_player_damaged(self, damage_amount):
        if self.player.blocking: 
            self.on_player_blocked()
            return
        self.player.take_damage(damage_amount)
        self.camera_shake_gain += 10

        if self.player.health <= 0:
            self.end_scene()
            self.state_game_result()
        else:
            self.sfxs["player_hurt"].play()

    def on_player_ammo_refilled(self, amount):
        self.player.add_ammo(amount)
        self.sfxs["reload"].play()

    def on_player_healed(self, amount):
        self.player.heal(amount)
        self.sfxs["heal"].play()

    def on_cannot_fire(self):
        pass

    def on_player_blocked(self):
        self.sfxs["parry"].play()
        self.camera_shake_gain += 10

     
#게임 실행
if __name__ == '__main__':
    game = Game()
    game.state_title_screen()
