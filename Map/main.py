<<<<<<< HEAD:Map/video_gamemenu.py
# making changes to settings
import pygame, json, os
=======
import pygame 
>>>>>>> 00e1455fbe346fd1e6fc00c1a846ce5592a6f333:Map/main.py
from scene import generateworld
pygame.init()
pygame.mixer.init()

clicking_sound = pygame.mixer.Sound("taco.mp3")

WIDTH, HEIGHT = pygame.display.Info().current_w, pygame.display.Info().current_h
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Campus of Cosmos')
fps = 60 
timer = pygame.time.Clock()
font = pygame.font.Font(None, 40)
title_font = pygame.font.Font(None, 200)

<<<<<<< HEAD:Map/video_gamemenu.py
KEYBINDS_FILE = "keybinds.json"

keybinds = {"left": pygame.K_a, "right": pygame.K_d, "jump": pygame.K_SPACE}
rebinding_key = None

if os.path.exists(KEYBINDS_FILE):
    with open(KEYBINDS_FILE, "r") as m:
        data = json.load(m)
        keybinds = {k: v for k, v in data.items()}

background = pygame.image.load("Map\BACKGROUND\sforest.png")
=======
background = pygame.image.load("Map\\BACKGROUND\\sforest.png")
>>>>>>> 00e1455fbe346fd1e6fc00c1a846ce5592a6f333:Map/main.py
background = pygame.transform.scale(background, (WIDTH, HEIGHT))    

STATE = "game"
volume = 0.5 

#continuelohic#
world = None

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
        clicking_sound.play()
        return "menu"
    if exit_btn.collidepoint(pygame.mouse.get_pos()) and pygame.mouse.get_pressed()[0]:
        clicking_sound.play()
        pygame.quit()
        exit()
    return "game"

