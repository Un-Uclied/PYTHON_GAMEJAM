import pygame as pg, pytweening as pt
import math, random
from Scripts.Particles import Spark, Particle
from Scripts.Bullets import PlayerBullet, Bullet, BossBullet

class Entity:
    def __init__(self, game, name : str, pos : tuple, size : tuple, anim_size : tuple):
        self.anim_offset = [0,0]
        self.game = game
        self.name = name
        self.pos = pg.Vector2(pos[0], pos[1])
        self.size = size
        self.anim_size = anim_size
        self.mask_color = (0, 0, 0, 0)
        self.velocity = [0, 0]

        self.action = ''
        self.flipx = False
        #self.set_action('idle')

        #디버깅용 히트박스
        self.hit_box = pg.surface.Surface((self.size[0], self.size[1]))
        self.hit_box.fill('red')

    def update(self):
        self.animation.update()

        self.pos.x += self.velocity[0]
        self.pos.y += self.velocity[1]

    #히트박스
    def get_rect(self):
        return pg.rect.Rect(self.pos.x, self.pos.y, self.size[0], self.size[1])
    
    def get_center_pos(self):
        return pg.math.Vector2(self.pos.x + self.size[0] / 2, self.pos.y + self.size[1] / 2)

    def set_action(self, action):
        if action != self.action:
            self.action = action
            self.animation = self.game.assets["entities"][self.name + '/' + self.action].copy()

    def can_interact(self):
        pass

    def render(self, surface, offset = (0, 0)):
        current_frame_img = pg.transform.scale(self.animation.img(), self.anim_size)
        surface.blit(pg.transform.flip(current_frame_img, self.flipx, 0), (self.pos.x - offset[0] + self.anim_offset[0], self.pos.y - offset[1] + self.anim_offset[1]))
        
        # self.mask = pg.mask.from_surface(current_frame_img)
        # self.mask_img = self.mask.to_surface(setcolor=self.mask_color, unsetcolor=(0,0,0,0))
        # surface.blit(pg.transform.flip(self.mask_img, self.flipx, 0), (self.pos.x - offset[0] + self.anim_offset[0], self.pos.y - offset[1] + self.anim_offset[1]))

class MoveableEntity(Entity):
    #생성자
    def __init__(self, game, name, pos, size, anim_size):
        super().__init__(game, name, pos, size, anim_size)

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
    def __init__(self, game, name, pos, size, anim_size ,max_health, gun_img : pg.Surface, shield_img : pg.Surface, max_rotation : float, attack_damage, bullet_speed, max_block_time,  offset = (0, 0)):
        super().__init__(game, name, pos, size, anim_size)

        #Status / number
        self.max_health = max_health
        self.health = max_health
        self.invincible = False

        self.max_jump_count = 1
        self.current_jump_count = 0

        #Status / Bool
        self.on_ground = False
        
        #총
        self.gun = gun_img
        self.shield = shield_img

        self.current_arm = self.gun
        self.arm_offset = offset
        self.arm_rotation = 0
        self.arm_max_roatation = max_rotation
        self.current_mouse_angle = 0

        self.attack_damage = attack_damage
        self.bullet_speed = bullet_speed
        self.max_ammo = 25
        self.ammo = self.max_ammo

        self.max_block_time = max_block_time
        self.current_block_time = 0
        self.blocking = False

        self.set_action("run")

    def update(self, tilemap, movement=[0, 0], move_speed=0):
        super().update(tilemap, [[movement[0], movement[1]], [0, 0]], move_speed)

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
        self.current_mouse_angle = math.degrees(math.atan2(y_dist, x_dist))
        self.arm_rotation = max(min(self.current_mouse_angle, self.arm_max_roatation), -self.arm_max_roatation)

        if self.current_block_time > 0:
            self.current_block_time -= 1
        elif self.current_block_time == 0 and self.blocking:
            self.unuse_shield()

        self.animation.update()

    def render(self, surface : pg.surface.Surface, offset=(0, 0)):
        super().render(surface)

        #총 렌더
        render_arm = pg.transform.rotate(self.current_arm, self.arm_rotation)
        rect_arm = render_arm.get_rect(center = (self.pos.x + self.arm_offset[0] + offset[0], self.pos.y + self.arm_offset[1] + offset[1]))

        surface.blit(render_arm, rect_arm)
    
    def gun_fire(self, mouse_pos : tuple):
        if -self.arm_max_roatation <= self.current_mouse_angle <= self.arm_max_roatation:
            if self.blocking: return False
            if self.ammo == 0: 
                self.game.on_cannot_fire()
                return False

            self.ammo -= 1
            self.game.projectiles.append(
                PlayerBullet(self.game, self.get_center_pos(), pg.math.Vector2(mouse_pos[0] - self.get_center_pos().x, mouse_pos[1] - self.get_center_pos().y), self.bullet_speed, self.game.assets["projectiles"]["bullet"], 60, "player's bullet",self, self.attack_damage)
            )
            return True
        else:
            return False
    
    def use_shield(self):
        self.current_arm = self.shield
        self.blocking = True
        self.current_block_time = self.max_block_time
        for i in range(10):
            self.game.sparks.append(Spark(tuple(self.get_center_pos()), math.radians(360) * random.random(), 7, (0, 100, 255)))

    def unuse_shield(self):
        self.current_arm = self.gun
        self.blocking = False

    def jump(self, jump_power : float):
        if self.current_jump_count == self.max_jump_count: return False
        self.set_action("jump")
        self.current_jump_count += 1
        self.velocity[1] = -jump_power

        for i in range(15):
            self.game.sparks.append(
                    Spark(self.get_foot_pos(), math.radians(90 * random.random() + 45), 5, "grey")
                )
        
        return True
    
    def get_foot_pos(self):
        return (self.pos.x + self.size[0] / 2, self.pos.y + self.size[1])

    def take_damage(self, damage : int):
        #대미지 입히기
        self.health -= damage

    def heal(self, amount : int):
        self.health = min(self.health + amount, self.max_health)

    def add_ammo(self, amount):
        self.ammo = min(self.ammo + amount, self.max_ammo)

    def gravity(self, max_gravity : float, gravity_strength : float):
        #중력 가속
        self.velocity[1] = min(max_gravity, self.velocity[1] + 0.1 * gravity_strength)

