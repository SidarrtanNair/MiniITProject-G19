import pygame
import os
import sys

# Directories
current_directory = os.path.dirname(os.path.abspath(__file__))
parent_directory = os.path.dirname(current_directory)
player_directory = os.path.join(parent_directory, 'Map')

# Add directories to sys.path so imports work
sys.path.append(current_directory)   # For local modules
sys.path.append(player_directory)    # For Map folder modules

# Now you can safely import
from spritesheet import SpriteSheet

pygame.init()

# Fullscreen setup
infoObject = pygame.display.Info()
SCREEN_WIDTH, SCREEN_HEIGHT = infoObject.current_w, infoObject.current_h
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.NOFRAME)
pygame.display.set_caption('2D Character Animation with Movement')

background = pygame.image.load("Map\\BACKGROUND\\sforest.png")
background = pygame.transform.scale(background,(1920,1080))

BLACK = (0, 0, 0)
BG = (50, 50, 50)
WHITE = (255, 255, 255)
FPS = 60

# Animation frames
base_animation_steps = [6, 8, 6, 5]  # idle, walk, jump, etc.
action_animation_steps = [6, 6]  # attack, mine

SCALE = 3

# States
IDLE = 0
WALK = 1
JUMP = 2
ATTACK = 3
MINE = 4

clock = pygame.time.Clock()
script_dir = os.path.dirname(os.path.abspath(__file__))

# --- ANIMATION LOADING ---
def load_base_animations(sprite_sheet_image):
    sprite_sheet = SpriteSheet(sprite_sheet_image)
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
    action_animations = []
    # Attack
    attack_sheet = SpriteSheet(attack_image)
    attack_frames = [attack_sheet.get_image(i, sprite_width, sprite_height, scale_factor, 'black') 
                     for i in range(action_animation_steps[0])]
    action_animations.append(attack_frames)
    # Mine
    mine_sheet = SpriteSheet(mine_image)
    mine_frames = [mine_sheet.get_image(i, sprite_width, sprite_height, scale_factor, 'black') 
                   for i in range(action_animation_steps[1])]
    action_animations.append(mine_frames)
    return action_animations

