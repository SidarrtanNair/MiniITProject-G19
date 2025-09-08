import pygame , os 

pygame.init()

# Set up the display
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
pygame.display.set_caption("Image Resizing in Pygame")

# Get the directory where this script is located
script_dir = os.path.dirname(os.path.abspath(__file__))

# Load an image
original_image = pygame.image.load(os.path.join(script_dir, 'male_sprites_V2.png')).convert_alpha()



# Resize the image using scale()
scaled_image_fast = pygame.transform.scale_by(original_image, 0.1)

# Resize the image using smoothscale()
scaled_image_smooth = pygame.transform.smoothscale_by(original_image, 0.1)

# Game loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Clear the screen
    screen.fill((255, 255, 255)) # White background

    # Blit the scaled images to the screen
    screen.blit(scaled_image_fast, (50, 50))
    screen.blit(scaled_image_smooth, (300, 100))

    pygame.display.flip()

pygame.quit()