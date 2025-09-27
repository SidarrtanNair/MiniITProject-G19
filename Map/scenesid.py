import pygame , random , time , sys , os 
from opensimplex import *

current_directory = os.path.dirname(os.path.abspath(__file__))
parent_directory = os.path.dirname(current_directory)
player_directory = os.path.join(parent_directory, 'PlayerMovementPhysics')
sys.path.append(player_directory)

from PlayerV4 import Player, load_base_animations, load_action_animations, gender_selection_screen, main
from PlayerV4 import IDLE, WALK, JUMP, ATTACK, MINE, SCALE
from Enemy import Enemy
from Boss import Boss
from spritesheet import SpriteSheet

# ======== ENEMY ======== #
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
        self.attack_cooldown = 2500  # 1.5 seconds between attacks (reduced for more responsive feel)
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
        # Find the highest (smallest top y) surface block (grass or magma_block) nearby
        ground_y = self.rect.y + (self.block_height * 10)  # Safer fallback: ~10 blocks below initial y (~320px)
        
        # Widen search to 5 blocks radius for better detection in varied terrain
        search_radius = self.block_width * 5
        for block in self.blocks:
            if (block["type"] in ["grass", "magma_block"] and 
                abs(block["rect"].centerx - self.rect.centerx) < search_radius):
                # No need for block.top > self.rect.y - we want the highest surface regardless
                ground_y = min(ground_y, block["rect"].top)
        
        # If no surface found (very rare), fallback to estimated screen midpoint
        if ground_y > self.rect.y + (self.block_height * 20):  # If fallback didn't change much
            screen_height = 720  # Approximate; adjust if your display is different (or pass as param)
            ground_y = screen_height // 2  # Safe high position to fall from
        
        # Position above the ground
        self.rect.bottom = ground_y - 50  # Reduced offset to -50px (less fall distance, safer)
        self.on_ground = False
        self.vel_y = 0
        
        # NEW: Anti-overlap safety - lift up if currently overlapping any solid block
        while self.check_collision(0, 0):
            self.rect.y -= 5  # Move up 5px at a time until clear
            if self.rect.top < 0:  # Prevent going off-screen top
                self.rect.top = 0
                break

    def check_collision(self, dx, dy):
        temp_rect = self.rect.copy()
        temp_rect.x += dx
        temp_rect.y += dy
        for block in self.blocks:
            if block["type"] in ["bush", "tree_stump", "tree_log", "tree_top", "fire_block"]:
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
                player.hit_flash = pygame.time.get_ticks()
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

#========== BOSS ==========#
boss_animation_config = {
    'idle': {'file': 'Sprite_Img/boss_idle.png', 'frames': 7, 'width': 128, 'height': 128},
    'dead': {'file': 'Sprite_Img/boss_dead.png', 'frames': 6, 'width': 128, 'height': 128},
    'attack1': {'file': 'Sprite_Img/boss_attack1.png', 'frames': 8, 'width': 128, 'height': 128},
    'attack2': {'file': 'Sprite_Img/boss_attack2.png', 'frames': 4, 'width': 128, 'height': 128},
    'fireball': {'file': 'Sprite_Img/boss_fireball.png', 'frames': 6, 'width': 64, 'height': 64},
    'run': {'file': 'Sprite_Img/boss_run.png', 'frames': 8, 'width': 128, 'height': 128},
    'jump': {'file': 'Sprite_Img/boss_jump.png', 'frames': 9, 'width': 128, 'height': 128}
}

