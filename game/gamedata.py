import os
from data.grass import GrassManager


class GameData:
    def __init__(self):
        self.level_map = None
        self.spores_max = 1
        self.spores_left = 1
        self.current_level = 1
        self.clear_level()

    def reset_cam(self):
        self.scroll[0] = self.player.pos[0] - 150
        self.scroll[1] = self.player.pos[1] - 100

    def clear_level(self):
        self.orbs = []
        self.spawn = [0, 0]
        self.player = None
        self.shrooms = []
        self.scroll = [0, 0]
        self.spores = []
        self.bodies = []
        self.foliage = []
        self.circle_effects = []
        self.glow_shrooms = []
        self.bounce_shrooms = []
        self.sparks = []
        self.particles = []


        current_dir = os.path.dirname(__file__)
        parent_dir = os.path.abspath(os.path.join(current_dir, os.pardir))
        grass_dir = os.path.join(parent_dir, 'data', 'images', 'grass')
        self.grass_manager = GrassManager(grass_dir, tile_size=18)

        self.finished_level = -30
        self.actually_finished = False

    def reset_level(self):
        self.spores_left = self.spores_max
        self.display_tutorial_text = True
        for orb in self.orbs:
            orb.hit = False
        self.finished_level = -30
        if self.player:
            self.player.squish_velocity = -0.15
            self.player.scale[1] = 0.8
