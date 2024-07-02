from data.entity import Entity

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