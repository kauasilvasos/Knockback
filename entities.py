import random

class Player(PhysicsEntity):
    import math
    import random
    import pygame
    from config import Config


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
            # Gravity
            self.acc.y += Config.GRAVITY
            # Integrate
            self.vel += self.acc
            # Apply air resistance
            if not self.on_ground:
                self.vel *= Config.AIR_RESISTANCE
            self.pos += self.vel
            # Reset acceleration
            self.acc *= 0

        def resolve_collisions(self, map_rects):
            # Simple AABB collision resolution
            self.on_ground = False
            r = self.rect
            for m in map_rects:
                if r.colliderect(m):
                    # Determine overlap
                    dx = min(r.right - m.left, m.right - r.left)
                    dy = min(r.bottom - m.top, m.bottom - r.top)
                    if dx < dy:
                        # horizontal push
                        if r.centerx < m.centerx:
                            self.pos.x -= dx
                        else:
                            self.pos.x += dx
                        self.vel.x = 0
                    else:
                        # vertical push
                        import math
                        import random
                        import pygame
                        from config import Config


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
                                # Gravity
                                self.acc.y += Config.GRAVITY
                                # Integrate
                                self.vel += self.acc
                                # Apply air resistance
                                if not self.on_ground:
                                    self.vel *= Config.AIR_RESISTANCE
                                self.pos += self.vel
                                # Reset acceleration
                                self.acc *= 0

                            def resolve_collisions(self, map_rects):
                                # Simple AABB collision resolution
                                self.on_ground = False
                                r = self.rect
                                for m in map_rects:
                                    if r.colliderect(m):
                                        # Determine overlap
                                        dx = min(r.right - m.left, m.right - r.left)
                                        dy = min(r.bottom - m.top, m.bottom - r.top)
                                        if dx < dy:
                                            # horizontal push
                                            if r.centerx < m.centerx:
                                                self.pos.x -= dx
                                            else:
                                                self.pos.x += dx
                                            self.vel.x = 0
                                        else:
                                            # vertical push
                                            if r.centery < m.centery:
                                                self.pos.y -= dy
                                                self.on_ground = True
                                            else:
                                                self.pos.y += dy
                                            self.vel.y = 0
                                        r = self.rect


                        class Player(PhysicsEntity):
                            def __init__(self, x, y, particle_system, camera_ref):
                                super().__init__(x, y, 30)
                                self.particle_system = particle_system
                                self.camera_ref = camera_ref
                                self.hook_active = False
                                self.hook_pos = pygame.math.Vector2(0, 0)
                                self.trail = []
                                self.was_on_ground = False
                                self.weapon_cooldown = 0

                            def input_update(self, actions, map_rects, projectiles_list=None):
                                accel_mod = 0.2 if self.hook_active else 1.0

                                if actions.get('left'):
                                    self.apply_force(pygame.math.Vector2(-Config.MOVE_ACCEL * accel_mod, 0))
                                if actions.get('right'):
                                    self.apply_force(pygame.math.Vector2(Config.MOVE_ACCEL * accel_mod, 0))

                                if actions.get('up') and self.on_ground:
                                    self.vel.y = -Config.JUMP_FORCE
                                    self.on_ground = False
                                    if self.particle_system:
                                        self.particle_system.emit(self.pos.x + 15, self.pos.y + 30, 5, (200, 200, 200), (1, 3))

                                # Hook
                                if actions.get('fire'):
                                    if not self.hook_active:
                                        target = pygame.math.Vector2(actions.get('mouse_pos', (0, 0)))
                                        direction = (target - self.pos)
                                        dist = direction.length()
                                        if dist <= Config.HOOK_RANGE:
                                            for rect in map_rects:
                                                if rect.collidepoint(target):
                                                    self.hook_active = True
                                                    self.hook_pos = target
                                                    if self.particle_system:
                                                        self.particle_system.emit(target.x, target.y, 10, Config.COLOR_HOOK, (2, 5))
                                                    if self.camera_ref:
                                                        self.camera_ref.trigger_shake(3, 5)
                                                    break
                                else:
                                    self.hook_active = False

                                # Hook physics
                                if self.hook_active:
                                    hook_vec = self.hook_pos - self.pos
                                    dist = hook_vec.length()
                                    if dist != 0:
                                        hook_dir = hook_vec.normalize()
                                        k = 0.05
                                        spring_force = (dist - 0.0) * k
                                        self.apply_force(hook_dir * spring_force * Config.HOOK_FORCE)
                                        self.vel *= 0.96

                                super().update_physics()
                                super().resolve_collisions(map_rects)

                                if self.on_ground and not self.was_on_ground:
                                    impact_vel = abs(self.vel.y)
                                    if impact_vel > 2 and self.particle_system:
                                        self.particle_system.emit(self.pos.x + 15, self.pos.y + 30, 8, Config.COLOR_GROUND, (1, 4))
                                        if impact_vel > 10 and self.camera_ref:
                                            self.camera_ref.trigger_shake(5, 10)

                                self.was_on_ground = self.on_ground
                                if len(self.trail) > 5:
                                    self.trail.pop(0)
                                self.trail.append((self.pos.x, self.pos.y))

                                # Shooting
                                if self.weapon_cooldown > 0:
                                    self.weapon_cooldown -= 1
                                if actions.get('shoot') and self.weapon_cooldown == 0 and projectiles_list is not None:
                                    self.weapon_cooldown = 40
                                    mouse_pos = pygame.math.Vector2(actions.get('mouse_pos', (0, 0)))
                                    player_center = self.pos + pygame.math.Vector2(self.size / 2, self.size / 2)
                                    diff = mouse_pos - player_center
                                    angle = math.atan2(diff.y, diff.x)
                                    new_proj = Projectile(player_center.x, player_center.y, angle, 18, self)
                                    projectiles_list.append(new_proj)
                                    if diff.length() != 0:
                                        self.vel -= diff.normalize() * 2

                            def draw(self, surface):
                                # uses camera_ref to draw adjusted
                                draw_pos = self.camera_ref.apply(pygame.Rect(self.pos.x, self.pos.y, self.size, self.size))
                                pygame.draw.rect(surface, Config.COLOR_PLAYER, draw_pos, border_radius=8)


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
                                if self.life <= 0:
                                    return
                                alpha = int((self.life / self.original_life) * 255)
                                size = max(1, int(4 * (self.life / self.original_life)))
                                surf = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
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
                                    vel_x = math.cos(angle) * speed
                                    vel_y = math.sin(angle) * speed
                                    life = random.randint(20, 40)
                                    self.particles.append(Particle(x, y, color, (vel_x, vel_y), life))

                            def update(self):
                                self.particles = [p for p in self.particles if p.life > 0]
                                for p in self.particles:
                                    p.update()

                            def draw(self, surface, camera):
                                for p in self.particles:
                                    p.draw(surface, camera)


                        class Projectile(PhysicsEntity):
                            def __init__(self, x, y, angle, force, owner):
                                super().__init__(x, y, 14)
                                self.owner = owner
                                self.vel.x = math.cos(angle) * force
                                self.vel.y = math.sin(angle) * force
                                self.active = True
                                self.explode_radius = Config.EXPLOSION_RADIUS
                                self.knockback_force = Config.KNOCKBACK_FORCE

                            def update(self, map_rects, entities_to_affect, particle_system, camera):
                                if not self.active:
                                    return
                                self.acc.y += Config.GRAVITY * 0.5
                                self.vel += self.acc
                                self.pos += self.vel
                                self.acc *= 0

                                proj_rect = pygame.Rect(self.pos.x, self.pos.y, self.size, self.size)
                                collision = False
                                for rect in map_rects:
                                    if proj_rect.colliderect(rect):
                                        collision = True
                                        break

                                if self.pos.y > 2000 or self.pos.x < -1000 or self.pos.x > 3000:
                                    self.active = False

                                if collision:
                                    self.explode(entities_to_affect, particle_system, camera)

                            def explode(self, entities, particle_system, camera):
                                if not self.active:
                                    return
                                self.active = False
                                center = self.pos + pygame.math.Vector2(self.size / 2, self.size / 2)
                                if camera:
                                    camera.trigger_shake(6, 8)
                                if particle_system:
                                    particle_system.emit(center.x, center.y, 20, (255, 100, 50), (2, 8))
                                    particle_system.emit(center.x, center.y, 10, (100, 100, 100), (1, 4))

                                for entity in entities:
                                    entity_center = entity.pos + pygame.math.Vector2(entity.size / 2, entity.size / 2)
                                    diff = entity_center - center
                                    dist = diff.length()
                                    if dist < self.explode_radius and dist > 0:
                                        direction = diff.normalize()
                                        factor = (1.0 - (dist / self.explode_radius))
                                        impulse = direction * (factor * self.knockback_force)
                                        entity.vel += impulse
                                        entity.on_ground = False


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

                            def update_ai(self, map_rects, dt=1):
                                if self.is_dead:
                                    return
                                self.move_timer -= 1
                                if self.move_timer <= 0:
                                    self.move_timer = random.randint(30, 120)
                                    self.current_move = random.choice([-1, 0, 1])

                                if self.current_move == -1:
                                    self.apply_force(pygame.math.Vector2(-Config.MOVE_ACCEL, 0))
                                elif self.current_move == 1:
                                    self.apply_force(pygame.math.Vector2(Config.MOVE_ACCEL, 0))

                                self.jump_timer -= 1
                                if self.jump_timer <= 0 and self.on_ground:
                                    if random.random() < 0.4:
                                        self.vel.y = -Config.JUMP_FORCE
                                        if self.particle_system:
                                            self.particle_system.emit(self.pos.x + 15, self.pos.y + 30, 5, (200, 200, 200), (1, 3))
                                    self.jump_timer = random.randint(60, 180)

                                super().update_physics()
                                super().resolve_collisions(map_rects)

                                if self.pos.y > 2000:
                                    self.take_damage(999)

                            def take_damage(self, amount):
                                self.hp -= amount
                                if self.particle_system:
                                    self.particle_system.emit(self.pos.x + 15, self.pos.y + 15, 5, self.color, (2, 6))
                                if self.hp <= 0 and not self.is_dead:
                                    self.die()

                            def die(self):
                                self.is_dead = True
                                if self.particle_system:
                                    self.particle_system.emit(self.pos.x + 15, self.pos.y + 15, 30, self.color, (3, 10))

                            def draw(self, surface, camera):
                                if self.is_dead:
                                    return
                                rect = pygame.Rect(self.pos.x, self.pos.y, self.size, self.size)
                                draw_rect = camera.apply(rect)
                                pygame.draw.rect(surface, self.color, draw_rect, border_radius=8)
                                hp_pct = self.hp / self.max_hp
                                bar_width = 40
                                bar_pos = (draw_rect.centerx - bar_width // 2, draw_rect.y - 15)
                                pygame.draw.rect(surface, (50, 0, 0), (*bar_pos, bar_width, 6))
                                pygame.draw.rect(surface, (0, 255, 0), (*bar_pos, bar_width * hp_pct, 6))