import pygame
import spritesheet 
import os
import sys

current_directory = os.path.dirname(os.path.abspath(__file__))
parent_directory = os.path.dirname(current_directory)
player_directory = os.path.join(parent_directory, 'Map')

pygame.init()

# Fullscreen setup
infoObject = pygame.display.Info()
SCREEN_WIDTH, SCREEN_HEIGHT = infoObject.current_w, infoObject.current_h
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.NOFRAME)
pygame.display.set_caption('2D Character Animation with Movement')

background = pygame.image.load("Map\BACKGROUND\sforest.png")
background = pygame.transform.scale(background,(1920,1080))
BLACK = (0, 0, 0)

BLACK = (0, 0, 0)
BG = (50, 50, 50)
WHITE = (255, 255, 255)
FPS = 60

# Animation frames count for base animations
base_animation_steps = [6, 8, 6, 5]  # idle, walk right, jump, etc.
# Animation frames count for action animations (attack, mine)
action_animation_steps = [6, 6]  # attack, mine - adjust these based on your actual sprite frames

SCALE = 3

# States
IDLE = 0
WALK = 1
JUMP = 2
ATTACK = 3
MINE = 4

clock = pygame.time.Clock()
script_dir = os.path.dirname(os.path.abspath(__file__))

def load_base_animations(sprite_sheet_image):
    """Load base animations (idle, walk, jump) from main sprite sheet."""
    sprite_sheet = spritesheet.SpriteSheet(sprite_sheet_image)
    animation_list = []
    step_counter = 0
    for animation_len in base_animation_steps:
        temp_img_list = []
        for _ in range(animation_len): 
            temp_img_list.append(sprite_sheet.get_image(step_counter, 104, 104, 0.3, 'black'))
            step_counter += 1
        animation_list.append(temp_img_list)
    return animation_list

def load_action_animations(attack_image, mine_image, sprite_width, sprite_height, scale_factor):
    """Load action animations (attack, mine) from separate sprite sheets."""
    action_animations = []
    
    # Load attack animation
    attack_sheet = spritesheet.SpriteSheet(attack_image)
    attack_frames = []
    for i in range(action_animation_steps[0]):  # attack frames
        frame = attack_sheet.get_image(i, sprite_width, sprite_height, scale_factor, 'black')
        attack_frames.append(frame)
    action_animations.append(attack_frames)
    
    # Load mine animation
    mine_sheet = spritesheet.SpriteSheet(mine_image)
    mine_frames = []
    for i in range(action_animation_steps[1]):  # mine frames
        frame = mine_sheet.get_image(i, sprite_width, sprite_height, scale_factor, 'black')
        mine_frames.append(frame)
    action_animations.append(mine_frames)
    
    return action_animations

