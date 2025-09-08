import pygame
import spritesheet 
import os
import sys

pygame.init()

# Fullscreen setup
infoObject = pygame.display.Info()
SCREEN_WIDTH, SCREEN_HEIGHT = infoObject.current_w, infoObject.current_h
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.NOFRAME)
pygame.display.set_caption('2D Character Animation with Movement')

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
script_dir = os.path.dirname(os.path.abspath(__file__))

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

class Player:
    def __init__(self, animation_list):
        self.animation_list = animation_list
        self.action = IDLE
        self.frame = 0
        self.flip = False  # Used to flip image for left movement
        
        self.image = self.animation_list[self.action][self.frame]
        self.image = pygame.transform.scale(self.image, (self.image.get_width()*SCALE, self.image.get_height()*SCALE))
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
        # Animation update
        current_time = pygame.time.get_ticks()
        if current_time - self.last_update >= self.animation_cooldown:
            self.frame += 1
            self.last_update = current_time
            if self.frame >= len(self.animation_list[self.action]):
                self.frame = 0

        if self.frame >= len(self.animation_list[self.action]):
            self.frame = 0

        self.image = self.animation_list[self.action][self.frame]
        self.image = pygame.transform.scale(self.image, (self.image.get_width()*SCALE, self.image.get_height()*SCALE))
        if self.flip:
            self.image = pygame.transform.flip(self.image, True, False)

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
    if gender == 'male':
        sprite_sheet_image = pygame.image.load(os.path.join(script_dir,'Sprite_Img/male_spriteV8_flipped.png')).convert_alpha()
    else:
        sprite_sheet_image = pygame.image.load(os.path.join(script_dir,'Sprite_Img/female_spriteV1_flipped.png')).convert_alpha()

    animation_list = load_animations(sprite_sheet_image)
    player = Player(animation_list)

    run = True
    while run:
        clock.tick(FPS)
        keys = pygame.key.get_pressed()
        left = keys[pygame.K_LEFT]
        right = keys[pygame.K_RIGHT]
        jump = keys[pygame.K_SPACE]

        # Test health bar keys
        if keys[pygame.K_UP]:
            player.get_health(50)
        if keys[pygame.K_DOWN]:
            player.get_damage(50)

        player.move(left, right, jump)
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
