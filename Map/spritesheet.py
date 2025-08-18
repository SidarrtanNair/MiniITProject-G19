import pygame

class Spritesheet:
    def __init__(self, filename):
        self.spritesheet = pygame.image.load(filename).convert_alpha()

    def parse_sprite(self, name):
        
        sprites = {
            "grass.png": (0, 0, 16, 16),  # x, y, w, h
            
        }
        x, y, w, h = sprites[name]
        image = pygame.Surface((w, h), pygame.SRCALPHA, 32).convert_alpha()
        image.blit(self.spritesheet, (0, 0), (x, y, w, h))
        return image
