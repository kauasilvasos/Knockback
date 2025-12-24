import pygame
from config import Config
from core import InputHandler, Camera
from map_system import TileMap
from entities import Player, ParticleManager, Bot

def main():
    pygame.init()
    screen = pygame.display.set_mode((Config.SCREEN_WIDTH, Config.SCREEN_HEIGHT))
    pygame.display.set_caption("Teeworlds Clone Rebased")
    clock = pygame.time.Clock()

    # Layout do mapa
    level = [
        "11111111111111111111111111111111",
        "10000000000000000000000000000001",
        "10000000000000000000000000000001",
        "10000011110000000000000000000001",
        "10000000000000000111000000000001",
        "10000000000000000000000000000001",
        "10000111000000000000000010000001",
        "10000000000011111000000010000001",
        "10000000000000000000000011100001",
        "11111111111111111111111111111111"
    ]

    # Setup
    camera = Camera(Config.SCREEN_WIDTH, Config.SCREEN_HEIGHT)
    input_handler = InputHandler()
    tile_map = TileMap(level)
    particles = ParticleManager()
    
    player = Player(100, 300, particles, camera)
    
    bots = [Bot(400, 300), Bot(600, 300), Bot(800, 300)]
    projectiles = []

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: running = False

        # 1. Input
        actions = input_handler.process_events()

        # 2. Update
        # Passamos projectiles e bots para o player interagir
        player.update(actions, tile_map.walls, projectiles)
        
        for p in projectiles:
            p.update(tile_map.walls, bots + [player])
        projectiles = [p for p in projectiles if p.active]
        
        for bot in bots:
            bot.update_ai(tile_map.walls)
        
        particles.update()
        camera.update(player)

        # 3. Draw
        screen.fill(Config.COLOR_BG)
        tile_map.draw(screen, camera)
        for bot in bots: bot.draw(screen, camera)
        player.draw(screen, camera)
        for p in projectiles: p.draw(screen, camera)
        particles.draw(screen, camera)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()