import pygame
import math
import random
from config import Config
from core import MathUtils

class ParticleManager:
    def __init__(self): 
        self.particles = []
    
    def emit(self, pos, count, color, speed_range, life_range, size_decay=True):
        for _ in range(count):
            angle = random.uniform(0, 6.28)
            # Velocidade aleatória para criar dispersão natural
            speed = random.uniform(*speed_range)
            vel = pygame.math.Vector2(math.cos(angle) * speed, math.sin(angle) * speed)
            life = random.randint(*life_range)
            # Estrutura: [pos, vel, color, life, max_life, decay_flag]
            self.particles.append([pygame.math.Vector2(pos), vel, list(color), life, life, size_decay])

    def update(self):
        for p in self.particles[:]:
            p[3] -= 1 # Reduz vida
            if p[3] <= 0:
                self.particles.remove(p)
                continue
            
            p[0] += p[1] # Move: pos += vel
            p[1] *= 0.92 # Atrito (Arraste) para as partículas desacelerarem (Splash Effect)

    def draw(self, surface, camera):
        for p in self.particles:
            pos, vel, color, life, max_life, decay = p
            
            # Alpha Fade (desaparece suavemente)
            alpha = int(255 * (life / max_life)) if max_life > 0 else 0
            
            # Tamanho dinâmico
            size = 4
            if decay:
                size = max(0, int(8 * (life / max_life)))
            
            # Desenha com transparência (SRCALPHA)
            s = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            pygame.draw.circle(s, (*color, alpha), (size, size), size)
            
            draw_pos = camera.apply(pos)
            surface.blit(s, (draw_pos.x - size, draw_pos.y - size))

class PhysicsEntity:
    def __init__(self, x, y, size):
        self.pos = pygame.math.Vector2(x, y)
        self.vel = pygame.math.Vector2(0, 0)
        self.size = size
        self.rect = pygame.Rect(x, y, size, size)
        self.on_ground = False
    
    def update_physics(self, walls):
        # Gravidade
        self.vel.y = min(self.vel.y + Config.GRAVITY, Config.TERMINAL_VELOCITY)
        
        # Eixo X
        self.pos.x += self.vel.x
        self.rect.x = round(self.pos.x)
        hits = self.rect.collidelistall(walls)
        for i in hits:
            wall = walls[i]
            if self.vel.x > 0: 
                self.rect.right = wall.left
                self.pos.x = self.rect.x
                self.vel.x = 0
            elif self.vel.x < 0: 
                self.rect.left = wall.right
                self.pos.x = self.rect.x
                self.vel.x = 0
        
        # Eixo Y
        self.pos.y += self.vel.y
        self.rect.y = round(self.pos.y)
        self.on_ground = False
        hits = self.rect.collidelistall(walls)
        for i in hits:
            wall = walls[i]
            if self.vel.y > 0: 
                self.rect.bottom = wall.top
                self.pos.y = self.rect.y
                self.vel.y = 0
                self.on_ground = True
            elif self.vel.y < 0: 
                self.rect.top = wall.bottom
                self.pos.y = self.rect.y
                self.vel.y = 0

    def apply_knockback(self, force_vec):
        self.vel += force_vec
        self.on_ground = False

