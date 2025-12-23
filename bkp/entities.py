import random

class Player(PhysicsEntity):
    def __init__(self, x, y, particle_system, camera_ref): # Recebe sistemas externos
        super().__init__(x, y, 30)
        self.particle_system = particle_system
        self.camera_ref = camera_ref # Para chamar o shake
        
        self.hook_active = False
        self.hook_pos = pygame.math.Vector2(0, 0)
        self.trail = []
        self.was_on_ground = False # Para detectar o momento do pouso

    def input_update(self, actions, map_rects):
        # 1. Movimentação Básica (Esquerda/Direita)
        # Se estiver no Hook, reduzimos o controle aéreo para dar prioridade à física
        accel_mod = 0.2 if self.hook_active else 1.0 
        
        if actions['left']:
            self.apply_force(pygame.math.Vector2(-Config.MOVE_ACCEL * accel_mod, 0))
        if actions['right']:
            self.apply_force(pygame.math.Vector2(Config.MOVE_ACCEL * accel_mod, 0))

        # 2. Pulo
        if actions['up'] and self.on_ground:
            self.vel.y = -Config.JUMP_FORCE
            self.on_ground = False
            # Game Feel: Partículas de poeira ao pular
            self.particle_system.emit(self.pos.x + 15, self.pos.y + 30, 5, (200, 200, 200), (1, 3))

        # 3. Hook Logic (Avançada)
        if actions['fire']:
            if not self.hook_active:
                target = pygame.math.Vector2(actions['mouse_pos'])
                direction = (target - self.pos)
                dist = direction.length()
                
                if dist <= Config.HOOK_RANGE:
                    for rect in map_rects:
                        if rect.collidepoint(target):
                            self.hook_active = True
                            self.hook_pos = target
                            # Game Feel: Partículas e Shake ao conectar
                            self.particle_system.emit(target.x, target.y, 10, Config.COLOR_HOOK, (2, 5))
                            self.camera_ref.trigger_shake(3, 5) # Magnitude 3, 5 frames
                            break
        else:
            self.hook_active = False

        # 4. Física do Hook (Estilo Teeworlds/Pêndulo)
        if self.hook_active:
            hook_vec = self.hook_pos - self.pos
            dist = hook_vec.length()
            hook_dir = hook_vec.normalize()
            
            # Hook Physics:
            # Em vez de puxar sempre, ele age como uma mola rígida.
            # Se o jogador tenta se afastar além do comprimento atual da corda, o hook puxa de volta forte.
            # Se o jogador está se movendo tangente (de lado), o hook mantém o embalo.
            
            rope_len = 0.0 # Em TW a corda tenta encolher para zero
            
            # Força Elástica (Lei de Hooke simplificada)
            # Quanto mais longe, mais forte puxa
            k = 0.05 # Constante elástica
            spring_force = (dist - rope_len) * k
            
            # Aplica força na direção do gancho
            self.apply_force(hook_dir * spring_force * Config.HOOK_FORCE)
            
            # Amortecimento (Damping) para não oscilar para sempre
            self.vel *= 0.96

        super().update_physics()
        super().resolve_collisions(map_rects)
        
        # Game Feel: Detecção de Pouso (Impacto no chão)
        if self.on_ground and not self.was_on_ground:
            impact_vel = abs(self.vel.y)
            if impact_vel > 2: # Só se cair com alguma velocidade
                self.particle_system.emit(self.pos.x + 15, self.pos.y + 30, 8, Config.COLOR_GROUND, (1, 4))
                if impact_vel > 10: # Queda muito alta
                    self.camera_ref.trigger_shake(5, 10)
        
        self.was_on_ground = self.on_ground

        # Trail logic
        if len(self.trail) > 5: self.trail.pop(0)
        self.trail.append((self.pos.x, self.pos.y))

        

class Particle:
    def __init__(self, x, y, color, velocity, life):
        self.pos = pygame.math.Vector2(x, y)
        self.vel = pygame.math.Vector2(velocity)
        self.color = color
        self.life = life # Duração em frames
        self.original_life = life

    def update(self):
        self.pos += self.vel
        self.life -= 1
        self.vel *= 0.95 # Desaceleração (atrito do ar nas partículas)

    def draw(self, surface, camera):
        if self.life > 0:
            # Alpha diminui conforme a vida acaba
            alpha = int((self.life / self.original_life) * 255)
            # Tamanho diminui
            size = int(4 * (self.life / self.original_life))
            
            # Criamos uma surface temporária para suportar transparência
            surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            pygame.draw.circle(surf, (*self.color, alpha), (size, size), size)
            
            # Aplica a câmera
            draw_pos = camera.apply(self.pos)
            surface.blit(surf, (draw_pos.x - size, draw_pos.y - size))

