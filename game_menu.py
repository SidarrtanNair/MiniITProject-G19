import pygame, sys, json, os
pygame.init()

# -----------------idk how wide yall want the screen to be so i will just leave it here-------------------
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Campus of Cosmos")

# Colors of the screen
WHITE = (255, 255, 255) 
BLACK = (0, 0, 0)
GRAY = (50, 50, 50)
LIGHT_GRAY = (170, 170, 170)
HOVER_COLOR = (100, 100, 255)

# this is for the fonts of the menu screen
title_font = pygame.font.Font(None, 80)
button_font = pygame.font.Font(None, 50)

SAVE_FILE = "savegame.json"

# ---------------Buttons-------------------
buttons = [
    {"text": "New Game", "pos": (WIDTH//2, 250)},
    {"text": "Continue", "pos": (WIDTH//2, 320)},
    {"text": "Settings", "pos": (WIDTH//2, 390)},
    {"text": "Credits", "pos": (WIDTH//2, 460)},
    {"text": "Exit", "pos": (WIDTH//2, 530)}
]

def draw_text(text, font, color, surface, x, y, center=True):
    text_obj = font.render(text, True, color)
    text_rect = text_obj.get_rect()
    if center:
        text_rect.center = (x, y)
    else:
        text_rect.topleft = (x, y)
    surface.blit(text_obj, text_rect)
    return text_rect

def save_game(data):
    with open(SAVE_FILE, "w") as file:
        json.dump(data, file)

def load_game():
    if os.path.exists(SAVE_FILE):
        with open(SAVE_FILE, "r") as file:
            return json.load(file)
    return None

def main_menu():
    clock = pygame.time.Clock()
    while True:
        screen.fill(BLACK)

        draw_text("Campus of Cosmos", title_font, WHITE, screen, WIDTH//2, 150)

        mouse_pos = pygame.mouse.get_pos()
        click = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                click = True

        for i, btn in enumerate(buttons):
            color = LIGHT_GRAY
            rect = draw_text(btn["text"], button_font, color, screen, btn["pos"][0], btn["pos"][1])
            if rect.collidepoint(mouse_pos):
                draw_text(btn["text"], button_font, HOVER_COLOR, screen, btn["pos"][0], btn["pos"][1])
                if click:
                    if btn["text"] == "New Game":
                        save_game({"player_name": "Hero", "level": 1, "score": 0})
                        print("Starting New Game...")
                    elif btn["text"] == "Continue":
                        data = load_game()
                        if data:
                            print("Loaded game:", data)
                        else:
                            print("No save file found.")
                    elif btn["text"] == "Settings":
                        print("Settings menu here")
                    elif btn["text"] == "Credits":
                        print("Credits screen here")
                    elif btn["text"] == "Exit":
                        pygame.quit()
                        sys.exit()

        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main_menu()
