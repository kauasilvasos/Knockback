import pygame
import math
import random
from config import Config

# ==============================================================================
# 1. CLASSE BASE DE FÍSICA
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
        
        # Atrito padrão (será sobrescrito no Player se estiver de Hook)
        if not self.on_ground:
            self.vel *= Config.AIR_RESISTANCE
            
        self.pos += self.vel
        self.acc *= 0

    def resolve_collisions(self, map_rects):
        self.on_ground = False
        r = self.rect
        
        # Colisão X
        r.x = self.pos.x + self.vel.x
        for m in map_rects:
            if r.colliderect(m):
                if self.vel.x > 0: self.pos.x = m.left - self.size
                elif self.vel.x < 0: self.pos.x = m.right
                self.vel.x = 0
                r.x = self.pos.x

        # Colisão Y
        r.y = self.pos.y + self.vel.y
        for m in map_rects:
            if r.colliderect(m):
                if self.vel.y > 0: # Caindo
                    self.pos.y = m.top - self.size
                    self.on_ground = True
                elif self.vel.y < 0: # Batendo cabeça
                    self.pos.y = m.bottom
                    self.vel.y = 0 # Para seco ao bater a cabeça
                else:
                    self.vel.y = 0
                
                # Nota: Não zeramos vel.y ao cair aqui para permitir calculo de impacto depois,
                # mas zeramos a posição. Se for chão, o update zera a gravidade acumulada se não tratar.
                if self.on_ground:
                    self.vel.y = 0

# RECOPIE AS CLASSES Particle e ParticleManager AQUI SE NECESSÁRIO, OU MANTENHA AS DO ARQUIVO ANTERIOR
# Vou incluir ParticleManager resumido para garantir funcionamento:

class Particle:
    def __init__(self, x, y, color, velocity, life):
        self.pos, self.vel, self.color, self.life, self.orig = pygame.math.Vector2(x,y), pygame.math.Vector2(velocity), color, life, life
    def update(self):
        self.pos += self.vel
        self.life -= 1
        self.vel *= 0.95
    def draw(self, surf, cam):
        if self.life > 0:
            sz = max(1, int(4 * (self.life/self.orig)))
            s = pygame.Surface((sz*2, sz*2), pygame.SRCALPHA)
            pygame.draw.circle(s, (*self.color, int(255*(self.life/self.orig))), (sz,sz), sz)
            dp = cam.apply(self.pos)
            surf.blit(s, (dp.x-sz, dp.y-sz))

class ParticleManager:
    def __init__(self): self.p = []
    def emit(self, x, y, c, col, spd):
        for _ in range(c):
            a = random.uniform(0, 6.28)
            s = random.uniform(*spd)
            self.p.append(Particle(x, y, col, (math.cos(a)*s, math.sin(a)*s), random.randint(20,40)))
    def update(self): 
        self.p = [x for x in self.p if x.life > 0]
        for x in self.p: x.update()
    def draw(self, s, c): 
        for x in self.p: x.draw(s, c)

