import pygame
import math
import random
from config import Config

# ==============================================================================
# 1. CLASSE BASE DE FÍSICA (Corrigida e Estruturada)
# ==============================================================================
class PhysicsEntity:
    def __init__(self, x, y, size):
        self.pos = pygame.math.Vector2(x, y)
        self.vel = pygame.math.Vector2(0, 0)
        self.acc = pygame.math.Vector2(0, 0)
        self.size = size
        self.on_ground = False

    @property
    def rect(self):
        return pygame.Rect(self.pos.x, self.pos.y, self.size, self.size)

    def apply_force(self, f):
        self.acc += pygame.math.Vector2(f)

    def update_physics(self):
        self.acc.y += Config.GRAVITY
        self.vel += self.acc
        if not self.on_ground:
            self.vel *= Config.AIR_RESISTANCE
        self.pos += self.vel
        self.acc *= 0

    def resolve_collisions(self, map_rects):
        self.on_ground = False
        r = self.rect
        
        # Eixo X
        r.x = self.pos.x + self.vel.x
        for m in map_rects:
            if r.colliderect(m):
                if self.vel.x > 0: self.pos.x = m.left - self.size
                elif self.vel.x < 0: self.pos.x = m.right
                self.vel.x = 0
                r.x = self.pos.x

        # Eixo Y
        r.y = self.pos.y + self.vel.y
        for m in map_rects:
            if r.colliderect(m):
                if self.vel.y > 0: # Pousando
                    self.pos.y = m.top - self.size
                    self.on_ground = True
                elif self.vel.y < 0: # Batendo cabeça
                    self.pos.y = m.bottom
                self.vel.y = 0

# ==============================================================================
# 2. SISTEMA DE PARTÍCULAS
# ==============================================================================
class Particle:
    def __init__(self, x, y, color, velocity, life):
        self.pos = pygame.math.Vector2(x, y)
        self.vel = pygame.math.Vector2(velocity)
        self.color = color
        self.life = life
        self.original_life = life

    def update(self):
        self.pos += self.vel
        self.life -= 1
        self.vel *= 0.95

    def draw(self, surface, camera):
        if self.life <= 0: return
        alpha = int((self.life / self.original_life) * 255)
        size = max(1, int(4 * (self.life / self.original_life)))
        surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
        pygame.draw.circle(surf, (*self.color, alpha), (size, size), size)
        draw_pos = camera.apply(self.pos)
        surface.blit(surf, (draw_pos.x - size, draw_pos.y - size))

class ParticleManager:
    def __init__(self):
        self.particles = []

    def emit(self, x, y, count, color, speed_range):
        for _ in range(count):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(speed_range[0], speed_range[1])
            vel = (math.cos(angle) * speed, math.sin(angle) * speed)
            life = random.randint(20, 40)
            self.particles.append(Particle(x, y, color, vel, life))

    def update(self):
        self.particles = [p for p in self.particles if p.life > 0]
        for p in self.particles: p.update()

    def draw(self, surface, camera):
        for p in self.particles: p.draw(surface, camera)

