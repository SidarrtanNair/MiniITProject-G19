import pygame
import random
import os
from spritesheet import SpriteSheet  
# Initialize pygame
pygame.init()

# file path
script_dir = os.path.dirname(os.path.abspath(__file__))

infoObject = pygame.display.Info()
SCREEN_WIDTH, SCREEN_HEIGHT = infoObject.current_w, infoObject.current_h
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.NOFRAME)
pygame.display.set_caption("Enemy Demo")

# Enemy spritesheet 
try:
    enemy_sheet_img = pygame.image.load(os.path.join(script_dir,'Sprite_Img/enemy_sprite.png')).convert_alpha()
except pygame.error:
    # Create a placeholder sprite sheet if file doesn't exist
    enemy_sheet_img = pygame.Surface((256, 32)).convert_alpha()
    enemy_sheet_img.fill((255, 0, 0))  # Red placeholder
    
enemy_sheet = SpriteSheet(enemy_sheet_img)

class Enemy(pygame.sprite.Sprite):
    def __init__(self, SCREEN_WIDTH, y, sprite_sheet, scale):
        pygame.sprite.Sprite.__init__(self)
        self.animation_list = []
        self.frame_index = 0
        self.update_time = pygame.time.get_ticks()
        self.direction = random.choice([-1, 1])
        if self.direction == 1:
            self.flip = True
        else:
            self.flip = False
        
        # Jumping variables
        self.vel_y = 0  
        self.gravity = 0.8  
        self.jump_speed = -15  
        self.on_ground = False  
        self.ground_y = y  
        self.jump_timer = 0  
        self.jump_cooldown = random.randint(60, 120)  
        
        #load images from spritesheet
        animation_steps = 8
        for animation in range(animation_steps):
            image = sprite_sheet.get_image(animation, 32, 32, scale, (0, 0, 0))
            image = pygame.transform.flip(image, self.flip, False)
            image.set_colorkey((0, 0, 0))
            self.animation_list.append(image)
        
        #select starting image and create rectangle from it
        self.image = self.animation_list[self.frame_index]
        self.rect = self.image.get_rect()
        if self.direction == 1:
            self.rect.x = 0
        else:
            self.rect.x = SCREEN_WIDTH
        self.rect.y = y

    def attack_player(self, player):
            if pygame.time.get_ticks() - getattr(self, "last_attack_time", 0) >= 1000:  # 1s cooldown
                self.last_attack_time = pygame.time.get_ticks()
                player.get_damage(10)    
        
    def update(self, scroll, SCREEN_WIDTH, player):
        ANIMATION_COOLDOWN = 50
        #update image depending on current frame
        self.image = self.animation_list[self.frame_index]
        #check if enough time has passed since the last update
        if pygame.time.get_ticks() - self.update_time > ANIMATION_COOLDOWN:
            self.update_time = pygame.time.get_ticks()
            self.frame_index += 1
        #if the animation has run out then reset back to the start
        if self.frame_index >= len(self.animation_list):
            self.frame_index = 0
        
        # Handle jumping logic
        self.jump_timer += 1
        
        # Check if enemy should jump (random intervals and only when on ground)
        if self.jump_timer >= self.jump_cooldown and self.on_ground:
            self.vel_y = self.jump_speed
            self.on_ground = False
            self.jump_timer = 0
            self.jump_cooldown = random.randint(60, 120)  
        
        # Apply gravity
        self.vel_y += self.gravity
        
        # Update vertical position
        self.rect.y += self.vel_y
        
        # Check ground collision
        if self.rect.y >= self.ground_y:
            self.rect.y = self.ground_y
            self.vel_y = 0
            self.on_ground = True
        
        #move enemy horizontally
        self.rect.x += self.direction * 2
        
        # Apply scroll to ground position as well
        self.ground_y += scroll
        self.rect.y += scroll
        
        #check if gone off screen
        if self.rect.right < 0 or self.rect.left > SCREEN_WIDTH:
            self.kill()
               
        if player and self.rect.colliderect(player.rect):
            self.attack_player(player)


# Create sprite group 
enemy_group = pygame.sprite.Group()

def main():
    clock = pygame.time.Clock()  
    run = True
    scroll = 0  
    
    while run:
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    run = False
        
        # Clear screen
        screen.fill((135, 206, 235))  # Light blue 
        
        # Generate enemy 
        if len(enemy_group) == 0:
            enemy = Enemy(SCREEN_WIDTH, SCREEN_HEIGHT - 100, enemy_sheet, 2)
            enemy_group.add(enemy)

        # Update enemy 
        enemy_group.update(scroll, SCREEN_WIDTH, player)

        # Draw sprite
        enemy_group.draw(screen) 

        # Update display window
        pygame.display.update()
        clock.tick(60)  # 60 FPS

    pygame.quit()  

# Run the game
if __name__ == "__main__":
    main()