# ==============================================================================
# 3. PLAYER COM FÍSICA DE HOOK DESLIZANTE
# ==============================================================================
class Player(PhysicsEntity):
    def __init__(self, x, y, particle_system, camera_ref):
        super().__init__(x, y, 30)
        self.particle_system = particle_system
        self.camera_ref = camera_ref
        
        self.jumps_left = 2
        self.hook_active = False
        self.hook_pos = pygame.math.Vector2(0, 0)
        self.hook_vel = pygame.math.Vector2(0, 0)
        self.hook_state = "IDLE" # IDLE, FLYING, ATTACHED
        self.hooked_entity = None

        self.trail = []
        self.was_on_ground = False
        self.weapon_cooldown = 0
        self.scale = pygame.math.Vector2(1, 1)

        # Direção da mira (input)
        self.aim_dir = pygame.math.Vector2(1, 0)

    # No arquivo entities.py, dentro da classe Player:

    def input_update(self, actions, map_rects, projectiles_list=None, bots_list=None):
        accel_mod = 0.4 if self.hook_active else 1.0

        if self.on_ground:
            self.jumps_left = 2
            
        # 1. Recuperação de Escala (Squash & Stretch)
        self.scale.x += (1.0 - self.scale.x) * 0.1
        self.scale.y += (1.0 - self.scale.y) * 0.1

        # 2. Atualização da Mira
        mouse_vec = pygame.math.Vector2(actions.get('mouse_pos', (0,0)))
        player_center_world = self.pos + pygame.math.Vector2(self.size/2, self.size/2)
        aim_vec = mouse_vec - player_center_world
        if aim_vec.length() > 0:
            self.aim_dir = aim_vec.normalize()

        # 3. Movimento e Pulo
        if actions.get('left'): self.apply_force((-Config.MOVE_ACCEL * accel_mod, 0))
        if actions.get('right'): self.apply_force((Config.MOVE_ACCEL * accel_mod, 0))

        # Pulo simples e pulo duplo
        if actions.get('up'):
            if self.on_ground and self.jumps_left > 0:
                self.vel.y = -Config.JUMP_FORCE
                self.on_ground = False
                self.jumps_left -= 1
                self.scale = pygame.math.Vector2(0.7, 1.4)
                if self.particle_system:
                    self.particle_system.emit(self.pos.x+15, self.pos.y+30, 5, (200,200,200), (1,3))
            elif (not self.on_ground) and self.jumps_left == 1:
                # Pulo duplo
                self.vel.y = -Config.DOUBLE_JUMP_FORCE
                self.jumps_left = 0
                self.scale = pygame.math.Vector2(0.8, 1.2)
                if self.particle_system:
                    self.particle_system.emit(self.pos.x+15, self.pos.y+30, 10, (255,220,120), (2,4))

        # 4. Lógica do Hook (Só enquanto segura)
        # --- Lógica de Hook para Ar e Entidades ---
        if actions.get('fire'):
            if self.hook_state == "IDLE":
                self.hook_state = "FLYING"
                self.hook_pos = pygame.math.Vector2(player_center_world)
                self.hook_vel = self.aim_dir * Config.HOOK_FLY_SPEED
                self.hooked_entity = None
        else:
            self.hook_state = "IDLE"
            self.hook_active = False

        if self.hook_state == "FLYING":
            self.hook_pos += self.hook_vel
            # Se atingir distância máxima no ar, o hook volta (estilo DDNet)
            if self.hook_pos.distance_to(player_center_world) > Config.HOOK_RANGE:
                self.hook_state = "IDLE"
            
            # Verifica colisão com mapa
            for rect in map_rects:
                if rect.collidepoint(self.hook_pos):
                    self.hook_state = "ATTACHED"
                    self.hook_active = True
                    break
                    
            # Verifica colisão com outros bots/players (bots_list deve conter bots)
            if bots_list:
                for bot in bots_list:
                    if bot.rect.collidepoint(self.hook_pos):
                        self.hook_state = "ATTACHED"
                        self.hook_active = True
                        self.hooked_entity = bot
                        break

        # --- Efeito Pêndulo (Tração não Linear) ---
        if self.hook_state == "ATTACHED":
            # Se preso a uma entidade, atualiza posição do gancho
            if hasattr(self, 'hooked_entity') and self.hooked_entity:
                try:
                    self.hook_pos = self.hooked_entity.pos + pygame.math.Vector2(15, 15)
                except Exception:
                    pass
                # Aplica força na entidade também (puxa um contra o outro)
                dir_to_player = (self.pos - self.hook_pos)
                if dir_to_player.length() > 0:
                    dir_to_player = dir_to_player.normalize()
                    try:
                        self.hooked_entity.apply_force(dir_to_player * 0.05)
                    except Exception:
                        pass

            hook_vec = self.hook_pos - self.pos
            dist = hook_vec.length()
            if dist > 0:
                hook_dir = hook_vec.normalize()
                pull_strength = dist * 0.01 * Config.HOOK_FORCE
                self.apply_force(hook_dir * pull_strength)
                self.vel *= Config.HOOK_DRAG

        # 5. LÓGICA DE DISPARO (Corrigida)
        if self.weapon_cooldown > 0:
            self.weapon_cooldown -= 1

        if actions.get('shoot') and self.weapon_cooldown == 0:
            self.weapon_cooldown = 40 
            if projectiles_list is not None:
                # Dispara na direção exata da mira
                angle = math.atan2(self.aim_dir.y, self.aim_dir.x)
                new_proj = Projectile(player_center_world.x, player_center_world.y, angle, 5.0, self)
                projectiles_list.append(new_proj)
                # Recuo visual
                self.vel -= self.aim_dir * 1.5

        # 6. Física Final
        self.update_physics()
        self.resolve_collisions_custom(map_rects)

        # Física de tração quando preso
        if self.hook_state == "ATTACHED":
            hook_vec = self.hook_pos - self.pos
            dist = hook_vec.length()
            if dist > 0:
                hook_dir = hook_vec.normalize()
                self.apply_force(hook_dir * dist * 0.08 * Config.HOOK_FORCE)
                self.vel *= Config.HOOK_DRAG

        # Física Geral e Colisão Customizada
        self.update_physics()
        self.resolve_collisions_custom(map_rects)

        # Game Feel de impacto
        if self.on_ground and not self.was_on_ground:
            if abs(self.vel.y) > 2:
                self.scale = pygame.math.Vector2(1.4, 0.7)
                if self.particle_system:
                    self.particle_system.emit(self.pos.x+15, self.pos.y+30, 8, Config.COLOR_GROUND, (1,4))
        self.was_on_ground = self.on_ground
    def resolve_collisions_custom(self, map_rects):
        """Versão modificada que permite deslizar melhor quando usa o gancho."""
        self.on_ground = False
        r = self.rect
        
        # X Axis
        r.x = self.pos.x + self.vel.x
        for m in map_rects:
            if r.colliderect(m):
                if self.vel.x > 0: self.pos.x = m.left - self.size
                elif self.vel.x < 0: self.pos.x = m.right
                
                # Se estiver de hook, não zera a velocidade X completamente se houver força vertical forte
                # Isso simula 'deslizar' na parede
                if not self.hook_active:
                    self.vel.x = 0
                else:
                    self.vel.x *= 0.5 # Perde velocidade mas não para
                
                r.x = self.pos.x

        # Y Axis
        r.y = self.pos.y + self.vel.y
        for m in map_rects:
            if r.colliderect(m):
                if self.vel.y > 0: 
                    self.pos.y = m.top - self.size
                    self.on_ground = True
                    self.vel.y = 0 # No chão para mesmo
                elif self.vel.y < 0: 
                    self.pos.y = m.bottom
                    self.vel.y = 0 
                r.y = self.pos.y

    def draw_hook(self, surface):
        if self.hook_state == "IDLE": return
        if not self.hook_active: return
        player_center = self.pos + pygame.math.Vector2(self.size/2, self.size/2)
        hook_vec = self.hook_pos - player_center
        dist = hook_vec.length()
        direction = hook_vec.normalize()
        
        # Desenha corrente
        for i in range(0, int(dist), 15):
            pos = player_center + direction * i
            dp = self.camera_ref.apply(pos)
            pygame.draw.circle(surface, (80,80,80), (int(dp.x), int(dp.y)), 2)
        
        # Garra
        cp = self.camera_ref.apply(self.hook_pos)
        pygame.draw.circle(surface, Config.COLOR_HOOK, (int(cp.x), int(cp.y)), 4)

    def draw(self, surface):
        self.draw_hook(surface)
        
        # Corpo com Squash/Stretch
        player_surf = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        pygame.draw.rect(player_surf, Config.COLOR_PLAYER, (0,0,self.size,self.size), border_radius=8)
        
        w = int(self.size * self.scale.x)
        h = int(self.size * self.scale.y)
        scaled = pygame.transform.scale(player_surf, (w, h))
        
        dr = self.camera_ref.apply(self.rect)
        # Ajusta offset para manter os pés no lugar
        off_x = (w - self.size)//2
        off_y = (h - self.size)
        
        surface.blit(scaled, (dr.x - off_x, dr.y - off_y))
        
        # Olhos baseados na mira (aim_dir)
        eye_base = pygame.math.Vector2(dr.centerx, dr.centery)
        eye_offset = self.aim_dir * 6
        pygame.draw.circle(surface, (255,255,255), (int(eye_base.x + eye_offset.x), int(eye_base.y + eye_offset.y)), 5)

