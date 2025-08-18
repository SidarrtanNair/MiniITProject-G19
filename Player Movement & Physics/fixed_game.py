import pygame
import sys
import os

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 1080
SCREEN_HEIGHT = 720
GRAVITY = 0.5
JUMP_STRENGTH = 10
DOUBLE_JUMP_STRENGTH = 8

# Colors
WHITE = (255, 255, 255)

# Get the directory where this script is located
script_dir = os.path.dirname(os.path.abspath(__file__))

# Load Sprites with correct paths
try:
    standing_sprite = pygame.image.load(os.path.join(script_dir, 'standing.png'))
    moving_forward_sprite = pygame.image.load(os.path.join(script_dir, 'moving_forward.png'))
    moving_backward_sprite = pygame.image.load(os.path.join(script_dir, 'moving_backward.png'))
    jumping_sprite = pygame.image.load(os.path.join(script_dir, 'jumping.png'))
    print("All images loaded successfully!")
except pygame.error as e:
    print(f"Error loading images: {e}")
    print(f"Looking in directory: {script_dir}")
    print("Make sure the image files are in the same folder as this script")
    sys.exit()

# Player Class
class Player:
    def __init__(self):
        self.image = standing_sprite
        self.rect = self.image.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50))
        self.velocity_y = 0
        self.on_ground = True
        self.double_jump_used = False

    def update(self):
        # Apply gravity
        if not self.on_ground:
            self.velocity_y += GRAVITY
        self.rect.y += self.velocity_y

        # Check for ground collision
        if self.rect.bottom >= SCREEN_HEIGHT:
            self.rect.bottom = SCREEN_HEIGHT
            self.on_ground = True
            self.velocity_y = 0
            self.double_jump_used = False

    def jump(self):
        if self.on_ground:
            self.velocity_y = -JUMP_STRENGTH
            self.on_ground = False
        elif not self.double_jump_used:
            self.velocity_y = -DOUBLE_JUMP_STRENGTH
            self.double_jump_used = True

    def move(self, direction):
        if direction == 'left':
            self.rect.x -= 5
            self.image = moving_backward_sprite
        elif direction == 'right':
            self.rect.x += 5
            self.image = moving_forward_sprite
        else:
            self.image = standing_sprite

# Main Game Loop
def main():
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Player Movement & Physics")
    clock = pygame.time.Clock()
    player = Player()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            player.move('left')
        elif keys[pygame.K_RIGHT]:
            player.move('right')
        else:
            player.move('stop')

        if keys[pygame.K_SPACE]:
            player.jump()

        player.update()

        # Clear screen
        screen.fill(WHITE)
        # Draw player
        screen.blit(player.image, player.rect)
        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()
