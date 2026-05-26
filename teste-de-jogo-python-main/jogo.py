"""
AIR ASSAULT - VERSÃO FINAL 2.5D COM PANDAS
Sem Áudio.
Execute: python jogo.py
"""
import pygame
import random
import math
import sys
import os
import pandas as pd

pygame.init()

W, H = 960, 768
MAP_WIDTH = 500
MAP_LEFT = (W - MAP_WIDTH) // 2
MAP_RIGHT = MAP_LEFT + MAP_WIDTH
FPS = 60

display_surf = pygame.Surface((W, H))
screen = pygame.display.set_mode((W, H))
pygame.display.set_caption("AIR ASSAULT - WARZONE VERTICAL")
pygame.mouse.set_visible(False)
clock = pygame.time.Clock()

# ─── SISTEMA DE PONTUAÇÃO (PANDAS) ────────────────────────────────────────────
def guardar_pontuacao(score, wave):
    ficheiro = 'historico_pontuacoes.csv'
    novo_registo = pd.DataFrame({'Pontuacao': [score], 'Wave_Alcancada': [wave]})
    try:
        if os.path.exists(ficheiro):
            df_antigo = pd.read_csv(ficheiro)
            df_atualizado = pd.concat([df_antigo, novo_registo], ignore_index=True)
            df_atualizado = df_atualizado.sort_values(by='Pontuacao', ascending=False)
            df_atualizado.to_csv(ficheiro, index=False)
        else:
            novo_registo.to_csv(ficheiro, index=False)
        print(f"Score de {score} guardado com sucesso no Excel/CSV!")
    except Exception as e:
        print(f"Erro ao guardar pontuação: {e}")

# ─── SISTEMA DE IMAGENS E GRÁFICOS VETORIAIS ──────────────────────────────────
ASSETS = {}

def desenhar_modelo_vetorial(tamanho, tipo):
    surf = pygame.Surface(tamanho, pygame.SRCALPHA)
    w, h = tamanho
    
    if tipo == 'player':
        pygame.draw.polygon(surf, (40, 50, 40), [(w/2, 0), (w*0.2, h*0.6), (w/2, h*0.8), (w*0.8, h*0.6)]) 
        pygame.draw.polygon(surf, (20, 30, 20), [(w/2, h*0.5), (0, h*0.8), (w*0.2, h*0.9), (w/2, h*0.7)]) 
        pygame.draw.polygon(surf, (20, 30, 20), [(w/2, h*0.5), (w, h*0.8), (w*0.8, h*0.9), (w/2, h*0.7)]) 
        pygame.draw.polygon(surf, (30, 40, 30), [(w*0.4, h*0.8), (w*0.4, h), (w*0.6, h), (w*0.6, h*0.8)]) 
        pygame.draw.ellipse(surf, (50, 200, 255), (w*0.4, h*0.3, w*0.2, h*0.25)) 
    elif tipo == 'tank':
        pygame.draw.rect(surf, (40, 40, 40), (0, h*0.1, w*0.2, h*0.8), border_radius=4) 
        pygame.draw.rect(surf, (40, 40, 40), (w*0.8, h*0.1, w*0.2, h*0.8), border_radius=4) 
        pygame.draw.rect(surf, (80, 90, 75), (w*0.15, h*0.15, w*0.7, h*0.7), border_radius=6) 
        pygame.draw.rect(surf, (50, 60, 45), (w*0.25, h*0.3, w*0.5, h*0.4), border_radius=3) 
    elif tipo == 'jeep':
        pygame.draw.rect(surf, (20, 20, 20), (w*0.05, h*0.1, w*0.15, h*0.25), border_radius=2) 
        pygame.draw.rect(surf, (20, 20, 20), (w*0.8, h*0.1, w*0.15, h*0.25), border_radius=2) 
        pygame.draw.rect(surf, (20, 20, 20), (w*0.05, h*0.65, w*0.15, h*0.25), border_radius=2) 
        pygame.draw.rect(surf, (20, 20, 20), (w*0.8, h*0.65, w*0.15, h*0.25), border_radius=2) 
        pygame.draw.rect(surf, (130, 110, 60), (w*0.15, 0, w*0.7, h), border_radius=5) 
        pygame.draw.rect(surf, (30, 40, 50), (w*0.25, h*0.3, w*0.5, h*0.3)) 
    elif tipo == 'turret':
        pts = [(w/2, 0), (w, h*0.25), (w, h*0.75), (w/2, h), (0, h*0.75), (0, h*0.25)]
        pygame.draw.polygon(surf, (60, 60, 60), pts)
        pygame.draw.circle(surf, (40, 40, 40), (w/2, h/2), w*0.3)
        pygame.draw.circle(surf, (255, 50, 50), (w/2, h/2), w*0.1)
    elif tipo == 'heli':
        pygame.draw.ellipse(surf, (100, 60, 60), (w*0.3, 0, w*0.4, h*0.9)) 
        pygame.draw.polygon(surf, (80, 40, 40), [(w*0.1, h*0.4), (w*0.3, h*0.3), (w*0.3, h*0.6)]) 
        pygame.draw.polygon(surf, (80, 40, 40), [(w*0.9, h*0.4), (w*0.7, h*0.3), (w*0.7, h*0.6)]) 
        pygame.draw.rect(surf, (80, 40, 40), (w*0.45, h*0.8, w*0.1, h*0.2)) 
        pygame.draw.ellipse(surf, (40, 40, 40), (w*0.4, h*0.15, w*0.2, h*0.2)) 
    elif tipo == 'drone':
        pygame.draw.polygon(surf, (200, 50, 50), [(w/2, 0), (w, h/2), (w/2, h), (0, h/2)])
        pygame.draw.circle(surf, (255, 255, 100), (w/2, h/2), w*0.2)
    elif tipo == 'boss':
        pygame.draw.polygon(surf, (70, 80, 90), [(w/2, 0), (w, h*0.4), (w*0.8, h), (w*0.2, h), (0, h*0.4)])
        pygame.draw.rect(surf, (40, 45, 50), (w*0.3, h*0.2, w*0.4, h*0.6), border_radius=10)
        pygame.draw.circle(surf, (255, 100, 50), (w/2, h*0.5), w*0.1)
        
    return surf

