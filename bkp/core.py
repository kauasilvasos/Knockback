import pygame
import math
from config import Config

class InputHandler:
    def __init__(self):
        self.mouse_pos = (0, 0)
        self.last_keys = pygame.key.get_pressed()

    def process_events(self):
        keys = pygame.key.get_pressed()
        mouse = pygame.mouse.get_pressed()
        self.mouse_pos = pygame.mouse.get_pos()

        just_pressed_jump = (keys[pygame.K_w] or keys[pygame.K_SPACE]) and not (self.last_keys[pygame.K_w] or self.last_keys[pygame.K_SPACE])
        
        self.last_keys = keys

        return {
            'left': keys[pygame.K_a] or keys[pygame.K_LEFT],
            'right': keys[pygame.K_d] or keys[pygame.K_RIGHT],
            'jump': just_pressed_jump, 
            'hook': mouse[2],          
            'shoot': mouse[0],         
            'mouse_pos': self.mouse_pos,
            'weapon1': keys[pygame.K_1], # Martelo
            'weapon2': keys[pygame.K_2]  # Granada
        }
# ... Resto da classe Camera e MathUtils (inaterado) ...
class Camera:
    # (Mantenha o código original da Camera aqui)
    def __init__(self):
        self.offset = pygame.math.Vector2(0, 0)
        self.target_offset = pygame.math.Vector2(0, 0)
        self.shake_timer = 0
        self.shake_magnitude = 0

    def trigger_shake(self, magnitude, duration):
        self.shake_magnitude = magnitude
        self.shake_timer = duration

    def update(self, target_pos):
        target_x = target_pos.x - Config.SCREEN_WIDTH // 2
        target_y = target_pos.y - Config.SCREEN_HEIGHT // 2
        
        self.offset.x += (target_x - self.offset.x) * 0.1
        self.offset.y += (target_y - self.offset.y) * 0.1
        
        if self.shake_timer > 0:
            self.shake_timer -= 1
            import random
            dx = random.randint(-self.shake_magnitude, self.shake_magnitude)
            dy = random.randint(-self.shake_magnitude, self.shake_magnitude)
            self.offset.x += dx
            self.offset.y += dy

    def apply_rect(self, rect):
        return pygame.Rect(rect.x - self.offset.x, rect.y - self.offset.y, rect.width, rect.height)
    
    def apply_point(self, point):
        return (point[0] - self.offset.x, point[1] - self.offset.y)
    
    def to_world(self, pos):
        return pygame.math.Vector2(pos[0] + self.offset.x, pos[1] + self.offset.y)

class MathUtils:
     # (Mantenha o código original aqui)
    @staticmethod
    def raycast(start, end, walls):
        vec = end - start
        length = vec.length()
        if length == 0: return None, None
        
        direction = vec.normalize()
        steps = int(length / 10) 
        
        current_pos = pygame.math.Vector2(start)
        for _ in range(steps):
            current_pos += direction * 10
            test_rect = pygame.Rect(current_pos.x, current_pos.y, 1, 1)
            for wall in walls:
                if wall.colliderect(test_rect):
                    return current_pos, wall
        return None, None