class Player(PhysicsEntity):
    def __init__(self, x, y, particles, camera_ref):
        super().__init__(x, y, 30)
        self.particles = particles
        self.camera = camera_ref
        self.jumps_left = 2
        self.facing_right = True
        
        self.hook_active = False
        self.hook_pos = pygame.math.Vector2(0,0)
        self.hook_vel = pygame.math.Vector2(0,0)
        self.hook_state = "IDLE" 
        
        self.weapon_cooldown = 0
        self.aim_dir = pygame.math.Vector2(1, 0)

    def update(self, actions, walls, projectiles_list=None):
        # Mira
        mouse_screen = pygame.math.Vector2(actions['mouse_pos'])
        mouse_world = mouse_screen - pygame.math.Vector2(self.camera.camera.topleft)
        player_center = self.pos + pygame.math.Vector2(self.size/2, self.size/2)
        
        aim_vec = mouse_world - player_center
        if aim_vec.length() > 0: self.aim_dir = aim_vec.normalize()
        
        if mouse_world.x > player_center.x: self.facing_right = True
        else: self.facing_right = False

        # Movimento
        if actions['left']: self.vel.x -= Config.MOVE_ACCEL
        if actions['right']: self.vel.x += Config.MOVE_ACCEL
        
        friction = Config.MOVE_FRICTION if self.on_ground else Config.AIR_FRICTION
        if self.hook_state == "HOOKED": friction = 0.999 
        self.vel.x *= friction
        
        if actions['up']:
            if self.on_ground:
                self.vel.y = -Config.JUMP_FORCE
                self.jumps_left = 1
                # Efeito de poeira no pulo
                self.particles.emit(self.rect.midbottom, 5, (200,200,200), (1, 3), (10, 20))
            elif self.jumps_left > 0 and not self.hook_active:
                self.vel.y = -Config.DOUBLE_JUMP_FORCE
                self.jumps_left = 0
                self.particles.emit(self.rect.midbottom, 5, (150,200,255), (1, 3), (10, 20))

        # HOOK
        if actions['hook']:
            if self.hook_state == "IDLE":
                self.hook_state = "THROWN"
                self.hook_pos = pygame.math.Vector2(player_center)
                self.hook_vel = self.aim_dir * Config.HOOK_SPEED
        else:
            self.hook_state = "IDLE"
            self.hook_active = False

        if self.hook_state == "THROWN":
            self.hook_pos += self.hook_vel
            for wall in walls:
                if wall.collidepoint(self.hook_pos):
                    self.hook_state = "HOOKED"
                    self.hook_active = True
                    self.camera.trigger_shake(2, 5) # Shake leve ao conectar
                    # Faíscas ao conectar
                    self.particles.emit(self.hook_pos, 8, (255,255,200), (2, 5), (10, 20))
                    break
            if self.hook_pos.distance_to(player_center) > Config.HOOK_RANGE:
                self.hook_state = "IDLE"

        if self.hook_state == "HOOKED":
            rope_vec = self.hook_pos - player_center
            dist = rope_vec.length()
            rope_dir = MathUtils.normalize_safe(rope_vec)
            
            if dist > 50:
                self.vel += rope_dir * Config.HOOK_PULL_FORCE * (dist * 0.05)
            
            tangent = pygame.math.Vector2(-rope_dir.y, rope_dir.x)
            input_dir = 0
            if actions['left']: input_dir = -1
            if actions['right']: input_dir = 1
            if input_dir != 0:
                self.vel += tangent * input_dir * Config.HOOK_SWING_FORCE
            
            self.vel *= Config.HOOK_DRAG

        # TIRO (Granada de Impacto)
        if self.weapon_cooldown > 0: self.weapon_cooldown -= 1
        
        if actions['shoot'] and self.weapon_cooldown == 0 and projectiles_list is not None:
            self.weapon_cooldown = 25 # Cadência de tiro
            
            # Velocidade inicial + Inércia do jogador
            start_vel = self.aim_dir * Config.GRENADE_SPEED + (self.vel * 0.4)
            
            projectiles_list.append(Grenade(player_center.x, player_center.y, start_vel, self.particles, self.camera))
            
            # Recuo (Juice)
            self.vel -= self.aim_dir * 3.0 
            self.camera.trigger_shake(3, 5) # Shake leve no disparo

        self.update_physics(walls)

    def draw(self, surface, camera):
        player_center = self.pos + pygame.math.Vector2(self.size/2, self.size/2)
        
        # Desenha Hook
        if self.hook_active or self.hook_state == "THROWN":
            start = camera.apply(player_center)
            end = camera.apply(self.hook_pos)
            pygame.draw.line(surface, Config.COLOR_HOOK, start, end, 3)
            pygame.draw.circle(surface, Config.COLOR_HOOK, end, 5)

        # Desenha Player
        rect_draw = camera.apply(self.rect)
        pygame.draw.rect(surface, Config.COLOR_PLAYER, rect_draw, border_radius=4)
        
        # Desenha Arma
        start_gun = rect_draw.center
        end_gun = (start_gun[0] + self.aim_dir.x * 25, start_gun[1] + self.aim_dir.y * 25)
        pygame.draw.line(surface, (40,40,40), start_gun, end_gun, 6)

