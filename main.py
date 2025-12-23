import pygame
from config import Config
from core import InputHandler, Camera
from map_system import TileMap
from entities import Player, ParticleManager, Projectile, Bot

class Game:
    def __init__(self):
        pygame.init()
        # MODO TELA CHEIA E RESOLUÇÃO AUTOMÁTICA
        info = pygame.display.Info()
        Config.SCREEN_WIDTH = info.current_w
        Config.SCREEN_HEIGHT = info.current_h
        
        self.screen = pygame.display.set_mode((Config.SCREEN_WIDTH, Config.SCREEN_HEIGHT), pygame.FULLSCREEN)
        pygame.display.set_caption(Config.TITLE)
        
        # ESCONDE O MOUSE DO SISTEMA
        pygame.mouse.set_visible(False)
        
        self.clock = pygame.time.Clock()
        self.running = True
        
        self.input = InputHandler()
        self.particles = ParticleManager()
        
        # Level Design Básico
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
        self.player = Player(100, 300, self.particles, self.camera)
        self.projectiles = []
        
        self.bots = []
        self.bots.append(Bot(350, 500, self.particles))
        self.bots.append(Bot(650, 400, self.particles))
        self.bots.append(Bot(950, 200, self.particles))

    def draw_custom_cursor(self):
        """Desenha a mira estilo DDNet: um círculo ao redor do player."""
        # Pega a posição do player na tela (onde ele foi desenhado)
        player_screen_pos = self.camera.apply(self.player.pos)
        center = pygame.math.Vector2(player_screen_pos.x + self.player.size/2, 
                                     player_screen_pos.y + self.player.size/2)
        
        # A mira fica a uma distância fixa do player (ex: 60 pixels)
        crosshair_radius = 60
        crosshair_pos = center + self.player.aim_dir * crosshair_radius
        
        # Desenha a mira (Crosshair)
        pygame.draw.circle(self.screen, Config.COLOR_CROSSHAIR, (int(crosshair_pos.x), int(crosshair_pos.y)), 6, 2)
        pygame.draw.circle(self.screen, (255, 255, 255), (int(crosshair_pos.x), int(crosshair_pos.y)), 2)

    def run(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                # Tecla ESC para sair (importante em fullscreen)
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    self.running = False
            
            actions = self.input.process_events()
            
            # --- Correção de Mouse Avançada ---
            # O mouse real do sistema move a mira do player.
            # O player calcula a mira baseada no centro da tela vs mouse.
            # Precisamos converter isso para "mundo" para o InputHandler entender onde atirar.
            
            # No modo DDNet, o input mouse_pos é usado principalmente para calcular o vetor de mira.
            # Convertemos o clique para coordenadas de mundo para o Hook funcionar:
            screen_mouse = pygame.math.Vector2(actions['mouse_pos'])
            world_mouse_pos = screen_mouse - pygame.math.Vector2(self.camera.camera.topleft)
            actions['mouse_pos'] = (world_mouse_pos.x, world_mouse_pos.y)

            # Updates
            self.player.input_update(actions, self.map.walls, self.projectiles)
            
            for bot in self.bots:
                bot.update_ai(self.map.walls)
                if bot.is_dead: # Respawn simples de teste
                   import random
                   if random.randint(0, 100) == 0:
                       bot.is_dead = False; bot.hp = 100; bot.pos = pygame.math.Vector2(random.randint(200,800),100)
            
            self.projectiles = [p for p in self.projectiles if p.active]
            targets = [self.player] + [b for b in self.bots if not b.is_dead]
            for p in self.projectiles:
                p.update(self.map.walls, targets, self.particles, self.camera)

            self.particles.update()
            self.camera.update(self.player)

            # Renders
            self.screen.fill(Config.COLOR_BG)
            self.map.draw(self.screen, self.camera)
            for bot in self.bots: bot.draw(self.screen, self.camera)
            for p in self.projectiles:
                dp = self.camera.apply(p.pos)
                pygame.draw.circle(self.screen, (50,50,50), (int(dp.x), int(dp.y)), 6)
                pygame.draw.circle(self.screen, (255,100,100), (int(dp.x), int(dp.y)), 4)
            
            self.particles.draw(self.screen, self.camera)
            self.player.draw(self.screen)
            
            # Desenha a mira por último (interface)
            self.draw_custom_cursor()

            # Debug
            fps = int(self.clock.get_fps())
            # Opcional: desenhar FPS na tela
            # ...

            pygame.display.flip()
            self.clock.tick(Config.FPS)

        pygame.quit()

if __name__ == "__main__":
    game = Game()
    game.run()