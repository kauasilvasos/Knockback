import pygame
import math
import random
from config import Config
from core import MathUtils

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
        for p in self.particles:
            pos_screen = camera.apply_point((p[0], p[1]))
            size = max(1, int(4 * (p[4] / 30)))
            pygame.draw.rect(surface, p[5], (pos_screen[0], pos_screen[1], size, size))

class Projectile:
    def __init__(self, x, y, angle, particles):
        self.pos = pygame.math.Vector2(x, y)
        self.vel = pygame.math.Vector2(math.cos(angle), math.sin(angle)) * Config.GRENADE_SPEED
        self.rect = pygame.Rect(x, y, 12, 12)
        self.particles = particles
        self.life = Config.GRENADE_LIFETIME
        self.active = True

    def update(self, walls, entities):
        self.vel.y += Config.GRAVITY
        self.pos += self.vel
        self.rect.topleft = (int(self.pos.x), int(self.pos.y))
        
        if random.random() < 0.3:
            self.particles.emit(self.pos, 1, (100, 100, 100), 1)

        self.life -= 1
        if self.life <= 0:
            self.explode(entities)
            return

        for w in walls:
            if self.rect.colliderect(w):
                self.explode(entities)
                return

        for entity in entities:
            if isinstance(entity, Dummy) and self.rect.colliderect(entity.rect):
                self.explode(entities)
                return

    def explode(self, entities):
        self.active = False
        self.particles.emit(self.pos, 20, Config.COLOR_EXPLOSION, 8)
        
        blast_center = self.pos
        for entity in entities:
            if isinstance(entity, PhysicsEntity):
                dist_vec = entity.pos - blast_center
                dist = dist_vec.length()
                
                if dist < Config.GRENADE_BLAST_RADIUS:
                    force_factor = (Config.GRENADE_BLAST_RADIUS - dist) / Config.GRENADE_BLAST_RADIUS
                    if dist > 0:
                        direction = dist_vec.normalize()
                    else:
                        direction = pygame.math.Vector2(0, -1)
                    
                    entity.vel += direction * (Config.GRENADE_BLAST_FORCE * force_factor)
                    if isinstance(entity, Dummy):
                        entity.hit_timer = 10

    def draw(self, surface, camera):
        draw_rect = camera.apply_rect(self.rect)
        pygame.draw.circle(surface, Config.COLOR_GRENADE, draw_rect.center, 6)

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

        # Movimento X
        self.pos.x += self.vel.x
        # CORREÇÃO: Usar int() em vez de round() evita a vibração (jitter)
        self.rect.x = int(self.pos.x) 
        
        hits = [w for w in walls if self.rect.colliderect(w)]
        for wall in hits:
            if self.vel.x > 0:
                self.rect.right = wall.left
                self.pos.x = self.rect.x
                self.vel.x = 0
            elif self.vel.x < 0:
                self.rect.left = wall.right
                self.pos.x = self.rect.x
                self.vel.x = 0

        # Movimento Y
        self.pos.y += self.vel.y
        # CORREÇÃO: Usar int() aqui estabiliza a gravidade no chão
        self.rect.y = int(self.pos.y)
        
        self.on_ground = False
        hits = [w for w in walls if self.rect.colliderect(w)]
        for wall in hits:
            if self.vel.y > 0:
                self.rect.bottom = wall.top
                self.pos.y = self.rect.y # Sincroniza posição float com o pixel exato
                self.vel.y = 0
                self.on_ground = True
            elif self.vel.y < 0:
                self.rect.top = wall.bottom
                self.pos.y = self.rect.y
                self.vel.y = 0

class Dummy(PhysicsEntity):
    def __init__(self, x, y):
        super().__init__(x, y, 40, 40)
        self.hit_timer = 0
    
    def update(self, walls):
        self.vel.x *= 0.9 
        self.update_physics(walls)
        if self.hit_timer > 0: self.hit_timer -= 1
        
    def draw(self, surface, camera):
        draw_rect = camera.apply_rect(self.rect)
        color = Config.COLOR_DUMMY
        if self.hit_timer > 0: color = (255, 255, 255) 
        
        pygame.draw.rect(surface, color, draw_rect, border_radius=4)
        eye_y = draw_rect.y + 10
        pygame.draw.circle(surface, (0,0,0), (draw_rect.x + 12, eye_y), 3)
        pygame.draw.circle(surface, (0,0,0), (draw_rect.x + 28, eye_y), 3)

