class Camera:
    def __init__(self, width, height):
        self.camera = pygame.Rect(0, 0, width, height)
        self.width = width
        self.height = height
        
        # Novo: Variáveis de Shake
        self.shake_magnitude = 0
        self.shake_timer = 0

    def trigger_shake(self, magnitude, duration):
        """Chame isso quando houver um impacto forte."""
        self.shake_magnitude = magnitude
        self.shake_timer = duration

    def apply(self, entity):
        # Mantém a lógica anterior...
        if isinstance(entity, pygame.Rect):
            return entity.move(self.camera.topleft)
        elif isinstance(entity, pygame.math.Vector2):
            return entity + pygame.math.Vector2(self.camera.topleft)
        return entity.rect.move(self.camera.topleft)

    def update(self, target):
        # ... Lógica LERP anterior ...
        x = -target.pos.x + int(Config.SCREEN_WIDTH / 2)
        y = -target.pos.y + int(Config.SCREEN_HEIGHT / 2)
        
        current_x, current_y = self.camera.x, self.camera.y
        new_x = current_x + (x - current_x) * 0.05
        new_y = current_y + (y - current_y) * 0.05

        # ... Lógica Clamp anterior ...
        x = min(0, new_x)
        y = min(0, new_y)
        x = max(-(self.width - Config.SCREEN_WIDTH), x)
        y = max(-(self.height - Config.SCREEN_HEIGHT), y)

        # Novo: Aplica o Offset do Shake
        if self.shake_timer > 0:
            offset_x = random.randint(-self.shake_magnitude, self.shake_magnitude)
            offset_y = random.randint(-self.shake_magnitude, self.shake_magnitude)
            x += offset_x
            y += offset_y
            self.shake_timer -= 1

        self.camera = pygame.Rect(x, y, self.width, self.height)

    def input_update(self, actions, map_rects, projectiles_list): # <--- Novo argumento
    # ... Movimento e Hook anteriores ...

    # -- Sistema de Arma (Bazuca) --
    if self.weapon_cooldown > 0:
        self.weapon_cooldown -= 1

    # Botão Esquerdo (mouse_buttons[0]) dispara foguete
    # Nota: actions['fire'] no InputHandler original pegava botão direito OU esquerdo.
    # Idealmente, separe no InputHandler: 'fire' (esq) e 'hook' (dir).
    # Vamos assumir aqui que você separou ou criou uma action 'shoot'.
    
    # Supondo que actions['shoot'] seja o clique esquerdo:
    if actions.get('shoot') and self.weapon_cooldown == 0:
        self.weapon_cooldown = 40 # Demora ~0.6s entre tiros
        
        # Calcula ângulo do tiro
        mouse_pos = pygame.math.Vector2(actions['mouse_pos']) # Já corrigido pela câmera na classe Game
        player_center = self.pos + pygame.math.Vector2(self.size/2, self.size/2)
        
        diff = mouse_pos - player_center
        angle = math.atan2(diff.y, diff.x)
        
        # Cria o projétil (Velocidade 18)
        new_proj = Projectile(player_center.x, player_center.y, angle, 18, self)
        projectiles_list.append(new_proj)
        
        # Recuo (Kickback) da arma no jogador (opcional, mas bom pra game feel)
        self.vel -= diff.normalize() * 2