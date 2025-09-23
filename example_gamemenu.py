import pygame
import json
import os
import sys
from enum import Enum

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)
DARK_GRAY = (64, 64, 64)
BLUE = (0, 100, 255)
LIGHT_BLUE = (100, 150, 255)
COSMIC_PURPLE = (75, 0, 130)
COSMIC_BLUE = (25, 25, 112)
GOLD = (255, 215, 0)

# Game States
class GameState(Enum):
    MENU = 1
    PLAYING = 2
    SETTINGS = 3
    CREDITS = 4
    PAUSED = 5

class Button:
    def __init__(self, x, y, width, height, text, font, color=GRAY, hover_color=LIGHT_BLUE, text_color=WHITE):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font = font
        self.color = color
        self.hover_color = hover_color
        self.text_color = text_color
        self.is_hovered = False
        
    def draw(self, screen):
        # Draw button background
        color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(screen, color, self.rect)
        pygame.draw.rect(screen, WHITE, self.rect, 2)  # Border
        
        # Draw text
        text_surface = self.font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)
    
    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                return True
        return False

class SaveSystem:
    def __init__(self, save_file="campus_cosmos_save.json"):
        self.save_file = save_file
    
    def save_game(self, game_data):
        """Save game data to a JSON file"""
        try:
            with open(self.save_file, 'w') as f:
                json.dump(game_data, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving game: {e}")
            return False
    
    def load_game(self):
        """Load game data from JSON file"""
        try:
            if os.path.exists(self.save_file):
                with open(self.save_file, 'r') as f:
                    return json.load(f)
            return None
        except Exception as e:
            print(f"Error loading game: {e}")
            return None
    
    def save_exists(self):
        """Check if a save file exists"""
        return os.path.exists(self.save_file)

class GameMenu:
    def __init__(self, screen):
        self.screen = screen
        self.clock = pygame.time.Clock()
        self.state = GameState.MENU
        self.save_system = SaveSystem()
        
        # Fonts
        self.title_font = pygame.font.Font(None, 72)
        self.button_font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        
        # Create buttons
        button_width = 200
        button_height = 50
        button_spacing = 70
        start_y = 250
        center_x = SCREEN_WIDTH // 2 - button_width // 2
        
        self.buttons = {
            'new_game': Button(center_x, start_y, button_width, button_height, 
                              "New Game", self.button_font, COSMIC_PURPLE, BLUE),
            'continue': Button(center_x, start_y + button_spacing, button_width, button_height,
                              "Continue", self.button_font, COSMIC_PURPLE, BLUE),
            'settings': Button(center_x, start_y + button_spacing * 2, button_width, button_height,
                              "Settings", self.button_font, COSMIC_PURPLE, BLUE),
            'credits': Button(center_x, start_y + button_spacing * 3, button_width, button_height,
                             "Credits", self.button_font, COSMIC_PURPLE, BLUE),
            'exit': Button(center_x, start_y + button_spacing * 4, button_width, button_height,
                          "Exit", self.button_font, COSMIC_PURPLE, BLUE)
        }
        
        # Sample game data for demonstration
        self.game_data = {
            'player_name': 'Cosmic Explorer',
            'level': 1,
            'score': 0,
            'inventory': ['space_suit', 'communicator'],
            'current_location': 'Earth Campus',
            'achievements': [],
            'playtime': 0
        }
        
        # Check if continue button should be enabled
        if not self.save_system.save_exists():
            self.buttons['continue'].color = DARK_GRAY
            self.buttons['continue'].hover_color = DARK_GRAY
    
    def draw_background(self):
        """Draw a cosmic-themed background"""
        # Gradient background
        for y in range(SCREEN_HEIGHT):
            color_ratio = y / SCREEN_HEIGHT
            r = int(COSMIC_BLUE[0] * (1 - color_ratio))
            g = int(COSMIC_BLUE[1] * (1 - color_ratio))
            b = int(COSMIC_BLUE[2] * (1 - color_ratio) + 50 * color_ratio)
            pygame.draw.line(self.screen, (r, g, b), (0, y), (SCREEN_WIDTH, y))
        
        # Draw some "stars"
        import random
        random.seed(42)  # Consistent star positions
        for _ in range(50):
            x = random.randint(0, SCREEN_WIDTH)
            y = random.randint(0, SCREEN_HEIGHT // 2)
            pygame.draw.circle(self.screen, WHITE, (x, y), 1)
    
    def draw_menu(self):
        """Draw the main menu"""
        self.draw_background()
        
        # Draw title
        title_text = self.title_font.render("CAMPUS OF COSMOS", True, GOLD)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, 100))
        self.screen.blit(title_text, title_rect)
        
        # Draw subtitle
        subtitle_text = self.small_font.render("Explore the Universe of Knowledge", True, WHITE)
        subtitle_rect = subtitle_text.get_rect(center=(SCREEN_WIDTH // 2, 140))
        self.screen.blit(subtitle_text, subtitle_rect)
        
        # Draw buttons
        for button in self.buttons.values():
            button.draw(self.screen)
        
        # Draw save status
        if self.save_system.save_exists():
            save_text = self.small_font.render("Save file found", True, WHITE)
            self.screen.blit(save_text, (10, SCREEN_HEIGHT - 30))
    
    def draw_settings(self):
        """Draw settings screen"""
        self.screen.fill(COSMIC_BLUE)
        
        title_text = self.title_font.render("SETTINGS", True, GOLD)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, 100))
        self.screen.blit(title_text, title_rect)
        
        # Placeholder settings
        settings_text = [
            "Sound Volume: 70%",
            "Music Volume: 80%",
            "Fullscreen: Off",
            "Difficulty: Normal"
        ]
        
        for i, text in enumerate(settings_text):
            text_surface = self.button_font.render(text, True, WHITE)
            text_rect = text_surface.get_rect(center=(SCREEN_WIDTH // 2, 200 + i * 50))
            self.screen.blit(text_surface, text_rect)
        
        # Back instruction
        back_text = self.small_font.render("Press ESC to return to menu", True, WHITE)
        back_rect = back_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50))
        self.screen.blit(back_text, back_rect)
    
    def draw_credits(self):
        """Draw credits screen"""
        self.screen.fill(COSMIC_BLUE)
        
        title_text = self.title_font.render("CREDITS", True, GOLD)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, 100))
        self.screen.blit(title_text, title_rect)
        
        credits_text = [
            "Campus of Cosmos",
            "",
            "Game Design: Your Name",
            "Programming: Your Name",
            "Art: Your Name",
            "Music: Your Name",
            "",
            "Built with Python & Pygame",
            "",
            "Thank you for playing!"
        ]
        
        for i, text in enumerate(credits_text):
            if text:  # Skip empty lines
                text_surface = self.button_font.render(text, True, WHITE)
                text_rect = text_surface.get_rect(center=(SCREEN_WIDTH // 2, 180 + i * 30))
                self.screen.blit(text_surface, text_rect)
        
        # Back instruction
        back_text = self.small_font.render("Press ESC to return to menu", True, WHITE)
        back_rect = back_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50))
        self.screen.blit(back_text, back_rect)
    
    def draw_game(self):
        """Draw the actual game (placeholder)"""
        self.screen.fill(BLACK)
        
        # Game placeholder
        game_text = self.title_font.render("GAME RUNNING", True, WHITE)
        game_rect = game_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
        self.screen.blit(game_text, game_rect)
        
        # Display some game data
        info_texts = [
            f"Player: {self.game_data['player_name']}",
            f"Level: {self.game_data['level']}",
            f"Score: {self.game_data['score']}",
            f"Location: {self.game_data['current_location']}"
        ]
        
        for i, text in enumerate(info_texts):
            text_surface = self.button_font.render(text, True, WHITE)
            self.screen.blit(text_surface, (50, 50 + i * 40))
        
        # Instructions
        instructions = [
            "Press S to save game",
            "Press ESC to return to menu"
        ]
        
        for i, instruction in enumerate(instructions):
            text_surface = self.small_font.render(instruction, True, WHITE)
            self.screen.blit(text_surface, (SCREEN_WIDTH - 250, 50 + i * 30))
    
    def start_new_game(self):
        """Start a new game"""
        self.game_data = {
            'player_name': 'Cosmic Explorer',
            'level': 1,
            'score': 0,
            'inventory': ['space_suit', 'communicator'],
            'current_location': 'Earth Campus',
            'achievements': [],
            'playtime': 0
        }
        self.state = GameState.PLAYING
        print("New game started!")
    
    def continue_game(self):
        """Continue from saved game"""
        if self.save_system.save_exists():
            loaded_data = self.save_system.load_game()
            if loaded_data:
                self.game_data = loaded_data
                self.state = GameState.PLAYING
                print("Game loaded successfully!")
            else:
                print("Failed to load game!")
        else:
            print("No save file found!")
    
    def save_game(self):
        """Save the current game"""
        # Update playtime or other dynamic data here
        self.game_data['score'] += 10  # Example: add some score
        
        if self.save_system.save_game(self.game_data):
            print("Game saved successfully!")
            # Update continue button availability
            self.buttons['continue'].color = COSMIC_PURPLE
            self.buttons['continue'].hover_color = BLUE
        else:
            print("Failed to save game!")
    
    def handle_events(self):
        """Handle all game events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.state != GameState.MENU:
                        self.state = GameState.MENU
                elif event.key == pygame.K_s and self.state == GameState.PLAYING:
                    self.save_game()
            
            elif self.state == GameState.MENU:
                # Handle menu button clicks
                if self.buttons['new_game'].handle_event(event):
                    self.start_new_game()
                elif self.buttons['continue'].handle_event(event):
                    if self.save_system.save_exists():
                        self.continue_game()
                elif self.buttons['settings'].handle_event(event):
                    self.state = GameState.SETTINGS
                elif self.buttons['credits'].handle_event(event):
                    self.state = GameState.CREDITS
                elif self.buttons['exit'].handle_event(event):
                    return False
        
        return True
    
    def update(self):
        """Update game logic"""
        # Add any game updates here
        pass
    
    def draw(self):
        """Draw the appropriate screen based on current state"""
        if self.state == GameState.MENU:
            self.draw_menu()
        elif self.state == GameState.PLAYING:
            self.draw_game()
        elif self.state == GameState.SETTINGS:
            self.draw_settings()
        elif self.state == GameState.CREDITS:
            self.draw_credits()
    
    def run(self):
        """Main game loop"""
        running = True
        
        while running:
            running = self.handle_events()
            self.update()
            self.draw()
            
            pygame.display.flip()
            self.clock.tick(FPS)
        
        pygame.quit()
        sys.exit()

def main():
    """Initialize and run the game"""
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Campus of Cosmos")
    
    game = GameMenu(screen)
    game.run()

if __name__ == "__main__":
    main()