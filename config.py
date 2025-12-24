import pygame

class Config:
    SCREEN_WIDTH = 1280
    SCREEN_HEIGHT = 720
    FPS = 60
    TITLE = "Project Teeworlds: Tag Team & Ricochet"
    
    # Cores
    COLOR_BG = (23, 26, 33)        
    COLOR_PLAYER_BLUE = (100, 200, 255) 
    COLOR_PLAYER_RED = (255, 100, 100)  # Cor do Dummy jogável
    COLOR_HOOK = (150, 150, 150)   
    COLOR_GROUND = (45, 55, 70)    
    COLOR_GRASS = (60, 180, 100)
    
    # Cores Armas
    COLOR_GRENADE = (255, 160, 50)
    COLOR_EXPLOSION = (255, 200, 100)
    COLOR_HAMMER_HANDLE = (139, 69, 19)
    COLOR_HAMMER_HEAD = (100, 100, 110)
    
    # Novas Cores
    COLOR_BAT = (210, 180, 140)    # Madeira clara
    COLOR_RIFLE_BEAM = (180, 50, 255) # Laser Roxo
    
    # Física
    GRAVITY = 0.5
    TERMINAL_VELOCITY = 20.0
    FRICTION_GROUND = 0.85
    FRICTION_AIR = 0.96
    
    # Movimento
    MOVE_ACCEL = 1.5
    JUMP_FORCE = 12.0
    MAX_JUMPS = 2
    
    # Hook
    HOOK_RANGE = 450
    HOOK_SPEED = 35.0
    HOOK_PULL_FORCE = 1.2      
    HOOK_DRAG_FORCE = 0.5      
    HOOK_SPRING_K = 0.04       # Força de mola suave
    HOOK_DAMPING = 0.90        # Amortecimento alto para estabilidade
    HOOK_YANK_FORCE = 7.0      # Tranco inicial moderado
    HOOK_PULL_FORCE = 0.7
    
    # --- ARMAS ---
    
    # Arma 1: Melee (Comum)
    HAMMER_RANGE = 70          
    HAMMER_FORCE = 16.0        
    HAMMER_COOLDOWN = 20       
    
    # Arma 2: Blue (Granada)
    GRENADE_SPEED = 18.0
    GRENADE_LIFETIME = 120     
    GRENADE_BLAST_RADIUS = 120 
    GRENADE_BLAST_FORCE = 10.0 
    GRENADE_COOLDOWN = 40
    
    # Arma 2: Red (Rifle Laser)
    RIFLE_COOLDOWN = 45
    RIFLE_MAX_BOUNCES = 3      # Quantas vezes rebate na parede
    RIFLE_FORCE = 15.0         # Força de empurrão/puxão
    RIFLE_RANGE = 800
    
    # Mapa
    CHUNK_HEIGHT = 600         
    PLATFORM_MIN_WIDTH = 3
    PLATFORM_MAX_WIDTH = 8

    STATE_MENU = 0
    STATE_GAME = 1
    STATE_SETTINGS = 2
    
    # Configurações iniciais
    FULLSCREEN = False