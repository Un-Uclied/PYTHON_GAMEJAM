import pygame as pg
import math, random
from Scripts.Particles import Spark, Particle

class Entity:
    def __init__(self, game, name : str, pos : tuple, size : tuple, anim_size : tuple):
        self.anim_offset = [0,0]
        self.game = game
        self.name = name
        self.pos = pg.math.Vector2(pos[0], pos[1])
        self.size = size
        self.anim_size = anim_size
        self.mask_color = (0, 0, 0, 0)

        self.action = ''
        self.flipx = False
        #self.set_action('idle')

        #디버깅용 히트박스
        self.hit_box = pg.surface.Surface((self.size[0], self.size[1]))
        self.hit_box.fill('red')

    #히트박스
    def get_rect(self):
        return pg.rect.Rect(self.pos.x, self.pos.y, self.size[0], self.size[1])

    def update(self):
        self.animation.update()

    def set_action(self, action):
        if action != self.action:
            self.action = action
            self.animation = self.game.assets["entities"][self.name + '/' + self.action].copy()

    def render(self, surface, offset = (0, 0)):
        current_frame_img = pg.transform.scale(self.animation.img(), self.anim_size)
        surface.blit(pg.transform.flip(current_frame_img, self.flipx, 0), (self.pos.x - offset[0] + self.anim_offset[0], self.pos.y - offset[1] + self.anim_offset[1]))
        
        self.mask = pg.mask.from_surface(current_frame_img)
        self.mask_img = self.mask.to_surface(setcolor=self.mask_color, unsetcolor=(0,0,0,0))
        surface.blit(pg.transform.flip(self.mask_img, self.flipx, 0), (self.pos.x - offset[0] + self.anim_offset[0], self.pos.y - offset[1] + self.anim_offset[1]))

        #디버깅용
        #surface.blit(self.hit_box, (self.pos.x - offset[0], self.pos.y - offset[1]))


class MoveableEntity(Entity):
    #생성자
    def __init__(self, game, name, pos, size, anim_size):
        super().__init__(game, name, pos, size, anim_size)

        self.velocity = [0, 0]

        #충돌 가능
        self.collisions = {'up' : False, 'down' : False, 
                            'right' : False, 'left' : False}

    #update:
    def update(self, physic_rects : list, movement = [[0, 0], [0, 0]], move_speed = 1):
        # movement [[좌, 우], [하, 상]]
        
        # movement를 벡터로 변환
        movement_vector = pg.math.Vector2((movement[0][0] - movement[0][1]), (movement[1][0] - movement[1][1]))
        
        # 벡터가 0이 아니면 노멀라이즈
        if movement_vector.length() > 0:
            movement_vector = movement_vector.normalize()
        
        movement_vector *= move_speed

        frame_movement = (movement_vector.x + self.velocity[0],
                           movement_vector.y + self.velocity[1])

        # 콜리션 초기화
        self.collisions = {'up': False, 'down': False, 'right': False, 'left': False}

        
        self.pos.y += frame_movement[1]
        entity_rect = self.get_rect()
        # 상하 충돌 체크
        for collided_rect in physic_rects:
            if entity_rect.colliderect(collided_rect):
                # #ex) 아래로 가고 있음 & 충돌함 => 자신의 아래 = 벽의 위
                if frame_movement[1] > 0:
                    entity_rect.bottom = collided_rect.top
                    self.collisions['down'] = True
                if frame_movement[1] < 0:
                    entity_rect.top = collided_rect.bottom
                    self.collisions['up'] = True
                self.pos.y = entity_rect.y
                pass

        self.pos.x += frame_movement[0]
        entity_rect = self.get_rect()
        # 좌우 충돌 체크
        for rect in physic_rects:
            if entity_rect.colliderect(rect):
                if frame_movement[0] > 0:
                    entity_rect.right = rect.left
                    self.collisions['right'] = True
                if frame_movement[0] < 0:
                    entity_rect.left = rect.right
                    self.collisions['left'] = True
                self.pos.x = entity_rect.x

        # 캐릭터가 오른쪽을 보고 있는지 확인
        if frame_movement[0] > 0:
            self.flipx = False
        elif frame_movement[0] < 0:
            self.flipx = True

