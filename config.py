import pygame

class Config:
    SCREEN_WIDTH = 1280
    SCREEN_HEIGHT = 720
    FPS = 60
    TITLE = "Project Teeworlds: Rebase"
    
    # Cores
    COLOR_BG = (240, 242, 245)
    COLOR_PLAYER = (59, 130, 246)
    COLOR_HOOK = (75, 85, 99)
    COLOR_GROUND = (31, 41, 55)
    
    # Física
    GRAVITY = 0.5
    TERMINAL_VELOCITY = 15.0
    
    # Movimento
    MOVE_ACCEL = 0.8
    MOVE_FRICTION = 0.85
    AIR_FRICTION = 0.98
    JUMP_FORCE = 11.0
    DOUBLE_JUMP_FORCE = 10.0
    
    # Hook
    HOOK_RANGE = 400
    HOOK_SPEED = 25.0
    HOOK_PULL_FORCE = 0.08
    HOOK_SWING_FORCE = 0.5
    HOOK_DRAG = 0.995
    
    # Granada
    GRENADE_SPEED = 18.0
    GRENADE_BOUNCINESS = 0.6
    EXPLOSION_RADIUS = 120
    EXPLOSION_FORCE = 12.0