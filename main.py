import pygame
from config import Config
from core import InputHandler, Camera
from map_system import InfiniteMap
from entities import Player, ParticleManager

class Game:
    def __init__(self):
        pygame.init()
        self.flags = pygame.DOUBLEBUF
        if Config.FULLSCREEN:
            self.flags |= pygame.FULLSCREEN
        
        self.screen = pygame.display.set_mode((Config.SCREEN_WIDTH, Config.SCREEN_HEIGHT), self.flags)
        pygame.display.set_caption(Config.TITLE)
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("arial", 24)
        self.state = Config.STATE_MENU
        self.running = True
        
        # Sistemas
        self.input_handler = InputHandler()
        self.camera = Camera()
        self.map_system = InfiniteMap()
        self.particles = ParticleManager()
        
        # Entidades
        self.projectiles = []
        spawn_y = self.map_system.base_y - 60
        self.player_blue = Player(0, spawn_y, self.particles, self.camera, char_type="BLUE")
        self.player_blue.set_projectiles_list(self.projectiles)
        self.player_red = None
        self.active_player = self.player_blue

    def toggle_fullscreen(self):
        Config.FULLSCREEN = not Config.FULLSCREEN
        self.flags = pygame.DOUBLEBUF
        if Config.FULLSCREEN:
            self.flags |= pygame.FULLSCREEN
        self.screen = pygame.display.set_mode((Config.SCREEN_WIDTH, Config.SCREEN_HEIGHT), self.flags)

    def draw_button(self, text, y_offset, active=False):
        color = (255, 255, 255) if active else (150, 150, 150)
        txt_surf = self.font.render(text, True, color)
        rect = txt_surf.get_rect(center=(Config.SCREEN_WIDTH//2, Config.SCREEN_HEIGHT//2 + y_offset))
        self.screen.blit(txt_surf, rect)
        return rect

    def run_menu(self):
        self.screen.fill(Config.COLOR_BG)
        title = pygame.font.SysFont("arial", 72, bold=True).render("DDNet Remake", True, Config.COLOR_PLAYER_BLUE)
        self.screen.blit(title, title.get_rect(center=(Config.SCREEN_WIDTH//2, 200)))
        
        mx, my = pygame.mouse.get_pos()
        click = pygame.mouse.get_pressed()[0]

        btn_play = self.draw_button("JOGAR", 50, active=True)
        btn_settings = self.draw_button("CONFIGURAÇÕES", 120)
        btn_exit = self.draw_button("SAIR", 190)

        if btn_play.collidepoint(mx, my) and click:
            self.state = Config.STATE_GAME
            pygame.time.delay(200) # Previne clique duplo
        if btn_settings.collidepoint(mx, my) and click:
            self.state = Config.STATE_SETTINGS
            pygame.time.delay(200)
        if btn_exit.collidepoint(mx, my) and click:
            self.running = False

    def run_settings(self):
        self.screen.fill(Config.COLOR_BG)
        label = self.font.render("CONFIGURAÇÕES", True, (255, 255, 255))
        self.screen.blit(label, (50, 50))

        mx, my = pygame.mouse.get_pos()
        click = pygame.mouse.get_pressed()[0]

        fs_text = f"TELA CHEIA: {'LIGADO' if Config.FULLSCREEN else 'DESLIGADO'}"
        btn_fs = self.draw_button(fs_text, 0)
        btn_back = self.draw_button("VOLTAR", 150)

        if btn_fs.collidepoint(mx, my) and click:
            self.toggle_fullscreen()
            pygame.time.delay(200)
        if btn_back.collidepoint(mx, my) and click:
            self.state = Config.STATE_MENU
            pygame.time.delay(200)

    def run_game(self):
        actions = self.input_handler.process_events()
        
        # Tecla ESC volta para o menu
        if pygame.key.get_pressed()[pygame.K_ESCAPE]:
            self.state = Config.STATE_MENU
            return

        # Lógica de Troca de Personagem (X)
        if actions['swap_char']:
            if self.player_red is None:
                spawn_pos = self.camera.to_world(actions['mouse_pos'])
                self.player_red = Player(spawn_pos.x, spawn_pos.y, self.particles, self.camera, char_type="DUMMY")
                self.player_red.set_projectiles_list(self.projectiles)
                self.active_player = self.player_red
                self.particles.emit((spawn_pos.x, spawn_pos.y), 20, Config.COLOR_PLAYER_RED, 5)
            else:
                self.active_player = self.player_red if self.active_player == self.player_blue else self.player_blue

        self.map_system.update(self.active_player.pos.y)
        players = [self.player_blue]
        if self.player_red: players.append(self.player_red)
        
        for p in players:
            p_actions = actions if p == self.active_player else {'left':False,'right':False,'jump':False,'hook':False,'shoot':False,'swap_char':False,'weapon1':False,'weapon2':False,'mouse_pos':(0,0)}
            p.update(p_actions, self.map_system.walls, players)
        
        for proj in self.projectiles[:]:
            proj.update(self.map_system.walls, players)
            if not proj.active: self.projectiles.remove(proj)
            
        self.camera.update(self.active_player.pos)
        self.particles.update()

        # Renderização
        self.screen.fill(Config.COLOR_BG)
        self.map_system.draw(self.screen, self.camera)
        for p in players: p.draw(self.screen, self.camera)
        for proj in self.projectiles: proj.draw(self.screen, self.camera)
        self.particles.draw(self.screen, self.camera)

    def main_loop(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT: self.running = False
            
            if self.state == Config.STATE_MENU:
                self.run_menu()
            elif self.state == Config.STATE_SETTINGS:
                self.run_settings()
            elif self.state == Config.STATE_GAME:
                self.run_game()
            
            pygame.display.flip()
            self.clock.tick(Config.FPS)
        pygame.quit()

if __name__ == "__main__":
    game = Game()
    game.main_loop()