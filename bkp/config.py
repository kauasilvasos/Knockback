# config.py
class Config:
    SCREEN_WIDTH = 1280
    SCREEN_HEIGHT = 720
    FPS = 60
    TITLE = "Project Teeworlds: Arena Prototype"
    
    # Cores
    COLOR_BG = (253, 251, 247)
    COLOR_PLAYER = (49, 130, 206)
    COLOR_HOOK = (74, 85, 104)
    COLOR_GROUND = (45, 55, 72)
    
    # Física
    GRAVITY = 0.5
    GROUND_FRICTION = 0.85
    AIR_RESISTANCE = 0.98
    MOVE_ACCEL = 1.2
    JUMP_FORCE = 12.0
    
    # Hook & Combate
    HOOK_RANGE = 400
    HOOK_FORCE = 1.5
    HOOK_DRAG = 0.92
    EXPLOSION_RADIUS = 120
    KNOCKBACK_FORCE = 15.0