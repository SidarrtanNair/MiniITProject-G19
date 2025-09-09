import pygame, sys

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((40, 40))
        self.image.fill((240, 240, 240))
        self.rect = self.image.get_rect(center=(400, 400))

        self.current_health = 200
        self.maximum_health = 1000
        self.health_bar_length = 400
        self.health_ratio = self.maximum_health / self.health_bar_length

    def get_damage(self, amount):
        if self.current_health > 0:
            self.current_health -= amount
        if self.current_health <= 0:
            self.current_health = 0

    def get_health(self, amount):
        if self.current_health < self.maximum_health:
            self.current_health += amount
        if self.current_health >= self.maximum_health:
            self.current_health = self.maximum_health

    def basic_health(self):
        pygame.draw.rect(screen, (60, 60, 60), (10, 10, self.health_bar_length, 50))
        pygame.draw.rect(screen, (255, 0, 0), (10, 10, self.current_health / self.health_ratio, 50))
        pygame.draw.rect(screen, (255,255,255),(10,10,self.health_bar_length,50),4)

        font = pygame.font.SysFont(None,80)
        health_percent = int((self.current_health / self.maximum_health) * 100)
        text = font.render(f"{health_percent}%", True, (255, 0, 0))
        screen.blit(text, (15 + self.health_bar_length, 10))

    def update(self):
        self.basic_health()
# i stupidly realised that i did not indent basic_health, get_damage and get_health under Player bruh

pygame.init()
screen = pygame.display.set_mode((1600, 900))
clock = pygame.time.Clock()
player = pygame.sprite.GroupSingle(Player())

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                player.sprite.get_health(200)   
            if event.key == pygame.K_DOWN:
                player.sprite.get_damage(200)  

    screen.fill((100, 100, 100))
    player.draw(screen)
    player.update()
    pygame.display.update()
    clock.tick(60)
