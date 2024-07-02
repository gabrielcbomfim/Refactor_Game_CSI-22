from data.entity import Entity
class RedOrb(Entity):
    def __init__(self, *args):
        super().__init__(*args)
        self.hit = False

    def render(self, *args, **kwargs):
        if not self.hit:
            super().render(*args, **kwargs)
