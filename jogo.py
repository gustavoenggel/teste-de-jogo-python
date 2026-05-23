"""
AIR ASSAULT - TACTICAL (Horda Massiva e Correção de Waves)
Sem Áudio.
Execute: python jogo.py
"""
import pygame
import random
import math
import sys

pygame.init()

W, H = 960, 560
GROUND_Y = H - 80
FPS = 60

display_surf = pygame.Surface((W, H))
screen = pygame.display.set_mode((W, H))
pygame.display.set_caption("AIR ASSAULT - WARZONE")
pygame.mouse.set_visible(False)
clock = pygame.time.Clock()

# ─── CORES E TEMAS ────────────────────────────────────────────────────────────
WHITE = (255, 255, 255); BLACK = (0, 0, 0)
GREEN = (50, 220, 50); RED = (220, 50, 50)
ORANGE = (255, 140, 0); YELLOW = (255, 255, 80)
CYAN = (50, 200, 255); BLUE = (30, 100, 200); PURPLE = (180, 50, 255)
SILVER = (192, 192, 192)
GRAY = (100, 100, 100)
SKY1 = (6, 12, 28)

THEMES = {
    'forest': {'sky_top': (4, 8, 20), 'sky_bot': (20, 45, 80), 'ground': (20, 45, 20), 'lines': (15, 35, 15), 'border': (50, 100, 40), 'mountains': (15, 25, 40)},
    'desert': {'sky_top': (60, 20, 0), 'sky_bot': (200, 100, 40), 'ground': (194, 150, 80), 'lines': (160, 110, 50), 'border': (220, 180, 100), 'mountains': (120, 60, 30)},
    'snow': {'sky_top': (5, 10, 15), 'sky_bot': (40, 50, 70), 'ground': (220, 230, 240), 'lines': (180, 190, 200), 'border': (255, 255, 255), 'mountains': (120, 130, 140)}
}

font_lg = pygame.font.SysFont("Courier New", 48, bold=True)
font_md = pygame.font.SysFont("Courier New", 22, bold=True)
font_sm = pygame.font.SysFont("Courier New", 14, bold=True)

# ─── ATRIBUTOS DAS ARMAS ──────────────────────────────────────────────────────
WEAPON_STATS = {
    'mg':      {'name': '1:METRALHADORA', 'cooldown': 7,  'heat': 12, 'speed': 18, 'dmg': 20, 'color': CYAN, 'pierce': False, 'size': 3},
    'shotgun': {'name': '2:ESCOPETA',     'cooldown': 35, 'heat': 35, 'speed': 15, 'dmg': 18, 'color': YELLOW, 'pierce': False, 'size': 4},
    'plasma':  {'name': '3:PLASMA',       'cooldown': 4,  'heat': 8,  'speed': 25, 'dmg': 10, 'color': PURPLE, 'pierce': True, 'size': 3}
}

# ─── PARTÍCULAS E EXPLOSÕES ───────────────────────────────────────────────────
class Particle:
    def __init__(self, x, y, kind='fire', big=False):
        self.x, self.y, self.kind = x, y, kind
        ang = random.uniform(0, math.pi * 2)
        if kind == 'fire':
            spd = random.uniform(2, 8) if big else random.uniform(1, 4)
            self.vx, self.vy = math.cos(ang) * spd, math.sin(ang) * spd - (3 if big else 1)
            self.color = random.choice([(255,255,200), (255,200,50), (255,100,0), (200,30,0)])
            self.size, self.life, self.decay = random.uniform(5, 12) if big else random.uniform(2, 6), 1.0, random.uniform(0.015, 0.03)
        elif kind == 'smoke':
            self.x += random.uniform(-10, 10)
            spd = random.uniform(0.5, 2.0)
            self.vx, self.vy = math.cos(ang) * spd - 1.0, math.sin(ang) * spd - 1.5
            self.color = (random.randint(40, 80),)*3
            self.size, self.life, self.decay = random.uniform(8, 20) if big else random.uniform(5, 12), 1.0, random.uniform(0.01, 0.02)
        elif kind == 'debris':
            spd = random.uniform(4, 12)
            self.vx, self.vy = math.cos(ang) * spd, math.sin(ang) * spd - 4
            self.color = random.choice([(80,80,80), (50,50,50), (120,60,30)])
            self.size, self.life, self.decay = random.uniform(2, 5), 1.0, random.uniform(0.01, 0.02)
        else: # spark
            spd = random.uniform(3, 7)
            self.vx, self.vy = math.cos(ang) * spd, math.sin(ang) * spd
            self.color = CYAN if big else (255, 255, 150)
            self.size, self.life, self.decay = random.uniform(1, 3), 1.0, random.uniform(0.05, 0.1)

    def update(self):
        self.x += self.vx; self.y += self.vy
        if self.kind == 'debris':
            self.vy += 0.4
            if self.y >= GROUND_Y: self.y, self.vy, self.vx = GROUND_Y, -self.vy * 0.4, self.vx * 0.6
        elif self.kind == 'fire': self.vy -= 0.1; self.size *= 0.94
        elif self.kind == 'smoke': self.size += 0.2; self.vy -= 0.05
        self.vx *= 0.95; self.vy *= 0.95; self.life -= self.decay

    def draw(self, surf):
        if self.life <= 0 or self.size < 0.5: return
        s = max(1, int(self.size))
        if self.kind in ['smoke', 'fire']:
            tmp = pygame.Surface((s*2, s*2), pygame.SRCALPHA)
            pygame.draw.circle(tmp, (*self.color, int(self.life * 255) if self.kind == 'smoke' else 255), (s, s), s)
            surf.blit(tmp, (int(self.x) - s, int(self.y) - s), special_flags=pygame.BLEND_ALPHA_SDL2)
        else:
            pygame.draw.circle(surf, self.color, (int(self.x), int(self.y)), s)

