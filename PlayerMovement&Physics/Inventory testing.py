import pygame , random , time , sys , os 
from opensimplex import *
current_directory = os.path.dirname(os.path.abspath(__file__))
parent_directory = os.path.dirname(current_directory)
player_directory = os.path.join(parent_directory, 'PlayerMovement&Physics')
sys.path.append(player_directory)

from PlayerV3 import Player, load_animations, gender_selection_screen , main
from PlayerV3 import IDLE, WALK, JUMP, SCALE

class Inventory:
    def __init__(self):
        self.blocks_broken = 0
        self.blocks_placed = 0
        self.font = pygame.font.SysFont('Arial', 24, bold=True)
        self.small_font = pygame.font.SysFont('Arial', 20)
        
    def add_broken_block(self):
        self.blocks_broken += 1
        
    def add_placed_block(self):
        self.blocks_placed += 1
        
    def draw(self, screen):
        # Background for inventory
        screen_width = screen.get_width()
        inventory_width = 250
        inventory_height = 120
        inventory_x = screen_width - inventory_width - 20
        inventory_y = 20
        
        # Semi-transparent background
        inventory_bg = pygame.Surface((inventory_width, inventory_height))
        inventory_bg.set_alpha(180)
        inventory_bg.fill((40, 40, 40))
        screen.blit(inventory_bg, (inventory_x, inventory_y))
        
        # Border
        pygame.draw.rect(screen, (100, 100, 100), 
                        (inventory_x, inventory_y, inventory_width, inventory_height), 2)
        
        # Title
        title_text = self.font.render("INVENTORY", True, (255, 255, 255))
        screen.blit(title_text, (inventory_x + 10, inventory_y + 10))
        
        # Inventory items
        broken_text = self.small_font.render(f"Blocks Broken: {self.blocks_broken}", True, (255, 100, 100))
        placed_text = self.small_font.render(f"Blocks Placed: {self.blocks_placed}", True, (100, 255, 100))
        
        screen.blit(broken_text, (inventory_x + 10, inventory_y + 45))
        screen.blit(placed_text, (inventory_x + 10, inventory_y + 70))
        
        # Controls hint
        hint_font = pygame.font.SysFont('Arial', 14)
        hint_text = hint_font.render("Left Click: Break | Right Click: Place", True, (200, 200, 200))
        screen.blit(hint_text, (inventory_x + 10, inventory_y + 95))

