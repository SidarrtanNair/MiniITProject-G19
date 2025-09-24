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
    def __init__(self, animation_list, blocks, block_width, block_height, world_width,parent):
        super().__init__(animation_list)
        self.blocks = blocks
        self.block_width = block_width
        self.block_height = block_height
        self.world_width = world_width
        self.health = 100
        self.parent = parent
        self.was_in_air = True       
        self.last_step_time = 0
    #======DamageLogic============#   
    def get_damage(self, amount):
        try:
            self.health -= amount
        except:
            self.health = max(0, 0)
        if self.health < 0:
            self.health = 0
    #========HealthLogic===========#
    def get_health(self, amount):
        try:
            self.health += amount
        except:
            self.health = 0
        if self.health > 100:
            self.health = 100
    #======CollisionCheck=============#
    def check_collision(self, dx, dy):
        temp_hitbox = self.hitbox.copy()
        temp_hitbox.x += dx
        temp_hitbox.y += dy
        for block in self.blocks:
            if block["type"] in ["bush", "tree_stump", "tree_log", "tree_top"]:
                continue
            if temp_hitbox.colliderect(block["rect"]):
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
        self.hitbox.center = self.rect.center
    
    # === sounds ===
    # footsteps (timed, not spam)
        if self.vel_x != 0 and not self.in_air:
            if current_time - self.last_step_time > 300:  # 300ms per step
                pygame.mixer.Channel(1).play(self.parent.sounds["footstep"])
                self.last_step_time = current_time

        # jump (trigger only at jump start)
        if self.vel_y < 0 and not self.jump_played:
            self.parent.sounds["jump"].play()
            self.jump_played = True
        if not self.in_air:
            self.jump_played = False
    #=============Scenecam===============#
    def draw(self, surf, camera_x):
        surf.blit(self.image, self.rect.move(camera_x, 0))
    #============blithealth==================#
    def draw_health_bar(self, surf, camera_x, alpha=255):
        bar_width = 100
        bar_height = 6
        x = self.rect.centerx + camera_x - bar_width//2
        y = self.rect.top - 15

        redback = pygame.Surface((bar_width, bar_height), pygame.SRCALPHA)
        redback.fill((255, 0, 0, alpha))
        surf.blit(redback, (x, y))

        green_width = int(bar_width * (self.health/100))
        if green_width > 0:
            greenback = pygame.Surface((green_width, bar_height), pygame.SRCALPHA)
            greenback.fill((0, 255, 0, alpha))
            surf.blit(greenback, (x, y))

