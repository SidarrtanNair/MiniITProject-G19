# so this shall be the death screen
import pygame
pygame.init()

info = pygame.display.Info()
WIDTH, HEIGHT = info.current_w, info.current_h
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
pygame.display.set_caption('Death Screen')
fps = 60
clock = pygame.time.Clock()
bg_deathscreen = pygame.image.load("cosmos3rd.jpg")
bg_deathscreen = pygame.transform.scale(bg_deathscreen, (WIDTH, HEIGHT))
font = pygame.font.Font(None, 120)
small_font = pygame.font.Font(None, 60)

STATE = "death"

def draw_death():
    screen.fill("black")
    text = font.render("Ain't no way bro just died", True, "red")
    screen.blit(text, (WIDTH//2 - text.get_width()//2, HEIGHT//2 - 200))

    retry_btn = pygame.draw.rect(screen, 'light gray', [WIDTH//2 - 200, HEIGHT//2, 400, 80], 0, 5)
    quit_btn = pygame.draw.rect(screen, 'light gray', [WIDTH//2 - 200, HEIGHT//2 + 120, 400, 80], 0, 5)

    screen.blit(small_font.render("Respawn", True, "black"), (WIDTH//2 - 60, HEIGHT//2 + 10))
    screen.blit(small_font.render("Back To Menu", True, "black"), (WIDTH//2 - 100, HEIGHT//2 + 130))

    if retry_btn.collidepoint(pygame.mouse.get_pos()) and pygame.mouse.get_pressed()[0]:
        return "respawn"
    if quit_btn.collidepoint(pygame.mouse.get_pos()) and pygame.mouse.get_pressed()[0]:
        return "quit"
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
        print("respawn pressed")
        run = False
    elif STATE == "quit":
        print("Quit pressed")
        run = False

    pygame.display.flip()
pygame.quit()