def carregar_imagem(nome_ficheiro, tamanho, tipo):
    if os.path.exists(nome_ficheiro):
        try:
            img = pygame.image.load(nome_ficheiro).convert_alpha()
            return pygame.transform.scale(img, tamanho)
        except:
            pass
    return desenhar_modelo_vetorial(tamanho, tipo)

def inicializar_assets():
    ASSETS['player'] = carregar_imagem('{06E0A84E-3793-4B20-BD2C-8D60FA54DCF0}.png', (64, 64), 'player')
    ASSETS['drone']  = carregar_imagem('drone.png', (45, 45), 'drone')
    ASSETS['tank']   = carregar_imagem('tank.png', (90, 65), 'tank')
    ASSETS['jeep']   = carregar_imagem('jeep.png', (70, 50), 'jeep')
    ASSETS['heli']   = carregar_imagem('heli.png', (95, 75), 'heli')
    ASSETS['turret'] = carregar_imagem('turret.png', (60, 60), 'turret')
    ASSETS['boss']   = carregar_imagem('boss.png', (250, 160), 'boss') 

inicializar_assets()

# ─── CORES E TEMAS ────────────────────────────────────────────────────────────
WHITE = (255, 255, 255); BLACK = (0, 0, 0)
GREEN = (50, 220, 50); RED = (220, 50, 50)
ORANGE = (255, 140, 0); YELLOW = (255, 255, 80)
CYAN = (50, 200, 255); BLUE = (30, 100, 200); PURPLE = (180, 50, 255)
SILVER = (192, 192, 192); GRAY = (100, 100, 100)
SKY1 = (6, 12, 28)

THEMES = {
    'forest': {'ground': (45, 85, 45), 'lines': (200, 200, 50), 'border': (25, 50, 25), 'mountains': (25, 55, 25)},
    'desert': {'ground': (194, 150, 80), 'lines': (255, 255, 255), 'border': (150, 110, 50), 'mountains': (130, 90, 40)},
    'snow': {'ground': (220, 230, 240), 'lines': (200, 200, 200), 'border': (180, 190, 200), 'mountains': (150, 160, 170)}
}

font_lg = pygame.font.SysFont("Courier New", 48, bold=True)
font_md = pygame.font.SysFont("Courier New", 22, bold=True)
font_sm = pygame.font.SysFont("Courier New", 14, bold=True)

WEAPON_STATS = {
    'mg':      {'name': '1:METRALHADORA', 'cooldown': 7,  'heat': 12, 'speed': 14, 'dmg': 20, 'color': CYAN, 'pierce': False, 'size': 3},
    'shotgun': {'name': '2:ESCOPETA',     'cooldown': 35, 'heat': 35, 'speed': 11, 'dmg': 18, 'color': YELLOW, 'pierce': False, 'size': 4},
    'plasma':  {'name': '3:PLASMA',       'cooldown': 4,  'heat': 8,  'speed': 18, 'dmg': 10, 'color': PURPLE, 'pierce': True, 'size': 3}
}

# ─── CLASSES DE PROFUNDIDADE (2.5D) ───────────────────────────────────────────
class Cloud:
    def __init__(self):
        self.x = random.randint(0, W)
        self.y = random.randint(-500, -100)
        self.speed = random.uniform(0.5, 1.8)
        self.size = random.randint(40, 120)
        
    def update(self, scroll_spd):
        self.y += scroll_spd * self.speed
        
    def draw(self, surf):
        nuvem_surf = pygame.Surface((self.size*2, self.size), pygame.SRCALPHA)
        pygame.draw.ellipse(nuvem_surf, (255, 255, 255, 40), (0, 0, self.size*2, self.size))
        surf.blit(nuvem_surf, (int(self.x), int(self.y)))

class Scenery:
    def __init__(self, theme):
        if random.choice([True, False]):
            self.x = random.randint(0, MAP_LEFT - 30)
        else:
            self.x = random.randint(MAP_RIGHT + 30, W)
        self.y = random.randint(-100, -50)
        self.theme = theme
        self.radius = random.randint(15, 40)

    def update(self, scroll_spd):
        self.y += scroll_spd
        
    def draw(self, surf):
        if self.theme == 'forest':
            pygame.draw.circle(surf, (20, 50, 20), (int(self.x), int(self.y)), self.radius)
            pygame.draw.circle(surf, (30, 70, 30), (int(self.x), int(self.y)-5), int(self.radius*0.8))
        elif self.theme == 'desert':
            pygame.draw.rect(surf, (140, 90, 40), (int(self.x-self.radius/2), int(self.y-self.radius), self.radius, self.radius*2), border_radius=5)
        else:
            pygame.draw.polygon(surf, (200, 210, 220), [(self.x, self.y-self.radius), (self.x-self.radius, self.y+self.radius), (self.x+self.radius, self.y+self.radius)])

