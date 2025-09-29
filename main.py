import pygame
from Map.scene import *
import time ,os , sys

#=================INIT================================================================================# IMRAN
pygame.init()
click_sound = pygame.mixer.Sound("Map\\Sounds\\user-interface-click-234656.mp3")
click_sound.set_volume(0.5)

WIDTH, HEIGHT = pygame.display.Info().current_w, pygame.display.Info().current_h
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Campus of Cosmos')
fps = 60 
timer = pygame.time.Clock()
font = pygame.font.Font(None, 40)
title_font = pygame.font.Font(None, 200)

background = pygame.image.load("Map\\BACKGROUND\\Menubackground.png")
background = pygame.transform.scale(background, (WIDTH, HEIGHT))    

STATE = "intro"
volume = 0.5 
world = None
introplay = 0

#=====================UIBUTTONIMAGES=============================================================================# IMRAN
ui_images = {
    "exit": pygame.image.load("Map\\UI+LOGO\\exit.png").convert_alpha(),
    "exit_menu": pygame.image.load("Map\\UI+LOGO\\exitmainmenu.png").convert_alpha(),
    "settings": pygame.image.load("Map\\UI+LOGO\\settings.png").convert_alpha(),
    "new_game": pygame.image.load("Map\\UI+LOGO\\newgame.png").convert_alpha(),
    "continue": pygame.image.load("Map\\UI+LOGO\\continue.png").convert_alpha(),
    "credits": pygame.image.load("Map\\UI+LOGO\\credits.png").convert_alpha() }

cutscene_male = [
    pygame.image.load("Map\\Cutscene\\male_intro1.png").convert_alpha(),
    pygame.image.load("Map\\Cutscene\\male_intro2.png").convert_alpha(),
    pygame.image.load("Map\\Cutscene\\male_intro3.png").convert_alpha()]

cutscene_female = [
    pygame.image.load("Map\\Cutscene\\female_intro1.png").convert_alpha(),
    pygame.image.load("Map\\Cutscene\\female_intro2.png").convert_alpha(),
    pygame.image.load("Map\\Cutscene\\female_intro3.png").convert_alpha()]

for i in range(3):
    cutscene_male[i] = pygame.transform.smoothscale(cutscene_male[i], (WIDTH, HEIGHT))
    cutscene_female[i] = pygame.transform.smoothscale(cutscene_female[i], (WIDTH, HEIGHT))
#=============Start=================#
def play_click():
    click_sound.set_volume(volume)
    click_sound.play()

def play_menu_music():
    pygame.mixer.music.load( "menu_music.mp3")
    pygame.mixer.music.set_volume(0.5)  
    pygame.mixer.music.play(-1)  
