"""
AIR ASSAULT - Versão Python com Pygame
Instale: pip install pygame
Execute: python air_assault.py
"""
import pygame
import random
import math
import sys

pygame.init()

W, H = 960, 560
GROUND_Y = H - 80
FPS = 60

screen = pygame.display.set_mode((W, H))
pygame.display.set_caption("AIR ASSAULT")
clock = pygame.time.Clock()

# ─── CORES ────────────────────────────────────────────────────────────────────
BLACK   = (0, 0, 0)
WHITE   = (255, 255, 255)
GREEN   = (50, 180, 50)
DKGREEN = (20, 80, 20)
RED     = (220, 50, 50)
ORANGE  = (255, 140, 0)
YELLOW  = (255, 255, 80)
BLUE    = (30, 100, 200)
GRAY    = (100, 100, 100)
BROWN   = (80, 60, 20)
SKY1    = (6, 12, 28)
SKY2    = (15, 37, 85)
SKY3    = (26, 64, 112)

# ─── FONTES ───────────────────────────────────────────────────────────────────
try:
    font_lg = pygame.font.SysFont("Courier New", 48, bold=True)
    font_md = pygame.font.SysFont("Courier New", 22, bold=True)
    font_sm = pygame.font.SysFont("Courier New", 13)
except:
    font_lg = pygame.font.Font(None, 52)
    font_md = pygame.font.Font(None, 26)
    font_sm = pygame.font.Font(None, 16)

# ─── SOM (procedural) ─────────────────────────────────────────────────────────
def make_sound(freq, duration_ms, vol=0.3, wave='square'):
    sample_rate = 22050
    n = int(sample_rate * duration_ms / 1000)
    buf = bytearray(n * 2)
    for i in range(n):
        t = i / sample_rate
        if wave == 'square':
            v = vol if (i % int(sample_rate / freq)) < (sample_rate / freq / 2) else -vol
        elif wave == 'saw':
            v = vol * (2 * ((t * freq) % 1) - 1)
        else:
            v = vol * math.sin(2 * math.pi * freq * t)
        val = int(v * 32767)
        val = max(-32768, min(32767, val))
        buf[i*2]   = val & 0xFF
        buf[i*2+1] = (val >> 8) & 0xFF
    return pygame.sndarray.make_sound(
        pygame.array.array('h', [int(v) for v in
            [int(vol * 32767 * (math.sin(2*math.pi*freq*i/sample_rate) if wave=='sine'
              else (1 if (i % max(1,int(sample_rate/freq))) < (sample_rate/max(1,freq)/2) else -1)))
             for i in range(n)]])
    )

# Gera sons simples
try:
    snd_shoot = make_sound(800, 80, 0.08, 'square')
    snd_explode = make_sound(120, 400, 0.2, 'saw')
    snd_hit = make_sound(400, 120, 0.12, 'square')
    snd_rocket = make_sound(300, 200, 0.15, 'saw')
    snd_pickup = make_sound(800, 250, 0.12, 'sine')
    SOUND_OK = True
except:
    SOUND_OK = False

def play(snd):
    if SOUND_OK:
        try: snd.play()
        except: pass

# ─── PARTÍCULAS ───────────────────────────────────────────────────────────────
class Particle:
    def __init__(self, x, y, big=False, kind='fire'):
        self.x = x + random.uniform(-10, 10) if kind == 'smoke' else x
        self.y = y
        self.kind = kind
        angle = random.uniform(0, math.pi * 2)
        if kind == 'fire':
            speed = random.uniform(2, 6) if big else random.uniform(1, 3)
            self.vx = math.cos(angle) * speed
            self.vy = math.sin(angle) * speed - (2.5 if big else 1)
            colors = [(255,100,0),(255,50,0),(255,180,0),(255,240,80)]
            self.color = random.choice(colors)
            self.size = random.randint(4, 9) if big else random.randint(2, 5)
            self.life = 1.0
            self.decay = 0.018 if big else 0.03
        elif kind == 'smoke':
            speed = random.uniform(0.3, 1.8) if big else random.uniform(0.2, 1.0)
            self.vx = math.cos(angle) * speed
            self.vy = math.sin(angle) * speed - 0.8
            self.color = (60, 70, 55)
            self.size = random.randint(8, 18) if big else random.randint(4, 10)
            self.life = 1.0
            self.decay = 0.009
        else:  # spark
            speed = random.uniform(1, 3)
            self.vx = math.cos(angle) * speed
            self.vy = math.sin(angle) * speed
            self.color = (255, 220, 80)
            self.size = random.randint(2, 4)
            self.life = 1.0
            self.decay = 0.12

    def update(self):
        self.x += self.vx
        self.y += self.vy
        if self.kind == 'fire':
            self.vy -= 0.07
        self.vx *= 0.98
        self.vy *= 0.98
        self.size *= 0.97
        self.life -= self.decay

    def draw(self, surf):
        if self.life <= 0 or self.size < 0.5:
            return
        alpha = int(self.life * 255)
        if self.kind == 'smoke':
            alpha = int(self.life * 100)
        s = max(1, int(self.size))
        tmp = pygame.Surface((s*2, s*2), pygame.SRCALPHA)
        r = min(255, self.color[0])
        g = min(255, self.color[1])
        b = min(255, self.color[2])
        pygame.draw.circle(tmp, (r, g, b, alpha), (s, s), s)
        surf.blit(tmp, (int(self.x) - s, int(self.y) - s))

