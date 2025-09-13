import pygame , random , time , sys , os 
from opensimplex import *

current_directory = os.path.dirname(os.path.abspath(__file__))
parent_directory = os.path.dirname(current_directory)
player_directory = os.path.join(parent_directory, 'PlayerMovement&Physics')
sys.path.append(player_directory)

from PlayerV3 import Player, load_animations, gender_selection_screen , main
from PlayerV3 import IDLE, WALK, JUMP, SCALE


class Playeronworld(Player): #1
    def __init__(self, animation_list, blocks, block_width, block_height, world_width):
        super().__init__(animation_list)
        self.blocks = blocks
        self.block_width = block_width
        self.block_height = block_height
        self.world_width = world_width
        self.health = 100
        
    def check_collision(self, dx, dy):
        temp_rect = self.rect.copy()
        temp_rect.x += dx
        temp_rect.y += dy
        for block in self.blocks:
            if block["type"] in ["bush", "tree_stump", "tree_log", "tree_top"]:
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

    def draw(self, surf, camera_x):
        surf.blit(self.image, self.rect.move(camera_x, 0))
        self.draw_health_bar(surf, camera_x) 

    def draw_health_bar(self, surf, camera_x):
        bar_width = 40
        bar_height = 5
        x = self.rect.x + camera_x + (self.rect.width // 2) - (bar_width // 2)
        y = self.rect.y - 12
        pygame.draw.rect(surf, (255,0,0), (x,y,bar_width,bar_height))
        pygame.draw.rect(surf, (0,255,0), (x,y,bar_width * (self.health/100),bar_height))


class generateworld:
    def __init__(self):
        pygame.init() 
        size = pygame.display.Info()
        self.screen = pygame.display.set_mode((size.current_w, size.current_h), pygame.NOFRAME)
        self.clock = pygame.time.Clock()
        self.background = pygame.image.load("Map\\BACKGROUND\\sforest.png").convert()
        self.background = pygame.transform.scale(self.background, self.screen.get_size())
        self.blocklibrary = {
            'dirt': pygame.transform.scale(
                pygame.image.load("Map\\BLOCK\\dirt_block_resize.png").convert(), (32, 32)),
            'grass': pygame.transform.scale(
                pygame.image.load("Map\\BLOCK\\grassdirt_block_resize.png").convert(), (32, 32)),
            'dirtstone': pygame.transform.scale(
                pygame.image.load("Map\\BLOCK\\dirtstone_block_gradient_1_resize.png").convert(),(32,32)),
            'stone': pygame.transform.scale(
                pygame.image.load("Map\\BLOCK\\stone_block_resize.png").convert(), (32, 32)),
            'bush':pygame.transform.scale(
                pygame.image.load("Map\\BLOCK\\grass_resize.png").convert_alpha(), (32, 32)),
            'tree_stump': pygame.transform.scale(
                pygame.image.load("Map\\BLOCK\\tree_wood_stump.png").convert_alpha(), (32, 32)),
            'tree_log': pygame.transform.scale(
                pygame.image.load("Map\\BLOCK\\tree_wood.png").convert_alpha(), (32, 32)),
            'tree_top': pygame.transform.scale(
                pygame.image.load("Map\\BLOCK\\tree.png").convert_alpha(), (32,32)),
        }
        self.block_width = self.blocklibrary['dirt'].get_width()
        self.block_height = self.blocklibrary['dirt'].get_height()
        self.blocks = []  
        self.seed = None
        self.set_seed()
        self.num_levels = 3
        self.gen_world(num_levels=self.num_levels)
        self.init_player()
        self.current_scene = 0  
        self.highlight = False

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
            if block["type"] not in ["bush","tree_stump","tree_log","tree_top"] and abs(block["rect"].centerx - spawn_x) < self.block_width:
                if block["rect"].top < spawn_y or spawn_y == 2:
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
                surface_y = screen_height - (height * self.block_height)
                for y in range(height):
                    y_px = screen_height - (y + 1) * self.block_height
                    if y == height - 1:
                        blocktype = "bush"
                        texture = self.blocklibrary[blocktype]
                    elif y == height -2:
                        blocktype = "grass"
                        texture = self.blocklibrary[blocktype]
                    elif y == height - 6 :
                        blocktype = "dirtstone"
                        texture = self.blocklibrary[blocktype]
                    elif y < height - 6:
                        blocktype = "stone"
                        texture = self.blocklibrary[blocktype]
                    else:
                        blocktype = "dirt"
                        texture = self.blocklibrary[blocktype]
                    depth = (y_px - surface_y) // self.block_height
                    if depth > 0:
                        max_depth = 20
                        factor = max(0, 1 - ((depth / max_depth) ** 2))  # quadratic falloff → very dark at bottom
                        texture = texture.copy()
                        texture.fill((int(255*factor), int(255*factor), int(255*factor)), special_flags=pygame.BLEND_MULT)
                    rect = texture.get_rect(
                        topleft=((x + level * cols) * self.block_width, y_px))
                    self.blocks.append({
                        "type": blocktype,
                        "texture": texture,
                        "rect": rect
                    })
                    if blocktype == "grass" and random.random() < 0.15:
                        ground_y = rect.y
                        stump_rect = self.blocklibrary['tree_stump'].get_rect(
                            topleft=(rect.x, ground_y - self.block_height))
                        self.blocks.append({
                            "type": "tree_stump",
                            "texture": self.blocklibrary['tree_stump'],
                            "rect": stump_rect
                        })
                        tree_height = random.randint(1, 3)
                        for i in range(tree_height):
                            log_rect = self.blocklibrary['tree_log'].get_rect(
                                topleft=(rect.x, ground_y - (i + 2) * self.block_height))
                            self.blocks.append({
                                "type": "tree_log",
                                "texture": self.blocklibrary['tree_log'],
                                "rect": log_rect
                            })
                        top_rect = self.blocklibrary['tree_top'].get_rect(
                            topleft=(rect.x, ground_y - (tree_height + 2) * self.block_height))
                        self.blocks.append({
                            "type": "tree_top",
                            "texture": self.blocklibrary['tree_top'],
                            "rect": top_rect
                        })

    def newseed(self):
        self.seed = random.randint(0, 10**9)
        self.gen_world(num_levels=self.num_levels)
        if self.player:
            self.init_player()

    def run(self):
        running = True
        radius = 5 * self.block_width 
        health_display_time = 3000  
        last_health_change = 0  
        camera_x = 0  
        screen_width = self.screen.get_width()
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
                    if event.key == pygame.K_RIGHT:
                        self.current_scene = min(self.num_levels-1, self.current_scene+1)
                    if event.key == pygame.K_LEFT:
                        self.current_scene = max(0, self.current_scene-1)
                    if event.key == pygame.K_c:
                        self.highlight = not self.highlight
                    if self.player:
                        if event.key == pygame.K_h:
                            self.player.health = min(100, self.player.health+10)
                            last_health_change = current_time
                        if event.key == pygame.K_j:
                            self.player.health = max(0, self.player.health-10)
                            last_health_change = current_time
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_position = pygame.mouse.get_pos()
                    if self.player:
                        player_center = self.player.rect.center
                        distance = ((mouse_position[0] - player_center[0])**2 + (mouse_position[1] - player_center[1]) **2) **0.5
                        if distance <= radius:  
                            if event.button == 1:  
                                for block in self.blocks:
                                    if block["rect"].collidepoint(mouse_position):
                                        self.blocks.remove(block)
                                        break  
                            elif event.button == 3:  
                                x, y = mouse_position
                                col = (x - camera_x) // self.block_width
                                row = (self.screen.get_height() - y) // self.block_height  
                                y_px = self.screen.get_height() - (row + 1) * self.block_height
                                new_block_rect = self.blocklibrary['dirt'].get_rect(topleft=(col * self.block_width, y_px))
                                if not new_block_rect.colliderect(self.player.rect):
                                    self.blocks.append({
                                        "type": "dirt",
                                        "texture": self.blocklibrary['dirt'],
                                        "rect": new_block_rect
                                    })
            keys = pygame.key.get_pressed()
            if self.player:
                left = keys[pygame.K_a] 
                right = keys[pygame.K_d] 
                jump = keys[pygame.K_SPACE] 
                self.player.move(left, right, jump)
                self.player.update()
            camera_x = -(self.current_scene * screen_width)
            self.screen.blit(self.background,(0,0))
            for block in self.blocks:
                block_rect = block["rect"].move(camera_x, 0)
                self.screen.blit(block["texture"], block_rect)
            if self.highlight:
                mx,my = pygame.mouse.get_pos()
                gx = ((mx - camera_x)//self.block_width)*self.block_width + camera_x
                gy = (my//self.block_height)*self.block_height
                pygame.draw.rect(self.screen,(186,142,35),(gx,gy,self.block_width,self.block_height),2)
            if self.player:
                if current_time - last_health_change <= health_display_time:
                    self.player.draw_health_bar(self.screen, camera_x)
                self.player.draw(self.screen, camera_x)
            pygame.display.flip()
            self.clock.tick(60)
        pygame.quit()


if __name__ == "__main__":
    generateworld().run()
