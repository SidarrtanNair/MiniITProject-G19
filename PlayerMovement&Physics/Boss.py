import pygame
import sys
import os

script_dir = os.path.dirname(os.path.abspath(__file__))

class Enemy(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()
        self.sprite_sheet = pygame.image.load(os.path.join(script_dir,'Sprite_Img/boss_spriteV1.png')).convert_alpha()
        self.frame_width = 134
        self.frame_height = 134
        self.num_frames = 8
        self.scale = 0.2

        # Extract frames from sprite sheet
        self.frames = []
        for i in range(self.num_frames):
            frame_surface = pygame.Surface((self.frame_width, self.frame_height), pygame.SRCALPHA)
            frame_surface.blit(
                self.sprite_sheet,
                (0, 0),
                (i * self.frame_width, 0, self.frame_width, self.frame_height)
            )
            # Scale frame
            scaled_frame = pygame.transform.scale(
                frame_surface,
                (int(self.frame_width * self.scale), int(self.frame_height * self.scale))
            )
            self.frames.append(scaled_frame)

        self.current_frame = 0
        self.image = self.frames[self.current_frame]
        self.rect = self.image.get_rect(topleft=pos)

        self.animation_speed = 10 # Controls how fast the animation cycles
        self.frame_timer = 0

    def update(self, dt):
        # Update animation timer
        self.frame_timer += self.animation_speed * dt
        if self.frame_timer >= 1:
            self.frame_timer = 0
            self.current_frame = (self.current_frame + 1) % self.num_frames
            self.image = self.frames[self.current_frame]

def main():
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    clock = pygame.time.Clock()

    enemy = Enemy((300, 200))
    all_sprites = pygame.sprite.Group(enemy)

    while True:
        dt = clock.tick(60) / 1000  # Delta time in seconds

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        all_sprites.update(dt)

        screen.fill((30, 30, 30))
        all_sprites.draw(screen)
        pygame.display.flip()

if __name__ == "__main__":
    main()
