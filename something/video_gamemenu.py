# i had to follow this code from a video and the code from the video gave me too much PTSD. I legit crashed out. 
# So i just did this the long way since i understood the longer code
import pygame 
pygame.init()

WIDTH = 1280
HEIGHT = 600
screen = pygame.display.set_mode([WIDTH, HEIGHT])
pygame.display.set_caption('Campus of Cosmos')
fps = 60 
timer = pygame.time.Clock()
font = pygame.font.Font(None, 40)

STATE = "game"

def draw_game():
    menu_btn = pygame.draw.rect(screen, 'light gray', [500, 450, 260, 40], 0, 5)
    pygame.draw.rect(screen, 'dark gray', [500, 450, 260, 40], 5, 5)
    text = font.render('Play', True, 'black')
    screen.blit(text, (515, 456))
    if menu_btn.collidepoint(pygame.mouse.get_pos()) and pygame.mouse.get_pressed()[0]:
        return "menu"
    return "game"

# okay this is just the buttons this took forever good lord
def draw_menu():
    pygame.draw.rect(screen, 'purple', [0, 100, 300, 500])

    new_game_btn = pygame.draw.rect(screen, 'light gray', [0, 120, 300, 50], 0, 5)
    pygame.draw.rect(screen, 'dark gray', [0, 120, 300, 50], 5, 5)
    screen.blit(font.render('New Game', True, 'black'), (10, 125))

    continue_btn = pygame.draw.rect(screen, 'light gray', [0, 190, 300, 50], 0, 5)
    pygame.draw.rect(screen, 'dark gray', [0, 190, 300, 50], 5, 5)
    screen.blit(font.render('Continue', True, 'black'), (10, 195))

    settings_btn = pygame.draw.rect(screen, 'light gray', [0, 260, 300, 50], 0, 5)
    pygame.draw.rect(screen, 'dark gray', [0, 260, 300, 50], 5, 5)
    screen.blit(font.render('Settings', True, 'black'), (10, 265))

    credits_btn = pygame.draw.rect(screen, 'light gray', [0, 330, 300, 50], 0, 5)
    pygame.draw.rect(screen, 'dark gray', [0, 330, 300, 50], 5, 5)
    screen.blit(font.render('Credits', True, 'black'), (10, 335))

    exit_btn = pygame.draw.rect(screen, 'light gray', [0, 500, 300, 50], 0, 5)
    pygame.draw.rect(screen, 'dark gray', [0, 500, 300, 50], 5, 5)
    screen.blit(font.render('Exit Main Menu', True, 'black'), (10, 505))

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
    screen.blit(font.render("The New Game Screen! It's empty though-", True, "white"), (300, 280))
    back_btn = pygame.draw.rect(screen, 'light gray', [10, 10, 150, 40], 0, 5)
    screen.blit(font.render("Back", True, "black"), (20, 15))
    if back_btn.collidepoint(pygame.mouse.get_pos()) and pygame.mouse.get_pressed()[0]:
        return "menu"
    return "new_game"

def draw_continue():
    screen.fill("black")
    screen.blit(font.render("Continuing Your Game is here", True, "white"), (300, 280))
    back_btn = pygame.draw.rect(screen, 'light gray', [10, 10, 150, 40], 0, 5)
    screen.blit(font.render("Back", True, "black"), (20, 15))
    if back_btn.collidepoint(pygame.mouse.get_pos()) and pygame.mouse.get_pressed()[0]:
        return "menu"
    return "continue"

def draw_settings():
    screen.fill("black")
    screen.blit(font.render("This is for the Settings.", True, "white"), (300, 280))
    back_btn = pygame.draw.rect(screen, 'light gray', [10, 10, 150, 40], 0, 5)
    screen.blit(font.render("Back", True, "black"), (20, 15))
    if back_btn.collidepoint(pygame.mouse.get_pos()) and pygame.mouse.get_pressed()[0]:
        return "menu"
    return "settings"

def draw_credits():
    screen.fill("black")
    screen.blit(font.render("insert funny image in credits screen", True, "white"), (300, 280))
    back_btn = pygame.draw.rect(screen, 'light gray', [10, 10, 150, 40], 0, 5)
    screen.blit(font.render("Back", True, "black"), (20, 15))
    if back_btn.collidepoint(pygame.mouse.get_pos()) and pygame.mouse.get_pressed()[0]:
        return "menu"
    return "credits"

run = True
while run:
    screen.fill('light blue')
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