def explode(particles, x, y, big=True):
    n = 28 if big else 12
    for _ in range(n):
        particles.append(Particle(x, y, big, 'fire'))
    for _ in range(10 if big else 4):
        particles.append(Particle(x, y, big, 'smoke'))

def sparks(particles, x, y):
    for _ in range(6):
        particles.append(Particle(x, y, False, 'spark'))

# ─── FUNDO ────────────────────────────────────────────────────────────────────
def gen_bg():
    mountains = [{'x': i*90+random.randint(0,50), 'h': 50+random.randint(0,130),
                  'w': 70+random.randint(0,90), 'layer': random.randint(0,2)} for i in range(30)]
    trees = [{'x': i*55+random.randint(0,40), 'h': 18+random.randint(0,28),
               'w': 10+random.randint(0,8)} for i in range(50)]
    clouds = [{'x': i*80+random.randint(0,60), 'y': 30+random.randint(0,100),
                'w': 50+random.randint(0,90), 'h': 20+random.randint(0,22),
                'sp': 0.15+random.random()*0.25} for i in range(14)]
    return mountains, trees, clouds

def draw_bg(surf, mountains, trees, clouds, scroll_x, frame):
    # Céu degradê
    for y in range(GROUND_Y):
        t = y / GROUND_Y
        r = int(SKY1[0] + (SKY3[0]-SKY1[0])*t)
        g = int(SKY1[1] + (SKY3[1]-SKY1[1])*t)
        b = int(SKY1[2] + (SKY3[2]-SKY1[2])*t)
        pygame.draw.line(surf, (r, g, b), (0, y), (W, y))

    # Nuvens
    for c in clouds:
        cx = int((c['x'] - scroll_x * c['sp'] * 0.4) % (W+250) - 100)
        r, g, b = 160, 185, 220
        tmp = pygame.Surface((int(c['w']), int(c['h'])), pygame.SRCALPHA)
        pygame.draw.ellipse(tmp, (r,g,b,25), (0, 0, int(c['w']), int(c['h'])))
        surf.blit(tmp, (cx - int(c['w'])//2, int(c['y']) - int(c['h'])//2))

    # Montanhas
    for layer in range(3):
        pf = 0.15 + layer * 0.18
        alpha = 20 + layer*22
        for m in mountains:
            if m['layer'] != layer: continue
            mx = int((m['x'] - scroll_x * pf) % (W+400) - 150)
            pts = [
                (mx, GROUND_Y),
                (mx, int(GROUND_Y - m['h']*0.5)),
                (int(mx + m['w']//2), int(GROUND_Y - m['h'])),
                (int(mx + m['w']), int(GROUND_Y - m['h']*0.5)),
                (int(mx + m['w']), GROUND_Y)
            ]
            tmp = pygame.Surface((W, H), pygame.SRCALPHA)
            pygame.draw.polygon(tmp, (8, 25, 50, alpha), pts)
            surf.blit(tmp, (0, 0))

    # Chão
    for y in range(GROUND_Y, H):
        t = (y - GROUND_Y) / (H - GROUND_Y)
        r = int(20*(1-t) + 8*t)
        g = int(52*(1-t) + 14*t)
        b = int(15*(1-t) + 6*t)
        pygame.draw.line(surf, (r, g, b), (0, y), (W, y))

    # Grade no chão
    gi = 55
    go = int(scroll_x) % gi
    for x in range(-go, W, gi):
        pygame.draw.line(surf, (30, 80, 20, 60), (x, GROUND_Y), (x, H))
    pygame.draw.line(surf, (26, 90, 18), (0, GROUND_Y), (W, GROUND_Y), 2)

    # Árvores
    for t in trees:
        tx = int((t['x'] - scroll_x * 0.92) % (W+120) - 60)
        th, tw = int(t['h']), int(t['w'])
        pygame.draw.rect(surf, (26, 14, 6), (tx+tw//2-2, GROUND_Y-int(th*.35), 4, int(th*.35)))
        pygame.draw.polygon(surf, (13, 46, 10),
            [(tx, GROUND_Y-int(th*.35)), (tx+tw//2, GROUND_Y-th), (tx+tw, GROUND_Y-int(th*.35))])
        pygame.draw.polygon(surf, (18, 58, 14),
            [(tx+2, GROUND_Y-int(th*.55)), (tx+tw//2, GROUND_Y-int(th*1.08)), (tx+tw-2, GROUND_Y-int(th*.55))])

# ─── JOGADOR ──────────────────────────────────────────────────────────────────
class Player:
    def __init__(self):
        self.x = 160.0; self.y = float(H//2)
        self.vx = 0.0; self.vy = 0.0
        self.w = 76; self.h = 28; self.spd = 5.2
        self.hp = 100; self.max_hp = 100
        self.scooldown = 0; self.srate = 8
        self.rockets = 5; self.rcooldown = 0
        self.inv = 0

    def update(self, keys):
        ax, ay = 0, 0
        if keys[pygame.K_LEFT]  or keys[pygame.K_a]: ax = -1
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]: ax =  1
        if keys[pygame.K_UP]    or keys[pygame.K_w]: ay = -1
        if keys[pygame.K_DOWN]  or keys[pygame.K_s]: ay =  1
        self.vx = (self.vx + ax*.55) * .84
        self.vy = (self.vy + ay*.55) * .84
        self.vx = max(-self.spd, min(self.spd, self.vx))
        self.vy = max(-self.spd, min(self.spd, self.vy))
        self.x += self.vx; self.y += self.vy
        self.x = max(self.w//2, min(W-self.w//2, self.x))
        self.y = max(self.h//2+50, min(GROUND_Y-self.h//2-4, self.y))
        if self.scooldown > 0: self.scooldown -= 1
        if self.rcooldown > 0: self.rcooldown -= 1
        if self.inv > 0: self.inv -= 1

    def draw(self, surf, frame):
        if self.inv > 0 and (frame // 4) % 2 == 1:
            return
        x, y = int(self.x), int(self.y)
        # Corpo
        pygame.draw.ellipse(surf, (58, 120, 58), (x-self.w//2, y-self.h//2, self.w, self.h))
        # Cockpit
        pygame.draw.ellipse(surf, (26, 90, 122), (x+8, y-self.h//3, self.w//4, self.h//2))
        # Cauda
        pygame.draw.polygon(surf, (42, 106, 42),
            [(x-self.w//2+8, y), (x-self.w//2-8, y-self.h//2), (x-self.w//2-8, y+self.h//2)])
        # Canhão
        pygame.draw.rect(surf, (30, 62, 30), (x+self.w//4, y-2, self.w//3+12, 5))
        # Cano do canhão (flash)
        if self.scooldown > self.srate - 3:
            pygame.draw.circle(surf, YELLOW, (x+self.w//4+self.w//3+16, y), 4)
        # Rotor principal (3 pás)
        rot_angle = (frame * 0.52) % (math.pi * 2)
        for i in range(3):
            a = rot_angle + i * 2.094
            ex2 = int(x + 5 + math.cos(a) * 38)
            ey2 = int(y - self.h//2 - 2 + math.sin(a) * 7)
            pygame.draw.line(surf, (170, 220, 170), (x+5, y-self.h//2-2), (ex2, ey2), 3)
        # Rotor cauda
        tr = (frame * 0.35) % (math.pi * 2)
        for i in range(2):
            a = tr + i * math.pi
            ex2 = int(x - self.w//2 - 5 + math.cos(a) * 10)
            ey2 = int(y + math.sin(a) * 3)
            pygame.draw.line(surf, (136, 204, 136), (x-self.w//2-5, y), (ex2, ey2), 2)
        # HP bar
        bw = 64
        bx = x - bw//2; by = y - self.h//2 - 13
        pygame.draw.rect(surf, (34, 34, 34), (bx, by, bw, 5))
        hr = self.hp / self.max_hp
        hcol = GREEN if hr > .5 else ORANGE if hr > .25 else RED
        pygame.draw.rect(surf, hcol, (bx, by, int(bw*hr), 5))

# ─── INIMIGOS ─────────────────────────────────────────────────────────────────
class Enemy:
    def __init__(self, kind, wave):
        sx = W + 60
        mult = 1 + (wave-1)*0.12
        self.kind = kind
        self.dead = False
        if kind == 'tank':
            self.x=sx; self.y=GROUND_Y-26; self.w=58; self.h=26
            self.vx=-(0.9*mult); self.vy=0
            self.hp=60+wave*8; self.max_hp=self.hp
            self.sc=int(80+random.random()*60); self.sr=90
            self.pts=100
        elif kind == 'jeep':
            self.x=sx; self.y=GROUND_Y-18; self.w=42; self.h=18
            self.vx=-(1.8*mult); self.vy=0
            self.hp=25+wave*5; self.max_hp=self.hp
            self.sc=int(45+random.random()*35); self.sr=55
            self.pts=50
        elif kind == 'heli':
            self.ty=70+random.random()*(GROUND_Y-160)
            self.x=sx; self.y=self.ty; self.w=58; self.h=22
            self.vx=-(1.2*mult); self.vy=0
            self.hp=45+wave*7; self.max_hp=self.hp
            self.sc=int(50+random.random()*50); self.sr=70
            self.pts=150; self.rot=0; self.bob=random.random()*6.28
        elif kind == 'turret':
            self.x=sx+random.random()*80; self.y=GROUND_Y-36; self.w=22; self.h=36
            self.vx=0; self.vy=0
            self.hp=80+wave*12; self.max_hp=self.hp
            self.sc=int(90+random.random()*40); self.sr=130
            self.pts=200

    def update(self, scroll_spd):
        self.x += self.vx
        if self.kind == 'turret': self.x -= scroll_spd
        if self.kind == 'heli':
            self.bob += 0.018
            self.y = self.ty + math.sin(self.bob) * 18
            self.rot = (self.rot + 0.28) % (math.pi*2)

    def draw(self, surf, frame, px, py):
        x, y = int(self.x), int(self.y)
        if self.kind == 'tank':
            to = (frame//5) % 7
            pygame.draw.rect(surf, (42, 42, 14), (x-self.w//2, y-4, self.w, 4+self.h//4))
            pygame.draw.rect(surf, (90, 90, 32), (x-self.w//2, y-self.h, self.w, self.h))
            pygame.draw.ellipse(surf, (106, 106, 40), (x-self.w//2+8, y-self.h-8, 28, 18))
            pygame.draw.line(surf, (58, 58, 18), (x-4, y-self.h), (x-32, y-self.h+5), 4)
        elif self.kind == 'jeep':
            pygame.draw.rect(surf, (74, 106, 40), (x-self.w//2, y-self.h, self.w, int(self.h*.65)))
            pygame.draw.rect(surf, (58, 90, 26), (x-self.w//2+4, y-self.h, self.w-8, self.h))
            wa = (frame * 0.18) % (math.pi*2)
            for wx in [x-self.w//2+7, x+self.w//2-7]:
                pygame.draw.circle(surf, (26, 26, 10), (wx, y), 6)
                pygame.draw.line(surf, (85, 85, 85),
                    (int(wx+math.cos(wa)*4), int(y+math.sin(wa)*4)),
                    (int(wx-math.cos(wa)*4), int(y-math.sin(wa)*4)), 1)
        elif self.kind == 'heli':
            pygame.draw.ellipse(surf, (122, 42, 26), (x-self.w//2, y-self.h//2, self.w, self.h))
            pygame.draw.ellipse(surf, (170, 34, 0), (x-self.w//2+4, y-self.h//3, self.w//4, self.h//2))
            pygame.draw.polygon(surf, (106, 34, 16),
                [(x-self.w//2+8, y), (x-self.w//2-8, y-self.h//2), (x-self.w//2-8, y+self.h//2)])
            pygame.draw.rect(surf, (58, 18, 8), (x+self.w//4, y-2, self.w//3+6, 4))
            for i in range(3):
                a = self.rot + i * 2.094
                ex2 = int(x + 5 + math.cos(a) * 28)
                ey2 = int(y - self.h//2 - 2 + math.sin(a) * 5)
                pygame.draw.line(surf, (204, 85, 51), (x+5, y-self.h//2-2), (ex2, ey2), 2)
        elif self.kind == 'turret':
            pygame.draw.rect(surf, (58, 58, 20), (x-11, y, 22, 8))
            pygame.draw.rect(surf, (90, 90, 32), (x-8, y-self.h+8, 16, self.h-8))
            dx = px - x; dy = py - (y-self.h//2)
            ga = math.atan2(dy, dx)
            end_x = int(x + math.cos(ga)*22)
            end_y = int(y - self.h//2 + math.sin(ga)*22)
            pygame.draw.line(surf, (42, 42, 8), (x, y-int(self.h*.55)), (end_x, end_y), 4)
        # HP bar
        if self.hp < self.max_hp:
            bw = self.w; bh = 4
            bx = x - self.w//2
            by = y - (self.h//2 if self.kind in ('heli','turret') else self.h) - 8
            pygame.draw.rect(surf, (34, 34, 34), (bx, by, bw, bh))
            r = self.hp / self.max_hp
            pygame.draw.rect(surf, GREEN if r > .5 else RED, (bx, by, int(bw*r), bh))

# ─── PICKUP ───────────────────────────────────────────────────────────────────
class Pickup:
    def __init__(self, x, y, kind, from_air=False):
        self.x = float(x); self.y = float(y)
        self.vx = 0; self.vy = 0.8 if from_air else 0
        self.kind = kind; self.life = 320

    def update(self):
        self.y += self.vy
        if self.y > GROUND_Y - 12: self.vy = 0
        self.x -= 0
        self.life -= 1

    def draw(self, surf, frame):
        x, y = int(self.x), int(self.y)
        pulse = int(math.sin(frame * .09) * 2)
        if self.kind == 'health':
            pygame.draw.rect(surf, (0, 200, 50), (x-10, y-3, 20, 6))
            pygame.draw.rect(surf, (0, 200, 50), (x-3, y-10, 6, 20))
        elif self.kind == 'rocket':
            pygame.draw.rect(surf, ORANGE, (x-8, y-3, 16, 6))
            pygame.draw.polygon(surf, RED, [(x+8, y-3), (x+14, y), (x+8, y+3)])
        else:
            pygame.draw.circle(surf, BLUE, (x, y), 8+pulse//3)
            lbl = font_sm.render('A', True, WHITE)
            surf.blit(lbl, (x-lbl.get_width()//2, y-lbl.get_height()//2))
        pygame.draw.rect(surf, (200, 200, 200, 150), (x-12, y-12, 24, 24), 1)

# ─── PROJÉTEIS ────────────────────────────────────────────────────────────────
class Bullet:
    def __init__(self, x, y, vx, vy, friendly):
        self.x=float(x); self.y=float(y)
        self.vx=vx; self.vy=vy
        self.friendly=friendly

    def update(self): self.x+=self.vx; self.y+=self.vy

    def draw(self, surf):
        col = YELLOW if self.friendly else RED
        angle = math.atan2(self.vy, self.vx)
        x, y = int(self.x), int(self.y)
        ex = int(x - math.cos(angle)*5); ey = int(y - math.sin(angle)*2)
        pygame.draw.line(surf, col, (x, y), (ex, ey), 2)
        pygame.draw.circle(surf, col, (x, y), 2)

class Rocket:
    def __init__(self, x, y):
        self.x=float(x); self.y=float(y)
        self.vx=10.0; self.vy=0.0; self.life=130

    def update(self, enemies):
        self.x+=self.vx; self.y+=self.vy; self.life-=1
        ne = None; nd = 350
        for e in enemies:
            d = math.hypot(e.x-self.x, e.y-self.y)
            if d < nd: nd=d; ne=e
        if ne:
            dx=ne.x-self.x; dy=ne.y-self.y; d=math.hypot(dx,dy)
            if d>0: self.vx+=dx/d*.55; self.vy+=dy/d*.3
            sp=math.hypot(self.vx,self.vy)
            if sp>13: self.vx=self.vx/sp*13; self.vy=self.vy/sp*13

    def draw(self, surf):
        x, y = int(self.x), int(self.y)
        angle = math.atan2(self.vy, self.vx)
        cos_a, sin_a = math.cos(angle), math.sin(angle)
        pts = [
            (int(x + cos_a*12), int(y + sin_a*12)),
            (int(x - sin_a*3), int(y + cos_a*3)),
            (int(x - cos_a*8), int(y - sin_a*8)),
            (int(x + sin_a*3), int(y - cos_a*3)),
        ]
        pygame.draw.polygon(surf, ORANGE, pts)
        pygame.draw.circle(surf, RED, (int(x - cos_a*8), int(y - sin_a*8)), 4)

# ─── HUD ──────────────────────────────────────────────────────────────────────
def draw_hud(surf, player, score, hi_score, wave, lives, wave_left, frame):
    # Barras
    bar = pygame.Surface((W, 46), pygame.SRCALPHA)
    bar.fill((0, 0, 0, 165)); surf.blit(bar, (0, 0))
    bar2 = pygame.Surface((W, 40), pygame.SRCALPHA)
    bar2.fill((0, 0, 0, 165)); surf.blit(bar2, (0, H-40))

    def txt(text, f, color, x, y, align='left'):
        s = f.render(text, True, color)
        if align == 'right': x -= s.get_width()
        elif align == 'center': x -= s.get_width()//2
        surf.blit(s, (x, y))

    txt('SCORE', font_sm, (68, 102, 68), 10, 6)
    txt(str(score).zfill(7), font_md, (204, 255, 204), 10, 20)
    txt(f'WAVE {wave}/6', font_sm, (68, 102, 68), W//2, 6, 'center')
    if wave_left > 0:
        txt(f'INIMIGOS: {wave_left}', font_sm, (170, 170, 170), W//2, 20, 'center')
    txt('HI-SCORE', font_sm, (68, 102, 68), W-10, 6, 'right')
    txt(str(hi_score).zfill(7), font_md, (255, 221, 85), W-10, 20, 'right')

    # HP
    txt('HP', font_sm, (68,102,68), 10, H-35)
    pygame.draw.rect(surf, (34,34,34), (10, H-22, 110, 12))
    hr = player.hp / player.max_hp
    hcol = GREEN if hr > .5 else ORANGE if hr > .25 else RED
    pygame.draw.rect(surf, hcol, (10, H-22, int(110*hr), 12))
    pygame.draw.rect(surf, GRAY, (10, H-22, 110, 12), 1)

    # Foguetes
    txt('FOGUETES', font_sm, (68,102,68), 130, H-35)
    for i in range(player.rockets):
        pygame.draw.rect(surf, ORANGE, (130+i*13, H-22, 9, 12))

    # Vidas
    txt('VIDAS', font_sm, (68,102,68), W-10, H-35, 'right')
    for i in range(lives):
        lx = W-20-i*26; ly = H-14
        pygame.draw.ellipse(surf, (51,204,51), (lx-9, ly-4, 18, 8))
        pygame.draw.polygon(surf, (34,170,34), [(lx-6,ly),(lx-14,ly-4),(lx-14,ly+4)])
        pygame.draw.line(surf, (136,238,136), (lx-6, ly-8), (lx+6, ly-8), 2)

def draw_message(surf, lines, colors=None):
    overlay = pygame.Surface((W, H), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 195))
    surf.blit(overlay, (0, 0))
    total_h = len(lines) * 60
    start_y = H//2 - total_h//2
    for i, line in enumerate(lines):
        f = font_lg if i == 0 else font_md
        col = (colors[i] if colors and i < len(colors) else WHITE)
        s = f.render(line, True, col)
        surf.blit(s, (W//2 - s.get_width()//2, start_y + i*60))

# ─── JOGO PRINCIPAL ───────────────────────────────────────────────────────────
WAVE_CONFIG = [
    {'tank':2,'jeep':3,'heli':1,'turret':0},
    {'tank':3,'jeep':3,'heli':2,'turret':1},
    {'tank':4,'jeep':4,'heli':3,'turret':1},
    {'tank':5,'jeep':4,'heli':4,'turret':2},
    {'tank':6,'jeep':5,'heli':5,'turret':3},
    {'tank':8,'jeep':6,'heli':6,'turret':3},
]

def build_queue(cfg):
    q = []
    for k, v in cfg.items():
        q += [k] * v
    random.shuffle(q)
    return q

def main():
    gs = 'menu'
    score = hi_score = 0
    wave = 1; lives = 3
    frame = 0; scroll_x = 0.0
    SCROLL_SPD = 1.2

    player = Player()
    p_bullets = []; p_rockets = []; e_bullets = []
    enemies = []; particles = []; pickups = []
    spawn_queue = []; spawn_timer = 0
    wave_left = 0; wave_complete = False; wave_clear_timer = 0

    mountains, trees, clouds = gen_bg()
    bg_surf = None

    def start_wave(w):
        nonlocal spawn_queue, spawn_timer, wave_left, wave_complete, wave_clear_timer
        cfg = WAVE_CONFIG[min(w-1, len(WAVE_CONFIG)-1)]
        spawn_queue = build_queue(cfg)
        wave_left = len(spawn_queue)
        spawn_timer = 55
        wave_complete = False
        wave_clear_timer = 0
        player.hp = min(player.max_hp, player.hp + 30)

    def start_game():
        nonlocal gs, score, wave, lives, frame, scroll_x
        nonlocal p_bullets, p_rockets, e_bullets, enemies, particles, pickups
        nonlocal spawn_queue, spawn_timer, wave_left, wave_complete, wave_clear_timer
        nonlocal mountains, trees, clouds
        gs='playing'; score=0; wave=1; lives=3; frame=0; scroll_x=0.0
        p_bullets=[]; p_rockets=[]; e_bullets=[]; enemies=[]; particles=[]; pickups=[]
        wave_complete=False; wave_clear_timer=0
        player.__init__()
        mountains, trees, clouds = gen_bg()
        start_wave(1)

    def kill_enemy(e):
        nonlocal score, hi_score, wave_left
        e.dead = True
        score += e.pts * wave
        if score > hi_score: hi_score = score
        wave_left = max(0, wave_left-1)
        ex, ey = e.x, e.y if e.kind == 'heli' else e.y - e.h//2
        explode(particles, ex, ey, True)
        play(snd_explode)
        if random.random() < 0.32:
            kinds = ['health','rocket','ammo']
            py = e.y if e.kind == 'heli' else GROUND_Y-14
            pickups.append(Pickup(ex, py, random.choice(kinds), e.kind=='heli'))

    def player_died():
        nonlocal lives, gs
        explode(particles, player.x, player.y, True)
        play(snd_explode)
        lives -= 1
        if lives <= 0:
            if score > hi_score: hi_score = score
            gs = 'over'; return
        player.hp=100; player.x=160; player.y=H//2
        player.vx=player.vy=0; player.inv=120
        p_bullets.clear(); p_rockets.clear(); e_bullets.clear()

    running = True
    while running:
        dt_keys = pygame.key.get_pressed()
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT: running = False; sys.exit()
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_ESCAPE: running = False; sys.exit()
                if ev.key == pygame.K_SPACE and gs in ('menu','over','win'):
                    start_game()

        if gs == 'playing':
            frame += 1; scroll_x += SCROLL_SPD
            player.update(dt_keys)
            # Shoot
            if dt_keys[pygame.K_SPACE] and player.scooldown == 0:
                gx = int(player.x + player.w//2 + 14); gy = int(player.y)
                p_bullets.append(Bullet(gx, gy, 13, 0, True))
                p_bullets.append(Bullet(gx, gy-6, 13, -0.3, True))
                p_bullets.append(Bullet(gx, gy+6, 13, 0.3, True))
                player.scooldown = player.srate; play(snd_shoot)
            if dt_keys[pygame.K_f] and player.rcooldown == 0 and player.rockets > 0:
                p_rockets.append(Rocket(player.x+player.w//2, player.y))
                player.rockets -= 1; player.rcooldown = 22; play(snd_rocket)

            # Update bullets
            for b in p_bullets: b.update()
            p_bullets[:] = [b for b in p_bullets if 0 < b.x < W+20]
            for b in p_bullets[:]:
                for e in enemies:
                    if e.dead: continue
                    ex = e.x-e.w//2; ey = e.y-e.h
                    if ex < b.x < ex+e.w and ey < b.y < ey+e.h:
                        e.hp -= 10; sparks(particles, int(b.x), int(b.y))
                        if e.hp <= 0: kill_enemy(e)
                        else: play(snd_hit)
                        try: p_bullets.remove(b)
                        except: pass
                        break

            for r in p_rockets: r.update(enemies)
            for r in p_rockets[:]:
                if r.x > W+20 or r.life <= 0:
                    p_rockets.remove(r); continue
                if r.y > GROUND_Y-5:
                    explode(particles, r.x, GROUND_Y, False)
                    play(snd_explode); p_rockets.remove(r); continue
                hit = False
                for e in enemies:
                    if e.dead: continue
                    if math.hypot(e.x-r.x, e.y-r.y) < 42:
                        e.hp -= 65; explode(particles, r.x, r.y, True); play(snd_explode)
                        if e.hp <= 0: kill_enemy(e)
                        hit = True; break
                if hit:
                    try: p_rockets.remove(r)
                    except: pass

            for b in e_bullets: b.update()
            e_bullets[:] = [b for b in e_bullets if -20 < b.x < W+20 and -20 < b.y < H+20]
            for b in e_bullets[:]:
                if player.inv > 0: continue
                if abs(b.x-player.x) < player.w//2-8 and abs(b.y-player.y) < player.h//2-5:
                    player.hp -= 10; player.inv = 28
                    sparks(particles, int(b.x), int(b.y)); play(snd_hit)
                    if player.hp <= 0: player_died()
                    try: e_bullets.remove(b)
                    except: pass

            # Update enemies
            for e in enemies:
                if e.dead: continue
                e.update(SCROLL_SPD)
                if e.x < -120: e.dead=True; wave_left=max(0,wave_left-1); continue
                e.sc -= 1
                if e.sc <= 0:
                    e.sc = e.sr
                    dx = player.x - e.x; dy = player.y - (e.y if e.kind=='heli' else e.y - e.h//2)
                    dist = math.hypot(dx, dy)
                    if dist < 600 and dist > 0:
                        sp = 7 if e.kind=='turret' else 5
                        e_bullets.append(Bullet(e.x, e.y if e.kind=='heli' else e.y-e.h//2, dx/dist*sp, dy/dist*sp, False))
                if player.inv <= 0:
                    ey = e.y if e.kind=='heli' else e.y - e.h//2
                    if abs(player.x-e.x) < (player.w//2+e.w//2-12) and abs(player.y-ey) < (player.h//2+e.h//2-6):
                        player.hp -= 22; player.inv = 55; e.hp -= 35; play(snd_hit)
                        if e.hp <= 0: kill_enemy(e)
                        if player.hp <= 0: player_died()
            enemies[:] = [e for e in enemies if not e.dead]

            # Pickups
            for p in pickups: p.update()
            pickups[:] = [p for p in pickups if p.life > 0 and p.x > -40]
            for p in pickups[:]:
                if abs(p.x-player.x) < 18 and abs(p.y-player.y) < 18:
                    if p.kind=='health': player.hp=min(player.max_hp,player.hp+35)
                    elif p.kind=='rocket': player.rockets=min(10,player.rockets+3)
                    else: player.srate=max(4,player.srate-1); score+=250
                    play(snd_pickup)
                    try: pickups.remove(p)
                    except: pass

            # Particles
            for pt in particles: pt.update()
            particles[:] = [p for p in particles if p.life > 0 and p.size > 0.3]

            # Wave management
            if spawn_queue and not wave_complete:
                spawn_timer -= 1
                if spawn_timer <= 0:
                    spawn_timer = 85
                    spawnEnemy(spawn_queue.pop(0), wave, enemies)
            if not spawn_queue and len(enemies)==0 and wave_left<=0 and not wave_complete:
                wave_complete=True; wave_clear_timer=0
                wave += 1
                if wave > 6:
                    if score > hi_score: hi_score=score
                    gs='win'
            if wave_complete:
                wave_clear_timer += 1
                if wave_clear_timer > 160:
                    start_wave(wave)

        # ─── RENDER ──────────────────────────────────────────────────────────
        draw_bg(screen, mountains, trees, clouds, scroll_x, frame)

        if gs in ('playing', 'over'):
            for p in pickups: p.draw(screen, frame)
            for pt in particles:
                if pt.kind == 'smoke': pt.draw(screen)
            for e in enemies: e.draw(screen, frame, int(player.x), int(player.y))
            for b in p_bullets: b.draw(screen)
            for b in e_bullets: b.draw(screen)
            for r in p_rockets: r.draw(screen)
            for pt in particles:
                if pt.kind != 'smoke': pt.draw(screen)
            player.draw(screen, frame)
            draw_hud(screen, player, score, hi_score, wave, lives, wave_left, frame)
            if wave_complete:
                wa = min(1.0, wave_clear_timer/35)
                ov = pygame.Surface((W,H), pygame.SRCALPHA)
                ov.fill((0,0,0,int(140*wa))); screen.blit(ov,(0,0))
                m1 = font_lg.render(f'WAVE {wave-1} COMPLETA!', True, (136,255,136))
                m2 = font_md.render(f'WAVE {wave} EM BREVE...', True, (221,255,221))
                screen.blit(m1, (W//2-m1.get_width()//2, H//2-30))
                screen.blit(m2, (W//2-m2.get_width()//2, H//2+26))

        if gs == 'menu':
            ov = pygame.Surface((W,H), pygame.SRCALPHA); ov.fill((0,0,0,184)); screen.blit(ov,(0,0))
            t = font_lg.render('AIR ASSAULT', True, (85,255,85))
            screen.blit(t, (W//2-t.get_width()//2, H//2-110))
            if (frame//28)%2==0:
                t2 = font_md.render('PRESSIONE ESPAÇO PARA INICIAR', True, (136,255,136))
                screen.blit(t2, (W//2-t2.get_width()//2, H//2+10))
            t3 = font_sm.render('WASD/SETAS: MOVER  |  ESPAÇO: ATIRAR  |  F: FOGUETE', True, (68,102,68))
            screen.blit(t3, (W//2-t3.get_width()//2, H//2+60))
            if hi_score > 0:
                th = font_md.render(f'RECORDE: {hi_score}', True, (255,221,85))
                screen.blit(th, (W//2-th.get_width()//2, H//2+100))

        if gs == 'over':
            ov = pygame.Surface((W,H), pygame.SRCALPHA); ov.fill((0,0,0,200)); screen.blit(ov,(0,0))
            t = font_lg.render('MISSÃO FALHOU', True, RED)
            screen.blit(t, (W//2-t.get_width()//2, H//2-80))
            t2 = font_md.render(f'PONTUAÇÃO: {score}', True, WHITE)
            screen.blit(t2, (W//2-t2.get_width()//2, H//2-10))
            if (frame//30)%2==0:
                t3 = font_md.render('ESPAÇO PARA TENTAR NOVAMENTE', True, (136,136,255))
                screen.blit(t3, (W//2-t3.get_width()//2, H//2+60))

        if gs == 'win':
            ov = pygame.Surface((W,H), pygame.SRCALPHA); ov.fill((0,0,0,200)); screen.blit(ov,(0,0))
            t = font_lg.render('MISSÃO COMPLETA!', True, YELLOW)
            screen.blit(t, (W//2-t.get_width()//2, H//2-80))
            t2 = font_md.render(f'PONTUAÇÃO FINAL: {score}', True, WHITE)
            screen.blit(t2, (W//2-t2.get_width()//2, H//2-10))
            if (frame//30)%2==0:
                t3 = font_md.render('ESPAÇO PARA JOGAR NOVAMENTE', True, (136,255,136))
                screen.blit(t3, (W//2-t3.get_width()//2, H//2+60))

        pygame.display.flip()
        clock.tick(FPS)

def spawnEnemy(kind, wave, enemies):
    enemies.append(Enemy(kind, wave))

if __name__ == '__main__':
    main()
