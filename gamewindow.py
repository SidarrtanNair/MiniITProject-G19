import pygame

pygame.init()
screen = pygame.display.set_mode((1000, 600))
pygame.display.set_caption("Campus To Cosmos")

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill(("white"))
    pygame.display.flip()

pygame.quit
