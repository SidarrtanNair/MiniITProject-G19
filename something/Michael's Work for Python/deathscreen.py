# so this shall be the death screen
import pygame
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

def draw_death():
    screen.blit(bg_deathscreen, (0,0))
    retry_btn = pygame.draw.rect(screen, 'light gray', [WIDTH//4 - 200, HEIGHT//2 + 200, 400, 80], 0, 5)
    quit_btn = pygame.draw.rect(screen, 'light gray', [WIDTH//1.3 - 200, HEIGHT//2 + 200 , 400, 80], 0, 5)

    screen.blit(small_font.render("Respawn", True, "black"), (WIDTH//4 - 75, HEIGHT//2 + 225))
    screen.blit(small_font.render("Back To Menu", True, "black"), (WIDTH//1.3 - 150, HEIGHT//2 + 225))

    if retry_btn.collidepoint(pygame.mouse.get_pos()) and pygame.mouse.get_pressed()[0]:
        return "respawn"
    if quit_btn.collidepoint(pygame.mouse.get_pos()) and pygame.mouse.get_pressed()[0]:
        return "menu"
    return "death"

run = True
while run:
    clock.tick(fps)
    if STATE == "death":
        STATE = draw_death()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    if STATE == "respawn":
        run = False
    elif STATE == "menu":
        run = False

    pygame.display.flip()
pygame.quit()