def explode(particles, x, y, big=True):
    for _ in range(30 if big else 10): particles.append(Particle(x, y, 'fire', big))
    for _ in range(15 if big else 5):  particles.append(Particle(x, y, 'smoke', big))
    for _ in range(10 if big else 3):  particles.append(Particle(x, y, 'debris', big))

# ─── FUNDO (MAPAS) ────────────────────────────────────────────────────────────
class Background:
    def __init__(self):
        self.stars_snow = [{'x': random.randint(0, W), 'y': random.randint(0, H), 's': random.uniform(0.1, 0.5)} for _ in range(100)]
        self.mountains = [{'x': i*90+random.randint(0,50), 'h': 50+random.randint(0,180), 'w': 70+random.randint(0,120), 'layer': random.randint(0,2)} for i in range(40)]

    def draw(self, surf, scroll_x, theme_name):
        th = THEMES[theme_name]
        for y in range(GROUND_Y):
            t = y / GROUND_Y
            c = (th['sky_top'][0] + (th['sky_bot'][0]-th['sky_top'][0])*t,
                 th['sky_top'][1] + (th['sky_bot'][1]-th['sky_top'][1])*t,
                 th['sky_top'][2] + (th['sky_bot'][2]-th['sky_top'][2])*t)
            pygame.draw.line(surf, c, (0, y), (W, y))
            
        for s in self.stars_snow:
            sx = (s['x'] - scroll_x * s['s'] * (0.2 if theme_name != 'snow' else 1.0)) % W
            sy = s['y']
            if theme_name == 'snow': s['y'] = (s['y'] + s['s'] * 2) % H
            pygame.draw.circle(surf, (200, 200, 255) if theme_name!='snow' else WHITE, (int(sx), int(sy)), 1 if s['s'] < 0.3 else 2)

        for layer in range(3):
            pf = 0.1 + layer * 0.15
            for m in self.mountains:
                if m['layer'] != layer: continue
                mx = int((m['x'] - scroll_x * pf) % (W+400) - 150)
                pts = [(mx, GROUND_Y), (mx, int(GROUND_Y - m['h']*0.5)), (int(mx + m['w']//2), int(GROUND_Y - m['h'])), (int(mx + m['w']), int(GROUND_Y - m['h']*0.5)), (int(mx + m['w']), GROUND_Y)]
                pygame.draw.polygon(surf, th['mountains'], pts)
                
        pygame.draw.rect(surf, th['ground'], (0, GROUND_Y, W, H - GROUND_Y))
        for x in range(-(int(scroll_x * 0.9) % 40), W, 40):
            pygame.draw.line(surf, th['lines'], (x, GROUND_Y), (x - 20, H), 2)
        pygame.draw.line(surf, th['border'], (0, GROUND_Y), (W, GROUND_Y), 3)

# ─── JOGADOR, INVENTÁRIO E REGEN ──────────────────────────────────────────────
class Player:
    def __init__(self):
        self.x, self.y = 160.0, float(H//2)
        self.vx, self.vy = 0.0, 0.0
        self.w, self.h, self.spd = 76, 28, 6.0
        
        self.hp = self.max_hp = 100.0
        self.level, self.xp, self.next_xp = 1, 0, 50
        
        self.weapons = ['mg'] 
        self.cur_wep = 'mg'   
        self.scooldown = 0
        self.rockets, self.rcooldown = 5, 0
        self.aim_angle = 0
        self.heat, self.max_heat = 0.0, 100.0
        self.overheated = False
        
        self.inv, self.dash_cd, self.is_dashing = 0, 0, False
        self.shield = False
        self.time_since_hit = 0
        self.regen_delay = 180
        self.regen_rate = 0.15

    def take_damage(self, amount, screen_shake):
        if self.shield:
            self.shield = False; self.inv = 60
        else:
            self.hp -= amount; self.inv = 30; self.time_since_hit = 0
            return max(screen_shake, 8)
        return screen_shake

    def update(self, keys, mx, my, particles):
        self.aim_angle = math.atan2(my - self.y, mx - self.x)
        ax, ay = 0, 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]: ax = -1
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]: ax = 1
        if keys[pygame.K_UP] or keys[pygame.K_w]: ay = -1
        if keys[pygame.K_DOWN] or keys[pygame.K_s]: ay = 1
        
        if keys[pygame.K_LSHIFT] and self.dash_cd == 0:
            self.vx, self.dash_cd, self.is_dashing = 25.0 if ax >= 0 else -25.0, 90, True
            for _ in range(10): particles.append(Particle(self.x, self.y, 'smoke'))

        if self.is_dashing:
            self.vx *= 0.85
            if abs(self.vx) < self.spd + 1: self.is_dashing = False
        else:
            self.vx, self.vy = (self.vx + ax*0.8) * 0.85, (self.vy + ay*0.8) * 0.85
            self.vx, self.vy = max(-self.spd, min(self.spd, self.vx)), max(-self.spd, min(self.spd, self.vy))
            
        self.x, self.y = max(self.w//2, min(W-self.w//2, self.x + self.vx)), max(self.h//2+50, min(GROUND_Y-self.h//2-4, self.y + self.vy))
        
        self.time_since_hit += 1
        if self.time_since_hit > self.regen_delay and self.hp < self.max_hp:
            self.hp = min(self.max_hp, self.hp + self.regen_rate)
            if random.random() < 0.1:
                particles.append(Particle(self.x + random.randint(-20,20), self.y + random.randint(-10,10), 'spark', big=False))
                particles[-1].color = GREEN

        if not self.overheated:
            self.heat = max(0, self.heat - 1.5)
            if self.heat >= self.max_heat: self.overheated = True
        else:
            self.heat -= 0.5
            if self.heat <= 0: self.overheated = False

        self.scooldown = max(0, self.scooldown - 1)
        self.rcooldown = max(0, self.rcooldown - 1)
        self.inv = max(0, self.inv - 1)
        self.dash_cd = max(0, self.dash_cd - 1)

    def add_xp(self, amount, particles):
        self.xp += amount
        if self.xp >= self.next_xp:
            self.level += 1; self.xp -= self.next_xp; self.next_xp = int(self.next_xp * 1.5)
            self.max_hp += 20; self.hp = self.max_hp
            for _ in range(20): particles.append(Particle(self.x, self.y, 'spark', big=True))

    def unlock_weapon(self, particles):
        available = [w for w in ['shotgun', 'plasma'] if w not in self.weapons]
        if available:
            new_wep = random.choice(available)
            self.weapons.append(new_wep)
            self.cur_wep = new_wep
            for _ in range(15): particles.append(Particle(self.x, self.y, 'spark', big=True))
        else:
            self.add_xp(30, particles) 
            self.rockets += 3

    def draw(self, surf, frame):
        if self.inv > 0 and (frame // 4) % 2 == 1: return
        x, y, tilt = int(self.x), int(self.y), int(self.vx * 1.5)
        
        pygame.draw.ellipse(surf, (40, 90, 40), (x-self.w//2, y-self.h//2 - tilt//4, self.w, self.h))
        pygame.draw.ellipse(surf, (20, 150, 255), (x+8, y-self.h//3 - tilt//4, self.w//4, self.h//2))
        pygame.draw.polygon(surf, (30, 70, 30), [(x-self.w//2+10, y - tilt//4), (x-self.w//2-15, y-self.h//2 - tilt), (x-self.w//2-15, y+self.h//4 - tilt)])
        
        cx, cy = x + math.cos(self.aim_angle)*25, y + 4 + math.sin(self.aim_angle)*25
        pygame.draw.line(surf, (20, 20, 20), (x, y+4), (cx, cy), 6)
        
        rot_angle = (frame * 0.6) % (math.pi * 2)
        for i in range(4):
            a = rot_angle + i * 1.57
            pygame.draw.line(surf, (200, 200, 200), (x, y-self.h//2-4), (int(x + math.cos(a) * 45), int(y - self.h//2 - 6 + math.sin(a) * 6)), 3)
            
        pygame.draw.rect(surf, (30,30,30), (x-20, y-30, 40, 5))
        pygame.draw.rect(surf, RED if self.overheated else (YELLOW if self.heat > 70 else WHITE), (x-20, y-30, int(40 * (self.heat/self.max_heat)), 5))
        if self.shield: pygame.draw.circle(surf, (50, 200, 255), (x, y), 50, 2)

# ─── INIMIGOS E BOSS ──────────────────────────────────────────────────────────
class Enemy:
    def __init__(self, kind, wave, theme, px=0, py=0):
        self.kind = kind
        self.dead = False
        self.theme = theme
        self.x = W + 30 
        
        m = 1 + (wave-1)*0.15
        speed_mod = 1.3 if theme == 'desert' else 1.0
        hp_mod = 1.2 if theme == 'snow' else 1.0
        
        if kind == 'drone':
            self.y, self.w, self.h = py + random.randint(-100, 100), 20, 20
            self.vx, self.vy = 0, 0
            self.hp = self.max_hp = (20+wave*5) * hp_mod
            self.pts, self.sc, self.sr = 30, 0, 0 
        elif kind == 'tank':
            self.y, self.w, self.h = GROUND_Y-26, 65, 30
            self.vx, self.vy = -(1.0*m) * speed_mod, 0
            self.hp = self.max_hp = (80+wave*10) * hp_mod
            self.sc, self.sr, self.pts = int(60+random.random()*60), 80, 100
        elif kind == 'jeep':
            self.y, self.w, self.h = GROUND_Y-18, 45, 20
            self.vx, self.vy = -(2.5*m) * speed_mod, 0
            self.hp = self.max_hp = (30+wave*5) * hp_mod
            self.sc, self.sr, self.pts = int(40+random.random()*30), 50, 50
        elif kind == 'heli':
            self.ty = 80+random.random()*(GROUND_Y-200)
            self.y, self.w, self.h = self.ty, 65, 26
            self.vx, self.vy = -(1.5*m) * speed_mod, 0
            self.hp = self.max_hp = (60+wave*8) * hp_mod
            self.sc, self.sr, self.pts, self.rot, self.bob = int(40+random.random()*40), 60, 150, 0, random.random()*6.28
        elif kind == 'turret':
            self.x += random.random()*100
            self.y, self.w, self.h = GROUND_Y-36, 26, 40
            self.vx, self.vy = 0, 0
            self.hp = self.max_hp = (100+wave*15) * hp_mod
            self.sc, self.sr, self.pts = int(70+random.random()*30), 100, 200

    def get_colors(self):
        if self.theme == 'desert': return (160, 130, 70), (120, 90, 40)
        elif self.theme == 'snow': return (190, 190, 200), (140, 140, 150)
        else: return (30, 30, 30), (80, 70, 30)

    def update(self, scroll_spd, px, py):
        if self.kind == 'drone':
            angle = math.atan2(py - self.y, px - self.x)
            spd = 6.0 if self.theme == 'desert' else 4.5
            self.vx, self.vy = math.cos(angle) * spd, math.sin(angle) * spd
            self.x += self.vx; self.y += self.vy
        else:
            if self.kind in ('tank', 'jeep', 'turret'):
                self.x -= scroll_spd  
                self.x += self.vx
            else:
                self.x += self.vx
                if self.kind == 'heli':
                    self.bob += 0.03; self.y = self.ty + math.sin(self.bob) * 30
                    self.rot = (self.rot + 0.4) % (math.pi*2)

    def draw(self, surf, frame, px, py):
        x, y = int(self.x), int(self.y)
        c1, c2 = self.get_colors()
        if self.kind in ['tank', 'jeep', 'turret']: pygame.draw.ellipse(surf, (10, 20, 10), (x-self.w//2, GROUND_Y-5, self.w, 10))

        if self.kind == 'drone':
            pygame.draw.circle(surf, RED if self.theme != 'snow' else (100,200,255), (x, y), self.w//2)
            pygame.draw.circle(surf, YELLOW, (x, y), self.w//4)
            pygame.draw.line(surf, ORANGE, (x, y), (x - self.vx*3, y - self.vy*3), 3)
        elif self.kind == 'tank':
            pygame.draw.rect(surf, c1, (x-self.w//2-5, y-4, self.w+10, 10))
            pygame.draw.rect(surf, c2, (x-self.w//2, y-self.h, self.w, self.h))
            angle = math.atan2(py - (y-self.h), px - x)
            pygame.draw.line(surf, (50, 50, 50), (x, y-self.h), (x + math.cos(angle)*30, y - self.h + math.sin(angle)*30), 6)
            pygame.draw.ellipse(surf, c1, (x-15, y-self.h-10, 30, 20))
        elif self.kind == 'jeep':
            pygame.draw.rect(surf, c2, (x-self.w//2, y-self.h, self.w, int(self.h*.7)))
            pygame.draw.rect(surf, c1, (x-self.w//2+5, y-self.h, self.w-10, self.h))
            wa = (frame * 0.3) % (math.pi*2)
            for wx in [x-self.w//2+8, x+self.w//2-8]:
                pygame.draw.circle(surf, (20, 20, 20), (wx, y), 8)
                pygame.draw.line(surf, (100,100,100), (int(wx+math.cos(wa)*6), int(y+math.sin(wa)*6)), (int(wx-math.cos(wa)*6), int(y-math.sin(wa)*6)), 2)
        elif self.kind == 'heli':
            pygame.draw.ellipse(surf, c2, (x-self.w//2, y-self.h//2, self.w, self.h))
            pygame.draw.ellipse(surf, c1, (x-self.w//2+5, y-self.h//3, self.w//4, self.h//2))
            for i in range(3):
                a = self.rot + i * 2.09
                pygame.draw.line(surf, (180, 180, 180), (x, y-self.h//2-4), (int(x + math.cos(a) * 35), int(y - self.h//2 - 4 + math.sin(a) * 8)), 3)
        elif self.kind == 'turret':
            pygame.draw.rect(surf, c1, (x-13, y, 26, 10))
            pygame.draw.rect(surf, c2, (x-10, y-self.h+10, 20, self.h-10))
            ga = math.atan2(py - (y-self.h//2), px - x)
            pygame.draw.line(surf, (255, 50, 50), (x, y-self.h//2), (x+math.cos(ga)*800, y-self.h//2+math.sin(ga)*800), 1)
            pygame.draw.line(surf, (30, 30, 30), (x, y-int(self.h*.6)), (int(x + math.cos(ga)*25), int(y - self.h//2 + math.sin(ga)*25)), 8)
            
        if self.x > W:
            pygame.draw.polygon(surf, RED, [(W - 5, y), (W - 15, y - 6), (W - 15, y + 6)])

class Boss:
    def __init__(self):
        self.x, self.y, self.w, self.h = W + 200, H//2, 180, 100
        self.hp = self.max_hp = 3500 
        self.dead, self.phase, self.timer = False, 'enter', 0
        self.bob = 0

    def update(self, player_x, player_y, e_bullets):
        self.bob += 0.05
        self.y = H//2 + math.sin(self.bob) * 50
        
        if self.phase == 'enter':
            self.x -= 2
            if self.x <= W - 150: self.phase, self.timer = 'attack', 120
        elif self.phase == 'attack':
            self.timer -= 1
            if self.timer <= 0:
                self.timer = 120
                if random.random() > 0.5:
                    for i in range(-3, 4): e_bullets.append(Bullet(self.x-90, self.y, -10, i*2, False, 10, ORANGE, 3))
                else:
                    for _ in range(8): e_bullets.append(Bullet(self.x-90, self.y-30+random.randint(-20,20), -12, random.uniform(-2,2), False, 10, ORANGE, 3))

    def draw(self, surf, frame):
        x, y = int(self.x), int(self.y)
        pygame.draw.ellipse(surf, (150, 180, 220), (x-self.w//2, y-self.h//2, self.w, self.h)) 
        pygame.draw.rect(surf, (80, 90, 100), (x-self.w//2-20, y-20, 60, 40))
        for off_x in [-50, 50]:
            pygame.draw.line(surf, (50, 60, 70), (x+off_x, y-self.h//2), (x+off_x, y-self.h//2-20), 8)
            rot = (frame * 0.5) % (math.pi * 2)
            pygame.draw.line(surf, WHITE, (x+off_x - math.cos(rot)*60, y-self.h//2-20), (x+off_x + math.cos(rot)*60, y-self.h//2-20), 4)

class Bullet:
    def __init__(self, x, y, vx, vy, friendly, damage, color=CYAN, size=3, pierce=False):
        self.x, self.y, self.vx, self.vy = float(x), float(y), vx, vy
        self.friendly, self.damage = friendly, damage
        self.color, self.size, self.pierce = color, size, pierce
        self.hit_enemies = [] 
        
    def update(self): self.x+=self.vx; self.y+=self.vy
    def draw(self, surf):
        pygame.draw.line(surf, self.color, (int(self.x), int(self.y)), (int(self.x - math.cos(math.atan2(self.vy, self.vx))*15), int(self.y - math.sin(math.atan2(self.vy, self.vx))*15)), self.size)
        pygame.draw.circle(surf, WHITE, (int(self.x), int(self.y)), self.size)

class Rocket:
    def __init__(self, x, y, aim_angle):
        self.x, self.y, self.life = float(x), float(y), 150
        self.vx = math.cos(aim_angle) * 12.0
        self.vy = math.sin(aim_angle) * 12.0
        
    def update(self, enemies, boss, particles):
        self.x+=self.vx; self.y+=self.vy; self.life-=1
        particles.append(Particle(self.x, self.y, 'smoke'))
        ne, nd = None, 400
        for e in enemies + ([boss] if boss and not boss.dead else []):
            d = math.hypot(e.x-self.x, e.y-self.y)
            if d < nd: nd, ne = d, e
        if ne:
            d = math.hypot(ne.x-self.x, ne.y-self.y)
            if d>0: self.vx+= (ne.x-self.x)/d*1.2; self.vy+= (ne.y-self.y)/d*1.2
            sp = math.hypot(self.vx,self.vy)
            if sp>18: self.vx, self.vy = self.vx/sp*18, self.vy/sp*18
    def draw(self, surf):
        x, y = int(self.x), int(self.y)
        ca, sa = math.cos(math.atan2(self.vy, self.vx)), math.sin(math.atan2(self.vy, self.vx))
        pygame.draw.polygon(surf, WHITE, [(x+ca*15, y+sa*15), (x-sa*4, y+ca*4), (x-ca*10, y-sa*10), (x+sa*4, y-ca*4)])
        pygame.draw.circle(surf, ORANGE, (int(x - ca*10), int(y - sa*10)), 5)

class Pickup:
    def __init__(self, x, y, kind, from_air=False):
        self.x, self.y, self.vy, self.kind, self.life, self.bob = float(x), float(y), 1.5 if from_air else 0, kind, 400, 0
    def update(self):
        self.y += self.vy; self.life -= 1; self.bob += 0.1
        if self.y > GROUND_Y - 15: self.vy = 0
    def draw(self, surf):
        x, y = int(self.x), int(self.y + math.sin(self.bob)*3)
        if self.kind == 'xp': pygame.draw.circle(surf, BLUE, (x, y), 8); pygame.draw.circle(surf, WHITE, (x, y), 10, 1) 
        elif self.kind == 'health': pygame.draw.rect(surf, GREEN, (x-10, y-4, 20, 8)); pygame.draw.rect(surf, GREEN, (x-4, y-10, 8, 20))
        elif self.kind == 'rocket': pygame.draw.rect(surf, ORANGE, (x-10, y-4, 20, 8)); pygame.draw.polygon(surf, RED, [(x+10, y-4), (x+18, y), (x+10, y+4)])
        elif self.kind == 'shield': pygame.draw.circle(surf, CYAN, (x, y), 10); pygame.draw.circle(surf, WHITE, (x, y), 14, 2)
        elif self.kind == 'weapon': pygame.draw.rect(surf, SILVER, (x-8, y-8, 16, 16)); pygame.draw.rect(surf, PURPLE, (x-8, y-8, 16, 16), 2); surf.blit(font_sm.render('W', True, BLACK), (x-4, y-7))
        if self.kind != 'xp': pygame.draw.circle(surf, WHITE, (x, y), 16, 1)

def draw_hud(surf, player, score, wave, boss, theme_name):
    bar = pygame.Surface((W, 55), pygame.SRCALPHA); bar.fill((0, 0, 0, 180)); surf.blit(bar, (0, 0))
    bar2 = pygame.Surface((W, 55), pygame.SRCALPHA); bar2.fill((0, 0, 0, 180)); surf.blit(bar2, (0, H-55))

    surf.blit(font_sm.render('SCORE', True, (100, 150, 100)), (15, 8))
    surf.blit(font_md.render(str(score).zfill(7), True, WHITE), (15, 25))
    
    map_text = "FLORESTA" if theme_name == 'forest' else ("DESERTO" if theme_name == 'desert' else "GELO")
    w_text = font_sm.render(f'WAVE {wave}/6 [{map_text}]' if wave <=6 else 'BOSS BATTLE', True, RED if wave > 6 else (100, 150, 100))
    surf.blit(w_text, (W//2 - w_text.get_width()//2, 8))

    regen_txt = "+ REGEN ATIVO +" if (player.time_since_hit > player.regen_delay and player.hp < player.max_hp) else ""
    surf.blit(font_sm.render(f'HP (LVL {player.level}) {regen_txt}', True, GREEN if regen_txt else (100,150,100)), (15, H-45))
    pygame.draw.rect(surf, (40,20,20), (15, H-30, 150, 12))
    pygame.draw.rect(surf, GREEN if player.hp > (player.max_hp*0.3) else RED, (15, H-30, int(150*(max(0,player.hp)/player.max_hp)), 12))
    
    pygame.draw.rect(surf, (20,20,60), (15, H-16, 150, 4))
    pygame.draw.rect(surf, BLUE, (15, H-16, int(150*(player.xp/player.next_xp)), 4))
    
    surf.blit(font_sm.render('ARMAS (1,2,3)', True, (100,150,100)), (200, H-45))
    wx = 200
    for w_id, w_info in WEAPON_STATS.items():
        if w_id in player.weapons:
            color = CYAN if player.cur_wep == w_id else GRAY
            surf.blit(font_sm.render(w_info['name'], True, color), (wx, H-30))
            wx += 110
    
    surf.blit(font_sm.render('FOGUETES (Botão Dir)', True, (100,150,100)), (550, H-45))
    for i in range(10): pygame.draw.rect(surf, (40,40,40), (550+i*14, H-30, 10, 12))
    for i in range(player.rockets): pygame.draw.rect(surf, ORANGE, (550+i*14, H-30, 10, 12))
    
    surf.blit(font_sm.render('DASH (SHIFT)', True, (100,150,100)), (750, H-45))
    pygame.draw.rect(surf, (40,40,40), (750, H-30, 100, 12))
    pygame.draw.rect(surf, CYAN, (750, H-30, int(100*(1-(player.dash_cd/90))), 12))
    
    if boss and not boss.dead:
        pygame.draw.rect(surf, (50,0,0), (W//2 - 200, 30, 400, 15))
        pygame.draw.rect(surf, RED, (W//2 - 200, 30, int(400*(boss.hp/boss.max_hp)), 15))

def draw_crosshair(surf, mx, my, player):
    wep = WEAPON_STATS[player.cur_wep]
    col = RED if player.overheated else wep['color']
    pygame.draw.circle(surf, col, (mx, my), 15, 1)
    pygame.draw.circle(surf, col, (mx, my), 2)
    pygame.draw.line(surf, col, (mx-20, my), (mx-5, my), 2)
    pygame.draw.line(surf, col, (mx+5, my), (mx+20, my), 2)
    pygame.draw.line(surf, col, (mx, my-20), (mx, my-5), 2)
    pygame.draw.line(surf, col, (mx, my+5), (mx, my+20), 2)

# ─── MAIN LOOP (Sistema de Ondas Corrigido) ───────────────────────────────────
# O triplo de inimigos para um combate verdadeiramente tático e frenético
WAVE_CONFIG = [
    {'tank':4,'jeep':6,'drone':5,'heli':2,'turret':1}, 
    {'tank':6,'jeep':8,'drone':8,'heli':4,'turret':2}, 
    {'tank':8,'jeep':10,'drone':12,'heli':6,'turret':4}, 
    {'tank':10,'jeep':12,'drone':16,'heli':8,'turret':6}, 
    {'tank':15,'jeep':15,'drone':20,'heli':12,'turret':8}, 
    {'tank':0,'jeep':0,'drone':0,'heli':0,'turret':0}  
]

def get_theme_for_wave(wave):
    if wave <= 2: return 'forest'
    elif wave <= 4: return 'desert'
    else: return 'snow'

def main():
    gs, score, wave, frame, scroll_x, screen_shake = 'menu', 0, 1, 0, 0.0, 0
    player, bg = Player(), Background()
    p_bullets, p_rockets, e_bullets, enemies, particles, pickups = [], [], [], [], [], []
    spawn_queue, spawn_timer, wave_complete, wave_clear_timer, boss = [], 0, False, 0, None
    theme_name = 'forest'

    def start_wave(w):
        nonlocal spawn_queue, spawn_timer, wave_complete, wave_clear_timer, boss, theme_name
        theme_name = get_theme_for_wave(w)
        if w == 6:
            boss = Boss()
        else:
            spawn_queue = []
            for k, v in WAVE_CONFIG[min(w-1, 4)].items(): spawn_queue += [k] * v
            random.shuffle(spawn_queue)
        spawn_timer, wave_complete, wave_clear_timer = 30, False, 0

    running = True
    while running:
        dt_keys = pygame.key.get_pressed()
        mx, my = pygame.mouse.get_pos()
        mouse_btns = pygame.mouse.get_pressed()
        
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT: running = False; sys.exit()
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_SPACE and gs in ('menu','over','win'):
                    gs, score, wave, frame, p_bullets, p_rockets, e_bullets, enemies, particles, pickups, boss = 'playing', 0, 1, 0, [], [], [], [], [], [], None
                    player = Player(); start_wave(1)
                
                if gs == 'playing':
                    if ev.key == pygame.K_1 and 'mg' in player.weapons: player.cur_wep = 'mg'
                    if ev.key == pygame.K_2 and 'shotgun' in player.weapons: player.cur_wep = 'shotgun'
                    if ev.key == pygame.K_3 and 'plasma' in player.weapons: player.cur_wep = 'plasma'

        if gs == 'playing':
            frame += 1; scroll_x += 2.5; screen_shake = max(0, screen_shake - 1)
            player.update(dt_keys, mx, my, particles)
            
            if mouse_btns[0] and player.scooldown <= 0 and not player.is_dashing and not player.overheated:
                wep = WEAPON_STATS[player.cur_wep]
                player.heat += wep['heat']
                player.scooldown = max(2, wep['cooldown'] - (player.level * 0.3))
                bx, by = player.x + math.cos(player.aim_angle)*25, player.y + 4 + math.sin(player.aim_angle)*25
                dmg = wep['dmg'] + (player.level * 2)
                
                if player.cur_wep == 'mg':
                    p_bullets.append(Bullet(bx, by, math.cos(player.aim_angle)*wep['speed'], math.sin(player.aim_angle)*wep['speed'], True, dmg, wep['color'], wep['size'], wep['pierce']))
                elif player.cur_wep == 'shotgun':
                    for ang_off in [-0.2, -0.1, 0, 0.1, 0.2]:
                        a = player.aim_angle + ang_off
                        p_bullets.append(Bullet(bx, by, math.cos(a)*wep['speed'], math.sin(a)*wep['speed'], True, dmg, wep['color'], wep['size'], wep['pierce']))
                elif player.cur_wep == 'plasma':
                    bx1, by1 = bx + math.cos(player.aim_angle - 1.57)*6, by + math.sin(player.aim_angle - 1.57)*6
                    bx2, by2 = bx + math.cos(player.aim_angle + 1.57)*6, by + math.sin(player.aim_angle + 1.57)*6
                    p_bullets.append(Bullet(bx1, by1, math.cos(player.aim_angle)*wep['speed'], math.sin(player.aim_angle)*wep['speed'], True, dmg, wep['color'], wep['size'], wep['pierce']))
                    p_bullets.append(Bullet(bx2, by2, math.cos(player.aim_angle)*wep['speed'], math.sin(player.aim_angle)*wep['speed'], True, dmg, wep['color'], wep['size'], wep['pierce']))
                
            if mouse_btns[2] and player.rcooldown <= 0 and player.rockets > 0:
                p_rockets.append(Rocket(player.x, player.y, player.aim_angle)); player.rockets -= 1; player.rcooldown = 25; screen_shake = max(screen_shake, 3)

            for b in p_bullets: b.update()
            p_bullets[:] = [b for b in p_bullets if 0 < b.x <= W and 0 < b.y < H] 
            
            for b in p_bullets[:]:
                hit_something = False
                for e in enemies:
                    if not e.dead and e.x <= W and e not in b.hit_enemies and e.x-e.w//2 < b.x < e.x+e.w//2 and e.y-e.h < b.y < e.y+e.h:
                        e.hp -= b.damage; particles.append(Particle(b.x, b.y, 'spark')); hit_something = True
                        b.hit_enemies.append(e)
                        if e.hp <= 0:
                            e.dead = True; score += e.pts; screen_shake = max(screen_shake, 5); explode(particles, e.x, e.y, True)
                            pickups.append(Pickup(e.x, e.y, 'xp', True)) 
                            
                            drop_chance = random.random()
                            if e.kind in ['heli', 'tank'] and drop_chance < 0.15: 
                                pickups.append(Pickup(e.x+15, e.y if e.kind=='heli' else GROUND_Y-15, 'weapon', e.kind=='heli'))
                            elif drop_chance < 0.35: 
                                pickups.append(Pickup(e.x+10, e.y if e.kind=='heli' else GROUND_Y-15, random.choice(['health','rocket','shield'])))
                
                if boss and not boss.dead and boss not in b.hit_enemies and abs(b.x-boss.x) < boss.w//2 and abs(b.y-boss.y) < boss.h//2:
                    boss.hp -= b.damage; particles.append(Particle(b.x, b.y, 'spark')); hit_something = True
                    b.hit_enemies.append(boss)
                    if boss.hp <= 0: boss.dead = True; score += 5000; wave_complete = True; explode(particles, boss.x, boss.y, True); screen_shake = 30
                
                if hit_something and not b.pierce:
                    try: p_bullets.remove(b)
                    except: pass

            for r in p_rockets: r.update(enemies, boss, particles)
            for r in p_rockets[:]:
                if r.x > W+50 or r.x < -50 or r.y < -50 or r.life <= 0: p_rockets.remove(r); continue
                if r.y > GROUND_Y-5: explode(particles, r.x, GROUND_Y, False); screen_shake = max(screen_shake, 8); p_rockets.remove(r); continue
                hit = False
                for e in enemies + ([boss] if boss and not boss.dead else []):
                    if e.x <= W and math.hypot(e.x-r.x, e.y-r.y) < (80 if isinstance(e, Boss) else 50):
                        e.hp -= 150 + (player.level*10); explode(particles, r.x, r.y, True); screen_shake = max(screen_shake, 12); hit = True
                        if e.hp <= 0:
                            e.dead = True; score += 5000 if isinstance(e, Boss) else getattr(e, 'pts', 0)
                            if isinstance(e, Boss): wave_complete = True
                        break
                if hit: p_rockets.remove(r)

            for b in e_bullets: b.update()
            e_bullets[:] = [b for b in e_bullets if -50 < b.x < W+50 and -50 < b.y < H+50]
            for b in e_bullets[:]:
                if player.inv > 0 or player.is_dashing: continue
                if abs(b.x-player.x) < player.w//2-10 and abs(b.y-player.y) < player.h//2-5:
                    screen_shake = player.take_damage(15, screen_shake)
                    explode(particles, b.x, b.y, False)
                    if player.hp <= 0: gs = 'over'; explode(particles, player.x, player.y, True); screen_shake = 20
                    try: e_bullets.remove(b)
                    except: pass

            for e in enemies:
                e.update(2.5, player.x, player.y)
                if e.x < -150: e.dead=True; continue
                
                if e.kind != 'drone':
                    e.sc -= 1
                    if e.sc <= 0 and e.x < W:
                        e.sc = e.sr
                        dist = math.hypot(player.x - e.x, player.y - e.y)
                        if 0 < dist < 700:
                            if e.kind == 'heli':
                                for ang in [-0.2, 0, 0.2]: e_bullets.append(Bullet(e.x, e.y, (player.x-e.x)*math.cos(ang) - (player.y-e.y)*math.sin(ang)/dist*6, (player.x-e.x)*math.sin(ang) + (player.y-e.y)*math.cos(ang)/dist*6, False, 15, ORANGE))
                            else: e_bullets.append(Bullet(e.x, e.y - e.h//2, (player.x-e.x)/dist*6, (player.y-e.y)/dist*6, False, 15, ORANGE))
                
                if player.inv <= 0 and not player.is_dashing and abs(player.x-e.x) < (player.w//2+e.w//2-10) and abs(player.y-(e.y if e.kind in ['heli', 'drone'] else e.y-e.h//2)) < (player.h//2+e.h//2-10):
                    if player.shield: 
                        player.shield = False; player.inv = 60
                        if e.kind == 'drone': 
                            e.dead = True; explode(particles, e.x, e.y, True)
                    else: 
                        if e.kind == 'drone':
                            screen_shake = player.take_damage(40, screen_shake) 
                            e.dead = True; explode(particles, e.x, e.y, True)
                        else:
                            screen_shake = player.take_damage(30, screen_shake)
                            e.hp -= 50
                            if e.hp <= 0:
                                e.dead = True; explode(particles, e.x, e.y, True)
                        if player.hp <= 0: gs = 'over'; explode(particles, player.x, player.y, True); screen_shake = 20
            
            enemies[:] = [e for e in enemies if not e.dead]
            
            if boss and not boss.dead: boss.update(player.x, player.y, e_bullets)

            for p in pickups: p.update()
            pickups[:] = [p for p in pickups if p.life > 0 and p.x > -50]
            for p in pickups[:]:
                if abs(p.x-player.x) < 40 and abs(p.y-player.y) < 40:
                    if p.kind == 'xp': player.add_xp(10, particles)
                    elif p.kind == 'health': player.hp=min(player.max_hp,player.hp+50)
                    elif p.kind == 'rocket': player.rockets=min(15,player.rockets+5)
                    elif p.kind == 'shield': player.shield = True
                    elif p.kind == 'weapon': player.unlock_weapon(particles)
                    pickups.remove(p)

            for pt in particles: pt.update()
            particles[:] = [p for p in particles if p.life > 0 and p.size > 0.5]

            # NOVO: Spawner dinâmico de inimigos! (Nascem em massa e super rápido)
            if spawn_queue and not wave_complete:
                spawn_timer -= 1
                if spawn_timer <= 0: 
                    spawn_timer = max(10, 40 - (wave * 5)) # Muito mais rápido nas waves finais
                    enemies.append(Enemy(spawn_queue.pop(0), wave, theme_name, player.x, player.y))
                    
            # NOVO: Correção Definitiva do Bug de "Wave Travada"
            if not spawn_queue and len(enemies) == 0 and not wave_complete and wave < 6:
                wave_complete = True; wave_clear_timer = 0; wave += 1
                
            if wave_complete:
                wave_clear_timer += 1
                if wave_clear_timer > 180:
                    if wave > 6: gs = 'win'
                    else: start_wave(wave)

        # ─── RENDERIZAR TUDO ─────────────────────────────────────────────
        if gs != 'menu': bg.draw(display_surf, scroll_x, theme_name)
        else: display_surf.fill(SKY1)

        if gs in ('playing', 'over'):
            for p in pickups: p.draw(display_surf)
            for pt in particles:
                if pt.kind == 'smoke': pt.draw(display_surf)
            for e in enemies: e.draw(display_surf, frame, int(player.x), int(player.y))
            if boss and not boss.dead: boss.draw(display_surf, frame)
            for b in p_bullets + e_bullets: b.draw(display_surf)
            for r in p_rockets: r.draw(display_surf)
            for pt in particles:
                if pt.kind != 'smoke': pt.draw(display_surf)
            if gs == 'playing': player.draw(display_surf, frame)
            
            draw_hud(display_surf, player, score, wave, boss, theme_name)
            if gs == 'playing': draw_crosshair(display_surf, mx, my, player)

        if gs == 'menu':
            display_surf.blit(font_lg.render('AIR ASSAULT WARZONE', True, CYAN), (W//2-250, H//2-110))
            if (frame//30)%2==0: display_surf.blit(font_md.render('PRESSIONE ESPAÇO PARA INICIAR', True, WHITE), (W//2-180, H//2+10))
            display_surf.blit(font_sm.render('WASD: MOVER | MOUSE: MIRAR/ATIRAR | 1,2,3: ARMAS', True, GRAY), (W//2-200, H//2+70))

        elif gs == 'over':
            display_surf.blit(font_lg.render('MISSÃO FALHOU', True, RED), (W//2-150, H//2-80))
            display_surf.blit(font_md.render(f'PONTUAÇÃO FINAL: {score}', True, WHITE), (W//2-130, H//2-10))

        elif gs == 'win':
            display_surf.blit(font_lg.render('VITÓRIA SUPREMA!', True, YELLOW), (W//2-180, H//2-80))
            display_surf.blit(font_md.render(f'PONTUAÇÃO: {score}', True, WHITE), (W//2-100, H//2-10))

        screen.blit(display_surf, (random.randint(-screen_shake, screen_shake), random.randint(-screen_shake, screen_shake)))
        pygame.display.flip()
        clock.tick(FPS)

if __name__ == '__main__':
    main()
