import math
import pygame

class Spark:
    def __init__(self, pos, angle, speed, decay):
        self.pos = pos
        self.angle = angle
        self.speed = speed
        self.decay = decay

    def update(self, gd, sparks_index, display, glow, light_surf):
        center = self.pos.copy()
        center[0] -= gd.scroll[0]
        center[1] -= gd.scroll[1]
        points = [
            (center[0] + math.cos(self.angle) * (self.speed + 5), center[1] + math.sin(self.angle) * (self.speed + 5)),
            (center[0] + math.cos(self.angle + math.pi / 2) * self.speed * 0.6, center[1] + math.sin(self.angle + math.pi / 2) * self.speed * 0.6),
            (center[0] + math.cos(self.angle + math.pi) * (self.speed + 5), center[1] + math.sin(self.angle + math.pi) * (self.speed + 5)),
            (center[0] + math.cos(self.angle - math.pi / 2) * self.speed * 0.6, center[1] + math.sin(self.angle - math.pi / 2) * self.speed * 0.6),
        ]
        pygame.draw.polygon(display, (255, 255, 255), points)
        glow(light_surf, None, center, min(249, int(30 * self.speed)))

        self.pos[0] += math.cos(self.angle) * self.speed
        self.pos[1] += math.sin(self.angle) * self.speed
        self.speed -= self.decay
        if self.speed <= 0:
            gd.sparks.pop(sparks_index)
