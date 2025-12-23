import pygame
import math
import random
from config import Config

class MathUtils:
    """Static utilities for physics calculations."""
    @staticmethod
    def angle_to(p1, p2):
        return math.atan2(p2.y - p1.y, p2.x - p1.x)

    @staticmethod
    def normalize_safe(vector):
        if vector.length() == 0:
            return pygame.math.Vector2(0, 0)
        return vector.normalize()

class InputHandler:
    def __init__(self):
        self.mouse_pos = (0, 0)
        self.mouse_world = (0, 0)

    def process_events(self, camera_offset):
        keys = pygame.key.get_pressed()
        mouse = pygame.mouse.get_pressed()
        screen_mouse = pygame.math.Vector2(pygame.mouse.get_pos())
        
        # Converte mouse da tela para o mundo
        self.mouse_world = screen_mouse - pygame.math.Vector2(camera_offset)

        return {
            'left': keys[pygame.K_a] or keys[pygame.K_LEFT],
            'right': keys[pygame.K_d] or keys[pygame.K_RIGHT],
            'up': keys[pygame.K_w] or keys[pygame.K_SPACE],
            'fire_hook': mouse[2],   # Botão Direito
            'fire_hammer': mouse[0], # Botão Esquerdo
            'fire_grenade': keys[pygame.K_e], # Tecla E
            'mouse_pos': (self.mouse_world.x, self.mouse_world.y)
        }

class Camera:
    def __init__(self, width, height):
        self.camera = pygame.Rect(0, 0, width, height)
        self.width = width
        self.height = height
        self.shake_timer = 0
        self.shake_magnitude = 0
        
        # FIX: Armazenar posição exata em float para evitar tremedeira (Jitter)
        self.exact_x = 0.0
        self.exact_y = 0.0

    def trigger_shake(self, magnitude, duration):
        self.shake_magnitude = magnitude
        self.shake_timer = duration

    def apply(self, entity):
        """Retorna a posição na tela de um objeto do mundo."""
        
        # 1. FIX CRÍTICO: Verificar se é Rect explicitamente ANTES de checar x/y
        if isinstance(entity, pygame.Rect):
            return entity.move(self.camera.topleft)
            
        # 2. Se for uma Entidade com propriedade .rect
        if hasattr(entity, 'rect'):
            return entity.rect.move(self.camera.topleft)
            
        # 3. Se for Vector2 ou ponto (tem x e y, mas não é Rect)
        if hasattr(entity, 'x') and hasattr(entity, 'y'):
             return pygame.math.Vector2(entity.x + self.camera.x, entity.y + self.camera.y)
             
        # 4. Fallback para tuplas
        return entity

    def update(self, target_pos, dt):
        # Smooth Follow (Lerp)
        desired_x = -target_pos.x + Config.SCREEN_WIDTH / 2
        desired_y = -target_pos.y + Config.SCREEN_HEIGHT / 2
        
        # Lerp suave usando floats (Smoothness)
        self.exact_x += (desired_x - self.exact_x) * 0.1
        self.exact_y += (desired_y - self.exact_y) * 0.1
        
        # Atualiza o Rect oficial (Pygame usa inteiros)
        self.camera.x = int(self.exact_x)
        self.camera.y = int(self.exact_y)

        # Screen Shake Logic
        if self.shake_timer > 0:
            self.shake_timer -= 1
            offset_x = random.randint(-self.shake_magnitude, self.shake_magnitude)
            offset_y = random.randint(-self.shake_magnitude, self.shake_magnitude)
            self.camera.x += offset_x
            self.camera.y += offset_y