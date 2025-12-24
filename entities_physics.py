import pygame
import math
import random
from config import Config
import entities_draw # Importa o desenhista

class ParticleManager:
    def __init__(self):
        self.particles = []

    def emit(self, pos, count, color, speed=5):
        for _ in range(count):
            angle = random.uniform(0, 6.28)
            velocity = random.uniform(1, speed)
            vx = math.cos(angle) * velocity
            vy = math.sin(angle) * velocity
            life = random.randint(20, 40)
            self.particles.append([pos[0], pos[1], vx, vy, life, color])

    def update(self):
        for p in self.particles[:]:
            p[0] += p[2]
            p[1] += p[3]
            p[2] *= 0.95 
            p[3] *= 0.95 
            p[4] -= 1    
            if p[4] <= 0:
                self.particles.remove(p)

    def draw(self, surface, camera):
        # Delega o desenho para o módulo visual
        entities_draw.draw_particles(surface, camera, self.particles)

class PhysicsEntity:
    def __init__(self, x, y, width, height):
        self.pos = pygame.math.Vector2(x, y)
        self.vel = pygame.math.Vector2(0, 0)
        self.rect = pygame.Rect(x, y, width, height)
        self.on_ground = False
        self.is_hookable = True

    def update_physics(self, walls):
        self.vel.y += Config.GRAVITY
        self.vel.y = min(self.vel.y, Config.TERMINAL_VELOCITY)

        # X Movement
        self.pos.x += self.vel.x
        self.rect.x = int(self.pos.x) 
        hits = [w for w in walls if self.rect.colliderect(w)]
        for wall in hits:
            if self.vel.x > 0:
                self.rect.right = wall.left; self.pos.x = self.rect.x; self.vel.x = 0
            elif self.vel.x < 0:
                self.rect.left = wall.right; self.pos.x = self.rect.x; self.vel.x = 0

        # Y Movement - CORREÇÃO DE VIBRAÇÃO (Sticky Ground)
        # Se já estávamos no chão e não estamos pulando (vel >= 0),
        # verifica se tem chão logo abaixo (1 pixel) para "colar" o personagem
        # e evitar o ciclo de cair-colidir-resetar que causa a vibração.
        if self.on_ground and self.vel.y >= 0:
             test_rect = self.rect.move(0, 1)
             ground_hits = [w for w in walls if test_rect.colliderect(w)]
             if ground_hits:
                 # Encontra o chão mais alto logo abaixo
                 highest_wall = min(ground_hits, key=lambda w: w.top)
                 
                 # Cola o player no chão
                 self.rect.bottom = highest_wall.top
                 self.pos.y = self.rect.y
                 self.vel.y = 0
                 self.on_ground = True
                 return # Pula o resto da física Y para este frame (estabilidade total)

        # Física Padrão Y (se estiver no ar ou pulando)
        self.pos.y += self.vel.y
        self.rect.y = int(self.pos.y)
        self.on_ground = False
        hits = [w for w in walls if self.rect.colliderect(w)]
        for wall in hits:
            if self.vel.y > 0:
                self.rect.bottom = wall.top; self.pos.y = self.rect.y; self.vel.y = 0; self.on_ground = True
            elif self.vel.y < 0:
                self.rect.top = wall.bottom; self.pos.y = self.rect.y; self.vel.y = 0