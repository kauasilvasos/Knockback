import pygame
from config import Config

class TileMap:
    def __init__(self, map_data):
        self.tile_size = 40
        self.walls = []
        for r, row in enumerate(map_data):
            for c, tile in enumerate(row):
                if tile == '1':
                    self.walls.append(pygame.Rect(c*40, r*40, 40, 40))

    def draw(self, surface, camera):
        # Otimização simples: Desenha apenas o que está na tela + margem
        view = pygame.Rect(-camera.camera.x, -camera.camera.y, Config.SCREEN_WIDTH, Config.SCREEN_HEIGHT)
        for w in self.walls:
            if view.colliderect(w):
                pygame.draw.rect(surface, Config.COLOR_GROUND, camera.apply(w))