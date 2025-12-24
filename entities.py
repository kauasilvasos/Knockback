import pygame
import math
import random
from config import Config
from core import MathUtils
from entities_physics import PhysicsEntity, ParticleManager 
import entities_draw 

# Re-exporta ParticleManager para compatibilidade com o main.py
__all__ = ['Player', 'Projectile', 'ParticleManager', 'PhysicsEntity']

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
            self.explode(entities); return

        for w in walls:
            if self.rect.colliderect(w): self.explode(entities); return

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
                    direction = dist_vec.normalize() if dist > 0 else pygame.math.Vector2(0, -1)
                    entity.vel += direction * (Config.GRENADE_BLAST_FORCE * force_factor)

    def draw(self, surface, camera):
        entities_draw.draw_projectile(surface, camera, self)

class Player(PhysicsEntity):
    def __init__(self, x, y, particles, camera, char_type="BLUE"):
        super().__init__(x, y, 30, 30)
        self.particles = particles
        self.camera = camera
        self.char_type = char_type
        self.color = Config.COLOR_PLAYER_BLUE if char_type == "BLUE" else Config.COLOR_PLAYER_RED
        
        # Physics vars
        self.hook_state = 0 # 0: idle, 1: flying, 2: anchored
        self.hook_pos = pygame.math.Vector2(0,0)
        self.hook_vel = pygame.math.Vector2(0,0)
        self.hook_target_entity = None
        self.hook_tension = 0
        self.jumps_left = 0
        
        # Visuals
        self.scale_x = 1.0; self.scale_y = 1.0; self.facing_right = True
        self.laser_trail = [] 

        # Weapons
        self.current_weapon = 1; self.shoot_cooldown = 0; self.projectiles = [] 

    def set_projectiles_list(self, proj_list):
        self.projectiles = proj_list

    def update(self, inputs, walls, entities):
        # 1. Weapon Switch
        if inputs['weapon1']: self.current_weapon = 1
        if inputs['weapon2']: self.current_weapon = 2

        # 2. Movimento
        accel = Config.MOVE_ACCEL
        if not self.on_ground: accel *= 0.5 
        
        if inputs['left']: self.vel.x -= accel; self.facing_right = False
        if inputs['right']: self.vel.x += accel; self.facing_right = True
        
        friction = Config.FRICTION_GROUND if self.on_ground else Config.FRICTION_AIR
        self.vel.x *= friction

        if self.on_ground: self.jumps_left = Config.MAX_JUMPS
        if inputs['jump'] and self.jumps_left > 0:
            self.vel.y = -Config.JUMP_FORCE; self.jumps_left -= 1
            self.scale_x = 0.7; self.scale_y = 1.3
            self.particles.emit((self.rect.centerx, self.rect.bottom), 5, (200, 200, 200))

        # 3. Actions
        self.update_hook(inputs, walls, entities)
        self.update_weapons(inputs, walls, entities)

        # 4. Physics Walls
        prev_ground = self.on_ground
        self.update_physics(walls)
        self.handle_player_collision(entities)

        if not prev_ground and self.on_ground: self.scale_x = 1.3; self.scale_y = 0.7
        self.scale_x += (1.0 - self.scale_x) * 0.1
        self.scale_y += (1.0 - self.scale_y) * 0.1
        if self.shoot_cooldown < Config.RIFLE_COOLDOWN - 5: self.laser_trail = []

    def handle_player_collision(self, entities):
        for other in entities:
            if other is self or not isinstance(other, PhysicsEntity): continue
            if self.rect.colliderect(other.rect):
                dx = self.rect.centerx - other.rect.centerx
                dy = self.rect.centery - other.rect.centery
                overlap_x = (self.rect.width + other.rect.width) / 2 - abs(dx)
                overlap_y = (self.rect.height + other.rect.height) / 2 - abs(dy)
                if overlap_x < overlap_y:
                    if dx > 0: self.pos.x += overlap_x
                    else: self.pos.x -= overlap_x
                    self.vel.x *= 0.5; self.rect.x = int(self.pos.x)
                else:
                    if dy < 0: 
                        self.pos.y -= overlap_y; self.rect.y = int(self.pos.y); self.vel.y = 0; self.on_ground = True
                        if abs(dx) > 2 or abs(self.vel.x) > 0.1:
                            self.vel.x += (1 if dx > 0 else -1) * 0.8
                    else: self.pos.y += overlap_y; self.rect.y = int(self.pos.y); self.vel.y = 0

    def update_weapons(self, inputs, walls, entities):
        if self.shoot_cooldown > 0: self.shoot_cooldown -= 1
        if inputs['shoot'] and self.shoot_cooldown == 0:
            mouse_world = self.camera.to_world(inputs['mouse_pos'])
            center = pygame.math.Vector2(self.rect.center)
            diff = mouse_world - center
            angle = math.atan2(diff.y, diff.x); direction = diff.normalize()
            if self.char_type == "BLUE":
                if self.current_weapon == 1: 
                    self.shoot_cooldown = Config.HAMMER_COOLDOWN; self.use_melee(center, angle, entities, False); self.camera.trigger_shake(2, 2)
                elif self.current_weapon == 2: 
                    self.shoot_cooldown = Config.GRENADE_COOLDOWN; proj = Projectile(center.x, center.y, angle, self.particles)
                    self.projectiles.append(proj); self.vel -= direction * 4 
            elif self.char_type == "DUMMY":
                if self.current_weapon == 1: 
                    self.shoot_cooldown = Config.HAMMER_COOLDOWN; self.use_melee(center, angle, entities, True); self.camera.trigger_shake(2, 2)
                elif self.current_weapon == 2: 
                    self.shoot_cooldown = Config.RIFLE_COOLDOWN; fire_pos = center + direction * 35 
                    self.use_rifle(fire_pos, direction, walls, entities); self.camera.trigger_shake(3, 4); self.vel -= direction * 2 

    def use_melee(self, center, angle, entities, is_bat):
        hit_range = Config.HAMMER_RANGE; hit_pos = center + pygame.math.Vector2(math.cos(angle), math.sin(angle)) * (hit_range * 0.8)
        force_dir = pygame.math.Vector2(math.cos(angle), math.sin(angle)); hit_something = False
        for entity in entities:
            if entity is not self and isinstance(entity, PhysicsEntity):
                if center.distance_to(entity.rect.center) < hit_range + 30: 
                    hit_something = True; entity.vel += force_dir * (Config.HAMMER_FORCE * 1.2 if is_bat else Config.HAMMER_FORCE)
                    self.particles.emit(entity.rect.center, 10, (255, 255, 255), 5)
        if hit_something: self.particles.emit(hit_pos, 5, (200, 200, 200), 2)

    def use_rifle(self, start_pos, direction, walls, entities):
        trajectory, hit_entity, hit_dir = MathUtils.raycast_bounce(start_pos, direction, walls, entities, Config.RIFLE_MAX_BOUNCES)
        self.laser_trail = trajectory 
        if hit_entity and isinstance(hit_entity, PhysicsEntity):
            hit_entity.vel += hit_dir * Config.RIFLE_FORCE; self.particles.emit(hit_entity.rect.center, 15, Config.COLOR_RIFLE_BEAM, 6)

    def update_hook(self, inputs, walls, entities):
        center = pygame.math.Vector2(self.rect.center)
        
        # 0. Disparo
        if inputs['hook'] and self.hook_state == 0:
            mouse_world = self.camera.to_world(inputs['mouse_pos'])
            direction = (mouse_world - center).normalize()
            self.hook_pos = pygame.math.Vector2(center)
            self.hook_vel = direction * Config.HOOK_SPEED
            self.hook_state = 1
            self.hook_target_entity = None
        
        # Soltar gancho
        if not inputs['hook']:
            self.hook_state = 0; self.hook_target_entity = None; self.hook_tension = 0
            return

        # 1. Gancho em Voo
        if self.hook_state == 1:
            self.hook_pos += self.hook_vel
            if center.distance_to(self.hook_pos) > Config.HOOK_RANGE:
                self.hook_state = 0; return
            
            # Colisão Paredes
            pt_rect = pygame.Rect(self.hook_pos.x, self.hook_pos.y, 1, 1)
            for w in walls:
                if w.colliderect(pt_rect): self.hook_state = 2; break
            
            # --- HITBOX EXPANDIDA PARA ENTIDADES ---
            hook_detector = pygame.Rect(0, 0, 20, 20)
            hook_detector.center = (self.hook_pos.x, self.hook_pos.y)

            for entity in entities:
                if entity is not self and entity.is_hookable:
                    dummy_hitbox = entity.rect.inflate(30, 30) 
                    if dummy_hitbox.colliderect(hook_detector): 
                        self.hook_state = 2; self.hook_target_entity = entity
                        self.hook_pos = pygame.math.Vector2(entity.rect.center)
                        # Yank inicial (puxão de impacto)
                        target_center = pygame.math.Vector2(entity.rect.center)
                        pull_dir = (center - target_center).normalize()
                        entity.vel += pull_dir * Config.HOOK_YANK_FORCE
                        break

        # 2. Gancho Ancorado (Mola Física Mútua)
        if self.hook_state == 2:
            if self.hook_target_entity: 
                target_pos = pygame.math.Vector2(self.hook_target_entity.rect.center)
                self.hook_pos = target_pos 
            else:
                target_pos = self.hook_pos
            
            diff = target_pos - center
            dist = diff.length()

            if dist > 5:
                direction = diff.normalize()
                
                if not self.hook_target_entity:
                    # Puxando a parede
                    self.vel += direction * Config.HOOK_PULL_FORCE
                    self.hook_tension = 0.5
                else:
                    # --- FÍSICA MÚTUA (DUMMY/PLAYER) ---
                    pull_margin = 70 
                    pull_point = center + direction * pull_margin
                    target_center = pygame.math.Vector2(self.hook_target_entity.rect.center)
                    
                    # Lei de Hooke (Aceleração)
                    vec_to_pull = pull_point - target_center
                    spring_force = vec_to_pull * Config.HOOK_SPRING_K
                    
                    # Amortecimento Relativo (Damping)
                    rel_vel = self.hook_target_entity.vel - self.vel
                    damping_force = rel_vel * (1 - Config.HOOK_DAMPING)
                    
                    final_accel = spring_force - damping_force
                    
                    # Aplica força em AMBOS (Ação e Reação)
                    self.hook_target_entity.vel += final_accel
                    self.vel -= final_accel * 0.5 # Tu sentes o peso do dummy
                    
                    # Anti-Gravidade Mútua (Flutuação clean de DDNet)
                    if self.hook_target_entity.vel.y > 0:
                        self.hook_target_entity.vel.y *= 0.94
                    if self.vel.y > 0:
                        self.vel.y *= 0.96

                    # Limites de Velocidade
                    if self.vel.length() > 25: self.vel.scale_to_length(25)
                    
                    self.hook_tension = min(1.0, final_accel.length() / 6.0)

    def draw(self, surface, camera):
        entities_draw.draw_player(surface, camera, self)