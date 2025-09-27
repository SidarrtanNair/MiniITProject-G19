import pygame
import sys
import os
from spritesheet import SpriteSheet

pygame.init()

# Animation configuration for boss sprites
boss_animation_config = {
    'idle': {'file': 'Sprite_Img/boss_idle.png', 'frames': 6, 'width': 128, 'height': 128},
    'dead': {'file': 'Sprite_Img/boss_dead.png', 'frames': 8, 'width': 128, 'height': 128},
    'attack1': {'file': 'Sprite_Img/boss_attack1.png', 'frames': 6, 'width': 128, 'height': 128},
    'attack2': {'file': 'Sprite_Img/boss_attack2.png', 'frames': 5, 'width': 128, 'height': 128},
    'fireball': {'file': 'Sprite_Img/boss_fireball.png', 'frames': 4, 'width': 64, 'height': 64},
    'run': {'file': 'Sprite_Img/boss_run.png', 'frames': 8, 'width': 128, 'height': 128},
    'jump': {'file': 'Sprite_Img/boss_jump.png', 'frames': 4, 'width': 128, 'height': 128}
}

# Fullscreen setup
infoObject = pygame.display.Info()
SCREEN_WIDTH, SCREEN_HEIGHT = infoObject.current_w, infoObject.current_h
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.NOFRAME)

SCALE = 4
FPS = 60

# Boss States with key bindings (keys 1-7)
boss_state_keys = {
    pygame.K_1: 'idle',      # Key 1 - Idle
    pygame.K_2: 'dead',      # Key 2 - Dead
    pygame.K_3: 'attack1',   # Key 3 - Attack1
    pygame.K_4: 'attack2',   # Key 4 - Attack2
    pygame.K_5: 'fireball',  # Key 5 - Fireball
    pygame.K_6: 'run',       # Key 6 - Run
    pygame.K_7: 'jump'       # Key 7 - Jump
}

clock = pygame.time.Clock()
script_dir = os.path.dirname(os.path.abspath(__file__))

def handle_animation_input(keys_pressed, current_animation):
    """Handle key input to change boss animation (keys 1-7)."""
    for key, animation_name in boss_state_keys.items():
        if keys_pressed[key]:
            return animation_name
    return current_animation

def load_boss_animations_dict(scale_factor=SCALE):
    """Load all boss animations and return as a dictionary."""
    boss_animations = {}
    
    for animation_name, config in boss_animation_config.items():
        sprite_path = os.path.join(script_dir, config['file'])
        
        try:
            sprite_image = pygame.image.load(sprite_path).convert_alpha()
            sprite_sheet = SpriteSheet(sprite_image)
            
            frames = []
            for frame_index in range(config['frames']):
                frame = sprite_sheet.get_image(
                    frame_index,
                    config['width'],
                    config['height'], 
                    scale_factor,
                    None
                )
                frames.append(frame)
            
            boss_animations[animation_name] = frames
        except pygame.error:
            print(f"Warning: Could not load {sprite_path}")
            # Create placeholder frames if sprite file is missing
            placeholder_surface = pygame.Surface((config['width'] * scale_factor, 
                                                config['height'] * scale_factor))
            placeholder_surface.fill((255, 0, 255))  # Magenta placeholder
            boss_animations[animation_name] = [placeholder_surface] * config['frames']
    
    return boss_animations

class BossAnimator:
    """Enhanced animator class to manage boss animations."""
    
    def __init__(self, scale_factor=SCALE):
        self.animations = load_boss_animations_dict(scale_factor)
        self.current_animation = 'idle'
        self.current_frame = 0
        self.animation_speed = 0.15   
        self.frame_timer = 0
        self.facing_right = True
        
    def update(self, dt):
        """Update the animation frame based on delta time."""
        self.frame_timer += dt
        
        if self.frame_timer >= self.animation_speed:
            self.frame_timer = 0
            self.current_frame += 1
            
            max_frames = len(self.animations[self.current_animation])
            if self.current_frame >= max_frames:
                self.current_frame = 0
    
    def set_animation(self, animation_name):
        """Change to a different animation."""
        if animation_name in self.animations and animation_name != self.current_animation:
            self.current_animation = animation_name
            self.current_frame = 0
            self.frame_timer = 0
    
    def get_current_frame(self):
        """Get the current frame surface to draw."""
        frame = self.animations[self.current_animation][self.current_frame]
        if not self.facing_right:
            frame = pygame.transform.flip(frame, True, False)
        return frame
    
    def is_animation_finished(self):
        """Check if current animation has completed one full cycle."""
        max_frames = len(self.animations[self.current_animation])
        return self.current_frame == max_frames - 1

