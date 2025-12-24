import pygame

class Config:
    SCREEN_WIDTH = 1280
    SCREEN_HEIGHT = 720
    FPS = 60
    TITLE = "Project Teeworlds: Infinite Climb"
    
    # Cores
    COLOR_BG = (23, 26, 33)        
    COLOR_PLAYER = (100, 200, 255) 
    COLOR_DUMMY = (255, 100, 100)  
    COLOR_HOOK = (150, 150, 150)   
    COLOR_GROUND = (45, 55, 70)    
    COLOR_GRASS = (60, 180, 100)
    
    # Cores Armas/Projéteis
    COLOR_GRENADE = (255, 160, 50)
    COLOR_EXPLOSION = (255, 200, 100)
    COLOR_HAMMER = (139, 69, 19)   # Cor do cabo do martelo
    COLOR_HAMMER_HEAD = (100, 100, 110) # Cor da cabeça do martelo
    
    # Física Global
    GRAVITY = 0.5
    TERMINAL_VELOCITY = 20.0
    FRICTION_GROUND = 0.85
    FRICTION_AIR = 0.96
    
    # Player Movimento
    MOVE_ACCEL = 1.5
    JUMP_FORCE = 12.0
    MAX_JUMPS = 2              # NOVO: Pulo duplo (1 chão + 1 ar)
    
    # Hook
    HOOK_RANGE = 450
    HOOK_SPEED = 35.0
    HOOK_PULL_FORCE = 1.2      
    HOOK_DRAG_FORCE = 0.5      
    HOOK_ELASTICITY = 0.1      
    
    # Armas
    HAMMER_RANGE = 70          
    HAMMER_FORCE = 16.0        
    HAMMER_COOLDOWN = 20       
    
    GRENADE_SPEED = 18.0
    GRENADE_LIFETIME = 120     
    GRENADE_BLAST_RADIUS = 120 
    GRENADE_BLAST_FORCE = 10.0 
    GRENADE_COOLDOWN = 40
    
    # Geração de Mapa
    CHUNK_HEIGHT = 600         
    PLATFORM_MIN_WIDTH = 3
    PLATFORM_MAX_WIDTH = 8
    Y_START_GEN = 500