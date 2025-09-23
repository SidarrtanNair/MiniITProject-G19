import pygame 
from scene import generateworld
pygame.init()

WIDTH, HEIGHT = pygame.display.Info().current_w, pygame.display.Info().current_h
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Campus of Cosmos')
fps = 60 
timer = pygame.time.Clock()
font = pygame.font.Font(None, 40)
title_font = pygame.font.Font(None, 200)

background = pygame.image.load("Map\\BACKGROUND\\sforest.png")
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
        return "menu"
    if exit_btn.collidepoint(pygame.mouse.get_pos()) and pygame.mouse.get_pressed()[0]:
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
        return "new_game"
    if continue_btn.collidepoint(pygame.mouse.get_pos()) and pygame.mouse.get_pressed()[0]:
        return "continue"
    if settings_btn.collidepoint(pygame.mouse.get_pos()) and pygame.mouse.get_pressed()[0]:
        return "settings"
    if credits_btn.collidepoint(pygame.mouse.get_pos()) and pygame.mouse.get_pressed()[0]:
        return "credits"
    if exit_btn.collidepoint(pygame.mouse.get_pos()) and pygame.mouse.get_pressed()[0]:
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
    from scene import generateworld
    world = generateworld(pause_callback=pause_menu)
    state = world.run()
    if state =="menu":
        return "menu"

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
            return "menu"
        return "continue"

def draw_settings():
    global volume
    screen.fill("black")
    screen.blit(font.render("Settings", True, "white"), (WIDTH//3, HEIGHT//10))
    back_btn = pygame.draw.rect(screen, 'white', [10, 10, 150, 40], 0, 5)
    screen.blit(font.render("Back", True, "black"), (20, 15))
    slider_x, slider_y, slider_w, slider_h = WIDTH//4, HEIGHT//2, 500, 40
    pygame.draw.rect(screen, "gray", [slider_x, slider_y, slider_w, slider_h])
    filled_w = int(volume * slider_w)
    pygame.draw.rect(screen, "white", [slider_x, slider_y, filled_w, slider_h], border_radius=5)
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

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    pygame.display.flip()
pygame.quit()
