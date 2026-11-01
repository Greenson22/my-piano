import colorsys
import pygame

MIN_PITCH = 21
MAX_PITCH = 108
NOTE_NAMES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']


class VisualNote:
    """Kelas untuk mengelola visualisasi dan animasi individual not piano."""

    def __init__(self, pitch: int, velocity: int, width: int, height: int):
        self.pitch = pitch
        self.velocity = velocity

        octave = (pitch // 12) - 1
        self.name = f"{NOTE_NAMES[pitch % 12]}{octave}"

        clamped_pitch = max(MIN_PITCH, min(pitch, MAX_PITCH))
        normalized = (clamped_pitch - MIN_PITCH) / (MAX_PITCH - MIN_PITCH)

        self.x = int(60 + normalized * (width - 120))
        self.y = int((height - 120) * (1 - normalized)) + 60

        # Gradasi Warna HSV -> RGB
        hue = normalized * 0.8
        r, g, b = colorsys.hsv_to_rgb(hue, 0.9, 1.0)
        self.color = (int(r * 255), int(g * 255), int(b * 255))

        # Rentang Font (16px - 36px)
        min_font_size = 16
        max_font_size = 36
        velo_normalized = max(1, min(velocity, 127)) / 127.0
        self.font_size = int(min_font_size + velo_normalized * (max_font_size - min_font_size))

        self.font = pygame.font.SysFont("Arial", self.font_size, bold=True)

        # Status animasi
        self.is_releasing = False
        self.alpha = 255
        self.fall_speed = 3
        self.fade_speed = 8

    def release(self):
        """Menandai not telah dilepas (mulai animasi jatuh/pudar)."""
        self.is_releasing = True

    def update(self):
        """Memperbarui posisi dan transparansi not saat pudar."""
        if self.is_releasing:
            self.y += self.fall_speed
            self.alpha -= self.fade_speed
            if self.alpha < 0:
                self.alpha = 0

    def draw(self, surface: pygame.Surface):
        """Gambar teks not beserta outline hitam ke surface Pygame."""
        outline_surface = self.font.render(self.name, True, (0, 0, 0))
        text_surface = self.font.render(self.name, True, self.color)

        w, h = text_surface.get_size()
        combined_surface = pygame.Surface((w + 4, h + 4), pygame.SRCALPHA)

        # Outline hitam di sekeliling
        for dx, dy in [(-2, 0), (2, 0), (0, -2), (0, 2), (-1, -1), (1, 1), (-1, 1), (1, -1)]:
            combined_surface.blit(outline_surface, (dx + 2, dy + 2))

        combined_surface.blit(text_surface, (2, 2))
        combined_surface.set_alpha(self.alpha)

        rect = combined_surface.get_rect(center=(self.x, self.y))
        surface.blit(combined_surface, rect)
