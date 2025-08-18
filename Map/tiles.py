import pygame,csv,os

class Spritesheet:
    def __init__(self, filename):
        self.spritesheet = pygame.image.load(filename).convert_alpha()

    def parse_sprite(self, name):
        # if you have coordinates for each sprite in a dict
        sprites = {
            "grass.png": (0, 0, 16, 16),  # x, y, w, h
            # add more here
        }
        x, y, w, h = sprites[name]
        image = pygame.Surface((w, h), pygame.SRCALPHA, 32).convert_alpha()
        image.blit(self.spritesheet, (0, 0), (x, y, w, h))
        return image

class Tile(pygame.sprite.Sprite):
    def __init__(self, image, x, y, spritesheet):
        pygame.sprite.Sprite.__init__(self)
        self.image = spritesheet.parse_sprite(image)
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = x, y

    def draw(self, surface):
        surface.blit(self.image, (self.rect.x, self.rect.y))

class TileMap():
    def __init__(self, filename, spritesheet):
        self.tile_size = 16
        self.start_x, self.start_y = 0, 0
        self.spritesheet = spritesheet
        self.tiles = self.load_tiles(filename)
        self.map_surface = pygame.Surface((self.map_w, self.map_h))
        self.map_surface.set_colorkey((0, 0, 0)) 
        self.load_map()

    def draw_map(self, surface):
        surface.blit(self.map_surface, (0, 0))

    def load_map(self):
        for tile in self.tiles:
            tile.draw(self.map_surface)   

    def read_csvfile(self, filename):
        map_data = []
        file_path = os.path.join("Map", filename)   # use the filename passed in
        with open(file_path, newline="") as data:
            reader = csv.reader(data, delimiter=",")
            for row in reader:
                map_data.append(list(row))
        return map_data
    
    def load_tiles(self, filename):
        tiles = []
        map_data = self.read_csvfile(filename)
        x, y = 0, 0

        for row in map_data:
            x = 0
            for tile in row:
                if tile == "0":
                    self.start_x, self.start_y = x * self.tile_size, y * self.tile_size
                elif tile == "378":
                    tiles.append(Tile('grass.png', x * self.tile_size, y * self.tile_size, self.spritesheet))
                x += 1
            y += 1

        self.map_w, self.map_h = x * self.tile_size, y * self.tile_size
        return tiles