# (Mantenha Projectile e Bot como estavam ou copie do anterior, mas a PhysicsEntity precisa estar atualizada no topo)
class Projectile(PhysicsEntity):
    def __init__(self, x, y, angle, force, owner):
        super().__init__(x, y, 14)
        self.owner, self.vel.x, self.vel.y, self.active = owner, math.cos(angle)*force, math.sin(angle)*force, True
    def update(self, map_rects, entities, p_sys, cam):
        if not self.active: return
        self.acc.y += Config.GRAVITY * 0.5
        self.vel += self.acc
        self.pos += self.vel
        self.acc *= 0
        if self.rect.collidelist(map_rects) != -1: self.explode(entities, p_sys, cam)
        elif not (-1000 < self.pos.x < 3000 and self.pos.y < 2000): self.active = False
    def explode(self, entities, p_sys, cam):
        self.active = False
        c = self.pos + pygame.math.Vector2(7,7)
        if cam: cam.trigger_shake(6,8)
        if p_sys: p_sys.emit(c.x, c.y, 20, (255,100,50), (2,8))
        for e in entities:
            dist = (e.pos + pygame.math.Vector2(15,15)).distance_to(c)
            if dist < Config.EXPLOSION_RADIUS and dist > 0:
                force = (1.0 - dist/Config.EXPLOSION_RADIUS) * Config.KNOCKBACK_FORCE
                e.vel += (e.pos - self.pos).normalize() * force
                e.on_ground = False
                if hasattr(e, 'take_damage'): e.take_damage(int(20*force))

