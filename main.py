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
        
        # 1. Core
        self.input = InputHandler()
        self.particles = ParticleManager()
        
        # 2. Map
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
        
        # 3. Entities
        self.player = Player(100, 300, self.particles, self.camera)
        self.projectiles = []
        
        self.bots = []
        self.bots.append(Bot(350, 500, self.particles))
        self.bots.append(Bot(650, 400, self.particles))
        self.bots.append(Bot(950, 200, self.particles))

    def run(self):
        while self.running:
            # --- INPUT ---
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
            
            actions = self.input.process_events()
            
            # Ajuste Mouse
            world_mouse_x = actions['mouse_pos'][0] - self.camera.camera.x
            world_mouse_y = actions['mouse_pos'][1] - self.camera.camera.y
            actions['mouse_pos'] = (world_mouse_x, world_mouse_y)

            # --- UPDATE ---
            self.player.input_update(actions, self.map.walls, self.projectiles)
            
            # Bots
            for bot in self.bots:
                bot.update_ai(self.map.walls)
                if bot.is_dead: # Respawn simples
                    import random
                    if random.randint(0, 200) == 0:
                        bot.is_dead = False
                        bot.hp = 100
                        bot.pos = pygame.math.Vector2(random.randint(200, 800), 100)
                        bot.vel *= 0

            # Projéteis
            self.projectiles = [p for p in self.projectiles if p.active]
            for p in self.projectiles:
                targets = [self.player] + [b for b in self.bots if not b.is_dead]
                p.update(self.map.walls, targets, self.particles, self.camera)

            self.particles.update()
            self.camera.update(self.player)

            # --- RENDER ---
            self.screen.fill(Config.COLOR_BG)
            self.map.draw(self.screen, self.camera)
            
            for bot in self.bots: bot.draw(self.screen, self.camera)
            
            # Desenha projéteis
            for p in self.projectiles:
                draw_pos = self.camera.apply(p.pos)
                pygame.draw.circle(self.screen, (50, 50, 50), (int(draw_pos.x), int(draw_pos.y)), 6)
                pygame.draw.circle(self.screen, (255, 100, 100), (int(draw_pos.x), int(draw_pos.y)), 4)

            self.particles.draw(self.screen, self.camera)
            
            # Desenha Player (Já inclui o hook e squash & stretch)
            self.player.draw(self.screen)

            # Debug UI
            fps = int(self.clock.get_fps())
            pygame.display.set_caption(f"{Config.TITLE} | FPS: {fps}")

            pygame.display.flip()
            self.clock.tick(Config.FPS)

        pygame.quit()

if __name__ == "__main__":
    game = Game()
    game.run()