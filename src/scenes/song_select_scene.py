import os
import pygame
from typing import List, Optional
import tkinter as tk
from tkinter import filedialog
from ..utils.constants import (
    COLOR_BG_DARK, COLOR_BG_CARD, COLOR_TEXT_WHITE,
    COLOR_TEXT_MUTED, COLOR_ACCENT_BLUE, COLOR_ACCENT_GOLD
)

class SongSelectScene:
    """Layar pemilihan lagu MIDI dari folder ./midi atau file picker kustom."""

    def __init__(self, screen, clock):
        self.screen = screen
        self.clock = clock
        self.width, self.height = screen.get_size()

        self.font_title = pygame.font.SysFont("Segoe UI", 32, bold=True)
        self.font_item = pygame.font.SysFont("Segoe UI", 18, bold=True)
        self.font_desc = pygame.font.SysFont("Segoe UI", 13)
        self.font_btn = pygame.font.SysFont("Segoe UI", 16, bold=True)

        self.midi_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "midi")
        self.refresh_song_list()
        self.selected_idx = 0

    def refresh_song_list(self):
        os.makedirs(self.midi_dir, exist_ok=True)
        self.songs: List[str] = [
            f for f in os.listdir(self.midi_dir)
            if f.lower().endswith(".mid") or f.lower().endswith(".midi")
        ]

    def browse_custom_file(self) -> Optional[str]:
        """Membuka dialog file explorer Windows untuk memilih file MIDI."""
        try:
            root = tk.Tk()
            root.withdraw()
            root.attributes('-topmost', True)
            file_path = filedialog.askopenfilename(
                title="Pilih File Musik MIDI",
                filetypes=[("MIDI files", "*.mid *.midi")]
            )
            root.destroy()
            return file_path if file_path else None
        except Exception:
            return None

    def run(self) -> str:
        running = True
        while running:
            self.screen.fill(COLOR_BG_DARK)
            mx, my = pygame.mouse.get_pos()

            # Header
            title = self.font_title.render("Pilih Lagu Klasik (MIDI)", True, COLOR_TEXT_WHITE)
            sub = self.font_desc.render("Pilih lagu dari koleksi atau klik 'Buka File dari Komputer' untuk menambah file baru", True, COLOR_TEXT_MUTED)
            self.screen.blit(title, (50, 35))
            self.screen.blit(sub, (50, 78))

            # Tombol Buka File Luar
            btn_browse = pygame.Rect(self.width - 290, 40, 240, 42)
            hover_browse = btn_browse.collidepoint(mx, my)
            pygame.draw.rect(self.screen, (0, 160, 210) if hover_browse else (0, 120, 170), btn_browse, border_radius=8)
            bt_txt = self.font_btn.render("+ Buka File dari Komputer", True, COLOR_TEXT_WHITE)
            self.screen.blit(bt_txt, (btn_browse.centerx - bt_txt.get_width() // 2, btn_browse.centery - bt_txt.get_height() // 2))

            # Daftar Lagu (Card List)
            list_y = 125
            card_h = 65
            gap = 12
            btn_w = self.width - 100

            if not self.songs:
                empty_txt = self.font_item.render("Belum ada file di folder /midi. Klik tombol di atas untuk memilih file!", True, (255, 120, 120))
                self.screen.blit(empty_txt, (50, 160))
            else:
                for i, song in enumerate(self.songs):
                    cy = list_y + i * (card_h + gap)
                    rect = pygame.Rect(50, cy, btn_w, card_h)
                    is_hover = rect.collidepoint(mx, my)
                    is_selected = (i == self.selected_idx)

                    bg_col = (40, 45, 65) if (is_hover or is_selected) else COLOR_BG_CARD
                    border_col = COLOR_ACCENT_BLUE if is_selected else ((70, 75, 100) if is_hover else (45, 50, 70))

                    pygame.draw.rect(self.screen, bg_col, rect, border_radius=10)
                    pygame.draw.rect(self.screen, border_col, rect, width=2 if (is_selected or is_hover) else 1, border_radius=10)

                    # Icon & Judul
                    title_clean = os.path.splitext(song)[0]
                    t_surf = self.font_item.render(f"🎼  {title_clean}", True, COLOR_TEXT_WHITE)
                    d_surf = self.font_desc.render(f"Format: MIDI File  |  Lokasi: midi/{song}", True, COLOR_TEXT_MUTED)
                    self.screen.blit(t_surf, (rect.x + 20, rect.y + 12))
                    self.screen.blit(d_surf, (rect.x + 20, rect.y + 38))

                    # Label "MAIN"
                    play_lbl = self.font_btn.render("Pilih ▶", True, COLOR_ACCENT_GOLD if (is_hover or is_selected) else (100, 105, 130))
                    self.screen.blit(play_lbl, (rect.right - 80, rect.y + 20))

            # Tombol Kembali
            btn_back = pygame.Rect(50, self.height - 65, 140, 42)
            hover_back = btn_back.collidepoint(mx, my)
            pygame.draw.rect(self.screen, (220, 50, 70) if hover_back else (160, 40, 55), btn_back, border_radius=8)
            back_txt = self.font_btn.render("Kembali [ESC]", True, COLOR_TEXT_WHITE)
            self.screen.blit(back_txt, (btn_back.centerx - back_txt.get_width() // 2, btn_back.centery - back_txt.get_height() // 2))

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return "quit"
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return "main_menu"
                    elif event.key == pygame.K_UP and self.songs:
                        self.selected_idx = (self.selected_idx - 1) % len(self.songs)
                    elif event.key == pygame.K_DOWN and self.songs:
                        self.selected_idx = (self.selected_idx + 1) % len(self.songs)
                    elif event.key in (pygame.K_RETURN, pygame.K_SPACE) and self.songs:
                        return os.path.join(self.midi_dir, self.songs[self.selected_idx])
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if btn_back.collidepoint(event.pos):
                        return "main_menu"
                    if btn_browse.collidepoint(event.pos):
                        chosen = self.browse_custom_file()
                        if chosen:
                            return chosen
                    # Cek klik lagu
                    if self.songs:
                        for i, song in enumerate(self.songs):
                            cy = list_y + i * (card_h + gap)
                            rect = pygame.Rect(50, cy, btn_w, card_h)
                            if rect.collidepoint(event.pos):
                                return os.path.join(self.midi_dir, song)

            pygame.display.flip()
            self.clock.tick(60)

        return "main_menu"