class Player(MoveableEntity):
    def __init__(self, game, name, pos, size, anim_size ,max_health):
        super().__init__(game, name, pos, size, anim_size)

        #Status / number
        self.health = max_health

        self.max_jump_count = 1
        self.current_jump_count = 0

        #Status / Bool
        self.on_ground = False
        
        #총
        self.gun = pg.surface.Surface(size)
        self.gun_offset = (0, 0)
        self.gun_rotation = 0
        self.gun_max_roatation = 0

        self.set_action("run")

    def give_gun(self, gun_img : pg.Surface, max_rotation : float, offset = (0, 0)):
        self.gun = gun_img
        self.gun_offset = offset
        self.gun_max_roatation = max_rotation

    def update(self, tilemap, movement=[[0, 0], [0, 0]], move_speed=0):
        super().update(tilemap, movement, move_speed)

        #중력 추가
        self.gravity(15, 10)

        #떨어지는 애니메이션
        if -self.velocity[1] < 0 and not self.on_ground and not self.collisions["down"]:
            self.set_action("fall")

        #바닥 충돌
        if self.collisions["down"]:
            self.on_ground = True
            self.current_jump_count = 0
            self.set_action("run")
            self.game.particles.append(Particle(self.game, "dusts", (self.get_foot_pos()[0] + 25 + (random.random() * 5), self.get_foot_pos()[1] + 25 + (random.random() * 5)), (50, 50),  (-5, -.1), frame=random.randint(0, 20)))
        else:
            self.on_ground = False

        #총 각도 계산
        mouse = pg.mouse.get_pos()
        x_dist = mouse[0] - self.pos.x
        y_dist = -(mouse[1] - self.pos.y)
        angle = math.degrees(math.atan2(y_dist, x_dist))
        self.gun_rotation = max(min(angle, self.gun_max_roatation), -self.gun_max_roatation)

    def render(self, surface : pg.surface.Surface, offset=(0, 0)):
        super().render(surface)

        #총 렌더
        render_gun = pg.transform.rotate(self.gun, self.gun_rotation)
        rect_gun = render_gun.get_rect(center = (self.pos.x + self.gun_offset[0] + offset[0], self.pos.y + self.gun_offset[1] + offset[1]))

        surface.blit(render_gun, rect_gun)

    def jump(self, jump_power : float):
        if self.current_jump_count == self.max_jump_count: return
        self.set_action("jump")
        self.current_jump_count += 1
        self.velocity[1] = -jump_power

        for i in range(15):
            self.game.sparks.append(
                    Spark(self.get_foot_pos(), math.radians(90 * random.random() + 45), 5, "grey")
                )
    
    def get_foot_pos(self):
        return (self.pos.x + self.size[0] / 2, self.pos.y + self.size[1])

    def take_damage(self, damage : int):
        #대미지 입히기
        self.health -= damage

    def gravity(self, max_gravity : float, gravity_strength : float):
        #중력 가속
        self.velocity[1] = min(max_gravity, self.velocity[1] + 0.1 * gravity_strength)

class MoveableEnemy(Entity):
    def __init__(self, game, name, pos, size, anim_size, move_speed):
        super().__init__(game, name, pos, size, anim_size)

        self.set_action('idle')

        self.target_pos = pos
        self.move_speed = move_speed

    def destroy(self):
        for i in range(5):
            self.game.particles.append(Particle(self.game, "blood",(self.pos.x - self.size[0] / 2, self.pos.y + self.size[1] / 2), (180, 180), [(10 * random.random()), 10 + (20 * random.random())], random.randint(0, 20)))
        for i in range(10):
            self.game.sparks.append(Spark((self.pos.x - self.size[0] / 2, self.pos.y + self.size[1] / 2), math.radians(360) * random.random(), 7, "black"))

    def update(self):
        super().update()

        target_vec = pg.math.Vector2(self.target_pos[0], self.target_pos[1])
        my_vec = pg.math.Vector2(self.pos.x, self.pos.y)

        self.move_direction = pg.math.Vector2(target_vec.x - my_vec.x, target_vec.y - my_vec.y).normalize()
        self.pos.x += self.move_direction.x * self.move_speed
        self.pos.y += self.move_direction.y * self.move_speed

class Obstacle(Entity):
    def __init__(self, game, name, pos, size, anim_size, speed):
        super().__init__(game, name, pos, size, anim_size)
        self.speed = speed
        self.set_action("idle")

    def update(self):
        super().update()
        self.pos.x -= self.speed

