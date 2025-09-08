import pygame
import spritesheet 
import os

pygame.init()

# Fullscreen setup
infoObject = pygame.display.Info()
SCREEN_WIDTH, SCREEN_HEIGHT = infoObject.current_w, infoObject.current_h

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.NOFRAME)
pygame.display.set_caption('2D Character Animation with Movement')

# Get the directory where this script is located
script_dir = os.path.dirname(os.path.abspath(__file__))

BLACK = (0, 0, 0)
BG = (50, 50, 50)
WHITE = (255, 255, 255)
FPS = 60

# Animation frames count (adjust if they differ)
animation_steps = [6, 8, 6]  # e.g. idle, walk right, jump, etc.

SCALE = 3

# States
IDLE = 0
WALK = 1
JUMP = 2

clock = pygame.time.Clock()

def load_animations(sprite_sheet_image):
    """Load animations from a sprite sheet image and return animation_list."""
    sprite_sheet = spritesheet.SpriteSheet(sprite_sheet_image)
    animation_list = []
    step_counter = 0
    for animation_len in animation_steps:
        temp_img_list = []
        for _ in range(animation_len): 
            temp_img_list.append(sprite_sheet.get_image(step_counter, 104, 104, 0.3, 'black'))
            step_counter += 1
        animation_list.append(temp_img_list)
    return animation_list

# Player class updated to accept animation_list
class Player:
    def __init__(self, animation_list):
        self.animation_list = animation_list
        self.action = IDLE
        self.frame = 0
        self.flip = False  # Used to flip image for left movement
        
        self.image = self.animation_list[self.action][self.frame]
        self.image = pygame.transform.scale(self.image, (self.image.get_width()*SCALE, self.image.get_height()*SCALE))
        
        self.rect = self.image.get_rect()
        self.rect.bottomleft = (50, SCREEN_HEIGHT - 50)  # start position

        self.vel_x = 0
        self.vel_y = 0
        self.speed = 7

        self.gravity = 0.5
        self.jump_speed = -12
        self.in_air = False

        self.last_update = pygame.time.get_ticks()
        self.animation_cooldown = 150  # Faster animation speed

    def update(self):
        # Animation update
        current_time = pygame.time.get_ticks()
        if current_time - self.last_update >= self.animation_cooldown:
            self.frame += 1
            self.last_update = current_time
            if self.frame >= len(self.animation_list[self.action]):
                self.frame = 0

        # Ensure frame is within bounds (safety check)
        if self.frame >= len(self.animation_list[self.action]):
            self.frame = 0

        # Set current image animation frame and scale
        self.image = self.animation_list[self.action][self.frame]
        self.image = pygame.transform.scale(self.image, (self.image.get_width()*SCALE, self.image.get_height()*SCALE))
        if self.flip:
            self.image = pygame.transform.flip(self.image, True, False)

        # Apply gravity
        self.vel_y += self.gravity
        self.rect.y += self.vel_y

        # Ground collision (simple floor barrier)
        if self.rect.bottom >= SCREEN_HEIGHT - 50:
            self.rect.bottom = SCREEN_HEIGHT - 50
            self.vel_y = 0
            self.in_air = False

        # Move horizontally
        self.rect.x += self.vel_x

        # Screen barriers left and right
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH

    def move(self, left, right, jump):
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

        # Store previous action to detect changes
        previous_action = self.action

        # Set action state
        if self.in_air:
            self.action = JUMP
        else:
            if self.vel_x != 0:
                self.action = WALK
            else:
                self.action = IDLE

        # Reset animation frame when action changes
        if previous_action != self.action:
            self.frame = 0

    def draw(self, surf):
        surf.blit(self.image, self.rect)

def gender_selection_screen():
    """Display gender selection screen and return selected gender string."""
    font = pygame.font.SysFont(None, 60)
    small_font = pygame.font.SysFont(None, 40)

    selecting = True
    selected_gender = None

    while selecting:
        screen.fill(BG)

        title_text = font.render("Select Your Character Gender", True, WHITE)
        male_text = small_font.render("Press M for Male", True, WHITE)
        female_text = small_font.render("Press F for Female", True, WHITE)

        screen.blit(title_text, (SCREEN_WIDTH//2 - title_text.get_width()//2, SCREEN_HEIGHT//3))
        screen.blit(male_text, (SCREEN_WIDTH//2 - male_text.get_width()//2, SCREEN_HEIGHT//2))
        screen.blit(female_text, (SCREEN_WIDTH//2 - female_text.get_width()//2, SCREEN_HEIGHT//2 + 50))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_m:
                    selected_gender = 'male'
                    selecting = False
                elif event.key == pygame.K_f:
                    selected_gender = 'female'
                    selecting = False
                elif event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    exit()

        pygame.display.update()
        clock.tick(FPS)

    return selected_gender

def main():
    # Show gender selection screen first
    gender = gender_selection_screen()

    # Load sprite sheet based on gender
    if gender == 'male':
        sprite_sheet_image = pygame.image.load(os.path.join(script_dir,'Sprite_Img/male_spriteV8_flipped.png')).convert_alpha()
    else:
        sprite_sheet_image = pygame.image.load(os.path.join(script_dir,'Sprite_Img/female_spriteV1_flipped.png')).convert_alpha()

    animation_list = load_animations(sprite_sheet_image)

    # Instantiate Player with selected animations
    player = Player(animation_list)

    run = True
    while run:
        clock.tick(FPS)

        # Handle inputs
        keys = pygame.key.get_pressed()
        left = keys[pygame.K_LEFT]
        right = keys[pygame.K_RIGHT]
        jump = keys[pygame.K_SPACE]

        # Update player movement and animation
        player.move(left, right, jump)
        player.update()

        # Draw background and player
        screen.fill(BG)
        player.draw(screen)

        # Event handler for quitting the app
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            # Exit fullscreen and quit on ESC
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    run = False

        pygame.display.update()

    pygame.quit()

if __name__ == "__main__":
    main()