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

        # Detecção de pressionamento único (Just Pressed)
        just_pressed_jump = (keys[pygame.K_w] or keys[pygame.K_SPACE]) and not (self.last_keys[pygame.K_w] or self.last_keys[pygame.K_SPACE])
        just_pressed_swap = keys[pygame.K_x] and not self.last_keys[pygame.K_x]
        
        self.last_keys = keys

        return {
            'left': keys[pygame.K_a] or keys[pygame.K_LEFT],
            'right': keys[pygame.K_d] or keys[pygame.K_RIGHT],
            'jump': just_pressed_jump,
            'swap_char': just_pressed_swap, # Tecla X
            'hook': mouse[2],          
            'shoot': mouse[0],         
            'mouse_pos': self.mouse_pos,
            'weapon1': keys[pygame.K_1], 
            'weapon2': keys[pygame.K_2]  
        }

class Camera:
    def __init__(self):
        self.offset = pygame.math.Vector2(0, 0)
        self.shake_timer = 0
        self.shake_magnitude = 0

    def trigger_shake(self, magnitude, duration):
        self.shake_magnitude = magnitude
        self.shake_timer = duration

    def update(self, target_pos):
        # Interpolação suave para seguir o alvo
        target_x = target_pos.x - Config.SCREEN_WIDTH // 2
        target_y = target_pos.y - Config.SCREEN_HEIGHT // 2
        
        self.offset.x += (target_x - self.offset.x) * 0.1
        self.offset.y += (target_y - self.offset.y) * 0.1
        
        if self.shake_timer > 0:
            self.shake_timer -= 1
            import random
            self.offset.x += random.randint(-self.shake_magnitude, self.shake_magnitude)
            self.offset.y += random.randint(-self.shake_magnitude, self.shake_magnitude)

    def apply_rect(self, rect):
        return pygame.Rect(rect.x - self.offset.x, rect.y - self.offset.y, rect.width, rect.height)
    
    def apply_point(self, point):
        return (point[0] - self.offset.x, point[1] - self.offset.y)
    
    def to_world(self, pos):
        return pygame.math.Vector2(pos[0] + self.offset.x, pos[1] + self.offset.y)

class MathUtils:
    @staticmethod
    def raycast_bounce(start_pos, direction, walls, entities, max_bounces=3):
        """
        Calcula a trajetória de um laser que rebate.
        Retorna uma lista de tuplas: (ponto_inicial, ponto_final, entidade_atingida_se_houver)
        """
        trajectory = []
        current_start = pygame.math.Vector2(start_pos)
        current_dir = pygame.math.Vector2(direction).normalize()
        
        remaining_dist = Config.RIFLE_RANGE
        
        for _ in range(max_bounces + 1):
            closest_hit = None
            closest_dist = remaining_dist
            hit_normal = pygame.math.Vector2(0, 0)
            hit_entity = None
            
            # 1. Raycast contra Paredes (Cálculo simplificado de AABB)
            end_pos = current_start + current_dir * remaining_dist
            test_line = (current_start, end_pos)
            
            # Verificação passo-a-passo (Raymarching simples para colisão precisa)
            step_size = 10
            steps = int(closest_dist / step_size)
            
            collision_found = False
            for i in range(steps):
                check_point = current_start + current_dir * (i * step_size)
                check_rect = pygame.Rect(check_point.x, check_point.y, 4, 4)
                
                for w in walls:
                    if w.colliderect(check_rect):
                        closest_hit = check_point
                        closest_dist = i * step_size
                        
                        # Determinar Normal (qual lado bateu?)
                        dx = (check_point.x - w.centerx) / (w.width / 2)
                        dy = (check_point.y - w.centery) / (w.height / 2)
                        if abs(dx) > abs(dy):
                            hit_normal = pygame.math.Vector2(1 if dx > 0 else -1, 0)
                        else:
                            hit_normal = pygame.math.Vector2(0, 1 if dy > 0 else -1)
                        collision_found = True
                        break
                if collision_found: break

            # 2. Raycast contra Entidades (Só se não bateu na parede antes)
            for ent in entities:
                # Checa intersecção linha-retângulo
                clipline = ent.rect.clipline(current_start, current_start + current_dir * closest_dist)
                if clipline:
                    closest_hit = pygame.math.Vector2(clipline[0])
                    closest_dist = current_start.distance_to(closest_hit)
                    hit_entity = ent
                    hit_normal = None # Laser para na entidade
                    break

            # Salva o segmento
            final_point = closest_hit if closest_hit else end_pos
            trajectory.append((current_start, final_point))
            
            if hit_entity:
                return trajectory, hit_entity, current_dir
            
            if closest_hit and hit_normal:
                # Refletir vetor: R = D - 2*(D . N)*N
                current_dir = current_dir.reflect(hit_normal)
                current_start = final_point + current_dir * 2 # Offset para não grudar
                remaining_dist -= closest_dist
                if remaining_dist <= 0: break
            else:
                break # Não bateu em nada, fim do laser
                
        return trajectory, None, None