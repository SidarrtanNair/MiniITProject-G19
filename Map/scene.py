import pygame , random , time , sys , os 
from opensimplex import *

current_directory = os.path.dirname(os.path.abspath(__file__))
parent_directory = os.path.dirname(current_directory)
player_directory = os.path.join(parent_directory, 'PlayerMovement&Physics')
sys.path.append(player_directory)

from PlayerV3 import Player, load_animations, gender_selection_screen , main
from PlayerV3 import IDLE, WALK, JUMP, SCALE
# =====PLAYER================================================================================================================= #
class Playeronworld(Player): #1
    def __init__(self, animation_list, blocks, block_width, block_height, world_width,):
        super().__init__(animation_list)
        self.blocks = blocks
        self.block_width = block_width
        self.block_height = block_height
        self.world_width = world_width
        self.health = 100
        
    #======DamageLogic============#   
    def get_damage(self, amt):
        try:
            self.health -= amt
        except:
            self.health = max(0, 0)
        if self.health < 0:
            self.health = 0
    #========HealthLogic===========#
    def get_health(self, amt):
        try:
            self.health += amt
        except:
            self.health = 0
        if self.health > 100:
            self.health = 100
    #======CollisionCheck=============#
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
    #=============ConstantSids========================#
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
    #=============Scenecam===============#
    def draw(self, surf, camera_x):
        surf.blit(self.image, self.rect.move(camera_x, 0))
        self.draw_health_bar(surf, camera_x) 
    #============blithealth==================#
    def draw_health_bar(self, surf, camera_x):
        bar_width = 40
        bar_height = 6
        x = self.rect.centerx + camera_x - bar_width//2
        y = self.rect.top - 15
        pygame.draw.rect(surf, (255,0,0), (x,y,bar_width,bar_height))
        pygame.draw.rect(surf, (0,255,0), (x,y,bar_width * (self.health/100),bar_height))

