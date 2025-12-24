import pygame
import random
from config import Config

class InfiniteMap:
    def __init__(self):
        self.tile_size = 40
        self.walls = [] 
        
        # Base do mapa (Chão)
        self.base_y = Config.SCREEN_HEIGHT - 40 
        self.highest_point = self.base_y
        
        # Parâmetros do Triângulo/Funil
        self.center_x = 0
        self.base_width_blocks = 14  # Largura inicial do chão (em blocos)
        
        self.generate_floor()
        
        # Gera os primeiros chunks para começar
        for _ in range(5):
            self.generate_chunk()

    def generate_floor(self):
        # Cria o chão base sólido no centro
        half_w = (self.base_width_blocks * self.tile_size) // 2
        
        # Gera chão de -half_w até +half_w
        start_x = self.center_x - half_w
        end_x = self.center_x + half_w
        
        for x in range(start_x, end_x + self.tile_size, self.tile_size):
            rect = pygame.Rect(x, self.base_y, self.tile_size, self.tile_size)
            self.walls.append(rect)

    def generate_chunk(self):
        # Gera paredes subindo e abrindo (Formato V)
        chunk_height = Config.CHUNK_HEIGHT
        start_y = self.highest_point
        end_y = start_y - chunk_height
        
        current_y = start_y
        
        while current_y > end_y:
            current_y -= self.tile_size
            
            # --- CÁLCULO DA LARGURA (Triangular) ---
            # Quanto mais alto (menor Y), mais largo fica
            height_climbed = self.base_y - current_y
            
            # A cada 80 pixels de altura (2 blocos), alarga 1 bloco para cada lado
            expansion = (height_climbed // 80) * self.tile_size
            
            current_half_width = ((self.base_width_blocks * self.tile_size) // 2) + expansion
            
            # Parede Esquerda
            left_x = self.center_x - current_half_width - self.tile_size
            self.walls.append(pygame.Rect(left_x, current_y, self.tile_size, self.tile_size))
            
            # Parede Direita
            right_x = self.center_x + current_half_width
            self.walls.append(pygame.Rect(right_x, current_y, self.tile_size, self.tile_size))
            
            # --- PLATAFORMAS INTERNAS ---
            # Gera plataformas apenas DENTRO do triângulo
            if random.random() < 0.25: # 25% de chance por linha
                # Define limites internos (com margem das paredes)
                inner_left = left_x + self.tile_size * 2
                inner_right = right_x - self.tile_size * 2
                
                if inner_right > inner_left:
                    # Tamanho da plataforma
                    plat_w = random.randint(3, 6) * self.tile_size
                    # Posição aleatória dentro do espaço disponível
                    plat_x = random.randint(inner_left, max(inner_left, inner_right - plat_w))
                    
                    # Evita criar plataformas coladas nas paredes
                    for i in range(0, plat_w, self.tile_size):
                        # Snap to grid
                        block_x = (plat_x + i) // self.tile_size * self.tile_size
                        if block_x + self.tile_size < right_x and block_x > left_x + self.tile_size:
                            self.walls.append(pygame.Rect(block_x, current_y, self.tile_size, self.tile_size))

        self.highest_point = end_y

    def update(self, player_y):
        # Gera mais mapa conforme sobe
        if player_y < self.highest_point + 1000:
            self.generate_chunk()
            # NOTA: Desativei o cleanup agressivo para permitir cair até o chão
            # Se quiser otimizar memória depois, podemos reativar com um threshold maior
            self.cleanup_old_chunks(player_y)

    def cleanup_old_chunks(self, player_y):
        # Só deleta se estiver MUITO longe (tipo 5000 pixels pra baixo)
        # Isso permite cair bastante sem o chão sumir
        threshold = player_y + 5000 
        # Mantém sempre o chão base (y >= base_y) para segurança
        self.walls = [w for w in self.walls if w.y < threshold or w.y >= self.base_y]

    def draw(self, surface, camera):
        view_rect = pygame.Rect(camera.offset.x, camera.offset.y, Config.SCREEN_WIDTH, Config.SCREEN_HEIGHT)
        view_rect.inflate_ip(200, 200) 
        
        for wall in self.walls:
            if view_rect.colliderect(wall):
                rect_screen = camera.apply_rect(wall)
                pygame.draw.rect(surface, Config.COLOR_GROUND, rect_screen)
                # Grama decorativa
                pygame.draw.rect(surface, Config.COLOR_GRASS, (rect_screen.x, rect_screen.y, rect_screen.width, 4))