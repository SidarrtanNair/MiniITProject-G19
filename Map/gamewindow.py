import pygame,sys,os,random

from tiles import *

spritesheet = ('1.png')



map = TileMap('background.csv',spritesheet)



pygame.init()
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Campus To Cosmos")

clock = pygame.time.Clock()

while True:
    clock.tick(60)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    screen.fill(("white"))
    pygame.display.update()

    screen.fill(0,180,240)
    map.draw_map(screen)
    screen.blit(screen,(0,0))
    pygame.display.update()