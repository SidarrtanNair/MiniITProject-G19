import pygame
import sys

pygame.init()
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Drag and Drop with Text")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 36)

# --- Draggable Box Class ---
class DraggableBox:
    def __init__(self, x, y, w, h, text=""):
        self.rect = pygame.Rect(x, y, w, h)
        self.color = (200, 100, 100)
        self.text = text
        self.dragging = False
        self.selected = False
        self.offset_x = 0
        self.offset_y = 0

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect)
        pygame.draw.rect(surface, (255, 255, 255), self.rect, 2)

        # Render text centered inside box
        text_surface = font.render(self.text, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # left click
                if self.rect.collidepoint(event.pos):
                    self.dragging = True
                    self.selected = True
                    mouse_x, mouse_y = event.pos
                    self.offset_x = self.rect.x - mouse_x
                    self.offset_y = self.rect.y - mouse_y
                else:
                    self.selected = False

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                self.dragging = False

        elif event.type == pygame.MOUSEMOTION:
            if self.dragging:
                mouse_x, mouse_y = event.pos
                self.rect.x = mouse_x + self.offset_x
                self.rect.y = mouse_y + self.offset_y

        elif event.type == pygame.KEYDOWN and self.selected:
            if event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            else:
                self.text += event.unicode


# --- Main Loop ---
boxes = [
    DraggableBox(100, 100, 150, 80, "Box 1"),
    DraggableBox(300, 200, 150, 80, "Box 2"),
]

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        for box in boxes:
            box.handle_event(event)

    screen.fill((30, 30, 30))
    for box in boxes:
        box.draw(screen)

    pygame.display.flip()
    clock.tick(60)
