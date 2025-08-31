import pygame
from opensimplex import *
import random, time
#=========================CLASS=====================================#
class generateworld:
    def __init__(self):

        pygame.init()
        self.screen = pygame.display.set_mode((1920, 1080))
        pygame.display.set_caption("World Gen Test")
        self.clock = pygame.time.Clock()
        self.background = pygame.image.load("Map\BACKGROUND\hCUwLQ.png").convert()
        self.background = pygame.transform.scale(self.background, self.screen.get_size())


        
        self.blocklibrary = {
            'dirt': pygame.transform.scale(
                pygame.image.load("Map\BLOCK\dirt_block_resize.png").convert(), (32, 32)),
            
            'grass': pygame.transform.scale(
                pygame.image.load("Map\BLOCK\grassdirt_block_resize.png").convert(), (32, 32)),

            'stone': pygame.transform.scale(
                pygame.image.load("Map\BLOCK\stone_block_resize.png").convert(), (32, 32)),

            'bush':pygame.transform.scale(
                pygame.image.load("Map\BLOCK\grass_resize.png").convert_alpha(), (32, 32)),
        }
        
       
    

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
                    blocktype = "bush"
                elif y == height -2:
                    blocktype = "grass"
                elif y < height - 5:
                    blocktype = "stone"
                else:
                    blocktype = "dirt"

                rect = self.blocklibrary[blocktype].get_rect(topleft=(x * self.block_width, y_px))
                self.blocks.append({
                    "type": blocktype,
                    "texture": self.blocklibrary[blocktype],
                    "rect": rect
                })
            #if random.random() < 0.7:  (for trees later)
                   # y_px = screen_height - height * self.block_height - self.block_height
                    #rect = self.blocklibrary['bush'].get_rect(topleft=(x * self.block_width, y_px))
                    #self.blocks.append({
                        #"type": "bush",
                        #"texture": self.blocklibrary['bush'],
                        #"rect": rect
                    #})
    # regenerate with new random seed
    def newseed(self):

        self.seed = random.randint(0, 10**9)
        print(self.seed)
        self.gen_world()

    def run(self):

        running = True
        while running:
            for event in pygame.event.get():

                if event.type == pygame.QUIT:
                    running = False

                if event.type == pygame.KEYDOWN:
                
                    if event.key == pygame.K_ESCAPE:
                        running = False
                        pygame.quit()
                    if event.key == pygame.K_r:
                        self.newseed()

                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_position = pygame.mouse.get_pos()

                    if event.button == 1: 
                        for block in self.blocks:
                            if block["rect"].collidepoint(mouse_position):
                                print("Destroyed", block["type"])
                                self.blocks.remove(block)
                                
                                
                    elif event.button == 3: 
                        x, y = mouse_position
                        col = x // self.block_width
                        row = (self.screen.get_height() - y) // self.block_height  
                        y_px = self.screen.get_height() - (row + 1) * self.block_height
                        rect = self.blocklibrary['dirt'].get_rect(topleft=(col * self.block_width, y_px))
                        self.blocks.append({
                            "type": "dirt",
                            "texture": self.blocklibrary['dirt'],
                            "rect": rect
                        })

                

            
            self.screen.blit(self.background,(0,0))
            for block in self.blocks:
                self.screen.blit(block["texture"], block["rect"])
            pygame.display.flip()
            self.clock.tick(60)
        pygame.quit()

if __name__ == "__main__":
    generateworld().run()