class Player:
    def __init__(self, base_animation_list, action_animation_list, gender):
        self.base_animation_list = base_animation_list
        self.action_animation_list = action_animation_list
        self.gender = gender
        self.action = IDLE
        self.frame = 0
        self.flip = False  # Used to flip image for left movement
        
        # Action state tracking
        self.is_performing_action = False
        self.action_start_time = 0
        self.action_duration = 1000  # 1 second action duration
        
        self.image = self.get_current_frame()
        self.image = self.scale_current_image()
        self.rect = self.image.get_rect()
        self.rect.bottomleft = (50, SCREEN_HEIGHT - 50)

        self.vel_x = 0
        self.vel_y = 0
        self.speed = 7
        self.gravity = 0.5
        self.jump_speed = -12
        self.in_air = False

        # --- HEALTH BAR ---
        self.current_health = 200
        self.maximum_health = 1000
        self.health_bar_length = 100  # smaller for above player
        self.health_ratio = self.maximum_health / self.health_bar_length

        self.last_update = pygame.time.get_ticks()
        self.animation_cooldown = 150

    def get_current_frame(self):
        """Get the current frame based on action state."""
        if self.action in [ATTACK, MINE]:
            action_index = self.action - ATTACK  # Convert to action animation index
            if action_index < len(self.action_animation_list):
                return self.action_animation_list[action_index][self.frame]
        
        # Default to base animations
        if self.action < len(self.base_animation_list):
            return self.base_animation_list[self.action][self.frame]
        
        # Fallback to idle
        return self.base_animation_list[IDLE][0]

    def scale_current_image(self):
        """Scale the current image appropriately."""
        image = self.get_current_frame()
        
        # Different scaling for action sprites due to different pixel dimensions
        if self.action in [ATTACK, MINE]:
            # Action sprites have different dimensions, so we scale them differently
            if self.gender == 'male':
                # Male action sprites are 273x182, scale to match base sprite size
                scale_factor = 2.0  # Adjust this to match your desired size
            else:
                # Female action sprites are 232x182, scale to match base sprite size  
                scale_factor = 2.2  # Adjust this to match your desired size
            
            scaled_image = pygame.transform.scale(image, 
                (int(image.get_width() * scale_factor), int(image.get_height() * scale_factor)))
        else:
            # Base sprites use the original scaling
            scaled_image = pygame.transform.scale(image, 
                (image.get_width() * SCALE, image.get_height() * SCALE))
        
        return scaled_image

    def get_animation_length(self):
        """Get the length of the current animation."""
        if self.action in [ATTACK, MINE]:
            action_index = self.action - ATTACK
            return len(self.action_animation_list[action_index])
        else:
            return len(self.base_animation_list[self.action])

    def perform_action(self, action_type):
        """Start performing an action (attack or mine)."""
        if not self.is_performing_action and not self.in_air:  # Can't perform actions while jumping
            self.action = action_type
            self.frame = 0
            self.is_performing_action = True
            self.action_start_time = pygame.time.get_ticks()

    # --- HEALTH FUNCTIONS ---
    def get_damage(self, amount):
        if self.current_health > 0:
            self.current_health -= amount
        if self.current_health <= 0:
            self.current_health = 0

    def get_health(self, amount):
        if self.current_health < self.maximum_health:
            self.current_health += amount
        if self.current_health >= self.maximum_health:
            self.current_health = self.maximum_health

    def draw_health_bar(self, surf):
        # Draw health bar above player
        x = self.rect.centerx - self.health_bar_length//2
        y = self.rect.top - 15
        pygame.draw.rect(surf, (60, 60, 60), (x, y, self.health_bar_length, 10))
        pygame.draw.rect(surf, (255, 0, 0), (x, y, self.current_health/self.health_ratio, 10))
        pygame.draw.rect(surf, (255, 255, 255), (x, y, self.health_bar_length, 2))

    # --- MOVEMENT & ANIMATION ---
    def update(self):
        # Check if action should end
        if self.is_performing_action:
            current_time = pygame.time.get_ticks()
            if current_time - self.action_start_time >= self.action_duration:
                self.is_performing_action = False
                self.action = IDLE
                self.frame = 0

        # Animation update
        current_time = pygame.time.get_ticks()
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

        # Only apply physics if not performing an action
        if not self.is_performing_action:
            # Gravity
            self.vel_y += self.gravity
            self.rect.y += self.vel_y
            if self.rect.bottom >= SCREEN_HEIGHT - 50:
                self.rect.bottom = SCREEN_HEIGHT - 50
                self.vel_y = 0
                self.in_air = False

            # Horizontal movement
            self.rect.x += self.vel_x
            if self.rect.left < 0:
                self.rect.left = 0
            if self.rect.right > SCREEN_WIDTH:
                self.rect.right = SCREEN_WIDTH

    def move(self, left, right, jump, attack, mine):
        # Handle action inputs first
        if attack:
            self.perform_action(ATTACK)
            return
        if mine:
            self.perform_action(MINE)
            return

        # Don't allow movement during actions
        if self.is_performing_action:
            return

        if jump and not self.in_air:
            self.vel_y = self.jump_speed
            self.in_air = True

        self.vel_x = 0
        if left:
            self.vel_x = -self.speed
            self.flip = True
        elif right:
            self.vel_x = self.speed
            self.flip = False

        previous_action = self.action
        if self.in_air:
            self.action = JUMP
        else:
            if self.vel_x != 0:
                self.action = WALK
            else:
                self.action = IDLE

        if previous_action != self.action:
            self.frame = 0

    def draw(self, surf):
        surf.blit(self.image, self.rect)
        self.draw_health_bar(surf)

