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

sprite_sheet_image = pygame.image.load(os.path.join(script_dir,'male_spriteV8_flipped.png')).convert_alpha()
sprite_sheet = spritesheet.SpriteSheet(sprite_sheet_image)

BLACK = (0, 0, 0)
BG = (50, 50, 50)
FPS = 60

# Animation frames count (adjust if they differ)
animation_steps = [6, 8, 6, 0]  # e.g. idle, walk right, jump, etc.

# Load animation s
animation_list = []
step_counter = 0
for animation_len in animation_steps:
    temp_img_list = []
    for _ in range(animation_len): 
        temp_img_list.append(sprite_sheet.get_image(step_counter, 104, 104, 0.3, 'black'))
        step_counter += 1
    animation_list.append(temp_img_list)

clock = pygame.time.Clock()

# Scale factor for sprite (optional, adjust as needed)
SCALE = 3

# States
IDLE = 0
WALK = 1
JUMP = 2

# Character class
class Player:
    def __init__(self):
        self.action = IDLE
        self.frame = 0
        self.flip = False  # Used to flip image for left movement
        
        self.image = animation_list[self.action][self.frame]
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
            if self.frame >= len(animation_list[self.action]):
                self.frame = 0

        # Set current image animation frame and scale
        self.image = animation_list[self.action][self.frame]
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

        # Set action state
        if self.in_air:
            self.action = JUMP
            self.frame = 0  # reset animation frame for jump
        else:
            if self.vel_x != 0:
                self.action = WALK
            else:
                self.action = IDLE

    def draw(self, surf):
        surf.blit(self.image, self.rect)

# Instantiate Player
player = Player()

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