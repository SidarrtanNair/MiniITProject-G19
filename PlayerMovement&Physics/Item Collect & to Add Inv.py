import pygame
from Player import Player

# Initialize Pygame
pygame.init()

# Screen setup
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode(pygame.NOFRAME)
pygame.display.set_caption("Resource Collection Demo")

# Clock for FPS control
clock = pygame.time.Clock()

# Resource class
class Resource(pygame.sprite.Sprite):
    def __init__(self, x, y, resource_type):
        super().__init__()
        self.resource_type = resource_type
        self.image = pygame.Surface((30, 30))
        # Color based on resource type
        if resource_type == "wood":
            self.image.fill((139, 69, 19))  # Brown
        elif resource_type == "stone":
            self.image.fill((128, 128, 128))  # Gray
        else:
            self.image.fill((255, 255, 0))  # Yellow for others
        self.rect = self.image.get_rect(topleft=(x, y))

# Create player instance
player = Player(100, 100)

# Create resource group
resources = pygame.sprite.Group()
resources.add(Resource(300, 200, "wood"))
resources.add(Resource(400, 300, "stone"))
resources.add(Resource(500, 400, "wood"))

# Inventory dictionary
inventory = {}

# Font for displaying inventory
font = pygame.font.SysFont(None, 24)

def draw_inventory():
    y_offset = 10
    for resource_type, count in inventory.items():
        text = font.render(f"{resource_type}: {count}", True, (255, 255, 255))
        screen.blit(text, (10, y_offset))
        y_offset += 25

# Main loop
running = True
while running:
    clock.tick(60)  # 60 FPS

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Update player position
    player.update()

    # Check collision between player and resources
    collided_resources = pygame.sprite.spritecollide(player, resources, dokill=True)
    for resource in collided_resources:
        # Add resource to inventory
        if resource.resource_type in inventory:
            inventory[resource.resource_type] += 1
        else:
            inventory[resource.resource_type] = 1
        print(f"Collected {resource.resource_type}! Total: {inventory[resource.resource_type]}")

    # Drawing
    screen.fill((0, 0, 0))  # Clear screen with black
    screen.blit(player.image, player.rect)
    resources.draw(screen)
    draw_inventory()

    pygame.display.flip()
    
pygame.quit()