def draw_menu():
    panel = pygame.Surface((WIDTH//4, HEIGHT//1.25), pygame.SRCALPHA)
    panel.fill((128, 128, 128, 180))  
    screen.blit(panel, (0, HEIGHT//6))

    
    new_game_btn = pygame.draw.rect(screen, 'white', [0, HEIGHT//6+20, WIDTH//4, 50], 0, 5)
    pygame.draw.rect(screen, 'dark gray', [0, HEIGHT//6+20, WIDTH//4, 50], 5, 5)
    new_game_text = font.render('New Game', True, 'black')
    new_game_text_rect = new_game_text.get_rect(center=new_game_btn.center)
    screen.blit(new_game_text, new_game_text_rect)


    continue_btn = pygame.draw.rect(screen, 'white', [0, HEIGHT//6+90, WIDTH//4, 50], 0, 5)
    pygame.draw.rect(screen, 'dark gray', [0, HEIGHT//6+90, WIDTH//4, 50], 5, 5)
    continue_text = font.render('Continue', True, 'black')
    continue_text_rect = continue_text.get_rect(center=continue_btn.center)
    screen.blit(continue_text, continue_text_rect)


    settings_btn = pygame.draw.rect(screen, 'white', [0, HEIGHT//6+160, WIDTH//4, 50], 0, 5)
    pygame.draw.rect(screen, 'dark gray', [0, HEIGHT//6+160, WIDTH//4, 50], 5, 5)
    settings_text = font.render('Settings', True, 'black')
    settings_text_rect = settings_text.get_rect(center=settings_btn.center)
    screen.blit(settings_text, settings_text_rect)

  
    credits_btn = pygame.draw.rect(screen, 'white', [0, HEIGHT//6+230, WIDTH//4, 50], 0, 5)
    pygame.draw.rect(screen, 'dark gray', [0, HEIGHT//6+230, WIDTH//4, 50], 5, 5)
    credits_text = font.render('Credits', True, 'black')
    credits_text_rect = credits_text.get_rect(center=credits_btn.center)
    screen.blit(credits_text, credits_text_rect)

   
    exit_btn = pygame.draw.rect(screen, 'white', [0, HEIGHT-100, WIDTH//4, 50], 0, 5)
    pygame.draw.rect(screen, 'dark gray', [0, HEIGHT-100, WIDTH//4, 50], 5, 5)
    exit_text = font.render('Exit Main Menu', True, 'black')
    exit_text_rect = exit_text.get_rect(center=exit_btn.center)
    screen.blit(exit_text, exit_text_rect)

    if new_game_btn.collidepoint(pygame.mouse.get_pos()) and pygame.mouse.get_pressed()[0]:
        clicking_sound.play()
        return "new_game"
    if continue_btn.collidepoint(pygame.mouse.get_pos()) and pygame.mouse.get_pressed()[0]:
        clicking_sound.play()
        return "continue"
    if settings_btn.collidepoint(pygame.mouse.get_pos()) and pygame.mouse.get_pressed()[0]:
        clicking_sound.play()
        return "settings"
    if credits_btn.collidepoint(pygame.mouse.get_pos()) and pygame.mouse.get_pressed()[0]:
        clicking_sound.play()
        return "credits"
    if exit_btn.collidepoint(pygame.mouse.get_pos()) and pygame.mouse.get_pressed()[0]:
        clicking_sound.play()
        return "game"

    return "menu"

#Imrans#
def pause_menu(screen, frozenbg):
    font = pygame.font.Font(None, 80)
    run = True
    while run:
        screen.blit(frozenbg, (0, 0))

        continue_btn = pygame.draw.rect(screen, 'light gray', 
                                        [screen.get_width()//2-200, 
                                         screen.get_height()//2-100, 400, 80], 
                                         0, 5)
        pygame.draw.rect(screen, 'dark gray', 
                         [screen.get_width()//2-200, 
                          screen.get_height()//2-100, 400, 80], 
                          5, 5)
        continue_text = font.render('Continue', True, 'black')
        continue_text_rec = continue_text.get_rect(center=continue_btn.center)
        screen.blit(continue_text, continue_text_rec)

        exit_btn = pygame.draw.rect(screen, 'light gray', 
                                    [screen.get_width()//2-200, 
                                     screen.get_height()//2+20, 400, 80], 
                                     0, 5)
        pygame.draw.rect(screen, 'dark gray',
                          [screen.get_width()//2-200, 
                           screen.get_height()//2+20, 400, 80],
                             5, 5)
        
        exit_text = font.render('Exit', True, 'black')
        exit_text_rect = exit_text.get_rect(center=exit_btn.center)
        screen.blit(exit_text, exit_text_rect)


        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if continue_btn.collidepoint(pygame.mouse.get_pos()):
                    return "continue"
                if exit_btn.collidepoint(pygame.mouse.get_pos()):
                    return "exit"

#Imrans#
def draw_new_game():
    global world
<<<<<<< HEAD:Map/video_gamemenu.py
    world = generateworld()
    state = world.run() 
    return state
=======
    from scene import generateworld
    world = generateworld(pause_callback=pause_menu)
    state = world.run()
    if state =="menu":
        return "menu"
>>>>>>> 00e1455fbe346fd1e6fc00c1a846ce5592a6f333:Map/main.py

def draw_continue():
    global world
    if world:
        state = world.run()
        return state
    else:
        screen.fill("black")
        screen.blit(font.render("No game to continue", True, "white"), (WIDTH//3, HEIGHT//2))
        back_btn = pygame.draw.rect(screen, 'white', [10, 10, 150, 40], 0, 5)
        screen.blit(font.render("Back", True, "black"), (20, 15))
        if back_btn.collidepoint(pygame.mouse.get_pos()) and pygame.mouse.get_pressed()[0]:
            clicking_sound.play()
            return "menu"
        return "continue"


def draw_settings():
    global volume, rebinding_key
    screen.fill("black")
    screen.blit(font.render("Settings", True, "white"), (WIDTH//3, HEIGHT//10))
    back_btn = pygame.draw.rect(screen, 'white', [10, 10, 150, 40], 0, 5)
    screen.blit(font.render("Back", True, "black"), (20, 15))
<<<<<<< HEAD:Map/video_gamemenu.py
    slider_x, slider_y, slider_w, slider_h = WIDTH//4, HEIGHT//4, 500, 40  # making the audio sliders. Ik no one asked but im still doing it anyway
=======
    slider_x, slider_y, slider_w, slider_h = WIDTH//4, HEIGHT//2, 500, 40
>>>>>>> 00e1455fbe346fd1e6fc00c1a846ce5592a6f333:Map/main.py
    pygame.draw.rect(screen, "gray", [slider_x, slider_y, slider_w, slider_h])
    filled_w = int(volume * slider_w)
    pygame.draw.rect(screen, "white", [slider_x, slider_y, filled_w, slider_h], border_radius=5)
    screen.blit(font.render(f"Volume: {int(volume*100)}%", True, "blue"), (slider_x, slider_y-50))
    if pygame.mouse.get_pressed()[0]:
        mx, my = pygame.mouse.get_pos()
        if slider_y-20 <= my <= slider_y+slider_h+20:
            mx = max(slider_x, min(mx, slider_x+slider_w))
            volume = (mx - slider_x) / slider_w
            pygame.mixer.music.set_volume(volume)
    # trying to do keybinds
    keybind_y = slider_y + 150
    screen.blit(font.render("The Keybinds", True, "orange"), (slider_x, keybind_y))

    # its only moving left and right for now, later gotta implement keybinds for adding health
    left_btn = pygame.draw.rect(screen, 'light gray', [slider_x, keybind_y+50, 250, 40], 0, 5) # the left button obviously
    left_text = f"LEFT: {pygame.key.name(keybinds['left'])}"
    screen.blit(font.render(left_text, True, "black"), (slider_x+10, keybind_y+55))

    right_btn = pygame.draw.rect(screen, 'light gray', [slider_x, keybind_y+100, 250, 40], 0, 5)
    right_text = f"RIGHT:{pygame.key.name(keybinds['right'])}"
    screen.blit(font.render(right_text, True, "black"), (slider_x+10, keybind_y+105))

    if rebinding_key is None:
        if left_btn.collidepoint(pygame.mouse.get_pos()) and pygame.mouse.get_pressed()[0]:
            rebinding_key = "left"
        elif right_btn.collidepoint(pygame.mouse.get_pos()) and pygame.mouse.get_pressed()[0]:
            rebinding_key = "right"

    if rebinding_key:
        screen.blit(font.render(f"Enter key for {rebinding_key.capitalize()}", True, "yellow"), (slider_x, keybind_y+160))
    if back_btn.collidepoint(pygame.mouse.get_pos()) and pygame.mouse.get_pressed()[0]:
        clicking_sound.play()
        return "menu"
    return "settings"

def draw_credits():
    screen.fill("black")
    screen.blit(font.render("insert funny image in credits screen", True, "white"), (WIDTH//3, HEIGHT//2))
    back_btn = pygame.draw.rect(screen, 'white', [10, 10, 150, 40], 0, 5)
    screen.blit(font.render("Back", True, "black"), (20, 15))
    if back_btn.collidepoint(pygame.mouse.get_pos()) and pygame.mouse.get_pressed()[0]:
        clicking_sound.play()
        return "menu"
    return "credits"

def run_deathscreen():
    pygame.init()
    info = pygame.display.Info()
    WIDTH, HEIGHT = info.current_w, info.current_h
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption('Death Screen')
    fps = 60
    clock = pygame.time.Clock()
    bg_deathscreen = pygame.image.load("Doors_DS.jpg")
    bg_deathscreen = pygame.transform.scale(bg_deathscreen, (WIDTH, HEIGHT))
    font = pygame.font.Font(None, 120)
    small_font = pygame.font.Font(None, 60)

    STATE = "death"
    run = True
    while run:
        clock.tick(fps)
        screen.blit(bg_deathscreen, (0,0))
        
        retry_btn = pygame.draw.rect(screen, 'light gray', [WIDTH//4 - 200, HEIGHT//2 + 200, 400, 80], 0, 5)
        quit_btn = pygame.draw.rect(screen, 'light gray', [WIDTH//1.3 - 200, HEIGHT//2 + 200 , 400, 80], 0, 5)

        screen.blit(small_font.render("Respawn", True, "black"), (WIDTH//4 - 75, HEIGHT//2 + 225))
        screen.blit(small_font.render("Back To Menu", True, "black"), (WIDTH//1.3 - 150, HEIGHT//2 + 225))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                return "menu"

        if retry_btn.collidepoint(pygame.mouse.get_pos()) and pygame.mouse.get_pressed()[0]:
            if world:
                world.init_player()
            return world.run()
        if quit_btn.collidepoint(pygame.mouse.get_pos()) and pygame.mouse.get_pressed()[0]:
            return "menu"

        pygame.display.flip()

run = True
while run:
    screen.blit(pygame.transform.scale(background, (WIDTH, HEIGHT)), (0, 0))
    timer.tick(fps)

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
    elif STATE == "death":
        STATE = run_deathscreen()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_F10:
                STATE = "death"
            else:
                 STATE = "game"

        if event.type == pygame.KEYDOWN and rebinding_key:
            keybinds[rebinding_key] = event.key
            with open(KEYBINDS_FILE, "w") as m:
                json.dump(keybinds, m)
            print(f"Your {rebinding_key} key is changed to {pygame.key.name(event.key)}")
            rebinding_key = None

    pygame.display.flip()
pygame.quit()