class Playeronworld(Player): #1
    def __init__(self, animation_list, blocks, block_width, block_height):
        super().__init__(animation_list)
        self.blocks = blocks
        self.block_width = block_width
        self.block_height = block_height
        
    def check_collision(self, dx, dy):
        temp_rect = self.rect.copy()
        temp_rect.x += dx
        temp_rect.y += dy

        for block in self.blocks:
            if block["type"] == "bush":
                continue
            if temp_rect.colliderect(block["rect"]):
                return True
        return False
    
    def update(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_update >= self.animation_cooldown:
            self.frame += 1
            self.last_update = current_time
            if self.frame >= len(self.animation_list[self.action]):
                self.frame = 0

        # Ensure frame is within bounds (safety check)
        if self.frame >= len(self.animation_list[self.action]):
            self.frame = 0

        self.image = self.animation_list[self.action][self.frame]
        self.image = pygame.transform.scale(self.image, (self.image.get_width()*SCALE, self.image.get_height()*SCALE))
        if self.flip:
            self.image = pygame.transform.flip(self.image, True, False)

        self.vel_y += self.gravity
        
        if not self.check_collision(0, self.vel_y):
            self.rect.y += self.vel_y
        else:
            if self.vel_y > 0:  
                self.vel_y = 0
                self.in_air = False
            elif self.vel_y < 0:  
                self.vel_y = 0

        if not self.check_collision(self.vel_x, 0):
            self.rect.x += self.vel_x

        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > pygame.display.get_surface().get_width():
            self.rect.right = pygame.display.get_surface().get_width()

    def draw(self, surf):
        surf.blit(self.image, self.rect)

#=========================CLASSforWorld=====================================#
class generateworld:
    def __init__(self):
        
        pygame.init() 
        size = pygame.display.Info()
        self.screen = pygame.display.set_mode((size.current_w, size.current_h), pygame.NOFRAME)
        self.clock = pygame.time.Clock()
        self.background = pygame.image.load("Map\BACKGROUND\sforest.png").convert()
        self.background = pygame.transform.scale(self.background, self.screen.get_size())
        
        # Initialize inventory system
        self.inventory = Inventory()
        
        # Initialize
        # Blocks
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
        self.init_player()

    def init_player(self):
        gender = gender_selection_screen()
        if gender == 'male':
            sprite_path = os.path.join(parent_directory, 'PlayerMovement&Physics', 'Sprite_Img', 'male_spriteV8_flipped.png')
            sprite_sheet_image = pygame.image.load(sprite_path).convert_alpha()
        else:
            sprite_path = os.path.join(parent_directory, 'PlayerMovement&Physics', 'Sprite_Img', 'female_spriteV1_flipped.png')
            sprite_sheet_image = pygame.image.load(sprite_path).convert_alpha()

        animation_list = load_animations(sprite_sheet_image)
        self.player = Playeronworld(animation_list, self.blocks, self.block_width, self.block_height)
        
        
        spawn_x = 300
        spawn_y = 300 #spawningcoords
        
        for block in self.blocks:
            if block["type"] != "bush" and abs(block["rect"].centerx - spawn_x) < self.block_width:
                if block["rect"].top < spawn_y or spawn_y == 0:
                    spawn_y = block["rect"].top

        self.player.rect.bottomleft = (spawn_x, spawn_y)

    def set_seed(self):
        self.seed = random.randint(0, 10**9)

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
        self.gen_world()
        # Reset inventory when generating new world
        self.inventory = Inventory()
        if self.player:
            self.init_player()

#====================================GAMELOOP=================================================#
    def run(self):
        running = True
        radius = 5 * self.block_width 
        health_display_time = 3000  
        last_health_change = 0  

        while running:
            current_time = pygame.time.get_ticks()
            for event in pygame.event.get():

                if event.type == pygame.QUIT:
                    running = False

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                        pygame.quit()
                    if event.key == pygame.K_r:
                        self.newseed()
                    
                    if self.player:
                        if event.key == pygame.K_d:
                            self.player.get_health(50)
                            last_health_change = current_time

                        if event.key == pygame.K_SPACE:
                            self.player.get_damage(50)
                            last_health_change = current_time

                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_position = pygame.mouse.get_pos()
                    if self.player:
                        player_center = self.player.rect.center
                        distance = ((mouse_position[0] - player_center[0])**2 + (mouse_position[1] - player_center[1]) **2) **0.5

                        if distance <= radius:  
                            if event.button == 1:  # Left click - break blocks
                                for block in self.blocks:
                                    if block["rect"].collidepoint(mouse_position):
                                        # Don't break bush blocks
                                        if block["type"] != "bush":
                                            self.blocks.remove(block)
                                            self.inventory.add_broken_block()
                                        break  
                            elif event.button == 3:  # Right click - place blocks
                                x, y = mouse_position
                                col = x // self.block_width
                                row = (self.screen.get_height() - y) // self.block_height  
                                y_px = self.screen.get_height() - (row + 1) * self.block_height
                                new_block_rect = self.blocklibrary['dirt'].get_rect(topleft=(col * self.block_width, y_px))
                                
                                # Check if the position is valid for placing
                                can_place = True
                                # Don't place if it would overlap with player
                                if new_block_rect.colliderect(self.player.rect):
                                    can_place = False
                                # Don't place if there's already a block there
                                for existing_block in self.blocks:
                                    if existing_block["rect"].colliderect(new_block_rect):
                                        can_place = False
                                        break
                                
                                if can_place:
                                    self.blocks.append({
                                        "type": "dirt",
                                        "texture": self.blocklibrary['dirt'],
                                        "rect": new_block_rect
                                    })
                                    self.inventory.add_placed_block()

            keys = pygame.key.get_pressed()
            if self.player:
                left = keys[pygame.K_a] 
                right = keys[pygame.K_d] 
                jump = keys[pygame.K_SPACE] 

                self.player.move(left, right, jump)
                self.player.update()
        
            # Draw everything
            self.screen.blit(self.background,(0,0))
            for block in self.blocks:
                self.screen.blit(block["texture"], block["rect"])
        
            if self.player: #draw
                if current_time - last_health_change <= health_display_time:
                    self.player.draw_health_bar(self.screen)
                self.player.draw(self.screen)

            # Draw inventory last so it's on top
            self.inventory.draw(self.screen)

            pygame.display.flip()
            self.clock.tick(60)
        pygame.quit()


if __name__ == "__main__":
    generateworld().run()