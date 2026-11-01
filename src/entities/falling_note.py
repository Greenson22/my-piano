import pygame
from ..audio.midi_parser import MidiNoteEvent
from ..utils.constants import COLOR_RIGHT_HAND, COLOR_LEFT_HAND, get_note_name

class FallingNote:
    """
    Representasi visual balok nada jatuh (Synthesia-style).
    Turun dari atas layar menuju hit_line tepat di atas tuts piano.
    """

    def __init__(self, event: MidiNoteEvent, x: float, width: float):
        self.event = event
        self.x = x - (width / 2)
        self.width = width
        self.color = COLOR_RIGHT_HAND if event.hand == 'right' else COLOR_LEFT_HAND
        self.note_name = get_note_name(event.pitch)

    def draw(self, surface: pygame.Surface, current_time: float, pixels_per_sec: float, hit_line_y: float):
        """
        Hitung koordinat Y berdasarkan waktu saat ini:
        Waktu sampai menyentuh garis = event.start_time - current_time
        y_bottom = hit_line_y - (event.start_time - current_time) * pixels_per_sec
        """
        time_until_hit = self.event.start_time - current_time
        y_bottom = hit_line_y - (time_until_hit * pixels_per_sec)
        note_height = max(18.0, self.event.duration * pixels_per_sec)
        y_top = y_bottom - note_height

        rect = pygame.Rect(int(self.x), int(y_top), int(self.width), int(note_height))

        # Hanya render jika berada dalam batas layar yang masuk akal
        if rect.bottom < 0 or rect.top > surface.get_height():
            return

        # Efek Balok Bercahaya
        # Warna inti
        pygame.draw.rect(surface, self.color, rect, border_radius=5)
        # Border halus yang lebih terang
        highlight_color = (
            min(255, self.color[0] + 40),
            min(255, self.color[1] + 40),
            min(255, self.color[2] + 40)
        )
        pygame.draw.rect(surface, highlight_color, rect, width=2, border_radius=5)

        # Nama Not di dalam balok jika ruang cukup
        if note_height >= 20:
            font = pygame.font.SysFont("Segoe UI", 10, bold=True)
            txt = font.render(self.note_name, True, (20, 20, 25))
            tx = rect.centerx - txt.get_width() // 2
            ty = rect.bottom - txt.get_height() - 2
            surface.blit(txt, (tx, ty))
