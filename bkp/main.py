import pygame
from config import Config
from core import InputHandler, Camera
from map_system import InfiniteMap
from entities import Player, ParticleManager, Dummy

def main():
    pygame.init()
    screen = pygame.display.set_mode((Config.SCREEN_WIDTH, Config.SCREEN_HEIGHT))
    pygame.display.set_caption(Config.TITLE)
    clock = pygame.time.Clock()

    camera = Camera()
    input_handler = InputHandler()
    map_system = InfiniteMap()
    particles = ParticleManager()
    
    player = Player(100, Config.SCREEN_HEIGHT - 100, particles, camera)
    
    # Lista de projéteis (Grenades)
    projectiles = []
    player.set_projectiles_list(projectiles)
    
    dummies = [
        Dummy(400, Config.SCREEN_HEIGHT - 100),
        Dummy(600, Config.SCREEN_HEIGHT - 200)
    ]

    running = True
    while running:
        # 1. Eventos Globais
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_e:
                mouse_world = camera.to_world(pygame.mouse.get_pos())
                dummies.append(Dummy(mouse_world.x, mouse_world.y))

        # 2. Input
        actions = input_handler.process_events()

        # 3. Update Lógico
        map_system.update(player.pos.y)
        
        if player.pos.y > map_system.highest_point + 2000:
             player.pos.y = map_system.highest_point
             player.vel.y = 0

        # Atualiza Entidades
        all_entities = dummies + [player]
        
        player.update(actions, map_system.walls, all_entities)
        
        for dummy in dummies:
            dummy.update(map_system.walls)
        
        # Atualiza Projéteis
        for proj in projectiles[:]:
            proj.update(map_system.walls, all_entities)
            if not proj.active:
                projectiles.remove(proj)
            
        camera.update(player.pos)
        particles.update()

        # 4. Renderização
        screen.fill(Config.COLOR_BG)
        
        map_system.draw(screen, camera)
        
        for dummy in dummies:
            dummy.draw(screen, camera)
        
        for proj in projectiles:
            proj.draw(screen, camera)
            
        player.draw(screen, camera)
        particles.draw(screen, camera)
        
        # UI Simples
        font = pygame.font.SysFont("arial", 18)
        current_weapon_name = "HAMMER" if player.current_weapon == 1 else "GRENADE"
        text = font.render(f"H: {int(-player.pos.y)} | W: {current_weapon_name}", True, (255, 255, 255))
        screen.blit(text, (10, 10))
        text_help = font.render("1: Hammer | 2: Grenade | R-Click: Hook | L-Click: Fire", True, (150, 150, 150))
        screen.blit(text_help, (10, 30))

        pygame.display.flip()
        clock.tick(Config.FPS)

    pygame.quit()

if __name__ == "__main__":
    main()