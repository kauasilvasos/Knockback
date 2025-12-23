class TileMap:
    def __init__(self, map_data):
        self.tile_size = 40 # Cada bloco tem 40x40px
        self.map_data = map_data
        self.width = len(map_data[0]) * self.tile_size
        self.height = len(map_data) * self.tile_size
        self.walls = [] # Lista de Rects para colisão
        
        self._generate_map()

    def _generate_map(self):
        """Transforma o array de texto em retângulos de colisão."""
        self.walls = []
        for row_idx, row in enumerate(self.map_data):
            for col_idx, tile in enumerate(row):
                if tile == '1': # '1' representa parede/chão
                    rect = pygame.Rect(
                        col_idx * self.tile_size, 
                        row_idx * self.tile_size, 
                        self.tile_size, 
                        self.tile_size
                    )
                    self.walls.append(rect)

    def draw(self, surface, camera):
        for wall in self.walls:
            # Só desenha o que a câmera vê (Culling básico para performance)
            adjusted_rect = camera.apply(wall)
            if -self.tile_size < adjusted_rect.x < Config.SCREEN_WIDTH and \
               -self.tile_size < adjusted_rect.y < Config.SCREEN_HEIGHT:
                pygame.draw.rect(surface, Config.COLOR_GROUND, adjusted_rect, border_radius=2)

# ==============================================================================
# JOGO ATUALIZADO (Integração)
# ==============================================================================
class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((Config.SCREEN_WIDTH, Config.SCREEN_HEIGHT))
        pygame.display.set_caption(Config.TITLE + " | Stage 2: Camera & Maps")
        self.clock = pygame.time.Clock()
        self.running = True
        
        self.input = InputHandler()
        
        # --- DEFINIÇÃO DO MAPA (Visualmente editável aqui) ---
        # 0 = Ar, 1 = Parede
        level_layout = [
            "1111111111111111111111111111111111111111",
            "1000000000000000000000000000000000000001",
            "1000000000000000000000000000000000000001",
            "1000000000001111000000000000000000000001",
            "1000000000000000000000001000000000000001",
            "1000001110000000000000001000000000000001",
            "1000000000000000000000111110000000000001",
            "1000000000000000000000000000000000000001",
            "1001000000000000000000000000000011100001",
            "1001000000000011100000000000000000000001",
            "1001111110000000000000000000000000000001",
            "1000000000000000000000000000110000000001",
            "1000000000000000000000000001110000000001",
            "1111111111111111111111111111111111111111",
        ]
        
        self.map = TileMap(level_layout)
        self.camera = Camera(self.map.width, self.map.height)
        self.player = Player(100, 300)

    def run(self):
        while self.running:
            # 1. Input
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
            
            actions = self.input.process_events()
            
            # --- Correção do Mouse para Coordenadas do Mundo ---
            # Como a câmera se move, o mouse na tela (0,0) não é o mouse no mundo (1000, 500)
            # Precisamos somar o offset da câmera (negativo) à posição do mouse
            screen_mouse = pygame.math.Vector2(actions['mouse_pos'])
            world_mouse_pos = screen_mouse - pygame.math.Vector2(self.camera.camera.topleft)
            
            # Hack temporário para passar a posição corrigida para o InputHandler
            # Em um sistema ECS real, isso seria feito de outra forma
            actions['mouse_pos'] = (world_mouse_pos.x, world_mouse_pos.y)

            # 2. Update
            self.player.input_update(actions, self.map.walls)
            self.camera.update(self.player)

            # 3. Render
            self.screen.fill(Config.COLOR_BG)

            # Desenha Mapa (Com Câmera)
            self.map.draw(self.screen, self.camera)

            # Desenha Player (Com Câmera)
            # Precisamos ajustar manualmente o desenho do Player para usar a Câmera
            # Pegamos o Rect ajustado
            player_draw_pos = self.camera.apply(self.player.pos)
            
            # Desenha Corda do Hook
            if self.player.hook_active:
                start_pos = player_draw_pos + pygame.math.Vector2(self.player.size/2, self.player.size/2)
                end_pos = self.camera.apply(self.player.hook_pos)
                pygame.draw.line(self.screen, Config.COLOR_HOOK, start_pos, end_pos, 4)
            
            # Desenha Rastro
            for i, pos in enumerate(self.player.trail):
                alpha = i * 40
                ghost_pos = self.camera.apply(pygame.math.Vector2(pos))
                ghost = pygame.Surface((self.player.size, self.player.size), pygame.SRCALPHA)
                pygame.draw.rect(ghost, (*Config.COLOR_PLAYER, alpha), (0,0, self.player.size, self.player.size), border_radius=4)
                self.screen.blit(ghost, ghost_pos)

            # Desenha Player Corpo
            pygame.draw.rect(self.screen, Config.COLOR_PLAYER, 
                             pygame.Rect(player_draw_pos.x, player_draw_pos.y, self.player.size, self.player.size), 
                             border_radius=8)

            # Debug UI (Fixo na tela, não usa câmera)
            fps_text = pygame.font.SysFont('Arial', 14).render(f"FPS: {int(self.clock.get_fps())}", True, (0,0,0))
            self.screen.blit(fps_text, (10, 10))

            pygame.display.flip()
            self.clock.tick(Config.FPS)

        pygame.quit()