import math
import random
import pygame

class MascotSunflower:
    """
    Maskot Karakter Bunga Matahari Interaktif & Menggemaskan:
    - Melentur/meliuk halus ke kiri/kanan mengikuti pitch nada (Bass/Treble).
    - Memantul gembira (bounce) saat ada nada dimainkan kencang (velocity tinggi).
    - Mata berbinar dan berkedip berkala.
    - Menghasilkan partikel musik / daun berkilau saat nada ditekan pas.
    """

    def __init__(self, x: int, y: int, base_radius: int = 42):
        self.base_x = float(x)
        self.base_y = float(y)
        self.radius = base_radius

        # Status Fisika Animasi (Spring & Lerp)
        self.lean_angle = 0.0        # Sudut kemiringan batang (radian)
        self.target_lean = 0.0
        self.bounce_y = 0.0          # Efek melonjak vertikal
        self.target_bounce = 0.0

        # Wajah & Ekspresi
        self.blink_timer = 0
        self.is_blinking = False
        self.expression = "happy"    # "happy", "excited", "curious"

        # Partikel
        self.particles = []

    def on_note_event(self, pitch: int, velocity: int = 80, hit_status: str = "hit"):
        """Merespons nada yang ditekan oleh pemain."""
        # Nada rendah (pitch < 60) meliuk ke kiri (-), nada tinggi (> 60) meliuk ke kanan (+)
        normalized_pitch = (pitch - 60) / 28.0
        self.target_lean = max(-0.35, min(0.35, normalized_pitch * 0.35))

        # Reaksi pantulan berdasarkan velocity
        bounce_strength = (velocity / 127.0) * 18.0
        self.target_bounce = -bounce_strength

        if hit_status == "hit":
            self.expression = "excited"
            # Munculkan 3-5 partikel bintang / kilau kecil
            for _ in range(4):
                self.particles.append({
                    'x': self.base_x + random.randint(-20, 20),
                    'y': self.base_y - 40 + random.randint(-15, 10),
                    'vx': random.uniform(-1.5, 1.5),
                    'vy': random.uniform(-2.5, -0.8),
                    'life': 1.0,
                    'color': random.choice([(255, 230, 80), (255, 100, 150), (100, 240, 255)])
                })
        else:
            self.expression = "curious"

    def update(self, dt: float = 0.016):
        """Memperbarui animasi dengan interpolasi halus."""
        # Smooth Spring lerp untuk lean
        self.lean_angle += (self.target_lean - self.lean_angle) * 0.12
        # Perlahan kembali ke posisi tegak idle
        self.target_lean *= 0.94

        # Smooth bounce lerp
        self.bounce_y += (self.target_bounce - self.bounce_y) * 0.2
        self.target_bounce *= 0.88

        # Logika kedip mata
        self.blink_timer += dt
        if self.blink_timer > 3.2:
            self.is_blinking = True
            if self.blink_timer > 3.4:
                self.is_blinking = False
                self.blink_timer = random.uniform(0.0, 1.5)

        # Update partikel
        for p in list(self.particles):
            p['x'] += p['vx']
            p['y'] += p['vy']
            p['life'] -= dt * 1.5
            if p['life'] <= 0:
                self.particles.remove(p)

    def draw(self, surface: pygame.Surface):
        # 1. Gambar Partikel
        for p in self.particles:
            alpha_val = int(max(0, min(255, p['life'] * 255)))
            p_surf = pygame.Surface((8, 8), pygame.SRCALPHA)
            pygame.draw.circle(p_surf, (*p['color'], alpha_val), (4, 4), 3)
            surface.blit(p_surf, (int(p['x']), int(p['y'])))

        # Hitung posisi kepala bunga matahari berdasarkan batang dan kemiringan
        stem_height = 55
        stem_start_x = self.base_x
        stem_start_y = self.base_y + 35

        head_x = stem_start_x + math.sin(self.lean_angle) * stem_height
        head_y = (stem_start_y - math.cos(self.lean_angle) * stem_height) + self.bounce_y

        # 2. Gambar Batang Hijau Lentur (Bézier/Curve Sederhana)
        ctrl_x = stem_start_x + (head_x - stem_start_x) * 0.3
        ctrl_y = stem_start_y - stem_height * 0.4
        pygame.draw.line(surface, (76, 175, 80), (int(stem_start_x), int(stem_start_y)), (int(head_x), int(head_y)), 7)

        # 3. Gambar Daun Tangan Lucu di batang
        leaf_x = stem_start_x + (head_x - stem_start_x) * 0.45
        leaf_y = stem_start_y - stem_height * 0.45
        pygame.draw.ellipse(surface, (56, 142, 60), (int(leaf_x - 18), int(leaf_y - 5), 20, 10))
        pygame.draw.ellipse(surface, (56, 142, 60), (int(leaf_x + 2), int(leaf_y - 8), 20, 10))

        # 4. Gambar Kelopak Bunga (Petals) Berwarna Kuning Keemasan
        num_petals = 12
        petal_len = self.radius * 0.55
        for i in range(num_petals):
            angle = (2 * math.pi / num_petals) * i + (self.lean_angle * 0.5)
            px = head_x + math.cos(angle) * (self.radius + petal_len * 0.4)
            py = head_y + math.sin(angle) * (self.radius + petal_len * 0.4)
            pygame.draw.circle(surface, (255, 204, 0), (int(px), int(py)), int(petal_len * 0.55))
            pygame.draw.circle(surface, (255, 238, 88), (int(px), int(py)), int(petal_len * 0.35))

        # 5. Piringan Wajah Bunga Cokelat Hangat
        pygame.draw.circle(surface, (121, 85, 72), (int(head_x), int(head_y)), self.radius)
        pygame.draw.circle(surface, (141, 110, 99), (int(head_x), int(head_y)), self.radius - 4)

        # 6. Pipi Merona Pink (Blush) Menggemaskan
        blush_y = head_y + 8
        pygame.draw.circle(surface, (255, 138, 128), (int(head_x - 16), int(blush_y)), 6)
        pygame.draw.circle(surface, (255, 138, 128), (int(head_x + 16), int(blush_y)), 6)

        # 7. Mata Berbinar
        eye_y = head_y - 4
        if self.is_blinking:
            # Garis lengkung tertutup saat berkedip
            pygame.draw.line(surface, (30, 20, 20), (int(head_x - 17), int(eye_y)), (int(head_x - 9), int(eye_y)), 3)
            pygame.draw.line(surface, (30, 20, 20), (int(head_x + 9), int(eye_y)), (int(head_x + 17), int(eye_y)), 3)
        else:
            # Mata bulat berbinar
            pygame.draw.circle(surface, (33, 33, 33), (int(head_x - 13), int(eye_y)), 6)
            pygame.draw.circle(surface, (33, 33, 33), (int(head_x + 13), int(eye_y)), 6)
            # Kilau putih di dalam mata (catchlight)
            pygame.draw.circle(surface, (255, 255, 255), (int(head_x - 15), int(eye_y - 2)), 2)
            pygame.draw.circle(surface, (255, 255, 255), (int(head_x + 11), int(eye_y - 2)), 2)

        # 8. Mulut Senyum Ceria
        mouth_rect = pygame.Rect(int(head_x - 8), int(head_y + 4), 16, 12)
        pygame.draw.arc(surface, (33, 33, 33), mouth_rect, math.pi, 2 * math.pi, 3)
