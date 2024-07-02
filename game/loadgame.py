
import os

import pygame

def load_img(path):
    img = pygame.image.load(path).convert()
    img.set_colorkey((0, 0, 0))
    return img

def load_sounds(sound_path):
    sounds = {sound.split('/')[-1].split('.')[0]: pygame.mixer.Sound(os.path.join(sound_path, sound)) for sound in os.listdir(sound_path)}
    sounds['thunk'].set_volume(0.2)
    sounds['shoot'].set_volume(0.3)
    sounds['bounce'].set_volume(0.8)
    sounds['transition'].set_volume(0.5)
    sounds['explode'].set_volume(0.5)
    sounds['restart'].set_volume(0.5)
    return sounds