# ==============================================================================
# 3. ENTIDADES DO JOGO (PLAYER COM GAME FEEL)
# ==============================================================================
class Player(PhysicsEntity):
    def __init__(self, x, y, particle_system, camera_ref):
        super().__init__(x, y, 30)
        self.particle_system = particle_system
        self.camera_ref = camera_ref
        
        # Hook Vars
        self.hook_active = False
        self.hook_pos = pygame.math.Vector2(0, 0)
        
        # Game Feel Vars
        self.trail = []
        self.was_on_ground = False
        self.weapon_cooldown = 0
        self.scale = pygame.math.Vector2(1, 1) # [Squash, Stretch]

    def input_update(self, actions, map_rects, projectiles_list=None):
        accel_mod = 0.2 if self.hook_active else 1.0

        # --- Voltar escala ao normal (Elasticidade) ---
        # Lerp suave de volta para (1, 1)
        self.scale.x += (1.0 - self.scale.x) * 0.1
        self.scale.y += (1.0 - self.scale.y) * 0.1

        # Movimento
        if actions.get('left'): self.apply_force((-Config.MOVE_ACCEL * accel_mod, 0))
        if actions.get('right'): self.apply_force((Config.MOVE_ACCEL * accel_mod, 0))

        # Pulo (Com Stretch - Estica verticalmente)
        if actions.get('up') and self.on_ground:
            self.vel.y = -Config.JUMP_FORCE
            self.on_ground = False
            self.scale = pygame.math.Vector2(0.7, 1.4) # <-- Efeito visual
            if self.particle_system:
                self.particle_system.emit(self.pos.x+15, self.pos.y+30, 5, (200,200,200), (1,3))

        # Hook Logic
        if actions.get('fire'):
            if not self.hook_active:
                target = pygame.math.Vector2(actions.get('mouse_pos', (0,0)))
                # Adiciona um pequeno "jitter" para o alvo não ser pixel perfect (Game Feel)
                target.x += random.randint(-2, 2)
                target.y += random.randint(-2, 2)
                
                direction = (target - self.pos)
                if direction.length() <= Config.HOOK_RANGE:
                    for rect in map_rects:
                        if rect.collidepoint(target):
                            self.hook_active = True
                            self.hook_pos = target
                            if self.particle_system:
                                self.particle_system.emit(target.x, target.y, 8, Config.COLOR_HOOK, (1,3))
                            if self.camera_ref:
                                self.camera_ref.trigger_shake(2, 4)
                            break
        else:
            self.hook_active = False

        if self.hook_active:
            hook_vec = self.hook_pos - self.pos
            dist = hook_vec.length()
            if dist > 0:
                hook_dir = hook_vec.normalize()
                spring_force = dist * 0.05
                self.apply_force(hook_dir * spring_force * Config.HOOK_FORCE)
                self.vel *= 0.96

        super().update_physics()
        super().resolve_collisions(map_rects)

        # Impacto no chão (Com Squash - Amassa horizontalmente)
        if self.on_ground and not self.was_on_ground:
            if abs(self.vel.y) > 2:
                self.scale = pygame.math.Vector2(1.4, 0.7) # <-- Efeito visual
                if self.particle_system:
                    self.particle_system.emit(self.pos.x+15, self.pos.y+30, 8, Config.COLOR_GROUND, (1,4))
        
        self.was_on_ground = self.on_ground

        # Rastro
        if len(self.trail) > 5: self.trail.pop(0)
        self.trail.append((self.pos.x, self.pos.y))

        # Tiro
        if self.weapon_cooldown > 0: self.weapon_cooldown -= 1
        if actions.get('shoot') and self.weapon_cooldown == 0 and projectiles_list is not None:
            self.weapon_cooldown = 40
            mouse_pos = pygame.math.Vector2(actions.get('mouse_pos', (0,0)))
            center = self.pos + pygame.math.Vector2(15, 15)
            diff = mouse_pos - center
            angle = math.atan2(diff.y, diff.x)
            # Recuo visual no Player
            self.vel -= diff.normalize() * 0.5
            projectiles_list.append(Projectile(center.x, center.y, angle, 2.7, self))

    def draw_hook(self, surface):
        """Desenha uma corrente estilizada em vez de uma linha."""
        if not self.hook_active: return

        player_center = self.pos + pygame.math.Vector2(self.size/2, self.size/2)
        hook_vec = self.hook_pos - player_center
        dist = hook_vec.length()
        direction = hook_vec.normalize()

        # Desenha elos da corrente a cada 15 pixels
        link_spacing = 15
        for i in range(0, int(dist), link_spacing):
            link_pos = player_center + direction * i
            draw_pos = self.camera_ref.apply(link_pos)
            # Elos alternam levemente de cor para dar textura
            color = (100, 100, 100) if (i // link_spacing) % 2 == 0 else (70, 70, 70)
            pygame.draw.circle(surface, color, (int(draw_pos.x), int(draw_pos.y)), 3)

        # Desenha a Garra na ponta
        claw_pos = self.camera_ref.apply(self.hook_pos)
        pygame.draw.circle(surface, (200, 50, 50), (int(claw_pos.x), int(claw_pos.y)), 4)
        pygame.draw.circle(surface, (50, 50, 50), (int(claw_pos.x), int(claw_pos.y)), 2)


    def draw(self, surface):
        # 1. Desenha Hook (atrás do player)
        self.draw_hook(surface)

        # 2. Desenha Player com Transformação (Squash & Stretch)
        # Cria uma surface temporária para o player
        player_surf = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        pygame.draw.rect(player_surf, Config.COLOR_PLAYER, (0, 0, self.size, self.size), border_radius=8)
        
        # Calcula novo tamanho baseado na escala
        new_w = int(self.size * self.scale.x)
        new_h = int(self.size * self.scale.y)
        scaled_surf = pygame.transform.scale(player_surf, (new_w, new_h))
        
        # Centraliza a imagem escalada na posição original
        # O Rect de desenho deve estar compensado pela diferença de tamanho para manter o centro
        draw_rect = self.camera_ref.apply(self.rect)
        offset_x = (new_w - self.size) // 2
        offset_y = (new_h - self.size) # Alinha pela base (pés), não pelo centro, para não enterrar no chão
        
        surface.blit(scaled_surf, (draw_rect.x - offset_x, draw_rect.y - offset_y))
        
        # Olhos (para dar direção)
        eye_x = draw_rect.centerx + (pygame.mouse.get_pos()[0] - draw_rect.centerx) * 0.1
        eye_y = draw_rect.centery + (pygame.mouse.get_pos()[1] - draw_rect.centery) * 0.1
        pygame.draw.circle(surface, (255,255,255), (eye_x, eye_y), 4)


class Projectile(PhysicsEntity):
    def __init__(self, x, y, angle, force, owner):
        super().__init__(x, y, 14)
        self.owner = owner
        self.vel.x = math.cos(angle) * force
        self.vel.y = math.sin(angle) * force
        self.active = True

    def update(self, map_rects, entities, particle_system, camera):
        if not self.active: return
        self.acc.y += Config.GRAVITY * 0.5
        self.vel += self.acc
        self.pos += self.vel
        self.acc *= 0

        rect = self.rect
        if rect.collidelist(map_rects) != -1:
            self.explode(entities, particle_system, camera)
        elif self.pos.y > 2000 or self.pos.x < -1000 or self.pos.x > 3000:
            self.active = False

    def explode(self, entities, particle_system, camera):
        self.active = False
        center = self.pos + pygame.math.Vector2(7, 7)
        if camera: camera.trigger_shake(6, 8)
        if particle_system:
            particle_system.emit(center.x, center.y, 20, (255,100,50), (2,8))

        for entity in entities:
            e_center = entity.pos + pygame.math.Vector2(entity.size/2, entity.size/2)
            dist = e_center.distance_to(center)
            if dist < Config.EXPLOSION_RADIUS and dist > 0:
                direction = (e_center - center).normalize()
                force = (1.0 - (dist / Config.EXPLOSION_RADIUS)) * Config.KNOCKBACK_FORCE
                entity.vel += direction * force
                entity.on_ground = False
                if hasattr(entity, 'take_damage'):
                    entity.take_damage(int(20 * (1.0 - dist/Config.EXPLOSION_RADIUS)))

class Bot(PhysicsEntity):
    def __init__(self, x, y, particle_system):
        super().__init__(x, y, 30)
        self.particle_system = particle_system
        self.color = (200, 50, 50)
        self.hp = 100
        self.max_hp = 100
        self.is_dead = False
        self.move_timer = 0
        self.jump_timer = 0
        self.current_move = 0

    def update_ai(self, map_rects):
        if self.is_dead: return
        self.move_timer -= 1
        if self.move_timer <= 0:
            self.move_timer = random.randint(30, 120)
            self.current_move = random.choice([-1, 0, 1])
        if self.current_move != 0: self.apply_force((Config.MOVE_ACCEL * self.current_move, 0))
        self.jump_timer -= 1
        if self.jump_timer <= 0 and self.on_ground:
            if random.random() < 0.4: self.vel.y = -Config.JUMP_FORCE
            self.jump_timer = random.randint(60, 180)
        super().update_physics()
        super().resolve_collisions(map_rects)
        if self.pos.y > 2000: self.take_damage(999)

    def take_damage(self, amount):
        self.hp -= amount
        if self.particle_system: self.particle_system.emit(self.pos.x+15, self.pos.y+15, 5, self.color, (2,6))
        if self.hp <= 0: self.die()

    def die(self):
        self.is_dead = True
        if self.particle_system: self.particle_system.emit(self.pos.x+15, self.pos.y+15, 30, self.color, (3,10))

    def draw(self, surface, camera):
        if self.is_dead: return
        draw_rect = camera.apply(self.rect)
        pygame.draw.rect(surface, self.color, draw_rect, border_radius=8)
        hp_pct = max(0, self.hp / self.max_hp)
        bar_pos = (draw_rect.centerx - 20, draw_rect.y - 10)
        pygame.draw.rect(surface, (50,0,0), (*bar_pos, 40, 5))
        pygame.draw.rect(surface, (0,255,0), (*bar_pos, 40 * hp_pct, 5))