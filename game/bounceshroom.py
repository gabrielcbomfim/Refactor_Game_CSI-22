import math
import random
import pygame


class BounceShroom:
    def __init__(self, pos, direction):
        self.pos = pos
        self.direction = direction
        self.squeeze = 1

    def update(self, gd, display, sounds, bounce_shroom_images):
        if self.direction == 'up_bounce':
            rect = pygame.Rect(self.pos[0] + 5, self.pos[1], 34, 31)
        else:
            rect = pygame.Rect(self.pos[0], self.pos[1] + 5, 31, 34)

        if self.squeeze < 0.99:
            self.squeeze += (1 - self.squeeze) / 14
        else:
            self.squeeze = 1

        if self.direction == 'up_bounce':
            display.blit(pygame.transform.scale(bounce_shroom_images[2], (44, int(31 * self.squeeze))), (self.pos[0] - gd.scroll[0], self.pos[1] - gd.scroll[1] + 31 - int(31 * self.squeeze)))
        if self.direction == 'right_bounce':
            display.blit(pygame.transform.scale(bounce_shroom_images[0], (int(31 * self.squeeze), 44)), (self.pos[0] - gd.scroll[0], self.pos[1] - gd.scroll[1]))
        if self.direction == 'left_bounce':
            display.blit(pygame.transform.scale(bounce_shroom_images[1], (int(31 * self.squeeze), 44)), (self.pos[0] - gd.scroll[0] + 31 - int(31 * self.squeeze), self.pos[1] - gd.scroll[1]))
        if rect.colliderect(gd.player.rect):
            sounds['bounce'].play()
            if self.direction == 'up_bounce':
                gd.player.velocity[1] = -8
                gd.player.squish_velocity = -0.15
                gd.player.scale[1] = 0.7
                self.squeeze = 0.2
                for i in range(12):
                    gd.sparks.append([gd.player.center, -math.pi / 2 + random.random() - 0.5, random.random() * 4 + 2, random.random() * 0.3 + 0.15])
            if self.direction == 'right_bounce':
                gd.player.velocity[0] = 8
                gd.player.velocity[1] = min(-2, gd.player.velocity[1])
                gd.player.squish_velocity = 0.15
                gd.player.scale[1] = 1.3
                self.squeeze = 0.2
                for i in range(12):
                    gd.sparks.append([gd.player.center, random.random() - 0.5, random.random() * 4 + 2, random.random() * 0.3 + 0.15])
            if self.direction == 'left_bounce':
                gd.player.velocity[0] = -8
                gd.player.velocity[1] = min(-2, gd.player.velocity[1])
                gd.player.squish_velocity = 0.15
                gd.player.scale[1] = 1.3
                self.squeeze = 0.2
                for i in range(12):
                    gd.sparks.append([gd.player.center, math.pi + random.random() - 0.5, random.random() * 4 + 2, random.random() * 0.3 + 0.15])