class Player(PhysicsEntity):
    def __init__(self, x, y, particles, camera):
        super().__init__(x, y, 30, 30)
        self.particles = particles
        self.camera = camera
        
        # Hook Vars
        self.hook_state = 0 
        self.hook_pos = pygame.math.Vector2(0, 0)
        self.hook_vel = pygame.math.Vector2(0, 0)
        self.hook_target_entity = None 
        
        # Mecânica de Pulo
        self.jumps_left = 0
        
        # Visuals
        self.scale_x = 1.0
        self.scale_y = 1.0
        self.facing_right = True

        # Weapon System
        self.current_weapon = 1 # 1: Hammer, 2: Grenade
        self.shoot_cooldown = 0
        self.projectiles = [] 

    def set_projectiles_list(self, proj_list):
        self.projectiles = proj_list

    def update(self, inputs, walls, entities):
        # 1. Troca de Arma
        if inputs['weapon1']: self.current_weapon = 1
        if inputs['weapon2']: self.current_weapon = 2

        # 2. Movimento & Física
        accel = Config.MOVE_ACCEL
        if not self.on_ground: accel *= 0.5 
        
        if inputs['left']: 
            self.vel.x -= accel
            self.facing_right = False
        if inputs['right']: 
            self.vel.x += accel
            self.facing_right = True
        
        friction = Config.FRICTION_GROUND if self.on_ground else Config.FRICTION_AIR
        self.vel.x *= friction

        # --- Lógica de Pulo Duplo ---
        if self.on_ground:
            self.jumps_left = Config.MAX_JUMPS # Reseta pulos
        
        if inputs['jump']:
            if self.jumps_left > 0:
                self.vel.y = -Config.JUMP_FORCE
                self.jumps_left -= 1
                
                # Efeitos
                self.scale_x = 0.7
                self.scale_y = 1.3
                self.particles.emit((self.rect.centerx, self.rect.bottom), 5, (200, 200, 200))

        # 3. Hook e Armas
        self.update_hook(inputs, walls, entities)
        self.update_weapons(inputs, entities)

        # 4. Física Final
        prev_ground = self.on_ground
        self.update_physics(walls)
        
        if not prev_ground and self.on_ground:
            self.scale_x = 1.3
            self.scale_y = 0.7
            self.camera.trigger_shake(2, 5)

        self.scale_x += (1.0 - self.scale_x) * 0.1
        self.scale_y += (1.0 - self.scale_y) * 0.1

    def update_weapons(self, inputs, entities):
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1

        if inputs['shoot'] and self.shoot_cooldown == 0:
            mouse_world = self.camera.to_world(inputs['mouse_pos'])
            center = pygame.math.Vector2(self.rect.center)
            diff = mouse_world - center
            angle = math.atan2(diff.y, diff.x)

            if self.current_weapon == 1: # HAMMER
                self.shoot_cooldown = Config.HAMMER_COOLDOWN
                self.use_hammer(center, angle, entities)
                self.camera.trigger_shake(2, 2) 

            elif self.current_weapon == 2: # GRENADE
                self.shoot_cooldown = Config.GRENADE_COOLDOWN
                proj = Projectile(center.x, center.y, angle, self.particles)
                self.projectiles.append(proj)
                self.vel -= pygame.math.Vector2(math.cos(angle), math.sin(angle)) * 2

    def use_hammer(self, center, angle, entities):
        hit_range = Config.HAMMER_RANGE
        # Ponto visual do hit
        hit_pos = center + pygame.math.Vector2(math.cos(angle), math.sin(angle)) * (hit_range * 0.8)
        
        hit_something = False
        for entity in entities:
            if entity is not self and isinstance(entity, PhysicsEntity):
                dist = center.distance_to(entity.rect.center)
                if dist < hit_range + 30: # Hitbox generosa
                    hit_something = True
                    entity.hit_timer = 10
                    
                    # --- DIREÇÃO DO KNOCKBACK CORRIGIDA ---
                    # Agora a força segue exatamente a mira do mouse (ângulo do martelo)
                    force_dir = pygame.math.Vector2(math.cos(angle), math.sin(angle))
                    
                    entity.vel += force_dir * Config.HAMMER_FORCE
                    self.particles.emit(entity.rect.center, 10, (255, 255, 255), 5)

        if hit_something:
            self.particles.emit(hit_pos, 5, (200, 200, 200), 2)

    def update_hook(self, inputs, walls, entities):
        center = pygame.math.Vector2(self.rect.center)
        if inputs['hook'] and self.hook_state == 0:
            mouse_world = self.camera.to_world(inputs['mouse_pos'])
            direction = (mouse_world - center).normalize()
            self.hook_pos = pygame.math.Vector2(center)
            self.hook_vel = direction * Config.HOOK_SPEED
            self.hook_state = 1
            self.hook_target_entity = None

        if not inputs['hook']:
            self.hook_state = 0
            self.hook_target_entity = None

        if self.hook_state == 1:
            self.hook_pos += self.hook_vel
            if center.distance_to(self.hook_pos) > Config.HOOK_RANGE:
                self.hook_state = 0
                return
            
            pt_rect = pygame.Rect(self.hook_pos.x, self.hook_pos.y, 1, 1)
            for w in walls:
                if w.colliderect(pt_rect):
                    self.hook_state = 2; break
            
            for entity in entities:
                if entity is not self and entity.is_hookable:
                    if entity.rect.collidepoint(self.hook_pos):
                        self.hook_state = 2
                        self.hook_target_entity = entity
                        break

        if self.hook_state == 2:
            target_pos = self.hook_pos
            if self.hook_target_entity:
                target_pos = pygame.math.Vector2(self.hook_target_entity.rect.center)
                self.hook_pos = target_pos 
            
            direction = target_pos - center
            distance = direction.length()
            if distance > 10:
                direction = direction.normalize()
                self.vel += direction * Config.HOOK_PULL_FORCE
                if self.hook_target_entity:
                    self.hook_target_entity.vel -= direction * Config.HOOK_DRAG_FORCE

    def draw(self, surface, camera):
        center = self.rect.center
        draw_center = camera.apply_point(center)

        # Hook Draw
        if self.hook_state != 0:
            hook_screen = camera.apply_point(self.hook_pos)
            pygame.draw.line(surface, Config.COLOR_HOOK, draw_center, hook_screen, 4)
            pygame.draw.circle(surface, (50, 50, 50), hook_screen, 5)

        # Draw Player
        w = self.rect.width * self.scale_x
        h = self.rect.height * self.scale_y
        draw_rect = pygame.Rect(0, 0, w, h)
        draw_rect.center = draw_center
        
        pygame.draw.rect(surface, Config.COLOR_PLAYER, draw_rect, border_radius=5)
        
        # --- DESENHO DE ARMAS ---
        mouse_pos = pygame.mouse.get_pos()
        mouse_dir = (pygame.math.Vector2(mouse_pos) - pygame.math.Vector2(draw_center))
        if mouse_dir.length() > 0: mouse_dir = mouse_dir.normalize()
        angle = math.degrees(math.atan2(mouse_dir.y, mouse_dir.x))
        
        if self.current_weapon == 1: # Martelo
            self.draw_hammer(surface, draw_center, angle)
        else: # Granada (Laser sight simples)
            weapon_end = (draw_center[0] + mouse_dir.x * 20, draw_center[1] + mouse_dir.y * 20)
            pygame.draw.line(surface, Config.COLOR_GRENADE, draw_center, weapon_end, 6)

        # Olhos
        eye_offset_x = 8 * self.scale_x
        if not self.facing_right: eye_offset_x *= -1 # Inverte olhos
        eye_offset_y = -5 * self.scale_y
        
        eye_l = (draw_center[0] - 6 + (2 if self.facing_right else -2), draw_center[1] + eye_offset_y)
        eye_r = (draw_center[0] + 6 + (2 if self.facing_right else -2), draw_center[1] + eye_offset_y)
        
        pygame.draw.circle(surface, (255, 255, 255), eye_l, 6)
        pygame.draw.circle(surface, (255, 255, 255), eye_r, 6)
        
        pupil_offset = mouse_dir * 2
        pygame.draw.circle(surface, (0, 0, 0), (eye_l[0] + pupil_offset.x, eye_l[1] + pupil_offset.y), 3)
        pygame.draw.circle(surface, (0, 0, 0), (eye_r[0] + pupil_offset.x, eye_r[1] + pupil_offset.y), 3)

    def draw_hammer(self, surface, center, angle):
        # Efeito visual de golpe
        swing_offset = 0
        if self.shoot_cooldown > Config.HAMMER_COOLDOWN * 0.5:
            swing_offset = -45 if self.facing_right else 45
        
        # Surface temporária para rotacionar o martelo
        hammer_surf = pygame.Surface((40, 30), pygame.SRCALPHA)
        
        # Desenha martelo na surface temp
        color_handle = (139, 69, 19)
        color_head = (100, 100, 110)
        pygame.draw.rect(hammer_surf, color_handle, (0, 12, 30, 6)) # Cabo
        pygame.draw.rect(hammer_surf, color_head, (20, 5, 12, 20)) # Cabeça
        
        # Rotação
        rotated_hammer = pygame.transform.rotate(hammer_surf, -angle + swing_offset)
        
        # Posicionamento
        rect = rotated_hammer.get_rect(center=center)
        offset_vec = pygame.math.Vector2(20, 0).rotate(angle)
        rect.centerx += offset_vec.x
        rect.centery += offset_vec.y
        
        surface.blit(rotated_hammer, rect)