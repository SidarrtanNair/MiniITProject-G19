import pygame, sys, json, os
from button import Button

pygame.init()

SCREEN = pygame.display.set_mode((1280, 720))
pygame.display.set_caption("Campus of Cosmos")

SAVE_FILE = "savegame.json"

# -------------------------
# Fonts (using system fonts)
# -------------------------
def make_font(size, bold=False):
    return pygame.font.SysFont("arial", size, bold=bold)

# -------------------------
# Save/Load Helpers
# -------------------------
def save_game(data):
    """Save game data as JSON."""
    with open(SAVE_FILE, "w") as f:
        json.dump(data, f)

def load_game():
    """Load game data if save file exists."""
    if os.path.exists(SAVE_FILE):
        with open(SAVE_FILE, "r") as f:
            return json.load(f)
    return None

# -------------------------
# Screens
# -------------------------
def play():
    """New Game screen (also creates a save file)."""
    save_game({"player_name": "Hero", "level": 1, "score": 0})

    while True:
        PLAY_MOUSE_POS = pygame.mouse.get_pos()
        SCREEN.fill("black")

        PLAY_TEXT = make_font(45).render("New Game Started! Save Created.", True, "White")
        PLAY_RECT = PLAY_TEXT.get_rect(center=(640, 260))
        SCREEN.blit(PLAY_TEXT, PLAY_RECT)

        PLAY_BACK = Button(image=None, pos=(640, 460), 
                           text_input="BACK", font=make_font(75), 
                           base_color="White", hovering_color="Green")

        PLAY_BACK.changeColor(PLAY_MOUSE_POS)
        PLAY_BACK.update(SCREEN)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if PLAY_BACK.checkForInput(PLAY_MOUSE_POS):
                    return  # go back to main menu

        pygame.display.update()


def continue_game():
    """Continue screen (loads saved data)."""
    while True:
        CONT_MOUSE_POS = pygame.mouse.get_pos()
        SCREEN.fill("black")

        data = load_game()
        if data:
            text = f"Loaded Save: {data['player_name']} | Level {data['level']} | Score {data['score']}"
        else:
            text = "No Save File Found!"

        CONT_TEXT = make_font(35).render(text, True, "White")
        CONT_RECT = CONT_TEXT.get_rect(center=(640, 260))
        SCREEN.blit(CONT_TEXT, CONT_RECT)

        CONT_BACK = Button(image=None, pos=(640, 460), 
                           text_input="BACK", font=make_font(75), 
                           base_color="White", hovering_color="Green")

        CONT_BACK.changeColor(CONT_MOUSE_POS)
        CONT_BACK.update(SCREEN)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if CONT_BACK.checkForInput(CONT_MOUSE_POS):
                    return

        pygame.display.update()


def options():
    """Settings screen"""
    while True:
        OPTIONS_MOUSE_POS = pygame.mouse.get_pos()
        SCREEN.fill("white")

        OPTIONS_TEXT = make_font(45).render("This is the SETTINGS screen.", True, "Black")
        OPTIONS_RECT = OPTIONS_TEXT.get_rect(center=(640, 260))
        SCREEN.blit(OPTIONS_TEXT, OPTIONS_RECT)

        OPTIONS_BACK = Button(image=None, pos=(640, 460), 
                              text_input="BACK", font=make_font(75), 
                              base_color="Black", hovering_color="Green")

        OPTIONS_BACK.changeColor(OPTIONS_MOUSE_POS)
        OPTIONS_BACK.update(SCREEN)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if OPTIONS_BACK.checkForInput(OPTIONS_MOUSE_POS):
                    return

        pygame.display.update()


def credits():
    """Credits screen"""
    while True:
        CRED_MOUSE_POS = pygame.mouse.get_pos()
        SCREEN.fill("black")

        CRED_TEXT = make_font(45).render("Campus of Cosmos - Created by Our Team", True, "White")
        CRED_RECT = CRED_TEXT.get_rect(center=(640, 260))
        SCREEN.blit(CRED_TEXT, CRED_RECT)

        CRED_BACK = Button(image=None, pos=(640, 460), 
                           text_input="BACK", font=make_font(75), 
                           base_color="White", hovering_color="Green")

        CRED_BACK.changeColor(CRED_MOUSE_POS)
        CRED_BACK.update(SCREEN)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if CRED_BACK.checkForInput(CRED_MOUSE_POS):
                    return

        pygame.display.update()

# -------------------------
# Main Menu
# -------------------------
def main_menu():
    while True:
        SCREEN.fill((0,0,0))  # Clean background

        MENU_MOUSE_POS = pygame.mouse.get_pos()

        MENU_TEXT = make_font(100, bold=True).render("MAIN MENU", True, "#b68f40")
        MENU_RECT = MENU_TEXT.get_rect(center=(640, 100))
        SCREEN.blit(MENU_TEXT, MENU_RECT)

        # Buttons
        PLAY_BUTTON = Button(image=pygame.image.load("assets/Play Rect.png"), pos=(640, 200), 
                             text_input="NEW GAME", font=make_font(75), base_color="#d7fcd4", hovering_color="White")
        
        CONTINUE_BUTTON = Button(image=pygame.image.load("assets/Options Rect.png"), pos=(640, 300), 
                             text_input="CONTINUE", font=make_font(75), base_color="#d7fcd4", hovering_color="White")

        OPTIONS_BUTTON = Button(image=pygame.image.load("assets/Options Rect.png"), pos=(640, 400), 
                             text_input="SETTINGS", font=make_font(75), base_color="#d7fcd4", hovering_color="White")
        
        CREDITS_BUTTON = Button(image=pygame.image.load("assets/Quit Rect.png"), pos=(640, 500), 
                             text_input="CREDITS", font=make_font(75), base_color="#d7fcd4", hovering_color="White")
        
        QUIT_BUTTON = Button(image=pygame.image.load("assets/Quit Rect.png"), pos=(640, 600), 
                             text_input="QUIT", font=make_font(75), base_color="#d7fcd4", hovering_color="White")

        # Draw buttons
        for button in [PLAY_BUTTON, CONTINUE_BUTTON, OPTIONS_BUTTON, CREDITS_BUTTON, QUIT_BUTTON]:
            button.changeColor(MENU_MOUSE_POS)
            button.update(SCREEN)
        
        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if PLAY_BUTTON.checkForInput(MENU_MOUSE_POS):
                    play()
                if CONTINUE_BUTTON.checkForInput(MENU_MOUSE_POS):
                    continue_game()
                if OPTIONS_BUTTON.checkForInput(MENU_MOUSE_POS):
                    options()
                if CREDITS_BUTTON.checkForInput(MENU_MOUSE_POS):
                    credits()
                if QUIT_BUTTON.checkForInput(MENU_MOUSE_POS):
                    pygame.quit()
                    sys.exit()

        pygame.display.update()

# -------------------------
# Run the Menu
# -------------------------
main_menu()