#========Opening===============#
def intro_sequence():
    time.sleep(0.5)

    logo1 = pygame.image.load("Map\\BACKGROUND\\logo.png").convert_alpha()

    logo_w, logo_h = logo1.get_size()

    scale_factor = min(WIDTH / logo_w * 0.6, HEIGHT / logo_h * 0.6)  
    new_size = (int(logo_w * scale_factor), int(logo_h * scale_factor))
    logo1 = pygame.transform.smoothscale(logo1, new_size)
    logo1_rect = logo1.get_rect(center=(WIDTH//2, HEIGHT//2))

    pygame.mixer.music.load("Map\\Sounds\\intro.mp3")
    pygame.mixer.music.set_volume(volume)
    pygame.mixer.music.play()

    fade_alpha = 0
    fade_speed = 2
    logo_linger = 120
    running_intro = True

    while running_intro:
        timer.tick(fps)
        screen.fill((0, 0, 0))

        if fade_alpha < 255:
            fade_alpha += fade_speed
        logo1.set_alpha(fade_alpha)
        screen.blit(logo1, logo1_rect)

        if fade_alpha >= 255:
            if logo_linger > 0:
                logo_linger -= 1
            else:
                running_intro = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                running_intro = False

        pygame.display.flip()

    character_imgs = [
        pygame.image.load("Map\\BACKGROUND\\michael.png").convert_alpha(),
        pygame.image.load("Map\\BACKGROUND\\imran.png").convert_alpha(),
        pygame.image.load("Map\\BACKGROUND\\siddartan.png").convert_alpha()
    ]
    character_names = ["Michael", "Imran", "Siddartan"]
    for i in range(3):
        character_imgs[i] = pygame.transform.scale(character_imgs[i], (WIDTH//6, HEIGHT//3))

    fade_in_alpha = 0
    display_frames = 180
    while display_frames > 0:
        timer.tick(fps)
        screen.fill((0, 0, 0))
        if fade_in_alpha < 255:
            fade_in_alpha += 3
        spacing = WIDTH//4

        for i in range(3):
            x = spacing*(i+1) - character_imgs[i].get_width()//2
            y = HEIGHT//4
            character_imgs[i].set_alpha(fade_in_alpha)
            screen.blit(character_imgs[i], (x, y))
            name_surf = font.render(character_names[i], True, "white")
            screen.blit(name_surf, (x + character_imgs[i].get_width()//2 - name_surf.get_width()//2, y + character_imgs[i].get_height() + 10))
            
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                display_frames = 0
        display_frames -= 1
        pygame.display.flip()

    pygame.mixer.music.stop()

screen = pygame.display.set_mode(screen.get_size(),pygame.NOFRAME)

def play_cutscene(images, fade_speed=5, linger_frames=120, music=None):
    if music:
        pygame.mixer.music.load(music)
        pygame.mixer.music.set_volume(volume)
        pygame.mixer.music.play(1)

    for img in images:
        fade_alpha = 0
        while fade_alpha < 255:
            timer.tick(fps)
            screen.fill((0,0,0))
            fade_alpha = min(fade_alpha + fade_speed, 255)
            temp_img = img.copy()
            temp_img.set_alpha(fade_alpha)
            screen.blit(temp_img, (0,0))
            pygame.display.flip()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                    return 
        linger = linger_frames
        while linger > 0:
            timer.tick(fps)
            screen.fill((0,0,0))
            img.set_alpha(255)
            screen.blit(img, (0,0))
            pygame.display.flip()
            linger -= 1
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                    return 


        while fade_alpha > 0:
            timer.tick(fps)
            screen.fill((0,0,0))
            fade_alpha = max(fade_alpha - fade_speed, 0)
            temp_img = img.copy()
            temp_img.set_alpha(fade_alpha)
            screen.blit(temp_img, (0,0))
            pygame.display.flip()   
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                    return 

#========Title Menu Screen=========#
def title_menu_screen():
    play_menu_music()
    title_bg = pygame.image.load("Map\\BACKGROUND\\Menubackground.png").convert_alpha()
    title_bg = pygame.transform.scale(title_bg, (WIDTH, HEIGHT))

    title_img = pygame.image.load("Map\\UI+LOGO\\title_campusofcosmos.png").convert_alpha()
    max_width = WIDTH // 2
    if title_img.get_width() > max_width:
        scale = max_width / title_img.get_width()
        title_img = pygame.transform.smoothscale(
            title_img,
            (int(title_img.get_width() * scale), int(title_img.get_height() * scale))
        )
    title_rect = title_img.get_rect(center=(WIDTH//2, HEIGHT//3))

    continue_img = ui_images["continue"]
    continue_scale = 0.5
    continue_img = pygame.transform.smoothscale(
        continue_img,
        (int(continue_img.get_width() * continue_scale), int(continue_img.get_height() * continue_scale))
    )
    continue_rect = continue_img.get_rect(center=(WIDTH//2, HEIGHT//2 + 250))

    exit_img = ui_images["exit"]
    exit_scale = 0.5
    exit_img = pygame.transform.smoothscale(
        exit_img,
        (int(exit_img.get_width() * exit_scale), int(exit_img.get_height() * exit_scale))
    )
    exit_rect = exit_img.get_rect(center=(WIDTH//2, continue_rect.bottom + 50))

    fade_alpha = 0
    fade_speed = 5
    running = True

    while running:
        timer.tick(fps)
        screen.fill((0, 0, 0))
        screen.blit(title_bg, (0, 0))

        if fade_alpha < 255:
            fade_alpha += fade_speed
        faded_title = title_img.copy()
        faded_title.set_alpha(fade_alpha)
        screen.blit(faded_title, title_rect)

        continue_btn = screen.blit(continue_img, continue_rect)
        exit_btn = screen.blit(exit_img, exit_rect)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

        if continue_btn.collidepoint(pygame.mouse.get_pos()) and pygame.mouse.get_pressed()[0]:
            play_click()
            pygame.time.wait(200)
            running = False
            return "menu"
        if exit_btn.collidepoint(pygame.mouse.get_pos()) and pygame.mouse.get_pressed()[0]:
            play_click()
            pygame.time.wait(200)
            pygame.quit()
            exit()

        pygame.display.flip()

#========Other Screens=========#
def draw_credits():
    screen.fill("black")

    credits = [
        "Campus of Cosmos",
        "",
        "Cosmos Studios Team",
        "Michael",
        "Settings, and Credits",
        "Sidarrtan",
        "Player & Gameplay Physics, character Selection, Enemy Physics & Spritesheet Frame,",
        "Boss Physics & Animation",
        "Imran",
        "Main Menu, Opening Cutscene & Ending Cutscene, Intro Screen, World Generation,",
        "Saving/Continue World, Inventory System, World Map, Level Generation, Crafting Recipe Logic,",
        "Music Background, Timer, Healthbar, Collison Detection, Placing & Destroying Blocks", "Final level generation",
        "Special Thanks to:",
        "Miss Suhaini",
        "Thank you for playing our game!",
    ]

    if not hasattr(draw_credits, "scroll_y"):
        draw_credits.scroll_y = HEIGHT

    y = draw_credits.scroll_y
    for line in credits:
        text = font.render(line, True, "white")
        screen.blit(text, (WIDTH//2 - text.get_width()//2, y))
        y += 40

    draw_credits.scroll_y -= 2

    if y < 0:
        draw_credits.scroll_y = HEIGHT

    back_btn = pygame.draw.rect(screen, 'white', [10, 10, 150, 40], 0, 5)
    screen.blit(font.render("Back", True, "black"), (20, 15))
    if back_btn.collidepoint(pygame.mouse.get_pos()) and pygame.mouse.get_pressed()[0]:
        draw_credits.scroll_y = HEIGHT
        return "menu"

    return "credits"

def draw_menu():
    panel = pygame.Surface((WIDTH//4, HEIGHT//1.25), pygame.SRCALPHA)
    panel.fill((128, 128, 128, 180))  
    screen.blit(panel, (0, HEIGHT//6))
    btns = [
        ("new_game", "new_game"),
        ("continue", "continue"),
        ("settings", "settings"),
        ("credits", "credits"),
        ("exit_menu", "game")]
    positions = [20, 110, 200, 290, HEIGHT-150]

    for i, (key, state) in enumerate(btns):
        img = ui_images[key]
        max_width = WIDTH//4 - 40
        if img.get_width() > max_width:
            scale = max_width / img.get_width()
            img = pygame.transform.smoothscale(
                img,
                (int(img.get_width() * scale), int(img.get_height() * scale))
            )

        btn_rect = screen.blit(img, (20, HEIGHT//6 + positions[i] if i < 4 else positions[i]))

        if btn_rect.collidepoint(pygame.mouse.get_pos()) and pygame.mouse.get_pressed()[0]:
            play_click()
            return state
    return "menu"

def pause_menu(screen, frozenbg):
    pygame.mixer.music.pause()
    font = pygame.font.Font(None, 80)
    while True:
        screen.blit(frozenbg, (0, 0))
        continue_btn = pygame.draw.rect(screen, 'light gray', [screen.get_width()//2-200, screen.get_height()//2-100, 400, 80], 0, 5)
        pygame.draw.rect(screen, 'dark gray', [screen.get_width()//2-200, screen.get_height()//2-100, 400, 80], 5, 5)
        continue_text = font.render('Continue', True, 'black')
        continue_text_rec = continue_text.get_rect(center=continue_btn.center)
        screen.blit(continue_text, continue_text_rec)
        exit_btn = pygame.draw.rect(screen, 'light gray', [screen.get_width()//2-200, screen.get_height()//2+20, 400, 80], 0, 5)
        pygame.draw.rect(screen, 'dark gray', [screen.get_width()//2-200, screen.get_height()//2+20, 400, 80], 5, 5)
        exit_text = font.render('Exit', True, 'black')
        exit_text_rect = exit_text.get_rect(center=exit_btn.center)
        screen.blit(exit_text, exit_text_rect)
        pygame.display.flip()
        timer.tick(fps)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if continue_btn.collidepoint(pygame.mouse.get_pos()):
                    pygame.mixer.unpause()
                    return "continue"
                if exit_btn.collidepoint(pygame.mouse.get_pos()):
                    return "exit"

def play_menu_music():
    if not pygame.mixer.music.get_busy(): 
        pygame.mixer.music.stop() 
        pygame.mixer.music.load("Map\\MusicMan\\Game Main Menu Music ( 4th Album ) _ copyright free music [1ivlmbq6Td8].mp3")
        pygame.mixer.music.set_volume(volume + 1)
        pygame.mixer.music.play(-1)

def draw_continue():
    global world
    if world:
        pygame.mixer.music.set_volume(volume)
        pygame.mixer.music.play(-1)
        state = world.running()
        if state == "menu":
            pygame.mixer.music.stop()
            return "menu"
        return state
    else:
        screen.fill("black")
        screen.blit(font.render("No game to continue", True, "white"), (WIDTH//3, HEIGHT//2))
        back_btn = pygame.draw.rect(screen, 'white', [10, 10, 150, 40], 0, 5)
        screen.blit(font.render("Back", True, "black"), (20, 15))
        if back_btn.collidepoint(pygame.mouse.get_pos()) and pygame.mouse.get_pressed()[0]:
            play_click()
            return "menu"
        
        return "continue"

pygame.mixer_music.set_volume(1.0)
volume = 1.0
pygame.mixer.music.set_volume(volume)

def draw_settings():
    global volume
    screen.fill("black")
    title_img = ui_images["settings"]
    max_width = WIDTH//2
    if title_img.get_width() > max_width:
        scale = max_width / title_img.get_width()
        title_img = pygame.transform.smoothscale(
            title_img,
            (int(title_img.get_width()*scale), int(title_img.get_height()*scale))
        )
    screen.blit(title_img, (WIDTH//3, HEIGHT//10))

    slider_x, slider_y, slider_w, slider_h = WIDTH//4, HEIGHT//2, 500, 40
    pygame.draw.rect(screen, "gray", [slider_x, slider_y, slider_w, slider_h])
    pygame.draw.rect(screen, "white", [slider_x, slider_y, int(volume*slider_w), slider_h], border_radius=5)
    screen.blit(font.render(f"Volume: {int(volume*100)}%", True, "blue"), (slider_x, slider_y-50))

    if pygame.mouse.get_pressed()[0]:
        mx, my = pygame.mouse.get_pos()
        if slider_x <= mx <= slider_x+slider_w and slider_y-20 <= my <= slider_y+slider_h+20:
            volume = (mx - slider_x) / slider_w
            pygame.mixer.music.set_volume(volume)
    
    back_img = ui_images["exit_menu"]
    max_width = 300
    if back_img.get_width() > max_width:
        scale = max_width / back_img.get_width()
        back_img = pygame.transform.smoothscale(
            back_img,
            (int(back_img.get_width() * scale), int(back_img.get_height() * scale))
        )
    back_rect = screen.blit(back_img, (10, 10))
    if back_rect.collidepoint(pygame.mouse.get_pos()) and pygame.mouse.get_pressed()[0]:
        play_click()
        return "menu"

    return "settings"

def show_dialogue(screen, text, portrait_img=None, typing_sound=None, clock=None):
    if clock is None:
        clock = pygame.time.Clock()
    
    font = pygame.font.SysFont("Consolas", 24)
    line_spacing = 30
    text_color = (255, 255, 255)
    type_speed = 40#ms

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
    box_x = (screen.get_width() - box_width) // 2
    box_y = screen.get_height() - box_height - 20

    while waiting_for_click:
        box_surf = pygame.Surface((box_width, box_height), pygame.SRCALPHA)
        box_surf.fill((0, 0, 0, 200))
        pygame.draw.rect(box_surf, (255, 255, 255), box_surf.get_rect(), 2)
        screen.blit(box_surf, (box_x, box_y))

        if portrait_img:
            screen.blit(portrait_img, (box_x + 10, box_y + box_height - portrait_img.get_height() - 10))

        now = pygame.time.get_ticks()
        if current_index < len(rendered_text) and now - last_update > type_speed:
            current_index += 1
            last_update = now
            if typing_sound:
                typing_sound.play()

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
            screen.blit(text_surf, (box_x + portrait_offset_x + 10, box_y + 10 + i * line_spacing))

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

        clock.tick(60)

def draw_new_game():
    global world
    screen.fill((0,0,0))
    pygame.display.flip()
    character_choice = gender_selection_screen()  
    if character_choice == "male":
        play_cutscene(cutscene_male, music="Map\\MusicMan\\storymusic1.mp3")
    elif character_choice == "female":
        play_cutscene(cutscene_female, music="Map\\MusicMan\\storymusic1.mp3")
    if character_choice == "male":
        portrait_img = pygame.image.load("Map\\Cutscene\\player_profile_m.png").convert_alpha()
    else:
        portrait_img = pygame.image.load("Map\\Cutscene\\player_profile_f.png").convert_alpha()

    pygame.mixer.music.load("Map\\Sounds\\TypeWriter- Sound Effect (Final Cut).mp3")
    pygame.mixer.music.play(1)
    show_dialogue(screen, 
                "Where tf am I, better get back through that portal, I have an assignment to do!",
                portrait_img=portrait_img,)
   
    world = generateworld(pause_callback=pause_menu, gender=character_choice) 
    state = world.running()
    if state == "menu":
        pygame.mixer.music.stop()
        return "menu"
#========Main Loop=========#
running = True
while running:
    screen.blit(pygame.transform.scale(background, (WIDTH, HEIGHT)), (0, 0))
    timer.tick(fps)

    if not introplay:
        intro_sequence()
        introplay = True
        STATE = title_menu_screen()

    if STATE == "game":
        STATE = title_menu_screen()
    elif STATE == "menu":
        STATE = draw_menu()
    elif STATE == "new_game":
        STATE = draw_new_game()
    elif STATE == "continue":
        STATE = draw_continue()
    elif STATE == "settings":
        STATE = draw_settings()
    elif STATE == "credits":
        STATE = draw_credits()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    pygame.display.flip()

pygame.quit()