class Boss:
    """Boss game entity class."""
    
    def __init__(self, x, y):
        self.animator = BossAnimator()
        self.x = x
        self.y = y
        self.vel_x = 0
        self.vel_y = 0
        self.health = 100
        self.max_health = 100
        self.is_alive = True
        self.ground_y = y
        self.jump_power = -400
        self.gravity = 800
        self.move_speed = 200
        
        # Get initial frame dimensions for collision
        frame = self.animator.get_current_frame()
        self.width = frame.get_width()
        self.height = frame.get_height()
    
    def update(self, dt, keys_pressed):
        """Update boss logic."""
        if not self.is_alive:
            return
            
        # Handle animation input
        new_animation = handle_animation_input(keys_pressed, self.animator.current_animation)
        
        # Handle movement based on current animation
        if new_animation == 'run':
            if keys_pressed[pygame.K_LEFT]:
                self.vel_x = -self.move_speed
                self.animator.facing_right = False
            elif keys_pressed[pygame.K_RIGHT]:
                self.vel_x = self.move_speed
                self.animator.facing_right = True
            else:
                self.vel_x = 0
        elif new_animation == 'jump' and self.y >= self.ground_y:
            self.vel_y = self.jump_power
        else:
            self.vel_x = 0
        
        # Set animation
        self.animator.set_animation(new_animation)
        
        # Apply physics
        self.x += self.vel_x * dt
        self.y += self.vel_y * dt
        
        # Apply gravity
        if self.y < self.ground_y:
            self.vel_y += self.gravity * dt
        else:
            self.y = self.ground_y
            self.vel_y = 0
        
        # Keep boss on screen
        self.x = max(0, min(self.x, SCREEN_WIDTH - self.width))
        
        # Update animator
        self.animator.update(dt)
        
        # Check if boss should die
        if self.health <= 0 and self.is_alive:
            self.is_alive = False
            self.animator.set_animation('dead')
    
    def take_damage(self, damage):
        """Apply damage to boss."""
        if self.is_alive:
            self.health = max(0, self.health - damage)
    
    def draw(self, screen):
        """Draw the boss."""
        current_frame = self.animator.get_current_frame()
        screen.blit(current_frame, (int(self.x), int(self.y)))
        
        # Draw health bar
        if self.is_alive:
            bar_width = 200
            bar_height = 20
            bar_x = SCREEN_WIDTH // 2 - bar_width // 2
            bar_y = 50
            
            # Background
            pygame.draw.rect(screen, (100, 0, 0), (bar_x, bar_y, bar_width, bar_height))
            
            # Health bar
            health_ratio = self.health / self.max_health
            health_width = int(bar_width * health_ratio)
            pygame.draw.rect(screen, (0, 200, 0), (bar_x, bar_y, health_width, bar_height))
            
            # Border
            pygame.draw.rect(screen, (255, 255, 255), (bar_x, bar_y, bar_width, bar_height), 2)

def draw_ui(screen, font, boss):
    """Draw UI elements."""
    # Draw instructions
    instructions = [
        "Boss Animation Controls:",
        "1 - Idle    2 - Dead    3 - Attack1    4 - Attack2",
        "5 - Fireball    6 - Run    7 - Jump",
        "Arrow Keys - Move (during Run)    Space - Damage Boss    ESC - Quit"
    ]
    
    y_offset = SCREEN_HEIGHT - 120
    for i, instruction in enumerate(instructions):
        color = (255, 255, 255) if i == 0 else (200, 200, 200)
        text = font.render(instruction, True, color)
        screen.blit(text, (20, y_offset + i * 25))
    
    # Draw current animation
    anim_text = font.render(f"Current Animation: {boss.animator.current_animation}", True, (255, 255, 0))
    screen.blit(anim_text, (20, 20))
    
    # Draw health
    health_text = font.render(f"Health: {boss.health}/{boss.max_health}", True, (255, 255, 255))
    screen.blit(health_text, (SCREEN_WIDTH - 200, 20))

def main():
    """Main game loop."""
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Boss Animation Demo")
    
    # Initialize font
    font = pygame.font.Font(None, 24)
    
    # Create boss
    boss_x = SCREEN_WIDTH // 2 - 64
    boss_y = SCREEN_HEIGHT - 600
    boss = Boss(boss_x, boss_y)
    
    # Game loop variables
    running = True
    dt = 0
    
    while running:
        # Calculate delta time
        dt = clock.tick(FPS) / 1000.0
        
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_SPACE:
                    # Damage boss for testing
                    boss.take_damage(10)
                elif event.key == pygame.K_r and not boss.is_alive:
                    # Reset boss
                    boss = Boss(boss_x, boss_y)
        
        # Get current key states
        keys_pressed = pygame.key.get_pressed()
        
        # Update game objects
        boss.update(dt, keys_pressed)
        
        # Render everything
        screen.fill((50, 50, 80))  # Dark blue background
        
        # Draw boss
        boss.draw(screen)
        
        # Draw UI
        draw_ui(screen, font, boss)
        
        # Show reset message if boss is dead
        if not boss.is_alive:
            reset_text = font.render("Boss is dead! Press 'R' to reset", True, (255, 255, 255))
            text_rect = reset_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            screen.blit(reset_text, text_rect)
        
        # Update display
        pygame.display.flip()
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()