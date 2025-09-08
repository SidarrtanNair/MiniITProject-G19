# i had to follow this code from a video and the code from the video gave me too much stress. I legit crashed out. 
# So i just did this the long way since i understood the longer code
import pygame 
pygame.init()

WIDTH, HEIGHT = pygame.display.Info().current_w, pygame.display.Info().current_h
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
pygame.display.set_caption('Campus of Cosmos')
fps = 60 
timer = pygame.time.Clock()
font = pygame.font.Font(None, 40)
title_font = pygame.font.Font(None, 200)

# background (the 4th time of doing this)
background = pygame.image.load("momentsbeforedisaster.png")
background = pygame.transform.scale(background, (WIDTH, HEIGHT))    

STATE = "game" 

def draw_game():
    title_text = title_font.render("Campus of Cosmos", True, "purple")
    screen.blit(title_text, (WIDTH//2 - title_text.get_width()//2, HEIGHT//3))

    menu_btn = pygame.draw.rect(screen, 'light gray', [WIDTH//2-280, HEIGHT-100, 260, 60], 0, 5)
    pygame.draw.rect(screen, 'dark gray', [WIDTH//2-280, HEIGHT-100, 260, 60], 5, 5)
    screen.blit(font.render('Play', True, 'black'), (WIDTH//2-190, HEIGHT-85))

    exit_btn = pygame.draw.rect(screen, 'light gray', [WIDTH//2+20, HEIGHT-100, 260, 60], 0, 5) 
    pygame.draw.rect(screen, 'dark gray', [WIDTH//2+20, HEIGHT-100, 260, 60], 5, 5)
    screen.blit(font.render('Exit Game', True, 'black'), (WIDTH//2+90, HEIGHT-85))

    if menu_btn.collidepoint(pygame.mouse.get_pos()) and pygame.mouse.get_pressed()[0]:
        return "menu"
    if exit_btn.collidepoint(pygame.mouse.get_pos()) and pygame.mouse.get_pressed()[0]:
        pygame.quit()
        exit()
    return "game"

# okay this is just the buttons this took forever good lord
def draw_menu():
    pygame.draw.rect(screen, 'purple', [0, HEIGHT//6, WIDTH//4, HEIGHT//1.25])

    new_game_btn = pygame.draw.rect(screen, 'light gray', [0, HEIGHT//6+20, WIDTH//4, 50], 0, 5)
    pygame.draw.rect(screen, 'dark gray', [0, HEIGHT//6+20, WIDTH//4, 50], 5, 5)
    screen.blit(font.render('New Game', True, 'black'), (10, HEIGHT//6+25))

    continue_btn = pygame.draw.rect(screen, 'light gray', [0, HEIGHT//6+90, WIDTH//4, 50], 0, 5)
    pygame.draw.rect(screen, 'dark gray', [0, HEIGHT//6+90, WIDTH//4, 50], 5, 5)
    screen.blit(font.render('Continue', True, 'black'), (10, HEIGHT//6+95))

    settings_btn = pygame.draw.rect(screen, 'light gray', [0, HEIGHT//6+160, WIDTH//4, 50], 0, 5)
    pygame.draw.rect(screen, 'dark gray', [0, HEIGHT//6+160, WIDTH//4, 50], 5, 5)
    screen.blit(font.render('Settings', True, 'black'), (10, HEIGHT//6+165))

    credits_btn = pygame.draw.rect(screen, 'light gray', [0, HEIGHT//6+230, WIDTH//4, 50], 0, 5)
    pygame.draw.rect(screen, 'dark gray', [0, HEIGHT//6+230, WIDTH//4, 50], 5, 5)
    screen.blit(font.render('Credits', True, 'black'), (10, HEIGHT//6+235))

    exit_btn = pygame.draw.rect(screen, 'light gray', [0, HEIGHT-100, WIDTH//4, 50], 0, 5)
    pygame.draw.rect(screen, 'dark gray', [0, HEIGHT-100, WIDTH//4, 50], 5, 5)
    screen.blit(font.render('Exit Main Menu', True, 'black'), (10, HEIGHT-95))

# commands
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

# this is just screens for the buttons 
def draw_new_game():
    screen.fill("black")
    screen.blit(font.render("The New Game Screen! It's empty though-", True, "white"), (WIDTH//3, HEIGHT//2))
    back_btn = pygame.draw.rect(screen, 'light gray', [10, 10, 150, 40], 0, 5)
    screen.blit(font.render("Back", True, "black"), (20, 15))
    if back_btn.collidepoint(pygame.mouse.get_pos()) and pygame.mouse.get_pressed()[0]:
        return "menu"
    return "new_game"

def draw_continue():
    screen.fill("black")
    screen.blit(font.render("Continuing Your Game is here", True, "white"), (WIDTH//3, HEIGHT//2))
    back_btn = pygame.draw.rect(screen, 'light gray', [10, 10, 150, 40], 0, 5)
    screen.blit(font.render("Back", True, "black"), (20, 15))
    if back_btn.collidepoint(pygame.mouse.get_pos()) and pygame.mouse.get_pressed()[0]:
        return "menu"
    return "continue"

def draw_settings():
    screen.fill("black")
    screen.blit(font.render("This is for the Settings.", True, "white"), (WIDTH//3, HEIGHT//2))
    back_btn = pygame.draw.rect(screen, 'light gray', [10, 10, 150, 40], 0, 5)
    screen.blit(font.render("Back", True, "black"), (20, 15))
    if back_btn.collidepoint(pygame.mouse.get_pos()) and pygame.mouse.get_pressed()[0]:
        return "menu"
    return "settings"

def draw_credits():
    screen.fill("black")
    screen.blit(font.render("insert funny image in credits screen", True, "white"), (WIDTH//3, HEIGHT//2))
    back_btn = pygame.draw.rect(screen, 'light gray', [10, 10, 150, 40], 0, 5)
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