# ─── PARTÍCULAS E ELEMENTOS BASE ──────────────────────────────────────────────
class Particle:
    def __init__(self, x, y, kind='fire', big=False):
        self.x, self.y, self.kind = x, y, kind
        ang = random.uniform(0, math.pi * 2)
        if kind == 'fire':
            spd = random.uniform(2, 8) if big else random.uniform(1, 4)
            self.vx, self.vy = math.cos(ang) * spd, math.sin(ang) * spd + 1
            self.color = random.choice([(255,255,200), (255,200,50), (255,100,0), (200,30,0)])
            self.size, self.life, self.decay = random.uniform(6, 15) if big else random.uniform(3, 8), 1.0, random.uniform(0.015, 0.03)
        elif kind == 'smoke':
            self.x += random.uniform(-10, 10)
            spd = random.uniform(0.5, 2.0)
            self.vx, self.vy = math.cos(ang) * spd, math.sin(ang) * spd + 1.5
            self.color = (random.randint(40, 80),)*3
            self.size, self.life, self.decay = random.uniform(10, 25) if big else random.uniform(6, 14), 1.0, random.uniform(0.01, 0.02)
        elif kind == 'debris':
            spd = random.uniform(3, 9)
            self.vx, self.vy = math.cos(ang) * spd, math.sin(ang) * spd + 2
            self.color = random.choice([(60,60,60), (40,40,40), (100,50,20)])
            self.size, self.life, self.decay = random.uniform(3, 6), 1.0, random.uniform(0.01, 0.02)
        else:
            spd = random.uniform(3, 7)
            self.vx, self.vy = math.cos(ang) * spd, math.sin(ang) * spd
            self.color = CYAN if big else (255, 255, 150)
            self.size, self.life, self.decay = random.uniform(1, 3), 1.0, random.uniform(0.05, 0.1)

    def update(self):
        self.x += self.vx; self.y += self.vy
        if self.kind == 'fire': self.size *= 0.94
        elif self.kind == 'smoke': self.size += 0.15
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
    for _ in range(40 if big else 15): particles.append(Particle(x, y, 'fire', big))
    for _ in range(25 if big else 8):  particles.append(Particle(x, y, 'smoke', big))
    for _ in range(15 if big else 5):  particles.append(Particle(x, y, 'debris', big))

