import pygame as pg
import os, json
import webbrowser

BASE_IMAGE_PATH = "Assets/Sprites/"

def load_image(path):
    img = pg.image.load(BASE_IMAGE_PATH + path)
    return img.convert_alpha()

def load_images(path):
    images = []
    for img_name in sorted(os.listdir(BASE_IMAGE_PATH + path)):
        images.append(load_image(path + '/' + img_name))
    return images

def load_data(save_file : str):
    with open(os.path.join(save_file), 'r+', encoding="utf-8") as file:
        dicts = json.load(file)
    return dicts

def set_data(file_dir: str, property_name: str, new_value):
    with open(file_dir, "r", encoding="utf-8") as f:
        data = json.load(f)

    keys = property_name.split("/")
    
    temp = data
    for key in keys[:-1]:
        temp = temp.get(key, {})
    temp[keys[-1]] = new_value

    with open(file_dir, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def open_site(url):
    webbrowser.open(url)