class Enemy(Entity):
    def __init__(self, game, name, pos, size, anim_size, damage):
        super().__init__(game, name, pos, size, anim_size)
        self.set_action('idle')

        self.damage = damage 

    def attack(self):
        self.game.on_player_damaged(self.damage)

class KillableEnemy(Enemy):
    def __init__(self, game, name, pos, size, anim_size, health, damage):
        super().__init__(game, name, pos, size, anim_size, damage)
        
        self.health = health

    def take_damage(self, damage_amount):
        self.health -= damage_amount
        
        if self.health <= 0:
            self.game.on_player_kill(self)
            self.destroy()
            if self in self.game.entities : self.game.entities.remove(self)
            self.game.sfxs["enemy_dying"].play()
        else:
            self.game.sfxs["enemy_hit"].play()
            for i in range(5):
                self.game.particles.append(Particle(self.game, "blood", tuple(self.get_center_pos()), (180, 180), [(10 * random.random()), 10 + (20 * random.random())], random.randint(0, 20)))

    def destroy(self):
        for i in range(5):
            self.game.particles.append(Particle(self.game, "blood", tuple(self.get_center_pos()), (180, 180), [(10 * random.random()), 10 + (20 * random.random())], random.randint(0, 20)))
        for i in range(10):
            self.game.sparks.append(Spark(tuple(self.get_center_pos()), math.radians(360) * random.random(), 7, "black"))
        for i in range(10):
            self.game.sparks.append(Spark(tuple(self.get_center_pos()), math.radians(360) * random.random(), 7, "red"))

class FollowingEnemy(KillableEnemy):
    def __init__(self, game, name, pos, size, anim_size, following_speed, max_health, damage):
        super().__init__(game, name, pos, size, anim_size, max_health, damage)
        
        #한 지점을 따라가는 적
        self.target_pos = pg.math.Vector2(0, 0)
        self.move_speed = following_speed
        self.target_magnitude = 0
        self.threshold = 100

    def set_target(self, target_pos):
        self.target_pos = target_pos

    def update(self):
        super().update()

        self.target_magnitude = (self.target_pos - self.pos).magnitude()
        if self.target_magnitude > self.threshold:
            self.move_direction = pg.math.Vector2(self.target_pos.x - self.pos.x, self.target_pos.y - self.get_center_pos().y).normalize()
            self.pos.x += self.move_direction.x * self.move_speed
            self.pos.y += self.move_direction.y * self.move_speed

