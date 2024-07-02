
import math
import random

class Firefly:
    def __init__(self, x, y, theta, w, v, gd, display):
        self.x = x
        self.y = y
        self.theta = theta
        self.w = w
        self.v = v
        self.gd = gd
        self.display = display

    def update(self, light_surf):
        self.x += math.cos(self.theta) * self.v
        self.y += math.sin(self.theta) * self.v
        self.theta += self.w
        if random.random() < 0.01:
            self.w = random.random() * 0.2 - 0.1
        render_pos = (int(self.x - self.gd.scroll[0]) % 300, int(self.y - self.gd.scroll[1]) % 200)
        self.display.set_at(render_pos, (254, 231, 97))
        glow(light_surf, self, render_pos, 10, yellow=True)
        if random.random() > 0.025:
            glow(light_surf, self, render_pos, 30, yellow=True)
