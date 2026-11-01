import pygame
from typing import Dict, Set
from ..utils.constants import (
    KEYBOARD_MIN_PITCH, KEYBOARD_MAX_PITCH,
    COLOR_WHITE_KEY, COLOR_WHITE_KEY_PRESSED,
    COLOR_BLACK_KEY, COLOR_BLACK_KEY_PRESSED,
    COLOR_KEY_BORDER, is_black_key, get_note_name
)

class PianoKeyboard:
    """
    Render tuts piano interaktif (putih dan hitam) di bagian bawah layar.
    Merespons saat tuts ditekan oleh input keyboard MIDI maupun nada dari file lagu.
    """

    def __init__(self, x: int, y: int, width: int, height: int, min_pitch=KEYBOARD_MIN_PITCH, max_pitch=KEYBOARD_MAX_PITCH):
        self.rect = pygame.Rect(x, y, width, height)
        self.min_pitch = min_pitch
        self.max_pitch = max_pitch

        self.pressed_keys: Set[int] = set()
        self.target_keys: Set[int] = set() # Tuts yang saat ini sedang disentuh oleh falling note

        # Hitung tuts putih
        self.white_pitches = [p for p in range(min_pitch, max_pitch + 1) if not is_black_key(p)]
        self.black_pitches = [p for p in range(min_pitch, max_pitch + 1) if is_black_key(p)]

        self.white_key_width = width / max(1, len(self.white_pitches))
        self.black_key_width = self.white_key_width * 0.62
        self.black_key_height = height * 0.62

        self.white_rects: Dict[int, pygame.Rect] = {}
        self.black_rects: Dict[int, pygame.Rect] = {}
        self._calculate_rects()

        self.font = pygame.font.SysFont("Segoe UI", 11, bold=True)

    def _calculate_rects(self):
        curr_x = self.rect.x
        for p in self.white_pitches:
            rect = pygame.Rect(curr_x, self.rect.y, int(self.white_key_width), self.rect.height)
            self.white_rects[p] = rect
            curr_x += self.white_key_width

        # Posisi tuts hitam bertengger di antara tuts putih
        for p in self.black_pitches:
            # Cari tuts putih sebelumnya
            prev_white = p - 1
            while prev_white >= self.min_pitch and is_black_key(prev_white):
                prev_white -= 1

            if prev_white in self.white_rects:
                w_rect = self.white_rects[prev_white]
                bx = w_rect.right - (self.black_key_width / 2)
                self.black_rects[p] = pygame.Rect(
                    int(bx), self.rect.y, int(self.black_key_width), int(self.black_key_height)
                )

    def get_pitch_x(self, pitch: int) -> float:
        """Mengembalikan koordinat x tengah untuk suatu nada pitch."""
        if pitch in self.black_rects:
            return self.black_rects[pitch].centerx
        elif pitch in self.white_rects:
            return self.white_rects[pitch].centerx
        else:
            # Fallback interpolasi jika pitch di luar rentang tuts
            ratio = (pitch - self.min_pitch) / max(1, (self.max_pitch - self.min_pitch))
            return self.rect.x + ratio * self.rect.width

    def press_key(self, pitch: int):
        self.pressed_keys.add(pitch)

    def release_key(self, pitch: int):
        self.pressed_keys.discard(pitch)

    def set_target_keys(self, pitches: Set[int]):
        self.target_keys = pitches

    def draw(self, surface: pygame.Surface):
        # 1. Gambar tuts putih
        for p, r in self.white_rects.items():
            is_active = p in self.pressed_keys
            is_target = p in self.target_keys

            if is_active:
                color = COLOR_WHITE_KEY_PRESSED
            elif is_target:
                color = (200, 240, 255)
            else:
                color = COLOR_WHITE_KEY

            pygame.draw.rect(surface, color, r, border_radius=4)
            pygame.draw.rect(surface, COLOR_KEY_BORDER, r, width=1, border_radius=4)

            # Tampilkan label nama nada C (C3, C4, C5)
            if p % 12 == 0:
                txt = self.font.render(get_note_name(p), True, (120, 125, 140))
                tx = r.centerx - txt.get_width() // 2
                ty = r.bottom - txt.get_height() - 4
                surface.blit(txt, (tx, ty))

        # 2. Gambar tuts hitam di lapisan atas
        for p, r in self.black_rects.items():
            is_active = p in self.pressed_keys
            is_target = p in self.target_keys

            if is_active:
                color = COLOR_BLACK_KEY_PRESSED
            elif is_target:
                color = (90, 180, 240)
            else:
                color = COLOR_BLACK_KEY

            pygame.draw.rect(surface, color, r, border_bottom_left_radius=3, border_bottom_right_radius=3)
            pygame.draw.rect(surface, (15, 15, 20), r, width=1, border_bottom_left_radius=3, border_bottom_right_radius=3)