def load_boss_animations(scale=2):
    boss_animations = {}
    sprite_img_dir = os.path.join(parent_directory, 'PlayerMovementPhysics' )
    
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
        self.animation_cooldown = 150  # ms per frame
        self.facing_right = False  # False = face left (toward player, negative x)
        # Define which animations loop (idle, run, jump should loop; attacks/dead don't)
        self.looping_animations = {'idle', 'run', 'jump'}

    def update(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.update_time > self.animation_cooldown:
            self.update_time = current_time
            max_frames = len(self.animations[self.current_animation])
            self.current_frame += 1
            if self.current_frame >= max_frames:
                if self.current_animation in self.looping_animations:
                    self.current_frame = 0  # Loop back to start
                else:
                    self.current_frame = max_frames - 1  # Stay on last frame (e.g., for dead/attack end)
        # Return True if at end (for non-looping anims)
        return self.current_frame >= len(self.animations[self.current_animation]) - 1

    def set_animation(self, animation_name, loop=True):
        if animation_name in self.animations and animation_name != self.current_animation:
            self.current_animation = animation_name
            self.current_frame = 0
            self.update_time = pygame.time.get_ticks()
            # Override loop if specified in config (but for simplicity, use class default)
            if animation_name in ['attack1', 'attack2']:
                loop = False  # Override for melee/ranged

    def reset_to_idle(self):
        self.set_animation('idle')

    def get_current_image(self):
        frame = self.animations[self.current_animation][self.current_frame]
        if not self.facing_right:  # Face left by default (negative x)
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
        self.damage = 3  # Damage to player on hit
    
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
            if block["type"] not in ["bush", "tree_stump", "tree_log", "tree_top", "fire_block"] and self.rect.colliderect(block["rect"]):
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

        # Physics: Lock to stationary (no movement or jumping)
        self.vel_y = 0  # Start with 0, no gravity/jumping
        self.gravity = 0.8  # Unused now, but keep for consistency
        self.jump_speed = -18  # Unused now
        self.on_ground = False  # Will be set True after find_ground

        # Combat (unchanged)
        self.health = 500
        self.max_health = 500
        self.attack_damage = 15
        self.attack_cooldown = 1000  # 1s between attacks
        self.last_attack = 0
        self.is_dead = False
        self.fireball_cooldown = 0
        self.fireball_cd_time = 3000  # 3s between fireballs

        # AI States: Simplified (no chase/jumping)
        self.state = 'idle'  
        self.last_state_change = 0
        self.state_change_cooldown = 500  # For attack triggers

        # World (unchanged, but bounds unused now)
        self.blocks = blocks
        self.block_width = block_width
        self.block_height = block_height
        self.world_width = world_width

        # Masks (unchanged)
        self.masks = {}
        for anim_name, frames in animations.items():
            if anim_name != 'fireball':
                self.masks[anim_name] = [pygame.mask.from_surface(f) for f in frames]
        self.current_mask = self.masks['idle'][0]

        self.find_ground()
        # CHANGE: Lock position after finding ground—no more physics
        self.vel_y = 0
        self.on_ground = True  # Stationary on ground forever

    def find_ground(self):
        # Unchanged: Find ground and set position
        ground_y = self.rect.y + 500
        for block in self.blocks:
            if (block["type"] in ["grass", "magma_block"] and
                abs(block["rect"].centerx - self.rect.centerx) < self.block_width * 10):
                if block["rect"].top > self.rect.y:
                    ground_y = min(ground_y, block["rect"].top)
        self.rect.bottom = ground_y - 1  # On ground
        # No vel_y or on_ground changes here—handled in __init__

    def check_collision(self, dx, dy):
        # Unchanged: Used for fireball blocks and melee (though dx/dy=0 for boss now)
        temp_rect = self.rect.copy()
        temp_rect.x += dx
        temp_rect.y += dy
        for block in self.blocks:
            if block["type"] in ["bush", "tree_stump", "tree_log", "tree_top", "fire_block"]:
                continue
            if temp_rect.colliderect(block["rect"]):
                return True
        return False

    def take_damage(self, damage):  # Unchanged
        if not self.is_dead:
            self.health -= damage
            print(f"Boss took {damage} damage. New health: {self.health}/{self.max_health}")
            if self.health <= 0:
                self.health = 0
                self.is_dead = True
                self.animator.set_animation('dead')
                print("Boss defeated!")

    def attack_player(self, player):  # Unchanged
        current_time = pygame.time.get_ticks()
        if current_time - self.last_attack >= self.attack_cooldown and not self.is_dead:
            player.get_damage(self.attack_damage)
            if hasattr(player, 'hit_flash'):
                player.hit_flash = pygame.time.get_ticks()
            self.last_attack = current_time
            print(f"Boss attacked player! Player health: {player.current_health}/{player.maximum_health}")
            return True
        return False

    def shoot_fireball(self, player, fireball_group):
        # Unchanged
        current_time = pygame.time.get_ticks()
        if current_time - self.fireball_cooldown >= self.fireball_cd_time and not self.is_dead:
            # Play attack1 for ranged wind-up
            if self.state != 'ranged':
                self.state = 'ranged'
                self.animator.set_animation('attack1')
            
            fireball_frames = self.animations['fireball']
            fireball = Fireball(
                self.rect.centerx, self.rect.centery,
                player.rect.centerx, fireball_frames,
                self.blocks, self.block_width, self.block_height
            )
            fireball_group.add(fireball)
            self.fireball_cooldown = current_time
            print("Boss shot fireball at 800px range!")
            return True
        return False

    def update(self, player, fireball_group):
        if self.is_dead:
            # Unchanged: Play dead animation
            self.animator.update()
            self.image = self.animator.get_current_image()
            state = self.animator.current_animation
            if state in self.masks:
                self.current_mask = self.masks[state][self.animator.current_frame]
            return

        if not player:
            return

        # Update animation (unchanged)
        anim_finished = self.animator.update()
        self.image = self.animator.get_current_image()
        state = self.animator.current_animation
        if state in self.masks:
            self.current_mask = self.masks[state][self.animator.current_frame % len(self.masks[state])]

        dist_x = abs(player.rect.centerx - self.rect.centerx)
        dist_y = abs(player.rect.centery - self.rect.centery)
        current_time = pygame.time.get_ticks()

        # CHANGE: Early melee collision check (triggers on overlap, no movement)
        if player and self.rect.colliderect(player.rect):
            offset_x = player.rect.x - self.rect.x
            offset_y = player.rect.y - self.rect.y
            if (hasattr(player, 'mask') and player.mask and 
                self.current_mask.overlap(player.mask, (offset_x, offset_y))):
                # Collision: Force melee state
                if self.state != 'melee':
                    self.state = 'melee'
                    self.animator.set_animation('attack2')
                    self.last_state_change = current_time
                self.attack_player(player)  # Deal damage
                print("Boss melee collision! Attack2 triggered.")
            # Update anim/mask again for melee (in case it changed)
            anim_finished = self.animator.update()
            self.image = self.animator.get_current_image()
            state = self.animator.current_animation
            if state in self.masks:
                self.current_mask = self.masks[state][self.animator.current_frame % len(self.masks[state])]
            # Reset after melee finishes
            if anim_finished and self.state == 'melee':
                self.state = 'idle'
                self.animator.reset_to_idle()
            return  # Exit early—melee handled

        # CHANGE: Simplified AI State Machine (no chase/jumping, only ranged or idle)
        # Only change state if cooldown allows and not in attack
        if (current_time - self.last_state_change >= self.state_change_cooldown and 
            self.state not in ['melee', 'ranged']):
            if dist_x > 800:  # Too far: Idle
                self.state = 'idle'
                self.animator.reset_to_idle()
            elif 400 < dist_x <= 800:  # Ranged: Fireball + attack1
                self.state = 'ranged'
                self.animator.set_animation('attack1')
                self.shoot_fireball(player, fireball_group)  # Triggers at ~800px
                # Face player during ranged
                self.animator.facing_right = player.rect.centerx > self.rect.centerx
            else:  # Close but no overlap: Idle (no chase)
                self.state = 'idle'
                self.animator.reset_to_idle()
            self.last_state_change = current_time

        # CHANGE: Handle non-looping anim finishes (reset to idle after ranged)
        if anim_finished and self.state == 'ranged':
            self.state = 'idle'
            self.animator.reset_to_idle()

        # CHANGE: NO PHYSICS OR MOVEMENT (removed gravity, vel_y, rect.x/y updates, bounds)

    # draw_health_bar and draw methods unchanged...
    def draw_health_bar(self, surf, camera_x):
        if self.is_dead:
            return
        
        bar_width = 100  
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
        # Always draw the current image (including dead animation)
        surf.blit(self.image, self.rect.move(camera_x, 0))
        
        # Only draw health bar if not dead
        if not self.is_dead:
            self.draw_health_bar(surf, camera_x)



# =====PLAYER================================================================================================================= #
class Playeronworld(Player): #1
    def __init__(self, base_animation_list, action_animation_list, gender, blocks, block_width, block_height, world_width, parent):
        super().__init__(base_animation_list, action_animation_list, gender)
        self.blocks = blocks
        self.block_width = block_width
        self.block_height = block_height
        self.world_width = world_width
        self.parent = parent
        self.was_in_air = True
        self.last_step_time = 0
        self.current_health = 100
        self.maximum_health = 100
        self.mask = None
        self.hit_flash = 0
        self.hitbox = self.rect.inflate(-60, -10)
    #======DamageLogic============#   
    def get_damage(self, amt):
        super().get_damage(amt)
    #========HealthLogic===========#
    def get_health(self, amt):
        super().get_health(amt)
    
    @property
    def health(self):
        return self.current_health
    @health.setter 
    def health(self, value):
        self.current_health = max(0, min(self.maximum_health, value))
    #======CollisionCheck=============#
    def check_collision(self, dx, dy):
        temp_hitbox = self.hitbox.copy()
        temp_hitbox.x += dx
        temp_hitbox.y += dy
        for block in self.blocks:
            if block["type"] in ["bush", "tree_stump", "tree_log", "tree_top", "fire_block"]:
                continue
            if temp_hitbox.colliderect(block["rect"]):
                return True
        return False
    
    # ==== NEW ENEMY ATTACK METHOD ==== #
    def attack_enemies(self, enemy_group, boss_group=None):
        attack_range = 60  # Pixels
        boss_attack_range = 150
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
        if boss_group and not attacked:  # Only attack boss if no enemy was attacked
            boss_list = boss_group.sprites()
            if boss_list:
                boss = boss_list[0]
                if boss and not boss.is_dead:
                    dx = boss.rect.centerx - self.rect.centerx
                    dy = boss.rect.centery - self.rect.centery
                    distance = (dx**2 + dy**2)**0.5
                    if distance <= boss_attack_range:
                        # Deal 10% of boss max health (500 * 0.1 = 50 damage)
                        # Change to 500 for 100% damage (instant kill)
                        boss.take_damage(100)  # 10% damage
                        attacked = True
                        print(f"Player attacked boss! Boss health: {boss.health}/{boss.max_health}")

        return attacked

    #=============ConstantSids========================#
    def update(self):
        current_time = pygame.time.get_ticks()
        
        if self.is_performing_action:
            if current_time - self.action_start_time >= self.action_duration:
                self.is_performing_action = False
                self.action = IDLE
                self.frame = 0

        # Animation update
        if current_time - self.last_update >= self.animation_cooldown:
            self.frame += 1
            self.last_update = current_time
            if self.frame >= self.get_animation_length():
                if self.is_performing_action:
                    self.is_performing_action = False
                    self.action = IDLE
                self.frame = 0

        self.image = self.scale_current_image()
        if self.flip:
            self.image = pygame.transform.flip(self.image, True, False)
        
        self.mask = pygame.mask.from_surface(self.image)

        if not self.is_performing_action:
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

            self.hitbox.center = self.rect.center
            self.hitbox = self.rect.inflate(-60, -10)

    # === sounds ===
        if self.vel_x != 0 and not self.in_air:
            if current_time - self.last_step_time > 300:  
                pygame.mixer.Channel(1).play(self.parent.sounds["footstep"])
                self.last_step_time = current_time

        if self.vel_y < 0 and not self.jump_played:
            self.parent.sounds["jump"].play()
            self.jump_played = True

        if not self.in_air:
            self.jump_played = False

    #=============Scenecam===============#
    def draw(self, surf, camera_x):
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
        #===========INIT=============#
        self.background = pygame.image.load("Map\\BACKGROUND\\sforest.png").convert()
        self.background = pygame.transform.scale(self.background, self.screen.get_size())
        # === UI assets ===
        self.hotbar_image= pygame.image.load("Map\\UI+LOGO\\hotbar_9slots.png").convert_alpha()

        self.inventory_bg = pygame.image.load("Map\\UI+LOGO\\inventory.png").convert_alpha()


        self.show_fullmap = False
        self.fullmap_scale = 0.1  #(will try 0.2, might be too big)
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
            'stone_bricks': pygame.transform.scale(
                pygame.image.load("Map\\BLOCK\\stone_brick_block.png").convert_alpha(), (32,32)),
            'bush': pygame.transform.scale(
                pygame.image.load("Map\\BLOCK\\grass_resize.png").convert_alpha(), (32, 32)),
            'biggerbush':pygame.transform.scale(
                pygame.image.load("Map\\BLOCK\\shrub.png").convert_alpha(), (32,32)),
            'tree_stump': pygame.transform.scale(
                pygame.image.load("Map\\BLOCK\\tree_wood_stump.png").convert_alpha(), (32, 32)),
            'tree_log': pygame.transform.scale(
                pygame.image.load("Map\\BLOCK\\tree_wood.png").convert_alpha(), (32, 32)),
            'tree_top': pygame.transform.scale(
                pygame.image.load("Map\\BLOCK\\tree_middlemiddle.png").convert_alpha(),(32,32)),
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
                pygame.image.load('Map\\BLOCK\\NEXT DIMENSION\\fire_block.png').convert_alpha(),(32,32)),
            'pickaxe' : pygame.transform.scale(
                pygame.image.load('Map\\BLOCK\\HOTBAR ITEMS\\aetherium_pickaxe_hotbar.png').convert_alpha(),(32,32)),
            'sword' : pygame.transform.scale(
                pygame.image.load('Map\\BLOCK\\HOTBAR ITEMS\\aetherium_sword_hotbar.png').convert_alpha(),(32,32)),
        }
        self.blocks = [] 
          #==========size=========#
        self.block_width = self.blocklibrary['dirt'].get_width()
        self.block_height = self.blocklibrary['dirt'].get_height()
        #levelcountar
        self.seed = None
        self.set_seed()
        self.number_levels = 5
        self.gen_world(number_levels=self.number_levels)

        self.init_player()
        self.current_scene = 0  
        self.highlight = False
        
        self.pause_callback = pause_callback

        #Health bar tracking for player (initialize after player creation)
        self.health_display_time = 3000  # 3 seconds in ms
        self.last_health_change = 0      # Timer start (0 means no recent damage)
        self.prev_player_health = self.player.current_health if self.player else 100  # Track previous health

        self.current_scene = 0  
        self.previous_scene = 0
        self.highlight = False
        
        self.pause_callback = pause_callback

        # =====Inventory/Hotbar Setup========= #
        self.hotbar_slots = [
            (None, 0),
            (None, 0),
            (None, 0),
            (None, 0),
            (None, 0),
            (None, 0),
            (None, 0),
            (None, 0),
            (None, 0),
        ]
        #Numberofblockstxt#
        self.hotbar_slot_size = 40
        self.hotbar_padding = 6
        self.font = pygame.font.SysFont(None, 20)
        

        #==========================Inventory n Hotbar Dragging=======================#
        self.dragging_item = None
        self.dragging_item_image = None
        self.dragging_index = None
        
        self.show_inventory = False
        self.inventory_cols = 9
        self.inventory_rows = 4
        self.inventory_slot_size = 48
        self.inventory_padding = 8
        self.inventory_surface = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
        
        self.inventory_slots = [None] * (self.inventory_cols * self.inventory_rows)

        self.dragging_item = None
        self.dragging_slot = None
  
        self.selected_index = 2 
        self.init_enemy_system()
        self.boss_group = pygame.sprite.Group()  
        self.fireball_group = pygame.sprite.Group()  
        # ===== Crafting System ===== #
        self.show_crafting = False
        self.recipes = {
            "wood_planks": {"tree_log": 1},
            "pickaxe": {"aetherium":3 , "wood_planks":1 },
            "stone_bricks": {"stone":1},
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
        self.current_music = "overworld"
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
    def update_music(self):
        """Update background music based on dimension and current scene."""
        current_time = pygame.time.get_ticks()  # Not strictly needed, but for future expansions
        
        # Boss music condition: Hell dimension AND last scene (boss area)
        if self.dimension == "hell" and self.current_scene == self.number_levels - 1:
            if self.current_music != "boss":
                pygame.mixer.music.stop()  # Stop current music
                pygame.mixer.music.load("Map\\MusicMan\\EpicBossFight.mp3")
                pygame.mixer.music.set_volume(self.volume)
                pygame.mixer.music.play(-1)  # Loop indefinitely
                self.current_music = "boss"
                print("Switched to Epic Boss Fight music!")  # Optional: For debugging
        else:
            # Default to overworld music (for overworld or non-boss hell scenes)
            if self.current_music != "overworld":
                pygame.mixer.music.stop()  # Stop current music
                pygame.mixer.music.load("Map\\MusicMan\\worldbackground.mp3")
                pygame.mixer.music.set_volume(self.volume)
                pygame.mixer.music.play(-1)
                self.current_music = "overworld"
                print("Switched back to overworld music!")  # Optional: For debugging


    # ==== ENEMY INITIALIZATION ==== #
    def show_dialogue(self, text, portrait_img=None, text_sound = None):
        pygame.mixer.music.stop()
        font = pygame.font.SysFont("Consolas", 24)
        line_spacing = 30
        text_color = (255, 255, 255)
        type_speed = 40

        portrait_offset_x = 0
        if portrait_img:
            max_height = 100
            scale = min(max_height / portrait_img.get_height(), 1)
            portrait_img = pygame.transform.smoothscale(
                portrait_img,
                (int(portrait_img.get_width() * scale), int(portrait_img.get_height() * scale))
            )
            portrait_offset_x = portrait_img.get_width() + 10

        rendered_text = [char for char in text]
        current_index = 0
        last_update = pygame.time.get_ticks()
        waiting_for_click = True

        box_width = 500
        box_height = 100
        box_x = (self.screen.get_width() - box_width) // 2
        box_y = self.screen.get_height() - box_height - 20

        while waiting_for_click:
            
            box_surf = pygame.Surface((box_width, box_height), pygame.SRCALPHA)
            box_surf.fill((0, 0, 0, 200))
            pygame.draw.rect(box_surf, (255, 255, 255), box_surf.get_rect(), 2)
            self.screen.blit(box_surf, (box_x, box_y))

            if portrait_img:
                self.screen.blit(portrait_img, (box_x + 10, box_y + box_height - portrait_img.get_height() - 10))

            now = pygame.time.get_ticks()
            if current_index < len(rendered_text) and now - last_update > type_speed:
                current_index += 1
                last_update = now

            words = "".join(rendered_text[:current_index]).split(" ")
            lines = []
            line = ""
            for word in words:
                test_line = line + word + " "
                if font.size(test_line)[0] > box_width - portrait_offset_x - 20:
                    lines.append(line)
                    line = word + " "
                else:
                    line = test_line
            lines.append(line)

            for i, line in enumerate(lines):
                text_surf = font.render(line, True, text_color)
                self.screen.blit(text_surf, (box_x + portrait_offset_x + 10, box_y + 10 + i * line_spacing))

            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN or (event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE):
                    if current_index >= len(rendered_text):
                        waiting_for_click = False
                    else:
                        current_index = len(rendered_text)

            self.clock.tick(60)
    def init_enemy_system(self):
        """Initialize enemy sprite sheet and enemy groups"""
        try:
            enemy_sheet_img = pygame.image.load("PlayerMovementPhysics/Sprite_Img/enemy_sprite.png").convert_alpha()
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
            num_enemies = random.randint(2, 3)  # 2-3 enemies per scene
            
            for _ in range(num_enemies):
                # Random x position within the scene
                x = random.randint(scene * screen_width + 100, (scene + 1) * screen_width - 100)
                
                # Find grass blocks in this scene to determine spawn height
                scene_grass_blocks = []
                for block in self.blocks:
                    if (block["type"] in ["grass", "magma_block"] and
                        scene * screen_width <= block["rect"].centerx < (scene + 1) * screen_width):
                        scene_grass_blocks.append(block)
                
                if scene_grass_blocks:
                    # Find the grass block closest to our spawn x position
                    closest_grass = min(scene_grass_blocks, 
                                      key=lambda b: abs(b["rect"].centerx - x))
                    y = closest_grass["rect"].top - 500  # Start 200 pixels above grass
                else:
                    # Fallback if no grass blocks found
                    y = 100
                
                # Create enemy
                enemy = Enemy(x, y, self.enemy_sheet, 2, self.blocks, 
                             self.block_width, self.block_height)
                self.enemy_group.add(enemy)

    #===== BOSS INITIALIZE =====#
    def init_boss_system(self, hell_mode=False):
        """Initialize boss animations and spawn the boss in the last scene (hell only)."""
        # Load boss animations once (scale=2 for visibility)
        self.boss_animations = load_boss_animations(scale=2)

        # Clear any existing boss/fireballs
        self.boss_group.empty()
        self.fireball_group.empty()

        # Spawn boss only if in hell and world is generated
        if hell_mode and len(self.blocks) > 0:
            self.spawn_boss(hell_mode=True)


    def spawn_boss(self, hell_mode=False):
        """Spawn the boss in the last scene, at the far right (hell only)."""
        if not hell_mode:
            return  # Only spawn in hell

        screen_width = self.screen.get_width()
        last_scene_index = self.number_levels - 1
        scene_start_x = last_scene_index * screen_width

        # Boss spawn x: Far right of last scene (100px margin from edge)
        boss_width = 128 * 2  # Scaled width from animations (128px * scale=2)
        spawn_x = scene_start_x + screen_width - boss_width - 100  # Most right side

        # Initial y: High up, will fall to ground via find_ground()
        spawn_y = 200  # Arbitrary high position to trigger gravity drop

        # Create boss with world data
        world_width = screen_width * self.number_levels
        boss = Boss(
            spawn_x, spawn_y,
            self.boss_animations,  # Loaded animations
            self.blocks, self.block_width, self.block_height,
            world_width  # For bounds checking
        )
        self.boss_group.add(boss)

        print(f"Boss spawned at ({spawn_x}, {spawn_y}) in last hell scene {last_scene_index}")


    def init_player(self):
        gender = gender_selection_screen()
        # Load base sprites
        if gender == 'male':
            base_sprite_image = pygame.image.load(os.path.join(parent_directory, 'PlayerMovementPhysics', 'Sprite_Img', 'male_spriteV8_flipped.png')).convert_alpha()
            attack_sprite_image = pygame.image.load(os.path.join(parent_directory, 'PlayerMovementPhysics', 'Sprite_Img', 'male_sprite_attack.png')).convert_alpha()
            mine_sprite_image = pygame.image.load(os.path.join(parent_directory, 'PlayerMovementPhysics', 'Sprite_Img', 'male_sprite_mine.png')).convert_alpha()
            action_sprite_width, action_sprite_height = 273, 182
            action_scale_factor = 0.3
        else:
            base_sprite_image = pygame.image.load(os.path.join(parent_directory, 'PlayerMovementPhysics', 'Sprite_Img', 'female_spriteV1_flipped.png')).convert_alpha()
            attack_sprite_image = pygame.image.load(os.path.join(parent_directory, 'PlayerMovementPhysics', 'Sprite_Img', 'female_sprite_attack.png')).convert_alpha()
            mine_sprite_image = pygame.image.load(os.path.join(parent_directory, 'PlayerMovementPhysics', 'Sprite_Img', 'female_sprite_attack.png')).convert_alpha()  # Using attack for mine if mine doesn't exist
            action_sprite_width, action_sprite_height = 232, 182
            action_scale_factor = 0.3
        # Load animations
        base_animation_list = load_base_animations(base_sprite_image)
        action_animation_list = load_action_animations(attack_sprite_image, mine_sprite_image, 
                                                     action_sprite_width, action_sprite_height, action_scale_factor)
        
        world_width = (pygame.display.get_surface().get_width() * self.number_levels)
        self.player = Playeronworld(base_animation_list, action_animation_list, gender, self.blocks, self.block_width, self.block_height, world_width,self)
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
        colums = screen_width // self.block_width
        rows = screen_height // self.block_height

        for level in range(number_levels):
            for x in range(colums):
                noise_value = noise.noise2((x + level * colums) * 0.1, 0)
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
                        if random.random() < 0.01 :
                            blocktype = "aetherium"
                        else:
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

                    rect = texture.get_rect(topleft=((x + level * colums) * self.block_width, y_px))
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
        colums = screen_width // self.block_width
        rows = screen_height // self.block_height

        # Hell background
        self.background = pygame.image.load("Map\\BACKGROUND\\hellgame1.gif").convert()
        self.background = pygame.transform.scale(self.background, self.screen.get_size())

        for level in range(number_levels):
            for x in range(colums):
                noise_value = noise.noise2((x + level * colums) * 0.1, 0)
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

                    rect = texture.get_rect(topleft=((x + level * colums) * self.block_width, y_px))
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

    def add_to_inventory(self, bloktype, amount=1):
    # Try stacking in inventory
        for i, slot in enumerate(self.inventory_slots):
            if slot and slot[0] == bloktype:
                self.inventory_slots[i] = (bloktype, slot[1] + amount)
                self.update_hotbar()
                return

        # If not found, put in first empty slot
        for i, slot in enumerate(self.inventory_slots):
            if slot is None:
                self.inventory_slots[i] = (bloktype, amount)
                self.update_hotbar()
                return

    def add_to_hotbar(self, block_type):
        for i, (item, count) in enumerate(self.hotbar_slots):
            if item == block_type:
                self.hotbar_slots[i] = (item, count + 1)
                return
        # Add to empty slot
        for i, (item, count) in enumerate(self.hotbar_slots):
            if item is None:
                self.hotbar_slots[i] = (block_type, 1)
                return
    def consume_from_hotbar(self, item, amount):
        remaining = amount
        for i in range(len(self.hotbar_slots)):
            if remaining <= 0:
                break
            slot_type, slot_count = self.hotbar_slots[i]
            if slot_type == item and slot_count > 0:
                take = min(slot_count, remaining)
                slot_count -= take
                remaining -= take
                if slot_count <= 0:
                    self.hotbar_slots[i] = (None, 0)
                else:
                    self.hotbar_slots[i] = (slot_type, slot_count)
        consumed = amount - remaining
        return consumed

                
    # ===== Inventory/Hotbar Drawing =====
    def draw_inventory(self):
        inv_width = self.inventory_cols * self.inventory_slot_size + (self.inventory_cols - 1) * self.inventory_padding
        inv_height = self.inventory_rows * self.inventory_slot_size + (self.inventory_rows - 1) * self.inventory_padding
        inv_x = (self.screen.get_width() - inv_width) // 2
        inv_y = (self.screen.get_height() - inv_height) // 2
        invbackground = pygame.transform.scale(self.inventory_bg,(inv_width,inv_height))
        self.screen.blit(invbackground,(inv_x,inv_y))

        for row in range(self.inventory_rows):
            for col in range(self.inventory_cols):
                index = row * self.inventory_cols + col
                slot = self.inventory_slots[index]
                slot_rect = pygame.Rect(
                    inv_x + col * (self.inventory_slot_size + self.inventory_padding),
                    inv_y + row * (self.inventory_slot_size + self.inventory_padding),
                    self.inventory_slot_size,
                    self.inventory_slot_size
                )
                pygame.draw.rect(self.screen, (50,50,50), slot_rect)
                pygame.draw.rect(self.screen, (0,0,0), slot_rect, 2)

                if slot:
                    item_name, count = slot
                    if item_name in self.blocklibrary:
                        icon = pygame.transform.scale(self.blocklibrary[item_name], (self.inventory_slot_size-8, self.inventory_slot_size-8))
                        icon_rect = icon.get_rect(center=slot_rect.center)
                        self.screen.blit(icon, icon_rect)
                        count_surf = self.font.render(str(count), True, (255,255,255))
                        count_rect = count_surf.get_rect(bottomright=(slot_rect.right-4, slot_rect.bottom-4))
                        self.screen.blit(count_surf, count_rect)

          
                if self.dragging_slot == index and self.dragging_item:
                    item_name, count = self.dragging_item
                    icon = pygame.transform.scale(self.blocklibrary[item_name], (self.inventory_slot_size-8, self.inventory_slot_size-8))
                    mx, my = pygame.mouse.get_pos()
                    icon_rect = icon.get_rect(center=(mx, my))
                    self.screen.blit(icon, icon_rect)
    



    def draw_hotbar(self, screen, selected_index):
        hotbar_slots = self.hotbar_slots
        
    
        original_width = self.hotbar_image.get_width()
        original_height = self.hotbar_image.get_height()
        scale_factor = 0.2  
        hotbar_width = int(original_width * scale_factor)
        hotbar_height = int(original_height * scale_factor)
        hotbar_x = (screen.get_width() - hotbar_width) // 2
        hotbar_y = screen.get_height() - hotbar_height - 10
        scaled_hotbar = pygame.transform.scale(self.hotbar_image, (hotbar_width, hotbar_height))
        screen.blit(scaled_hotbar, (hotbar_x, hotbar_y))
        
        total_slots = 9
        slot_width = hotbar_width // total_slots
        slot_height = hotbar_height
        
      
        for i, (item, count) in enumerate(hotbar_slots[:9]):

            slot_x = hotbar_x + (i * slot_width)
            slot_y = hotbar_y
            
            slot_rect = pygame.Rect(slot_x, slot_y, slot_width, slot_height)
            
            if i == selected_index:
                highlight_rect = pygame.Rect(slot_x + 2, slot_y + 2, slot_width - 4, slot_height - 4)
                pygame.draw.rect(screen, (255, 215, 0, 100), highlight_rect, 3)
            
            if item and item in self.blocklibrary:
                icon_size = min(slot_width - 12, slot_height - 12)
                icon = pygame.transform.scale(self.blocklibrary[item], (icon_size, icon_size))
                icon_rect = icon.get_rect(center=slot_rect.center)
                screen.blit(icon, icon_rect)
                
                if count > 1:
                    count_surf = self.font.render(str(count), True, (255, 255, 255))
                    count_rect = count_surf.get_rect(bottomright=(slot_rect.right - 4, slot_rect.bottom - 4))
                    outline_surf = self.font.render(str(count), True, (0, 0, 0))
                    for dx, dy in [(-1, -1), (-1, 1), (1, -1), (1, 1)]:
                        screen.blit(outline_surf, (count_rect.x + dx, count_rect.y + dy))
                    screen.blit(count_surf, count_rect)

    # ===== Inventory Drag & Drop =====
    def handle_inventory_click(self):
        mx, my = pygame.mouse.get_pos()
        mouse_pressed = pygame.mouse.get_pressed()
        
        inv_width = self.inventory_cols * self.inventory_slot_size + (self.inventory_cols - 1) * self.inventory_padding
        inv_height = self.inventory_rows * self.inventory_slot_size + (self.inventory_rows - 1) * self.inventory_padding
        inv_x = (self.screen.get_width() - inv_width) // 2
        inv_y = (self.screen.get_height() - inv_height) // 2

        # ===== Start dragging =====
        if mouse_pressed[0] and not self.dragging_item:
            for row in range(self.inventory_rows):
                for col in range(self.inventory_cols):
                    index = row * self.inventory_cols + col
                    slot_rect = pygame.Rect(
                        inv_x + col * (self.inventory_slot_size + self.inventory_padding),
                        inv_y + row * (self.inventory_slot_size + self.inventory_padding),
                        self.inventory_slot_size,
                        self.inventory_slot_size
                    )
                    if slot_rect.collidepoint(mx, my) and self.inventory_slots[index]:
                        self.dragging_item = self.inventory_slots[index] 
                        self.dragging_slot = index
                        self.dragging_row = row
                        self.dragging_col = col
                        self.inventory_slots[index] = None  
                        return

        # ===== Drop item =====
        if not mouse_pressed[0] and self.dragging_item is not None:
            for row in range(self.inventory_rows):
                for col in range(self.inventory_cols):
                    index = row * self.inventory_cols + col
                    slot_rect = pygame.Rect(
                        inv_x + col * (self.inventory_slot_size + self.inventory_padding),
                        inv_y + row * (self.inventory_slot_size + self.inventory_padding),
                        self.inventory_slot_size,
                        self.inventory_slot_size
                    )
                    if slot_rect.collidepoint(mx, my):
                        dest_item = self.inventory_slots[index]
                        src_item = self.dragging_item

                        
                        if dest_item is None:
                            self.inventory_slots[index] = src_item
                            self.dragging_item = None

                       
                        elif dest_item[0] == src_item[0]:
                            MAX_STACK = 64
                            new_count = dest_item[1] + src_item[1]
                            if new_count <= MAX_STACK:
                                self.inventory_slots[index] = (dest_item[0], new_count)
                                self.dragging_item = None
                            else:
                                self.inventory_slots[index] = (dest_item[0], MAX_STACK)
                                self.dragging_item = (dest_item[0], new_count - MAX_STACK)

                       
                        else:
                            self.inventory_slots[index] = src_item
                            self.dragging_item = dest_item

                        if row == 0:
                            slot = self.inventory_slots[index]
                            self.hotbar_slots[col] = slot if slot else (None, 0)

                        if self.dragging_row == 0:
                            sidx = self.dragging_slot
                            scol = self.dragging_col
                            slot = self.inventory_slots[sidx]
                            self.hotbar_slots[scol] = slot if slot else (None, 0)

                    
                        if self.dragging_item is None:
                            self.dragging_slot = None
                            self.dragging_row = None
                            self.dragging_col = None
                        return

            # ===== Dropped outside → return to original slot =====
            self.inventory_slots[self.dragging_slot] = self.dragging_item
            if self.dragging_row == 0:
                scol = self.dragging_col
                slot = self.inventory_slots[self.dragging_slot]
                self.hotbar_slots[scol] = slot if slot else (None, 0)

            self.dragging_item = None
            self.dragging_slot = None
            self.dragging_row = None
            self.dragging_col = None



    # ===== Hotbar Sync =====
    def update_hotbar(self):
        for i in range(9):  # first row of inventory
            slot = self.inventory_slots[i]
            if slot:
                self.hotbar_slots[i] = slot
            else:
                self.hotbar_slots[i] = (None, 0)

                

    def run(self):
        if self.player:
            if self.player.gender == "male":
                portrait_img = pygame.image.load("Map\\Cutscene\\player_profile_m.png").convert_alpha()
            else:
                portrait_img = pygame.image.load("Map\\Cutscene\\player_profile_f.png").convert_alpha()

            self.show_dialogue(
                "Where tf am I, better get back through that portal, I have an assignment to do!",
                portrait_img=portrait_img,
            )
            pygame.mixer.music.load("Map\MusicMan\worldbackground.mp3")
            pygame.mixer.music.set_volume(self.volume)
            pygame.mixer.music.play(-1)
        running = True
        radius = 7 * self.block_width 
        health_display_time = 3000  
        last_health_change = 0  
        screen_width = self.screen.get_width()

        while running:
            current_time = pygame.time.get_ticks()
            camera_x = -(self.current_scene * screen_width)
            self.update_music()
            if self.show_inventory:
                self.handle_inventory_click()
                
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
                                    self.dimension = "hell"
                                    self.current_scene = 0
                                    self.gen_hell(number_levels=self.number_levels)
                                    self.enemy_group.empty()
                                    self.spawn_enemies()
                                    # Move player to hell spawn
                                    self.player.rect.topleft = (self.hell_spawn_x, self.hell_spawn_y)
                                    self.player.vel_x = 0
                                    self.player.vel_y = 0
                                    
                                    self.init_boss_system(hell_mode=True)
                                    self.current_music = "overworld"  
                                    self.player.rect.topleft = (self.hell_spawn_x, self.hell_spawn_y)
                                    self.player.vel_x = 0
                                    self.player.vel_y = 0
                                else:
                                    self.loading_screen("Returning to Overworld...", 1.5)
                                    self.dimension = "overworld"
                                    self.current_scene = 0
                                    self.gen_world(number_levels=self.number_levels)
                                    self.dimension = "overworld"
                                    self.current_scene = 0
                                    self.gen_world(number_levels=self.number_levels)
                                    # Move player to overworld spawn
                                    self.player.rect.topleft = (self.overworld_spawn_x, self.overworld_spawn_y)
                                    self.player.vel_x = 0
                                    self.player.vel_y = 0
                                    self.enemy_group.empty()
                                    self.spawn_enemies()
                                    # NEW: Clear boss when leaving hell
                                    self.boss_group.empty()
                                    self.fireball_group.empty()
                                    self.current_music = "overworld"  # Ensure overworld music plays
                                    # In the update section, after updating fireballs:
                                    for fireball in self.fireball_group.copy():
                                        if not fireball.alive():  # Fireballs self-kill on collision
                                            self.fireball_group.remove(fireball)
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
                    crafted_amount = 1

                    for i in range(self.crafting_visible):
                        if indexs >= len(self.recipes):
                            break

                        crafted_item = list(self.recipes.keys())[indexs]
                        reqs = self.recipes[crafted_item]

                        rect = pygame.Rect(20, start_y + i * 30, 160, 30)

                        if rect.collidepoint(mx, my):
        
                            if all(inventory_counts.get(mat, 0) >= amount for mat, amount in reqs.items()):
                                if crafted_item == "wood_planks":
                                    crafted_amount = 4 
                                elif crafted_item == "stone_bricks":
                                    crafted_amount = 4

                                # consume materials from inventory
                                for mat, amount in reqs.items():
                                    remaining = amount
                                    for idx, slot in enumerate(self.inventory_slots):
                                        if slot and slot[0] == mat:
                                            item_name, count = slot
                                            if count > remaining:
                                                self.inventory_slots[idx] = (item_name, count - remaining)
                                                remaining = 0
                                                break
                                            else:
                                                remaining -= count
                                                self.inventory_slots[idx] = None

                                # add crafted items to inventory
                                self.add_to_inventory(crafted_item, crafted_amount)
                                self.update_hotbar()
                                self.sounds["craft"].play()

                        indexs += 1



                                # add crafted item using your existing system
                        

                                
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
                                        added = False
# Try to find existing slot
                                        for i, slot in enumerate(self.inventory_slots):
                                            if slot and slot[0] == bloktype:
                                                self.inventory_slots[i] = (bloktype, slot[1]+1)
                                                added = True
                                                break
                                        # If not found, add to first empty slot
                                        if not added:
                                            for i, slot in enumerate(self.inventory_slots):
                                                if slot is None:
                                                    self.inventory_slots[i] = (bloktype, 1)
                                                    break
                                        self.update_hotbar()           
                                    
                                            

                                        self.sounds["block_break"].play()

                                        if bloktype =="grass":
                                        
                                            for top in self.blocks[:]:
                                                if top["type"] == "bush" and top["rect"].x == removed_block["rect"].x and top["rect"].bottom == removed_block["rect"].top:
                                                    self.blocks.remove(top)
                                            break
                                    
                                        break  
                            
                            # ===== Right-click block placement =====
                            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
                                mx, my = pygame.mouse.get_pos()
                                world_mouse = (mx - camera_x, my)

                                # Determine the block grid coordinates
                                col = int(world_mouse[0] // self.block_width)
                                row = int((self.screen.get_height() - world_mouse[1]) // self.block_height)
                                y_px = self.screen.get_height() - (row + 1) * self.block_height

                                selected_type, selected_count = self.hotbar_slots[self.selected_index]

                                if selected_type is None or selected_count <= 0:
                                    continue

                        
                                new_block_rect = self.blocklibrary[selected_type].get_rect(topleft=(col * self.block_width, y_px))

                              
                                occupied = any(b["rect"].colliderect(new_block_rect) for b in self.blocks)
                                if new_block_rect.colliderect(self.player.rect) or occupied:
                                    continue

                              
                                self.blocks.append({
                                    "type": selected_type,
                                    "texture": self.blocklibrary[selected_type],
                                    "rect": new_block_rect
                                })
                                self.sounds["block_place"].play()

                                for i, slot in enumerate(self.inventory_slots) :
                                    if slot and slot[0] == selected_type:
                                        new_count = slot[1] - 1
                                        if new_count > 0:
                                            self.inventory_slots[i] = (selected_type,new_count)
                                        else:
                                            self.inventory_slots[i] = None
                                        break
                                self.update_hotbar()
                                
                                new_count = selected_count - 1
                                if new_count > 0:
                                    self.hotbar_slots[self.selected_index] = (selected_type, new_count)
                                else:
                                    self.hotbar_slots[self.selected_index] = (None, 0)

                        if event.type == pygame.MOUSEBUTTONDOWN and event.button ==4:
                            self.selected_index = (self.selected_index -1)
            keys = pygame.key.get_pressed()
            if self.player and not self.show_inventory or self.show_crafting:
                left = keys[pygame.K_a] 
                right = keys[pygame.K_d] 
                jump = keys[pygame.K_SPACE] 
                attack = keys[pygame.K_q]
                mouse_button = pygame.mouse.get_pressed()
                mine = mouse_button[0]
                self.player.move(left, right, jump, attack, mine)
                self.player.update()

                # Update enemies in current and adjacent scenes (for performance)
                screen_width = self.screen.get_width()
                current_scene_start = self.current_scene * screen_width
                current_scene_end = (self.current_scene + 1) * screen_width

                for enemy in self.enemy_group:
                    # Only update if enemy is in/near current scene (avoids updating off-screen enemies)
                    if (enemy.rect.right > current_scene_start - 200 and 
                        enemy.rect.left < current_scene_end + 200):
                        enemy.update(self.player)

                # ==== NEW: UPDATE BOSS AND FIREBALLS ==== #
                last_scene_index = self.number_levels - 1
                if abs(self.current_scene - last_scene_index) <= 1:  # Update in last scene or adjacent
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
                    # Add attack cooldown to prevent spam
                    current_time = pygame.time.get_ticks()
                    if not hasattr(self, 'last_player_attack'):
                        self.last_player_attack = 0
                    
                    if current_time - self.last_player_attack >= 500:  # 0.5 second cooldown
                        attacked = self.player.attack_enemies(self.enemy_group, self.boss_group)
                        if attacked:
                            self.last_player_attack = current_time


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
            # ==== DRAW ENEMIES ==== #
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

            #==================Drawbar==========================#
            # Replace all the hotbar drawing code with just this line:
            self.draw_hotbar(self.screen, self.selected_index)

                #===========Heathdissapearlogic============#
            should_show_health = (
                current_time - self.last_health_change <= self.health_display_time or  # Recent change
                self.player.current_health < self.player.maximum_health  # Not at full health
            )
            
            if should_show_health:
                self.player.draw_health_bar(self.screen, camera_x)
            
            # Always draw the player
            self.player.draw(self.screen, camera_x)

           
            if self.show_crafting:
                panel_width = 300
                panel_height = self.screen.get_height()
                panel = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
                panel.fill((30, 30, 30, 180))
                self.screen.blit(panel, (0, 0))

                # === build inventory counts as a dict ===
                inventory_counts = {}
                for slot in self.inventory_slots:
                    if slot:  # slot = (item, count)
                        item, count = slot
                        inventory_counts[item] = inventory_counts.get(item, 0) + count

                start_y = 40
                indexs = self.crafting_scroll
                slot_height = 36

                for i in range(self.crafting_visible):
                    if indexs >= len(self.recipes):
                        break

                    crafted_item = list(self.recipes.keys())[indexs]
                    reqs = self.recipes[crafted_item]

                    row_y = start_y + i * slot_height
                    x_offset = 20

                    # --- check if player has enough materials ---
                    craftable = True
                    for mat, amount in reqs.items():
                        total = inventory_counts.get(mat, 0)
                        if total < amount:
                            craftable = False
                            break
                    color = (255, 255, 255) if craftable else (150, 50, 50)

                    # --- draw crafted item icon ---
                    if crafted_item in self.blocklibrary:
                        icon = pygame.transform.scale(self.blocklibrary[crafted_item], (32, 32))
                        self.screen.blit(icon, (x_offset, row_y))
                    x_offset += 36

                    # --- draw crafted amount ---
                    crafted_amount = 4 if crafted_item in ["wood_planks", "stone_bricks"] else 1
                    count_surf = self.crafting_font.render(f"x{crafted_amount}", True, color)
                    self.screen.blit(count_surf, (x_offset, row_y + 8))
                    x_offset += 36

                    # --- draw arrow separator ---
                    arrow_surf = self.crafting_font.render("←", True, color)
                    self.screen.blit(arrow_surf, (x_offset, row_y + 8))
                    x_offset += 16

                    # --- draw material icons + counts ---
                    for mat, amount in reqs.items():
                        if mat in self.blocklibrary:
                            mat_icon = pygame.transform.scale(self.blocklibrary[mat], (32, 32))
                            self.screen.blit(mat_icon, (x_offset, row_y))
                        x_offset += 36

                        amount_surf = self.crafting_font.render(f"x{amount}", True, color)
                        self.screen.blit(amount_surf, (x_offset, row_y + 8))
                        x_offset += 36

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