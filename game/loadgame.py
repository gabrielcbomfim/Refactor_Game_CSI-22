import os
import pygame
from game.player import Player
from game.constants import entity_types
from game.constants import spore_maximums
from game.redorb import RedOrb
from game.glowshroom import GlowShroom
from game.bounceshroom import BounceShroom

import os
from data.text import Font
def load_font_img():
    current_dir = os.path.dirname(__file__)
    parent_dir = os.path.abspath(os.path.join(current_dir, os.pardir))
    dir = os.path.join(parent_dir, 'data', 'fonts', 'small_font.png')

    main_font = Font(dir, (255, 255, 255))
    black_font = Font(dir, (0, 0, 1))
    return main_font, black_font

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

def load_level(gd, level, animation_manager):
    gd.clear_level()
    gd.level_map.load_map('data/maps/level_' + str(level) + '.json')
    gd.level_map.load_grass(gd.grass_manager)
    gd.spores_max = spore_maximums[level - 1]
    gd.reset_level()

    for entity in gd.level_map.load_entities():
        entity_type = entity_types[entity[2]['type'][1]]
        entity_pos = entity[2]['raw'][0].copy()

        if entity_type == 'spawn':
            gd.spawn = entity_pos

        if entity_type == 'orb':
            gd.orbs.append(RedOrb(animation_manager, entity_pos, (11, 11), 'orb'))

        if entity_type == 'glow_shroom':
            gd.glow_shrooms.append(GlowShroom(entity_pos))

        if entity_type in ['right_bounce', 'left_bounce', 'up_bounce']:
            gd.bounce_shrooms.append(BounceShroom(entity_pos, entity_type))

    gd.player = Player(animation_manager, (gd.spawn[0], gd.spawn[1]), (17, 17), 'player')
    gd.reset_cam()
