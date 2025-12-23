# config.py
class Config:
    # Deixe 0, 0 para detectar automaticamente no modo Fullscreen
    SCREEN_WIDTH = 0 
    SCREEN_HEIGHT = 0
    FPS = 60
    TITLE = "Project Teeworlds: DDNet Style"
    
    # Cores
    COLOR_BG = (253, 251, 247)
    COLOR_PLAYER = (49, 130, 206)
    COLOR_HOOK = (74, 85, 104)
    COLOR_GROUND = (45, 55, 72)
    COLOR_CROSSHAIR = (150, 150, 150) # Nova cor para a mira
    
    # --- FÍSICA AJUSTADA (Mais pesado/rápido) ---
    # Aumentei a gravidade para cair mais rápido (DDNet feel)
    GRAVITY = 0.035       # Antes era ~0.011 no slow mo. Aumentei para pesar.
    
    MOVE_ACCEL = 0.05       # Aceleração de movimento um pouco mais ágil
    JUMP_FORCE = 1.8        # Força de pulo mantida (compensa com gravidade)
    
    # Atrito
    GROUND_FRICTION = 0.92  
    AIR_RESISTANCE = 0.99   
    
    # --- HOOK & COMBATE ---
    HOOK_RANGE = 300
    HOOK_FORCE = 0.05       # Reduzido para não sobrepor a inércia
    HOOK_DRAG = 0.99        # Maior retenção de velocidade para o pêndulo
    HOOK_FLY_SPEED = 6.5
    
    EXPLOSION_RADIUS = 100
    KNOCKBACK_FORCE = 2.25