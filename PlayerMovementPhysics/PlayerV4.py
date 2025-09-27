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
        self.flip = False

        # Reference position for bottom-left (prevents blit shift)
        self.pos = pygame.math.Vector2(50, SCREEN_HEIGHT - 50)

        # Action state
        self.is_performing_action = False
        self.action_start_time = 0
        self.action_duration = 1000  # 1 sec

        # Initial image
        self.image = self.get_current_frame()
        self.image = self.scale_current_image()
        self.rect = self.image.get_rect()
        self.rect.bottomleft = self.pos

        # Hitbox
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

    def get_current_frame(self):
        if self.action in [ATTACK, MINE]:
            index = self.action - ATTACK
            return self.action_animation_list[index][self.frame]
        return self.base_animation_list[self.action][self.frame]

    def scale_current_image(self):
        img = self.get_current_frame()
        if self.action in [ATTACK, MINE]:
            scale_factor = 2.0 if self.gender == 'male' else 2.2
            img = pygame.transform.scale(img, 
                (int(img.get_width()*scale_factor), int(img.get_height()*scale_factor)))
        else:
            img = pygame.transform.scale(img, (img.get_width()*SCALE, img.get_height()*SCALE))
        return img

    def get_animation_length(self):
        if self.action in [ATTACK, MINE]:
            return len(self.action_animation_list[self.action - ATTACK])
        return len(self.base_animation_list[self.action])

    def perform_action(self, action_type):
        if not self.is_performing_action and not self.in_air:
            self.action = action_type
            self.frame = 0
            self.is_performing_action = True
            self.action_start_time = pygame.time.get_ticks()

    # Health
    def take_damage(self, amount):
        self.health = max(0, self.health - amount)

    # Healing Logic
    def heal(self, amount):
        self.health = min(self.max_health, self.health + amount)
    def draw_health_bar(self, surf, camera_x):
        total_hearts = 10
        heart_width = self.heart_img.get_width()
        heart_height = self.heart_img.get_height()

        hearts_to_show = int(self.health / 10)

        x_start = self.rect.centerx + camera_x - (heart_width * total_hearts) // 2
        y = self.rect.top - 25  # above player

        for i in range(total_hearts):
            x = x_start + i * heart_width
            if i < hearts_to_show:
                # Full heart
                surf.blit(self.heart_img, (x, y))
            else:
                # Greyed-out heart
                grey_heart = self.heart_img.copy()
                grey_heart.fill((100, 100, 100, 255), special_flags=pygame.BLEND_RGB_MULT)
                surf.blit(grey_heart, (x, y))


    # Movement & Animation
    def update(self):
        # End action if duration exceeded
        if self.is_performing_action:
            if pygame.time.get_ticks() - self.action_start_time >= self.action_duration:
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
                if self.is_performing_action:
                    self.is_performing_action = False
                    self.action = IDLE

        # Update image and rect using consistent bottom-left position
        self.image = self.scale_current_image()
        if self.flip:
            self.image = pygame.transform.flip(self.image, True, False)

        self.rect = self.image.get_rect()
        self.rect.bottomleft = self.pos

        # Physics (if not performing action)
        if not self.is_performing_action:
            self.vel_y += self.gravity
            self.pos.y += self.vel_y
            if self.pos.y >= SCREEN_HEIGHT - 50:
                self.pos.y = SCREEN_HEIGHT - 50
                self.vel_y = 0
                self.in_air = False

            self.pos.x += self.vel_x
            if self.pos.x < 0: self.pos.x = 0
            if self.pos.x + self.rect.width > SCREEN_WIDTH:
                self.pos.x = SCREEN_WIDTH - self.rect.width

        # Update hitbox
        self.rect.bottomleft = self.pos
        self.hitbox = self.rect.inflate(-60, -10)

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