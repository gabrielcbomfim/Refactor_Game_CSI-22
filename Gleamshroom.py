import sys
import math
import random

import pygame
from pygame.locals import *

import data.tile_map as tile_map
import data.spritesheet_loader as spritesheet_loader
from data.anim_loader import AnimationManager
from data.foliage import AnimatedFoliage
from data.particles import Particle, load_particle_images
from game.gamedata import GameData
from game.spore import Spore
from game.firefly import Firefly
from game.loadgame import load_level
from game.spark import Spark
from game import constants
from game.loadgame import load_img
from game.loadgame import load_sounds
from game.displaytext import DisplayText
from game.loadgame import load_font_img
from game.body import Body
from game.physical_rect_filter import physical_rect_filter

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
screen = pygame.display.set_mode((constants.SCREEN_WIDTH, constants.SCREEN_HEIGHT), pygame.RESIZABLE + pygame.SCALED)
display = pygame.Surface((constants.DISPLAY_WIDTH, constants.DISPLAY_HEIGHT))

gd = GameData()

level_map = tile_map.TileMap((constants.TILE_SIZE, constants.TILE_SIZE), (constants.DISPLAY_WIDTH, constants.DISPLAY_HEIGHT))
gd.level_map = level_map

animation_manager = AnimationManager()

load_level(gd, gd.current_level,animation_manager)
load_particle_images('data/images/particles')
spritesheets, spritesheets_data = spritesheet_loader.load_spritesheets('data/images/spritesheets/')
spritesheet_keys = list(spritesheets.keys())
spritesheet_keys.sort()
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

main_font, black_font = load_font_img()

sounds = load_sounds('data/sfx')

for radius in range(1, 250):
    light_masks.append(pygame.transform.scale(light_mask_base, (radius, radius)))
for radius in range(1, 50):
    light_masks_yellow.append(pygame.transform.scale(light_mask_base_yellow, (radius, radius)))

global_time = 0

pygame.mouse.set_visible(False)

bg_bubbles = []
bg_bubble_particles = []
fg_flies = []

for i in range(30):
    fg_flies.append(Firefly(random.random() * 300, random.random() * 200, random.random() * math.pi * 2, 0, random.random() * 0.25 + 0.1, gd, display))

pygame.mixer.music.load('data/music.wav')
pygame.mixer.music.play(-1)
pygame.mixer.music.set_volume(0.35)

while True:
    global_time += 1
    if gd.finished_level != 0:
        gd.finished_level += 1
        if gd.finished_level >= 30:
            if gd.actually_finished:
                gd.current_level += 1
                load_level(gd, gd.current_level, animation_manager)
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
        bounce_shroom.update(gd, display, sounds, bounce_shroom_images)

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
        orb.update_orb(gd, glow, global_time, light_surf)

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
        spore.update(display, spore_img, gd, sounds, i, glow, light_surf)

    # flies
    for fly_obj in fg_flies:
        fly_obj.update(light_surf, glow)

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
        spark.update(gd, i, display, glow, light_surf)

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
            if gd.current_level != 8:
                if event.key in [K_UP, K_DOWN, K_LEFT, K_RIGHT]:
                    if gd.current_level == 1:
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
                                gd.sparks.append(Spark(gd.player.center, -math.pi / 2 + random.random() - 0.5, random.random() * 3 + 2, random.random() * 0.3 + 0.2))
                        if event.key == K_DOWN:
                            gd.player.velocity[1] = -2
                            gd.spores.append(Spore(gd.player.center, [0, 3], True))
                            gd.player.squish_velocity = -0.15
                            gd.player.scale[1] = 0.8
                            for i in range(6):
                                gd.sparks.append(Spark(gd.player.center, math.pi / 2 + random.random() - 0.5, random.random() * 3 + 2, random.random() * 0.3 + 0.2))
                        if event.key == K_RIGHT:
                            gd.player.velocity[0] = -2
                            gd.spores.append(Spore(gd.player.center, [3, 0], True))
                            gd.player.squish_velocity = 0.15
                            gd.player.scale[1] = 1.2
                            for i in range(6):
                                gd.sparks.append(Spark(gd.player.center, random.random() - 0.5, random.random() * 3 + 2, random.random() * 0.3 + 0.2))
                        if event.key == K_LEFT:
                            gd.player.velocity[0] = 2
                            gd.spores.append(Spore(gd.player.center, [-3, 0], True))
                            gd.player.squish_velocity = 0.15
                            gd.player.scale[1] = 1.2
                            for i in range(6):
                                gd.sparks.append(Spark(gd.player.center, math.pi + random.random() - 0.5, random.random() * 3 + 2, random.random() * 0.3 + 0.2))
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
    DisplayText(gd, global_time, display, main_font, black_font)

    # lighting
    display.blit(light_surf, (0, 0), special_flags=BLEND_RGBA_MULT)

    # ui
    if gd.current_level != 8:
        display.blit(ui_img, (5, 5))
        main_font.render(str(len([orb for orb in gd.orbs if orb.hit])) + '/' + str(len(gd.orbs)), display, (13, 4))
        main_font.render(str(gd.spores_left), display, (13, 13))

    if screen.get_height() > screen.get_width() / constants.aspect_ratio:
        screen.blit(pygame.transform.scale(display, (screen.get_width(), int(screen.get_width() / constants.aspect_ratio))), (0, 0))
    else:
        screen.blit(pygame.transform.scale(display, (int(screen.get_height() * constants.aspect_ratio), screen.get_height())), (0, 0))
    pygame.display.update()

    clock.tick(60)