# THIS CODE WAS WRITTEN IN UNDER 48 HOURS FOR A GAME JAM
# there is a ton of spaghetti...
# read at your own risk

import os
import sys
import math
import random

import pygame
from pygame.locals import *

import data.tile_map as tile_map
import data.spritesheet_loader as spritesheet_loader
from data.anim_loader import AnimationManager
from data.entity import Entity
from data.foliage import AnimatedFoliage
from data.text import Font
from data.particles import Particle, load_particle_images
from player import Player
from gamedata import GameData

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
class Firefly:
    def __init__(self, x, y, theta, w, v):
        self.x = x
        self.y = y
        self.theta = theta
        self.w = w
        self.v = v

    def update(self, light_surf):
        self.x += math.cos(self.theta) * self.v
        self.y += math.sin(self.theta) * self.v
        self.theta += self.w
        if random.random() < 0.01:
            self.w = random.random() * 0.2 - 0.1
        render_pos = (int(self.x - gd.scroll[0]) % 300, int(self.y - gd.scroll[1]) % 200)
        display.set_at(render_pos, (254, 231, 97))
        glow(light_surf, self, render_pos, 10, yellow=True)
        if random.random() > 0.025:
            glow(light_surf, self, render_pos, 30, yellow=True)


class Spore:
    def __init__(self, pos, velocity, moving):
        self.pos = pos
        self.velocity = velocity
        self.moving = moving



class GlowShroom:
    def __init__(self, data):
        self.data = data

class RedOrb(Entity):
    def __init__(self, *args):
        super().__init__(*args)
        self.hit = False

    def render(self, *args, **kwargs):
        if not self.hit:
            super().render(*args, **kwargs)

class Body(Entity):
    def __init__(self, *args):
        super().__init__(*args)
        self.velocity = [0, 0]
        self.planted = False

    def update(self, rects):
        if not self.planted:
            self.velocity[1] = min(3, self.velocity[1] + 0.1)
            collisions = self.move(self.velocity, rects)
            if collisions['bottom']:
                self.planted = True

def physical_rect_filter(tiles):
    valid = []
    for tile in tiles:
        for tile_type in tile[0]:
            if tile_type[0] in ['grass_tileset', 'dirt_tileset']:
                valid.append(tile[1])
                break
    return valid

