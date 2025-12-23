# main.py
import pygame
from config import Config
from core import InputHandler, Camera
from map_system import TileMap
from entities import Player, ParticleManager, Projectile, Bot


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((Config.SCREEN_WIDTH, Config.SCREEN_HEIGHT))
        pygame.display.set_caption(Config.TITLE)
        self.clock = pygame.time.Clock()
        self.running = True
        
        self.bots = []
        self.bots.append(Bot(350, 500, self.particles))
        self.bots.append(Bot(650, 400, self.particles))
        self.bots.append(Bot(950, 200, self.particles))

        # 1. Inicializa Sistemas Core
        self.input = InputHandler()
        self.particles = ParticleManager()
        
        # 2. Inicializa Mundo (Level Design)
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
            "1111111111111111111111111111111111111111",
        ]
        self.map = TileMap(level_layout)    
        self.camera = Camera(self.map.width, self.map.height)
        
        # 3. Inicializa Entidades
        self.player = Player(100, 300, self.particles, self.camera)
        self.projectiles = []

    def run(self):
        while self.running:
            # --- INPUT ---
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
            
            actions = self.input.process_events()
            
            # Correção de Mouse (Screen -> World)
            mouse_vec = pygame.math.Vector2(actions['mouse_pos'])
            world_mouse = self.camera.apply(mouse_vec) # Usando método reverso se necessário, ou somando offset manual
            # Simplificação: Ajuste manual aqui se a classe Camera não tiver unproject
            world_mouse_x = actions['mouse_pos'][0] - self.camera.camera.x
            world_mouse_y = actions['mouse_pos'][1] - self.camera.camera.y
            actions['mouse_pos'] = (world_mouse_x, world_mouse_y)

            # --- UPDATE ---
            self.player.input_update(actions, self.map.walls, self.projectiles)
            
            # Atualiza Projéteis
            self.projectiles = [p for p in self.projectiles if p.active]
            for p in self.projectiles:
                # Lista de alvos afetados pela explosão (Player + futuros inimigos)
                targets = [self.player] 
                p.update(self.map.walls, targets, self.particles, self.camera)

            self.particles.update()
            self.camera.update(self.player)

            # --- RENDER ---
            self.screen.fill(Config.COLOR_BG)
            self.map.draw(self.screen, self.camera)
            
            for bot in self.bots:
                bot.draw(self.screen, self.camera)

            # Desenha Projéteis
            for p in self.projectiles:
                draw_pos = self.camera.apply(p.pos)
                pygame.draw.circle(self.screen, (50, 50, 50), (int(draw_pos.x), int(draw_pos.y)), 6)
                pygame.draw.circle(self.screen, (255, 100, 100), (int(draw_pos.x), int(draw_pos.y)), 4)

            self.particles.draw(self.screen, self.camera)
            self.player.draw(self.screen) # Método draw do player precisa aplicar a câmera internamente ou receber posição ajustada

            # UI Debug
            fps = int(self.clock.get_fps())
            pygame.display.set_caption(f"{Config.TITLE} | FPS: {fps} | Projectiles: {len(self.projectiles)}")

            pygame.display.flip()
            self.clock.tick(Config.FPS)

        pygame.quit()

if __name__ == "__main__":
    game = Game()
    game.run()