class Grenade(PhysicsEntity):
    def __init__(self, x, y, velocity, particle_sys, camera_ref):
        super().__init__(x, y, 12)
        self.vel = velocity
        self.particles = particle_sys
        self.camera = camera_ref
        self.timer = 180 # Tempo máximo de vida (se não bater em nada)
        self.max_timer = 180
        self.active = True

    def update(self, walls, entities):
        if not self.active: return
        
        self.vel.y += Config.GRAVITY
        
        # Colisão com Paredes (Impacto Instantâneo)
        self.pos.x += self.vel.x
        self.rect.x = round(self.pos.x)
        if self.rect.collidelist(walls) != -1:
            self.explode(entities)
            return

        self.pos.y += self.vel.y
        self.rect.y = round(self.pos.y)
        if self.rect.collidelist(walls) != -1:
            self.explode(entities)
            return

        # Colisão com Entidades (Bots/Player)
        # Grace period: só explode em entidades após 10 frames de vida
        # para não explodir no próprio jogador instantaneamente.
        if (self.max_timer - self.timer) > 10:
            for e in entities:
                # Ignora a si mesmo na checagem
                if e is not self and self.rect.colliderect(e.rect):
                    self.explode(entities)
                    return

        self.timer -= 1
        if self.timer <= 0:
            self.explode(entities)

    def explode(self, entities):
        if not self.active: return
        self.active = False
        
        # --- GAME FEEL: SPLASH EFFECT ---
        # 1. Screen Shake forte
        self.camera.trigger_shake(15, 12) 
        
        # 2. Partículas (Splash Visual)
        center = self.pos + pygame.math.Vector2(self.size/2, self.size/2)
        
        # Camada 1: Núcleo (Flash Branco/Amarelo - Rápido)
        self.particles.emit(center, 15, (255, 255, 200), (6, 12), (5, 15))
        
        # Camada 2: Explosão Principal (Laranja/Vermelho - Médio)
        self.particles.emit(center, 30, (255, 100, 50), (3, 8), (20, 40))
        
        # Camada 3: Fumaça/Detritos (Cinza Escuro - Lento e Duradouro)
        self.particles.emit(center, 20, (100, 100, 100), (1, 4), (40, 70))

        # 3. Lógica de Dano e Knockback
        for e in entities:
            if hasattr(e, 'is_dead') and e.is_dead: continue
            if e is self: continue
            
            ent_center = e.pos + pygame.math.Vector2(e.size/2, e.size/2)
            dist = center.distance_to(ent_center)
            
            if dist < Config.EXPLOSION_RADIUS:
                # Vetor de força normalizado
                force_dir = MathUtils.normalize_safe(ent_center - center)
                
                # Força decai com a distância (mais perto = mais forte)
                knockback_mag = Config.EXPLOSION_FORCE * (1 - (dist / Config.EXPLOSION_RADIUS))
                
                e.apply_knockback(force_dir * knockback_mag)
                
                if hasattr(e, 'hp'):
                    e.hp -= 40
                    if e.hp <= 0: e.is_dead = True

    def draw(self, surface, camera):
        if not self.active: return
        draw_pos = camera.apply(self.rect)
        
        # Desenha a granada piscando (aviso visual)
        color = (50, 50, 50)
        if (self.timer // 4) % 2 == 0: 
            color = (200, 50, 50)
            
        pygame.draw.circle(surface, color, draw_pos.center, 6)
        pygame.draw.circle(surface, (255,255,255), draw_pos.center, 2)

class Bot(PhysicsEntity):
    def __init__(self, x, y):
        super().__init__(x, y, 30)
        self.hp = 100
        self.is_dead = False
        self.move_timer = 0
        self.dir = 0

    def update_ai(self, walls):
        if self.is_dead: return
        self.move_timer -= 1
        if self.move_timer <= 0:
            self.move_timer = random.randint(50, 150)
            self.dir = random.choice([-1, 0, 1])
        
        if self.dir: 
            self.vel.x += self.dir * 0.5
            self.vel.x = max(min(self.vel.x, 3), -3) # Cap de velocidade
            
        self.update_physics(walls)
        self.vel.x *= Config.MOVE_FRICTION

    def draw(self, surface, camera):
        if self.is_dead: return
        
        rect_draw = camera.apply(self.rect)
        
        # Efeito de dano (piscar branco se tomou dano recentemente seria legal, mas simples por enquanto)
        color = (200, 50, 50)
        pygame.draw.rect(surface, color, rect_draw, border_radius=4)
        
        # Barra de HP
        hp_width = 30 * (self.hp / 100)
        pygame.draw.rect(surface, (0,0,0), (rect_draw.x, rect_draw.y - 10, 30, 6))
        pygame.draw.rect(surface, (0,255,0), (rect_draw.x, rect_draw.y - 10, hp_width, 6))