class Ratbit(FollowingEnemy):
    def __init__(self, game, name, pos, size, anim_size, following_speed : float, health : int, damage : int, attack_range : float):
        super().__init__(game, name, pos, size, anim_size, following_speed, health, damage)
        
        self.is_returning = False
        self.range = attack_range

    def update(self):
        super().update()
        self.set_target(self.game.player.get_center_pos())

        if self.is_returning:
            #화면 밖으로 나갔을때 릴리즈
            if self.pos.x + self.size[0] < 0:
                if self in self.game.entities : self.game.entities.remove(self)

    def set_target(self, target_pos):
        if not self.is_returning:
            super().set_target(target_pos)

    def can_interact(self):
        if (self.target_pos - self.pos).magnitude() < self.range and not self.is_returning:
            self.attack()
        if (self.target_pos - self.pos).magnitude() < self.range and self.is_returning:
            self.destroy()
            if self in self.game.entities : self.game.entities.remove(self)

    def attack(self):
        #패링 성공시 적 처치로 간주
        if self.game.player.blocking:
            self.game.on_player_blocked()
            self.game.on_player_kill(self)
        else:
            super().attack()

        self.set_target(pg.math.Vector2((1900, 400)))
        self.is_returning = True
        self.set_action("attack")
        
class Helli(FollowingEnemy):
    def __init__(self, game, name, pos, size, anim_size, speed, health, damage, up, down, attack_chance, bullet_speed):
        super().__init__(game, name, pos, size, anim_size, speed, health, damage)
        self.turn_magnitude = 100 #임의

        self.ceil_pos = pg.math.Vector2(up[0], up[1])
        self.floor_pos = pg.math.Vector2(down[0], down[1])

        self.target_pos = self.ceil_pos

        self.bullet_speed = bullet_speed
        self.attack_chance = attack_chance
        

    def update(self):
        super().update()
        if (self.target_pos - self.pos).magnitude() < self.turn_magnitude:
            if self.target_pos == self.ceil_pos:
                self.target_pos = self.floor_pos
            elif self.target_pos == self.floor_pos:
                self.target_pos = self.ceil_pos

    def can_interact(self):
        if (random.randint(1, self.attack_chance) == 1):
            self.attack()

    def attack(self):
        #탄막을 쏘기에 super().attack()안함
        self.game.sfxs["fire"].play()
        self.game.projectiles.append(Bullet(self.game, self.pos, pg.math.Vector2(-1, 0), self.bullet_speed, self.game.assets["projectiles"]["helli_fire_bullet"], 60, "helli's bullet", self, self.damage))

class Brook(FollowingEnemy):
    def __init__(self, game, name, pos, size, anim_size, start_following_speed, following_speed, max_health, damage, speed_change_speed):
        super().__init__(game, name, pos, size, anim_size, start_following_speed, max_health, damage)
        
        self.spawn_pos = pg.math.Vector2(pos[0], pos[1])
        self.target_pos = self.game.player.get_center_pos()
        self.attack_range = 120

        self.target_speed = following_speed
        self.speed_change_speed = speed_change_speed
        self.is_triggered = False
        self.trigger_timer = random.randint(120, 180)
        self.current_trigger_timer = 0

        self.blocked = False

    def update(self):
        super().update()

        if not self.blocked:
            self.target_pos = self.game.player.get_center_pos()
        else:
            #화면 밖으로 나갔을때 릴리즈
            if self.pos.x + self.size[0] < 0:
                if self in self.game.entities : self.game.entities.remove(self)

        if self.blocked and (self.spawn_pos - self.pos).magnitude() < self.attack_range:
            if self in self.game.entities : self.game.entities.remove(self)
        
        #점화
        if self.current_trigger_timer < self.trigger_timer:
            self.current_trigger_timer += 1
        if not self.is_triggered and self.current_trigger_timer >= self.trigger_timer:
            self.is_triggered = True
            self.set_action("triggered")

        # 점화시 움직임 속도 증가  
        if self.is_triggered and self.move_speed < self.target_speed:
            self.move_speed += self.speed_change_speed

    def take_damage(self, damage_amount):
        #죽을수 없음 공격했을시 EXPLODE
        self.attack()
        if self in self.game.entities : self.game.entities.remove(self)
        return
    
    def can_interact(self):
        #플레이어에 접근했을시
        if (self.target_pos - self.pos).magnitude() < self.attack_range and not self.blocked:
            #패링중
            if self.game.player.blocking:
                #튕김
                self.blocked = True
                self.target_pos = self.spawn_pos
                self.game.on_player_blocked()
                self.game.on_player_kill(self)
            #패링중이 아님
            else:
                #EXPLODE
                self.attack()
                if self in self.game.entities : self.game.entities.remove(self)

    def attack(self):
        for i in range(5):
            self.game.particles.append(Particle(self.game, "flame", (self.get_center_pos().x, self.get_center_pos().y), (300, 300), (random.randint(-5, 5), random.randint(10, 30))))
        for i in range(30):
            self.game.sparks.append(Spark(self.get_center_pos(), math.radians(360 * random.random()), 16, "red"))
        
        super().attack()

        self.game.sfxs["explosion"].play()

        #Brook, 플레이어를 제외한 모든 적 제거
        for enemy in self.game.entities:
            if hasattr(enemy, "take_damage") and not isinstance(enemy, Player) and not isinstance(enemy, Brook):
                enemy.take_damage(1000)

