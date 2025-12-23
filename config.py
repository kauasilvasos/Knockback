# config.py
class Config:
    SCREEN_WIDTH = 1280
    SCREEN_HEIGHT = 720
    FPS = 60
    TITLE = "Project Teeworlds: Slow Motion Edition"
    
    # Cores
    COLOR_BG = (253, 251, 247)
    COLOR_PLAYER = (49, 130, 206)
    COLOR_HOOK = (74, 85, 104)
    COLOR_GROUND = (45, 55, 72)
    
    # --- FÍSICA (ESCALA 0.15x) ---
    # Acelerações (Gravidade, Move) são multiplicadas por 0.15 * 0.15 = 0.0225
    GRAVITY = 0.01125       # Antes: 0.5
    MOVE_ACCEL = 0.027      # Antes: 1.2
    
    # Impulsos (Pulo) são multiplicados por 0.15
    JUMP_FORCE = 1.8        # Antes: 12.0
    
    # Atrito (Mantido próximo para preservar "deslize", levemente ajustado se sentir travado)
    GROUND_FRICTION = 0.96  # Aumentado (menos atrito) para compensar velocidades baixas
    AIR_RESISTANCE = 0.99   # Quase sem resistência no ar
    
    # --- HOOK & COMBATE ---
    HOOK_RANGE = 400        # Alcance mantém igual
    
    # Hook é uma força contínua (Aceleração), então * 0.0225
    HOOK_FORCE = 0.034      # Antes: 1.5
    HOOK_DRAG = 0.95        # Um pouco mais solto
    
    EXPLOSION_RADIUS = 120
    
    # Knockback é um impulso instantâneo, então * 0.15
    KNOCKBACK_FORCE = 2.25  # Antes: 15.0