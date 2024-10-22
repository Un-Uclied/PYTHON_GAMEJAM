import pygame as pg
import os

BASE_IMAGE_PATH = "Assets/Sprites/"

def load_image(path):
    img = pg.image.load(BASE_IMAGE_PATH + path).convert_alpha()
    return img

def load_images(path):
    images = []
    for img_name in sorted(os.listdir(BASE_IMAGE_PATH + path)):
        images.append(load_image(path + '/' + img_name))
    return images