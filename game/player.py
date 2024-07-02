
from data.entity import Entity

class Player(Entity):
    def __init__(self, *args):
        super().__init__(*args)
        self.velocity = [0, 0]
        self.squish_velocity = 0

    def update(self, rects):
        super().update(1 / 60)
        self.velocity[1] = min(2, self.velocity[1] + 0.05)
        self.velocity[0] *= 0.97
        if abs(self.velocity[0]) < 0.25:
            self.velocity[0] = 0

        collisions = self.move(self.velocity, rects)
        if collisions['top'] or collisions['bottom']:
            self.velocity[1] = 1
        if collisions['left'] or collisions['right']:
            self.velocity[0] = 0

        self.scale[1] += self.squish_velocity
        self.scale[1] = max(0.3, min(self.scale[1], 1.7))
        self.scale[0] = 2 - self.scale[1]

        if self.scale[1] > 1:
            self.squish_velocity -= 0.04
        elif self.scale[1] < 1:
            self.squish_velocity += 0.04
        if self.squish_velocity > 0:
            self.squish_velocity -= 0.016
        if self.squish_velocity < 0:
            self.squish_velocity += 0.016

        self.render_offset = [(1 - self.scale[0]) * 17 / 2, (1 - self.scale[1]) * 17 / 2]

        if self.squish_velocity != 0:
            if (abs(self.squish_velocity) < 0.03) and (abs(self.scale[1] - 1) < 0.06):
                self.scale[1] = 1
                self.squish_velocity = 0