class Obstacle(Enemy):
    def __init__(self, game, name, pos, size, anim_size, speed, damage):
        super().__init__(game, name, pos, size, anim_size, damage)
        self.speed = speed 

        #1회 공격만 가능
        self.attacked = False

    def update(self):
        super().update()
        #왼쪽으로 이동
        self.pos.x -= self.speed

        #화면 밖으로 나갔을때 릴리즈
        if self.pos.x + self.size[0] < 0:
            if self in self.game.entities : self.game.entities.remove(self)

    def can_interact(self):
        if self.game.player.get_rect().colliderect(self.get_rect()) and not self.attacked:
            self.attacked = True
            self.attack()

class BlugLogger(FollowingEnemy):
    def __init__(self, game, name, pos, size, anim_size, following_speed, max_health, damage, wait_time, attack_rate):
        super().__init__(game, name, pos, size, anim_size, following_speed, max_health, damage)
        self.wait_time = wait_time
        self.current_wait_time = 0
        self.is_attack = False

        self.target_pos = pg.math.Vector2(self.pos.x - 400, self.pos[1] + 80)

        self.beam : pg.Surface = self.game.assets["entities"]["beam"]

        self.current_attack_time = 0
        self.attack_rate = attack_rate
        
    def can_interact(self):
        if self.current_wait_time < self.wait_time and not self.is_attack:
            self.current_wait_time += 1
        else:
            self.is_attack = True
            self.set_action("attack")

        if self.is_attack and self.game.player.pos.y + 100 >= self.pos.y and self.current_attack_time > self.attack_rate:
            self.attack()
            self.current_attack_time = 0

    def update(self):
        super().update()
        self.current_attack_time += 1

            
    def render(self, surface, offset=(0, 0)):
        super().render(surface, offset)
        if self.is_attack:
            surface.blit(self.beam, (self.pos.x - self.beam.get_size()[0] + 20, self.pos.y))

class Medicine(Entity):
    def __init__(self, game, name, pos, size, anim_size, speed, heal_amount):
        super().__init__(game, name, pos, size, anim_size)
        self.set_action("idle")
        self.speed = speed

        self.heal_amount = heal_amount
        self.healed = False

    def set_action(self, action):
        if action != self.action:
            self.action = action
            self.animation = self.game.assets["items"][self.name + '/' + self.action].copy()
    
    def update(self):
        super().update()
        self.pos.x -= self.speed

        #화면 밖으로 나갔을때 릴리즈
        if self.pos.x + self.size[0] < 0:
            if self in self.game.entities : self.game.entities.remove(self)

    def can_interact(self):
        if self.game.player.get_rect().colliderect(self.get_rect()) and not self.healed:
            self.healed = True
            self.game.on_player_healed(self.heal_amount)
            self.set_action("use")
            for i in range(30):
                self.game.sparks.append(Spark(self.get_center_pos(), math.radians(360 * random.random()), 7, "green"))

class Ammo(Entity):
    def __init__(self, game, name, pos, size, anim_size, speed, ammo_refill_amount):
        super().__init__(game, name, pos, size, anim_size)
        self.set_action("idle")
        self.speed = speed

        self.add_amount = ammo_refill_amount
        self.used = False

    def set_action(self, action):
        if action != self.action:
            self.action = action
            self.animation = self.game.assets["items"][self.name + '/' + self.action].copy()
    
    def update(self):
        super().update()
        self.pos.x -= self.speed

        #화면 밖으로 나갔을때 릴리즈
        if self.pos.x + self.size[0] < 0:
            if self in self.game.entities : self.game.entities.remove(self)

    def can_interact(self):
        if self.game.player.get_rect().colliderect(self.get_rect()) and not self.used:
            self.used = True
            self.game.on_player_ammo_refilled(self.add_amount)
            self.set_action("use")
            for i in range(30):
                self.game.sparks.append(Spark(self.get_center_pos(), math.radians(360 * random.random()), 7, "green"))

