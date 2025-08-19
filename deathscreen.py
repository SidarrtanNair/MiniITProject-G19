import pygame
import sys
from game_menu import main_menu
pygame.init()

# -----------------Setup for the Screen--------------------------
WINDOW_WIDTH, WINDOW_HEIGHT = 800, 600
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Campus of Cosmos - Death Screen")


# ---------------Fonts--------------------
title_font = pygame.font.Font(None, 120)
button_font = pygame.font.Font(None, 60)

# ------------------Buttons------------------
buttons = [
    {"text": "Respawn", "y": 350},
    {"text": "Main Menu", "y": 430}
]

def draw_text(text, font, color, x, y, center=True):
    """Helper to draw text and return its rect for collision."""
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect()
    if center:
        text_rect.center = (x, y)
    else:
        text_rect.topleft = (x, y)
    screen.blit(text_surface, text_rect)
    return text_rect

def death_screen():
    """Shows the death screen and waits for player choice."""
    clock = pygame.time.Clock()

    while True:
        screen.fill("black")

        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        overlay.set_alpha(180)  
        overlay.fill("gray")
        screen.blit(overlay, (0, 0))

        # insert funny text here
        draw_text("Bro died? Wow.", title_font, "red", WINDOW_WIDTH // 2, 200)

        mouse_pos = pygame.mouse.get_pos()
        clicked = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                clicked = True

        for button in buttons:
            rect = draw_text(button["text"], button_font, "white", WINDOW_WIDTH // 2, button["y"])

            if rect.collidepoint(mouse_pos):
                draw_text(button["text"], button_font, "blue", WINDOW_WIDTH // 2, button["y"])
                if clicked:
                    if button["text"] == "Respawn":
                        print("Respawning player...")
                        return "respawn"  
                    elif button["text"] == "Main Menu":
                        print("Returning to main menu...")
                        main_menu()

        # FPS stuff
        pygame.display.flip()
        clock.tick(60)

# some testing
if __name__ == "__main__":
    choice = death_screen()
    print("Player chose:", choice)