# =====WORLDGEN================================================================================================================= #
class generateworld:
    def __init__(self, pause_callback = None, volume =0.5):
        pygame.init()
        self.dimension = 'overworld'

        pygame.mixer.init() 
        self.pause_callback = pause_callback

        self.overworld_spawn_x = 300
        self.overworld_spawn_y = 300
        self.hell_spawn_x = 300  
        self.hell_spawn_y = 300

        size = pygame.display.Info()
        self.screen = pygame.display.set_mode((size.current_w, size.current_h), pygame.NOFRAME)
        self.clock = pygame.time.Clock()
        self.background = pygame.image.load("Map\\BACKGROUND\\sforest.png").convert()
        self.background = pygame.transform.scale(self.background, self.screen.get_size())

        self.show_fullmap = False
        self.fullmap_scale = 0.1  # adjust for performance vs detail
        self.fullmap_surf = None

        self.blocklibrary = {
            'aetherium': pygame.transform.scale(
                pygame.image.load("Map\BLOCK\\aetherium_block.png").convert(), (32, 32)),
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
                pygame.image.load("Map\\BLOCK\\shrub.png").convert_alpha(), (32,32)),
            'tree_stump': pygame.transform.scale(
                pygame.image.load("Map\\BLOCK\\tree_wood_stump.png").convert_alpha(), (32, 32)),
            'tree_log': pygame.transform.scale(
                pygame.image.load("Map\\BLOCK\\tree_wood.png").convert_alpha(), (32, 32)),
            'tree_topleft': pygame.transform.scale(
                pygame.image.load("Map\\BLOCK\\tree_top_left.png").convert_alpha(), (32,32)),
            'tree_topright': pygame.transform.scale(
                pygame.image.load("Map\\BLOCK\\tree_top_right.png").convert_alpha(), (32,32)),
            'tree_topmiddle': pygame.transform.scale(
                pygame.image.load("Map\\BLOCK\\tree_top_middle.png").convert_alpha(), (32,32)),
            'tree_botleft': pygame.transform.scale(
                pygame.image.load("Map\\BLOCK\\tree_bottom_left.png").convert_alpha(), (32,32)),
            'tree_botright': pygame.transform.scale(
                pygame.image.load("Map\\BLOCK\\tree_bottom_right.png").convert_alpha(), (32,32)),
            'tree_botmiddle': pygame.transform.scale(
                pygame.image.load("Map\\BLOCK\\tree_bottom_middle.png").convert_alpha(), (32,32)),
            'tree_middlemiddle': pygame.transform.scale(
                pygame.image.load("Map\\BLOCK\\tree_middlemiddle.png").convert_alpha(),(32,32)),
            'tree_middleright': pygame.transform.scale(
                pygame.image.load("Map\\BLOCK\\tree_middle_right.png").convert_alpha(),(32,32)),
            'tree_middleleft': pygame.transform.scale(
                pygame.image.load("Map\\BLOCK\\tree_middle_left.png").convert_alpha(),(32,32)),
            'wood_planks': pygame.transform.scale(
                pygame.image.load("Map\BLOCK\wooden_block_resize.png").convert_alpha(), (32,32)),
            'portal_block': pygame.transform.scale(
                pygame.image.load('Map\\BLOCK\\NEXT DIMENSION\\portal_block.png').convert_alpha(),(32,32)),
            'portal_energy_block': pygame.transform.scale(
                pygame.image.load('Map\\BLOCK\\NEXT DIMENSION\\portal_energy_block.png').convert_alpha(),(32,32)),
            'magma_block' : pygame.transform.scale(
                pygame.image.load('Map\\BLOCK\\NEXT DIMENSION\\magma_block.png').convert_alpha(),(32,32)),
            'lava_block' : pygame.transform.scale(
                pygame.image.load('Map\\BLOCK\\NEXT DIMENSION\\lava_block.png').convert_alpha(),(32,32)),
            'fire_block' : pygame.transform.scale(
                pygame.image.load('Map\\BLOCK\\NEXT DIMENSION\\fire_block.png').convert_alpha(),(32,32))
                
            

        }
       #==========checkthesize=========#
        self.block_width = self.blocklibrary['dirt'].get_width()
        self.block_height = self.blocklibrary['dirt'].get_height()
        
        self.blocks = []  
        self.seed = None
        self.set_seed()
        self.number_levels = 5
        self.gen_world(number_levels=self.number_levels)
        self.init_player()
        self.current_scene = 0  
        self.highlight = False
        
        self.pause_callback = pause_callback

        # =====Inventory/Hotbar Setup========= #
        self.hotbar_slots = [None] * 9
        self.hotbar_counts = [0] * 9
        self.hotbar_slot_size = 40
        self.hotbar_padding = 6
        self.font = pygame.font.SysFont(None, 20)
       
        self.show_inventory = False
        self.inventory_cols = 9
        self.inventory_rows = 4
        self.inventory_slot_size = 48
        self.inventory_padding = 8
        self.inventory_surface = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)

        self.hotbar_slots[0] = None
        self.hotbar_slots[1] = None
        self.hotbar_counts[0] = 0
        self.hotbar_counts[1] = 0

        # inventory totals
        self.inventory = { 
            'dirt': 0,
            'grass': 0,
            'stone': 0 ,
            'tree_log': 0,
            'tree_top':0,
            'wood_planks': 0
        }
        
        self.selected_index = 2 

        # ===== Crafting System ===== #
        self.show_crafting = False
        self.recipes = {
            "wood_planks": {"tree_log": 1}
        }
        self.crafting_font = pygame.font.SysFont(None, 32)
        self.crafting_scroll = 0
        self.crafting_visible = 6
        
        #====Timerforfun===========#
        self.start_time = pygame.time.get_ticks()


        #=======Music=============#
        pygame.mixer.music.load("Map\MusicMan\worldbackground.mp3")   
        pygame.mixer.music.play(-1)
        self.volume =volume
                # ===== Sound Effects ===== #
        self.sounds = {
            "footstep": pygame.mixer.Sound("Map\\Sounds\\footstep_grass.mp3"),
            "jump": pygame.mixer.Sound("Map\\Sounds\\jump.mp3"),
            "land": pygame.mixer.Sound("Map\\Sounds\\land.mp3"),
            "block_break": pygame.mixer.Sound("Map\\Sounds\\block_break.mp3"),
            "block_place": pygame.mixer.Sound("Map\\Sounds\\block_place.mp3"),
            "leaves": pygame.mixer.Sound("Map\\Sounds\\birds.wav"),
            "craft": pygame.mixer.Sound("Map\\Sounds\\craft.mp3"),
            "inv_open": pygame.mixer.Sound("Map\\Sounds\\inventory_open.mp3"),
            "inv_close": pygame.mixer.Sound("Map\\Sounds\\inventory_close.mp3"),
            #"hurt": pygame.mixer.Sound("Map\\Sounds\\player_hurt.mp3"),
            #"heal": pygame.mixer.Sound("Map\\Sounds\\heal.mp3"),
        }
            # ===== Sound Volume Control ===== #
        
        self.sfx_volume = 0.5  
        for s in self.sounds.values():
            s.set_volume(self.sfx_volume)

    def loading_screen(self, text="Loading...", duration=1.0):
        self.screen.fill((0, 0, 0))  # black background
        font = pygame.font.SysFont("Arial", 48)
        label = font.render(text, True, (255, 100, 0))  # fiery orange
        label_rect = label.get_rect(center=(self.screen.get_width()//2, self.screen.get_height()//2))
        self.screen.blit(label, label_rect)
        pygame.display.update()
        time.sleep(duration)

    def play_music(self):
        pygame.mixer.music.load("Map\MusicMan\worldbackground.mp3")
        pygame.mixer.music.set_volume(self.volume)
        pygame.mixer.music.play(-1)

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
        self.player = Playeronworld(animation_list, self.blocks, self.block_width, self.block_height, world_width, self)
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
        self.background = pygame.image.load("Map\\BACKGROUND\\sforest.png").convert()
        self.background = pygame.transform.scale(self.background, self.screen.get_size())
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
                    elif y == height - 2:
                        blocktype = "grass"
                    elif y == height - 6:
                        blocktype = "dirtstone"
                    elif y < height - 6:
                        blocktype = "stone"
                    else:
                        blocktype = "dirt"

                    texture = self.blocklibrary[blocktype].copy()

                    # shading for depth
                    depth = (y_px - surface_y) // self.block_height
                    if depth > 0:
                        max_depth = 20
                        factor = max(0, 1 - ((depth / max_depth) ** 2))
                        texture.fill((int(255*factor), int(255*factor), int(255*factor)), special_flags=pygame.BLEND_MULT)

                    rect = texture.get_rect(topleft=((x + level * cols) * self.block_width, y_px))
                    self.blocks.append({"type": blocktype, "texture": texture, "rect": rect})

                    # randomly add trees
                    if blocktype == "grass" and random.random() < 0.15:
                        ground_y = rect.y
                        # stump
                        stump_rect = self.blocklibrary['tree_stump'].get_rect(topleft=(rect.x, ground_y - self.block_height))
                        self.blocks.append({"type": "tree_stump", "texture": self.blocklibrary['tree_stump'], "rect": stump_rect})

                        # remove bush underneath
                        self.blocks = [b for b in self.blocks if not (b["type"] == "bush" and b["rect"].colliderect(stump_rect))]

                        # tree logs
                        tree_height = random.randint(3, 6)
                        for i in range(tree_height):
                            log_rect = self.blocklibrary['tree_log'].get_rect(topleft=(rect.x, ground_y - (i + 2) * self.block_height))
                            self.blocks.append({"type": "tree_log", "texture": self.blocklibrary['tree_log'], "rect": log_rect})

                        # treetop
                        treetop_y = ground_y - (tree_height + 4) * self.block_height
                        treetop_textures = [
                            ['tree_topleft','tree_topmiddle','tree_topright'],
                            ['tree_middleleft','tree_middlemiddle','tree_middleright'],
                            ['tree_botleft','tree_botmiddle','tree_botright']
                        ]
                        for dy, row in enumerate(treetop_textures):
                            for dx, tex_name in enumerate(row):
                                leaf_rect = self.blocklibrary[tex_name].get_rect(
                                    topleft=(rect.x + (dx - 1) * self.block_width, treetop_y + dy * self.block_height))
                                self.blocks.append({"type": "tree_top", "texture": self.blocklibrary[tex_name], "rect": leaf_rect})

        # ===== Build fullmap once after generating all blocks =====
        # Each block = 1 pixel on minimap
        world_width_blocks = max(block["rect"].right for block in self.blocks) // self.block_width
        world_height_blocks = max(block["rect"].bottom for block in self.blocks) // self.block_height
        self.fullmap_surf = pygame.Surface((world_width_blocks, world_height_blocks))

        for block in self.blocks:
            color = (100, 100, 100)
            if block["type"] == "grass":
                color = (0, 200, 0)
            elif block["type"] == "dirt":
                color = (139, 69, 19)
            elif block["type"] == "stone":
                color = (150, 150, 150)
            elif block["type"] in ["tree_log", "tree_stump"]:
                color = (139, 100, 50)
            elif block["type"] == "tree_top":
                color = (0, 150, 0)
            mx = block["rect"].x // self.block_width
            my = block["rect"].y // self.block_height
            if 0 <= mx < self.fullmap_surf.get_width() and 0 <= my < self.fullmap_surf.get_height():
                self.fullmap_surf.set_at((mx, my), color)

            # make sure we stay in bounds

        # find the rightmost bush block
        portal_x = None
        portal_y = None
        for block in self.blocks:
            if block["type"] == "bush":
                if portal_x is None or block["rect"].x > portal_x:
                    portal_x = block["rect"].x
                    portal_y = block["rect"].y
        if portal_x is not None and portal_y is not None:
            px = portal_x // self.block_width
            py = portal_y // self.block_height

            py = py - 6  # portal base in blocks

            # clear space in blocks
            portal_rect = pygame.Rect(px*self.block_width, py*self.block_height,
                          1*self.block_width, 6*self.block_height)
            self.blocks = [b for b in self.blocks if not portal_rect.colliderect(b["rect"])]


            # === Build 1x6 portal ===
            rect = self.blocklibrary['portal_block'].get_rect(topleft=(px*self.block_width, py*self.block_height))
            self.blocks.append({"type": "portal_block", "texture": self.blocklibrary['portal_block'], "rect": rect})

            for i in range(1, 5):  # middle 4 = energy
                rect = self.blocklibrary['portal_energy_block'].get_rect(topleft=(px*self.block_width, (py+i)*self.block_height))
                self.blocks.append({"type": "portal_energy_block", "texture": self.blocklibrary['portal_energy_block'], "rect": rect})

            rect = self.blocklibrary['portal_block'].get_rect(topleft=(px*self.block_width, (py+5)*self.block_height))
            self.blocks.append({"type": "portal_block", "texture": self.blocklibrary['portal_block'], "rect": rect})

            # corrupt area around portal in block units
            self.corrupt_area(px, py, radius=15, seed=self.seed)

    def gen_hell(self, number_levels=3):
        self.blocks.clear()
        noise = OpenSimplex(seed=self.seed)
        screen_width, screen_height = self.screen.get_size()
        cols = screen_width // self.block_width
        rows = screen_height // self.block_height

        # Hell background
        self.background = pygame.image.load("Map\\BACKGROUND\\hellgame1.gif").convert()
        self.background = pygame.transform.scale(self.background, self.screen.get_size())

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
                        blocktype = "magma_block"
                    elif y < height - 1 and random.random() < 0.05:
                        blocktype = "lava_block"
                    else:
                        blocktype = "magma_block"

                    texture = self.blocklibrary[blocktype].copy()

                    # shading for depth
                    depth = (y_px - surface_y) // self.block_height
                    if depth > 0:
                        max_depth = 20
                        factor = max(0, 1 - ((depth / max_depth) ** 2))
                        texture.fill((int(255*factor), int(100*factor), int(50*factor)), special_flags=pygame.BLEND_MULT)

                    rect = texture.get_rect(topleft=((x + level * cols) * self.block_width, y_px))
                    self.blocks.append({"type": blocktype, "texture": texture, "rect": rect})

                    # Random fire blocks on top of magma
                    if blocktype == "magma_block" and random.random() < 0.08:
                        fire_rect = self.blocklibrary['fire_block'].get_rect(topleft=(rect.x, rect.y - self.block_height))
                        self.blocks.append({"type": "fire_block", "texture": self.blocklibrary['fire_block'], "rect": fire_rect})
                        

        # Build fullmap once for hell
        world_width_blocks = max(block["rect"].right for block in self.blocks) // self.block_width
        world_height_blocks = max(block["rect"].bottom for block in self.blocks) // self.block_height
        self.fullmap_surf = pygame.Surface((world_width_blocks, world_height_blocks))

        for block in self.blocks:
            color = (255, 100, 0)
            if block["type"] == "lava_block":
                color = (255, 0, 0)
            elif block["type"] == "fire_block":
                color = (255, 255, 0)
            mx = block["rect"].x // self.block_width
            my = block["rect"].y // self.block_height
            if 0 <= mx < self.fullmap_surf.get_width() and 0 <= my < self.fullmap_surf.get_height():
                self.fullmap_surf.set_at((mx, my), color)


    def corrupt_area(self, px, py, radius=10, seed=None):
        noise = OpenSimplex(seed if seed is not None else random.randint(0,10000))
        new_blocks = []
        for b in self.blocks:
            bx = b["rect"].x // self.block_width
            by = b["rect"].y // self.block_height
            dx = bx - px
            dy = by - py
            dist = (dx**2 + dy**2) ** 0.5
            if dist < radius:
                fade = 1 - (dist / radius)
                nval = noise.noise2(bx * 0.15, by * 0.15)
                chance = (nval + 1) / 2 * fade
                if b["type"] in ["grass","dirt","dirtstone","stone","bush",]:
                    if dist < radius:
                        fade = 1 - (dist / radius)
                        nval = noise.noise2(bx * 0.15, by * 0.15)
                        chance = (nval + 1) / 2  # keep full range [0..1]
                        threshold = 0.3 * fade   # easier to trigger near center
                        if chance > threshold:
                            if b["type"] in ["grass","dirt","dirtstone","stone","bush","tree_log","tree_stump"]:
                                tex = self.blocklibrary["magma_block"]
                                rect = tex.get_rect(topleft=b["rect"].topleft)
                                new_blocks.append({"type":"corrupt","texture":tex,"rect":rect})
                            continue

                    else:
                        new_blocks.append(b)  # keep original
                else:
                    new_blocks.append(b)  # keep non-terrain
            else:
                new_blocks.append(b)
        self.blocks = new_blocks

    def set_sfx_volume(self, volume: float):
        self.sfx_volume = max(0.0, min(1.0, volume))
        for s in self.sounds.values():
            s.set_volume(self.sfx_volume)

    def set_music_volume(self, volume: float):
        self.music_volume = max(0.0, min(1.0, volume))
        pygame.mixer.music.set_volume(self.music_volume)
    
    def newseed(self):
        self.seed = random.randint(0, 10**9)
        self.gen_world(number_levels=self.number_levels)
        if self.player:
            self.init_player()

    def add_to_hotbar(self, item, amount=1):
        for i in range(2,9):
            if self.hotbar_slots[i] == item:
                self.hotbar_counts[i] += amount
                return
       
        for i in range(2,9):
            if self.hotbar_slots[i] is None:
                self.hotbar_slots[i] = item
                self.hotbar_counts[i] = amount
                return
    
    def consume_from_hotbar(self, item, amount):
        remaining = amount
        for i in range(2, 9):  
            if remaining <= 0:
                break
            if self.hotbar_slots[i] == item and self.hotbar_counts[i] > 0:
                take = min(self.hotbar_counts[i], remaining)
                self.hotbar_counts[i] -= take
                remaining -= take
                if self.hotbar_counts[i] <= 0:
                    self.hotbar_slots[i] = None
                    self.hotbar_counts[i] = 0
        consumed = amount - remaining
        return consumed
             
    def draw_inventory(self):
        overlay = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0,0))

        #=======INVGRID===========#
        grid_width = self.inventory_cols * (self.inventory_slot_size + self.inventory_padding) - self.inventory_padding
        grid_height = self.inventory_rows * (self.inventory_slot_size + self.inventory_padding) - self.inventory_padding
        start_x = (self.screen.get_width() - grid_width) // 2
        start_y = (self.screen.get_height() - grid_height) // 2

        #==========SLOTCON===========#
        slot_index = 0
        for row in range(self.inventory_rows):
            for col in range(self.inventory_cols):
                slot_x = start_x + col * (self.inventory_slot_size + self.inventory_padding)
                slot_y = start_y + row * (self.inventory_slot_size + self.inventory_padding)
                rect = pygame.Rect(slot_x, slot_y, self.inventory_slot_size, self.inventory_slot_size)
                pygame.draw.rect(self.screen, (180,180,180), rect, 2)

                if slot_index < len(self.inventory):
                    block = list(self.inventory.keys())[slot_index]
                    count = self.inventory[block]

                    if block in self.blocklibrary:
                        img = self.blocklibrary[block]
                        img = pygame.transform.scale(img, (self.inventory_slot_size-8, self.inventory_slot_size-8))
                        self.screen.blit(img, (slot_x+4, slot_y+4))

                    if count > 0:
                        txt = self.font.render(str(count), True, (255,255,255))
                        self.screen.blit(txt, (slot_x+self.inventory_slot_size-18, slot_y+self.inventory_slot_size-18))
                slot_index += 1

    def run(self):
        running = True
        radius = 7 * self.block_width 
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
                            pygame.mixer_music.pause()
                            choice = self.pause_callback(self.screen,frozenbg)
                            pygame.mixer_music.unpause()
                            if choice == "exit":
                                pygame.mixer_music.pause()
                                return "menu"
                    if event.key == pygame.K_TAB :
                        self.show_inventory = not self.show_inventory
                        if self.show_inventory:
                            self.sounds["inv_open"].play()
                        else:
                            self.sounds["inv_close"].play()

                    
                        
                    if event.key == pygame.K_r:
                        self.newseed()
                    if event.key == pygame.K_c:
                        self.show_crafting = not self.show_crafting
                        if self.show_crafting:
                            self.crafting_scroll = 0
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_m:
                            self.show_fullmap = not self.show_fullmap

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
                            #self.sounds["hurt"].play()

                    if pygame.K_1 <= event.key <= pygame.K_9:
                        self.selected_index = event.key - pygame.K_1

                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    mx,my = pygame.mouse.get_pos()
                    world_mouse = (mx - camera_x, my)
                    for block in self.blocks:
                        if block["rect"].collidepoint(world_mouse):
                            if block["type"] in ["portal_block", "portal_energy_block"]:
                                if self.dimension == "overworld":
                                    self.loading_screen("Entering Hell...", 1.5)  # optional loading screen
                                    self.dimension = "hell"
                                    self.current_scene = 0
                                    self.gen_hell(number_levels=self.number_levels)
                                    # move player to hell spawn coordinates
                                    self.player.rect.topleft = (self.hell_spawn_x, self.hell_spawn_y)
                                    self.player.vel_x = 0
                                    self.player.vel_y = 0
                                else:
                                    self.loading_screen("Returning to Overworld...", 1.5)
                                    self.dimension = "overworld"
                                    self.current_scene = 0
                                    self.gen_world(number_levels=self.number_levels)
                                    # move player to overworld spawn
                                    self.player.rect.topleft = (self.overworld_spawn_x, self.overworld_spawn_y)
                                    self.player.vel_x = 0
                                    self.player.vel_y = 0
                                break

                # ===== Crafting click =====
                if self.show_crafting and event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    mx, my = pygame.mouse.get_pos()
                    start_y = 40
                    indexs = self.crafting_scroll
                    for i in range(self.crafting_visible):
                        if indexs >= len(self.recipes):
                            break
                        item = list(self.recipes.keys())[indexs]
                        reqs = self.recipes[item]
                        rect = pygame.Rect(20, start_y + i*30, 160, 30)
                        if rect.collidepoint(mx, my):
                            if all(self.inventory.get(mat, 0) >= amount for mat, amount in reqs.items()):
                                
                                for mat, amount in reqs.items():
                                    self.inventory[mat] -= amount

                                    
                                    consumed = self.consume_from_hotbar(mat, amount)

            
                                if item == "wood_planks":
                                    
                                    self.add_to_hotbar("wood_planks", 4)
                                    self.inventory["wood_planks"] += 4
                                    self.sounds["craft"].play()


                        indexs += 1
                
                if event.type == pygame.MOUSEBUTTONDOWN and not self.show_inventory or self.show_crafting:
                    mouse_position = pygame.mouse.get_pos()
                    world_mouse = (mouse_position[0] - camera_x, mouse_position[1])
                    if self.player:
                        player_center = self.player.rect.center
                        distance = ((world_mouse[0] - player_center[0])**2 + (world_mouse[1] - player_center[1]) **2) **0.5
                        if distance <= radius:  
                            if event.type == pygame.MOUSEBUTTONDOWN and event.button ==1 :  
                                for block in self.blocks:
                                    if block["rect"].collidepoint(world_mouse):
                                        removed_block = block
                                        self.blocks.remove(block)
                                        bloktype = removed_block.get("type")
                                        if bloktype in self.inventory:
                                            self.inventory[bloktype] += 1
                                            self.add_to_hotbar(bloktype, 1)
                                        self.sounds["block_break"].play()

                                        if bloktype =="grass":
                                        
                                            for top in self.blocks[:]:
                                                if top["type"] == "bush" and top["rect"].x == removed_block["rect"].x and top["rect"].bottom == removed_block["rect"].top:
                                                    self.blocks.remove(top)
                                            break
                                    
                                        break  
                            elif event.type ==pygame.MOUSEBUTTONDOWN and event.button == 3:  
                                x, y = world_mouse
                                col = int(x // self.block_width)
                                row = int((self.screen.get_height() - y) // self.block_height)  
                                y_px = self.screen.get_height() - (row + 1) * self.block_height

                                new_block_rect = self.blocklibrary['dirt'].get_rect(topleft=(col * self.block_width, y_px))
                                occupied = any(b["rect"].colliderect(new_block_rect) for b in self.blocks)
                                
                                selected_type = self.hotbar_slots[self.selected_index]
                                if selected_type is None:
                                    selected_type = "dirt"
                                selected_texture = self.blocklibrary.get(selected_type, self.blocklibrary['dirt'])
                               
                                inv_ok = True
                                if selected_type in self.inventory and self.inventory[selected_type] <= 0:
                                    inv_ok = False

                                if not new_block_rect.colliderect(self.player.rect) and not occupied and inv_ok:
                                    self.sounds["block_place"].play()
                                    self.blocks.append({
                                        "type": selected_type,
                                        "texture": selected_texture,
                                        "rect": new_block_rect
                                    })
                                    if selected_type in self.inventory:
                                        self.inventory[selected_type] -= 1
                                        for i in range(2,9):
                                            if self.hotbar_slots[i] == selected_type:
                                                self.hotbar_counts[i] = max(0, self.hotbar_counts[i]-1)
                                                if self.hotbar_counts[i] == 0:
                                                    self.hotbar_slots[i] = None
                                                break
                        if event.type == pygame.MOUSEBUTTONDOWN and event.button ==4:
                            self.selected_index = (self.selected_index -1)
            keys = pygame.key.get_pressed()
            if self.player and not self.show_inventory or self.show_crafting:
                left = keys[pygame.K_a] 
                right = keys[pygame.K_d] 
                jump = keys[pygame.K_SPACE] 
                self.player.move(left, right, jump)
                self.player.update()

                #=========Cameralogic=======
                screen_width = self.screen.get_width()
                world_width = screen_width * self.number_levels

                if self.player.rect.right > (self.current_scene + 1) * screen_width:
                    if self.player.rect.right > (self.current_scene + 1) * screen_width:
                        if self.current_scene < self.number_levels - 1:
                            self.current_scene += 1
                            self.player.rect.left = self.current_scene * screen_width + 2 * self.block_width
                            self.player.rect.bottom = self.get_safe_spawn_y(self.player.rect.centerx, self.current_scene)


                elif self.player.rect.left < self.current_scene * screen_width:
                    if self.current_scene > 0:
                        self.current_scene -= 1
                        self.player.rect.right = (self.current_scene + 1) * screen_width - 2 * self.block_width
                        new_scene_blocks = [b for b in self.blocks if self.current_scene * screen_width <= b["rect"].x < (self.current_scene+1)*screen_width]
                        ground_y = min([b["rect"].top for b in new_scene_blocks if b["rect"].colliderect(self.player.rect.move(0,1000))],default=self.player.rect.bottom)
                        self.player.rect.bottom = ground_y

                self.player.rect.left = max(0, self.player.rect.left)
                self.player.rect.right = min(world_width, self.player.rect.right)
                camera_x = -self.current_scene * screen_width


            # ================= HOTBAR NUMBER KEYS ============== #
            pressed = pygame.key.get_pressed()
            for n in range(1,10):
                if pressed[getattr(pygame, f"K_{n}")]:
                    self.selected_index = n-1

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
            #drawbar#==============
            hotbar_slots = self.hotbar_slots
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
                
                if i == self.selected_index:
                    pygame.draw.rect(self.screen, (255,215,0), rect, 3)  
                else:
                    pygame.draw.rect(self.screen, (0,0,0), rect, 2)
                
                hotbartexture = None
                if bloktype and bloktype in self.blocklibrary:
                    hotbartexture = self.blocklibrary.get(bloktype)

                if hotbartexture:
                    icon = pygame.transform.scale(hotbartexture, (slot_w - 8, slot_h - 8))
                    icon_rect = icon.get_rect(center=rect.center)
                    self.screen.blit(icon, icon_rect)
                
                count = 0
                if bloktype:
                    if self.hotbar_slots[i] == bloktype and self.hotbar_counts[i] > 0:
                        count = self.hotbar_counts[i]
                    else:
                        count = self.inventory.get(bloktype, 0)
                count_surf = self.font.render(str(count), True, (255,255,255))
                count_rect = count_surf.get_rect(bottomright=(rect.right - 4, rect.bottom - 4))
                self.screen.blit(count_surf, count_rect)
                #===========Heathdissapearlogic============#
            if self.player:
                if current_time - last_health_change <= health_display_time:
                    self.player.draw_health_bar(self.screen, camera_x)
                self.player.draw(self.screen, camera_x)

           
            if self.show_crafting:
                panel_width = 200
                panel_height = self.screen.get_height()
                panel = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
                panel.fill((30,30,30,180))
                self.screen.blit(panel, (0,0))

                start_y = 40
                indexs = self.crafting_scroll
                for i in range(self.crafting_visible):
                    if indexs >= len(self.recipes):
                        break
                    item = list(self.recipes.keys())[indexs]
                    reqs = self.recipes[item]
                    craftable = all(self.inventory.get(mat, 0) >= amount for mat, amount in reqs.items())
                    color = (255,255,255) if craftable else (150,50,50)
                    
                    if item == "wood_planks":
                        text = f"{item} x4: tree_log x1"
                    else:
                        text = f"{item}: " + ", ".join([f"{m}x{a}" for m,a in reqs.items()])

                    txt = self.crafting_font.render(text, True, color)
                    self.screen.blit(txt, (20, start_y + i*30))
                    indexs += 1
            if self.show_inventory:
                self.draw_inventory()
            



            # =====TIMER=====#
            elapsed_ms = current_time - self.start_time
            minutes = elapsed_ms // 60000
            seconds = (elapsed_ms % 60000) // 1000
            hundredths = (elapsed_ms % 1000) // 10  

            
            self.timer_font = pygame.font.SysFont("Consolas", 26)  
            time_text = f"{minutes:02}:{seconds:02}:{hundredths:02}"
            time_surf = self.timer_font.render(time_text, True, (255, 255, 255))

            x_offset = self.screen.get_width() - 120  
            time_rect = time_surf.get_rect(topleft=(x_offset, 20))

            self.screen.blit(time_surf, time_rect)

            if self.show_fullmap and self.fullmap_surf:
                # Dark overlay
                overlay = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 200))
                self.screen.blit(overlay, (0, 0))

                # Determine scale factor
                max_width = self.screen.get_width() - 100
                max_height = self.screen.get_height() - 100
                scale_x = max_width / self.fullmap_surf.get_width()
                scale_y = max_height / self.fullmap_surf.get_height()
                scale = min(scale_x, scale_y)

                # Scale minimap
                map_display = pygame.transform.scale(
                    self.fullmap_surf,
                    (int(self.fullmap_surf.get_width() * scale),
                    int(self.fullmap_surf.get_height() * scale))
                )

                # Centered rectangle
                map_rect = map_display.get_rect(center=self.screen.get_rect().center)

                # Draw a background panel with border
                panel = pygame.Surface((map_rect.width + 12, map_rect.height + 12), pygame.SRCALPHA)
                panel.fill((20, 20, 20, 180))  # dark semi-transparent
                pygame.draw.rect(panel, (255, 215, 0), panel.get_rect(), 2)  # golden border
                panel_rect = panel.get_rect(center=self.screen.get_rect().center)
                self.screen.blit(panel, panel_rect.topleft)

                # Draw minimap on top
                self.screen.blit(map_display, map_rect)

                # Player dot
                px = int(self.player.rect.x / self.block_width * scale)
                py = int(self.player.rect.y / self.block_height * scale)
                pygame.draw.rect(self.screen, (255, 0, 0), (map_rect.left + px, map_rect.top + py, 6, 6))






            pygame.display.flip()
            self.clock.tick(60)
        return "pause"

    def get_safe_spawn_y(self, x, scene_index):
        screen_width = self.screen.get_width()
        scene_blocks = [b for b in self.blocks if scene_index * screen_width <= b["rect"].x < (scene_index + 1) * screen_width]

        # Find blocks right under the player's X
        candidates = [b for b in scene_blocks if b["rect"].left <= x < b["rect"].right]
        if candidates:
            return min(b["rect"].top for b in candidates)
        return self.screen.get_height() - self.block_height
if __name__ == "__main__":
    generateworld().run()
