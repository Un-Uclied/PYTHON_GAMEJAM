import pygame as pg
import math

class Entity:
    def __init__(self, game, name : str, pos : tuple, size : tuple, anim_size : tuple):
        self.anim_offset = [0,0]
        self.game = game
        self.name = name
        self.pos = list(pos)
        self.size = size
        self.anim_size = anim_size
        self.mask_color = (0, 0, 0, 0)

        self.action = ''
        self.flipx = False
        self.set_action('idle')

    def set_action(self, action):
        if action != self.action:
            self.action = action
            self.animation = self.game.assets["entities"][self.name + '/' + self.action].copy()

    def render(self, surface, offset):
        current_frame_img = pg.transform.scale(self.animation.img(), self.anim_size)
        surface.blit(pg.transform.flip(current_frame_img, self.flipx, 0), (self.pos[0] - offset[0] + self.anim_offset[0], self.pos[1] - offset[1] + self.anim_offset[1]))
        self.mask = pg.mask.from_surface(current_frame_img)
        self.mask_img = self.mask.to_surface(setcolor=self.mask_color, unsetcolor=(0,0,0,0))
        surface.blit(pg.transform.flip(self.mask_img, self.flipx, 0), (self.pos[0] - offset[0] + self.anim_offset[0], self.pos[1] - offset[1] + self.anim_offset[1]))


class MoveableEntity(Entity):
    #생성자
    def __init__(self, game, name, pos, size, anim_size):
        super().__init__(game, name, pos, size, anim_size)

        #충돌 가능
        self.collisions = {'up' : False, 'down' : False, 
                            'right' : False, 'left' : False}

        #디버깅용 히트박스
        #self.hit_box = pg.surface.Surface((self.size[0], self.size[1]))
        #self.hit_box.fill('red')

    #히트박스
    def get_rect(self):
        return pg.rect.Rect(self.pos[0], self.pos[1], self.size[0], self.size[1])

    #update:
    def update(self, tilemap, movement = [[0, 0], [0, 0]], move_speed = 1):
        # movement [[좌, 우], [하, 상]]
        
        # movement를 벡터로 변환
        movement_vector = pg.math.Vector2((movement[0][0] - movement[0][1]), (movement[1][0] - movement[1][1]))
        
        # 벡터가 0이 아니면 노멀라이즈
        if movement_vector.length() > 0:
            movement_vector = movement_vector.normalize()
        
        movement_vector *= move_speed
        # 콜리션 초기화
        self.collisions = {'up': False, 'down': False, 'right': False, 'left': False}

        # 엔티티 이동
        self.pos[0] += movement_vector.x
        self.pos[1] += movement_vector.y
        entity_rect = self.get_rect()

        # 상하 충돌 체크
        for collided_rect in tilemap.physics_rects_around(self.pos):
            if entity_rect.colliderect(collided_rect):
                #ex) 아래로 가고 있음 & 충돌함 => 자신의 아래 = 벽의 위
                if movement_vector.y < 0:
                    entity_rect.bottom = collided_rect.top
                    self.collisions['down'] = True
                elif movement_vector.y > 0:
                    entity_rect.top = collided_rect.bottom
                    self.collisions['up'] = True
                self.pos[1] = entity_rect.y

        # 좌우 충돌 체크
        for collided_rect in tilemap.physics_rects_around(self.pos):
            if entity_rect.colliderect(collided_rect):
                if movement_vector.x > 0:
                    entity_rect.right = collided_rect.left
                    self.collisions['right'] = True
                elif movement_vector.x < 0:
                    entity_rect.left = collided_rect.right
                    self.collisions['left'] = True
                self.pos[0] = entity_rect.x

        # 캐릭터가 오른쪽을 보고 있는지 확인
        if movement_vector.x > 0:
            self.flipx = False
        elif movement_vector.x < 0:
            self.flipx = True