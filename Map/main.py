import pygame 
from scene import generateworld
import time ,os

#=================INIT=============#
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

background = pygame.image.load("Map\\BACKGROUND\\sforest.png")
background = pygame.transform.scale(background, (WIDTH, HEIGHT))    

STATE = "intro"
volume = 0.5 
world = None
introplay = 0

#=============Start=================#
def play_click():
    click_sound.set_volume(volume)
    click_sound.play()

def play_menu_music():
    pygame.mixer.music.load( "menu_music.mp3")
    pygame.mixer.music.set_volume(0.5)  # adjust as you like
    pygame.mixer.music.play(-1)  # loop forever


#========Opening===============#
def intro_sequence():
    time.sleep(0.5)

    logo1 = pygame.image.load("Map\\BACKGROUND\\logo.png").convert_alpha()
    logo1 = pygame.transform.scale(logo1, (WIDTH//2, HEIGHT//2))
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

#========Title Menu Screen=========#
def title_menu_screen():
    title_bg = pygame.image.load("Map\\BACKGROUND\\sforest.png").convert_alpha()
    title_bg = pygame.transform.scale(title_bg, (WIDTH, HEIGHT))

    if not pygame.mixer.music.get_busy():
        pygame.mixer.music.load("Map\\MusicMan\\Game Main Menu Music ( 4th Album ) _ copyright free music [1ivlmbq6Td8].mp3")
        pygame.mixer.music.set_volume(volume)
        pygame.mixer.music.play(-1)

    fade_alpha = 0
    fade_speed = 5
    running = True

    while running:
        timer.tick(fps)
        screen.fill((0, 0, 0))

        bg_surf = title_bg.copy()
        if fade_alpha < 255:
            fade_alpha += fade_speed
        bg_surf.set_alpha(fade_alpha)
        screen.blit(bg_surf, (0, 0))

        title_text = title_font.render("Campus of Cosmos", True, "white")
        title_text.set_alpha(fade_alpha)
        screen.blit(title_text, (WIDTH//2 - title_text.get_width()//2, HEIGHT//3))

        menu_btn = pygame.draw.rect(screen, 'white', [WIDTH//2-280, HEIGHT-100, 260, 60], 0, 5)
        pygame.draw.rect(screen, 'dark gray', [WIDTH//2-280, HEIGHT-100, 260, 60], 5, 5)
        screen.blit(font.render('Play', True, 'black'), (WIDTH//2-190, HEIGHT-85))

        exit_btn = pygame.draw.rect(screen, 'white', [WIDTH//2+20, HEIGHT-100, 260, 60], 0, 5) 
        pygame.draw.rect(screen, 'dark gray', [WIDTH//2+20, HEIGHT-100, 260, 60], 5, 5)
        screen.blit(font.render('Exit Game', True, 'black'), (WIDTH//2+90, HEIGHT-85))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

        if menu_btn.collidepoint(pygame.mouse.get_pos()) and pygame.mouse.get_pressed()[0]:
            play_click()
            running = False
            return "menu"
        if exit_btn.collidepoint(pygame.mouse.get_pos()) and pygame.mouse.get_pressed()[0]:
            play_click()
            pygame.quit()
            exit()

        pygame.display.flip()

#========Other Screens=========#
def draw_game():
    title_text = title_font.render("Campus of Cosmos", True, "white")
    screen.blit(title_text, (WIDTH//2 - title_text.get_width()//2, HEIGHT//3))

    menu_btn = pygame.draw.rect(screen, 'white', [WIDTH//2-280, HEIGHT-100, 260, 60], 0, 5)
    pygame.draw.rect(screen, 'dark gray', [WIDTH//2-280, HEIGHT-100, 260, 60], 5, 5)
    screen.blit(font.render('Play', True, 'black'), (WIDTH//2-190, HEIGHT-85))

    exit_btn = pygame.draw.rect(screen, 'white', [WIDTH//2+20, HEIGHT-100, 260, 60], 0, 5) 
    pygame.draw.rect(screen, 'dark gray', [WIDTH//2+20, HEIGHT-100, 260, 60], 5, 5)
    screen.blit(font.render('Exit Game', True, 'black'), (WIDTH//2+90, HEIGHT-85))

    if menu_btn.collidepoint(pygame.mouse.get_pos()) and pygame.mouse.get_pressed()[0]:
        play_click()
        return "menu"
    if exit_btn.collidepoint(pygame.mouse.get_pos()) and pygame.mouse.get_pressed()[0]:
        play_click()
        pygame.quit()
        exit()
    return "game"

def draw_menu():
    panel = pygame.Surface((WIDTH//4, HEIGHT//1.25), pygame.SRCALPHA)
    panel.fill((128, 128, 128, 180))  
    screen.blit(panel, (0, HEIGHT//6))
    btns = ["New Game", "Continue", "Settings", "Credits", "Exit Main Menu"]
    positions = [20, 90, 160, 230, HEIGHT-100]
    for i, text in enumerate(btns):
        btn = pygame.draw.rect(screen, 'white', [0, HEIGHT//6 + positions[i] if i<4 else positions[i], WIDTH//4, 50], 0, 5)
        pygame.draw.rect(screen, 'dark gray', [0, HEIGHT//6 + positions[i] if i<4 else positions[i], WIDTH//4, 50], 5, 5)
        txt_surf = font.render(text, True, 'black')
        txt_rect = txt_surf.get_rect(center=btn.center)
        screen.blit(txt_surf, txt_rect)
        if btn.collidepoint(pygame.mouse.get_pos()) and pygame.mouse.get_pressed()[0]:
            play_click()
            if text == "New Game": return "new_game"
            elif text == "Continue": 
                pygame.mixer.unpause()
                return "continue"
            elif text == "Settings": 
                return "settings"
            elif text == "Credits": 
                return "credits"
            elif text == "Exit Main Menu":
                play_menu_music()
                return "game"
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
        pygame.mixer.music.stop() # only start if nothing else is playing
        pygame.mixer.music.load("Map\\MusicMan\\Game Main Menu Music ( 4th Album ) _ copyright free music [1ivlmbq6Td8].mp3")
        pygame.mixer.music.set_volume(volume)
        pygame.mixer.music.play(-1)

def draw_new_game():
    global world
    screen.fill((0,0,0))
    loading_text = font.render("Loading World....", True, "white")
    screen.blit(loading_text,(WIDTH//2 - loading_text.get_width()//2,HEIGHT//2))

    world = generateworld(pause_callback=pause_menu)
    world.play_music()
    state = world.run()
    if state == "menu":
        pygame.mixer.music.stop()
        return "menu"

def draw_continue():
    global world
    if world:
        world.play_music()
        state = world.run()
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
        pygame.mixer.music.stop()
        pygame.mixer.music.load("Map\MusicMan\worldbackground.mp3")
        pygame.mixer.music.set_volume(volume)
        pygame.mixer.music.play(-1)
        return "continue"


def draw_settings():
    global volume
    screen.fill("black")
    screen.blit(font.render("Settings", True, "white"), (WIDTH//3, HEIGHT//10))
    back_btn = pygame.draw.rect(screen, 'white', [10, 10, 150, 40], 0, 5)
    screen.blit(font.render("Back", True, "black"), (20, 15))
    slider_x, slider_y, slider_w, slider_h = WIDTH//4, HEIGHT//2, 500, 40
    pygame.draw.rect(screen, "gray", [slider_x, slider_y, slider_w, slider_h])
    pygame.draw.rect(screen, "white", [slider_x, slider_y, int(volume*slider_w), slider_h], border_radius=5)
    screen.blit(font.render(f"Volume: {int(volume*100)}%", True, "blue"), (slider_x, slider_y-50))
    if pygame.mouse.get_pressed()[0]:
        mx, my = pygame.mouse.get_pos()
        if slider_x <= mx <= slider_x+slider_w and slider_y-20 <= my <= slider_y+slider_h+20:
            volume = (mx - slider_x) / slider_w
            pygame.mixer.music.set_volume(volume)
    if back_btn.collidepoint(pygame.mouse.get_pos()) and pygame.mouse.get_pressed()[0]:
        return "menu"
    return "settings"

def draw_credits():
    screen.fill("black")
    screen.blit(font.render("insert funny image in credits screen", True, "white"), (WIDTH//3, HEIGHT//2))
    back_btn = pygame.draw.rect(screen, 'white', [10, 10, 150, 40], 0, 5)
    screen.blit(font.render("Back", True, "black"), (20, 15))
    if back_btn.collidepoint(pygame.mouse.get_pos()) and pygame.mouse.get_pressed()[0]:
        return "menu"
    return "credits"

#========Main Loop=========#
run = True
while run:
    screen.blit(pygame.transform.scale(background, (WIDTH, HEIGHT)), (0, 0))
    timer.tick(fps)

    if not introplay:
        intro_sequence()
        introplay = True
        STATE = title_menu_screen()

    if STATE == "game":
        STATE = draw_game()
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
            run = False

    pygame.display.flip()

pygame.quit()
