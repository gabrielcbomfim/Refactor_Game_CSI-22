from data.entity import Entity
from data.particles import Particle
import math
import pygame
import random

class RedOrb(Entity):
    def __init__(self, *args):
        super().__init__(*args)
        self.hit = False

    def render(self, *args, **kwargs):
        if not self.hit:
            super().render(*args, **kwargs)

    def update_orb(self, gd, glow, global_time, light_surf):
        self.update(1 / 60)
        if not self.hit:
            float_shift = math.sin((hash(self) / 100) % (math.pi * 2) + global_time / 30) * 4
            glow(light_surf, self, (self.center[0] - gd.scroll[0], self.center[1] - gd.scroll[1] - float_shift), 140)
            if (global_time + int(self.center[0])) % 240 == 0:
                gd.circle_effects.append([(self.center[0], self.center[1] - float_shift), 4, 8, 0.25, 1])

    def interact_with_spore(self, sounds, spore, gd, spore_index):
        orb_r = pygame.Rect(self.pos[0] - 2, self.pos[1] - 2, 15, 15)
        if orb_r.collidepoint(spore.pos):
            sounds['explode'].play()
            sounds['point'].play()

            if gd.current_level == 2:
                gd.display_tutorial_text = False

            gd.spores.pop(spore_index)
            self.hit = True
            gd.circle_effects.append([self.center, 4, 4, 0.15, 2])
            gd.circle_effects.append([self.center, 4, 6, 0.15, 0.5])
            for i in range(20):
                angle = random.random() * math.pi * 2
                speed = random.random() * 60 + 30
                gd.particles.append(
                    Particle(self.center[0], self.center[1], 'p2', [math.cos(angle) * speed, math.sin(angle) * speed],
                             random.random() * 5 + 3, 0, custom_color=(228, 59, 68)))
            if len([orb for orb in gd.orbs if not orb.hit]) == 0:
                gd.finished_level = 1
                gd.actually_finished = True
                sounds['transition'].play()