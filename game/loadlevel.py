
from game.player import Player
from game.constants import entity_types
from game.constants import spore_maximums
from game.redorb import RedOrb
from game.glowshroom import GlowShroom
from game.bounceshroom import BounceShroom


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
