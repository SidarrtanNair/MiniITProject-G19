import pygame
from opensimplex import *
import random, time
#=========================CLASS=====================================#
class generateworld:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((800, 600))
        pygame.display.set_caption("World Gen Test")
        self.clock = pygame.time.Clock()


        self.blocklibrary = {
            'dirt': pygame.Surface((32, 32)),
            'grass': pygame.Surface((32, 32)),
            'stone': pygame.Surface((32, 32))

        }
        self.blocklibrary['dirt'].fill((139, 69, 19))
        self.blocklibrary['grass'].fill((0, 200, 0)) #to be replaced with textures
        self.blocklibrary['stone'].fill((100, 100, 100))

        self.block_width = self.blocklibrary['dirt'].get_width()
        self.block_height = self.blocklibrary['dirt'].get_height()

        self.blocks = []
        self.seed = None
        self.set_seed()
        self.gen_world()

    def set_seed(self):
            self.seed = random.randint(0, 10**9)
            print(self.seed)

    def gen_world(self):
        self.blocks.clear()
        noise = OpenSimplex(seed=self.seed)

        screen_width, screen_height = self.screen.get_size()
        cols = screen_width // self.block_width
        rows = screen_height // self.block_height

        for x in range(cols):
            noise_value = noise.noise2(x * 0.1, 0)
            base = rows // 4
            height = int((noise_value + 1) * 5 + base)
            height = max(1, min(rows, height))

            for y in range(height):
                y_px = screen_height - (y + 1) * self.block_height

                if y == height - 1:
                    texture = self.blocklibrary['grass']
                elif y < height - 5:
                    texture = self.blocklibrary['stone']
                else:
                    texture = self.blocklibrary['dirt']

                rectangle = texture.get_rect(topleft=(x * self.block_width, y_px))
                self.blocks.append((texture, rectangle))
    def newseed(self):
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    self.seed = random.randint(0, 10**9)
                    print( self.seed)
                    self.gen_world()

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
            self.screen.fill((135, 206, 235))
            for texture, rect in self.blocks:
                self.screen.blit(texture, rect)
            pygame.display.flip()
            self.clock.tick(60)
            self.newseed()
        pygame.quit()

if __name__ == "__main__":
    generateworld().run()
