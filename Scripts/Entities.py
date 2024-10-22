import pygame as pg

class Entity:
    def __init__(self, game, name, pos, size):
        self.anim_offset = [0,0]
        self.game = game
        self.name = name
        self.pos = list(pos)
        self.size = size
        self.mask_color = "black"

        self.collisions = {'up' : False, 'down' : False, 
                           'right' : False, 'left' : False}

        self.action = ''
        self.flipx = False
        self.flipy = False
        self.set_action('idle')

        self.last_movement = [0, 0]
        self.hit_box = pg.surface.Surface((self.size[0], self.size[1]))
        self.hit_box.fill('red')

    def get_rect(self):
        return pg.rect.Rect(self.pos[0], self.pos[1], self.size[0], self.size[1])

    def set_action(self, action):
        if action != self.action:
            self.action = action
            self.animation = self.game.assets[self.name + '/' + self.action].copy()

    def update(self, tilemap, movement = [0, 0]):
        #콜리션 프레임간 초기화 > 아직 충돌중이면 바뀌지 게임에선 않음
        self.collisions = {'up' : False, 'down' : False, 'right' : False, 'left' : False}

        #엔티티 이동
        frame_movement = (movement[0], movement[1])
        
        #x축 이동/접촉
        self.pos[0] += frame_movement[0]
        entity_rect = self.get_rect()
        for rect in tilemap.physics_rects_around(self.pos):
            if entity_rect.colliderect(rect):
                #x축 오른쪽으로 이동 블록
                if frame_movement[0] > 0:
                    entity_rect.right = rect.left
                    self.collisions['right'] = True
                #x축 왼쪽으로 이동 블록
                if frame_movement[0] < 0:
                   entity_rect.left = rect.right
                   self.collisions['left'] = True
                self.pos[0] = entity_rect.x
    
        #y축 이동/접촉
        self.pos[1] += frame_movement[1]
        entity_rect = self.get_rect()
        for rect in tilemap.physics_rects_around(self.pos):
            if entity_rect.colliderect(rect):
                #y축 발 - 블럭 위
                if frame_movement[1] > 0:
                    entity_rect.bottom = rect.top
                    self.collisions['down'] = True
                #y축 머리 - 블럭 바닥
                if frame_movement[1] < 0:
                   entity_rect.top = rect.bottom
                   self.collisions['up'] = True
                self.pos[1] = entity_rect.y
        
        #캐릭터 왼/오른쪽 보고있는지 > 왼쪽으로 갔"었"는가? 
        if movement[0] > 0:
            #오른쪽 보고있음
            self.flipx = False
        if movement[0] < 0:
            #왼쪽 보고있음
            self.flipx = True

        self.last_movement = movement

    def render(self, surface, offset):
        surface.blit(pg.transform.flip(self.animation.img(), self.flipx, self.flipy), (self.pos[0] - offset[0] + self.anim_offset[0], self.pos[1] - offset[1] + self.anim_offset[1]))
        self.mask = pg.mask.from_surface(self.animation.img())
        self.mask_img = self.mask.to_surface(setcolor=self.mask_color, unsetcolor=(0,0,0,0))
        surface.blit(pg.transform.flip(self.mask_img, self.flipx, self.flipy), (self.pos[0] - offset[0] + self.anim_offset[0], self.pos[1] - offset[1] + self.anim_offset[1]))