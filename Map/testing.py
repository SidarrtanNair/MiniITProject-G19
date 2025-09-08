import pygame
from opensimplex import *
import random, time
import sys
import os

# Add the player module path
sys.path.append('PSD/PSD1/MAINMOVEMENT')
try:
    from PlayerV2 import Player, load_animations, gender_selection_screen
    from PlayerV2 import IDLE, WALK, JUMP, SCALE
except ImportError:
    print("Could not import PlayerV2. Make sure the path is correct.")
    sys.exit()

# Enhanced Player class that works with your blocks
class EnhancedPlayer(Player):
    def __init__(self, animation_list, blocks, block_width, block_height):
        super().__init__(animation_list)
        self.blocks = blocks
        self.block_width = block_width
        self.block_height = block_height
        
    def check_collision(self, dx, dy):
        """Check collision with blocks - ignores bush blocks for natural movement"""
        temp_rect = self.rect.copy()
        temp_rect.x += dx
        temp_rect.y += dy
        
        for block in self.blocks:
            # Skip collision check for bush blocks - they're decorative only
            if block["type"] == "bush":
                continue
                
            if temp_rect.colliderect(block["rect"]):
                return True
        return False
    
    def update(self):
        # Animation update (same as original)
        current_time = pygame.time.get_ticks()
        if current_time - self.last_update >= self.animation_cooldown:
            self.frame += 1
            self.last_update = current_time
            if self.frame >= len(self.animation_list[self.action]):
                self.frame = 0

        # Set current image animation frame and scale
        self.image = self.animation_list[self.action][self.frame]
        self.image = pygame.transform.scale(self.image, (self.image.get_width()*SCALE, self.image.get_height()*SCALE))
        if self.flip:
            self.image = pygame.transform.flip(self.image, True, False)

        # Apply gravity
        self.vel_y += self.gravity
        
        # Check vertical collision
        if not self.check_collision(0, self.vel_y):
            self.rect.y += self.vel_y
        else:
            if self.vel_y > 0:  # Falling down
                self.vel_y = 0
                self.in_air = False
            elif self.vel_y < 0:  # Jumping up
                self.vel_y = 0

        # Check horizontal collision
        if not self.check_collision(self.vel_x, 0):
            self.rect.x += self.vel_x

        # Screen barriers
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > pygame.display.get_surface().get_width():
            self.rect.right = pygame.display.get_surface().get_width()

#=========================CLASS=====================================#
class generateworld:
    def __init__(self):

        pygame.init()
        size = pygame.display.Info()
        self.screen = pygame.display.set_mode((size.current_w, size.current_h), pygame.NOFRAME)

        pygame.display.set_caption("World Gen Test")
        self.clock = pygame.time.Clock()
        self.background = pygame.image.load("Map\BACKGROUND\hCUwLQ.png").convert()
        self.background = pygame.transform.scale(self.background, self.screen.get_size())

        self.blocklibrary = {
            'dirt': pygame.transform.scale(
                pygame.image.load("Map\BLOCK\dirt_block_resize.png").convert(), (32, 32)),
            
            'grass': pygame.transform.scale(
                pygame.image.load("Map\BLOCK\grassdirt_block_resize.png").convert(), (32, 32)),

            'dirtstone': pygame.transform.scale(
                pygame.image.load("Map\BLOCK\dirtstone_block_gradient_1_resize.png").convert(),(32,32)),

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

        # Initialize player after world generation
        self.init_player()

    def init_player(self):
        """Initialize the player"""
        try:
            gender = gender_selection_screen()
            
            if gender == 'male':
                sprite_sheet_image = pygame.image.load('PSD/PSD1/MAINMOVEMENT/male_spriteV8_flipped.png').convert_alpha()
            else:
                sprite_sheet_image = pygame.image.load('PSD/PSD1/MAINMOVEMENT/female_spriteV1_flipped.png').convert_alpha()

            animation_list = load_animations(sprite_sheet_image)
            self.player = EnhancedPlayer(animation_list, self.blocks, self.block_width, self.block_height)
            
            # Find a good spawn position on top of the world
            screen_height = self.screen.get_height()
            spawn_x = self.screen.get_width() // 4  # Spawn at 1/4 of screen width
            spawn_y = 0
            
            # Find the highest solid block at spawn position (ignoring bushes)
            for block in self.blocks:
                if block["type"] != "bush" and abs(block["rect"].centerx - spawn_x) < self.block_width:
                    if block["rect"].top < spawn_y or spawn_y == 0:
                        spawn_y = block["rect"].top
            
            if spawn_y == 0:
                spawn_y = screen_height - 100
            
            self.player.rect.bottomleft = (spawn_x, spawn_y)
            
        except Exception as e:
            print(f"Error loading player: {e}")
            self.player = None

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
                elif y == height - 6 :
                    blocktype = "dirtstone"
                elif y < height - 6:
                    blocktype = "stone"
                else:
                    blocktype = "dirt"

                rect = self.blocklibrary[blocktype].get_rect(topleft=(x * self.block_width, y_px))
                self.blocks.append({
                    "type": blocktype,
                    "texture": self.blocklibrary[blocktype],
                    "rect": rect
                })

    def newseed(self):
        self.seed = random.randint(0, 10**9)
        print(self.seed)
        self.gen_world()
        # Respawn player after world regeneration
        if self.player:
            self.init_player()

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

            # Player controls
            keys = pygame.key.get_pressed()
            if self.player:
                left = keys[pygame.K_LEFT] or keys[pygame.K_a]
                right = keys[pygame.K_RIGHT] or keys[pygame.K_d] 
                jump = keys[pygame.K_SPACE] or keys[pygame.K_UP] or keys[pygame.K_w]
                
                self.player.move(left, right, jump)
                self.player.update()
            
            # Draw everything
            self.screen.blit(self.background,(0,0))
            for block in self.blocks:
                self.screen.blit(block["texture"], block["rect"])
            
            # Draw player
            if self.player:
                self.player.draw(self.screen)
                
            pygame.display.flip()
            self.clock.tick(60)
        pygame.quit()


if __name__ == "__main__":
    generateworld().run()