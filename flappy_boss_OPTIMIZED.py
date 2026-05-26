import pygame
import sys
import random
import math
import os
import array
import time

pygame.init()

# ===== SKILL ICON FALLBACK =====
fireball_icon = None
thunder_icon = None
heal_icon = None
ultimate_icon = None
pygame.mixer.init(frequency=22050, size=-16, channels=1)

# =================================================================
# ⚙ CAU HINH ADMIN BAN DAU
QUYEN_ADMIN = 1
# =================================================================

# ================= SHOP & SKILL SYSTEM =================
SKINS = {
    "Classic": {"price": 0, "tier": "C", "hp": 0, "damage": 0, "shield": 0, "skill_count":1, "color":(247,216,52)},
    "Shadow": {"price": 150, "tier": "B", "hp": 10, "damage": 2, "shield": 1, "skill_count":2, "color":(80,80,80)},
    "Thunder": {"price": 400, "tier": "A", "hp": 20, "damage": 4, "shield": 2, "skill_count":3, "color":(255,255,0)},
    "Galaxy": {"price": 900, "tier": "S", "hp": 40, "damage": 7, "shield": 4, "skill_count":4, "color":(120,0,255)},
    "Dragon God": {"price": 2000, "tier": "SS", "hp": 60, "damage": 10, "shield": 6, "skill_count":4, "color":(255,50,0)},
    "Phoenix": {"price": 5000, "tier": "GOD", "hp": 100, "damage": 18, "shield": 10, "skill_count":4, "color":(255,80,0)},
    "Void King": {"price": 9000, "tier": "MYTHIC", "hp": 160, "damage": 25, "shield": 15, "skill_count":4, "color":(0,255,255)},
}

MISSIONS = [
    {"name": "Vuot 10 diem", "goal": 10, "reward": 100},
    {"name": "Vuot 30 diem", "goal": 30, "reward": 250},
    {"name": "Vuot 50 diem", "goal": 50, "reward": 500},
    {"name": "Ha boss lan 1", "goal": 1000, "reward": 1500},
    {"name": "Kiem 5000 coin", "goal": 5000, "reward": 2500},
]

# =======================================================

# Cau hinh man hinh
SCREEN_WIDTH = 450
SCREEN_HEIGHT = 800
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Flappy Bird: Super Expansion v3")
clock = pygame.time.Clock()
FPS = 50

# --- HE THONG LUU TRU VA DUONG DAN AN TOAN TREN ANDROID ---
base_dir = os.path.expanduser("~")
SCORE_FILE = os.path.join(base_dir, "flappy_highscore_v3.txt")
COIN_FILE = os.path.join(base_dir, "flappy_coins_v3.txt")
MISSION_RESET_FILE = os.path.join(base_dir, "mission_reset_time.txt")

# Khoi tao cac file neu chua co
if not os.path.exists(SCORE_FILE):
    with open(SCORE_FILE, "w") as f: f.write("0")
if not os.path.exists(COIN_FILE):
    with open(COIN_FILE, "w") as f: f.write("999999" if QUYEN_ADMIN == 1 else "0")

def load_high_score():
    try:
        with open(SCORE_FILE, "r") as f: return int(f.read().strip())
    except: return 0

def save_high_score(score):
    try:
        if score > load_high_score():
            with open(SCORE_FILE, "w") as f: f.write(str(score))
    except: pass

def load_last_reset():
    try:
        with open(MISSION_RESET_FILE, "r") as f:
            return float(f.read().strip())
    except:
        return time.time()

def save_last_reset():
    try:
        with open(MISSION_RESET_FILE, "w") as f:
            f.write(str(time.time()))
    except:
        pass

def load_coins():
    try:
        with open(COIN_FILE, "r") as f:
            return int(f.read().strip())
    except:
        return 999999 if QUYEN_ADMIN == 1 else 0

def save_coins(coins):
    try:
        with open(COIN_FILE, "w") as f:
            f.write(str(coins))
    except:
        pass

# --- QUET VA NAP ANH BOSS DU PHONG ---
boss_sprite = None
paths_to_check = [os.path.dirname(os.path.abspath(__file__)), "/sdcard/Download", "/storage/emulated/0/Download", base_dir, "."]
for folder in paths_to_check:
    img_path = os.path.join(folder, "boss.png")
    if os.path.exists(img_path):
        try:
            boss_sprite = pygame.transform.scale(pygame.image.load(img_path).convert_alpha(), (130, 130))
            break
        except: pass

# --- CAU HINH HE THONG AM THANH ---
volume_effects = 0.5
volume_music = 0.5
sound_muted = False

def generate_beep_sound(frequency, duration, volume=0.5):
    try:
        sample_rate = 22050
        num_samples = int(sample_rate * duration)
        buf = array.array('h', [0] * num_samples)
        for i in range(num_samples):
            t = float(i) / sample_rate
            buf[i] = int(volume * 32767.0 * math.sin(2.0 * math.pi * frequency * t))
        return pygame.mixer.Sound(buf)
    except: return None

sound_flap = generate_beep_sound(587.33, 0.08, 0.3)
sound_score = generate_beep_sound(880.00, 0.15, 0.4)
sound_hit = generate_beep_sound(150.00, 0.25, 0.6)
sound_laser = generate_beep_sound(400.00, 0.1, 0.2)
sound_powerup = generate_beep_sound(783.99, 0.2, 0.4)

def play_sound(sound):
    if sound and not sound_muted:
        sound.set_volume(volume_effects)
        sound.play()


# ===== ENHANCED AUDIO SYSTEM =====
def generate_wave_sound(frequency=440, duration=0.2, volume=0.5, wave_type="sine"):
    try:
        sample_rate = 22050
        num_samples = int(sample_rate * duration)
        buf = array.array('h', [0] * num_samples)

        for i in range(num_samples):
            t = float(i) / sample_rate

            if wave_type == "square":
                wave = 1.0 if math.sin(2 * math.pi * frequency * t) > 0 else -1.0
            elif wave_type == "saw":
                wave = 2 * ((t * frequency) % 1.0) - 1.0
            else:
                wave = math.sin(2 * math.pi * frequency * t)

            envelope = max(0.0, 1.0 - (i / num_samples))
            buf[i] = int(volume * 32767 * wave * envelope)

        return pygame.mixer.Sound(buffer=buf)
    except:
        return None

sound_skill_fire = generate_wave_sound(920, 0.18, 0.5, "saw")
sound_skill_thunder = generate_wave_sound(140, 0.35, 0.7, "square")
sound_skill_heal = generate_wave_sound(640, 0.30, 0.5, "sine")
sound_skill_ultimate = generate_wave_sound(80, 0.65, 0.9, "square")
sound_boss_warning = generate_wave_sound(220, 0.40, 0.7, "saw")
sound_boss_death = generate_wave_sound(60, 1.0, 0.9, "square")

# Bang Mau 
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BIRD_COLOR = (247, 216, 52)
SKIN_COLOR = (255, 69, 0) # Mau dai bang lua khi hack code
PIPE_COLOR = (115, 191, 46)
GROUND_COLOR = (222, 216, 149)
GOLD_COLOR = (255, 215, 0)
RED_COLOR = (220, 53, 69)
GREEN_COLOR = (40, 167, 69)
BANANA_COLOR = (255, 230, 30)
CYAN_COLOR = (0, 255, 255)
GRAY = (100, 100, 100)
LIGHT_GRAY = (200, 200, 200)

