#라이브러리 임포트
import pygame as pg
import sys, random, math, time
import requests
import time
import json

from Scripts.utils import load_image, load_images, load_data, set_data
from Scripts.Entities import Player, Entity, KillableEnemy, Obstacle, Ratbit, Helli, Brook, BlugLogger, Medicine, Ammo, Boss, Ufo, BossSoul
from Scripts.Animations import Animation
from Scripts.Particles import Spark, Particle
from Scripts.Ui import TextUi, ButtonUi, WiggleButtonUi, LinkUi, TextButton, InputField, Slider, VanishingTextUi, KeyInputField, VanishingImageUi
from Scripts.Bullets import Bullet, PlayerBullet, BossBullet

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
        pg.display.set_icon(load_image("UI/ExitNode.png"))

        self.clock = pg.time.Clock()
        self.current_time = pg.time.get_ticks()

        self.camera_shake_gain = 0
        self.camera_shrink_speed = .6
        self.shake = (self.camera_shake_gain * random.random(), self.camera_shake_gain * random.random())

        self.score = 0
        self.current_level_data = {}
        self.status = load_data("Status.json")

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
                "dogam" : load_image("UI/Dogam.png"),
                "setting" : load_image("UI/Settings.png"),
                "replay" : load_image("UI/Replay.png"),
                
                "made_by" : load_image("UI/MadeBy.png"),

                "world_bg" : load_image("UI/WorldBg.png"),
                "endless_bg" : load_image("UI/EndlessBg.png"),
                "credits_bg" : load_image("UI/CreditBg.png"),
                "records_bg" : load_image("UI/RankingBg.png"),
                "quit_bg" : load_image("UI/QuitBg.png"),
                "dogam_bg" : load_image("UI/DogamBg.png"),
                "setting_bg" : load_image("UI/SettingBg.png"),
                "login_bg" : load_image("UI/Login.png"),

                "credits_서준범_icon" : load_image("서준범.png"),
                "credits_이준영_icon" : load_image("못밤.png"),
                "credits_motbam_icon" : load_image("UI/CupMotbam.png"),

                "node" : load_image("UI/Node.png"),
                "exit_node" : load_image("UI/ExitNode.png"),
                "locked_node" : load_image("UI/Locked.png"),

                "pawn" : load_image("UI/Pawn.png"),

            },

            "projectiles" : {
                "bullet" : load_image("Projectiles/Bullet.png"),
                "helli_fire_bullet" : load_image("Projectiles/FireBullet.png"),
                "energy_bullet" : load_image("Projectiles/EnergyBullet.png"),
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

                "boss/idle" : Animation(load_images("Characters/Boss/Idle"), 8, True),
                "boss/change" : Animation(load_images("Characters/Boss/Change"), 8, True),
                "boss/attack" : Animation(load_images("Characters/Boss/Attack"), 8, True),

                "ufo/idle" : Animation(load_images("Characters/Ufo"), 8, True),
                "world_doom/idle" : Animation(load_images("Characters/Fire"), 4, True),
                "cannon/idle" : Animation(load_images("Projectiles/Cannon"), 4, True),
            },

            "props" : {
                "player/arm_gun" : load_image("Characters/Player/Arm.png"),
                "player/arm_shield" : load_image("Characters/Player/ArmShield.png"),
                "boss/arm" : load_image("Characters/Boss/Arm.png")
            },

            "bg" : {
                "office/0" : load_image("Backgrounds/office_0.png"),
                "office/1" : load_image("Backgrounds/office_1.png"),
                "steam_room/0" : load_image("Backgrounds/steam_room_0.png"),
                "steam_room/1" : load_image("Backgrounds/steam_room_1.png"),
                "foyer/0" : load_image("Backgrounds/foyer_0.png"),
                "foyer/1" : load_image("Backgrounds/foyer_1.png"),
                "secure_room/0" : load_image("Backgrounds/secure_room_0.png"),
                "secure_room/1" : load_image("Backgrounds/secure_room_1.png"),
                "horror_office/0" : load_image("Backgrounds/horror_office_0.png"),
                "horror_office/1" : load_image("Backgrounds/horror_office_1.png"),
                "dark_office/0" : load_image("Backgrounds/dark_office_0.png"),
                "dark_office/1" : load_image("Backgrounds/dark_office_1.png"),
                "desert/0" : load_image("Backgrounds/desert_0.png"),
                "desert/1" : load_image("Backgrounds/desert_1.png"),

                "light" : load_image("Backgrounds/Light.png"),
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

            "cutscenes" : {
                "start" : load_images("Cutscenes/Start"),
                "boss_intro" : load_images("Cutscenes/BossStart"),
                "boss_end" : load_images("Cutscenes/BossEnd"),
            },

            "dogam" : {
                "ratbit" : load_image("Characters/Ratbit/Idle/0.png"),
                "helli" : load_image("Characters/Helli/Idle/0.png"),
                "strucker" : load_image("Characters/Strucker/0.png"),
                "stalker" : load_image("Characters/Stalker/Idle/0.png"),
                "brook" : load_image("Characters/Brook/Idle/0.png"),
                "bluglogger" : load_image("Characters/Bluglogger/Idle/0.png")
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
            "gamewon" : pg.mixer.Sound('Assets/Sfxs/GameWin.wav'),
            "gameover" : pg.mixer.Sound('Assets/Sfxs/GameOver.mp3'),
            "explosion" : pg.mixer.Sound("Assets/Sfxs/Explosion.wav"),
            "cannon_fire" : pg.mixer.Sound("Assets/Sfxs/CannonFire.wav"),
            "ufo_attack" : pg.mixer.Sound("Assets/Sfxs/UfoAttack.wav"),
            "ufo_explosion" : pg.mixer.Sound("Assets/Sfxs/UfoExplosion.wav"),
            "world_doom" : pg.mixer.Sound("Assets/Sfxs/WorldDoom.wav"),
            "world_doom_start" : pg.mixer.Sound("Assets/Sfxs/WorldDoomStart.wav"),
            "world_doom_cancel" : pg.mixer.Sound("Assets/Sfxs/WorldDoomCancel.wav"),
            "drink" : pg.mixer.Sound("Assets/Sfxs/Drink.mp3"),
            "fire" :  pg.mixer.Sound("Assets/Sfxs/Fire.mp3"),
            "laser_shoot" :  pg.mixer.Sound("Assets/Sfxs/LaserShoot.wav"),
        }

        self.bgm = {
            "main_title" : pg.mixer.Sound("Assets/Bgms/GameTitle.wav"),
            "run1" : pg.mixer.Sound("Assets/Bgms/Run1.mp3"),
            "run2" : pg.mixer.Sound("Assets/Bgms/Run2.wav"),
            "world" : pg.mixer.Sound("Assets/Bgms/World.wav"),
            "result" : pg.mixer.Sound("Assets/Bgms/GameResult.ogg"),
            "dogam" : pg.mixer.Sound("Assets/Bgms/Dogam.wav"),
            "dialouge" : pg.mixer.Sound("Assets/Bgms/Dialogue.mp3"),
            "rankings" : pg.mixer.Sound("Assets/Bgms/Rankings.mp3"),
            "login" : pg.mixer.Sound("Assets/Bgms/Lab.mp3"),
            "boss" : pg.mixer.Sound("Assets/Bgms/Boss.wav")
        }

        #음량 설정
        self.set_volumes()

        #게임 폰트
        self.fonts = {
            "aggro" : 'Assets/Fonts/SB 어그로 B.ttf',
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
        fps_ui = TextUi(f"FPS : {int(self.clock.get_fps())}", (1540, 0), self.fonts["aggro"], 12, "white")
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
                    if isinstance(enemy, BossSoul):
                        if isinstance(projectile, BossBullet):
                            enemy.take_damage(projectile.damage)
                            self.projectiles.remove(projectile)
                    else:
                        enemy.take_damage(projectile.damage)
                        self.projectiles.remove(projectile)
                        
                    
            #플레이어 감지
            if not projectile.tag == "player's bullet" and self.player.get_rect().collidepoint(projectile.pos[0], projectile.pos[1]) and projectile in self.projectiles:
                #패링 : 적 탄막 => 플레이어 탄막으로 변경
                if self.player.blocking:
                    #패링
                    if projectile.shoot_by in self.entities:
                        projectile.direction =  pg.math.Vector2(projectile.shoot_by.get_center_pos().x - projectile.pos.x, projectile.shoot_by.get_center_pos().y - projectile.pos.y).normalize() * projectile.speed
                    else:
                        projectile.direction =  pg.math.Vector2(1, 0).normalize() * projectile.speed
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

    def spawn_items(self):
        if self.current_level_data["entities"]["medicine"] and random.randint(1, self.current_level_data["spawn_rates"]["medicine_spawn_rate"]) == 1:
            self.entities.append(
                Medicine(self, "medicine", FLOOR_SPAWN_POS, (130 , 130), (130, 130), 20, self.current_level_data["amount"]["heal_amount"])
            )
        #추가 탄약은 플레이어가 최대 탄약이 아닐때 생김
        if self.player.ammo != self.player.max_ammo and self.current_level_data["entities"]["ammo"] and random.randint(1, self.current_level_data["spawn_rates"]["ammo_spawn_rate"]) == 1:
            self.entities.append(
                Ammo(self, "ammo", FLOOR_SPAWN_POS, (130 , 130), (130, 130), 20, self.current_level_data["amount"]["ammo_amount"])
            )

    def spawn_boss_entity(self):
        if not any(isinstance(entity, Obstacle) for entity in self.entities):
            if self.current_level_data["entities"]["cannon"] and random.randint(1, self.current_level_data["spawn_rates"]["cannon_spawn_rate"]) == 1:
                self.sfxs["cannon_fire"].play()
                self.entities.append(Obstacle(self, "cannon", 
                                            pos=(FLOOR_SPAWN_POS[0], FLOOR_SPAWN_POS[1] + 10),
                                            size=(150, 150), anim_size=(150, 150), 
                                            speed=self.current_level_data["speed"]["cannon_speed"], damage=self.current_level_data["damages"]["cannon_damage"]))
        
        if self.current_level_data["entities"]["ufo"] and random.randint(1, self.current_level_data["spawn_rates"]["ufo_spawn_rate"]) == 1:
            self.entities.append(Ufo(self, "ufo", (1600, 0), (150, 150), (150, 150),
                                     self.current_level_data["speed"]["ufo_move_speed"], self.current_level_data["healths"]["ufo_health"],
                                     self.current_level_data["damages"]["ufo_damage"], self.current_level_data["speed"]["ufo_attack_speed"]))

    def state_made_by(self):
        timer = 180
        self.sfxs["drink"].play()
        while True:
            self.screen.fill("black")
            self.camera.fill("black")

            self.screen.blit(pg.transform.scale(self.assets["ui"]["made_by"], SCREEN_SCALE), (0, 0))

            self.manage_spark()
            self.manage_particle()
            self.manage_ui()
            self.manage_camera_shake()

            if timer <= 0:
                self.end_scene()
                self.state_title_screen()
            else:
                timer -= 1

            self.camera.blit(self.screen, self.shake)

            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self.end_scene()
                    pg.quit()
                    sys.exit()
    
            self.clock.tick(TARGET_FPS)
            pg.display.flip()

    #타이틀 스크린
    def state_title_screen(self):
        #start:
        margin = 150
        y_offset = 0
        scroll_speed = 30
        btns = []
        map_btn = WiggleButtonUi(pg.transform.scale(self.assets["ui"]["world"], (200, 150)), (500, 20), self.sfxs["ui_hover"], 1, 20)
        endless_btn = WiggleButtonUi(pg.transform.scale(self.assets["ui"]["endless"], (200, 150)), (500, 20 + margin), self.sfxs["ui_hover"], 1, 20)
        records_btn = WiggleButtonUi(pg.transform.scale(self.assets["ui"]["records"], (200, 150)), (500, 20 + margin * 2), self.sfxs["ui_hover"], 1, 20)
        credits_btn = WiggleButtonUi(pg.transform.scale(self.assets["ui"]["credits"], (200, 150)), (500, 20 + margin * 3), self.sfxs["ui_hover"], 1, 20)
        dogam_btn = WiggleButtonUi(pg.transform.scale(self.assets["ui"]["dogam"], (200, 150)), (500, 20 + margin * 4), self.sfxs["ui_hover"], 1, 20)
        setting_btn = WiggleButtonUi(pg.transform.scale(self.assets["ui"]["setting"], (200, 150)), (500, 20 + margin * 5), self.sfxs["ui_hover"], 1, 20)
        quit_btn = WiggleButtonUi(pg.transform.scale(self.assets["ui"]["quit"], (200, 150)), (500, 20 + margin * 6), self.sfxs["ui_hover"], 1, 20)

        btns.append(map_btn)
        btns.append(endless_btn)
        btns.append(records_btn)
        btns.append(credits_btn)
        btns.append(dogam_btn)
        btns.append(quit_btn)
        btns.append(setting_btn)

        for btn in btns:
            self.uis.append(btn)

        tokenFile = open("token.txt", "r")
        token = tokenFile.read()

        user = 0
        if token:
            try:
                # ID 토큰을 검증하여 사용자 정보 가져오기
                decoded_token = auth.verify_id_token(token, clock_skew_seconds=30)
                uid = decoded_token['uid']
                user = auth.get_user(uid)
                
                # 사용자 정보 출력
                #print("User ID:", user.uid)
                #print("Email:", user.email)

                doc_ref = db.collection("users").document(user.uid)
                doc = doc_ref.get()
                if doc.exists:
                    #print("Nickname:", doc.to_dict()["name"])
                    pass
                else:
                    print("에러! : 계정 정보 없음")
                
            except auth.InvalidIdTokenError:
                tokenFile = open("token.txt", "w")
                w = tokenFile.write("")
                tokenFile.close()

            except Exception as e:
                print("Error verifying ID token:", e)

        login_btn = TextButton(doc.to_dict().get("name") if token and user else "<로그인해주세요 현재 : 익명", self.fonts["aggro"], 30, (30, 560), self.sfxs["ui_hover"], "yellow", "blue")
        logout_btn = 0
        save_data_btn = 0
        get_data_btn = 0
        if token and user:
            logout_btn = TextButton("로그아웃", self.fonts["aggro"], 30, (30, 610), self.sfxs["ui_hover"], "yellow", "blue")
            self.uis.append(logout_btn)
            save_data_btn = TextButton("정보 저장", self.fonts["aggro"], 30, (30, 660), self.sfxs["ui_hover"], "yellow", "blue")
            self.uis.append(save_data_btn)
            get_data_btn = TextButton("정보 불러오기", self.fonts["aggro"], 30, (180, 660), self.sfxs["ui_hover"], "yellow", "blue")
            self.uis.append(get_data_btn)


        self.uis.append(login_btn)

        self.uis.append(VanishingTextUi(self, f"마우스 휠로 메뉴 스크롤", (800, 730), self.fonts["aggro"], 40, "white", 60, 5))

        hover_image = pg.Surface((100, 100))

        elapsed_time = 0

        self.set_bgm("main_title")

        while(True):
            #update:
            self.current_time = pg.time.get_ticks()

            #화면 초기화
            self.screen.fill("black")
            self.camera.fill("black")

            self.screen.blit(hover_image, (700, 0))
            self.screen.blit(pg.transform.rotate(self.assets["ui"]["bottom_fade"], -90), (800, 0))
            pg.draw.rect(self.screen, "black", (0, 0, 800, 800))

            self.screen.blit(self.assets["ui"]["title"], (0, 0))

            #버튼 위치 조정 
            for btn in btns:
                btn.pos[1] = 20 + y_offset + margin * btns.index(btn)
    
            #지도 버튼    tlqkf 나도 좀 똥코드인건 아는데 어쩔수가;
            if map_btn.hovering:
                hover_image = self.assets["ui"]["world_bg"]
            #엔드레스 게임으로
            if endless_btn.hovering:
                hover_image = self.assets["ui"]["endless_bg"]
            #리코드 볼수 있음
            if records_btn.hovering:
                hover_image = self.assets["ui"]["records_bg"]
            #크레딧
            if credits_btn.hovering:
                hover_image = self.assets["ui"]["credits_bg"]
            #나가기
            if quit_btn.hovering:
                hover_image = self.assets["ui"]["quit_bg"]
            #도감
            if dogam_btn.hovering:
                hover_image = self.assets["ui"]["dogam_bg"]
            #설정 드가자
            if setting_btn.hovering:
                hover_image = self.assets["ui"]["setting_bg"]
            #로그인
            if login_btn.hovering:
                hover_image = self.assets["ui"]["login_bg"]

            self.manage_spark()
            self.manage_particle()
            self.manage_ui()
            self.manage_camera_shake()

            #화면 렌더
            self.camera.blit(self.screen, (0, 0))

            #이벤트 리슨
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self.end_scene()
                    pg.quit()
                    sys.exit()
                if event.type == pg.MOUSEWHEEL:
                    if event.y < 0:
                        y_offset = max(y_offset - scroll_speed, -320)
                    else:
                        y_offset = min(y_offset + scroll_speed, 0)
                
                if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                    #지도 버튼
                    if map_btn.hovering:
                        self.end_scene()
                        self.state_main_world()
                    #엔드레스 게임으로
                    if endless_btn.hovering:
                        if token and user:
                            self.end_scene()
                            self.current_level_data = load_data("Assets/Levels/BigBreakout.json")
                            self.state_main_game(is_endless=True)
                        else:
                            self.uis.append(VanishingTextUi(self, f"무한 모드는 로그인 후 이용 가능합니다.", (800, 730), self.fonts["aggro"], 40, "red", 60, 5))
                            print("무한 모드는 로그인 후 이용 가능합니다.")
                            
                    #리코드 볼수 있음
                    if records_btn.hovering:
                        self.end_scene()
                        self.state_records()
                    #크레딧
                    if credits_btn.hovering:
                        self.end_scene()
                        self.state_credits()
                    #나가기
                    if quit_btn.hovering:
                        self.end_scene()
                        pg.quit()
                        sys.exit()
                    #도감
                    if dogam_btn.hovering:
                        self.end_scene()
                        self.state_dogam()
                    #설정 드가자
                    if setting_btn.hovering:
                        self.end_scene()
                        self.state_settings()
                    #로그인
                    if login_btn.hovering and user == 0:
                        self.end_scene()
                        self.state_login_menu()
                    #로그아웃
                    if logout_btn !=0 and logout_btn.hovering:
                        self.end_scene()
                        self.state_logout()
                    #정보 저장
                    if save_data_btn !=0 and save_data_btn.hovering:
                        with open("Status.json", "r", encoding="utf-8") as file:
                            status_data = json.load(file)

                        # high_scores 분리
                        high_scores = status_data.pop("high_scores")

                        # 기존 데이터는 그냥 저장
                        doc_ref = db.collection("users").document(user.uid)
                        doc_ref.update(status_data)
                        
                        current_high_scores = doc_ref.get()

                        # 이미 존재하면 비교해서 큰 데이터로 저장
                        if current_high_scores.exists:
                            current_high_scores = current_high_scores.to_dict().get("high_scores", {})
                            final_high_scores = {
                                key: max(high_scores.get(key, 0), current_high_scores.get(key, 0))
                                for key in set(high_scores) | set(current_high_scores)
                            }
                            doc_ref.update({"high_scores": final_high_scores})

                        # 아니면 그냥 저장
                        else:
                            doc_ref.update({"high_scores": high_scores})
                        
                        print("정보가 저장되었습니다.")
                    if get_data_btn !=0 and get_data_btn.hovering:
                        doc_ref = db.collection("users").document(user.uid)
                        data = doc_ref.get()

                        filtered_data = 0
                        if data:
                            filtered_data = {key: value for key, value in data.to_dict().items() if key != "name"}

                        with open("status.json", "w", encoding="utf-8") as file:
                            json.dump(filtered_data, file, indent=4, ensure_ascii=False)
                        
                        print("정보를 불러왔습니다.")

            dt = self.clock.tick(TARGET_FPS) / 1000
            elapsed_time += dt
            #카메라 업데이트
            pg.display.flip()

    #메인 게임
    def state_main_game(self, is_endless = False):
        #start:
        PAUSED = False #상수는 아니지만 그래도 중요하니까 ^^ 아시져?
        ENDING = False

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
        if is_endless:
            choice = random.choice(["office", "steam_room", "foyer", "secure_room", "horror_office", "dark_office"])
            background1 = self.assets["bg"][f"{choice}/0"]
            background2 = self.assets["bg"][f"{choice}/1"]

        bg_width = background1.get_width()
        bg_scroll_speed = 20

        bg_x1 = 0
        bg_x2 = bg_width

        light_pos = [1600, 0]

        #천장 & 바닥 & 배경
        floor = pg.rect.Rect(200, 700, SCREEN_SCALE[0], 100)
        ceil = pg.rect.Rect(200, 0, SCREEN_SCALE[0], 100)
        self.physic_rects = [floor, ceil]

        #ui
        stat_ui = TextUi("", (50, 30), self.fonts["aggro"], 30, "white")
        self.uis.append(stat_ui)

        #일시 정지 UI
        pause_bg = background1
        pause_rect_surface = pg.Surface(pause_bg.get_size(), pg.SRCALPHA)
        pause_rect_surface.fill((0, 0, 0, 200))
        esc_time = 35
        esc_pressing = False
        current_esc_time = 0
        esc_txt = TextUi("ESC를 꾹눌러 월드로 돌아가기", (100, 490), self.fonts["aggro"], 20, "white")

        duration = self.current_level_data["level_length"]
        start_pos = (1000, 22)
        end_pos = (1520, 22)
        start_time = time.time()

        self.set_bgm(f"run{random.randint(1, 2)}")
            
        while(True):
            #update:
            #화면 초기화
            self.screen.fill("black")
            self.camera.fill("black")
            
            #일시 정지에 영향을 받음
            if not PAUSED:
                self.current_time = pg.time.get_ticks()
                elapsed_time = time.time() - start_time
                
                #레벨 끝나기 1초전에 엔딩애니메이션 보여주기
                if duration - elapsed_time <= 1 and not is_endless:
                    ENDING = True
                    self.player.pos.x += 25
                    self.player.invincible = True
                    worm.pos.x -= 10

                #배경 움직이기
                if not ENDING:
                    bg_x1 -= bg_scroll_speed
                    bg_x2 -= bg_scroll_speed

                if bg_x1 <= -bg_width:
                    bg_x1 = bg_width
                if bg_x2 <= -bg_width:
                    bg_x2 = bg_width
    
                self.screen.blit(background1, (bg_x1, 0))
                self.screen.blit(background2, (bg_x2, 0))

                #엔딩 빛 애니메이션
                if ENDING:
                    light_pos[0] = max(light_pos[0] - 10, 1400)
                    self.screen.blit(self.assets["bg"]["light"], (light_pos[0], light_pos[1]))

                #UI렌더
                stat_ui.text = f"남은 탄: {self.player.ammo} | {self.score} | 거대 괴물로부터 남은 거리 : {self.player.health}cm"
                self.screen.blit(pg.transform.scale(self.assets["ui"]["bottom_fade"], (SCREEN_SCALE[0], 150)), (0, 700))
                self.screen.blit(pg.transform.flip(pg.transform.scale(self.assets["ui"]["bottom_fade"], (SCREEN_SCALE[0], 150)), False, True), (0, 0))
                self.screen.blit(pg.transform.flip(pg.transform.rotate(self.assets["ui"]["bottom_fade"], 90), True, False), (0, 0))

                #쿠키런 마냥 움직이는 바 어쩌구 유남생?
                current_pos = [0, 0]
                if not is_endless:
                    t = min(elapsed_time / duration, 1)

                    x = start_pos[0] + (end_pos[0] - start_pos[0]) * t
                    y = start_pos[1] + (end_pos[1] - start_pos[1]) * t
                    current_pos = [x, y]
                    pg.draw.line(self.screen, "white", (start_pos[0], start_pos[1] + 30), (end_pos[0], end_pos[1] + 30), 20)

                    #레벨 승리
                    if elapsed_time >= duration:
                        self.end_scene()
                        self.state_game_result(True)
                
                #플레이어 업데이트 & 렌더
                self.player.update(self.physic_rects)
                self.player.render(self.screen)
                #플레이어 업데이트 & 렌더 끝

                #적 스폰
                if not ENDING:
                    self.spawn_entity()
                    self.spawn_items()

                #매니징
                self.manage_projectiles()
                self.manage_camera_shake()
                self.manage_entity()
                #매니징 끝

                #구렁이 업데이트 ㅋㅋ
                if not ENDING: #체력에 따라서 구렁이 앞뒤로
                    worm.pos.x = -self.player.health * 2
                worm.update()
                worm.render(self.screen)
                #구렁이 ㅋㅋ 끝

                #매니징
                self.manage_particle()
                self.manage_spark()
                self.manage_ui()
                #매니징 끝 
                
                #ui인데 그 뭐냐 그거 움직이는거
                if not is_endless:
                    self.screen.blit(pg.transform.scale(self.assets["ui"]["pawn"], (60, 60)), (current_pos[0] - 30, current_pos[1]))

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
                #ESC를 꾹눌러야 월드로 나감
                if esc_pressing:
                    current_esc_time += 1
                if current_esc_time >= esc_time: #EARLY RETURN
                    self.end_scene()
                    self.state_main_world()
                    return
                
                self.screen.blit(pause_bg, (0, 0))
                self.screen.blit(pause_rect_surface, (0, 0))

                pg.draw.rect(self.screen, "black", (0, 0, 300, SCREEN_SCALE[1]))
                self.screen.blit(pg.transform.rotate(self.assets["ui"]["bottom_fade"], -90), (300, 0))

                paused_txt = TextUi("일시정지", (100, 300), self.fonts["aggro"], 100, "white")
                paused_txt.update()
                paused_txt.render(self.screen)
                space_txt = TextUi("스페이스바로 게임으로 돌아가기", (100, 420), self.fonts["aggro"], 30, "white")
                space_txt.update()
                space_txt.render(self.screen)
                esc_txt.update()
                esc_txt.render(self.screen)
                

                self.camera.blit(self.screen, (0, 0))

            #이벤트 리슨
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self.end_scene()
                    pg.quit()
                    sys.exit()

                if event.type == pg.KEYDOWN:
                    if event.key == self.status["key_bindings"]["점프키"]:
                        if self.player.jump(20):
                            self.sfxs["jump"].play()
                    if event.key == pg.K_SPACE:
                        if PAUSED:
                            PAUSED = False
                    
                    
                    if event.key == pg.K_ESCAPE:
                        if PAUSED: #ESC누르기 시작
                            current_esc_time += 1
                            esc_pressing = True
                            esc_txt.text = "계속 누르고 계세요.."
                        else :
                            PAUSED = True

                if event.type == pg.KEYUP:
                    if event.key == pg.K_ESCAPE:
                        if PAUSED: #ESC를 누르다 뗌
                            esc_pressing = False
                            current_esc_time = 0
                            esc_txt.text = "ESC를 꾹눌러 월드로 돌아가기"
                        
                
                #마우스가 창밖에 나가면 PAUSE
                if event.type == pg.ACTIVEEVENT:
                    if event.gain == 0:
                        PAUSED = True
            #이벤트 리슨 끝

            self.clock.tick(TARGET_FPS)
            #카메라 업데이트
            pg.display.flip()
    
    #보스 게임
    def state_boss(self):
        #start:
        PAUSED = False #상수는 아니지만 그래도 중요하니까 ^^ 아시져?

        #플레이어 : game, name, pos, hit_box_size, anim_size, max health
        self.player = Player(self, "player", 
                            pos=(200, 640), size=(70, 170), anim_size=(170, 170),
                            max_health=100, 
                            gun_img=self.assets["props"]["player/arm_gun"], shield_img=self.assets["props"]["player/arm_shield"],
                            max_rotation=100,
                            max_block_time=15, attack_damage=20, bullet_speed=45, 
                            offset=(55, 75))
        self.player.anim_offset = [-25, 20]
        self.player_movement = [False, False]
        self.player_speed = 8
        #총 세팅
        gun_cooltime = 300 #.3초
        gun_fire_shake = 4.5
        last_fire_time = pg.time.get_ticks()
        last_block_time = pg.time.get_ticks()
        block_cooltime = 800

        #백그라운드 스크롤
        background1 = self.assets["bg"][f"{self.current_level_data['bg_name']}/0"]
        background2 = self.assets["bg"][f"{self.current_level_data['bg_name']}/1"]

        bg_width = background1.get_width()
        bg_scroll_speed = 20

        bg_x1 = 0
        bg_x2 = bg_width
        rect_surface = pg.Surface(background1.get_size(), pg.SRCALPHA)
        rect_surface.fill((0, 0, 0, 70))

        #천장 & 바닥 & 배경
        floor = pg.rect.Rect(0, 700, SCREEN_SCALE[0], 100)
        ceil = pg.rect.Rect(0, 0, SCREEN_SCALE[0], 100)
        self.physic_rects = [floor, ceil]

        #ui
        stat_ui = TextUi("", (50, 30), self.fonts["aggro"], 30, "white")
        self.uis.append(stat_ui)

        #일시 정지 UI
        pause_bg = background1
        pause_rect_surface = pg.Surface(pause_bg.get_size(), pg.SRCALPHA)
        pause_rect_surface.fill((0, 0, 0, 200))
        esc_time = 35
        esc_pressing = False
        current_esc_time = 0
        esc_txt = TextUi("ESC를 꾹눌러 월드로 돌아가기", (100, 490), self.fonts["aggro"], 20, "white")

        duration = self.current_level_data["level_length"]
        start_pos = (1000, 22)
        end_pos = (1520, 22)
        start_time = time.time()

        self.set_bgm("boss")

        #보스
        boss = Boss(self, "boss", (1200, 150), (500, 500), (500, 500), 5000, self.assets["props"]["boss/arm"], self.current_level_data["damages"]["boss_bullet_damage"], self.current_level_data["speed"]["boss_bullet_speed"], self.current_level_data["attack_chance"]["boss_attack_chance"], (280, 190))
        self.entities.append(boss)
        boss_soul = BossSoul(self, "world_doom", (1100, 300), (150, 150), (150, 150), 100, self.current_level_data["speed"]["world_doom_speed"])
        self.entities.append(boss_soul)
        self.boss_died = False

        self.uis.append(VanishingTextUi(self, f"{pg.key.name(self.status["key_bindings"]["좌로 움직이기키"]).upper()}, {pg.key.name(self.status["key_bindings"]["우로 움직이기키"]).upper()}로 움직이기", (650, 730), self.fonts["aggro"], 40, "white", 60, 5))

        while(True):
            #update:
            #화면 초기화
            self.screen.fill("black")
            self.camera.fill("black")
            
            #일시 정지에 영향을 받음
            if not PAUSED:
                elapsed_time = time.time() - start_time
                self.current_time = pg.time.get_ticks()
                #배경 움직이기
                bg_x1 -= bg_scroll_speed
                bg_x2 -= bg_scroll_speed

                if bg_x1 <= -bg_width:
                    bg_x1 = bg_width
                if bg_x2 <= -bg_width:
                    bg_x2 = bg_width
    
                self.screen.blit(background1, (bg_x1, 0))
                self.screen.blit(background2, (bg_x2, 0))
                self.screen.blit(rect_surface, (0, 0))

                #UI렌더
                stat_ui.text = f"남은 탄: {self.player.ammo} | {self.score} | HP : {self.player.health}"

                #쿠키런 마냥 움직이는 바 어쩌구 유남생?
                current_pos = [0, 0]
                t = min(elapsed_time / duration, 1)

                x = start_pos[0] + (end_pos[0] - start_pos[0]) * t
                y = start_pos[1] + (end_pos[1] - start_pos[1]) * t
                current_pos = [x, y]
                pg.draw.line(self.screen, "white", (start_pos[0], start_pos[1] + 30), (end_pos[0], end_pos[1] + 30), 20)
                self.screen.blit(pg.transform.scale(self.assets["ui"]["pawn"], (60, 60)), (current_pos[0] - 30, current_pos[1]))

                #레벨 승리
                if self.boss_died:
                    self.end_scene()
                    self.state_cut_scene(self.assets["cutscenes"]["boss_end"], self.state_game_result)
                    
                boss_soul.check_time(elapsed_time)
                self.spawn_boss_entity()
                self.spawn_items()

                #플레이어 업데이트 & 렌더
                self.player.update(self.physic_rects, self.player_movement, self.player_speed)
                self.player.pos[0] = min(max(self.player.pos[0], 0), 700)
                self.player.render(self.screen)
                #플레이어 업데이트 & 렌더 끝

                #매니징
                self.manage_projectiles()
                self.manage_camera_shake()
                self.manage_entity()
                #매니징 끝

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
                #ESC를 꾹눌러야 월드로 나감
                if esc_pressing:
                    current_esc_time += 1
                if current_esc_time >= esc_time: #EARLY RETURN
                    self.end_scene()
                    self.state_main_world()
                    return
                
                self.screen.blit(pause_bg, (0, 0))
                self.screen.blit(pause_rect_surface, (0, 0))

                pg.draw.rect(self.screen, "black", (0, 0, 300, SCREEN_SCALE[1]))
                self.screen.blit(pg.transform.rotate(self.assets["ui"]["bottom_fade"], -90), (300, 0))

                paused_txt = TextUi("일시정지", (100, 300), self.fonts["aggro"], 100, "white")
                paused_txt.update()
                paused_txt.render(self.screen)
                space_txt = TextUi("스페이스바로 게임으로 돌아가기", (100, 420), self.fonts["aggro"], 30, "white")
                space_txt.update()
                space_txt.render(self.screen)
                esc_txt.update()
                esc_txt.render(self.screen)
                

                self.camera.blit(self.screen, (0, 0))

            #이벤트 리슨
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self.end_scene()
                    pg.quit()
                    sys.exit()

                if event.type == pg.KEYDOWN:
                    if event.key == self.status["key_bindings"]["점프키"]:
                        if self.player.jump(20):
                            self.sfxs["jump"].play()
                    if event.key == pg.K_SPACE:
                        if PAUSED:
                            PAUSED = False

                    if event.key == self.status["key_bindings"]["좌로 움직이기키"] and not PAUSED:
                        self.player_movement[1] = True
                    if event.key == self.status["key_bindings"]["우로 움직이기키"] and not PAUSED:
                        self.player_movement[0] = True
                    
                    if event.key == pg.K_ESCAPE:
                        if PAUSED: #ESC누르기 시작
                            current_esc_time += 1
                            esc_pressing = True
                            esc_txt.text = "계속 누르고 계세요.."
                        else :
                            PAUSED = True
                
                if event.type == pg.KEYUP:
                    if event.key == pg.K_ESCAPE:
                        if PAUSED: #ESC를 누르다 뗌
                            esc_pressing = False
                            current_esc_time = 0
                            esc_txt.text = "ESC를 꾹눌러 월드로 돌아가기"
                    if event.key == self.status["key_bindings"]["좌로 움직이기키"]:
                        self.player_movement[1] = False
                    if event.key == self.status["key_bindings"]["우로 움직이기키"]:
                        self.player_movement[0] = False
                        
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

        #처음 플레이한다면 컷씬 시작 Early Return
        if self.status["is_first_play"]:
            self.end_scene()
            self.state_cut_scene(self.assets["cutscenes"]["start"], self.first_play_cutscene)

        quit_btn = WiggleButtonUi(pg.transform.scale(self.assets["ui"]["quit"], (200, 150)), (70, 650), self.sfxs["ui_hover"], 1, 20)
        self.uis.append(quit_btn)

        bg = self.assets["level_world"]

        button_pos = [(390, 40), (500, 200), (920, 340), (1250, 450), (1070, 580), (1200, 700), (1500, 680)]
        buttons = []
        for i in range(6):
            btn = ButtonUi(pg.transform.scale(self.assets["ui"]["node"] if i < self.status["level"] else self.assets["ui"]["locked_node"], (50, 50)), button_pos[i], self.sfxs["ui_hover"])
            buttons.append(btn)
            self.uis.append(btn)

        boss_btn = ButtonUi(pg.transform.scale(self.assets["ui"]["exit_node"], (50, 50)), button_pos[6], self.sfxs["ui_hover"])
        self.uis.append(boss_btn)

        selected_level = 0
        text = TextUi("", (10, 10), self.fonts["aggro"], 60, "white")
        self.uis.append(text)
        escape_btn = WiggleButtonUi(pg.transform.scale(self.assets["ui"]["escape"], (200, 150)), (70, 500), self.sfxs["ui_hover"], 1, 20)

        level_name = TextUi("", (10, 100), self.fonts["aggro"], 40, "white")
        self.uis.append(level_name)
        high_score = TextUi("", (10, 150), self.fonts["aggro"], 30, "white")
        self.uis.append(high_score)

        line_pos = []
        for pos in button_pos:
            line_pos.append((pos[0] + 25, pos[1] + 25))

        self.set_bgm("world")

        while True:
            self.screen.fill("black")
            self.camera.fill("black")

            self.screen.blit(bg, (-200, 0))

            pg.draw.rect(self.screen, "black", (0, 0, 300, SCREEN_SCALE[1]))
            self.screen.blit(pg.transform.rotate(self.assets["ui"]["bottom_fade"], -90), (300, 0))
            
            pg.draw.lines(self.screen, "red", False, line_pos, 5)

            mouse_click = pg.mouse.get_pressed(3)[0]

            #레벨 선택
            for btn in buttons:
                if btn.hovering and mouse_click and buttons.index(btn) + 1 <= self.status["level"]:
                    selected_level = buttons.index(btn) + 1
                    text.text = f"{selected_level} 레벨"
                    high_score.text = f"하이스코어: {self.status['high_scores'][str(buttons.index(btn) + 1)]}"
                    #high_score.text = "하이스코어 : {}".format(self.status["high_scores"][str(buttons.index(btn) + 1)])
                    level_name.text = f"\"{load_data(f"Assets/Levels/{selected_level}.json")["level_name"]}\""
                    if not escape_btn in self.uis:
                        self.uis.append(escape_btn)
            if boss_btn.hovering and mouse_click and self.status["level"] > 6:
                selected_level = "Boss"
                text.text = f"{selected_level} 레벨"
                high_score.text = f"하이스코어 : {self.status["high_scores"]["Boss"]}"
                level_name.text = f"\"{load_data(f"Assets/Levels/{selected_level}.json")["level_name"]}\""
                if not escape_btn in self.uis:
                        self.uis.append(escape_btn)
            
            #게임 시작
            if escape_btn.hovering and mouse_click:
                self.end_scene()
                self.current_level_data = load_data(f"Assets/Levels/{selected_level}.json")
                if selected_level == "Boss":
                    #보su!!
                    self.current_level_data = load_data(f"Assets/Levels/Boss.json")
                    #self.state_boss()
                    self.state_cut_scene(self.assets["cutscenes"]["boss_intro"], self.state_boss)
                else:
                    self.state_main_game()

            self.manage_spark()
            self.manage_particle()
            self.manage_ui()
            self.manage_camera_shake()

            self.camera.blit(self.screen, self.shake)

            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self.end_scene()
                    pg.quit()
                    sys.exit()
                if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                    if quit_btn.hovering:
                        self.end_scene()
                        self.state_title_screen()
    
            self.clock.tick(TARGET_FPS)
            pg.display.flip()

    #게임 종료
    def state_game_result(self, won = True):
        
        quit_btn = WiggleButtonUi(pg.transform.scale(self.assets["ui"]["quit"], (200, 150)), (700, 650), self.sfxs["ui_hover"], 1, 20)
        self.uis.append(quit_btn)
        map_btn = WiggleButtonUi(pg.transform.scale(self.assets["ui"]["world"], (200, 150)), (400, 650), self.sfxs["ui_hover"], 1, 20)
        self.uis.append(map_btn)
        replay_btn = WiggleButtonUi(pg.transform.scale(self.assets["ui"]["replay"], (200, 150)), (1000, 650), self.sfxs["ui_hover"], 1, 20)
        self.uis.append(replay_btn)

        bg = self.assets["bg"][f"{self.current_level_data["bg_name"]}/0"]
        rect_surface = pg.Surface(bg.get_size(), pg.SRCALPHA)
        rect_surface.fill((0, 0, 0, 200))
        
        self.uis.append(TextUi("탈출 성공!" if won else "탈출실패..", (300, 50), self.fonts["aggro"], 100, "white"))
        self.uis.append(TextUi(f"{self.score}점", (300, 200), self.fonts["aggro"], 55, "white"))

        if won:
            self.sfxs["gamewon"].play()
            if self.current_level_data["level_index"] == "Boss":
                set_data("Status.json", "level", 7)
            else:
                set_data("Status.json", "level", max(int(self.current_level_data["level_index"]) + 1, int(self.status["level"])))
        else:
            self.sfxs["gameover"].play()
            

        if self.score > self.status["high_scores"][f"{self.current_level_data["level_index"]}"]:
            set_data("Status.json", f"high_scores/{self.current_level_data['level_index']}", self.score)

        #db에 기록 저장
        if self.current_level_data["level_index"] == "BigBreakOut":
            tokenFile = open("token.txt", "r")
            token = tokenFile.read()

            try:
                # ID 토큰을 검증하여 사용자 정보 가져오기
                decoded_token = auth.verify_id_token(token, clock_skew_seconds=30)
                uid = decoded_token['uid']
                user = auth.get_user(uid)
                userDoc_ref = db.collection("users").document(user.uid)
                userData = userDoc_ref.get()

                #기존 자신의 랭킹 정보 불러오기
                doc_ref = db.collection("ranking").document(userData.to_dict().get("name"))
                doc = doc_ref.get()

                if doc.exists:
                    #기존 기록보다 좋을 때만 변경
                    if self.score > doc.to_dict().get("score"):
                        data = {
                            "score" : self.score
                        }
                        doc_ref.set(data)
                else:
                    data = {
                        "score" : self.score
                    }
                    doc_ref.set(data)
                    
            except Exception as e:
                print("Error verifying ID token:", e)
        
        self.status = load_data("Status.json")
        self.uis.append(TextUi(f"최고 점수 : {self.status["high_scores"][f"{self.current_level_data["level_index"]}"]}점", (300, 260), self.fonts["aggro"], 32, "white"))

        self.set_bgm("result")

        #점su 초기화잉
        self.score = 0

        while True:
            self.screen.fill("black")
            self.camera.fill("black")

            self.screen.blit(bg, (0, 0))
            self.screen.blit(rect_surface, (0, 0))

            pg.draw.rect(self.screen, "black", (0, 0, 300, SCREEN_SCALE[1]))
            self.screen.blit(pg.transform.rotate(self.assets["ui"]["bottom_fade"], -90), (300, 0))

            self.manage_spark()
            self.manage_particle()
            self.manage_ui()
            self.manage_camera_shake()

            self.camera.blit(self.screen, self.shake)

            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self.end_scene()
                    pg.quit()
                    sys.exit()
                if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                    if quit_btn.hovering:
                        self.end_scene()
                        self.state_title_screen()
                    if map_btn.hovering:
                        self.end_scene()
                        self.state_main_world()
                    if replay_btn.hovering:
                        self.end_scene()
                        if self.current_level_data["level_index"] == "Boss":
                            self.state_boss()
                        elif self.current_level_data["level_index"] == "BigBreakOut":
                            self.state_main_game(True)
                        else:
                            self.state_main_game(False)
                        
    
            self.clock.tick(TARGET_FPS)
            pg.display.flip()

    #크레딧
    def state_credits(self):

        quit_btn = WiggleButtonUi(pg.transform.scale(self.assets["ui"]["quit"], (200, 150)), (70, 650), self.sfxs["ui_hover"], 1, 20)
        self.uis.append(quit_btn)

        self.uis.append(TextUi("98세 못밤할아버지의 마지막 물 한모금 팀", (600, 50), self.fonts["aggro"], 50, "white"))

        self.uis.append(TextUi("서준범", (830, 220), self.fonts["aggro"], 50, "white"))
        self.uis.append(LinkUi("깃허브", (850, 520), self.fonts["aggro"], 40, "white", "blue", self.sfxs["ui_hover"], "https://github.com/Un-Uclied"))
        self.uis.append(LinkUi("유튜브", (850, 600), self.fonts["aggro"], 40, "white", "blue", self.sfxs["ui_hover"], "https://www.youtube.com/@null_plr/featured"))

        self.uis.append(TextUi("이준영    (<-못밤)", (1130, 220), self.fonts["aggro"], 50, "white"))
        self.uis.append(LinkUi("깃허브", (1150, 520), self.fonts["aggro"], 40, "white", "blue", self.sfxs["ui_hover"], "https://github.com/MicKoreaYoutube"))

        bg = self.assets["bg"]["office/1"]
        rect_surface = pg.Surface(bg.get_size(), pg.SRCALPHA)
        rect_surface.fill((0, 0, 0, 200))

        self.set_bgm("dogam")

        while True:
            self.screen.fill("black")
            self.camera.fill("black")

            self.screen.blit(bg, (0, 0))
            self.screen.blit(rect_surface, (0, 0))

            pg.draw.rect(self.screen, "black", (0, 0, 300, SCREEN_SCALE[1]))
            self.screen.blit(pg.transform.rotate(self.assets["ui"]["bottom_fade"], -90), (300, 0))

            self.screen.blit(self.assets["ui"]["credits"], (10, 5))

            self.screen.blit(self.assets["ui"]["credits_서준범_icon"], (800, 300))
            self.screen.blit(self.assets["ui"]["credits_이준영_icon"], (1100, 300))
            self.screen.blit(pg.transform.scale(self.assets["ui"]["credits_motbam_icon"], (100, 100)), (470, 30))

            self.manage_spark()
            self.manage_particle()
            self.manage_ui()
            self.manage_camera_shake()

            self.camera.blit(self.screen, self.shake)

            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self.end_scene()
                    pg.quit()
                    sys.exit()
                if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                    if quit_btn.hovering:
                        self.end_scene()
                        self.state_title_screen()
    
            self.clock.tick(TARGET_FPS)
            pg.display.flip()

    #로그인
    def state_login_menu(self):
        quit_btn = WiggleButtonUi(pg.transform.scale(self.assets["ui"]["quit"], (200, 150)), (70, 650), self.sfxs["ui_hover"], 1, 20)
        self.uis.append(quit_btn)

        email = InputField((750, 200), (500, 50), self.fonts["aggro"], 30, "black", "white")
        self.uis.append(email)
        password = InputField((750, 300), (500, 50), self.fonts["aggro"], 30, "black", "white", True)
        self.uis.append(password)

        self.uis.append(TextUi("로그인", (500, 50), self.fonts["aggro"], 60, "white"))
        self.uis.append(TextUi("이메일 : ", (500, 200), self.fonts["aggro"], 40, "white"))
        self.uis.append(TextUi("비밀번호 : ", (500, 300), self.fonts["aggro"], 40, "white"))

        send_btn = TextButton("로그인!", self.fonts["aggro"], 35, (500, 500), self.sfxs["ui_hover"], "yellow", "blue")
        self.uis.append(send_btn)
        create_btn = TextButton("전 계정이 없어요!", self.fonts["aggro"], 35, (500, 600), self.sfxs["ui_hover"], "yellow", "blue")
        self.uis.append(create_btn)

        error = TextUi("", (500, 350), self.fonts["aggro"], 35, "red")
        self.uis.append(error)

        bg = self.assets["bg"]["office/1"]
        rect_surface = pg.Surface(bg.get_size(), pg.SRCALPHA)
        rect_surface.fill((0, 0, 0, 200))

        self.set_bgm("login")

        while True:
            self.screen.fill("black")
            self.camera.fill("black")

            self.screen.blit(bg, (0, 0))
            self.screen.blit(rect_surface, (0, 0))

            pg.draw.rect(self.screen, "black", (0, 0, 300, SCREEN_SCALE[1]))
            self.screen.blit(pg.transform.rotate(self.assets["ui"]["bottom_fade"], -90), (300, 0))

            mouse_click = pg.mouse.get_pressed(3)[0]
            if send_btn.hovering and mouse_click:
                url = "https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key=AIzaSyDGpmnNcJ2ZOShNz371uqmV3647ct7i4KE"

                payload = {
                    "email": email.text,
                    "password": password.text,
                    "returnSecureToken": True
                }

                response = requests.post(url, json = payload)

                if response.status_code == 200:
                    # 로그인 성공 시 ID 토큰 반환
                    id_token = response.json().get('idToken')
                    #print(f"ID Token: {id_token}")

                    tokenFile = open("token.txt", "w")
                    w = tokenFile.write(id_token)
                    tokenFile.close()

                    self.end_scene()
                    self.state_title_screen()

                else:
                    print("Failed to sign in:", response.json())
                    target = ""
                    if response.json()["error"]["message"] == "INVALID_LOGIN_CREDENTIALS":
                        target = "비밀번호 오류!"
                    elif response.json()["error"]["message"] == "INVALID_EMAIL":
                        target = "메일주소가 유효하지 않습니다!"
                    error.text = f"오류! : {target}"

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
                    self.end_scene()
                    pg.quit()
                    sys.exit()
                if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                    if quit_btn.hovering:
                        self.end_scene()
                        self.state_title_screen()
                
                #tlqkf 왜 안됨?
                email.get_event(event)
                password.get_event(event)
    
            self.clock.tick(TARGET_FPS)
            pg.display.flip()

    #계정 생성
    def state_make_account(self):
        quit_btn = WiggleButtonUi(pg.transform.scale(self.assets["ui"]["quit"], (200, 150)), (70, 650), self.sfxs["ui_hover"], 1, 20)
        self.uis.append(quit_btn)

        email = InputField((850, 200), (500, 50), self.fonts["aggro"], 30, "black", "white")
        self.uis.append(email)
        password = InputField((850, 300), (500, 50), self.fonts["aggro"], 30, "black", "white", True)
        self.uis.append(password)
        passwordCheck = InputField((850, 400), (500, 50), self.fonts["aggro"], 30, "black", "white", True)
        self.uis.append(passwordCheck)
        nickname = InputField((850, 500), (500, 50), self.fonts["aggro"], 30, "black", "white")
        self.uis.append(nickname)

        self.uis.append(TextUi("계정 생성", (500, 50), self.fonts["aggro"], 60, "white"))
        self.uis.append(TextUi("이메일 : ", (500, 200), self.fonts["aggro"], 40, "white"))
        self.uis.append(TextUi("비밀번호 : ", (500, 300), self.fonts["aggro"], 40, "white"))
        self.uis.append(TextUi("비밀번호 확인 : ", (500, 400), self.fonts["aggro"], 40, "white"))
        self.uis.append(TextUi("닉네임 : ", (500, 500), self.fonts["aggro"], 40, "white"))

        send_btn = TextButton("계정 만들기", self.fonts["aggro"], 35, (500, 650), self.sfxs["ui_hover"], "yellow", "blue")
        self.uis.append(send_btn)

        bg = self.assets["bg"]["office/1"]
        rect_surface = pg.Surface(bg.get_size(), pg.SRCALPHA)
        rect_surface.fill((0, 0, 0, 200)) 

        error = TextUi("", (500, 550), self.fonts["aggro"], 35, "red")
        self.uis.append(error)

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
                if password.text == passwordCheck.text:
                    docs = db.collection("users").stream()

                    nickname_exists = False  # 닉네임 존재 여부를 추적하는 변수

                    for doc in docs:
                        if nickname.text == doc.to_dict().get("name"):
                            error.text = "오류! : 이미 사용 중인 닉네임입니다!"
                            nickname_exists = True
                            break  # 중복 닉네임을 찾으면 더 이상 확인하지 않고 종료

                    # 닉네임이 중복되지 않는 경우에만 회원가입 요청 실행
                    if not nickname_exists:
                        # API 요청 넣기
                        url = "https://identitytoolkit.googleapis.com/v1/accounts:signUp?key=AIzaSyDGpmnNcJ2ZOShNz371uqmV3647ct7i4KE"

                        payload = {
                            "email": email.text,
                            "password": password.text,
                            "returnSecureToken": True
                        }

                        response = requests.post(url, json=payload)

                        if response.status_code == 200:
                            # 회원가입 성공 시 사용자 ID 토큰 반환
                            id_token = response.json().get('idToken')

                            with open("token.txt", "w") as tokenFile:
                                tokenFile.write(id_token)

                            try:
                                # ID 토큰을 이용하여 사용자 정보 가져오기
                                with open("token.txt", "r") as tokenFile:
                                    token = tokenFile.read()

                                decoded_token = auth.verify_id_token(token, clock_skew_seconds=30)
                                uid = decoded_token['uid']
                                user = auth.get_user(uid)

                                # 유저의 정보를 db에 저장
                                data = {
                                    "name": nickname.text,
                                    "is_first_play": True,
                                    "need_to_see_made_by": False,
                                    "high_scores": {
                                        "BigBreakOut": 0,
                                        "1": 0,
                                        "2": 0,
                                        "3": 0,
                                        "4": 0,
                                        "5": 0,
                                        "6": 0,
                                        "Boss": 0
                                    },
                                    "key_bindings": {
                                        "좌로 움직이기키": 97,
                                        "우로 움직이기키": 100,
                                        "점프키": 32
                                    },
                                    "level": 1,
                                    "sfx_volume": 1,
                                    "bgm_volume": 1
                                }

                                doc_ref = db.collection("users").document(user.uid)
                                doc_ref.set(data)

                                self.end_scene()
                                self.state_title_screen()

                            except Exception as e:
                                print("Error verifying ID token:", e)

                        else:
                            print("Failed to sign up:", response.json())
                            target = ""
                            if response.json()["error"]["message"] == "INVALID_EMAIL":
                                target = "메일주소가 유효하지 않습니다!"
                            error.text = f"오류! : {target}"
                    # 비밀번호 확인이 일치하지 않는 경우
                else:
                    error.text = "오류! : 비밀번호와 비밀번호 확인란이 일치하지 않습니다!"


            self.manage_spark()
            self.manage_particle()
            self.manage_ui()
            self.manage_camera_shake()

            self.camera.blit(self.screen, self.shake)

            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self.end_scene()
                    pg.quit()
                    sys.exit()
                
                #tlqkf 왜 안됨?
                email.get_event(event)
                password.get_event(event)
                passwordCheck.get_event(event)
                nickname.get_event(event)
    
            self.clock.tick(TARGET_FPS)
            pg.display.flip()

    def state_logout(self):
        tokenFile = open("token.txt", "w")
        w = tokenFile.write("")
        tokenFile.close()

        clear_data = {
            "is_first_play": True,
            "need_to_see_made_by": False,
            "high_scores": {
            "BigBreakOut": 0,
                "1": 0,
                "2": 0,
                "3": 0,
                "4": 0,
                "5": 0,
                "6": 0,
                "Boss": 0
            },
            "key_bindings": {
                "좌로 움직이기키": 97,
                "우로 움직이기키": 100,
                "점프키": 32
            },
                "level": 1,
                "sfx_volume": 1,
                "bgm_volume": 1
        }

        with open("status.json", "w", encoding="utf-8") as file:
            json.dump(clear_data, file, indent=4, ensure_ascii=False)

        self.end_scene()
        self.state_title_screen()

    #레코드
    def state_records(self):
        
        quit_btn = WiggleButtonUi(pg.transform.scale(self.assets["ui"]["quit"], (200, 150)), (50, 650), self.sfxs["ui_hover"], 1, 20)
        self.uis.append(quit_btn)

        bg = self.assets["bg"]["office/0"]
        rect_surface = pg.Surface(bg.get_size(), pg.SRCALPHA)
        rect_surface.fill((0, 0, 0, 200))

        self.uis.append(TextUi("랭킹               닉네임                            점수", (500, 30), self.fonts["aggro"], 40, "white"))

        y_offset = 0
        scroll_speed = 60
        plr_texts = [] #[[rank : TextUi, nickname : TextUi, score : TextUi], [rank, nickname, score],]
        margin = 100
        #[["닉네임", 점수], ["닉네임", 점수]]

        rankingDatas = db.collection("ranking").stream()
        players = []

        for doc in rankingDatas:
            players.append([doc.id, doc.to_dict().get("score")])
            
        players.sort(key=lambda x: x[1], reverse=True)
        for plr in players:
            rank = TextUi(str(list.index(players, plr) + 1), (500, 150 + margin * list.index(players, plr)), self.fonts["aggro"], 40, "white")
            nickname = TextUi(plr[0], (700, 150 + margin * list.index(players, plr)), self.fonts["aggro"], 40, "white")
            score = TextUi(str(plr[1]), (1170, 150 + margin * list.index(players, plr)), self.fonts["aggro"], 40, "white")
            plr_texts.append([rank, nickname, score])
        
        
        self.set_bgm("rankings")

        while True:
            self.screen.fill("black")
            self.camera.fill("black")

            self.screen.blit(bg, (0, 0))
            self.screen.blit(rect_surface, (0, 0))

            #요 텍스트는 따로 관리 ㅇㅇ
            for ui_list in plr_texts: # ui_list = [rank : TextUi, nickname : TextUi, score : TextUi]
                for i in range(3):
                    ui_list[i].update()
                    ui_list[i].render(self.screen)
                    ui_list[i].pos[1] = 150 + margin * plr_texts.index(ui_list) + y_offset

            pg.draw.rect(self.screen, "black", (0, 0, 300, SCREEN_SCALE[1]))
            pg.draw.rect(self.screen, "black", (0, 0, SCREEN_SCALE[0], 100))
            self.screen.blit(pg.transform.scale(pg.transform.rotate(self.assets["ui"]["bottom_fade"], 180), (SCREEN_SCALE[0], 100)), (0, 100))
            self.screen.blit(pg.transform.rotate(self.assets["ui"]["bottom_fade"], -90), (300, 0))

            self.screen.blit(self.assets["ui"]["records"], (10, 5))

            self.manage_spark()
            self.manage_particle()
            self.manage_ui()
            self.manage_camera_shake()

            self.camera.blit(self.screen, self.shake)

            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self.end_scene()
                    pg.quit()
                    sys.exit()
                if event.type == pg.MOUSEWHEEL:
                    if event.y < 0:
                        y_offset -= scroll_speed
                    else:
                        y_offset = min(y_offset + scroll_speed, 0)
                if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                    if quit_btn.hovering:
                        self.end_scene()
                        self.state_title_screen()
    
            self.clock.tick(TARGET_FPS)
            pg.display.flip()

    #도감
    def state_dogam(self):
         
        quit_btn = WiggleButtonUi(pg.transform.scale(self.assets["ui"]["quit"], (200, 150)), (50, 650), self.sfxs["ui_hover"], 1, 20)
        self.uis.append(quit_btn)

        enemy_list = ["ratbit", "helli", "strucker", "stalker", "brook", "bluglogger"]        
        current_index = 0
        current_enemy = enemy_list[current_index]
        current_image = self.assets["dogam"][current_enemy]

        enemy_name_text = TextUi("ratbit", (750, 50), self.fonts["aggro"], 60, "black")
        self.uis.append(enemy_name_text)

        current_data = load_data(f"Assets/EntityDogam/{current_enemy.capitalize()}.json")

        explain_texts = []
        bigo_texts = []

        self.uis.append(VanishingTextUi(self, "(<- or A , -> or D)로 넘기기", (650, 730), self.fonts["aggro"], 40, "black", 240, 5))

        self.set_bgm("dogam")

        while True:
            self.screen.fill("black")
            self.camera.fill("black")

            pg.draw.rect(self.screen, "white", (0, 0, SCREEN_SCALE[0], SCREEN_SCALE[1]))

            pg.draw.rect(self.screen, "black", (0, 0, 300, SCREEN_SCALE[1]))
            self.screen.blit(pg.transform.rotate(self.assets["ui"]["bottom_fade"], -90), (300, 0))

            self.screen.blit(self.assets["ui"]["dogam"], (10, 5))

            current_enemy = enemy_list[current_index] 
            current_image = self.assets["dogam"][current_enemy]
            self.screen.blit(pg.transform.scale_by(current_image, 1.5), (400, 50))
            enemy_name_text.text = current_enemy

            #설명
            current_data = load_data(f"Assets/EntityDogam/{current_enemy.capitalize()}.json")
            lines = current_data["explain"].split("o")
            bigos = current_data["bigo"].split("o")
            margin = 40
            for explain in explain_texts:
                if explain in self.uis:
                    self.uis.remove(explain)
            for bigo in bigo_texts:
                if bigo in self.uis:
                    self.uis.remove(bigo)
                    
            for line in lines:
                text = TextUi(line, (750, 200 + margin * lines.index(line)), self.fonts["aggro"], 40, "black")
                explain_texts.append(text)
                self.uis.append(text)
            for bigo in bigos:
                text = TextUi(f"비고 : {bigo}" if bigos.index(bigo) == 0 else bigo, (750, 400 + margin * bigos.index(bigo)), self.fonts["aggro"], 30, "black")
                explain_texts.append(text)
                self.uis.append(text)
            #설명끝

            self.manage_spark()
            self.manage_particle()
            self.manage_ui()
            self.manage_camera_shake()

            self.camera.blit(self.screen, self.shake)

            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self.end_scene()
                    pg.quit()
                    sys.exit()
                if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                    if quit_btn.hovering:
                        self.end_scene()
                        self.state_title_screen()
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_RIGHT or event.key == pg.K_d:
                        current_index += 1
                    if event.key == pg.K_LEFT or event.key == pg.K_a:
                        current_index -= 1

                    #인덱스
                    if current_index == len(enemy_list):
                        current_index = 0
                    elif current_index == -1:
                        current_index = len(enemy_list) - 1

                    #설명 업데이트
                    current_data = load_data(f"Assets/EntityDogam/{current_enemy.capitalize()}.json")
                    lines = current_data["explain"].split("o")
                    bigos = current_data["bigo"].split("o")
                    margin = 40
                    for explain in explain_texts:
                        if explain in self.uis:
                            self.uis.remove(explain)
                    for bigo in bigo_texts:
                        if bigo in self.uis:
                            self.uis.remove(bigo)
                            
                    for line in lines:
                        text = TextUi(line, (750, 200 + margin * lines.index(line)), self.fonts["aggro"], 40, "black")
                        explain_texts.append(text)
                        self.uis.append(text)
                    for bigo in bigos:
                        text = TextUi(f"비고 : {bigo}" if bigos.index(bigo) == 0 else bigo, (750, 400 + margin * bigos.index(bigo)), self.fonts["aggro"], 30, "black")
                        explain_texts.append(text)
                        self.uis.append(text)
                    #설명 업데이트 끝
    
            self.clock.tick(TARGET_FPS)
            pg.display.flip()
    
    #음향 시작

    #음량 설정
    def state_settings(self):
         
        quit_btn = WiggleButtonUi(pg.transform.scale(self.assets["ui"]["quit"], (200, 150)), (50, 650), self.sfxs["ui_hover"], 1, 20)
        self.uis.append(quit_btn)

        bg = self.assets["bg"]["office/0"]
        rect_surface = pg.Surface(bg.get_size(), pg.SRCALPHA)
        rect_surface.fill((0, 0, 0, 200))

        index = 0
        need_to_change = False
        title = TextUi("음향 설정", (300, 50), self.fonts["aggro"], 70, "white")
        self.uis.append(title)

        #음향 설정
        sfx_vol = TextUi("효과음 음량 : {}".format(int(self.status["sfx_volume"] * 100)), (400, 200), self.fonts["aggro"], 50, "white")
        bgm_vol = TextUi("배경음악 음량 : {}".format(int(self.status["bgm_volume"] * 100)), (400, 400), self.fonts["aggro"], 50, "white")
        sfx_slider = Slider((700, 600), (500, 50), self.status["sfx_volume"], 0, 1)
        bgm_slider = Slider((700, 1000), (500, 50), self.status["bgm_volume"], 0, 1)

        self.uis.append(sfx_vol)
        self.uis.append(bgm_vol)
        self.uis.append(sfx_slider)
        self.uis.append(bgm_slider)
        #키바인딩 설정
        move_left_key = KeyInputField("좌로 움직이기키",(1000, 250), (200, 60), self.fonts["aggro"], 50, "white", "black", (550, 250))
        move_right_key = KeyInputField("우로 움직이기키",(1000, 350), (200, 60), self.fonts["aggro"], 50, "white", "black", (550, 350))
        jump_key = KeyInputField("점프키",(1000, 450), (200, 60), self.fonts["aggro"], 50, "white", "black", (550, 450))
        key_listener = [move_left_key, move_right_key, jump_key]
        for listener in key_listener:
            listener.key = self.status["key_bindings"][listener.name]
            listener.text = pg.key.name(self.status["key_bindings"][listener.name])


        self.uis.append(VanishingTextUi(self, "(<- or A , -> or D)로 넘기기", (650, 730), self.fonts["aggro"], 40, "white", 240, 5))
        
        key_listening = False
        keys = self.status["key_bindings"].values()

        while True:
            self.screen.fill("black")
            self.camera.fill("black")

            self.screen.blit(bg, (0, 0))
            self.screen.blit(rect_surface, (0, 0))

            pg.draw.rect(self.screen, "black", (0, 0, 300, SCREEN_SCALE[1]))
            self.screen.blit(pg.transform.rotate(self.assets["ui"]["bottom_fade"], -90), (300, 0))

            self.screen.blit(self.assets["ui"]["setting"], (10, 5))

            if index == 0 and need_to_change:
                need_to_change = False
                title.text = "음향 설정"
                #키바인딩 설정 숨기기
                for input_field in key_listener:
                    self.uis.remove(input_field)
                #음향효과 설정 보이기
                self.uis.append(sfx_vol)
                self.uis.append(bgm_vol)
                self.uis.append(sfx_slider)
                self.uis.append(bgm_slider)
            if index == 1 and need_to_change:
                need_to_change = False
                title.text = "키바인딩 설정"
                #음향효과 설정 숨기기
                self.uis.remove(sfx_vol)
                self.uis.remove(bgm_vol)
                self.uis.remove(sfx_slider)
                self.uis.remove(bgm_slider)
                #키바인딩 설정 보이기
                for input_field in key_listener:
                    self.uis.append(input_field)

            self.manage_spark()
            self.manage_particle()
            self.manage_ui()
            self.manage_camera_shake()

            if index == 0:
                sfx_vol.text = "효과음 음량 : {}".format(int(self.status["sfx_volume"] * 100))
                bgm_vol.text = "배경음악 음량 : {}".format(int(self.status["bgm_volume"] * 100))

                set_data("Status.json", "sfx_volume", sfx_slider.get_val())
                set_data("Status.json", "bgm_volume", bgm_slider.get_val())
            if index == 1:
                for input_field in key_listener:
                    set_data("Status.json", f"key_bindings/{input_field.name}", input_field.key)
            
            self.status = load_data("Status.json")

            actived = 0
            for key_field in key_listener:
                if key_field.active:
                    actived += 1
            if actived > 0:
                key_listening = True
            else : key_listening = False

            self.camera.blit(self.screen, self.shake)

            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self.end_scene()
                    pg.quit()
                    sys.exit()
                if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                    if quit_btn.hovering:
                        self.end_scene()
                        self.state_title_screen()
                if event.type == pg.KEYDOWN:
                    if (event.key == pg.K_a or event.key == pg.K_RIGHT) and not key_listening:
                        if index == 0: index = 1
                        else: index -= 1
                        need_to_change = True
                    if (event.key == pg.K_d or event.key == pg.K_LEFT) and not key_listening:
                        if index == 1: index = 0
                        else: index += 1
                        need_to_change = True
                    if key_listening:
                        pass

                if index == 1:
                    for input_field in key_listener:
                        input_field.get_event(event)

            self.set_volumes()
            
            self.clock.tick(TARGET_FPS)
            pg.display.flip()

    def set_volumes(self):
        for sfx in self.sfxs.values():
            sfx.set_volume(self.status["sfx_volume"])
        for 브금 in self.bgm.values():
            브금.set_volume(self.status["bgm_volume"])

    def set_bgm(self, name):
        for bgm in self.bgm.values():
            bgm.stop()
        self.bgm[name].play(loops = -1)

    #음향 끝
    #컷씬
    def state_cut_scene(self, images, func):
        current_index = 0
        cutscene_len = len(images) - 1
        cutscene_time = 10
        cutscene_current_time = 0
        can_next = False

        self.set_bgm("dialouge")

        while True:
            self.screen.fill("black")
            self.camera.fill("black")

            self.manage_spark()
            self.manage_particle()
            self.manage_ui()
            self.manage_camera_shake()

            self.screen.blit(images[min(current_index, cutscene_len)], (0, 0))

            self.camera.blit(self.screen, self.shake)

            cutscene_current_time += 1
            if cutscene_current_time > cutscene_time:
                can_next = True
            else:
                can_next = False

            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self.end_scene()
                    pg.quit()
                    sys.exit()
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_SPACE:
                        if can_next:
                            current_index += 1
                            cutscene_current_time = 0
                            if current_index > cutscene_len:
                                #컷씬 다봤을때 할거
                                func()
                                
    
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
        self.status = load_data("Status.json")

    def on_player_kill(self, killed_entity : Entity):
        self.camera_shake_gain += 5
        #print(f"killed : {killed_entity.name}")
        self.score += self.current_level_data["scores"][f"{killed_entity.name}_add_score"]

    def on_player_damaged(self, damage_amount):
        if self.player.invincible:
            return
        if self.player.blocking: 
            self.on_player_blocked()
            return
        self.player.take_damage(damage_amount)
        self.camera_shake_gain += 10

        if self.player.health <= 0:
            self.end_scene()
            self.state_game_result(False)
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

    #걍 컷씬 함수 여따가 만듬;
    def first_play_cutscene(self):
        set_data("Status.json", "is_first_play", False)
        self.end_scene()
        self.state_main_world()
     
# #게임 실행
game = Game()
game.state_made_by()
