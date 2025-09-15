class Inventory:
    def __init__(self):
        self.blocks_broken = 0
        self.blocks_placed = 0
        self.font = pygame.font.SysFont('Arial', 24, bold=True)
        self.small_font = pygame.font.SysFont('Arial', 20)
        
    def add_broken_block(self):
        self.blocks_broken += 1
        
    def add_placed_block(self):
        self.blocks_placed += 1
        
    def draw(self, screen):
        # Background for inventory
        screen_width = screen.get_width()
        inventory_width = 250
        inventory_height = 120
        inventory_x = screen_width - inventory_width - 20
        inventory_y = 20
        
        # Semi-transparent background
        inventory_bg = pygame.Surface((inventory_width, inventory_height))
        inventory_bg.set_alpha(180)
        inventory_bg.fill((40, 40, 40))
        screen.blit(inventory_bg, (inventory_x, inventory_y))
        
        # Border
        pygame.draw.rect(screen, (100, 100, 100), 
                        (inventory_x, inventory_y, inventory_width, inventory_height), 2)
        
        # Title
        title_text = self.font.render("INVENTORY", True, (255, 255, 255))
        screen.blit(title_text, (inventory_x + 10, inventory_y + 10))
        
        # Inventory items
        broken_text = self.small_font.render(f"Blocks Broken: {self.blocks_broken}", True, (255, 100, 100))
        placed_text = self.small_font.render(f"Blocks Placed: {self.blocks_placed}", True, (100, 255, 100))
        
        screen.blit(broken_text, (inventory_x + 10, inventory_y + 45))
        screen.blit(placed_text, (inventory_x + 10, inventory_y + 70))
        
        # Controls hint
        hint_font = pygame.font.SysFont('Arial', 14)
        hint_text = hint_font.render("Left Click: Break | Right Click: Place", True, (200, 200, 200))
        screen.blit(hint_text, (inventory_x + 10, inventory_y + 95))

 # Initialize inventory system
        self.inventory = Inventory()

# Reset inventory when generating new world
        self.inventory = Inventory()
        if self.player:
            self.init_player()

 # Draw inventory last so it's on top
            self.inventory.draw(self.screen)