class Bot(PhysicsEntity):
    def __init__(self, x, y, p_sys):
        super().__init__(x, y, 30)
        self.p_sys, self.color, self.hp, self.max_hp, self.is_dead = p_sys, (200,50,50), 100, 100, False
        self.move_timer, self.jump_timer, self.curr_move = 0, 0, 0
    def update_ai(self, rects):
        if self.is_dead: return
        self.move_timer -= 1
        if self.move_timer <= 0: self.move_timer, self.curr_move = random.randint(30,120), random.choice([-1,0,1])
        if self.curr_move: self.apply_force((Config.MOVE_ACCEL*self.curr_move, 0))
        self.jump_timer -= 1
        if self.jump_timer <= 0 and self.on_ground and random.random()<0.4: self.vel.y = -Config.JUMP_FORCE; self.jump_timer = random.randint(60,180)
        super().update_physics(); super().resolve_collisions(rects)
        if self.pos.y > 2000: self.take_damage(999)
    def take_damage(self, a):
        self.hp -= a
        if self.p_sys: self.p_sys.emit(self.pos.x, self.pos.y, 5, self.color, (2,6))
        if self.hp <= 0: self.is_dead = True; self.p_sys.emit(self.pos.x, self.pos.y, 30, self.color, (3,10))
    def draw(self, s, c):
        if self.is_dead: return
        dr = c.apply(self.rect)
        pygame.draw.rect(s, self.color, dr, border_radius=8)
        # HP Bar
        pygame.draw.rect(s, (50,0,0), (dr.centerx-20, dr.y-10, 40, 5))
        pygame.draw.rect(s, (0,255,0), (dr.centerx-20, dr.y-10, 40*max(0, self.hp/self.max_hp), 5))