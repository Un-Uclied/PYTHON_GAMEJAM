import pygame as pg
import pytweening as pt
import os, json
import math

BASE_IMAGE_PATH = "Assets/Sprites/"

def load_image(path):
    img = pg.image.load(BASE_IMAGE_PATH + path)
    return img

def load_images(path):
    images = []
    for img_name in sorted(os.listdir(BASE_IMAGE_PATH + path)):
        images.append(load_image(path + '/' + img_name))
    return images

class Animation:
    def __init__(self, images, img_dur = 5, loop=True):
        self.images = images
        self.loop = loop
        self.img_duration = img_dur
        self.done = False
        self.frame = 0

    def copy(self):
        return Animation(self.images, self.img_duration, self.loop)
    
    def update(self):
        if self.loop:
            self.frame = (self.frame + 1) % (self.img_duration * len(self.images))
        else:
            self.frame = min(self.frame + 1, self.img_duration * len(self.images) - 1)
            if self.frame >= self.img_duration * len(self.images) - 1:
                self.done = True

    def img(self):
        return self.images[int(self.frame / self.img_duration)].convert_alpha()
    

class ImageSets:
    def __init__(self, images : list):
        self.images = images

    def img(self, index):
        return self.images[index].convert_alpha()
class UI:
    def __init__(self, img: pg.Surface, position: tuple):
        self.img = img
        self.position = list(position)  # 리스트로 변경해서 위치 값을 수정 가능하게
        self.target_position = None
        self.tween_duration = 0
        self.tween_time = 0
        self.speed = 0  # 선형 이동 속도 추가

    def tween_to(self, target_pos: tuple, duration: float, mode: str = 'lerp'):
        self.target_position = list(target_pos)
        self.tween_duration = duration
        self.tween_time = 0  # 트윈 시작 시점

        if mode == 'linear':  # linear 모드일 때 속도 계산
            distance = math.sqrt((self.target_position[0] - self.position[0]) ** 2 + 
                                 (self.target_position[1] - self.position[1]) ** 2)
            self.speed = distance / duration  # 이동할 거리를 시간으로 나눈 값이 속도

    def update(self, delta_time):
        if self.target_position:
            if self.speed > 0:  # linear 모드
                direction = [self.target_position[0] - self.position[0], 
                             self.target_position[1] - self.position[1]]
                distance = math.sqrt(direction[0]**2 + direction[1]**2)

                # 방향 단위 벡터 계산
                if distance > 0:
                    direction = [direction[0] / distance, direction[1] / distance]
                    
                    # 속도에 따른 이동
                    move_step = [direction[0] * self.speed * delta_time, 
                                 direction[1] * self.speed * delta_time]
                    self.position[0] += move_step[0]
                    self.position[1] += move_step[1]
                
                # 목표 위치에 도달했는지 확인
                if distance <= self.speed * delta_time:
                    self.position = self.target_position
                    self.target_position = None
                    self.speed = 0

            else:  # lerp 모드
                self.tween_time += delta_time  # 트윈 진행 시간 업데이트
                t = min(self.tween_time / self.tween_duration, 1)  # 0 ~ 1 사이의 비율 계산

                # 선형 보간으로 새로운 위치 계산
                self.position[0] = self.lerp(self.position[0], self.target_position[0], t)
                self.position[1] = self.lerp(self.position[1], self.target_position[1], t)

                # 트윈이 끝났을 경우
                if t >= 1:
                    self.target_position = None  # 트윈 종료 후 목표 위치 삭제

    def render(self, target_surface: pg.Surface):
        target_surface.blit(self.img, self.position)

    def lerp(self, start, end, t):
        return start + (end - start) * t

    


def get_surface_center_to(surface : pg.Surface, dest : tuple):
    return (dest[0]-surface.get_size()[0], dest[1]-surface.get_size()[1])

# {id : [Surface, original_pos, target_pos, duration, step, offset]}
class Tweener:
    def __init__(self):
        self.tweener_id = 0
        self.tweeners = {}

    def tween_to(self, surface: pg.Surface, original_pos, target_pos, duration):
        self.tweener_id += 1
        self.tweeners[self.tweener_id] = [surface, original_pos, target_pos, duration, 0, 0] 
    
    def update_all(self, delta_time):
        for i in list(self.tweeners.keys()):
            tweener = self.tweeners[i]
            surface, original_pos, target_pos, duration, step, _ = tweener

            step += delta_time / duration
            if step >= 1:
                step = 1

            current_x = self.lerp(original_pos[0], target_pos[0], step)
            current_y = self.lerp(original_pos[1], target_pos[1], step)
            new_pos = (current_x, current_y)

            tweener[5] = new_pos
            tweener[4] = step
            
            if step == 1:
                del self.tweeners[i]

            return new_pos

    def lerp(self, start, end, t):
        return start + (end - start) * t