# --- PLAYER CLASS ---
class Player:
    def __init__(self, base_animation_list, action_animation_list, gender):
        self.base_animation_list = base_animation_list
        self.action_animation_list = action_animation_list
        self.gender = gender
        self.action = IDLE
        self.frame = 0
        self.flip = False

        # Reference position (fixed feet position)
        self.pos = pygame.math.Vector2(50, SCREEN_HEIGHT - 50)
        self.ground_y = SCREEN_HEIGHT - 50

        # Action state
        self.is_performing_action = False
        self.action_start_time = 0
        self.action_duration = 1000

        # Initial image
        self.image = self.get_current_frame()
        self.image = self.scale_current_image()
        self.rect = self.image.get_rect()
        self.rect.bottomleft = self.pos
        self.hitbox = self.rect.inflate(-60, -10)

        # Physics
        self.vel_x = 0
        self.vel_y = 0
        self.speed = 7
        self.gravity = 0.5
        self.jump_speed = -12
        self.in_air = False

        # Health
        self.current_health = 200
        self.maximum_health = 1000
        self.health_bar_length = 100
        self.health_ratio = self.maximum_health / self.health_bar_length

        self.last_update = pygame.time.get_ticks()
        self.animation_cooldown = 150

    # --- FRAME FUNCTIONS ---
    def get_current_frame(self):
        if self.action in [ATTACK, MINE]:
            return self.action_animation_list[self.action - ATTACK][self.frame]
        return self.base_animation_list[self.action][self.frame]

    def scale_current_image(self):
        img = self.get_current_frame()
        if self.action in [ATTACK, MINE]:
            scale_factor = 2.0 if self.gender == 'male' else 2.2
            img = pygame.transform.scale(img, (int(img.get_width()*scale_factor), int(img.get_height()*scale_factor)))
        else:
            img = pygame.transform.scale(img, (img.get_width()*SCALE, img.get_height()*SCALE))
        return img

    def get_animation_length(self):
        if self.action in [ATTACK, MINE]:
            return len(self.action_animation_list[self.action - ATTACK])
        return len(self.base_animation_list[self.action])

    # --- ACTIONS ---
    def perform_action(self, action_type):
        if not self.is_performing_action and not self.in_air:
            self.action = action_type
            self.frame = 0
            self.is_performing_action = True
            self.action_start_time = pygame.time.get_ticks()

    # --- HEALTH ---
    def get_damage(self, amount):
        self.current_health = max(self.current_health - amount, 0)
    def get_health(self, amount):
        self.current_health = min(self.current_health + amount, self.maximum_health)
    def draw_health_bar(self, surf):
        x = self.rect.centerx - self.health_bar_length//2
        y = self.rect.top - 15
        pygame.draw.rect(surf, (60,60,60), (x,y,self.health_bar_length,10))
        pygame.draw.rect(surf, (255,0,0), (x,y,self.current_health/self.health_ratio,10))
        pygame.draw.rect(surf, (255,255,255), (x,y,self.health_bar_length,2))

    # --- UPDATE ---
    def update(self):
        # End action if frame exceeds animation length
        if self.is_performing_action:
            if self.frame >= self.get_animation_length() - 1:
                self.is_performing_action = False
                self.action = IDLE
                self.frame = 0

        # Animate
        now = pygame.time.get_ticks()
        if now - self.last_update >= self.animation_cooldown:
            self.frame += 1
            self.last_update = now
            if self.frame >= self.get_animation_length():
                self.frame = 0

        # Image scaling
        self.image = self.scale_current_image()
        if self.flip:
            self.image = pygame.transform.flip(self.image, True, False)

        # Align bottom to ground
        self.rect = self.image.get_rect()
        self.rect.bottom = self.ground_y
        self.rect.x = self.pos.x

        # Physics (if not performing action)
        if not self.is_performing_action:
            self.vel_y += self.gravity
            self.pos.y += self.vel_y
            if self.pos.y >= self.ground_y:
                self.pos.y = self.ground_y
                self.vel_y = 0
                self.in_air = False

        # Horizontal movement
        self.pos.x += self.vel_x
        if self.pos.x < 0: self.pos.x = 0
        if self.pos.x + self.rect.width > SCREEN_WIDTH:
            self.pos.x = SCREEN_WIDTH - self.rect.width

        # Update rect & hitbox
        self.rect.bottom = self.pos.y
        self.hitbox = self.rect.inflate(-60, -10)

    # --- MOVEMENT ---
    def move(self, left, right, jump, attack=False, mine=False):
        if attack:
            self.perform_action(ATTACK)
            return
        if mine:
            self.perform_action(MINE)
            return
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

        prev_action = self.action
        if self.in_air:
            self.action = JUMP
        else:
            self.action = WALK if self.vel_x != 0 else IDLE
        if prev_action != self.action:
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

    male_img = pygame.image.load("Map\\Cutscene\\player_profile_m.png").convert_alpha()
    female_img = pygame.image.load("Map\\Cutscene\\player_profile_f.png").convert_alpha()

    max_width = SCREEN_WIDTH // 6
    max_height = SCREEN_HEIGHT // 3

    def scale_proportional(img, max_w, max_h):
        w,h = img.get_size()
        scale = min(max_w/w, max_h/h,1)
        return pygame.transform.smoothscale(img,(int(w*scale), int(h*scale)))

    male_img = scale_proportional(male_img, max_width, max_height)
    female_img = scale_proportional(female_img, max_width, max_height)

    margin = SCREEN_WIDTH // 6
    male_pos = (margin, SCREEN_HEIGHT // 3)
    female_pos = (SCREEN_WIDTH - margin - female_img.get_width(), SCREEN_HEIGHT // 3)

    male_rect = pygame.Rect(male_pos, (male_img.get_width(), male_img.get_height()))
    female_rect = pygame.Rect(female_pos, (female_img.get_width(), female_img.get_height()))

    bg_image = pygame.image.load("Map\\BACKGROUND\\genderbg1.png").convert()
    bg_image = pygame.transform.scale(bg_image, (SCREEN_WIDTH, SCREEN_HEIGHT))

    while selecting:
        screen.blit(bg_image, (0,0))
        title_text = font.render("Select Your Character Gender", True, 'white')
        screen.blit(title_text,(SCREEN_WIDTH//2 - title_text.get_width()//2,50))

        screen.blit(male_img, male_pos)
        screen.blit(female_img, female_pos)

        male_text = small_font.render("Male", True, 'white')
        female_text = small_font.render("Female", True, 'white')
        screen.blit(male_text,(male_pos[0]+male_img.get_width()//2 - male_text.get_width()//2,
                               male_pos[1]+male_img.get_height()+10))
        screen.blit(female_text,(female_pos[0]+female_img.get_width()//2 - female_text.get_width()//2,
                                 female_pos[1]+female_img.get_height()+10))
        instr_text = small_font.render("Click a portrait or press M/F to select", True, 'yellow')
        screen.blit(instr_text,(SCREEN_WIDTH//2 - instr_text.get_width()//2, SCREEN_HEIGHT-100))

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
            
        pygame.display.update()
        clock.tick(FPS)

    return selected_gender

# --- MAIN ---
def main():
    gender = gender_selection_screen()

    if gender=='male':
        base_sprite_image = pygame.image.load(os.path.join(script_dir,'Sprite_Img/male_spriteV8_flipped.png')).convert_alpha()
        attack_sprite_image = pygame.image.load(os.path.join(script_dir,'Sprite_Img/male_sprite_attack.png')).convert_alpha()
        mine_sprite_image = pygame.image.load(os.path.join(script_dir,'Sprite_Img/male_sprite_mine.png')).convert_alpha()
        action_width, action_height = 273,182
    else:
        base_sprite_image = pygame.image.load(os.path.join(script_dir,'Sprite_Img/female_spriteV1_flipped.png')).convert_alpha()
        attack_sprite_image = pygame.image.load(os.path.join(script_dir,'Sprite_Img/female_sprite_attack.png')).convert_alpha()
        mine_sprite_image = pygame.image.load(os.path.join(script_dir,'Sprite_Img/female_sprite_mine.png')).convert_alpha()
        action_width, action_height = 273,182

    base_animation_list = load_base_animations(base_sprite_image)
    action_animation_list = load_action_animations(attack_sprite_image, mine_sprite_image,
                                                   action_width, action_height, 0.3)

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

        # Test health bar
        if keys[pygame.K_UP]:
            player.get_health(50)
        if keys[pygame.K_DOWN]:
            player.get_damage(50)

        player.move(left, right, jump, attack, mine)
        player.update()

        screen.fill(BG)
        player.draw(screen)

        for event in pygame.event.get():
            if event.type==pygame.QUIT or (event.type==pygame.KEYDOWN and event.key==pygame.K_ESCAPE):
                run=False

        pygame.display.update()

    pygame.quit()

if __name__=="__main__":
    main()
