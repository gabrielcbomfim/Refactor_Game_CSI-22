import math
import random
from data.particles import Particle

class Spore:
    def __init__(self, pos, velocity, moving):
        self.pos = pos
        self.velocity = velocity
        self.moving = moving

    def update(self, display, spore_img, gd, sounds, spore_index, glow, light_surf):
        display.blit(spore_img, (self.pos[0] - gd.scroll[0] - 2, self.pos[1] - gd.scroll[1] - 2))
        if self.moving:
            self.pos[0] += self.velocity[0]
            self.pos[1] += self.velocity[1]

            # Se colidir, toca um som de batida, o esporo para de se mover e solta faiscas
            if gd.level_map.tile_collide(self.pos):
                sounds['thunk'].play()
                self.moving = False
                for i in range(6):
                    angle = math.atan2(self.velocity[1], self.velocity[0])
                    gd.sparks.append([self.pos.copy(), angle + random.random() - 0.5, random.random() * 3 + 2,
                                      random.random() * 0.3 + 0.2])

            gd.particles.append(
                Particle(self.pos[0], self.pos[1], 'p', [0, 0], 10, 1.9, custom_color=(255, 255, 255)))

            for orb in gd.orbs:
                if not orb.hit:
                    orb.interact_with_spore(sounds, self, gd, spore_index)

        glow(light_surf, self, (self.pos[0] - gd.scroll[0], self.pos[1] - gd.scroll[1]), 70)
