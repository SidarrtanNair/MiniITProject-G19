# so this shall be the death screen
import pygame, sys
pygame.init()

info = pygame.display.Info()
WIDTH, HEIGHT = info.current_w, info.current_h
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Death Screen')
fps = 60
clock = pygame.time.Clock()
bg_deathscreen = pygame.image.load("dead_text.jpg")
bg_deathscreen = pygame.transform.scale(bg_deathscreen, (WIDTH, HEIGHT))
font = pygame.font.Font(None, 120)
small_font = pygame.font.Font(None, 60)

STATE = "death"

def draw_death():
    screen.blit(bg_deathscreen, (0,0))
    retry_btn = pygame.draw.rect(screen, 'light gray', [WIDTH//4 - 200, HEIGHT//2 + 200, 400, 80], 0, 5)
    quit_btn = pygame.draw.rect(screen, 'light gray', [WIDTH//1.3 - 200, HEIGHT//2 + 200 , 400, 80], 0, 5)

    screen.blit(small_font.render("Respawn", True, "black"), (WIDTH//4 - 75, HEIGHT//2 + 225))
    screen.blit(small_font.render("Back To Menu", True, "black"), (WIDTH//1.3 - 150, HEIGHT//2 + 225))

    clicked_what = None


    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.MOUSEBUTTONDOWN:
            if retry_btn.collidepoint(pygame.mouse.get_pos()):
                clicked_what = "respawn"
            if quit_btn.collidepoint(pygame.mouse.get_pos()):
                clicked_what = "menu"
            
    return clicked_what


