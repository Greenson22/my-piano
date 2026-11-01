# Konstanta Umum Proyek Piano Visualizer & Learning

import pygame

# Ukuran Layar Default
SCREEN_WIDTH = 1100
SCREEN_HEIGHT = 680
FPS = 60

# Rentang Nada Piano Standar (88 Keys: A0=21 sampai C8=108)
MIN_PITCH = 21
MAX_PITCH = 108

# Rentang Nada Tampilan Keyboard Default (C2=36 sampai C7=96)
# 5 Oktaf penuh (36 s/d 96) agar tuts terlihat pas, presisi, dan proporsional
KEYBOARD_MIN_PITCH = 36  # C2
KEYBOARD_MAX_PITCH = 96  # C7

NOTE_NAMES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']

# Warna Tema Modern Dark Aesthetic
COLOR_BG_DARK = (14, 15, 23)
COLOR_BG_CARD = (24, 26, 38)
COLOR_BG_LIGHTER = (34, 38, 56)

COLOR_ACCENT_BLUE = (0, 210, 255)
COLOR_ACCENT_PINK = (255, 64, 129)
COLOR_ACCENT_GOLD = (255, 193, 7)
COLOR_ACCENT_GREEN = (0, 230, 118)

COLOR_TEXT_WHITE = (245, 245, 250)
COLOR_TEXT_MUTED = (160, 165, 185)

# Warna Balok Tangan
COLOR_RIGHT_HAND = (0, 220, 255)   # Neon Cyan untuk Melodi Tangan Kanan
COLOR_LEFT_HAND = (255, 165, 0)    # Amber/Gold untuk Iringan Tangan Kiri

# Warna Tuts Piano
COLOR_WHITE_KEY = (245, 245, 247)
COLOR_WHITE_KEY_PRESSED = (170, 220, 255)
COLOR_BLACK_KEY = (28, 30, 38)
COLOR_BLACK_KEY_PRESSED = (60, 150, 220)
COLOR_KEY_BORDER = (100, 105, 125)


def get_note_name(pitch: int) -> str:
    """Mengembalikan representasi string not (misal C4, F#5)."""
    octave = (pitch // 12) - 1
    return f"{NOTE_NAMES[pitch % 12]}{octave}"


def is_black_key(pitch: int) -> bool:
    """Mengecek apakah pitch adalah tuts hitam (accidental)."""
    return (pitch % 12) in [1, 3, 6, 8, 10]
