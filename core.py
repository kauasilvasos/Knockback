import pygame
import random
import math
from config import Config


class InputHandler:
    """Simplified input handler used by main.py.
    Returns a dict with boolean actions and mouse position.
    """
    def __init__(self):
        self.mouse_pos = (0, 0)

    def process_events(self):
        keys = pygame.key.get_pressed()
        mouse_buttons = pygame.mouse.get_pressed()
        self.mouse_pos = pygame.mouse.get_pos()

        return {
            'left': keys[pygame.K_a] or keys[pygame.K_LEFT],
            'right': keys[pygame.K_d] or keys[pygame.K_RIGHT],
            'up': keys[pygame.K_w] or keys[pygame.K_SPACE] or keys[pygame.K_UP],
            'fire': mouse_buttons[2],
            'shoot': mouse_buttons[0],
            'mouse_pos': self.mouse_pos,
        }


class Camera:
    def __init__(self, width, height):
        self.camera = pygame.Rect(0, 0, width, height)
        self.width = width
        self.height = height
        self.shake_magnitude = 0
        self.shake_timer = 0

    def trigger_shake(self, magnitude, duration):
        self.shake_magnitude = magnitude
        self.shake_timer = duration

    def apply(self, entity):
        # Accept Rect, Vector2 or tuple
        if isinstance(entity, pygame.Rect):
            return entity.move(self.camera.topleft)
        if isinstance(entity, pygame.math.Vector2):
            return entity + pygame.math.Vector2(self.camera.topleft)
        if isinstance(entity, tuple) and len(entity) == 2:
            return (entity[0] + self.camera.x, entity[1] + self.camera.y)
        # Fallback: try to use rect attribute
        try:
            return entity.rect.move(self.camera.topleft)
        except Exception:
            return entity

    def update(self, target):
        # Para centralização absoluta e imediata:
        # Mudamos de LERP (0.05) para 1.0 ou apenas definimos a posição
        target_x = -target.pos.x + (Config.SCREEN_WIDTH / 2) - (target.size / 2)
        target_y = -target.pos.y + (Config.SCREEN_HEIGHT / 2) - (target.size / 2)

        # Se quiser manter um pouco de suavização estilo DDNet, use 0.1 a 0.2
        # Para trava total, use 1.0
        lerp_speed = 1.0 
        self.camera.x = -target.pos.x + (Config.SCREEN_WIDTH / 2) - (target.size / 2)
        self.camera.y = -target.pos.y + (Config.SCREEN_HEIGHT / 2) - (target.size / 2)
        
        # Opcional: Remova o código de "Clamp" (min/max) se quiser que a câmera 
        # siga o jogador mesmo fora dos limites do mapa.