class ParticleManager:
    def __init__(self):
        self.particles = []

    def emit(self, x, y, count, color, speed_range):
        """Cria uma explosão de partículas."""
        for _ in range(count):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(speed_range[0], speed_range[1])
            vel_x = math.cos(angle) * speed
            vel_y = math.sin(angle) * speed
            life = random.randint(20, 40)
            self.particles.append(Particle(x, y, color, (vel_x, vel_y), life))

    def update(self):
        # Atualiza e remove partículas mortas
        self.particles = [p for p in self.particles if p.life > 0]
        for p in self.particles:
            p.update()

    def draw(self, surface, camera):
        for p in self.particles:
            p.draw(surface, camera)

            class Projectile(PhysicsEntity):
    def __init__(self, x, y, angle, force, owner):
        super().__init__(x, y, 14) # Tamanho 14px
        self.owner = owner # Quem atirou (para não se matar instantaneamente, opcional)
        
        # Define velocidade baseada no ângulo
        self.vel.x = math.cos(angle) * force
        self.vel.y = math.sin(angle) * force
        
        self.active = True
        self.explode_radius = 120 # Raio da explosão (AoE)
        self.knockback_force = 15.0 # Força do empurrão

    def update(self, map_rects, entities_to_affect, particle_system, camera):
        if not self.active: return

        # Física de arco (gravidade)
        self.acc.y += Config.GRAVITY * 0.5 # Projéteis caem um pouco mais devagar que players
        self.vel += self.acc
        self.pos += self.vel
        self.acc *= 0

        # Colisão com Mapa (Explode ao tocar)
        proj_rect = pygame.Rect(self.pos.x, self.pos.y, self.size, self.size)
        
        collision = False
        for rect in map_rects:
            if proj_rect.colliderect(rect):
                collision = True
                break
        
        # Verifica se saiu do mapa
        if self.pos.y > 2000 or self.pos.x < -1000 or self.pos.x > 3000:
            self.active = False # Remove sem explodir se cair no void

        if collision:
            self.explode(entities_to_affect, particle_system, camera)

    def explode(self, entities, particle_system, camera):
        self.active = False
        center = self.pos + pygame.math.Vector2(self.size/2, self.size/2)
        
        # 1. Game Feel: Efeitos Visuais
        camera.trigger_shake(6, 8) # Shake forte
        particle_system.emit(center.x, center.y, 20, (255, 100, 50), (2, 8)) # Fogo
        particle_system.emit(center.x, center.y, 10, (100, 100, 100), (1, 4)) # Fumaça

        # 2. Física: Cálculo de Knockback (A Mágica do Rocket Jump)
        for entity in entities:
            # Vetor da explosão até a entidade
            entity_center = entity.pos + pygame.math.Vector2(entity.size/2, entity.size/2)
            diff = entity_center - center
            dist = diff.length()

            # Se estiver dentro do raio da explosão
            if dist < self.explode_radius and dist > 0:
                # Normaliza o vetor (direção do empurrão)
                direction = diff.normalize()
                
                # Força é inversamente proporcional à distância (mais perto = mais forte)
                # Fórmula: (1 - dist/raio) * força_maxima
                factor = (1.0 - (dist / self.explode_radius))
                impulse = direction * (factor * self.knockback_force)
                
                # Aplica o impulso instantâneo na velocidade da entidade
                entity.vel += impulse
                
                # Tira o jogador do chão para ele voar
                entity.on_ground = False
                class Bot(PhysicsEntity):
    def __init__(self, x, y, particle_system):
        super().__init__(x, y, 30) # Mesmo tamanho do player
        self.particle_system = particle_system
        self.color = (200, 50, 50) # Vermelho (Inimigo)
        
        # Atributos de Vida
        self.hp = 100
        self.max_hp = 100
        self.is_dead = False
        
        # "Cérebro" da IA (Timer para ações)
        self.move_timer = 0
        self.jump_timer = 0
        self.current_move = 0 # -1 (Esq), 0 (Parado), 1 (Dir)

    def update_ai(self, map_rects, dt=1):
        """Simula inputs baseado em um comportamento aleatório simples."""
        if self.is_dead: return

        # 1. Decisão de Movimento Horizontal
        self.move_timer -= 1
        if self.move_timer <= 0:
            self.move_timer = random.randint(30, 120) # Muda de ideia a cada 0.5s ~ 2s
            self.current_move = random.choice([-1, 0, 1]) # Esq, Nada, Dir

        # Aplica força baseado na decisão
        if self.current_move == -1:
            self.apply_force(pygame.math.Vector2(-Config.MOVE_ACCEL, 0))
        elif self.current_move == 1:
            self.apply_force(pygame.math.Vector2(Config.MOVE_ACCEL, 0))

        # 2. Decisão de Pulo (Aleatório para ser difícil de acertar)
        self.jump_timer -= 1
        if self.jump_timer <= 0 and self.on_ground:
            if random.random() < 0.4: # 40% de chance de pular quando o timer zera
                self.vel.y = -Config.JUMP_FORCE
                # Efeito visual (Poeira)
                self.particle_system.emit(self.pos.x + 15, self.pos.y + 30, 5, (200, 200, 200), (1, 3))
            self.jump_timer = random.randint(60, 180)

        # 3. Física Padrão (Gravidade, Colisão)
        super().update_physics()
        super().resolve_collisions(map_rects)

        # 4. Checagem de Morte (Cair do mapa)
        if self.pos.y > 2000:
            self.take_damage(999)

    def take_damage(self, amount):
        """Recebe dano e gera feedback visual."""
        self.hp -= amount
        # Efeito visual de dano (Partículas de "sangue" ou faísca)
        self.particle_system.emit(self.pos.x + 15, self.pos.y + 15, 5, self.color, (2, 6))
        
        if self.hp <= 0 and not self.is_dead:
            self.die()

    def die(self):
        self.is_dead = True
        # Explosão visual de morte
        self.particle_system.emit(self.pos.x + 15, self.pos.y + 15, 30, self.color, (3, 10))

    def draw(self, surface, camera):
        if self.is_dead: return

        # Desenha o Bot
        rect = pygame.Rect(self.pos.x, self.pos.y, self.size, self.size)
        draw_rect = camera.apply(rect)
        pygame.draw.rect(surface, self.color, draw_rect, border_radius=8)

        # Barra de Vida (Health Bar)
        hp_pct = self.hp / self.max_hp
        bar_width = 40
        bar_pos = (draw_rect.centerx - bar_width // 2, draw_rect.y - 15)
        
        # Fundo da barra
        pygame.draw.rect(surface, (50, 0, 0), (*bar_pos, bar_width, 6))
        # Vida atual
        pygame.draw.rect(surface, (0, 255, 0), (*bar_pos, bar_width * hp_pct, 6))