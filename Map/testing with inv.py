import pygame , random , time , sys , os 
from opensimplex import *

# Your existing imports remain the same
current_directory = os.path.dirname(os.path.abspath(__file__))
parent_directory = os.path.dirname(current_directory)
player_directory = os.path.join(parent_directory, 'PlayerMovement&Physics')
sys.path.append(player_directory)

from PlayerV3 import Player, load_animations, gender_selection_screen , main
from PlayerV3 import IDLE, WALK, JUMP, SCALE

# NEW INVENTORY CLASS
class Inventory:
    def __init__(self):
        # Initialize inventory with 4 block types
        self.blocks = {
            1: {'name': 'dirt', 'broken': 0, 'placed': 0},
            2: {'name': 'grass', 'broken': 0, 'placed': 0},
            3: {'name': 'dirtstone', 'broken': 0, 'placed': 0},
            4: {'name': 'stone', 'broken': 0, 'placed': 0}
        }
        self.selected_block_key = 1  # Default to dirt (key 1)
        self.font = pygame.font.Font(None, 24)
        
    def get_selected_block_type(self):
        """Returns the currently selected block type name"""
        return self.blocks[self.selected_block_key]['name']
    
    def select_block(self, key):
        """Select block type based on key press (1-4)"""
        if key in self.blocks:
            self.selected_block_key = key
    
    def add_broken(self, block_type):
        """Increment broken count for a block type"""
        for key, block in self.blocks.items():
            if block['name'] == block_type:
                block['broken'] += 1
                break
    
    def add_placed(self, block_type):
        """Increment placed count for a block type"""
        for key, block in self.blocks.items():
            if block['name'] == block_type:
                block['placed'] += 1
                break
    
    def draw(self, screen):
        """Draw the inventory in the top right corner"""
        screen_width = screen.get_width()
        start_x = screen_width - 200  # 200 pixels from right edge
        start_y = 20  # 20 pixels from top
        
        # Background for inventory
        inventory_bg = pygame.Rect(start_x - 10, start_y - 10, 190, 120)
        pygame.draw.rect(screen, (0, 0, 0, 128), inventory_bg)  # Semi-transparent black
        pygame.draw.rect(screen, (255, 255, 255), inventory_bg, 2)  # White border
        
        # Title
        title_text = self.font.render("INVENTORY", True, (255, 255, 255))
        screen.blit(title_text, (start_x, start_y))
        
        # Draw each inventory item
        y_offset = start_y + 25
        for key, block in self.blocks.items():
            # Highlight selected block
            color = (255, 255, 0) if key == self.selected_block_key else (255, 255, 255)
            
            # Format: "1. dirt - 2 : 4"
            text = f"{key}. {block['name']} - {block['broken']} : {block['placed']}"
            rendered_text = self.font.render(text, True, color)
            screen.blit(rendered_text, (start_x, y_offset))
            y_offset += 22

class Playeronworld(Player): #1
    def __init__(self, animation_list, blocks, block_width, block_height, world_width):
        super().__init__(animation_list)
        self.blocks = blocks
        self.block_width = block_width
        self.block_height = block_height
        self.world_width = world_width
        self.health = 100

    def get_damage(self, amt):
        try:
            self.health -= amt
        except:
            self.health = max(0, 0)
        if self.health < 0:
            self.health = 0

    def get_health(self, amt):
        try:
            self.health += amt
        except:
            self.health = 0
        if self.health > 100:
            self.health = 100
        
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
        if self.rect.right > self.world_width: 
            self.rect.right = self.world_width
    def draw(self, surf):
        surf.blit(self.image, self.rect)
        self.draw_health_bar(surf) 

    def draw_health_bar(self, surf):
        bar_width = 50
        bar_height = 6
        x = self.rect.x
        y = self.rect.y - 15
        pygame.draw.rect(surf, (255,0,0), (x,y,bar_width,bar_height))
        pygame.draw.rect(surf, (0,255,0), (x,y,bar_width * (self.health/100),bar_height))

#=========================CLASSforWorld=====================================#
class generateworld:
    def __init__(self):
        pygame.init() 
        # Initialize font for inventory
        pygame.font.init()
        
        size = pygame.display.Info()
        self.screen = pygame.display.set_mode((size.current_w, size.current_h), pygame.NOFRAME)
        self.clock = pygame.time.Clock()
        self.background = pygame.image.load("Map\BACKGROUND\sforest.png").convert()
        self.background = pygame.transform.scale(self.background, self.screen.get_size())
        
        # Initialize inventory system
        self.inventory = Inventory()
        
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
        self.num_levels = 3
        self.current_scene = 0
        self.gen_world(num_levels=self.num_levels)
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
        world_width = (pygame.display.get_surface().get_width() * self.num_levels)
        self.player = Playeronworld(animation_list, self.blocks, self.block_width, self.block_height, world_width)
        spawn_x = 300
        spawn_y = 300
        for block in self.blocks:
            if block["type"] != "bush" and abs(block["rect"].centerx - spawn_x) < self.block_width:
                if block["rect"].top < spawn_y or spawn_y == 0:
                    spawn_y = block["rect"].top
        self.player.rect.bottomleft = (spawn_x, spawn_y)

    def set_seed(self):
        self.seed = random.randint(0, 10**9)

    def gen_world(self, num_levels=3):
        self.blocks.clear()
        noise = OpenSimplex(seed=self.seed)
        screen_width, screen_height = self.screen.get_size()
        cols = screen_width // self.block_width
        rows = screen_height // self.block_height
        for level in range(num_levels):
            for x in range(cols):
                noise_value = noise.noise2((x + level * cols) * 0.1, 0)
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
                    rect = self.blocklibrary[blocktype].get_rect(
                        topleft=((x + level * cols) * self.block_width, y_px))
                    self.blocks.append({
                        "type": blocktype,
                        "texture": self.blocklibrary[blocktype],
                        "rect": rect
                    })

    def newseed(self):
        self.seed = random.randint(0, 10**9)
        self.gen_world(num_levels=self.num_levels)
        if self.player:
            self.init_player()

