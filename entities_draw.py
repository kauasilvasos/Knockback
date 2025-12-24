import pygame
import math
from config import Config

def draw_particles(surface, camera, particles):
    for p in particles:
        pos_screen = camera.apply_point((p[0], p[1]))
        size = max(1, int(4 * (p[4] / 30)))
        pygame.draw.rect(surface, p[5], (pos_screen[0], pos_screen[1], size, size))

def draw_projectile(surface, camera, projectile):
    draw_rect = camera.apply_rect(projectile.rect)
    pygame.draw.circle(surface, Config.COLOR_GRENADE, draw_rect.center, 6)

def draw_player(surface, camera, player):
    center = player.rect.center
    draw_center = camera.apply_point(center)

    # 1. Rastro do Laser
    if player.laser_trail:
        for i in range(len(player.laser_trail)):
            start, end = player.laser_trail[i]
            p1 = camera.apply_point((start.x, start.y))
            p2 = camera.apply_point((end.x, end.y))
            pygame.draw.line(surface, Config.COLOR_RIFLE_BEAM, p1, p2, 3)

    # 2. Hook com Espessura e Cor Dinâmica
    if player.hook_state != 0:
        hook_screen = camera.apply_point(player.hook_pos)
        tension = getattr(player, 'hook_tension', 0)
        color_val = int(150 + (105 * tension))
        thickness = int(3 + (4 * tension))
        pygame.draw.line(surface, (color_val, color_val, color_val), draw_center, hook_screen, thickness)
        pygame.draw.circle(surface, (50, 50, 50), hook_screen, 5)

    # 3. Corpo com Inclinação (Inércia Rotacional)
    tilt_angle = -player.vel.x * 1.5 
    w = max(1, int(player.rect.width * player.scale_x))
    h = max(1, int(player.rect.height * player.scale_y))
    body_surf = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.rect(body_surf, player.color, (0, 0, w, h), border_radius=5)
    rotated_body = pygame.transform.rotate(body_surf, tilt_angle)
    body_rect = rotated_body.get_rect(center=draw_center)
    surface.blit(rotated_body, body_rect)
    
    # 4. Arma e Olhos
    mouse_pos = pygame.mouse.get_pos()
    mouse_dir = (pygame.math.Vector2(mouse_pos) - pygame.math.Vector2(draw_center))
    if mouse_dir.length() > 0: mouse_dir = mouse_dir.normalize()
    angle = math.degrees(math.atan2(mouse_dir.y, mouse_dir.x))
    
    if player.current_weapon == 1:
        _draw_melee(surface, draw_center, angle, player.facing_right, player.shoot_cooldown, (player.char_type == "DUMMY"))
    else:
        weapon_color = Config.COLOR_RIFLE_BEAM if player.char_type == "DUMMY" else Config.COLOR_GRENADE
        weapon_end = (draw_center[0] + mouse_dir.x * 25, draw_center[1] + mouse_dir.y * 25)
        pygame.draw.line(surface, weapon_color, draw_center, weapon_end, 6)

    _draw_eyes(surface, draw_center, mouse_dir, player.facing_right, player.scale_x, player.scale_y)

def _draw_eyes(surface, center, mouse_dir, facing_right, scale_x, scale_y):
    eye_offset_x = 8 * scale_x * (1 if facing_right else -1)
    eye_l = (center[0] - 6 + (2 if facing_right else -2), center[1] - 5 * scale_y)
    eye_r = (center[0] + 6 + (2 if facing_right else -2), center[1] - 5 * scale_y)
    pygame.draw.circle(surface, (255, 255, 255), eye_l, 6)
    pygame.draw.circle(surface, (255, 255, 255), eye_r, 6)
    pupil_offset = mouse_dir * 2
    pygame.draw.circle(surface, (0, 0, 0), (eye_l[0] + pupil_offset.x, eye_l[1] + pupil_offset.y), 3)
    pygame.draw.circle(surface, (0, 0, 0), (eye_r[0] + pupil_offset.x, eye_r[1] + pupil_offset.y), 3)

def _draw_melee(surface, center, angle, facing_right, cooldown, is_bat):
    swing = -60 if facing_right else 60 if cooldown > Config.HAMMER_COOLDOWN * 0.5 else 0
    w_surf = pygame.Surface((50, 40), pygame.SRCALPHA)
    if is_bat: pygame.draw.polygon(w_surf, Config.COLOR_BAT, [(0, 18), (45, 12), (45, 24), (0, 22)])
    else: 
        pygame.draw.rect(w_surf, Config.COLOR_HAMMER_HANDLE, (0, 15, 30, 6))
        pygame.draw.rect(w_surf, Config.COLOR_HAMMER_HEAD, (20, 8, 12, 20))
    rotated = pygame.transform.rotate(w_surf, -angle + swing)
    rect = rotated.get_rect(center=center)
    offset = pygame.math.Vector2(20, 0).rotate(angle)
    surface.blit(rotated, (rect.x + offset.x, rect.y + offset.y))