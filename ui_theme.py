import pygame
import math

# ──────────────── Color Palette (Light/White theme) ────────────────
BG          = (245, 246, 248)
PANEL       = (255, 255, 255)
BORDER      = (220, 223, 230)
TEXT_DARK   = (30,  35,  50)
TEXT_MID    = (100, 108, 130)
TEXT_LIGHT  = (160, 168, 185)
ACCENT      = (67, 133, 245)     # blue
OPERATOR    = (142, 68, 213)     # purple
OPERAND     = (39, 174, 96)      # green
ACTIVE_BG   = (232, 240, 255)
ACTIVE_BD   = (67, 133, 245)
SHADOW      = (210, 213, 220)

def rounded_rect(surface, color, rect, radius=10, border=0, border_color=None):
    pygame.draw.rect(surface, color, rect, border_radius=radius)
    if border and border_color:
        pygame.draw.rect(surface, border_color, rect, width=border, border_radius=radius)

def draw_shadow(surface, rect, radius=10, offset=3, alpha=40):
    shadow_surf = pygame.Surface((rect.width + offset*2, rect.height + offset*2), pygame.SRCALPHA)
    pygame.draw.rect(shadow_surf, (*SHADOW, alpha),
                     shadow_surf.get_rect(), border_radius=radius+2)
    surface.blit(shadow_surf, (rect.x - offset, rect.y - offset))

def token_color(tok, operators='*|+.^?'):
    return OPERATOR if tok in operators else OPERAND

def draw_token(surface, tok, rect, fonts, active=False, opacity=255, scale=1.0):
    w = int(rect.width * scale)
    h = int(rect.height * scale)
    cx = rect.centerx
    cy = rect.centery
    r = pygame.Rect(cx - w//2, cy - h//2, w, h)

    bg   = ACTIVE_BG  if active else PANEL
    bd   = ACTIVE_BD  if active else BORDER
    col  = OPERATOR if tok in '*|+.^?' else OPERAND

    rounded_rect(surface, bg, r, radius=6)
    rounded_rect(surface, r, r, radius=6, border=2, border_color=bd)

    txt_surf = fonts['mono'].render(tok, True, col)
    surface.blit(txt_surf, txt_surf.get_rect(center=r.center))
