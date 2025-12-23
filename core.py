import pygame
import random
import math
from config import Config


class InputHandler:
    """Simplified input handler used by main.py.
    Returns a dict with boolean actions and mouse position.
    """
    def __init__(self):
        self.mouse_pos = (0, 0)

    def process_events(self):
        keys = pygame.key.get_pressed()
        mouse_buttons = pygame.mouse.get_pressed()
        self.mouse_pos = pygame.mouse.get_pos()

        return {
            'left': keys[pygame.K_a] or keys[pygame.K_LEFT],
            'right': keys[pygame.K_d] or keys[pygame.K_RIGHT],
            'up': keys[pygame.K_w] or keys[pygame.K_SPACE] or keys[pygame.K_UP],
            'fire': mouse_buttons[2],
            'shoot': mouse_buttons[0],
            'mouse_pos': self.mouse_pos,
        }


class Camera:
    def __init__(self, width, height):
        self.camera = pygame.Rect(0, 0, width, height)
        self.width = width
        self.height = height
        self.shake_magnitude = 0
        self.shake_timer = 0

    def trigger_shake(self, magnitude, duration):
        self.shake_magnitude = magnitude
        self.shake_timer = duration

    def apply(self, entity):
        # Accept Rect, Vector2 or tuple
        if isinstance(entity, pygame.Rect):
            return entity.move(self.camera.topleft)
        if isinstance(entity, pygame.math.Vector2):
            return entity + pygame.math.Vector2(self.camera.topleft)
        if isinstance(entity, tuple) and len(entity) == 2:
            return (entity[0] + self.camera.x, entity[1] + self.camera.y)
        # Fallback: try to use rect attribute
        try:
            return entity.rect.move(self.camera.topleft)
        except Exception:
            return entity

    def update(self, target):
        x = -target.pos.x + int(Config.SCREEN_WIDTH / 2)
        y = -target.pos.y + int(Config.SCREEN_HEIGHT / 2)

        current_x, current_y = self.camera.x, self.camera.y
        new_x = current_x + (x - current_x) * 0.05
        new_y = current_y + (y - current_y) * 0.05

        x = min(0, new_x)
        y = min(0, new_y)
        x = max(-(self.width - Config.SCREEN_WIDTH), x)
        y = max(-(self.height - Config.SCREEN_HEIGHT), y)

        if self.shake_timer > 0:
            offset_x = random.randint(-self.shake_magnitude, self.shake_magnitude)
            offset_y = random.randint(-self.shake_magnitude, self.shake_magnitude)
            x += offset_x
            y += offset_y
            self.shake_timer -= 1

        self.camera = pygame.Rect(int(x), int(y), self.width, self.height)