COLOR_DAY_SKY = (113, 197, 207)

# Cau hinh can bang game ban dau
DEFAULT_GRAVITY = 0.3
DEFAULT_FLAP_STRENGTH = -7.5
DEFAULT_PIPE_SPEED = 2.8
DEFAULT_PIPE_GAP = 240
PIPE_FREQUENCY = 1900

font_title = pygame.font.SysFont(None, 50)
font_menu = pygame.font.SysFont(None, 35)
font_msg = pygame.font.SysFont(None, 26)
font_admin = pygame.font.SysFont(None, 20)
font_score = pygame.font.SysFont(None, 45)

def draw_text(surface, text, font, color, center_pos):
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect(center=center_pos)
    surface.blit(text_surface, text_rect)

class Particle:
    """Hieu ung muoi lua phat ra tu duoi vu khi chuoi"""
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.vx = random.uniform(-3, -1)
        self.vy = random.uniform(-1, 1)
        self.radius = random.randint(3, 6)
        self.color = random.choice([RED_COLOR, GOLD_COLOR, BANANA_COLOR])
        self.lifetime = 15

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.lifetime -= 1

    def draw(self, surface):
        if self.lifetime > 0:
            pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.radius)

class Cloud:
    def __init__(self, is_random_x=False):
        self.x = random.randint(0, SCREEN_WIDTH) if is_random_x else SCREEN_WIDTH + random.randint(10, 100)
        self.y = random.randint(50, 250)
        self.speed = random.uniform(0.3, 0.8)
        self.size = random.randint(30, 50)

    def update(self): self.x -= self.speed
    def draw(self, surface):
        pygame.draw.circle(surface, (240, 245, 250), (int(self.x), int(self.y)), self.size)
        pygame.draw.circle(surface, (240, 245, 250), (int(self.x + self.size*0.6), int(self.y - self.size*0.2)), int(self.size*0.8))

class Bird:
    def __init__(self):
        self.x = 100
        self.y = SCREEN_HEIGHT // 2
        self.radius = 18
        self.velocity = 0
        self.wing_flap = 0
        self.shield_timer = 0
        self.power_timer = 0
        self.max_hp = 25
        self.hp = 25

    def update(self, gravity):
        self.velocity += gravity
        self.y += self.velocity
        self.wing_flap += 0.25
        if self.y < self.radius:
            self.y = self.radius
            self.velocity = 0
        if self.shield_timer > 0: self.shield_timer -= 1
        if self.power_timer > 0: self.power_timer -= 1

    def flap(self, strength):
        self.velocity = strength
        play_sound(sound_flap)

    def draw(self, surface, use_admin_skin=False):
        wing_offset = int(math.sin(self.wing_flap * 5) * 5)
        if self.shield_timer > 0:
            pygame.draw.circle(surface, CYAN_COLOR, (self.x, int(self.y)), self.radius + 8, width=3)
            
        skin_data = SKINS.get(game.skin_equipped, SKINS["Classic"])
        color = skin_data.get("color", BIRD_COLOR)
        pygame.draw.circle(surface, color, (self.x, int(self.y)), self.radius)
        pygame.draw.ellipse(surface, (200, 160, 20) if not use_admin_skin else (150, 0, 0), (self.x - 14, int(self.y) - 6 + wing_offset, 18, 14))
        pygame.draw.circle(surface, WHITE, (self.x + 9, int(self.y) - 6), 6)
        pygame.draw.circle(surface, BLACK, (self.x + 11, int(self.y) - 6), 3)
        pygame.draw.polygon(surface, (247, 131, 32), [(self.x + 16, int(self.y) - 2), (self.x + 28, int(self.y) + 3), (self.x + 16, int(self.y) + 8)])

        # Ve thanh HP nho tren dau con chim
        hp_bar_width = 40
        hp_bar_height = 6
        hp_pct = max(0, self.hp / self.max_hp)
        pygame.draw.rect(surface, RED_COLOR, (self.x - 20, self.y - 30, hp_bar_width, hp_bar_height))
        pygame.draw.rect(surface, GREEN_COLOR, (self.x - 20, self.y - 30, int(hp_bar_width * hp_pct), hp_bar_height))

    def get_rect(self): return pygame.Rect(self.x - self.radius, self.y - self.radius, self.radius * 2, self.radius * 2)

class Pipe:
    def __init__(self, x, gap):
        self.x = x
        self.width = 80
        self.gap = gap
        self.top_height = random.randint(120, SCREEN_HEIGHT - self.gap - 220)
        self.bottom_y = self.top_height + self.gap
        self.bottom_height = SCREEN_HEIGHT - self.bottom_y - 50
        self.passed = False

    def update(self, speed): self.x -= speed
    def draw(self, surface):
        top_rect = (self.x, 0, self.width, self.top_height)
        bottom_rect = (self.x, self.bottom_y, self.width, self.bottom_height)

        pygame.draw.rect(surface, PIPE_COLOR, top_rect, border_radius=8)
        pygame.draw.rect(surface, PIPE_COLOR, bottom_rect, border_radius=8)

        for i in range(0, self.top_height, 24):
            pygame.draw.line(surface, (160,255,120), (self.x+5, i), (self.x+self.width-5, i), 2)

        for i in range(self.bottom_y, SCREEN_HEIGHT-50, 24):
            pygame.draw.line(surface, (160,255,120), (self.x+5, i), (self.x+self.width-5, i), 2)

        pygame.draw.rect(surface, GOLD_COLOR, (self.x-3, self.top_height-18, self.width+6, 18), border_radius=5)
        pygame.draw.rect(surface, GOLD_COLOR, (self.x-3, self.bottom_y, self.width+6, 18), border_radius=5)
    def is_offscreen(self): return self.x + self.width < 0
    def collide(self, bird_rect):
        top_rect = pygame.Rect(self.x, 0, self.width, self.top_height)
        bottom_rect = pygame.Rect(self.x, self.bottom_y, self.width, self.bottom_height)
        return bird_rect.colliderect(top_rect) or bird_rect.colliderect(bottom_rect)

class BananaBullet:
    """Vu khi dan chuoi than cong co hieu ung xoay goc do hoa"""
    def __init__(self, x, y, is_super=False):
        self.x = x
        self.y = y
        self.speed = 9 if is_super else 6.5
        self.angle = 0
        self.is_super = is_super
        self.damage = 5 if is_super else 2

    def update(self):
        self.x += self.speed
        self.angle = (self.angle + 12) % 360

    def draw(self, surface):
        # Thiet ke do hoa hinh luoi liem chuoi chien dau xoay tron
        color = GOLD_COLOR if self.is_super else BANANA_COLOR
        w, h = (36, 18) if self.is_super else (24, 12)
        bullet_surf = pygame.Surface((w, h), pygame.SRCALPHA)
        pygame.draw.ellipse(bullet_surf, color, (0, 0, w, h))
        pygame.draw.ellipse(bullet_surf, (0, 0, 0, 0), (0, -4, w, h)) # Cat ranh khuyet hinh chuoi
        rotated_surf = pygame.transform.rotate(bullet_surf, self.angle)
        new_rect = rotated_surf.get_rect(center=(int(self.x), int(self.y)))
        surface.blit(rotated_surf, new_rect.topleft)

    def get_rect(self): return pygame.Rect(self.x - 12, self.y - 6, 24, 12)