class Boss(Enemy):
    def __init__(self, game, name, pos, size, anim_size ,max_health, gun_img : pg.Surface, attack_damage, bullet_speed, attack_chance, offset = (0, 0)):
        super().__init__(game, name, pos, size, anim_size, attack_damage)
        #Status / number
        self.max_health = 6
        self.health = 6
        
        #총
        self.gun = gun_img

        self.current_arm = self.gun
        self.arm_offset = offset
        self.arm_rotation = 0

        self.attack_damage = attack_damage
        self.bullet_speed = bullet_speed

        self.elapsed_time = 0
        self.wiggle_speed = 1
        self.wiggle_amount = 50
        self.wiggle_offset = 0

        self.attack_chance = attack_chance

        self.set_action("idle")

    def can_interact(self):
        pass

    def set_action(self, action):
        super().set_action(action)
        self.state = action

    def update(self):
        super().update()
        self.elapsed_time += .01 * self.wiggle_speed

        if random.randint(1, self.attack_chance) == 1:
            self.set_action("attack")
            for i in range(1):
                self.gun_fire(self.game.player.get_center_pos())

        #총 각도 계산
        x_dist = self.game.player.pos.x - self.pos.x
        y_dist = -(self.game.player.pos.y - self.pos.y)
        self.arm_rotation = math.degrees(math.atan2(y_dist, x_dist))

        tween_value = pt.easeInOutSine((self.elapsed_time % 2) / 2)
        self.wiggle_offset = math.sin(tween_value * math.pi * 2) * self.wiggle_amount

        self.animation.update()

    def render(self, surface : pg.surface.Surface, offset=(0, 0)):
        super().render(surface, (0, self.wiggle_offset))

        if self.state == "attack":
            #총 렌더
            render_arm = pg.transform.rotate(self.current_arm, self.arm_rotation)
            rect_arm = render_arm.get_rect(center = (self.pos.x + self.arm_offset[0] + offset[0], self.pos.y + self.arm_offset[1] + offset[1] - self.wiggle_offset))

            surface.blit(render_arm, rect_arm)
    
    def gun_fire(self, target_pos : tuple):
        self.game.sfxs["laser_shoot"].play()
        self.game.projectiles.append(
                BossBullet(self.game, self.get_center_pos(), pg.math.Vector2(target_pos[0] - self.get_center_pos().x, target_pos[1] - self.get_center_pos().y), self.bullet_speed, self.game.assets["projectiles"]["energy_bullet"], 60, "Boss's Bullet", self, self.attack_damage)
        )
    
    def take_damage(self, damage : int):
        #대미지 입히기
        self.health -= damage

class BossSoul(KillableEnemy):
    def __init__(self, game, name, pos, size, anim_size, damage, doom_speed):
        super().__init__(game, name, pos, size, anim_size, 5, damage)

        self.elapsed_time = 0
        self.wiggle_speed = 1
        self.wiggle_amount = 100
        self.wiggle_offset = 0
        self.got_hit = False
        self.got_hit_timer = 60
        self.current_hit_timer = 0

        self.is_triggered = False
        self.attack_timer = doom_speed
        self.current_attack_timer = 0
        self.mask_color = "white"

    def update(self):
        self.elapsed_time += .01 * self.wiggle_speed
        tween_value = pt.easeInOutSine((self.elapsed_time % 2) / 2)
        self.wiggle_offset = math.sin(tween_value * math.pi * 2) * self.wiggle_amount

        if self.is_triggered:
            if self.current_attack_timer == 0:
                self.game.sfxs["world_doom_start"].play()
            if self.current_attack_timer < self.attack_timer:
                self.current_attack_timer += 1
            else:
                self.game.sfxs["world_doom"].play()
                self.attack()
        if self.got_hit:
            self.current_hit_timer += 1
        if self.current_hit_timer > self.got_hit_timer:
            self.got_hit = False
            self.current_hit_timer = 0

        super().update()

    def render(self, surface, offset=(0, 0)):
        super().render(surface, (0, self.wiggle_offset))
        if self.is_triggered:
            self.mask = pg.mask.from_surface(self.animation.img())
            self.mask_img = self.mask.to_surface(setcolor=self.mask_color, unsetcolor=(0,0,0,0))
            surface.blit(pg.transform.flip(self.mask_img, self.flipx, False), (self.pos[0] - offset[0] + self.anim_offset[0], self.pos[1] - offset[1] + self.anim_offset[1] - self.wiggle_offset))

    def check_time(self, current_time):
        if not int(current_time) == 0 and int(current_time) % 35 == 0 and not self.got_hit:
            self.is_triggered = True

    def take_damage(self, damage_amount):
        if self.is_triggered:
            self.health -= 1
            self.is_triggered = False
            self.current_attack_timer = 0
            self.got_hit = True
        
            if self.health <= 0:
                self.destroy()
                if self in self.game.entities : self.game.entities.remove(self)
                self.game.sfxs["enemy_dying"].play()
                self.game.boss_died = True
            else:
                self.game.sfxs["world_doom_cancel"].play()
                self.game.sfxs["enemy_hit"].play()
                for i in range(10):
                    self.game.sparks.append(Spark(tuple(self.get_center_pos()), math.radians(360) * random.random(), 7, "white"))
                for i in range(10):
                    self.game.sparks.append(Spark(tuple(self.get_center_pos()), math.radians(360) * random.random(), 7, "green"))
            

    def destroy(self):
        pass

    def can_interact(self):
        pass

