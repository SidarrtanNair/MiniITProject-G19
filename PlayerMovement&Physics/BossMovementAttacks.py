import pygame
import random
import math
import os
import sys

# Assuming the spritesheet module exists in your project
# from spritesheet import SpriteSheet

# Animation configuration for boss
animation_steps = [6, 8, 6]  # idle, walk, jump
SCALE = 3

# Boss states
IDLE = 0
WALK = 1
JUMP = 2

class SpriteSheet:
    """Simple spritesheet loader for the boss animations"""
    def __init__(self, image):
        self.sheet = image
    
    def get_image(self, frame, width, height, scale, colorkey):
        """Extract a single frame from the spritesheet"""
        image = pygame.Surface((width, height)).convert_alpha()
        image.blit(self.sheet, (0, 0), (frame * width, 0, width, height))
        image = pygame.transform.scale(image, (int(width * scale), int(height * scale)))
        image.set_colorkey(colorkey)
        return image

def load_boss_animations(sprite_sheet_image):
    """Load boss animations from sprite sheet"""
    sprite_sheet = SpriteSheet(sprite_sheet_image)
    animation_list = []
    step_counter = 0
    
    for animation_len in animation_steps:
        temp_img_list = []
        for _ in range(animation_len):
            temp_img_list.append(sprite_sheet.get_image(step_counter, 104, 104, 0.3, 'black'))
            step_counter += 1
        animation_list.append(temp_img_list)
    
    return animation_list