class Item:
    def __init__(self, x, y, type_name):
        self.x = x
        self.y = y
        self.type = type_name
        self.size = 28
        self.speed_x = -2.5

    def update(self): self.x += self.speed_x
    def draw(self, surface):
        cx, cy = int(self.x), int(self.y)

        # HEAL ITEM ❤️
        if self.type == "HEAL":
            pygame.draw.circle(surface, (255, 80, 80), (cx, cy), 18)
            pygame.draw.circle(surface, WHITE, (cx, cy), 18, width=3)

            pygame.draw.rect(surface, WHITE, (cx - 4, cy - 10, 8, 20), border_radius=2)
            pygame.draw.rect(surface, WHITE, (cx - 10, cy - 4, 20, 8), border_radius=2)

        # SHIELD ITEM 🛡
        elif self.type == "SHIELD":
            pygame.draw.circle(surface, CYAN_COLOR, (cx, cy), 18)
            pygame.draw.circle(surface, WHITE, (cx, cy), 18, width=3)

            shield_points = [
                (cx, cy - 12),
                (cx - 10, cy - 2),
                (cx - 6, cy + 12),
                (cx, cy + 16),
                (cx + 6, cy + 12),
                (cx + 10, cy - 2),
            ]

            pygame.draw.polygon(surface, WHITE, shield_points, width=3)

        # POWER ITEM ⚡
        else:
            pygame.draw.circle(surface, (255, 220, 0), (cx, cy), 18)
            pygame.draw.circle(surface, WHITE, (cx, cy), 18, width=3)

            lightning = [
                (cx + 2, cy - 12),
                (cx - 6, cy + 1),
                (cx + 1, cy + 1),
                (cx - 2, cy + 12),
                (cx + 8, cy - 2),
                (cx + 1, cy - 2)
            ]

            pygame.draw.polygon(surface, WHITE, lightning)

    def get_rect(self): return pygame.Rect(self.x - self.size//2, self.y - self.size//2, self.size, self.size)

class Boss:
    def __init__(self):
        self.width = 130
        self.height = 130
        self.x = SCREEN_WIDTH + 50
        self.y = SCREEN_HEIGHT // 3 + 20
        self.version = 1
        self.max_hp = 300
        self.hp = 300
        self.speed_y = 2
        self.state = "ENTER"
        self.last_attack_time = pygame.time.get_ticks()
        self.attack_cooldown = 1500

    def update(self):
        if self.state == "ENTER":
            if self.x > SCREEN_WIDTH - 160: self.x -= 2
            else: self.state = "BATTLE"
        elif self.state == "BATTLE":
            self.y += self.speed_y
            if self.y <= 130 or self.y >= SCREEN_HEIGHT - 220:
                self.speed_y *= -1

    def draw(self, surface):
        aura_color = (180,50,255) if self.version == 1 else (255,40,40)

        for radius in range(75, 95, 10):
            pygame.draw.circle(surface, aura_color, (int(self.x + 65), int(self.y + 65)), radius, 1)

        if boss_sprite:
            surface.blit(boss_sprite, (self.x, self.y))
        else:
            color = (150, 50, 200) if self.version == 1 else (255, 0, 50)
            pygame.draw.rect(surface, color, (self.x, self.y, self.width, self.height), border_radius=18)

            pygame.draw.circle(surface, WHITE, (self.x + 35, self.y + 40), 12)
            pygame.draw.circle(surface, WHITE, (self.x + 95, self.y + 40), 12)

            pygame.draw.circle(surface, RED_COLOR, (self.x + 35, self.y + 40), 5)
            pygame.draw.circle(surface, RED_COLOR, (self.x + 95, self.y + 40), 5)

            pygame.draw.arc(surface, GOLD_COLOR, (self.x+25, self.y+55, 70, 40), 0, math.pi, 4)

        pygame.draw.rect(surface, aura_color, (self.x - 5, self.y - 5, self.width + 10, self.height + 10), width=3, border_radius=20)

    def get_rect(self): return pygame.Rect(self.x, self.y, self.width, self.height)

class BossBullet:
    def __init__(self, x, y, is_minion=False):
        self.x = x
        self.y = y
        self.is_minion = is_minion
        self.radius = 10 if not is_minion else 15
        self.speed = 5.5 if not is_minion else 7

    def update(self): self.x -= self.speed
    def draw(self, surface):
        if not self.is_minion:
            pygame.draw.circle(surface, RED_COLOR, (int(self.x), int(self.y)), self.radius)
            pygame.draw.circle(surface, GOLD_COLOR, (int(self.x), int(self.y)), self.radius - 4)
        else:
            pygame.draw.polygon(surface, (230, 50, 50), [(self.x, self.y-12), (self.x-22, self.y), (self.x, self.y+12)])
    def get_rect(self): return pygame.Rect(self.x - self.radius, self.y - self.radius, self.radius * 2, self.radius * 2)

class Game:
    def __init__(self):
        self.is_admin = (QUYEN_ADMIN == 1)
        self.high_score = load_high_score()

        # Coin mac dinh theo quyen admin
        if self.is_admin:
            self.coins = 999999
        else:
            self.coins = 0

        save_coins(self.coins)
        self.unlocked_skins = ["Classic"]
        self.selected_skin = "Classic"
        self.skin_equipped = "Classic"
        self.skill_cooldown = 0
        self.skill_enabled = False
        self.skill_slots = [
            {"name":"Fire Ball","cd":0,"max_cd":180},
            {"name":"Thunder","cd":0,"max_cd":300},
            {"name":"Heal","cd":0,"max_cd":420},
            {"name":"Ultimate","cd":0,"max_cd":600},
        ]
        self.skill_buttons = []
        self.no_skill_cooldown = False
        self.game_state = "MENU" # MENU, PLAYING, SETTINGS, SHOP, MISSIONS, GAMEOVER, WIN
        self.clouds = [Cloud(is_random_x=True) for _ in range(5)]
        
        # Flag dieu kien loai bo Boss vinh vien sau thang cuoc
        self.boss_disabled_forever = False
        self.reset_game_data()

    def reset_game_data(self, keep_score=False):
        self.bird = Bird()
        skin_data = SKINS.get(self.skin_equipped, SKINS["Classic"])
        self.bird.max_hp += skin_data["hp"]
        self.bird.hp = self.bird.max_hp
        if not keep_score:
            self.score = 0
        self.pipes = []
        self.bananas = []
        self.boss_bullets = []
        self.items = []
        self.particles = []
        self.skill_effects = []
        self.boss = None
        self.laser_active = False
        self.last_pipe_time = pygame.time.get_ticks()
        self.last_shoot_time = 0
        
        self.admin_mode = False
        self.god_mode = False
        self.custom_speed = DEFAULT_PIPE_SPEED
        self.custom_gap = DEFAULT_PIPE_GAP
        self.admin_btn_rect = pygame.Rect(15, 15, 45, 45)

    def trigger_boss_battle(self):
        if not self.boss_disabled_forever:
            self.pipes.clear()

            # TAO BOSS
            self.boss = Boss()

            # BAT SKILL
            self.skill_enabled = True

            # RESET CD
            for sk in self.skill_slots:
                sk["cd"] = 0
    def use_skill(self, idx):
        if idx >= len(self.skill_slots):
            return

        skill_count = SKINS.get(self.skin_equipped, SKINS["Classic"]).get("skill_count", 1)
        if idx >= skill_count:
            return

        sk = self.skill_slots[idx]

        if sk["cd"] > 0:
            return

        boss_exists = self.boss is not None

        # Skill 1 - Flame Burst
        if idx == 0:
            play_sound(sound_skill_fire)

            for offset in [-35, -15, 15, 35]:
                self.bananas.append(BananaBullet(self.bird.x + 20, self.bird.y + offset, is_super=True))

            self.skill_effects.append({
                "type": "FIRE",
                "x": self.bird.x + 120,
                "y": self.bird.y,
                "timer": 28
            })

        # Skill 2 - Thunder Crash
        elif idx == 1:
            play_sound(sound_skill_thunder)

            self.skill_effects.append({
                "type": "THUNDER",
                "x": SCREEN_WIDTH // 2,
                "y": SCREEN_HEIGHT // 2,
                "timer": 24
            })

            if boss_exists:
                self.boss.hp -= 80
            else:
                for pipe in self.pipes[:]:
                    if abs(pipe.x - self.bird.x) < 300:
                        self.pipes.remove(pipe)

        # Skill 3 - Holy Heal
        elif idx == 2:
            play_sound(sound_skill_heal)

            self.bird.hp = min(self.bird.max_hp, self.bird.hp + 45)
            self.bird.shield_timer = 180

            self.skill_effects.append({
                "type": "HEAL",
                "x": self.bird.x,
                "y": self.bird.y,
                "timer": 36
            })

        # Skill 4 - Ultimate Chaos
        elif idx == 3:
            play_sound(sound_skill_ultimate)

            self.skill_effects.append({
                "type": "ULTIMATE",
                "x": SCREEN_WIDTH // 2,
                "y": SCREEN_HEIGHT // 2,
                "timer": 60
            })

            if boss_exists:
                self.boss.hp -= 120

                # FIX: đảm bảo boss chết đúng cách
                if self.boss.hp <= 0:
                    if self.boss.version == 1:
                        self.boss.version = 2
                        self.boss.max_hp = 700
                        self.boss.hp = 700
                        self.boss.attack_cooldown = 1100
                        self.boss.speed_y = 4
                        play_sound(sound_powerup)
                    else:
                        self.score += 1000
                        save_high_score(self.score)
                        play_sound(sound_boss_death)
                        self.game_state = "WIN"

            self.bird.power_timer = 300
            self.bird.shield_timer = 140

        sk["cd"] = 0 if self.no_skill_cooldown else sk["max_cd"]


    def run(self):
        global volume_effects, volume_music, sound_muted
        running = True
        
        while running:
            clock.tick(FPS)
            current_time = pygame.time.get_ticks()
            
            for sk in getattr(self, "skill_slots", []):
                if not self.no_skill_cooldown:
                    if sk["cd"] > 0:
                        sk["cd"] -= 1
                else:
                    sk["cd"] = 0
            screen.fill(COLOR_DAY_SKY)

            # Ve dam may chay nen cho dep mat o tat ca trang thai man hinh
            if len(self.clouds) < 6 and random.random() < 0.01: self.clouds.append(Cloud())
            for cloud in self.clouds:
                if self.game_state == "PLAYING" and not self.admin_mode: cloud.update()
                cloud.draw(screen)

            # --- QUAN LY SU KIEN (EVENTS) ---
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    pygame.quit()
                    sys.exit()

                
                if event.type == pygame.KEYDOWN and self.game_state == "PLAYING":
                    if event.key == pygame.K_1:
                        self.use_skill(0)

                    elif event.key == pygame.K_2:
                        self.use_skill(1)

                    elif event.key == pygame.K_3:
                        self.use_skill(2)

                    elif event.key == pygame.K_4:
                        self.use_skill(3)

                if event.type == pygame.MOUSEBUTTONDOWN:
                    mx, my = event.pos

                    # 1. LOGIC XU LY TAI MAN HINH CHO (MENU)
                    if self.game_state == "MENU":
                        if SCREEN_WIDTH//2 - 100 <= mx <= SCREEN_WIDTH//2 + 100:
                            if 320 <= my <= 365: # Nut choi game
                                self.reset_game_data()
                                self.boss_disabled_forever = False
                                self.game_state = "PLAYING"
                            elif 390 <= my <= 435:
                                self.game_state = "SETTINGS"
                            elif 460 <= my <= 505:
                                self.game_state = "SHOP"
                            elif 530 <= my <= 575:
                                self.game_state = "MISSIONS"
                        continue

                    # 2. LOGIC XU LY TAI MAN HINH CAI DAT
                    elif self.game_state == "SETTINGS":
                        # Nut Quay lai
                        if SCREEN_WIDTH//2 - 80 <= mx <= SCREEN_WIDTH//2 + 80 and 550 <= my <= 595:
                            self.game_state = "MENU"
                        # Nut Mute am thanh
                        elif SCREEN_WIDTH//2 - 100 <= mx <= SCREEN_WIDTH//2 + 100 and 260 <= my <= 295:
                            sound_muted = not sound_muted
                        # Thanh truot Volume FX (Y: 340)
                        elif SCREEN_WIDTH//2 - 100 <= mx <= SCREEN_WIDTH//2 + 100 and 330 <= my <= 350:
                            volume_effects = (mx - (SCREEN_WIDTH//2 - 100)) / 200.0
                        # Thanh truot Volume Music (Y: 420)
                        elif SCREEN_WIDTH//2 - 100 <= mx <= SCREEN_WIDTH//2 + 100 and 410 <= my <= 430:
                            volume_music = (mx - (SCREEN_WIDTH//2 - 100)) / 200.0
                        continue

                    # 3. LOGIC SHOP
                    elif self.game_state == "SHOP":
                        if 20 <= mx <= 120 and 20 <= my <= 60:
                            self.game_state = "MENU"
                            continue

                        start_y = 170
                        for idx, (skin_name, skin_data) in enumerate(SKINS.items()):
                            btn_y = start_y + idx * 85
                            if 40 <= mx <= 410 and btn_y <= my <= btn_y + 60:
                                
                                if skin_name in self.unlocked_skins:
                                    if self.skin_equipped == skin_name:
                                        self.skin_equipped = "Classic"
                                    else:
                                        self.skin_equipped = skin_name

                                elif self.coins >= skin_data["price"]:
                                    if not skin_data.get("admin_only", False) or self.is_admin:
                                        self.coins -= skin_data["price"]
                                        self.unlocked_skins.append(skin_name)
                                        self.selected_skin = skin_name
                                        save_coins(self.coins)
                                break
                        continue

                    # 3B. LOGIC MISSIONS
                    elif self.game_state == "MISSIONS":
                        if 20 <= mx <= 120 and 20 <= my <= 60:
                            self.game_state = "MENU"
                        continue

                    # 4. LOGIC XU LY TRONG KHI CHOI (PLAYING)
                    elif self.game_state == "PLAYING":

                        # Skill mobile touch
                        for idx, rect in enumerate(getattr(self, "skill_buttons", [])):
                            if rect.collidepoint(mx, my):
                                self.use_skill(idx)
                                break

                        # Bam nut MOD bang dieu khien Admin
                        if self.is_admin and self.admin_btn_rect.collidepoint(mx, my):
                            self.admin_mode = not self.admin_mode
                            continue

                        if self.admin_mode:
                            if 50 <= mx <= 400 and 250 <= my <= 290: self.god_mode = not self.god_mode
                            elif 50 <= mx <= 220 and 330 <= my <= 365: self.custom_speed = max(1.0, self.custom_speed - 0.5)
                            elif 230 <= mx <= 400 and 330 <= my <= 365: self.custom_speed = min(10.0, self.custom_speed + 0.5)
                            elif 50 <= mx <= 400 and 440 <= my <= 485:
                                self.score = 100
                                self.trigger_boss_battle()
                                self.admin_mode = False
                            elif 60 <= mx <= 380 and 540 <= my <= 575:
                                self.coins += 99999
                                save_coins(self.coins)
                            elif 60 <= mx <= 380 and 585 <= my <= 620:
                                self.unlocked_skins = list(SKINS.keys())
                            elif 60 <= mx <= 380 and 630 <= my <= 665:
                                self.no_skill_cooldown = not self.no_skill_cooldown
                            continue

                        self.bird.flap(DEFAULT_FLAP_STRENGTH)

                    # 5. MAN HINH THANG TRAN (WIN)
                    elif self.game_state == "WIN":
                        # Nut CHOI TIEP (Giu nguyen diem, xoa sach boss vinh vien)
                        if SCREEN_WIDTH//2 - 130 <= mx <= SCREEN_WIDTH//2 - 10 and 480 <= my <= 525:
                            self.boss_disabled_forever = True
                            self.reset_game_data(keep_score=True)
                            self.game_state = "PLAYING"
                        # Nut Quay Ve Menu
                        elif SCREEN_WIDTH//2 + 10 <= mx <= SCREEN_WIDTH//2 + 130 and 480 <= my <= 525:
                            self.game_state = "MENU"
                        continue

                    # 6. MAN HINH GAME OVER
                    elif self.game_state == "GAMEOVER":
                        self.game_state = "MENU"

            # =================================================================
            # HE THONG VE VA CAP NHAT LOGIC THEO TUNG MAN HINH TRANG THAI
            # =================================================================

            # --- MAN HINH CHO CHINH (MENU) ---
            if self.game_state == "MENU":
                draw_text(screen, "FLAPPY BOSS", font_title, GOLD_COLOR, (SCREEN_WIDTH // 2, 160))
                draw_text(screen, "HC EDITION", font_msg, WHITE, (SCREEN_WIDTH // 2, 210))
                
                # Ve khoi thong tin Bang Xep Hang Diem Cao
                pygame.draw.rect(screen, (30, 40, 60), (50, 560, 350, 140), border_radius=10)
                pygame.draw.rect(screen, GOLD_COLOR, (50, 560, 350, 140), width=2, border_radius=10)
                draw_text(screen, "∆ BANG XEP HANG ∆", font_msg, GOLD_COLOR, (SCREEN_WIDTH//2, 590))
                draw_text(screen, f"TOP 1 KY LUC MAY: {self.high_score} Diem", font_menu, WHITE, (SCREEN_WIDTH//2, 640))
                
                # Cac nut bam Menu
                for y, label, col in [(320, "CHOI GAME", GREEN_COLOR), (390, "CAI DAT", GRAY), (460, "SHOP", (120,80,220)), (530, "NHIEM VU", (220,120,40))]:
                    pygame.draw.rect(screen, col, (SCREEN_WIDTH//2 - 100, y, 200, 45), border_radius=8)
                    draw_text(screen, label, font_menu, WHITE, (SCREEN_WIDTH//2, y + 22))

            # --- MAN HINH CAI DAT (SETTINGS) ---
            elif self.game_state == "SETTINGS":
                draw_text(screen, "CAI DAT HE THONG", font_title, WHITE, (SCREEN_WIDTH // 2, 150))
                
                # Nut Bat/Tat am nhanh
                mute_lbl = "AM THANH: DANG TAT" if sound_muted else "AM THANH: DANG BAT"
                pygame.draw.rect(screen, RED_COLOR if sound_muted else GREEN_COLOR, (SCREEN_WIDTH//2 - 120, 260, 240, 40), border_radius=6)
                draw_text(screen, mute_lbl, font_msg, WHITE, (SCREEN_WIDTH//2, 280))

                # Thanh truot hieu ung FX Volume
                draw_text(screen, f"Am luong FX: {int(volume_effects * 100)}%", font_msg, WHITE, (SCREEN_WIDTH//2, 330))
                pygame.draw.rect(screen, GRAY, (SCREEN_WIDTH//2 - 100, 345, 200, 8))
                pygame.draw.circle(screen, GOLD_COLOR, (int(SCREEN_WIDTH//2 - 100 + (volume_effects * 200)), 349), 10)

                # Thanh truot nhac nen
                draw_text(screen, f"Am luong Nhac: {int(volume_music * 100)}%", font_msg, WHITE, (SCREEN_WIDTH//2, 410))
                pygame.draw.rect(screen, GRAY, (SCREEN_WIDTH//2 - 100, 425, 200, 8))
                pygame.draw.circle(screen, CYAN_COLOR, (int(SCREEN_WIDTH//2 - 100 + (volume_music * 200)), 429), 10)

                # Nut Quay lai
                pygame.draw.rect(screen, BLACK, (SCREEN_WIDTH//2 - 80, 550, 160, 45), border_radius=8)
                draw_text(screen, "QUAY LAI", font_menu, WHITE, (SCREEN_WIDTH//2, 572))

            # --- SHOP ---
            elif self.game_state == "SHOP":
                draw_text(screen, "CUA HANG SKIN", font_title, GOLD_COLOR, (SCREEN_WIDTH // 2, 80))
                draw_text(screen, f"COIN: {self.coins}", font_menu, WHITE, (SCREEN_WIDTH // 2, 120))

                pygame.draw.rect(screen, BLACK, (20, 20, 100, 40), border_radius=8)
                draw_text(screen, "MENU", font_admin, WHITE, (70, 40))

                start_y = 170
                for idx, (skin_name, skin_data) in enumerate(SKINS.items()):
                    y = start_y + idx * 85
                    owned = skin_name in self.unlocked_skins

                    pygame.draw.rect(screen, (40,40,60), (40, y, 370, 60), border_radius=10)
                    pygame.draw.rect(screen, GOLD_COLOR, (40, y, 370, 60), width=2, border_radius=10)

                    
                    status = "TRANG BI" if owned else f"MUA {skin_data['price']} COIN"
                    if self.skin_equipped == skin_name:
                        status = "HUY TRANG BI"

                    if skin_data.get("admin_only", False):
                        status += " [ADMIN]"

                    draw_text(screen, skin_name, font_msg, WHITE, (130, y + 18))
                    draw_text(screen, status, font_admin, GOLD_COLOR, (220, y + 42))

            # --- MISSIONS ---
            elif self.game_state == "MISSIONS":
                draw_text(screen, "NHIEM VU", font_title, GOLD_COLOR, (SCREEN_WIDTH // 2, 100))

                pygame.draw.rect(screen, BLACK, (20, 20, 100, 40), border_radius=8)
                draw_text(screen, "MENU", font_admin, WHITE, (70, 40))

                for idx, mission in enumerate(MISSIONS):
                    y = 180 + idx * 100
                    done = mission.get("done", False)

                    pygame.draw.rect(screen, (40,40,60), (50, y, 350, 70), border_radius=10)
                    pygame.draw.rect(screen, GREEN_COLOR if done else GOLD_COLOR, (50, y, 350, 70), width=2, border_radius=10)

                    state = "DA HOAN THANH" if done else "CHUA HOAN THANH"

                    draw_text(screen, mission["name"], font_msg, WHITE, (SCREEN_WIDTH//2, y + 20))
                    draw_text(screen, f"Thuong: {mission['reward']} coin - {state}", font_admin, GOLD_COLOR, (SCREEN_WIDTH//2, y + 48))

            
                # Reset mission moi 1 gio
                last_reset = load_last_reset()
                if time.time() - last_reset >= 3600:
                    for mission in MISSIONS:
                        mission["done"] = False
                    save_last_reset()

            # --- TRANG THAI DANG CHOI GAME CHINH (PLAYING) ---
            elif self.game_state == "PLAYING":
                if not self.admin_mode:
                    self.bird.update(DEFAULT_GRAVITY)

                    if self.score >= 100 and self.boss is None and not self.boss_disabled_forever:
                        self.trigger_boss_battle()

                    if self.boss is None:
                        if current_time - self.last_pipe_time > PIPE_FREQUENCY:
                            self.pipes.append(Pipe(SCREEN_WIDTH, self.custom_gap))
                            self.last_pipe_time = current_time

                        for pipe in self.pipes[:]:
                            pipe.update(self.custom_speed)
                            if not self.god_mode and self.bird.shield_timer <= 0 and pipe.collide(self.bird.get_rect()):
                                play_sound(sound_hit)
                                self.game_state = "GAMEOVER"
                            if not pipe.passed and pipe.x + pipe.width < self.bird.x:
                                self.score += 1
                                play_sound(sound_score)
                                save_high_score(self.score)
                                pipe.passed = True
                            if pipe.is_offscreen(): self.pipes.remove(pipe)
                    else:
                        # LOGIC CHIEN DAU VOI BOSS
                        self.boss.update()

                        shoot_cooldown = 120 if self.bird.power_timer > 0 else 250
                        if current_time - self.last_shoot_time > shoot_cooldown:
                            is_super = self.bird.power_timer > 0
                            self.bananas.append(BananaBullet(self.bird.x + 15, self.bird.y, is_super))
                            self.last_shoot_time = current_time

                        for banana in self.bananas[:]:
                            banana.update()
                            # Sinh ra hat tia lua duoi dan chuoi
                            if random.random() < 0.18:
                                self.particles.append(Particle(banana.x, banana.y))
                                
                            if self.boss.get_rect().colliderect(banana.get_rect()):
                                self.boss.hp -= banana.damage
                                if banana in self.bananas: self.bananas.remove(banana)
                                if random.random() < 0.18:
                                    self.items.append(Item(self.boss.x, self.boss.y + 40, random.choice(["HEAL", "SHIELD", "POWER"])))

                                if self.boss.hp <= 0:
                                    if self.boss.version == 1:
                                        self.boss.version = 2
                                        self.boss.max_hp = 700
                                        self.boss.hp = 700
                                        self.boss.attack_cooldown = 1100
                                        self.boss.speed_y = 4
                                        play_sound(sound_powerup)
                                    else:
                                        self.score += 1000
                                        save_high_score(self.score)
                                        play_sound(sound_boss_death)
                                        self.game_state = "WIN"
                                    break
                            elif banana.x > SCREEN_WIDTH:
                                if banana in self.bananas: self.bananas.remove(banana)

                        # Vat pham di chuyen va va cham hoi mau
                        for item in self.items[:]:
                            item.update()
                            if item.get_rect().colliderect(self.bird.get_rect()):
                                play_sound(sound_powerup)
                                if item.type == "HEAL": 
                                    self.bird.hp = min(self.bird.max_hp, self.bird.hp + 100) # Cong 100 mau day binh luon
                                elif item.type == "SHIELD": self.bird.shield_timer = 300
                                elif item.type == "POWER": self.bird.power_timer = 300
                                self.items.remove(item)
                            elif item.x < 0: self.items.remove(item)

                        # Boss phan cong ban dan trung chim tru 10 mau
                        if self.boss and self.boss.state == "BATTLE" and current_time - self.boss.last_attack_time > self.boss.attack_cooldown:
                            self.boss.last_attack_time = current_time
                            skills = ["BULLET", "LASER", "THUNDER", "METEOR", "FIREBALL"] if self.boss.version == 1 else ["BULLET", "LASER", "MINION", "THUNDER", "SKELETON", "METEOR", "DARK LASER", "CHAOS"]
                            stype = random.choice(skills)
                            play_sound(sound_boss_warning)
                            if stype == "BULLET":
                                self.boss_bullets.append(BossBullet(self.boss.x, self.boss.y + 20))
                                self.boss_bullets.append(BossBullet(self.boss.x, self.boss.y + 100))
                            elif stype == "LASER" and not self.laser_active:
                                self.laser_active = True
                                self.laser_y = self.bird.y
                                self.laser_start_time = current_time
                                play_sound(sound_laser)
                            elif stype == "MINION":
                                self.boss_bullets.append(BossBullet(self.boss.x, self.boss.y + 50, is_minion=True))
                            elif stype == "THUNDER":
                                if not self.god_mode:
                                        self.bird.hp -= 5
                                self.boss_bullets.append(BossBullet(self.boss.x, self.boss.y + 30))
                            elif stype == "SKELETON":
                                self.boss_bullets.append(BossBullet(self.boss.x, self.boss.y + 70, is_minion=True))
                                self.boss_bullets.append(BossBullet(self.boss.x, self.boss.y + 90, is_minion=True))

                            elif stype == "METEOR":
                                for yy in range(120, SCREEN_HEIGHT - 120, 120):
                                    self.boss_bullets.append(BossBullet(self.boss.x, yy, is_minion=True))

                            
                            elif stype == "FIREBALL":
                                for i in range(4):
                                    self.boss_bullets.append(BossBullet(self.boss.x, self.boss.y + 30 + i * 25))

                            elif stype == "CHAOS":
                                self.laser_active = True
                                self.laser_y = random.randint(120, SCREEN_HEIGHT - 120)
                                self.laser_start_time = current_time
                                for yy in range(120, SCREEN_HEIGHT - 120, 90):
                                    self.boss_bullets.append(BossBullet(self.boss.x, yy, is_minion=True))

                            elif stype == "DARK LASER":
                                self.laser_active = True
                                self.laser_y = random.randint(150, SCREEN_HEIGHT - 150)
                                self.laser_start_time = current_time

                            elif stype == "SKELETON":
                                self.boss_bullets.append(BossBullet(self.boss.x, self.boss.y + 70, is_minion=True))

                        for b_bullet in self.boss_bullets[:]:
                            b_bullet.update()
                            if not self.god_mode and self.bird.shield_timer <= 0 and b_bullet.get_rect().colliderect(self.bird.get_rect()):
                                play_sound(sound_hit)
                                if not self.god_mode:
                                        self.bird.hp -= 10  # Trung dan tru 10 mau
                                if b_bullet in self.boss_bullets: self.boss_bullets.remove(b_bullet)
                                if self.bird.hp <= 0: self.game_state = "GAMEOVER"
                            elif b_bullet.x < 0: self.boss_bullets.remove(b_bullet)

                        if self.laser_active:
                            elapsed = current_time - self.laser_start_time
                            if 400 < elapsed < 450: # Sat thuong laser quet trung tia
                                laser_rect = pygame.Rect(0, self.laser_y - 15, SCREEN_WIDTH, 30)
                                if not self.god_mode and self.bird.shield_timer <= 0 and laser_rect.colliderect(self.bird.get_rect()):
                                    play_sound(sound_hit)
                                    if not self.god_mode:
                                        self.bird.hp -= 10
                                    if self.bird.hp <= 0:
                                        self.game_state = "GAMEOVER"
                            if elapsed > 900: self.laser_active = False

                    # Roi cham dat
                    if self.bird.y + self.bird.radius >= SCREEN_HEIGHT - 50:
                        if self.god_mode or self.bird.shield_timer > 0:
                            self.bird.y = SCREEN_HEIGHT - 50 - self.bird.radius
                            self.bird.velocity = 0
                        else:
                            play_sound(sound_hit)
                            self.game_state = "GAMEOVER"

                # --- VE HINH DO HOA TRONG GAME ---
                for p in self.particles[:]:
                    p.update()
                    p.draw(screen)
                    if p.lifetime <= 0: self.particles.remove(p)

                for effect in self.skill_effects[:]:
                    effect["timer"] -= 1

                    if effect["type"] == "FIRE":
                        for i in range(3):
                            pygame.draw.circle(
                                screen,
                                (255, random.randint(80, 200), 0),
                                (int(effect["x"] + random.randint(-50, 50)), int(effect["y"] + random.randint(-50, 50))),
                                random.randint(6, 14)
                            )

                    elif effect["type"] == "THUNDER":
                        for i in range(3):
                            sx = effect["x"] + random.randint(-60, 60)
                            ex = sx + random.randint(-25, 25)
                            pygame.draw.line(screen, CYAN_COLOR, (sx, 0), (ex, SCREEN_HEIGHT), 5)

                    elif effect["type"] == "HEAL":
                        pygame.draw.circle(screen, GREEN_COLOR, (int(self.bird.x), int(self.bird.y)), 70, width=6)
                        pygame.draw.circle(screen, WHITE, (int(self.bird.x), int(self.bird.y)), 45, width=3)

                    elif effect["type"] == "ULTIMATE":
                        pygame.draw.rect(screen, (180, 0, 255), (0, 0, SCREEN_WIDTH, SCREEN_HEIGHT), width=12)
                        for i in range(3):
                            pygame.draw.circle(
                                screen,
                                (255, 0, random.randint(120, 255)),
                                (random.randint(0, SCREEN_WIDTH), random.randint(0, SCREEN_HEIGHT)),
                                random.randint(10, 28),
                                width=3
                            )

                    if effect["timer"] <= 0:
                        self.skill_effects.remove(effect)
                    
                for pipe in self.pipes: pipe.draw(screen)
                for banana in self.bananas: banana.draw(screen)
                for b_bullet in self.boss_bullets: b_bullet.draw(screen)
                for item in self.items: item.draw(screen)

                if self.laser_active and self.boss:
                    if (current_time - self.laser_start_time) < 400:
                        pygame.draw.line(screen, (255, 0, 0), (0, self.laser_y), (SCREEN_WIDTH, self.laser_y), 2)
                    else:
                        pygame.draw.rect(screen, (255, 70, 70), (0, self.laser_y - 10, SCREEN_WIDTH, 20))

                if self.boss: self.boss.draw(screen)

                # Ve thanh HP cua Boss ben tren man hinh
                if self.boss:
                    hp_box_rect = pygame.Rect(30, 22, SCREEN_WIDTH - 60, 26)
                    pygame.draw.rect(screen, (30, 30, 30), hp_box_rect, border_radius=6)
                    pygame.draw.rect(screen, GOLD_COLOR, hp_box_rect, width=3, border_radius=6)
                    pct = max(0, self.boss.hp / self.boss.max_hp)
                    hp_fill_width = int((SCREEN_WIDTH - 66) * pct)
                    if hp_fill_width > 0:
                        b_color = (200, 50, 250) if self.boss.version == 1 else RED_COLOR
                        pygame.draw.rect(screen, b_color, (33, 25, hp_fill_width, 20), border_radius=4)
                    draw_text(screen, f"TUSU BOSS V{self.boss.version}: {self.boss.hp}/{self.boss.max_hp}", font_admin, WHITE, (SCREEN_WIDTH//2, 35))

                pygame.draw.rect(screen, GROUND_COLOR, (0, SCREEN_HEIGHT - 50, SCREEN_WIDTH, 50))
                pygame.draw.line(screen, (115, 191, 46), (0, SCREEN_HEIGHT - 50), (SCREEN_WIDTH, SCREEN_HEIGHT - 50), 5)
                
                # Goi ve chim kem cau hinh skin Admin lua neu da mo khoa thanh cong
                self.bird.draw(screen, use_admin_skin=(self.skin_equipped == "Phoenix"))

                # Skill UI chi hien khi boss xuat hien
                self.skill_buttons = []

                if self.boss:
                    draw_text(screen, "SKILL", font_msg, GOLD_COLOR, (SCREEN_WIDTH - 80, SCREEN_HEIGHT - 360))

                    skill_x = SCREEN_WIDTH - 85
                    skill_y = SCREEN_HEIGHT - 290
                    skill_count = SKINS.get(self.skin_equipped, SKINS["Classic"]).get("skill_count", 1)

                    for idx, sk in enumerate(self.skill_slots[:skill_count]):
                        y = skill_y + idx * 90

                        btn_rect = pygame.Rect(skill_x - 42, y - 42, 84, 84)
                        self.skill_buttons.append(btn_rect)

                        skill_colors = [
                            (255, 90, 0),
                            (0, 255, 255),
                            (0, 255, 120),
                            (180, 0, 255)
                        ]

                        main_color = skill_colors[idx]

                        for glow in range(52, 42, -2):
                            pygame.draw.circle(screen, main_color, (skill_x, y), glow, 1)

                        pygame.draw.circle(screen, (15, 15, 15), (skill_x, y), 42)
                        pygame.draw.circle(screen, main_color, (skill_x, y), 38, width=5)
                        pygame.draw.circle(screen, GOLD_COLOR, (skill_x, y), 34, width=4)

                        txt = str(idx + 1)
                        icons = [fireball_icon, thunder_icon, heal_icon, ultimate_icon]

                        if idx < len(icons) and icons[idx]:
                            icon = pygame.transform.scale(icons[idx], (52, 52))
                            screen.blit(icon, (skill_x - 26, y - 26))
                        else:
                            draw_text(screen, txt, font_score, WHITE, (skill_x, y))

                        if sk["cd"] > 0:
                            cd_text = str(round(sk["cd"] / 60, 1))
                            draw_text(screen, cd_text, font_msg, RED_COLOR, (skill_x, y + 50))
                        else:
                            draw_text(screen, "READY", font_msg, GREEN_COLOR, (skill_x, y + 50))

                if self.is_admin:
                    pygame.draw.circle(screen, GOLD_COLOR, (self.admin_btn_rect.centerx, self.admin_btn_rect.centery), 22)
                    pygame.draw.circle(screen, (50, 50, 50), (self.admin_btn_rect.centerx, self.admin_btn_rect.centery), 18)
                    draw_text(screen, "ADMIN", font_admin, GOLD_COLOR, (self.admin_btn_rect.centerx, self.admin_btn_rect.centery))

                
                    # Nhiem vu reward
                    for mission in MISSIONS:
                        if self.score >= mission["goal"] and mission.get("done") != True:
                            self.coins += mission["reward"]
                            save_coins(self.coins)
                            mission["done"] = True

                draw_text(screen, f"COIN: {self.coins}", font_admin, GOLD_COLOR, (80, 80))

                if not self.boss:
                    draw_text(screen, str(self.score), font_score, WHITE, (SCREEN_WIDTH // 2, 80))

                # Render bang dieu khien MOD
                if self.admin_mode and self.is_admin:
                    admin_rect = pygame.Rect(30, 140, 390, 390)
                    pygame.draw.rect(screen, (40, 40, 40), admin_rect, border_radius=15)
                    pygame.draw.rect(screen, GOLD_COLOR, admin_rect, width=3, border_radius=15)
                    draw_text(screen, "=== ADMIN PANEL ===", font_score, GOLD_COLOR, (SCREEN_WIDTH // 2, 180))
                    god_btn = pygame.Rect(50, 250, 350, 40)
                    pygame.draw.rect(screen, GREEN_COLOR if self.god_mode else RED_COLOR, god_btn, border_radius=8)
                    draw_text(screen, f"BAT TU: {'BAT (ON)' if self.god_mode else 'TAT (OFF)'}", font_msg, WHITE, (SCREEN_WIDTH // 2, 270))
                    draw_text(screen, f"Toc do Ong: {self.custom_speed}", font_admin, WHITE, (SCREEN_WIDTH // 2, 310))
                    pygame.draw.rect(screen, (100, 100, 100), (50, 330, 170, 35), border_radius=5)
                    draw_text(screen, "GIAM TOC -", font_admin, WHITE, (135, 347))
                    pygame.draw.rect(screen, (100, 100, 100), (230, 330, 170, 35), border_radius=5)
                    draw_text(screen, "TANG TOC +", font_admin, WHITE, (315, 347))
                    boss_btn = pygame.Rect(50, 440, 350, 45)
                    pygame.draw.rect(screen, (150, 50, 200), boss_btn, border_radius=8)
                    draw_text(screen, "GOI THUC TINH BOSS", font_msg, WHITE, (SCREEN_WIDTH // 2, 462))
                    draw_text(screen, "ADMIN: +99999 COIN / MO KHOA SKIN / NO CD", font_admin, CYAN_COLOR, (SCREEN_WIDTH//2, 510))

                    btn_coin = pygame.Rect(60, 540, 320, 35)
                    pygame.draw.rect(screen, (80,120,40), btn_coin, border_radius=6)
                    draw_text(screen, "+99999 COIN", font_admin, WHITE, (220, 557))

                    btn_skin = pygame.Rect(60, 585, 320, 35)
                    pygame.draw.rect(screen, (120,80,180), btn_skin, border_radius=6)
                    draw_text(screen, "MO KHOA TOAN BO SKIN", font_admin, WHITE, (220, 602))

                    btn_cd = pygame.Rect(60, 630, 320, 35)
                    pygame.draw.rect(screen, (180,60,60), btn_cd, border_radius=6)
                    draw_text(screen, "KHONG HOI CHIEU", font_admin, WHITE, (220, 647))

            # --- MAN HINH GAME OVER ---
            elif self.game_state == "GAMEOVER":
                draw_text(screen, "GAME OVER", font_title, RED_COLOR, (SCREEN_WIDTH // 2, 300))
                draw_text(screen, f"Diem dat duoc: {self.score}", font_menu, WHITE, (SCREEN_WIDTH // 2, 360))
                draw_text(screen, "Cham man hinh de quay lai Menu chinh", font_msg, WHITE, (SCREEN_WIDTH // 2, 450))

            # --- MAN HINH CHIEN THANG BOSS (WIN) ---
            elif self.game_state == "WIN":
                win_rect = pygame.Rect(40, SCREEN_HEIGHT // 2 - 150, SCREEN_WIDTH - 80, 310)
                pygame.draw.rect(screen, (20, 20, 20), win_rect, border_radius=15)
                pygame.draw.rect(screen, GOLD_COLOR, win_rect, width=4, border_radius=15)
                
                draw_text(screen, "VICTORY!", font_title, GOLD_COLOR, (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 90))
                draw_text(screen, f"Tong diem: {self.score}", font_msg, WHITE, (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 20))
                
                # Nut CHOI TIEP (Giu nguyen diem so, khong bao gio xuat hien Boss nua)
                btn_continue = pygame.Rect(SCREEN_WIDTH//2 - 130, SCREEN_HEIGHT//2 + 40, 120, 45)
                pygame.draw.rect(screen, GREEN_COLOR, btn_continue, border_radius=8)
                draw_text(screen, "CHOI TIEP", font_msg, WHITE, (SCREEN_WIDTH//2 - 70, SCREEN_HEIGHT//2 + 62))
                
                # Nut THOAT ra Menu cho
                btn_exit = pygame.Rect(SCREEN_WIDTH//2 + 10, SCREEN_HEIGHT//2 + 40, 120, 45)
                pygame.draw.rect(screen, RED_COLOR, btn_exit, border_radius=8)
                draw_text(screen, "MENU", font_msg, WHITE, (SCREEN_WIDTH//2 + 70, SCREEN_HEIGHT//2 + 62))

            pygame.display.flip()

game = None


# ===== MAIN =====
if __name__ == "__main__":
    pygame.init()

    try:
        game = Game()
        game.run()
    except Exception as e:
        print("GAME ERROR:", e)
        import traceback
        traceback.print_exc()