# --- GENDER SELECTION SCREEN ---
def gender_selection_screen():
    font = pygame.font.SysFont(None, 60)
    small_font = pygame.font.SysFont(None, 40)

    selecting = True
    selected_gender = None

    while selecting:
        screen.blit(background,(0,0))
        
        title_text = font.render("Select Your Character Gender", True, 'white')
        male_text = small_font.render("Press M for Male", True, 'white')
        female_text = small_font.render("Press F for Female", True, 'white')

        screen.blit(title_text, (SCREEN_WIDTH//2 - title_text.get_width()//2, SCREEN_HEIGHT//3))
        screen.blit(male_text, (SCREEN_WIDTH//2 - male_text.get_width()//2, SCREEN_HEIGHT//2))
        screen.blit(female_text, (SCREEN_WIDTH//2 - female_text.get_width()//2, SCREEN_HEIGHT//2 + 50))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_m:
                    selected_gender = 'male'
                    selecting = False
                elif event.key == pygame.K_f:
                    selected_gender = 'female'
                    selecting = False
                elif event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

        pygame.display.update()
        clock.tick(FPS)

    return selected_gender

# --- MAIN LOOP ---
def main():
    gender = gender_selection_screen()
    
    # Load base sprites
    if gender == 'male':
        base_sprite_image = pygame.image.load(os.path.join(script_dir,'Sprite_Img/male_spriteV8_flipped.png')).convert_alpha()
        attack_sprite_image = pygame.image.load(os.path.join(script_dir,'Sprite_Img/male_sprite_attack.png')).convert_alpha()
        mine_sprite_image = pygame.image.load(os.path.join(script_dir,'Sprite_Img/male_sprite_mine.png')).convert_alpha()
        action_sprite_width, action_sprite_height = 273, 182
        action_scale_factor = 0.3
    else:
        base_sprite_image = pygame.image.load(os.path.join(script_dir,'Sprite_Img/female_spriteV1_flipped.png')).convert_alpha()
        attack_sprite_image = pygame.image.load(os.path.join(script_dir,'Sprite_Img/female_sprite_attack.png')).convert_alpha()
        mine_sprite_image = pygame.image.load(os.path.join(script_dir,'Sprite_Img/female_sprite_mine.png')).convert_alpha()
        action_sprite_width, action_sprite_height = 232, 182
        action_scale_factor = 0.3

    # Load animations
    base_animation_list = load_base_animations(base_sprite_image)
    action_animation_list = load_action_animations(attack_sprite_image, mine_sprite_image, 
                                                 action_sprite_width, action_sprite_height, action_scale_factor)
    
    player = Player(base_animation_list, action_animation_list, gender)



    run = True
    while run:
        clock.tick(FPS)
        keys = pygame.key.get_pressed()
        left = keys[pygame.K_LEFT]
        right = keys[pygame.K_RIGHT]
        jump = keys[pygame.K_SPACE]
        attack = keys[pygame.K_1]
        mine = keys[pygame.K_2]

        # Test health bar keys
        if keys[pygame.K_UP]:
            player.get_health(50)
        if keys[pygame.K_DOWN]:
            player.get_damage(50)

        player.move(left, right, jump, attack, mine)
        player.update()

        screen.fill(BG)
        player.draw(screen)

        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    run = False

        pygame.display.update()

    pygame.quit()

if __name__ == "__main__":
    main()