# =====WORLDGEN================================================================================================================= #
class generateworld:
    def __init__(self, pause_callback = None):
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
            'biggerbush':pygame.transform.scale(
                pygame.image.load("Map\BLOCK\shrub.png").convert_alpha(), (32,32)),
            'tree_stump': pygame.transform.scale(
                pygame.image.load("Map\\BLOCK\\tree_wood_stump.png").convert_alpha(), (32, 32)),
            'tree_log': pygame.transform.scale(
                pygame.image.load("Map\\BLOCK\\tree_wood.png").convert_alpha(), (32, 32)),
            'tree_top': pygame.transform.scale(
                pygame.image.load("Map\\BLOCK\\bushpreview32.png").convert_alpha(), (32,32)),
        }
       #==========checkthesize=========#
        self.block_width = self.blocklibrary['dirt'].get_width()
        self.block_height = self.blocklibrary['dirt'].get_height()
        
        self.blocks = []  
        self.seed = None
        self.set_seed()
        self.number_levels = 3
        self.gen_world(number_levels=self.number_levels)
        self.init_player()
        self.current_scene = 0  
        self.highlight = False
        
        self.pause_callback = pause_callback

        # =====InventorySetup========= #
        self.hotbar_keys = {
            pygame.K_3: 'dirt',
            pygame.K_4: 'grass',
            pygame.K_5: 'stone',
            pygame.K_6: 'tree_log',
            pygame.K_7: 'tree_top'}
        self.hotbar_slots = list(self.hotbar_keys.values())
        self.selected_index = 0
        self.selected_block = self.hotbar_slots[self.selected_index]

        self.inventory = { 
            'dirt': 10,
            'grass': 6,
            'stone': 8 ,
           'tree_log': 0,
           'tree_top':0,}
        
        self.selected_block = self.hotbar_keys[pygame.K_3]
        self.hotbar_slot_size = 40
        self.hotbar_padding = 6
        self.font = pygame.font.SysFont(None, 20)
        

    def init_player(self):
        gender = gender_selection_screen()
        if gender == 'male':
            sprite_path = os.path.join(parent_directory, 'PlayerMovement&Physics', 'Sprite_Img', 'male_spriteV8_flipped.png')
            sprite_sheet_image = pygame.image.load(sprite_path).convert_alpha()
        else:
            sprite_path = os.path.join(parent_directory, 'PlayerMovement&Physics', 'Sprite_Img', 'female_spriteV1_flipped.png')
            sprite_sheet_image = pygame.image.load(sprite_path).convert_alpha()
        animation_list = load_animations(sprite_sheet_image)
        world_width = (pygame.display.get_surface().get_width() * self.number_levels)
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

    def gen_world(self, number_levels=3):
        self.blocks.clear()
        noise = OpenSimplex(seed=self.seed)
        screen_width, screen_height = self.screen.get_size()
        cols = screen_width // self.block_width
        rows = screen_height // self.block_height
        for level in range(number_levels):
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
                        factor = max(0, 1 - ((depth / max_depth) ** 2))
                        texture = texture.copy()
                        texture.fill((int(255*factor), int(255*factor), int(255*factor)), special_flags=pygame.BLEND_MULT)
                    rect = texture.get_rect(
                        topleft=((x + level * cols) * self.block_width, y_px))
                    self.blocks.append({
                        "type": blocktype,
                        "texture": texture,
                        "rect": rect
                    })
                    if blocktype == "grass":
                        if random.random() < 0.15:
                            ground_y = rect.y
                            stump_rect = self.blocklibrary['tree_stump'].get_rect(
                                topleft=(rect.x, ground_y - self.block_height))
                            self.blocks.append({
                                "type": "tree_stump",
                                "texture": self.blocklibrary['tree_stump'],
                                "rect": stump_rect
                            })
                            self.blocks = [b for b in self.blocks if not (b["type"] == "bush" and b["rect"].colliderect(stump_rect))]
                            tree_height = random.randint(3, 6)
                            for i in range(tree_height):
                                log_rect = self.blocklibrary['tree_log'].get_rect(
                                    topleft=(rect.x, ground_y - (i + 2) * self.block_height))
                                self.blocks.append({
                                    "type": "tree_log",
                                    "texture": self.blocklibrary['tree_log'],
                                    "rect": log_rect
                                })
                            treetop_y = ground_y - (tree_height +2) * self.block_height
                            for dx in [-1 , 0 , 1]:
                                for dy in [-1,0,1]:
                                    leaf_rect = self.blocklibrary['tree_top'].get_rect(
                                        topleft = (rect.x + dx * self.block_width, treetop_y + dy * self.block_height))
                                    self.blocks.append({
                                        "type": "tree_top",
                                        "texture": self.blocklibrary['tree_top'],
                                        "rect": leaf_rect
                                    })
                            

                            

    def newseed(self):
        self.seed = random.randint(0, 10**9)
        self.gen_world(number_levels=self.number_levels)
        if self.player:
            self.init_player()

    def run(self):
        running = True
        radius = 5 * self.block_width 
        health_display_time = 3000  
        last_health_change = 0  
        screen_width = self.screen.get_width()
        while running:
            current_time = pygame.time.get_ticks()
            camera_x = -(self.current_scene * screen_width)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        frozenbg = self.screen.copy()
                        if self.pause_callback:
                            choice = self.pause_callback(self.screen,frozenbg)
                            if choice == "exit":
                                return "menu"
                        
                    if event.key == pygame.K_r:
                        self.newseed()
                    if event.key == pygame.K_c:
                        self.highlight = not self.highlight
                    if self.player:
                        if event.key == pygame.K_h:
                            self.player.health = min(100, self.player.health+10)
                            last_health_change = current_time
                        if event.key == pygame.K_j:
                            self.player.health = max(0, self.player.health-10)
                            last_health_change = current_time
                        if event.key == pygame.K_d:
                            self.player.get_health(10)
                            last_health_change = current_time
                        if event.key == pygame.K_SPACE:
                            self.player.get_damage(10)
                            last_health_change = current_time

            
                        if event.key in self.hotbar_keys:
                            self.selected_block = self.hotbar_keys[event.key]

                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_position = pygame.mouse.get_pos()
                    world_mouse = (mouse_position[0] - camera_x, mouse_position[1])
                    if self.player:
                        player_center = self.player.rect.center
                        distance = ((world_mouse[0] - player_center[0])**2 + (world_mouse[1] - player_center[1]) **2) **0.5
                        if distance <= radius:  
                            if event.button == 1:  
                                for block in self.blocks:
                                    if block["rect"].collidepoint(world_mouse):
                                    
                                        removed_block = block
                                        self.blocks.remove(block)
                                        bloktype = removed_block.get("type")
                                        if bloktype in self.inventory:
                                            try:
                                                self.inventory[bloktype] += 1
                                            except:
                                                self.inventory[bloktype] = 1
                                        break  
                            elif event.button == 3:  
                                x, y = world_mouse
                                col = int(x // self.block_width)
                                row = int((self.screen.get_height() - y) // self.block_height)  
                                y_px = self.screen.get_height() - (row + 1) * self.block_height

                                new_block_rect = self.blocklibrary['dirt'].get_rect(topleft=(col * self.block_width, y_px))
                                occupied = any(b["rect"].colliderect(new_block_rect) for b in self.blocks)
                                
                                selected_type = self.selected_block
                                selected_texture = self.blocklibrary.get(selected_type, self.blocklibrary['dirt'])
                               
                                inv_ok = True


                                if selected_type in self.inventory:
                                    if self.inventory[selected_type] <= 0:
                                        inv_ok = False
                                if not new_block_rect.colliderect(self.player.rect) and not occupied and inv_ok:
                                    self.blocks.append({
                                        "type": selected_type,
                                        "texture": selected_texture,
                                        "rect": new_block_rect
                                    })
                                    
                                    if selected_type in self.inventory:
                                        try:
                                            self.inventory[selected_type] -= 1
                                        except:
                                            self.inventory[selected_type] = 0
                        if event.button ==4:
                            self.selected_index = (self.selected_index -1) % len(self.hotbar_slots)
                            self.selected_block = self.hotbar_slots[self.selected_index]
                        elif event.button == 5 :
                            self.selected_index = (self.selected_index +1) % len(self.hotbar_slots)
                            self.selected_block = self.hotbar_slots[self.selected_index]

            keys = pygame.key.get_pressed()
            if self.player:
                left = keys[pygame.K_a] 
                right = keys[pygame.K_d] 
                jump = keys[pygame.K_SPACE] 
                self.player.move(left, right, jump)
                self.player.update()
                if self.player.rect.right > (self.current_scene + 1) * screen_width:
                    if self.current_scene < self.number_levels - 1:
                        self.current_scene += 1
                        self.player.rect.left = self.current_scene * screen_width + 1
                elif self.player.rect.left < self.current_scene * screen_width:
                    if self.current_scene > 0:
                        self.current_scene -= 1
                        self.player.rect.right = (self.current_scene + 1) * screen_width - 1

            self.screen.blit(self.background,(0,0))
            for block in self.blocks:
                block_rect = block["rect"].move(camera_x, 0)
                if block_rect.right < 0 or block_rect.left > screen_width:
                    continue
                self.screen.blit(block["texture"], block_rect)
            if self.highlight:
                mx,my = pygame.mouse.get_pos()
                gx = ((mx - camera_x)//self.block_width)*self.block_width + camera_x
                gy = (my//self.block_height)*self.block_height
                pygame.draw.rect(self.screen,(186,142,35),(gx,gy,self.block_width,self.block_height),2)
            #drawbar#
            hotbar_slots = list(self.hotbar_keys.values())
            total_slots = len(hotbar_slots)
            slot_w = self.hotbar_slot_size
            slot_h = self.hotbar_slot_size
            hotbar_w = total_slots * slot_w + (total_slots - 1) * self.hotbar_padding
            hotbar_x = (screen_width - hotbar_w) // 2
            hotbar_y = self.screen.get_height() - slot_h - 20

            for i, bloktype in enumerate(hotbar_slots):
                sx = hotbar_x + i * (slot_w + self.hotbar_padding)
                sy = hotbar_y
                rect = pygame.Rect(sx, sy, slot_w, slot_h)
                pygame.draw.rect(self.screen, (50,50,50), rect)  
                
                if bloktype == self.selected_block:
                    pygame.draw.rect(self.screen, (255,215,0), rect, 3)  
                else:
                    pygame.draw.rect(self.screen, (0,0,0), rect, 2)
                
                tex = self.blocklibrary.get(bloktype)
                if tex:
                    icon = pygame.transform.scale(tex, (slot_w - 8, slot_h - 8))
                    icon_rect = icon.get_rect(center=rect.center)
                    self.screen.blit(icon, icon_rect)
                
                count = self.inventory.get(bloktype, 0)
                count_surf = self.font.render(str(count), True, (255,255,255))
                count_rect = count_surf.get_rect(bottomright=(rect.right - 4, rect.bottom - 4))
                self.screen.blit(count_surf, count_rect)
#Heathdissapearlogic#
            if self.player:
                if current_time - last_health_change <= health_display_time:
                    self.player.draw_health_bar(self.screen, camera_x)
                self.player.draw(self.screen, camera_x)
            pygame.display.flip()
            self.clock.tick(60)
        return "pause"


if __name__ == "__main__":
    generateworld().run()