class Ufo(FollowingEnemy):
    def __init__(self, game, name, pos, size, anim_size, following_speed, max_health, damage, target_speed):
        super().__init__(game, name, pos, size, anim_size, following_speed, max_health, damage)
        self.target_speed = target_speed
        self.current_target_speed = 0
        self.term = 60
        self.current_term_speed = 0
        self.lazer_time = 30
        self.current_lazer_time = 0
        self.attack_timer = 10
        self.current_attack_timer = 30

        self.attacked = False
        self.attacking = False

        self.lazer = pg.Rect(self.pos.x + 55, self.pos.y + 50, 40, 2000)

    def update(self):
        super().update()
        self.lazer = pg.Rect(self.pos.x + 55, self.pos.y + 50, 40, 2000)

        if self.current_target_speed < self.target_speed:
            self.current_target_speed += 1
            self.set_target(pg.math.Vector2(self.game.player.get_center_pos().x - self.size[0] / 2 - 10, 100))
        if self.current_target_speed >= self.target_speed:
            if self.current_term_speed < self.term:
                self.current_term_speed += 1
            else:
                self.attack()
        if self.attacked:
            if self.current_lazer_time < self.lazer_time:
                self.current_lazer_time += 1
            else:
                self.attacked = False
                self.attacking = False
                self.current_target_speed = 0
                self.current_term_speed = 0
                self.current_lazer_time = 0
        
        if self.attacking and self.lazer.colliderect(self.game.player.get_rect()):
            self.game.on_player_damaged(self.damage)
            self.attacking = False
            self.current_target_speed = 0
            self.current_term_speed = 0
            self.current_lazer_time = 0
            self.current_attack_timer = self.attack_timer
        
        if self.current_attack_timer > 0:
            self.current_attack_timer -= 1

    def take_damage(self, damage_amount):
        self.health -= damage_amount
        
        if self.health <= 0:
            self.game.on_player_kill(self)
            self.destroy()
            if self in self.game.entities : self.game.entities.remove(self)
        else:
            self.game.sfxs["enemy_hit"].play()
            for i in range(10):
                self.game.sparks.append(Spark(tuple(self.get_center_pos()), math.radians(360) * random.random(), 4, "black"))
            for i in range(10):
                self.game.sparks.append(Spark(tuple(self.get_center_pos()), math.radians(360) * random.random(), 4, "green"))

    def can_interact(self):
        pass

    def destroy(self):
        self.game.sfxs["ufo_explosion"].play()
        for i in range(10):
            self.game.sparks.append(Spark(tuple(self.get_center_pos()), math.radians(360) * random.random(), 7, "black"))
        for i in range(10):
            self.game.sparks.append(Spark(tuple(self.get_center_pos()), math.radians(360) * random.random(), 7, "green"))
        
    def render(self, surface, offset=(0, 0)):
        if self.attacking or self.current_attack_timer > 0:
            pg.draw.rect(surface, "green", self.lazer)
        super().render(surface, offset)
        
    
    def attack(self):
        if self.attacking == False:
            self.game.sfxs["ufo_attack"].play()
            self.game.camera_shake_gain += 10
        self.attacked = True
        self.attacking = True
