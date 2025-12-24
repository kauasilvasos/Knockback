import pygame
from config import Config

class InputHandler:
    def __init__(self):
        self.mouse_pos = (0, 0)

    def process_events(self):
        # Não pede argumentos, pega o mouse cru da tela
        keys = pygame.key.get_pressed()
        mouse = pygame.mouse.get_pressed()
        self.mouse_pos = pygame.mouse.get_pos()

        return {
            'left': keys[pygame.K_a] or keys[pygame.K_LEFT],
            'right': keys[pygame.K_d] or keys[pygame.K_RIGHT],
            'up': keys[pygame.K_w] or keys[pygame.K_SPACE],
            
            # PADRONIZAÇÃO DOS BOTÕES
            'hook': mouse[2],    # Botão Direito = Hook
            'shoot': mouse[0],   # Botão Esquerdo = Granada
            
            'mouse_pos': self.mouse_pos
        }

class Camera:
    def __init__(self, width, height):
        self.camera = pygame.Rect(0, 0, width, height)
        self.width = width
        self.height = height
        self.shake_magnitude = 0
        self.shake_timer = 0
        self.exact_x = 0.0
        self.exact_y = 0.0

    def trigger_shake(self, magnitude, duration):
        self.shake_magnitude = magnitude
        self.shake_timer = duration

    def apply(self, entity):
        # Resolve o erro de "rect argument invalid" aceitando qualquer coisa
        if isinstance(entity, pygame.Rect):
            return entity.move(self.camera.topleft)
        if hasattr(entity, 'rect'):
            return entity.rect.move(self.camera.topleft)
        if hasattr(entity, 'x') and hasattr(entity, 'y'):
             return pygame.math.Vector2(entity.x + self.camera.x, entity.y + self.camera.y)
        return entity

    def update(self, target):
        # Centraliza
        target_x = -target.pos.x + Config.SCREEN_WIDTH / 2
        target_y = -target.pos.y + Config.SCREEN_HEIGHT / 2
        
        # Lerp Suave
        self.exact_x += (target_x - self.exact_x) * 0.1
        self.exact_y += (target_y - self.exact_y) * 0.1
        
        # Shake
        offset_x = 0
        offset_y = 0
        if self.shake_timer > 0:
            self.shake_timer -= 1
            import random
            offset_x = random.randint(-self.shake_magnitude, self.shake_magnitude)
            offset_y = random.randint(-self.shake_magnitude, self.shake_magnitude)

        self.camera.x = int(self.exact_x + offset_x)
        self.camera.y = int(self.exact_y + offset_y)

class MathUtils:
    @staticmethod
    def normalize_safe(vector):
        if vector.length() == 0: return pygame.math.Vector2(0, 0)
        return vector.normalize()