class Boss:
    """
    Game Boss class with physics, AI movement, and block detection
    """
    def __init__(self, animation_list, blocks, block_width, block_height, spawn_x, spawn_y):
        # Animation properties
        self.animation_list = animation_list
        self.action = IDLE
        self.frame = 0
        self.animation_cooldown = 100
        self.last_update = pygame.time.get_ticks()
        
        # Sprite setup
        self.image = self.animation_list[self.action][self.frame]
        self.image = pygame.transform.scale(self.image, 
                                          (self.image.get_width() * SCALE, 
                                           self.image.get_height() * SCALE))
        self.rect = self.image.get_rect()
        self.rect.x = spawn_x
        self.rect.y = spawn_y
        
        # Physics properties
        self.vel_x = 0
        self.vel_y = 0
        self.gravity = 0.8
        self.max_speed = 2
        self.jump_strength = -15
        self.in_air = False
        self.flip = False
        
        # AI and movement properties
        self.detection_range = 128  # pixels
        self.attack_range = 64
        self.move_timer = 0
        self.idle_duration = 2000  # milliseconds
        self.last_direction_change = pygame.time.get_ticks()
        
        # Block collision system
        self.blocks = blocks
        self.block_width = block_width
        self.block_height = block_height
        
        # Health and status
        self.max_health = 200
        self.health = self.max_health
        self.alive = True
        
        # Pathfinding properties
        self.target_x = spawn_x
        self.stuck_timer = 0
        self.max_stuck_time = 1000  # milliseconds before trying to jump

    def update_animation(self):
        """Handle sprite animation updates"""
        current_time = pygame.time.get_ticks()
        if current_time - self.last_update >= self.animation_cooldown:
            self.frame += 1
            self.last_update = current_time
            if self.frame >= len(self.animation_list[self.action]):
                self.frame = 0
        
        # Update sprite image
        self.image = self.animation_list[self.action][self.frame]
        self.image = pygame.transform.scale(self.image, 
                                          (self.image.get_width() * SCALE, 
                                           self.image.get_height() * SCALE))
        if self.flip:
            self.image = pygame.transform.flip(self.image, True, False)

    def check_collision(self, dx, dy):
        """Check collision with blocks at a given offset"""
        temp_rect = self.rect.copy()
        temp_rect.x += dx
        temp_rect.y += dy
        
        for block in self.blocks:
            # Skip bush blocks (non-solid)
            if block["type"] == "bush":
                continue
            if temp_rect.colliderect(block["rect"]):
                return True
        return False

    def check_ground_ahead(self, direction, distance=32):
        """Check if there's ground ahead in the given direction"""
        check_x = self.rect.centerx + (direction * distance)
        check_y = self.rect.bottom + self.block_height
        
        for block in self.blocks:
            if block["type"] != "bush":
                if (abs(block["rect"].centerx - check_x) < self.block_width//2 and 
                    abs(block["rect"].top - check_y) < self.block_height//2):
                    return True
        return False

    def detect_obstacle_ahead(self, direction):
        """Detect if there's an obstacle that requires jumping"""
        # Check for blocks at boss height in movement direction
        check_distance = self.block_width * 2
        check_x = self.rect.centerx + (direction * check_distance)
        
        for block in self.blocks:
            if block["type"] != "bush":
                if (abs(block["rect"].centerx - check_x) < self.block_width and
                    block["rect"].bottom > self.rect.top and
                    block["rect"].top < self.rect.bottom):
                    return True
        return False

    def get_distance_to_player(self, player):
        """Calculate distance to player"""
        return math.sqrt((self.rect.centerx - player.rect.centerx)**2 + 
                        (self.rect.centery - player.rect.centery)**2)

    def ai_behavior(self, player):
        """Main AI logic for boss behavior"""
        if not self.alive:
            return
        
        current_time = pygame.time.get_ticks()
        distance_to_player = self.get_distance_to_player(player)
        
        # Determine if player is within detection range
        if distance_to_player <= self.detection_range:
            # Player detected - move towards player
            direction = 1 if player.rect.centerx > self.rect.centerx else -1
            self.target_x = player.rect.centerx
            
            # Check if we need to jump over obstacles
            if self.detect_obstacle_ahead(direction) and not self.in_air:
                self.jump()
                self.action = JUMP
            elif not self.check_ground_ahead(direction) and not self.in_air:
                # No ground ahead, try to jump
                self.jump()
                self.action = JUMP
            else:
                # Move towards player
                if distance_to_player > self.attack_range:
                    self.vel_x = direction * self.max_speed
                    self.flip = direction < 0
                    self.action = WALK
                else:
                    # Close enough - can attack or idle
                    self.vel_x *= 0.8  # Slow down when close
                    self.action = IDLE
        else:
            # Player not detected - idle or patrol behavior
            self.vel_x *= 0.9  # Gradually stop
            if abs(self.vel_x) < 0.1:
                self.vel_x = 0
                self.action = IDLE

    def jump(self):
        """Make the boss jump"""
        if not self.in_air:
            self.vel_y = self.jump_strength
            self.in_air = True

    def apply_physics(self):
        """Apply gravity and movement physics"""
        # Apply gravity
        self.vel_y += self.gravity
        
        # Limit falling speed
        if self.vel_y > 15:
            self.vel_y = 15
        
        # Vertical movement and collision
        if not self.check_collision(0, self.vel_y):
            self.rect.y += self.vel_y
        else:
            if self.vel_y > 0:  # Landing
                self.vel_y = 0
                self.in_air = False
            elif self.vel_y < 0:  # Hit ceiling
                self.vel_y = 0
        
        # Horizontal movement and collision
        if not self.check_collision(self.vel_x, 0):
            self.rect.x += self.vel_x
            self.stuck_timer = 0
        else:
            # Stuck against wall - try to jump if stuck too long
            self.stuck_timer += 1
            if self.stuck_timer > 60 and not self.in_air:  # 1 second at 60 FPS
                self.jump()
                self.stuck_timer = 0
        
        # Screen boundaries (optional)
        screen_width = pygame.display.get_surface().get_width()
        if self.rect.left < 0:
            self.rect.left = 0
            self.vel_x = 0
        elif self.rect.right > screen_width:
            self.rect.right = screen_width
            self.vel_x = 0

    def take_damage(self, damage):
        """Handle boss taking damage"""
        self.health -= damage
        if self.health <= 0:
            self.health = 0
            self.alive = False

    def draw_health_bar(self, surface):
        """Draw boss health bar above the boss"""
        if self.alive and self.health < self.max_health:
            bar_width = 60
            bar_height = 8
            bar_x = self.rect.centerx - bar_width // 2
            bar_y = self.rect.top - 15
            
            # Background (red)
            pygame.draw.rect(surface, (255, 0, 0), 
                           (bar_x, bar_y, bar_width, bar_height))
            
            # Health (green)
            health_width = int((self.health / self.max_health) * bar_width)
            pygame.draw.rect(surface, (0, 255, 0), 
                           (bar_x, bar_y, health_width, bar_height))
            
            # Border
            pygame.draw.rect(surface, (255, 255, 255), 
                           (bar_x, bar_y, bar_width, bar_height), 2)

    def update(self, player):
        """Main update method - call this every frame"""
        if self.alive:
            self.ai_behavior(player)
            self.apply_physics()
        
        self.update_animation()

    def draw(self, surface):
        """Draw the boss on the screen"""
        if self.alive:
            surface.blit(self.image, self.rect)
            self.draw_health_bar(surface)

# Integration example for your existing game class
class BossIntegratedWorld:
    """Example of how to integrate the boss into your existing world class"""
    
    def __init__(self, existing_world_instance):
        self.world = existing_world_instance
        self.boss = None
        self.boss_spawned = False
        
    def spawn_boss(self):
        """Spawn the boss at a suitable location"""
        if not self.boss_spawned:
            # Load boss sprite (you'll need to have boss_sprite.png in your directory)
            try:
                sprite_path = 'boss_sprite.png'  # Adjust path as needed
                sprite_sheet_image = pygame.image.load(sprite_path).convert_alpha()
                animation_list = load_boss_animations(sprite_sheet_image)
                
                # Find a suitable spawn location (away from player)
                spawn_x = self.world.player.rect.x + 400  # Spawn 400 pixels away
                spawn_y = 300
                
                # Adjust spawn_y to be on ground
                for block in self.world.blocks:
                    if block["type"] != "bush" and abs(block["rect"].centerx - spawn_x) < self.world.block_width:
                        if block["rect"].top < spawn_y:
                            spawn_y = block["rect"].top
                
                self.boss = Boss(animation_list, self.world.blocks, 
                               self.world.block_width, self.world.block_height, 
                               spawn_x, spawn_y)
                self.boss_spawned = True
                print("Boss spawned!")
                
            except pygame.error as e:
                print(f"Could not load boss sprite: {e}")
                print("Make sure 'boss_sprite.png' exists in your game directory")
    
    def update_boss(self):
        """Update boss if it exists"""
        if self.boss and self.boss.alive:
            self.boss.update(self.world.player)
    
    def draw_boss(self, surface):
        """Draw boss if it exists"""
        if self.boss:
            self.boss.draw(surface)

# Usage example - modify your game loop to include:
"""
# In your generateworld class __init__ method, add:
self.boss_system = BossIntegratedWorld(self)

# In your game loop, add these calls:
# After player update:
if not self.boss_system.boss_spawned:
    self.boss_system.spawn_boss()

self.boss_system.update_boss()

# In your drawing section:
self.boss_system.draw_boss(self.screen)
"""