#====================================GAMELOOP=================================================#
    def run(self):
        running = True
        radius = 5 * self.block_width 
        health_display_time = 3000  
        last_health_change = 0  
        screen_width = self.screen.get_width()
        
        while running:
            current_time = pygame.time.get_ticks()
            offset_x = -self.current_scene * screen_width
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                        pygame.quit()
                    if event.key == pygame.K_r:
                        self.newseed()
                        
                    # INVENTORY KEY BINDINGS (1-4)
                    if event.key == pygame.K_1:
                        self.inventory.select_block(1)
                    elif event.key == pygame.K_2:
                        self.inventory.select_block(2)
                    elif event.key == pygame.K_3:
                        self.inventory.select_block(3)
                    elif event.key == pygame.K_4:
                        self.inventory.select_block(4)
                        
                    if self.player:
                        if event.key == pygame.K_d:
                            self.player.get_health(20)
                            last_health_change = current_time
                        if event.key == pygame.K_SPACE:
                            self.player.get_damage(20)
                            last_health_change = current_time
                            
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_position = pygame.mouse.get_pos()
                    world_mouse = (mouse_position[0] - offset_x, mouse_position[1])
                    
                    if self.player:
                        player_center = self.player.rect.center
                        distance = ((world_mouse[0] - player_center[0])**2 + (world_mouse[1] - player_center[1]) **2) **0.5
                        
                        if distance <= radius:  
                            if event.button == 3:  # RIGHT CLICK = BREAK BLOCK
                                for block in self.blocks:
                                    if block["rect"].collidepoint(world_mouse):
                                        # Add to inventory broken count
                                        self.inventory.add_broken(block["type"])
                                        self.blocks.remove(block)
                                        break  
                                        
                            elif event.button == 1:  # LEFT CLICK = PLACE BLOCK
                                x, y = world_mouse
                                col = int(x // self.block_width)
                                row = int((self.screen.get_height() - y) // self.block_height)  
                                y_px = self.screen.get_height() - (row + 1) * self.block_height
                                
                                # Get selected block type from inventory
                                selected_block_type = self.inventory.get_selected_block_type()
                                
                                new_block_rect = self.blocklibrary[selected_block_type].get_rect(
                                    topleft=(col * self.block_width, y_px))
                                
                                # Check if position is valid (no collision with player or existing blocks)
                                can_place = True
                                if new_block_rect.colliderect(self.player.rect):
                                    can_place = False
                                
                                for existing_block in self.blocks:
                                    if existing_block["rect"].colliderect(new_block_rect):
                                        can_place = False
                                        break
                                
                                if can_place:
                                    # Add to inventory placed count
                                    self.inventory.add_placed(selected_block_type)
                                    
                                    self.blocks.append({
                                        "type": selected_block_type,
                                        "texture": self.blocklibrary[selected_block_type],
                                        "rect": new_block_rect
                                    })
                                    
            keys = pygame.key.get_pressed()
            if self.player:
                left = keys[pygame.K_a] 
                right = keys[pygame.K_d] 
                jump = keys[pygame.K_SPACE] 
                self.player.move(left, right, jump)
                self.player.update()

                # scene switching when player crosses scene bounds
                if self.player.rect.right > (self.current_scene + 1) * screen_width:
                    if self.current_scene < self.num_levels - 1:
                        self.current_scene += 1
                        self.player.rect.left = self.current_scene * screen_width + 1
                elif self.player.rect.left < self.current_scene * screen_width:
                    if self.current_scene > 0:
                        self.current_scene -= 1
                        self.player.rect.right = (self.current_scene + 1) * screen_width - 1

            self.screen.blit(self.background,(0,0))

            # draw only current scene (offset everything by offset_x)
            for block in self.blocks:
                block_rect = block["rect"].move(offset_x, 0)
                if block_rect.right < 0 or block_rect.left > screen_width:
                    continue
                self.screen.blit(block["texture"], block_rect)
        
            if self.player:
                # draw healthbar only when recently changed (same style as your code)
                temp_rect = self.player.rect.move(offset_x, 0)
                if current_time - last_health_change <= health_display_time:
                    bar_width = 50
                    bar_height = 6
                    x = temp_rect.x
                    y = temp_rect.y - 15
                    pygame.draw.rect(self.screen, (255,0,0), (x,y,bar_width,bar_height))
                    pygame.draw.rect(self.screen, (0,255,0), (x,y,bar_width * (self.player.health/100),bar_height))
                # draw player (using current animation image)
                self.screen.blit(self.player.image, temp_rect)

            # DRAW INVENTORY (always visible in top right)
            self.inventory.draw(self.screen)

            pygame.display.flip()
            self.clock.tick(60)
        pygame.quit()

if __name__ == "__main__":
    generateworld().run()