def glow(surf, host, pos, radius, yellow=False):
    if host:
        timing_offset = (hash(host) / 1000) % 1
    else:
        timing_offset = 0
    glow_width = int(math.sin(global_time / 30 + timing_offset * math.pi * 2) * radius * 0.15 + radius * 0.85)
    if not yellow:
        glow_img = light_masks[glow_width - 1]
    else:
        glow_img = light_masks_yellow[glow_width - 1]
    surf.blit(glow_img, (pos[0] - glow_width // 2, pos[1] - glow_width // 2), special_flags=BLEND_RGBA_ADD)

clock = pygame.time.Clock()

pygame.init()
pygame.display.set_caption('Gleamshroom')

screen = pygame.display.set_mode((900, 600), pygame.RESIZABLE + pygame.SCALED)

aspect_ratio = 3 / 2

display = pygame.Surface((300, 200))

gd = GameData()

tile_size = 18
level_map = tile_map.TileMap((tile_size, tile_size), (300, 200))
gd.level_map = level_map

entity_types = ['spawn', 'orb', 'glow_shroom', 'right_bounce', 'left_bounce', 'up_bounce']
spore_maximums = [5, 3, 7, 7, 38, 10, 33, 99]
current_level = 1

animation_manager = AnimationManager()

def load_level(gd, level):
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
            gd.bounce_shrooms.append([entity_pos, entity_type, 1])

    gd.player = Player(animation_manager, (gd.spawn[0], gd.spawn[1]), (17, 17), 'player')
    gd.reset_cam()

load_level(gd, current_level)

spritesheets, spritesheets_data = spritesheet_loader.load_spritesheets('data/images/spritesheets/')
spritesheet_keys = list(spritesheets.keys())
spritesheet_keys.sort()

load_particle_images('data/images/particles')

tree_animations = [AnimatedFoliage(load_img('data/images/foliage/' + str(i) + '.png'), [[38, 92, 66], [62, 137, 72], [99, 199, 77]], motion_scale=0.5) for i in range(2)]
bounce_shroom_images = [load_img('data/images/bounce_' + str(i + 1) + '.png') for i in range(3)]

spore_img = load_img('data/images/spore.png')
ui_img = load_img('data/images/ui.png')

light_mask_base = load_img('data/images/lights/light.png')
light_mask_base_yellow = light_mask_base.copy()
light_mask_base_yellow.fill((127, 116, 48))
light_mask_base_yellow.blit(light_mask_base, (0, 0), special_flags=BLEND_RGBA_MULT)
light_mask_full = pygame.transform.scale(light_mask_base, (400, 300))
light_mask_full.blit(light_mask_full, (0, 0), special_flags=BLEND_RGBA_ADD)
light_masks = []
light_masks_yellow = []
for radius in range(1, 250):
    light_masks.append(pygame.transform.scale(light_mask_base, (radius, radius)))
for radius in range(1, 50):
    light_masks_yellow.append(pygame.transform.scale(light_mask_base_yellow, (radius, radius)))

main_font = Font('data/fonts/small_font.png', (255, 255, 255))
black_font = Font('data/fonts/small_font.png', (0, 0, 1))

sounds = load_sounds('data/sfx')

global_time = 0

pygame.mouse.set_visible(False)

bg_bubbles = []
bg_bubble_particles = []
fg_flies = []

for i in range(30):
    fg_flies.append(Firefly(random.random() * 300, random.random() * 200, random.random() * math.pi * 2, 0, random.random() * 0.25 + 0.1))

pygame.mixer.music.load('data/music.wav')
pygame.mixer.music.play(-1)
pygame.mixer.music.set_volume(0.35)

while True:
    global_time += 1
    if gd.finished_level != 0:
        gd.finished_level += 1
        if gd.finished_level >= 30:
            if gd.actually_finished:
                current_level += 1
                load_level(gd, current_level)
            else:
                gd.bodies.append(Body(animation_manager, gd.player.pos.copy(), (17, 12), 'body'))
                gd.player.pos = [gd.spawn[0], gd.spawn[1]]
                gd.player.velocity = [0, 0]
                gd.reset_level()

    display.fill((12, 10, 18))

    if random.random() < 0.1:
        if random.random() > 0.25:
            bg_bubbles.append([[random.random() * 300, 200], random.random() * 1.5 + 0.25, random.random() * 18 + 1, random.random() - 0.5])
        else:
            bg_bubbles.append([[random.random() * 300, 0], random.random() * -1.5 - 0.25, random.random() * 18 + 1, random.random() - 0.5])
    for i, bubble in sorted(enumerate(bg_bubbles), reverse=True):
        bg_bubble_particles.append([((bubble[0][0] + gd.scroll[0] * bubble[3]) % 300, bubble[0][1]), bubble[2]])
        bubble[0][1] -= bubble[1]
        if (bubble[0][1] < 0) or (bubble[0][1] > 200):
            bg_bubbles.pop(i)

    for i, p in sorted(enumerate(bg_bubble_particles), reverse=True):
        pygame.draw.circle(display, (0, 0, 0), p[0], int(p[1]))
        p[1] -= 0.3
        if p[1] <= 0:
            bg_bubble_particles.pop(i)

    light_surf = display.copy()
    light_surf.fill((5, 15, 35))

    gd.scroll[0] += (gd.player.center[0] - display.get_width() // 2 - gd.scroll[0]) / 20
    gd.scroll[1] += (gd.player.center[1] - display.get_height() // 2 - gd.scroll[1]) / 20

    rendered_entities = False

    # handle bounce shrooms
    for bounce_shroom in gd.bounce_shrooms:
        if bounce_shroom[1] == 'up_bounce':
            rect = pygame.Rect(bounce_shroom[0][0] + 5, bounce_shroom[0][1], 34, 31)
        else:
            rect = pygame.Rect(bounce_shroom[0][0], bounce_shroom[0][1] + 5, 31, 34)

        if bounce_shroom[2] < 0.99:
            bounce_shroom[2] += (1 - bounce_shroom[2]) / 14
        else:
            bounce_shroom[2] = 1

        if bounce_shroom[1] == 'up_bounce':
            display.blit(pygame.transform.scale(bounce_shroom_images[2], (44, int(31 * bounce_shroom[2]))), (bounce_shroom[0][0] - gd.scroll[0], bounce_shroom[0][1] - gd.scroll[1] + 31 - int(31 * bounce_shroom[2])))
        if bounce_shroom[1] == 'right_bounce':
            display.blit(pygame.transform.scale(bounce_shroom_images[0], (int(31 * bounce_shroom[2]), 44)), (bounce_shroom[0][0] - gd.scroll[0], bounce_shroom[0][1] - gd.scroll[1]))
        if bounce_shroom[1] == 'left_bounce':
            display.blit(pygame.transform.scale(bounce_shroom_images[1], (int(31 * bounce_shroom[2]), 44)), (bounce_shroom[0][0] - gd.scroll[0] + 31 - int(31 * bounce_shroom[2]), bounce_shroom[0][1] - gd.scroll[1]))
        if rect.colliderect(gd.player.rect):
            sounds['bounce'].play()
            if bounce_shroom[1] == 'up_bounce':
                gd.player.velocity[1] = -8
                gd.player.squish_velocity = -0.15
                gd.player.scale[1] = 0.7
                bounce_shroom[2] = 0.2
                for i in range(12):
                    gd.sparks.append([gd.player.center, -math.pi / 2 + random.random() - 0.5, random.random() * 4 + 2, random.random() * 0.3 + 0.15])
            if bounce_shroom[1] == 'right_bounce':
                gd.player.velocity[0] = 8
                gd.player.velocity[1] = min(-2, gd.player.velocity[1])
                gd.player.squish_velocity = 0.15
                gd.player.scale[1] = 1.3
                bounce_shroom[2] = 0.2
                for i in range(12):
                    gd.sparks.append([gd.player.center, random.random() - 0.5, random.random() * 4 + 2, random.random() * 0.3 + 0.15])
            if bounce_shroom[1] == 'left_bounce':
                gd.player.velocity[0] = -8
                gd.player.velocity[1] = min(-2, gd.player.velocity[1])
                gd.player.squish_velocity = 0.15
                gd.player.scale[1] = 1.3
                bounce_shroom[2] = 0.2
                for i in range(12):
                    gd.sparks.append([gd.player.center, math.pi + random.random() - 0.5, random.random() * 4 + 2, random.random() * 0.3 + 0.15])

    # render tiles
    render_list = gd.level_map.get_visible(gd.scroll)
    for layer in render_list:
        if not rendered_entities:
            if layer[0] >= -2:
                for orb in gd.orbs:
                    float_shift = math.sin((hash(orb) / 100) % (math.pi * 2) + global_time / 30) * 4
                    orb.render(display, offset=[gd.scroll[0], gd.scroll[1] + float_shift])

                for body in gd.bodies:
                    body.render(display, offset=gd.scroll)

                gd.player.render(display, offset=gd.scroll)

                rendered_entities = True

        layer_id = layer[0]
        for tile in layer[1]:
            if tile[1][0] == 'trees':
                seed = int(tile[0][1] * tile[0][0] + (tile[0][0] + 10000000) ** 1.2)
                tree_animations[tile[1][1]].render(display, (tile[0][0] - gd.scroll[0], tile[0][1] - gd.scroll[1]), m_clock=global_time / 100, seed=seed)
            else:
                offset = [0, 0]
                if tile[1][0] in spritesheets_data:
                    tile_id = str(tile[1][1]) + ';' + str(tile[1][2])
                    if tile_id in spritesheets_data[tile[1][0]]:
                        if 'tile_offset' in spritesheets_data[tile[1][0]][tile_id]:
                            offset = spritesheets_data[tile[1][0]][tile_id]['tile_offset']
                img = spritesheet_loader.get_img(spritesheets, tile[1])
                display.blit(img, (tile[0][0] - gd.scroll[0] + offset[0], tile[0][1] - gd.scroll[1] + offset[1]))

    # grass
    gd.grass_manager.update_render(display, 1 / 60, offset=gd.scroll.copy(), rot_function=lambda x, y: int(math.sin(x / 100 + global_time / 40) * 30) / 10)

    if not rendered_entities:
        for orb in gd.orbs:
            float_shift = math.sin((hash(orb) / 100) % (math.pi * 2) + global_time / 30) * 4
            orb.render(display, offset=[gd.scroll[0], gd.scroll[1] + float_shift])

        for body in gd.bodies:
            body.render(display, offset=gd.scroll)

        gd.player.render(display, offset=gd.scroll)

    for orb in gd.orbs:
        orb.update(1 / 60)
        if not orb.hit:
            float_shift = math.sin((hash(orb) / 100) % (math.pi * 2) + global_time / 30) * 4
            glow(light_surf, orb, (orb.center[0] - gd.scroll[0], orb.center[1] - gd.scroll[1] - float_shift), 140)
            if (global_time + int(orb.center[0])) % 240 == 0:
                gd.circle_effects.append([(orb.center[0], orb.center[1] - float_shift), 4, 8, 0.25, 1])

    gd.bodies = gd.bodies[-16:]
    for body in gd.bodies:
        body.update(physical_rect_filter(gd.level_map.get_nearby_rects(body.pos)))

    gd.player.update(physical_rect_filter(gd.level_map.get_nearby_rects(gd.player.pos)))
    gd.grass_manager.apply_force(gd.player.center, 6, 12)
    glow(light_surf, gd.player, (gd.player.center[0] - gd.scroll[0], gd.player.center[1] - gd.scroll[1]), 140)

    for glow_shroom_obj in gd.glow_shrooms:
        glow(light_surf, glow_shroom_obj, (glow_shroom_obj.data[0] - gd.scroll[0] + 11, glow_shroom_obj.data[1] - gd.scroll[1] + 15), 120)

    gd.spores = gd.spores[-100:]
    for i, spore in sorted(enumerate(gd.spores), reverse=True):
        display.blit(spore_img, (spore.pos[0] - gd.scroll[0] - 2, spore.pos[1] - gd.scroll[1] - 2))
        if spore.moving:
            spore.pos[0] += spore.velocity[0]
            spore.pos[1] += spore.velocity[1]

            # Se colidir, toca um som de batida, o esporo para de se mover e solta faiscas
            if gd.level_map.tile_collide(spore.pos):
                sounds['thunk'].play()
                spore.moving = False
                for i in range(6):
                    angle = math.atan2(spore.velocity[1], spore.velocity[0])
                    gd.sparks.append([spore.pos.copy(), angle + random.random() - 0.5, random.random() * 3 + 2, random.random() * 0.3 + 0.2])

            gd.particles.append(Particle(spore.pos[0], spore.pos[1], 'p', [0, 0], 10, 1.9, custom_color=(255, 255, 255)))

            for orb in gd.orbs:
                if not orb.hit:
                    orb_r = pygame.Rect(orb.pos[0] - 2, orb.pos[1] - 2, 15, 15)
                    if orb_r.collidepoint(spore.pos):
                        sounds['explode'].play()
                        sounds['point'].play()

                        if current_level == 2:
                            gd.tutorial_text = False

                        gd.spores.pop(i)
                        orb.hit = True
                        gd.circle_effects.append([orb.center, 4, 4, 0.15, 2])
                        gd.circle_effects.append([orb.center, 4, 6, 0.15, 0.5])
                        for i in range(20):
                            angle = random.random() * math.pi * 2
                            speed = random.random() * 60 + 30
                            gd.particles.append(Particle(orb.center[0], orb.center[1], 'p2', [math.cos(angle) * speed, math.sin(angle) * speed], random.random() * 5 + 3, 0, custom_color=(228, 59, 68)))
                        if len([orb for orb in gd.orbs if not orb.hit]) == 0:
                            gd.finished_level = 1
                            gd.actually_finished = True
                            sounds['transition'].play()

        glow(light_surf, spore, (spore.pos[0] - gd.scroll[0], spore.pos[1] - gd.scroll[1]), 70)

    # flies
    for fly_obj in fg_flies:
        fly_obj.update(light_surf)

    # particles
    for i, particle in sorted(enumerate(gd.particles), reverse=True):
        alive = particle.update(1 / 60)
        particle.draw(display, gd.scroll)
        if particle.type == 'p2':
            glow(light_surf, None, (particle.x - gd.scroll[0], particle.y - gd.scroll[1]), 30)
        if not alive:
            gd.particles.pop(i)

    # circle effects
    for i, effect in sorted(enumerate(gd.circle_effects), reverse=True):
        # pos, radius, width, decay, speed
        pygame.draw.circle(display, (255, 255, 255), [effect[0][0] - gd.scroll[0], effect[0][1] - gd.scroll[1]], int(effect[1]), max(1, int(effect[2])))
        glow(light_surf, None, (effect[0][0] - gd.scroll[0], effect[0][1] - gd.scroll[1]), min(249, int(100 * effect[2])))
        effect[1] += effect[4]
        effect[2] -= effect[3]
        if effect[2] <= 0:
            gd.circle_effects.pop(i)

    # sparks
    for i, spark in sorted(enumerate(gd.sparks), reverse=True):
        # pos, angle, speed, decay
        center = spark[0].copy()
        center[0] -= gd.scroll[0]
        center[1] -= gd.scroll[1]
        points = [
            (center[0] + math.cos(spark[1]) * (spark[2] + 5), center[1] + math.sin(spark[1]) * (spark[2] + 5)),
            (center[0] + math.cos(spark[1] + math.pi / 2) * spark[2] * 0.6, center[1] + math.sin(spark[1] + math.pi / 2) * spark[2] * 0.6),
            (center[0] + math.cos(spark[1] + math.pi) * (spark[2] + 5), center[1] + math.sin(spark[1] + math.pi) * (spark[2] + 5)),
            (center[0] + math.cos(spark[1] - math.pi / 2) * spark[2] * 0.6, center[1] + math.sin(spark[1] - math.pi / 2) * spark[2] * 0.6),
        ]
        pygame.draw.polygon(display, (255, 255, 255), points)
        glow(light_surf, None, center, min(249, int(30 * spark[2])))

        spark[0][0] += math.cos(spark[1]) * spark[2]
        spark[0][1] += math.sin(spark[1]) * spark[2]
        spark[2] -= spark[3]
        if spark[2] <= 0:
            gd.sparks.pop(i)

    # events
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        if event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                pygame.quit()
                sys.exit()
            if event.key == K_f:
                print(clock.get_fps())
            if current_level != 8:
                if event.key in [K_UP, K_DOWN, K_LEFT, K_RIGHT]:
                    if current_level == 1:
                        gd.tutorial_text = False
                    if gd.spores_left > 0:
                        gd.spores_left -= 1
                        sounds['shoot'].play()
                        if event.key == K_UP:
                            gd.player.velocity[1] = 3
                            gd.spores.append(Spore(gd.player.center, [0, -3], True))
                            gd.player.squish_velocity = -0.15
                            gd.player.scale[1] = 0.8
                            for i in range(6):
                                gd.sparks.append([gd.player.center, -math.pi / 2 + random.random() - 0.5, random.random() * 3 + 2, random.random() * 0.3 + 0.2])
                        if event.key == K_DOWN:
                            gd.player.velocity[1] = -2
                            gd.spores.append(Spore(gd.player.center, [0, 3], True))
                            gd.player.squish_velocity = -0.15
                            gd.player.scale[1] = 0.8
                            for i in range(6):
                                gd.sparks.append([gd.player.center, math.pi / 2 + random.random() - 0.5, random.random() * 3 + 2, random.random() * 0.3 + 0.2])
                        if event.key == K_RIGHT:
                            gd.player.velocity[0] = -2
                            gd.spores.append(Spore(gd.player.center, [3, 0], True))
                            gd.player.squish_velocity = 0.15
                            gd.player.scale[1] = 1.2
                            for i in range(6):
                                gd.sparks.append([gd.player.center, random.random() - 0.5, random.random() * 3 + 2, random.random() * 0.3 + 0.2])
                        if event.key == K_LEFT:
                            gd.player.velocity[0] = 2
                            gd.spores.append(Spore(gd.player.center, [-3, 0], True))
                            gd.player.squish_velocity = 0.15
                            gd.player.scale[1] = 1.2
                            for i in range(6):
                                gd.sparks.append([gd.player.center, math.pi + random.random() - 0.5, random.random() * 3 + 2, random.random() * 0.3 + 0.2])
                if event.key == K_r:
                    gd.finished_level = 1
                    sounds['restart'].play()
                    for i, spore in sorted(enumerate(gd.spores), reverse=True):
                        if spore.moving:
                            gd.spores.pop(i)

    light_surf.blit(light_mask_full, (-50, -50), special_flags=BLEND_RGBA_MULT)

    if gd.finished_level:
        dark_surf = pygame.Surface(light_surf.get_size())
        dark_surf.fill([255 - abs(gd.finished_level) / 30 * 255] * 3)
        light_surf.blit(dark_surf, (0, 0), special_flags=BLEND_RGBA_MULT)

    # tutorial text
    offset_y = 1 if global_time % 90 > 80 else 0
    if gd.tutorial_text:
        if current_level == 1:
            black_font.render('shoot spores with arrow keys', display, (gd.player.center[0] - gd.scroll[0] - main_font.width('shoot spores with arrow keys') // 2 + 1, gd.player.pos[1] - 11 - gd.scroll[1] + offset_y))
            main_font.render('shoot spores with arrow keys', display, (gd.player.center[0] - gd.scroll[0] - main_font.width('shoot spores with arrow keys') // 2, gd.player.pos[1] - 12 - gd.scroll[1] + offset_y))
        if (current_level == 2) and (gd.spores_left > 0):
            black_font.render('destroy red orbs', display, (gd.player.center[0] - gd.scroll[0] - main_font.width('destroy red orbs') // 2 + 1, gd.player.pos[1] - 11 - gd.scroll[1] + offset_y))
            main_font.render('destroy red orbs', display, (gd.player.center[0] - gd.scroll[0] - main_font.width('destroy red orbs') // 2, gd.player.pos[1] - 12 - gd.scroll[1] + offset_y))

    if gd.spores_left <= 0:
        black_font.render('out of spores! press "r"', display, (gd.player.center[0] - gd.scroll[0] - main_font.width('out of spores! press "r"') // 2 + 1, gd.player.pos[1] - 11 - gd.scroll[1] + offset_y))
        main_font.render('out of spores! press "r"', display, (gd.player.center[0] - gd.scroll[0] - main_font.width('out of spores! press "r"') // 2, gd.player.pos[1] - 12 - gd.scroll[1] + offset_y))

    if current_level == 8:
        black_font.render('thanks for playing!', display, (gd.player.center[0] - gd.scroll[0] - main_font.width('thanks for playing!') // 2 + 1, gd.player.pos[1] - 11 - gd.scroll[1] + offset_y))
        main_font.render('thanks for playing!', display, (gd.player.center[0] - gd.scroll[0] - main_font.width('thanks for playing!') // 2, gd.player.pos[1] - 12 - gd.scroll[1] + offset_y))

    # lighting
    display.blit(light_surf, (0, 0), special_flags=BLEND_RGBA_MULT)

    # ui
    if current_level != 8:
        display.blit(ui_img, (5, 5))
        main_font.render(str(len([orb for orb in gd.orbs if orb.hit])) + '/' + str(len(gd.orbs)), display, (13, 4))
        main_font.render(str(gd.spores_left), display, (13, 13))

    if screen.get_height() > screen.get_width() / aspect_ratio:
        screen.blit(pygame.transform.scale(display, (screen.get_width(), int(screen.get_width() / aspect_ratio))), (0, 0))
    else:
        screen.blit(pygame.transform.scale(display, (int(screen.get_height() * aspect_ratio), screen.get_height())), (0, 0))
    pygame.display.update()
    clock.tick(60)
