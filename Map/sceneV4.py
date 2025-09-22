import pygame, random, time, sys, os
from opensimplex import *

current_directory = os.path.dirname(os.path.abspath(__file__))
parent_directory = os.path.dirname(current_directory)
player_directory = os.path.join(parent_directory, 'PlayerMovement&Physics')
sys.path.append(player_directory)

# Updated imports for PlayerV4
from PlayerV4 import Player, load_base_animations, load_action_animations, gender_selection_screen, main
from PlayerV4 import IDLE, WALK, JUMP, ATTACK, MINE, SCALE
from Enemy import Enemy
from Boss import Boss

# ==== NEW ENEMY SPRITESHEET CLASS ==== #
class SpriteSheet:
    def __init__(self, image):
        self.sheet = image

    def get_image(self, frame, width, height, scale, colour):
        image = pygame.Surface((width, height)).convert_alpha()
        image.blit(self.sheet, (0, 0), ((frame * width), 0, width, height))
        image = pygame.transform.scale(image, (int(width * scale), int(height * scale)))
        image.set_colorkey(colour)
        return image

# ==== NEW ENEMY CLASS FOR SCENE ==== #
class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, sprite_sheet, scale, blocks, block_width, block_height):
        pygame.sprite.Sprite.__init__(self)
        # Animation variables
        self.animation_list = []
        self.frame_index = 0
        self.update_time = pygame.time.get_ticks()
        self.direction = random.choice([-1, 1])
        self.flip = True if self.direction == 1 else False
        
        # Physics variables
        self.vel_y = 0
        self.gravity = 0.8
        self.jump_speed = -15
        self.on_ground = False
        self.jump_timer = 0
        self.jump_cooldown = random.randint(60, 120)
        
        # Combat variables
        self.health = 100
        self.max_health = 100
        self.attack_damage = 5  # 5% of player max health (100). Change to 100 for full player damage.
        self.attack_cooldown = 500  # 0.5 seconds between attacks (reduced for more responsive feel)
        self.last_attack_time = 0
        self.is_dead = False
        
        # World collision
        self.blocks = blocks
        self.block_width = block_width
        self.block_height = block_height
        
        # Load animation frames
        animation_steps = 8
        for animation in range(animation_steps):
            image = sprite_sheet.get_image(animation, 32, 32, scale, (0, 0, 0))
            if self.flip:
                image = pygame.transform.flip(image, True, False)
            image.set_colorkey((0, 0, 0))
            self.animation_list.append(image)
        
        # Set initial image and rect
        self.image = self.animation_list[self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        
        # NEW: Create masks for pixel-perfect collision (one per animation frame)
        self.masks = []
        for image in self.animation_list:
            mask = pygame.mask.from_surface(image)
            self.masks.append(mask)
        self.current_mask = self.masks[self.frame_index]  # Start with first frame's mask
        
        # Find ground position after initialization
        self.find_ground()
    
    def find_ground(self):
        # Find the nearest grass block below the enemy's spawn position
        ground_y = self.rect.y + 500  # Default fallback
        
        for block in self.blocks:
            if (block["type"] == "grass" and 
                abs(block["rect"].centerx - self.rect.centerx) < self.block_width * 3):
                if block["rect"].top > self.rect.y:
                    ground_y = min(ground_y, block["rect"].top)
        
        # Start enemy above the ground so it falls down
        self.rect.bottom = ground_y - 100  # Start 100 pixels above ground
        self.on_ground = False
        self.vel_y = 0  # Start with no velocity so gravity takes effect
    
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
    
    def take_damage(self, damage):
        self.health -= damage
        if self.health <= 0:
            self.health = 0
            self.is_dead = True
    
    def can_attack(self):
        current_time = pygame.time.get_ticks()
        return current_time - self.last_attack_time >= self.attack_cooldown
    
    def attack_player(self, player):
        if self.can_attack() and not self.is_dead:
            player.get_damage(self.attack_damage)
            self.last_attack_time = pygame.time.get_ticks()
            # Optional: Trigger visual flash on player hit
            if hasattr(player, 'hit_flash'):
                player.h极it_flash = pygame.time.get_ticks()
            return True
        return False
    
    def update(self, player=None):
        if self.is_dead:
            return
        
        # Update animation
        ANIMATION_COOLDOWN = 150
        if pygame.time.get_ticks() - self.update_time > ANIMATION_COOLDOWN:
            self.update_time = pygame.time.get_ticks()
            self.frame_index += 1
        
        if self.frame_index >= len(self.animation_list):
            self.frame_index = 0
        
        self.image = self.animation_list[self.frame_index]
        
        # NEW: Update current mask for the active frame
        self.current_mask = self.masks[self.frame_index % len(self.masks)]  # Cycle if needed
        
        # Handle jumping (only when on ground)
        self.jump_timer += 1
        if self.jump_timer >= self.jump_cooldown and self.on_ground:
            self.vel_y = self.jump_speed
            self.on_ground = False
            self.jump_timer = 0
            self.jump_cooldown = random.randint(60, 120)
        
        # Apply gravity
        self.vel_y += self.gravity
        
        # Vertical movement with collision
        if not self.check_collision(0, self.vel_y):
            self.rect.y += self.vel_y
        else:
            if self.vel_y > 0:  # Landing
                self.vel_y = 0
                self.on_ground = True
            elif self.vel_y < 0:  # Hitting ceiling
                self.vel_y = 0
        
        # Horizontal movement with collision and direction change
        move_x = self.direction * 1
        if not self.check_collision(move_x, 0):
            self.rect.x += move_x
        else:
            # Change direction when hitting wall
            self.direction *= -1
            self.flip = not self.flip
            # Update animation frames for new direction
            for i, frame in enumerate(self.animation_list):
                self.animation_list[i] = pygame.transform.flip(frame, True, False)
        
        # Check collision with player for attack (now pixel-perfect)
        if player and self.rect.colliderect(player.rect):
            # First, quick rect check passed. Now do pixel-perfect mask check
            # Offset masks to align with sprite positions
            if hasattr(player, 'mask') and player.mask and self.current_mask.overlap(player.mask, (player.rect.x - self.rect.x, player.rect.y - self.rect.y)):
                self.attack_player(player)
            else:
                # Fallback to rect collision if no mask
                self.attack_player(player)
    
    def draw_health_bar(self, surf, camera_x):
        if self.is_dead:
            return
        
        bar_width = 40
        bar_height = 4
        x = self.rect.centerx + camera_x - bar_width//2
        y = self.rect.top - 10

        # Red background
        redback = pygame.Surface((bar_width, bar_height))
        redback.fill((255, 0, 0))
        surf.blit(redback, (x, y))

        # Green health
        green_width = int(bar_width * (self.health/self.max_health))
        if green_width > 0:
            greenback = pygame.Surface((green_width, bar_height))
            greenback.fill((0, 255, 0))
            surf.blit(greenback, (x, y))
    
    def draw(self, surf, camera_x):
        if not self.is_dead:
            surf.blit(self.image, self.rect.move(camera_x, 0))
            self.draw_health_bar(surf, camera_x)

#=====BOSS=====#
boss_animation_config = {
    'idle': {'file': 'Sprite_Img/boss_idle.png', 'frames': 6, 'width': 128, 'height': 128},
    'dead': {'file': 'Sprite_Img/boss_dead.png', 'frames': 8, 'width': 128, 'height': 128},
    'attack1': {'file': 'Sprite_Img/boss_attack1.png', 'frames': 6, 'width': 128, 'height': 128},
    'attack2': {'file': 'Sprite_Img/boss_attack2.png', 'frames': 5, 'width': 128, 'height': 128},
    'fireball': {'file': 'Sprite_Img/boss_fireball.png', 'frames': 4, 'width': 64, 'height': 64},
    'run': {'file': 'Sprite_Img/boss_run.png', 'frames': 8, 'width': 128, 'height': 128},
    'jump': {'file': 'Sprite_Img/boss_jump.png', 'frames': 4, 'width': 128, 'height': 128}
}

def load_boss_animations(scale=2):
    boss_animations = {}
    sprite_img_dir = os.path.join(parent_directory, 'PlayerMovement&Physics' )
    
    for animation_name, config in boss_animation_config.items():
        sprite_path = os.path.join(sprite_img_dir, config['file'])
        
        try:
            sprite_image = pygame.image.load(sprite_path).convert_alpha()
            sprite_sheet = SpriteSheet(sprite_image)
            
            frames = []
            for frame_index in range(config['frames']):
                frame = sprite_sheet.get_image(
                    frame_index, config['width'], config['height'], scale, (0, 0, 0)  # Black colorkey
                )
                frames.append(frame)
            boss_animations[animation_name] = frames
        except pygame.error:
            print(f"Warning: Could not load boss sprite {sprite_path}. Using placeholder.")
            # Placeholder: Magenta surface
            placeholder = pygame.Surface((config['width'] * scale, config['height'] * scale)).convert_alpha()
            placeholder.fill((255, 0, 255))
            boss_animations[animation_name] = [placeholder] * config['frames']
    
    return boss_animations

class BossAnimator:
    def __init__(self, animations):
        self.animations = animations
        self.current_animation = 'idle'
        self.current_frame = 0
        self.update_time = pygame.time.get_ticks()
        self.animation_cooldown = 150  # ms, matches enemy timing
        self.facing_right = False  # Face left initially (toward player)
    
    def update(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.update_time > self.animation_cooldown:
            self.update_time = current_time
            self.current_frame += 1
            max_frames = len(self.animations[self.current_animation])
            if self.current_frame >= max_frames:
                self.current_frame = 0
                return True  # Animation finished (used for attack resets)
        return False
    
    def set_animation(self, animation_name):
        if animation_name in self.animations and animation_name != self.current_animation:
            self.current_animation = animation_name
            self.current_frame = 0
            self.update_time = pygame.time.get_ticks()
    
    def get_current_image(self):
        frame = self.animations[self.current_animation][self.current_frame]
        if not self.facing_right:
            frame = pygame.transform.flip(frame, True, False)
        return frame
    
class Fireball(pygame.sprite.Sprite):
    def __init__(self, x, y, target_x, fireball_frames, blocks, block_width, block_height):
        super().__init__()
        self.frames = fireball_frames
        self.frame_index = 0
        self.image = self.frames[0]
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = 4  # Pixels per frame
        self.direction = -1 if target_x < x else 1  # Move toward player
        self.update_time = pygame.time.get_ticks()
        self.animation_cooldown = 100  # Faster animation for fireball
        self.blocks = blocks
        self.block_width = block_width
        self.block_height = block_height
        self.damage = 15  # Damage to player on hit
    
    def update(self, player):
        # Animate
        current_time = pygame.time.get_ticks()
        if current_time - self.update_time > self.animation_cooldown:
            self.update_time = current_time
            self.frame_index = (self.frame_index + 1) % len(self.frames)
            self.image = self.frames[self.frame_index]
        
        # Move horizontally
        self.rect.x += self.direction * self.speed
        
        # Check block collision (despawn if hit solid block)
        for block in self.blocks:
            if block["type"] not in ["bush", "tree_stump", "tree_log", "tree_top"] and self.rect.colliderect(block["rect"]):
                self.kill()  # Despawn
                return
        
        # Check player collision (damage and despawn)
        if player and self.rect.colliderect(player.rect):
            player.get_damage(self.damage)
            if hasattr(player, 'hit_flash'):
                player.hit_flash = pygame.time.get_ticks()
            self.kill()
        
        # Despawn if off-screen
        if self.rect.right < 0 or self.rect.left > player.world_width if hasattr(player, 'world_width') else self.rect.left > 2000:
            self.kill()
    
    def draw(self, surf, camera_x):
        surf.blit(self.image, self.rect.move(camera_x, 0))

class Boss(pygame.sprite.Sprite):
    def __init__(self, x, y, animations, blocks, block_width, block_height, world_width):
        super().__init__()
        self.animations = animations
        self.animator = BossAnimator(animations)
        self.image = self.animator.get_current_image()
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        
        # Physics (similar to Enemy)
        self.vel_y = 0
        self.gravity = 0.8
        self.jump_speed = -15
        self.on_ground = False
        self.speed = 2  # Slower than player for chase feel
        
        # Combat
        self.health = 500
        self.max_health = 500
        self.attack_damage = 20
        self.attack_cooldown = 1000  # 1s between attacks
        self.last_attack = 0
        self.is_dead = False
        self.fireball_cooldown = 0
        self.fireball_cd_time = 3000  # 3s between fireballs
        self.current_state = 'idle'
        
        # World
        self.blocks = blocks
        self.block_width = block_width
        self.block_height = block_height
        self.world_width = world_width
        
        # Masks for pixel-perfect collision
        self.masks = {}
        for state, frames in animations.items():
            if state != 'fireball':  # No mask for projectiles
                self.masks[state] = [pygame.mask.from_surface(f) for f in frames]
        self.current_mask = self.masks['idle'][0]
        
        self.find_ground()
    
    def find_ground(self):
        # Similar to Enemy.find_ground
        ground_y = self.rect.y + 500
        for block in self.blocks:
            if (block["type"] == "grass" and 
                abs(block["rect"].centerx - self.rect.centerx) < self.block_width * 5):  # Wider search for boss
                if block["rect"].top > self.rect.y:
                    ground_y = min(ground_y, block["rect"].top)
        self.rect.bottom = ground_y - 100  # Start above ground
        self.on_ground = False
    
    def check_collision(self, dx, dy):
        # Same as Enemy.check_collision
        temp_rect = self.rect.copy()
        temp_rect.x += dx
        temp_rect.y += dy
        for block in self.blocks:
            if block["type"] in ["bush", "tree_stump", "tree_log", "tree_top"]:
                continue
            if temp_rect.colliderect(block["rect"]):
                return True
        return False
    
    def take_damage(self, damage):
        if not self.is_dead:
            self.health -= damage
            if self.health <= 0:
                self.health = 0
                self.is_dead = True
                self.animator.set_animation('dead')
    
    def attack_player(self, player):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_attack >= self.attack_cooldown and not self.is_dead:
            player.get_damage(self.attack_damage)
            if hasattr(player, 'hit_flash'):
                player.hit_flash = pygame.time.get_ticks()
            self.last_attack = current_time
            return True
        return False
    
    def update(self, player, fireball_group):
        if self.is_dead or not player:
            self.animator.update()
            self.image = self.animator.get_current_image()
            return
        
        anim_finished = self.animator.update()
        self.image = self.animator.get_current_image()
        state = self.animator.current_animation
        self.current_mask = self.masks[state][self.animator.current_frame % len(self.masks[state])]
        
        dist_x = abs(player.rect.centerx - self.rect.centerx)
        current_time = pygame.time.get_ticks()
        
        # State machine
        if self.current_state == 'attack2' and anim_finished:
            # Reset after attack2
            self.current_state = 'chase' if dist_x <= 320 else 'idle'
            self.animator.set_animation('run' if self.current_state == 'chase' else 'idle')
        
        elif dist_x >= 800:
            # Attack1 + Fireball
            if self.current_state != 'attack1':
                self.current_state = 'attack1'
                self.animator.set_animation('attack1')
            if current_time - self.fireball_cooldown >= self.fireball_cd_time:
                # Spawn fireball from boss center toward player
                fx = self.rect.centerx
                fy = self.rect.centery
                fireball = Fireball(fx, fy, player.rect.centerx, self.animations['fireball'], 
                                   self.blocks, self.block_width, self.block_height)
                fireball_group.add(fireball)
                self.fireball_cooldown = current_time
        
        elif dist_x <= 320:
            # Chase mode: Move + Jump AI
            if self.current_state != 'chase':
                self.current_state = 'chase'
                self.animator.set_animation('run')
            direction = 1 if player.rect.centerx > self.rect.centerx else -1
            self.animator.facing_right = direction > 0
            move_x = direction * self.speed
            
            # Jump AI: If blocked, jump (only on ground)
            if self.check_collision(move_x, 0) and self.on_ground:
                self.vel_y = self.jump_speed
                self.on_ground = False
                self.animator.set_animation('jump')
            else:
                self.rect.x += move_x
            
            # Check collision for attack2
            if self.rect.colliderect(player.rect):
                offset_x = player.rect.x - self.rect.x
                offset_y = player.rect.y - self.rect.y
                if (hasattr(player, 'mask') and player.mask and 
                    player.mask.overlap(self.current_mask, (offset_x, offset_y))):
                    self.current_state = 'attack2'
                    self.animator.set_animation('attack2')
                    self.attack_player(player)
                else:
                    # Fallback rect collision
                    self.attack_player(player)
        
        else:
            # Idle (mid-range)
            if self.current_state not in ['idle', 'attack1']:
                self.current_state = 'idle'
                self.animator.set_animation('idle')
        
        # Vertical physics (gravity + collision, like Enemy)
        self.vel_y += self.gravity
        if not self.check_collision(0, self.vel_y):
            self.rect.y += self.vel_y
        else:
            if self.vel_y > 0:  # Land
                self.vel_y = 0
                self.on_ground = True
            else:  # Ceiling
                self.vel_y = 0
        
        # Reset to run after jump lands
        if self.on_ground and self.animator.current_animation == 'jump':
            self.animator.set_animation('run')
        
        # World bounds
        self.rect.left = max(0, self.rect.left)
        self.rect.right = min(self.world_width, self.rect.right)
    
    def draw_health_bar(self, surf, camera_x):
        if self.is_dead:
            return
        bar_width = 100  # Wider for boss
        bar_height = 8
        x = self.rect.centerx + camera_x - bar_width // 2
        y = self.rect.top - 20
        # Red background
        pygame.draw.rect(surf, (255, 0, 0), (x, y, bar_width, bar_height))
        # Green health
        health_ratio = self.health / self.max_health
        green_width = int(bar_width * health_ratio)
        pygame.draw.rect(surf, (0, 255, 0), (x, y, green_width, bar_height))
        # Border
        pygame.draw.rect(surf, (255, 255, 255), (x, y, bar_width, bar_height), 2)
    
    def draw(self, surf, camera_x):
        if not self.is_dead:
            surf.blit(self.image, self.rect.move(camera_x, 0))
            self.draw_health_bar(surf, camera_x)



# =====PLAYER================================================================================================================= #
class Playeronworld(Player): #1
    def __init__(self, base_animation_list, action_animation_list, gender, blocks, block_width, block_height, world_width):
        super().__init__(base_animation_list, action_animation_list, gender)
        self.blocks = blocks
        self.block_width = block_width
        self.block_height = block_height
        self.world_width = world_width
        # Use PlayerV4's health system
        self.current_health = 100
        self.maximum_health = 100
        
        # NEW: Pixel-perfect collision mask (updated in update method)
        self.mask = None
        
        # NEW: For visual hit flash
        self.hit_flash = 0
        
    #======DamageLogic============#   
    def get_damage(self, amt):
        super().get_damage(amt)  # Use PlayerV4's method
    
    #========HealthLogic===========#
    def get_health(self, amt):
        super().get_health(amt)  # Use PlayerV4's method
    
    @property
    def health(self):
        """Compatibility property for existing scene.py code"""
        return self.current_health
    
    @health.setter 
    def health(self, value):
        """Compatibility property setter"""
        self.current_health = max(0, min(self.maximum_health, value))
    
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
    
    # ==== NEW ENEMY ATTACK METHOD ==== #
    # Replace the existing attack_enemies method in Playeronworld
    def attack_enemies(self, enemy_group, boss_group=None):
        """Attack nearby enemies or boss when player presses attack key"""
        attack_range = 60  # Pixels
        attacked = False
        
        # Attack enemies (existing logic)
        for enemy in enemy_group:
            if not enemy.is_dead:
                dx = enemy.rect.centerx - self.rect.centerx
                dy = enemy.rect.centery - self.rect.centery
                distance = (dx**2 + dy**2)**0.5
                if distance <= attack_range:
                    enemy.take_damage(100)  # Kill enemy
                    attacked = True
                    break  # One attack per frame
        
        # Attack boss if present and in range
        if boss_group:
            boss_list = boss_group.sprites()
            if boss_list:  # make sure it's not empty
                boss = boss_list[0]  # first boss
                if boss and not boss.is_dead:
                    dx = boss.rect.centerx - self.rect.centerx
                    dy = boss.rect.centery - self.rect.centery
                    distance = (dx**2 + dy**2)**0.5
                    if distance <= attack_range:
                        boss.take_damage(50)
                        attacked = True
        
        return attacked

    
    #=============ConstantSids========================#
    def update(self):
        # Use PlayerV4's update method but with collision checking
        current_time = pygame.time.get_ticks()
        
        # Check极 if action should end
        if self.is_performing_action:
            if current_time - self.action_start_time >= self.action_duration:
                self.is_performing_action = False
                self.action = IDLE
                self.frame = 0

        # Animation update
        if current_time - self.last_update >= self.animation_cooldown:
            self.frame += 1
            self.last_update = current_time
            
            # Check if we've reached the end of the current animation
            if self.frame >= self.get_animation_length():
                if self.is_performing_action:
                    # For actions, stop the action when animation completes
                    self.is_performing_action = False
                    self.action = IDLE
                self.frame = 0

        # Get and scale the current image
        self.image = self.scale_current_image()
        if self.flip:
            self.image = pygame.transform.flip(self.image, True, False)
        
        # NEW: Create/update mask for pixel-perfect collision
        self.mask = pygame.mask.from_surface(self.image)

        # Only apply physics if not performing an action
        if not self.is_performing_action:
            # Gravity with collision checking
            self.vel_y += self.gravity
            if not self.check_collision(0, self.vel_y):
                self.rect.y += self.vel_y
            else:
                if self.vel_y > 0:  
                    self.vel_y = 0
                    self.in_air = False
                elif self.vel_y < 0:  
                    self.vel_y = 0

            # Horizontal movement with collision checking
            if not self.check_collision(self.vel_x, 0):
                self.rect.x += self.vel_x
            
            # World bounds
            if self.rect.left < 0:
                self.rect.left = 0
            if self.rect.right > self.world_width:
                self.rect.right = self.world_width
    
    #=============Scenecam===============#
    def draw(self, surf, camera_x):
        # NEW: Flash red if recently hit
        if self.hit_flash and pygame.time.get_ticks() - self.hit_flash < 200:
            flash_image = self.image.copy()
            flash_image.fill((255, 0, 0, 128), special_flags=pygame.BLEND_RGBA_MULT)
            surf.blit(flash_image, self.rect.move(camera_x, 0))
        else:
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

        green_width = int(bar_width * (self.current_health/self.maximum_health))
        if green_width > 0:
            greenback = pygame.Surface((green_width, bar_height), pygame.SRCALPHA)
            greenback.fill((0, 255, 0, alpha))
            surf.blit(greenback, (x, y))

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
        self.number_levels = 5
        self.gen_world(number_levels=self.number_levels)
        self.init_player()
        self.current_scene = 0  
        self.highlight = False
        
        self.pause_callback = pause_callback

        # ==== NEW ENEMY SYSTEM ==== #
        self.init_enemy_system()
        self.boss_group = pygame.sprite.Group()  
        self.fireball_group = pygame.sprite.Group()  
        self.init_boss_system()

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
        
    # ==== ENEMY INITIALIZATION ==== #
    def init_enemy_system(self):
        """Initialize enemy sprite sheet and enemy groups"""
        try:
            enemy_sheet_img = pygame.image.load("PlayerMovement&Physics/Sprite_Img/enemy_sprite.png").convert_alpha()
        except pygame.error:
            # Create placeholder sprite sheet if file doesn't exist
            enemy_sheet_img = pygame.Surface((256, 32)).convert_alpha()
            enemy_sheet_img.fill((255, 0, 0))  # Red placeholder
        
        self.enemy_sheet = SpriteSheet(enemy_sheet_img)
        self.enemy_group = pygame.sprite.Group()
        
        # Ensure world is generated before spawning enemies
        if len(self.blocks) > 0:
            self.spawn_enemies()
    
    def spawn_enemies(self):
        """Spawn enemies in scenes 2 and 3 only"""
        self.enemy_group.empty()  # Clear existing enemies
        screen_width = self.screen.get_width()
        
        # Wait a moment to ensure blocks are fully generated
        if len(self.blocks) == 0:
            return
        
        # Spawn enemies only in scenes 2 & 3 (index 1 & 2)
        for scene in [1, 2]:  # Scene indices 1 and 2 (scenes 2 and 3)
            num_enemies = random.randint(2, 4)  # 2-4 enemies per scene
            
            for _ in range(num_enemies):
                # Random x position within the scene
                x = random.randint(scene * screen_width + 100, (scene + 1) * screen_width - 100)
                
                # Find grass blocks in this scene to determine spawn height
                scene_grass_blocks = []
                for block in self.blocks:
                    if (block["type"] == "grass" and 
                        scene * screen_width <= block["rect"].centerx < (scene + 1) * screen_width):
                        scene_grass_blocks.append(block)
                
                if scene_grass_blocks:
                    # Find the grass block closest to our spawn x position
                    closest_grass = min(scene_grass_blocks, 
                                      key=lambda b: abs(b["rect"].centerx - x))
                    y = closest_grass["rect"].top - 200  # Start 200 pixels above grass
                else:
                    # Fallback if no grass blocks found
                    y = 100
                
                # Create enemy
                enemy = Enemy(x, y, self.enemy_sheet, 2, self.blocks, 
                             self.block_width, self.block_height)
                self.enemy_group.add(enemy)

#===== BOSS INITIALIZE =====#
    def init_boss_system(self):
        "Initialize boss animations and spawn the boss in the last scene."
        # Load boss animations once (scale=2 for visibility, adjust if needed)
        self.boss_animations = load_boss_animations(scale=2)
    
        # Clear any existing boss/fireballs
        self.boss_group.empty()
        self.fireball_group.empty()
    
        # Spawn boss only if world is generated
        if len(self.blocks) > 0:
            self.spawn_boss()

    def spawn_boss(self):
        """Spawn the boss in the last scene, at the far right."""
        screen_width = self.screen.get_width()
        last_scene_index = self.number_levels - 1
        scene_start_x = last_scene_index * screen_width
    
        # Boss spawn x: Far right of last scene (100px margin from edge)
        boss_width = 128 * 2  # Approximate scaled width from animations (128px * scale=2)
        spawn_x = scene_start_x + screen_width - boss_width - 100  # Most right
    
        # Initial y: High up, will fall to ground via find_ground()
        spawn_y = 200  # Arbitrary high position
        
        # Create boss with world data
        world_width = screen_width * self.number_levels
        boss = Boss(
            spawn_x, spawn_y, 
            self.boss_animations,  # Loaded animations
            self.blocks, self.block_width, self.block_height, 
            world_width  # For bounds checking
        )
        self.boss_group.add(boss)
        
        print(f"Boss spawned at ({spawn_x}, {spawn_y}) in scene {last_scene_index}")


    #===== PLAYER INITALIZE =====#
    def init_player(self):
        gender = gender_selection_screen()
        
        # Load base sprites
        if gender == 'male':
            base_sprite_image = pygame.image.load(os.path.join(parent_directory, 'PlayerMovement&Physics', 'Sprite_Img', 'male_spriteV8_flipped.png')).convert_alpha()
            attack_sprite_image = pygame.image.load(os.path.join(parent_directory, 'PlayerMovement&Physics', 'Sprite_Img', 'male_sprite_attack.png')).convert_alpha()
            mine_sprite_image = pygame.image.load(os.path.join(parent_directory, 'PlayerMovement&Physics', 'Sprite_Img', 'male_sprite_mine.png')).convert_alpha()
            action_sprite_width, action_sprite_height = 273, 182
            action_scale_factor = 0.3
        else:
            base_sprite_image = pygame.image.load(os.path.join(parent_directory, 'PlayerMovement&Physics', 'Sprite_Img', 'female_spriteV1_flipped.png')).convert_alpha()
            attack_sprite_image = pygame.image.load(os.path.join(parent_directory, 'PlayerMovement&Physics', 'Sprite_Img', 'female_sprite_attack.png')).convert_alpha()
            mine_sprite_image = pygame.image.load(os.path.join(parent_directory, 'PlayerMovement&Physics', 'Sprite_Img', 'female_sprite_attack.png')).convert_alpha()  # Using attack for mine if mine doesn't exist
            action_sprite_width, action_sprite_height = 232, 182
            action_scale_factor = 0.3

        # Load animations
        base_animation_list = load_base_animations(base_sprite_image)
        action_animation_list = load_action_animations(attack_sprite_image, mine_sprite_image, 
                                                     action_sprite_width, action_sprite_height, action_scale_factor)
        
        world_width = (pygame.display.get_surface().get_width() * self.number_levels)
        self.player = Playeronworld(base_animation_list, action_animation_list, gender, self.blocks, self.block_width, self.block_height, world_width)
        
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
        # ==== RESPAWN ENEMIES AND BOSS AFTER WORLD GENERATION ==== #
        self.spawn_enemies()
        self.init_boss_system()

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
                    # ==== ADD DEBUG KEY FOR ENEMY SPAWNING ==== #
                    if event.key == pygame.K_e:  # Press 'E' to manually spawn enemies
                        self.spawn_enemies()
                        print(f"Spawned {len(self.enemy_group)} enemies")
                    
                    if self.player:
                        if event.key == pygame.K_h:
                            self.player.health = min(100, self.player.health+10)
                            last_health_change = current_time
                        if event.key == pygame.K_j:
                            self.player.health = max(0, self.player.health-10)
                            last_health_change = current_time
                        if event.key == pygame.K_UP:  # Updated for PlayerV4 compatibility
                            self.player.get_health(10)
                            last_health_change = current_time
                        if event.key == pygame.K_DOWN:  # Updated for PlayerV4 compatibility
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
                # New PlayerV4 actions
                attack = keys[pygame.K_1]
                mine = keys[pygame.K_2]
                
                # ==== NEW: PLAYER ATTACK ENEMIES ==== #
                if attack and self.player.is_performing_action and self.player.action == ATTACK:
                    # Only attack enemies during attack animation
                    self.player.attack_enemies(self.enemy_group)
                
                self.player.move(left, right, jump, attack, mine)
                self.player.update()

                # ==== NEW: UPDATE BOSS AND FIREBALLS ==== #
                last_scene_index = self.number_levels - 1
                if self.current_scene == last_scene_index:  # Only update boss in its scene
                    if self.boss_group:
                        bosses = self.boss_group.sprites()  # <-- call the function
                        for boss in bosses:
                            boss.update(self.player, self.fireball_group)

                    # Update fireballs (global, as they can cross scenes)
                    for fireball in self.fireball_group:
                        fireball.update(self.player)

                # Remove dead fireballs
                for fireball in self.fireball_group.copy():
                    if not fireball.alive():  # Fireballs self-kill on collision
                        self.fireball_group.remove(fireball)
                
                # ==== NEW: PLAYER ATTACK BOSS/ENEMIES ==== #
                if attack and self.player.is_performing_action and self.player.action == ATTACK:
                    # Existing: self.player.attack_enemies(self.enemy_group)
                    self.player.attack_enemies(self.enemy_group, self.boss_group)  # Updated call


                #=========Cameralogic=======
                screen_width = self.screen.get_width()
                world_width = screen_width * self.number_levels

                # Move to next scene if player crosses right edge
                if self.player.rect.right > (self.current_scene + 1) * screen_width:
                    if self.current_scene < self.number_levels - 1:
                        self.current_scene += 1
                        # Snap player to nearest ground in the new scene
                        new_scene_blocks = [b for b in self.blocks if (self.current_scene * screen_width <= b["rect"].x < (self.current_scene+1)*screen_width)]
                        player_bottom_y = min([b["rect"].top for b in new_scene_blocks if b["rect"].colliderect(self.player.rect.move(0, self.player.vel_y))], default=self.player.rect.bottom)
                        self.player.rect.left = self.current_scene * screen_width + 1
                        self.player.rect.bottom = player_bottom_y

                # Move to previous scene if player crosses left edge
                elif self.player.rect.left < self.current_scene * screen_width:
                    if self.current_scene > 0:
                        self.current_scene -= 1
                        # Snap player to nearest ground in the new scene
                        new_scene_blocks = [b for b in self.blocks if (self.current_scene * screen_width <= b["rect"].x < (self.current_scene+1)*screen_width)]
                        player_bottom_y = min([b["rect"].top for b in new_scene_blocks if b["rect"].colliderect(self.player.rect.move(0, self.player.vel_y))], default=self.player.rect.bottom)
                        self.player.rect.right = self.current_scene * screen_width + screen_width - 1
                        self.player.rect.bottom = player_bottom_y

                # Clamp player position to world bounds
                self.player.rect.left = max(0, self.player.rect.left)
                self.player.rect.right = min(world_width, self.player.rect.right)

                # Camera X offset for drawing
                camera_x = -self.current_scene * screen_width

            self.screen.blit(self.background,(0,0))
            for block in self.blocks:
                block_rect = block["rect"].move(camera_x, 0)
                if block_rect.right < 0 or block_rect.left > screen_width:
                    continue
                self.screen.blit(block["texture"], block_rect)
            
            # ==== NEW: DRAW ENEMIES ==== #
            # Only draw enemies in current scene or adjacent scenes for performance
            current_scene_start = self.current_scene * screen_width
            current_scene_end = (self.current_scene + 1) * screen_width
            
            for enemy in self.enemy_group:
                # Check if enemy is in visible area (current scene +/- some margin)
                if (enemy.rect.right > current_scene_start - 200 and 
                    enemy.rect.left < current_scene_end + 200):
                    enemy.draw(self.screen, camera_x)

            # ==== NEW: DRAW BOSS AND FIREBALLS ==== #
            if self.current_scene == last_scene_index or abs(self.current_scene - last_scene_index) <= 1:  # Visible in adjacent scenes
                # Draw boss
                for boss in self.boss_group:
                    boss.draw(self.screen, camera_x)
    
                # Draw fireballs (with camera)
                for fireball in self.fireball_group:
                    # Only draw if in visible area
                    if (fireball.rect.right > current_scene_start - 200 and 
                        fireball.rect.left < current_scene_end + 200):
                        fireball.draw(self.screen, camera_x)

            

            
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
            
            # ==== DEBUG INFO ==== #
            # Display enemy count for debugging
            if len(self.enemy_group) > 0:
                debug_text = self.font.render(f"Enemies: {len(self.enemy_group)}", True, (255, 255, 255))
                self.screen.blit(debug_text, (10, 10))
            
            pygame.display.flip()
            self.clock.tick(60)
        return "pause"


if __name__ == "__main__":
    generateworld().run()