class Background:
    def draw(self, surf, scroll_y, theme_name):
        th = THEMES[theme_name]
        surf.fill(th['mountains'])
        pygame.draw.rect(surf, th['ground'], (MAP_LEFT, 0, MAP_WIDTH, H))
        pygame.draw.rect(surf, th['border'], (MAP_LEFT - 6, 0, 6, H))
        pygame.draw.rect(surf, th['border'], (MAP_RIGHT, 0, 6, H))
        
        road_w = 140
        pygame.draw.rect(surf, (50, 50, 50), (W//2 - road_w//2, 0, road_w, H))
        pygame.draw.rect(surf, (30, 30, 30), (W//2 - road_w//2 - 4, 0, 4, H))
        pygame.draw.rect(surf, (30, 30, 30), (W//2 + road_w//2, 0, 4, H))
        
        line_height = 40; gap = 30; step = line_height + gap
        start_y = int(scroll_y) % step
        
        for y in range(start_y - step, H + step, step):
            pygame.draw.rect(surf, th['lines'], (W//2 - 3, y, 6, line_height))

class Player:
    def __init__(self):
        self.x, self.y = float(W//2), float(H - 150)
        self.vx, self.vy = 0.0, 0.0
        self.w, self.h, self.spd = 64, 64, 5.5
        self.hp = self.max_hp = 100.0
        self.level, self.xp, self.next_xp = 1, 0, 50
        self.weapons = ['mg'] 
        self.cur_wep = 'mg'   
        self.scooldown = 0
        self.rockets, self.rcooldown = 5, 0
        self.aim_angle = -math.pi/2
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
            self.vx, self.dash_cd, self.is_dashing = 18.0 if ax >= 0 else -18.0, 90, True
            for _ in range(10): particles.append(Particle(self.x, self.y, 'smoke'))

        if self.is_dashing:
            self.vx *= 0.85
            if abs(self.vx) < self.spd + 1: self.is_dashing = False
        else:
            self.vx, self.vy = (self.vx + ax*0.9) * 0.85, (self.vy + ay*0.9) * 0.85
            self.vx, self.vy = max(-self.spd, min(self.spd, self.vx)), max(-self.spd, min(self.spd, self.vy))
            
        self.x = max(MAP_LEFT + self.w//2, min(MAP_RIGHT - self.w//2, self.x + self.vx))
        self.y = max((H // 2) - 100, min(H - 80, self.y + self.vy))
        
        self.time_since_hit += 1
        if self.time_since_hit > self.regen_delay and self.hp < self.max_hp:
            self.hp = min(self.max_hp, self.hp + self.regen_rate)
            if random.random() < 0.1:
                particles.append(Particle(self.x + random.randint(-15,15), self.y + random.randint(-15,15), 'spark', big=False))
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
        x, y = int(self.x), int(self.y)
        
        # Sombra do Jogador (Efeito 2.5D)
        sombra = pygame.Surface((self.w, self.h), pygame.SRCALPHA)
        sombra.blit(ASSETS['player'], (0, 0))
        sombra.fill((0, 0, 0, 80), special_flags=pygame.BLEND_RGBA_MULT)
        surf.blit(sombra, (x - self.w//2 + 15, y - self.h//2 + 25))
        
        surf.blit(ASSETS['player'], (x - self.w//2, y - self.h//2))
        
        cx, cy = x + math.cos(self.aim_angle)*30, y + math.sin(self.aim_angle)*30
        pygame.draw.line(surf, (15, 15, 15), (x, y), (cx, cy), 5)
        
        rot_angle = (frame * 0.75) % (math.pi * 2)
        for i in range(4):
            a = rot_angle + i * (math.pi / 2)
            pygame.draw.line(surf, (220, 220, 220), (x, y), (int(x + math.cos(a) * 65), int(y + math.sin(a) * 65)), 3)
            
        pygame.draw.rect(surf, (30,30,30), (x-20, y-45, 40, 5))
        pygame.draw.rect(surf, RED if self.overheated else (YELLOW if self.heat > 70 else WHITE), (x-20, y-45, int(40 * (self.heat/self.max_heat)), 5))
        if self.shield: pygame.draw.circle(surf, (50, 200, 255), (x, y), 65, 2)

class Enemy:
    def __init__(self, kind, wave, theme, px=0, py=0):
        self.kind = kind
        self.dead = False
        self.theme = theme
        self.y = random.randint(-400, -100)
        self.x = random.randint(MAP_LEFT + 50, MAP_RIGHT - 50)
        
        m = 1 + (wave-1)*0.15
        hp_mod = 1.2 if theme == 'snow' else 1.0
        
        if kind == 'drone':
            self.w, self.h = 45, 45
            self.hp = self.max_hp = (60+wave*15) * hp_mod
            self.pts, self.sc, self.sr = 30, 0, 0 
        elif kind == 'tank':
            self.w, self.h = 90, 65
            self.hp = self.max_hp = (250+wave*30) * hp_mod
            self.sc, self.sr, self.pts = int(60+random.random()*60), 80, 100
            self.x = random.randint(MAP_LEFT + 60, MAP_RIGHT - 60)
        elif kind == 'jeep':
            self.w, self.h = 70, 50
            self.hp = self.max_hp = (100+wave*15) * hp_mod
            self.sc, self.sr, self.pts = int(40+random.random()*30), 50, 50
        elif kind == 'heli':
            self.w, self.h = 95, 75
            self.hp = self.max_hp = (200+wave*25) * hp_mod
            self.sc, self.sr, self.pts, self.rot, self.bob = int(40+random.random()*40), 60, 150, 0, random.random()*6.28
        elif kind == 'turret':
            self.w, self.h = 60, 60
            self.hp = self.max_hp = (300+wave*30) * hp_mod
            self.sc, self.sr, self.pts = int(70+random.random()*30), 100, 200
            self.x = random.choice([MAP_LEFT + 40, MAP_RIGHT - 40]) 

    def update(self, scroll_spd, px, py):
        if self.kind == 'drone':
            angle = math.atan2(py - self.y, px - self.x)
            spd = 2.8 if self.theme == 'desert' else 2.2 
            self.x += math.cos(angle) * spd
            self.y += math.sin(angle) * spd
        else:
            self.y += scroll_spd
            if self.kind == 'heli':
                self.bob += 0.04
                self.x += math.sin(self.bob) * 1.5
                self.y += 0.5 
                self.rot = (self.rot + 0.45) % (math.pi*2)

    def draw(self, surf, frame, px, py):
        x, y = int(self.x), int(self.y)
        
        # Sombra de Voo (Apenas para inimigos voadores)
        if self.kind in ['heli', 'drone']:
            sombra = pygame.Surface((self.w, self.h), pygame.SRCALPHA)
            sombra.blit(ASSETS[self.kind], (0, 0))
            sombra.fill((0, 0, 0, 80), special_flags=pygame.BLEND_RGBA_MULT)
            surf.blit(sombra, (x - self.w//2 + 15, y - self.h//2 + 25))
            
        surf.blit(ASSETS[self.kind], (x - self.w//2, y - self.h//2))

        if self.kind == 'tank' or self.kind == 'turret':
            angle = math.atan2(py - y, px - x)
            comprimento = 45 if self.kind == 'tank' else 32
            pygame.draw.line(surf, (20, 20, 20), (x, y), (x + math.cos(angle)*comprimento, y + math.sin(angle)*comprimento), 7)
            if self.kind == 'turret':
                pygame.draw.line(surf, (255, 50, 50), (x, y), (x + math.cos(angle)*250, y + math.sin(angle)*250), 1)
        
        elif self.kind == 'heli':
            for i in range(2):
                a = self.rot + i * math.pi
                pygame.draw.line(surf, (160, 160, 160), (x, y), (int(x + math.cos(a)*50), int(y + math.sin(a)*50)), 3)
            
        if self.y < -10:
            pygame.draw.polygon(surf, RED, [(x, 12), (x - 8, 24), (x + 8, 24)])

class Boss:
    def __init__(self):
        self.x, self.y, self.w, self.h = W//2, -350, 250, 160
        self.hp = self.max_hp = 10000 
        self.dead, self.phase, self.timer = False, 'enter', 0
        self.bob = 0

    def update(self, player_x, player_y, e_bullets):
        self.bob += 0.05
        self.x = W//2 + math.sin(self.bob) * 120
        
        if self.phase == 'enter':
            self.y += 1.0
            if self.y >= 160: self.phase, self.timer = 'attack', 120
        elif self.phase == 'attack':
            self.timer -= 1
            if self.timer <= 0:
                self.timer = 110
                if random.random() > 0.5:
                    for i in range(-4, 5): e_bullets.append(Bullet(self.x, self.y + 40, i*1.5, 5.5, False, 10, ORANGE, 5))
                else:
                    for _ in range(12): e_bullets.append(Bullet(self.x + random.randint(-70,70), self.y + 40, random.uniform(-1.5,1.5), 6.5, False, 10, ORANGE, 4))

    def draw(self, surf, frame):
        x, y = int(self.x), int(self.y)
        
        sombra = pygame.Surface((self.w, self.h), pygame.SRCALPHA)
        sombra.blit(ASSETS['boss'], (0, 0))
        sombra.fill((0, 0, 0, 80), special_flags=pygame.BLEND_RGBA_MULT)
        surf.blit(sombra, (x - self.w//2 + 25, y - self.h//2 + 40))
        
        surf.blit(ASSETS['boss'], (x - self.w//2, y - self.h//2))
        
        for off_x in [-75, 75]:
            rot = (frame * 0.45) % (math.pi * 2)
            pygame.draw.line(surf, WHITE, (x+off_x - math.cos(rot)*50, y - math.sin(rot)*50), (x+off_x + math.cos(rot)*50, y + math.sin(rot)*50), 4)

class Bullet:
    def __init__(self, x, y, vx, vy, friendly, damage, color=CYAN, size=3, pierce=False):
        self.x, self.y, self.vx, self.vy = float(x), float(y), vx, vy
        self.friendly, self.damage = friendly, damage
        self.color, self.size, self.pierce = color, size, pierce
        self.hit_enemies = [] 
        
    def update(self): self.x+=self.vx; self.y+=self.vy
    def draw(self, surf):
        ang = math.atan2(self.vy, self.vx)
        pygame.draw.line(surf, self.color, (int(self.x), int(self.y)), (int(self.x - math.cos(ang)*15), int(self.y - math.sin(ang)*15)), self.size)
        pygame.draw.circle(surf, WHITE, (int(self.x), int(self.y)), self.size)

class Rocket:
    def __init__(self, x, y, aim_angle):
        self.x, self.y, self.life = float(x), float(y), 150
        self.vx = math.cos(aim_angle) * 9.0
        self.vy = math.sin(aim_angle) * 9.0
        
    def update(self, enemies, boss, particles):
        self.x+=self.vx; self.y+=self.vy; self.life-=1
        particles.append(Particle(self.x, self.y, 'smoke'))
        ne, nd = None, 500
        for e in enemies + ([boss] if boss and not boss.dead else []):
            d = math.hypot(e.x-self.x, e.y-self.y)
            if d < nd: nd, ne = d, e
        if ne:
            d = math.hypot(ne.x-self.x, ne.y-self.y)
            if d>0: self.vx+= (ne.x-self.x)/d*1.2; self.vy+= (ne.y-self.y)/d*1.2
            sp = math.hypot(self.vx,self.vy)
            if sp>13: self.vx, self.vy = self.vx/sp*13, self.vy/sp*13
    def draw(self, surf):
        x, y = int(self.x), int(self.y)
        ca, sa = math.cos(math.atan2(self.vy, self.vx)), math.sin(math.atan2(self.vy, self.vx))
        pygame.draw.polygon(surf, WHITE, [(x+ca*15, y+sa*15), (x-sa*5, y+ca*5), (x-ca*10, y-sa*10), (x+sa*5, y-ca*5)])
        pygame.draw.circle(surf, ORANGE, (int(x - ca*10), int(y - sa*10)), 5)

class Pickup:
    def __init__(self, x, y, kind, from_air=False):
        self.x, self.y, self.kind, self.life, self.bob = float(x), float(y), kind, 400, 0
    def update(self, scroll_spd):
        self.y += scroll_spd
        self.life -= 1; self.bob += 0.1
    def draw(self, surf):
        x, y = int(self.x), int(self.y + math.sin(self.bob)*3)
        if self.kind == 'xp': pygame.draw.circle(surf, BLUE, (x, y), 8); pygame.draw.circle(surf, WHITE, (x, y), 10, 1) 
        elif self.kind == 'health': pygame.draw.rect(surf, GREEN, (x-10, y-4, 20, 8)); pygame.draw.rect(surf, GREEN, (x-4, y-10, 8, 20))
        elif self.kind == 'rocket': pygame.draw.rect(surf, ORANGE, (x-10, y-4, 20, 8)); pygame.draw.polygon(surf, RED, [(x+10, y-4), (x+18, y), (x+10, y+4)])
        elif self.kind == 'shield': pygame.draw.circle(surf, CYAN, (x, y), 10); pygame.draw.circle(surf, WHITE, (x, y), 14, 2)
        elif self.kind == 'weapon': pygame.draw.rect(surf, SILVER, (x-8, y-8, 16, 16)); pygame.draw.rect(surf, PURPLE, (x-8, y-8, 16, 16), 2); surf.blit(font_sm.render('W', True, BLACK), (x-4, y-7))
        if self.kind != 'xp': pygame.draw.circle(surf, WHITE, (x, y), 16, 1)

def draw_hud(surf, player, score, wave, boss, theme_name):
    bar = pygame.Surface((W, 55), pygame.SRCALPHA); bar.fill((0, 0, 0, 190)); surf.blit(bar, (0, 0))
    bar2 = pygame.Surface((W, 55), pygame.SRCALPHA); bar2.fill((0, 0, 0, 190)); surf.blit(bar2, (0, H-55))

    surf.blit(font_sm.render('SCORE', True, (100, 150, 100)), (15, 8))
    surf.blit(font_md.render(str(score).zfill(7), True, WHITE), (15, 25))
    
    map_text = "ESTRADA FLORESTA" if theme_name == 'forest' else ("VALE DESERTO" if theme_name == 'desert' else "PISTA GELADA")
    w_text = font_sm.render(f'WAVE {wave}/6 [{map_text}]' if wave <=6 else 'BOSS FINAL', True, RED if wave > 6 else (100, 150, 100))
    surf.blit(w_text, (W//2 - w_text.get_width()//2, 8))

    regen_txt = "+ REGEN + " if (player.time_since_hit > player.regen_delay and player.hp < player.max_hp) else ""
    surf.blit(font_sm.render(f'INTEGRIDADE (LVL {player.level}) {regen_txt}', True, GREEN if regen_txt else (100,150,100)), (15, H-45))
    pygame.draw.rect(surf, (40,20,20), (15, H-30, 150, 12))
    pygame.draw.rect(surf, GREEN if player.hp > (player.max_hp*0.3) else RED, (15, H-30, int(150*(max(0,player.hp)/player.max_hp)), 12))
    
    pygame.draw.rect(surf, (20,20,60), (15, H-16, 150, 4))
    pygame.draw.rect(surf, BLUE, (15, H-16, int(150*(player.xp/player.next_xp)), 4))
    
    surf.blit(font_sm.render('ARMAS SELECIONÁVEIS (1,2,3)', True, (100,150,100)), (210, H-45))
    wx = 210
    for w_id, w_info in WEAPON_STATS.items():
        if w_id in player.weapons:
            color = CYAN if player.cur_wep == w_id else GRAY
            surf.blit(font_sm.render(w_info['name'], True, color), (wx, H-30))
            wx += 120
    
    surf.blit(font_sm.render('MÍSSEIS (BOTÃO DIR.)', True, (100,150,100)), (580, H-45))
    for i in range(10): pygame.draw.rect(surf, (40,40,40), (580+i*14, H-30, 10, 12))
    for i in range(player.rockets): pygame.draw.rect(surf, ORANGE, (580+i*14, H-30, 10, 12))
    
    surf.blit(font_sm.render('DASH (SHIFT)', True, (100,150,100)), (750, H-45))
    pygame.draw.rect(surf, (40,40,40), (750, H-30, 100, 12))
    pygame.draw.rect(surf, CYAN, (750, H-30, int(100*(1-(player.dash_cd/90))), 12))
    
    if boss and not boss.dead:
        pygame.draw.rect(surf, (50,0,0), (W//2 - 200, 32, 400, 14))
        pygame.draw.rect(surf, RED, (W//2 - 200, 32, int(400*(boss.hp/boss.max_hp)), 14))

def draw_crosshair(surf, mx, my, player):
    wep = WEAPON_STATS[player.cur_wep]
    col = RED if player.overheated else wep['color']
    pygame.draw.circle(surf, col, (mx, my), 15, 1)
    pygame.draw.circle(surf, col, (mx, my), 2)
    pygame.draw.line(surf, col, (mx-18, my), (mx-4, my), 2)
    pygame.draw.line(surf, col, (mx+4, my), (mx+18, my), 2)
    pygame.draw.line(surf, col, (mx, my-18), (mx, my-4), 2)
    pygame.draw.line(surf, col, (mx, my+4), (mx, my+18), 2)

WAVE_CONFIG = [
    {'tank':3,'jeep':5,'drone':6,'heli':2,'turret':2}, 
    {'tank':5,'jeep':7,'drone':8,'heli':4,'turret':3}, 
    {'tank':7,'jeep':9,'drone':12,'heli':5,'turret':4}, 
    {'tank':9,'jeep':11,'drone':15,'heli':7,'turret':5}, 
    {'tank':12,'jeep':14,'drone':18,'heli':10,'turret':7}, 
    {'tank':0,'jeep':0,'drone':0,'heli':0,'turret':0}  
]

def get_theme_for_wave(wave):
    if wave <= 2: return 'forest'
    elif wave <= 4: return 'desert'
    else: return 'snow'

def main():
    gs, score, wave, frame, scroll_y, screen_shake = 'menu', 0, 1, 0, 0.0, 0
    cutscene_timer = 0
    player, bg = Player(), Background()
    p_bullets, p_rockets, e_bullets, enemies, particles, pickups = [], [], [], [], [], []
    
    # Listas do cenário 2.5D
    clouds = [Cloud() for _ in range(6)]
    scenery_items = []
    
    spawn_queue, spawn_timer, wave_complete, wave_clear_timer, boss = [], 0, False, 0, None
    theme_name = 'forest'
    cenario_scroll_speed = 2.0 

    def start_wave(w):
        nonlocal spawn_queue, spawn_timer, wave_complete, wave_clear_timer, boss, theme_name
        theme_name = get_theme_for_wave(w)
        if w == 6:
            boss = Boss()
        else:
            spawn_queue = []
            for k, v in WAVE_CONFIG[min(w-1, 4)].items(): spawn_queue += [k] * v
            random.shuffle(spawn_queue)
        spawn_timer, wave_complete, wave_clear_timer = 50, False, 0 

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
                    scenery_items = []
                    cutscene_timer = 0
                    player = Player(); start_wave(1)
                
                if gs == 'playing':
                    if ev.key == pygame.K_1 and 'mg' in player.weapons: player.cur_wep = 'mg'
                    if ev.key == pygame.K_2 and 'shotgun' in player.weapons: player.cur_wep = 'shotgun'
                    if ev.key == pygame.K_3 and 'plasma' in player.weapons: player.cur_wep = 'plasma'

        if gs == 'cutscene':
            frame += 1
            scroll_y += cenario_scroll_speed * 1.5 
            cutscene_timer += 1
            
            player.y -= 2.0
            player.x += (W//2 - player.x) * 0.05
            
            if frame % 5 == 0: particles.append(Particle(player.x, player.y, 'smoke'))
                
            for pt in particles: pt.update()
            particles[:] = [p for p in particles if p.life > 0 and p.size > 0.5]
            
            for c in clouds:
                c.update(cenario_scroll_speed * 1.5)
                if c.y > H + 100: c.__init__()
            
            if cutscene_timer > 300: 
                gs = 'win'
                guardar_pontuacao(score, wave) # Guarda o score de vitória!

        if gs == 'playing':
            frame += 1
            scroll_y += cenario_scroll_speed 
            screen_shake = max(0, screen_shake - 1)
            
            # --- Atualizar Cenário 2.5D ---
            if random.random() < 0.05: scenery_items.append(Scenery(theme_name))
            for s in scenery_items: s.update(cenario_scroll_speed)
            scenery_items[:] = [s for s in scenery_items if s.y < H + 100]
            
            for c in clouds:
                c.update(cenario_scroll_speed)
                if c.y > H + 100: c.__init__() # Reseta nuvem no topo
            # ------------------------------
            
            player.update(dt_keys, mx, my, particles)
            
            if mouse_btns[0] and player.scooldown <= 0 and not player.is_dashing and not player.overheated:
                wep = WEAPON_STATS[player.cur_wep]
                player.heat += wep['heat']
                player.scooldown = max(2, wep['cooldown'] - (player.level * 0.3))
                bx, by = player.x + math.cos(player.aim_angle)*25, player.y + math.sin(player.aim_angle)*25
                dmg = wep['dmg'] + (player.level * 2)
                
                if player.cur_wep == 'mg':
                    p_bullets.append(Bullet(bx, by, math.cos(player.aim_angle)*wep['speed'], math.sin(player.aim_angle)*wep['speed'], True, dmg, wep['color'], wep['size']))
                elif player.cur_wep == 'shotgun':
                    for ang_off in [-0.2, -0.1, 0, 0.1, 0.2]:
                        a = player.aim_angle + ang_off
                        p_bullets.append(Bullet(bx, by, math.cos(a)*wep['speed'], math.sin(a)*wep['speed'], True, dmg, wep['color'], wep['size']))
                elif player.cur_wep == 'plasma':
                    bx1, by1 = bx + math.cos(player.aim_angle - 1.57)*8, by + math.sin(player.aim_angle - 1.57)*8
                    bx2, by2 = bx + math.cos(player.aim_angle + 1.57)*8, by + math.sin(player.aim_angle + 1.57)*8
                    p_bullets.append(Bullet(bx1, by1, math.cos(player.aim_angle)*wep['speed'], math.sin(player.aim_angle)*wep['speed'], True, dmg, wep['color'], wep['size'], wep['pierce']))
                    p_bullets.append(Bullet(bx2, by2, math.cos(player.aim_angle)*wep['speed'], math.sin(player.aim_angle)*wep['speed'], True, dmg, wep['color'], wep['size'], wep['pierce']))
                
            if mouse_btns[2] and player.rcooldown <= 0 and player.rockets > 0:
                p_rockets.append(Rocket(player.x, player.y, player.aim_angle)); player.rockets -= 1; player.rcooldown = 25; screen_shake = max(screen_shake, 3)

            for b in p_bullets: b.update()
            p_bullets[:] = [b for b in p_bullets if 0 < b.x <= W and 0 < b.y < H] 
            
            for b in p_bullets[:]:
                hit_something = False
                for e in enemies:
                    if not e.dead and abs(b.x - e.x) < e.w//2 and abs(b.y - e.y) < e.h//2:
                        e.hp -= b.damage; particles.append(Particle(b.x, b.y, 'spark')); hit_something = True
                        b.hit_enemies.append(e)
                        if e.hp <= 0:
                            e.dead = True; score += e.pts; screen_shake = max(screen_shake, 6); explode(particles, e.x, e.y, True)
                            pickups.append(Pickup(e.x, e.y, 'xp')) 
                            
                            drop_chance = random.random()
                            if e.kind in ['heli', 'tank'] and drop_chance < 0.20: pickups.append(Pickup(e.x, e.y, 'weapon'))
                            elif drop_chance < 0.40: pickups.append(Pickup(e.x, e.y, random.choice(['health','rocket','shield'])))
                
                if boss and not boss.dead and boss not in b.hit_enemies and abs(b.x-boss.x) < boss.w//2 and abs(b.y-boss.y) < boss.h//2:
                    boss.hp -= b.damage; particles.append(Particle(b.x, b.y, 'spark')); hit_something = True
                    b.hit_enemies.append(boss)
                    if boss.hp <= 0: 
                        boss.dead = True; score += 5000; wave_complete = True; wave += 1 
                        explode(particles, boss.x, boss.y, True); screen_shake = 30
                
                if hit_something and not b.pierce:
                    if b in p_bullets: p_bullets.remove(b)

            for r in p_rockets: r.update(enemies, boss, particles)
            for r in p_rockets[:]:
                if r.x > W+50 or r.x < -50 or r.y < -50 or r.y > H+50 or r.life <= 0: 
                    if r in p_rockets: p_rockets.remove(r)
                    continue
                hit = False
                for e in enemies + ([boss] if boss and not boss.dead else []):
                    if math.hypot(e.x-r.x, e.y-r.y) < (70 if isinstance(e, Boss) else 45):
                        e.hp -= 160 + (player.level*10); explode(particles, r.x, r.y, True); screen_shake = max(screen_shake, 12); hit = True
                        if e.hp <= 0:
                            e.dead = True; score += 5000 if isinstance(e, Boss) else getattr(e, 'pts', 0)
                            if isinstance(e, Boss): wave_complete = True; wave += 1
                        break
                if hit and r in p_rockets: p_rockets.remove(r)

            for b in e_bullets: b.update()
            e_bullets[:] = [b for b in e_bullets if -50 < b.x < W+50 and -50 < b.y < H+50]
            for b in e_bullets[:]:
                if player.inv > 0 or player.is_dashing: continue
                if abs(b.x-player.x) < player.w//2-8 and abs(b.y-player.y) < player.h//2-8:
                    screen_shake = player.take_damage(15, screen_shake)
                    explode(particles, b.x, b.y, False)
                    if player.hp <= 0: 
                        gs = 'over'
                        explode(particles, player.x, player.y, True)
                        screen_shake = 20
                        guardar_pontuacao(score, wave) # Guarda o score de derrota!
                    if b in e_bullets: e_bullets.remove(b)

            for e in enemies:
                e.update(cenario_scroll_speed, player.x, player.y) 
                if e.y > H + 80: e.dead=True; continue
                
                if e.kind != 'drone':
                    e.sc -= 1
                    if e.sc <= 0 and 0 < e.y < H:
                        e.sc = e.sr
                        dist = math.hypot(player.x - e.x, player.y - e.y)
                        if dist < 650:
                            if e.kind == 'heli':
                                for ang in [-0.2, 0, 0.2]: e_bullets.append(Bullet(e.x, e.y, (player.x-e.x)*math.cos(ang) - (player.y-e.y)*math.sin(ang)/dist*3.5, (player.x-e.x)*math.sin(ang) + (player.y-e.y)*math.cos(ang)/dist*3.5, False, 15, ORANGE))
                            else: e_bullets.append(Bullet(e.x, e.y, (player.x-e.x)/dist*3.5, (player.y-e.y)/dist*3.5, False, 15, ORANGE)) 
                
                if player.inv <= 0 and not player.is_dashing and abs(player.x-e.x) < (player.w//2+e.w//2-10) and abs(player.y-e.y) < (player.h//2+e.h//2-10):
                    if player.shield: 
                        player.shield = False; player.inv = 60
                        if e.kind == 'drone': e.dead = True; explode(particles, e.x, e.y, True)
                    else: 
                        if e.kind == 'drone':
                            screen_shake = player.take_damage(35, screen_shake) 
                            e.dead = True; explode(particles, e.x, e.y, True)
                        else:
                            screen_shake = player.take_damage(25, screen_shake)
                            e.hp -= 40
                            if e.hp <= 0: e.dead = True; explode(particles, e.x, e.y, True)
                        if player.hp <= 0: 
                            gs = 'over'
                            explode(particles, player.x, player.y, True)
                            screen_shake = 20
                            guardar_pontuacao(score, wave) # Guarda o score de colisão!
            
            enemies[:] = [e for e in enemies if not e.dead]
            if boss and not boss.dead: boss.update(player.x, player.y, e_bullets)

            for p in pickups: p.update(cenario_scroll_speed) 
            pickups[:] = [p for p in pickups if p.life > 0 and p.y < H + 50]
            for p in pickups[:]:
                if abs(p.x-player.x) < 35 and abs(p.y-player.y) < 35:
                    if p.kind == 'xp': player.add_xp(10, particles)
                    elif p.kind == 'health': player.hp=min(player.max_hp,player.hp+50)
                    elif p.kind == 'rocket': player.rockets=min(15,player.rockets+5)
                    elif p.kind == 'shield': player.shield = True
                    elif p.kind == 'weapon': player.unlock_weapon(particles)
                    if p in pickups: pickups.remove(p)

            for pt in particles: pt.update()
            particles[:] = [p for p in particles if p.life > 0 and p.size > 0.5]

            if spawn_queue and not wave_complete:
                spawn_timer -= 1
                if spawn_timer <= 0: 
                    spawn_timer = max(35, 80 - (wave * 6)) 
                    enemies.append(Enemy(spawn_queue.pop(0), wave, theme_name, player.x, player.y))
                    
            if not spawn_queue and len(enemies) == 0 and not wave_complete and wave < 6:
                wave_complete = True; wave_clear_timer = 0; wave += 1
                
            if wave_complete:
                wave_clear_timer += 1
                if wave_clear_timer > 200: 
                    if wave > 6: 
                        gs = 'cutscene'
                        cutscene_timer = 0
                        wave_complete = False 
                    else: 
                        start_wave(wave)

        # ─── RENDERING ──────────────────────────────────────────────────────────
        if gs != 'menu': bg.draw(display_surf, scroll_y, theme_name)
        else: display_surf.fill(SKY1)

        if gs in ('playing', 'over', 'cutscene'):
            # Desenha cenário nas laterais
            for s in scenery_items: s.draw(display_surf)
            
            for p in pickups: p.draw(display_surf)
            for pt in particles:
                if pt.kind == 'smoke': pt.draw(display_surf)
            for e in enemies: e.draw(display_surf, frame, int(player.x), int(player.y))
            if boss and not boss.dead: boss.draw(display_surf, frame)
            for b in p_bullets + e_bullets: b.draw(display_surf)
            for r in p_rockets: r.draw(display_surf)
            for pt in particles:
                if pt.kind != 'smoke': pt.draw(display_surf)
            
            if gs in ('playing', 'cutscene'): player.draw(display_surf, frame)
            
            # Desenha nuvens de Parallax a passar por cima de tudo
            for c in clouds: c.draw(display_surf)
            
            if gs == 'playing':
                draw_hud(display_surf, player, score, wave, boss, theme_name)
                draw_crosshair(display_surf, mx, my, player)
            
            if gs == 'cutscene':
                if cutscene_timer > 60:
                    txt = font_lg.render('AMEAÇA ELIMINADA', True, YELLOW)
                    display_surf.blit(txt, (W//2 - txt.get_width()//2, H//3))
                if cutscene_timer > 140:
                    txt2 = font_md.render('RETORNANDO À BASE...', True, WHITE)
                    display_surf.blit(txt2, (W//2 - txt2.get_width()//2, H//2))

        if gs == 'menu':
            display_surf.blit(font_lg.render('AIR ASSAULT 2.5D', True, CYAN), (W//2-220, H//2-110))
            if (frame//30)%2==0: display_surf.blit(font_md.render('PRESSIONE ESPAÇO PARA INICIAR', True, WHITE), (W//2-180, H//2+10))
            display_surf.blit(font_sm.render('WASD/SETAS: MOVER | MOUSE: MIRAR E ATIRAR | 1,2,3: ARMAS', True, GRAY), (W//2-230, H//2+70))

        elif gs == 'over':
            display_surf.blit(font_lg.render('MISSÃO FALHOU', True, RED), (W//2-160, H//2-80))
            display_surf.blit(font_md.render(f'PONTUAÇÃO FINAL: {score}', True, WHITE), (W//2-130, H//2-10))
            display_surf.blit(font_sm.render('PRESSIONE ESPAÇO PARA REINICIAR', True, GRAY), (W//2-140, H//2+50))

        elif gs == 'win':
            display_surf.blit(font_lg.render('VITÓRIA SUPREMA!', True, YELLOW), (W//2-200, H//2-80))
            display_surf.blit(font_md.render(f'PONTUAÇÃO FINAL: {score}', True, WHITE), (W//2-130, H//2-10))
            display_surf.blit(font_sm.render('PRESSIONE ESPAÇO PARA JOGAR DE NOVO', True, GRAY), (W//2-150, H//2+50))

        screen.blit(display_surf, (random.randint(-screen_shake, screen_shake), random.randint(-screen_shake, screen_shake)))
        pygame.display.flip()
        clock.tick(FPS)

if __name__ == '__main__':
    main()