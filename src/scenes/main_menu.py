import pygame
from ..utils.constants import (
    COLOR_BG_DARK, COLOR_BG_CARD, COLOR_TEXT_WHITE,
    COLOR_TEXT_MUTED, COLOR_ACCENT_BLUE, COLOR_ACCENT_PINK, COLOR_ACCENT_GOLD
)

class MainMenuScene:
    """Menu Utama Aplikasi dengan UI Modern & Elegan."""

    def __init__(self, screen, clock):
        self.screen = screen
        self.clock = clock
        self.width, self.height = screen.get_size()

        self.font_title = pygame.font.SysFont("Segoe UI", 42, bold=True)
        self.font_subtitle = pygame.font.SysFont("Segoe UI", 18)
        self.font_btn = pygame.font.SysFont("Segoe UI", 20, bold=True)
        self.font_desc = pygame.font.SysFont("Segoe UI", 14)

    def run(self) -> str:
        buttons = [
            {
                "id": "song_select",
                "title": "1. Belajar Piano Klasik (Game)",
                "desc": "Falling notes, Wait Mode, latihan tangan kanan/kiri & maskot bunga",
                "color": COLOR_ACCENT_BLUE
            },
            {
                "id": "visualizer",
                "title": "2. Free Play & Visualizer",
                "desc": "Mode visualisasi bebas klasik untuk bermain tanpa batas lagu",
                "color": COLOR_ACCENT_PINK
            },
            {
                "id": "settings",
                "title": "3. Pengaturan Suara & MIDI",
                "desc": "Pilih karakter suara laptop (Grand Piano, Upright, dll.) & input MIDI",
                "color": COLOR_ACCENT_GOLD
            },
            {
                "id": "quit",
                "title": "4. Keluar",
                "desc": "Tutup aplikasi piano",
                "color": (220, 70, 70)
            }
        ]

        running = True
        while running:
            self.screen.fill(COLOR_BG_DARK)
            mx, my = pygame.mouse.get_pos()

            # Render Judul & Subjudul
            title = self.font_title.render("PIANO MASTER CLASSIC", True, COLOR_TEXT_WHITE)
            sub = self.font_subtitle.render("Aplikasi Interaktif Belajar Lagu Klasik & Visualizer Piano", True, COLOR_TEXT_MUTED)
            self.screen.blit(title, (self.width // 2 - title.get_width() // 2, 60))
            self.screen.blit(sub, (self.width // 2 - sub.get_width() // 2, 120))

            # Render Tombol Menu
            btn_w, btn_h = 580, 80
            start_y = 180
            gap_y = 100

            action_clicked = None

            for i, b in enumerate(buttons):
                by = start_y + i * gap_y
                bx = self.width // 2 - btn_w // 2
                rect = pygame.Rect(bx, by, btn_w, btn_h)

                is_hover = rect.collidepoint(mx, my)

                # Card Box
                bg_col = (35, 38, 55) if is_hover else COLOR_BG_CARD
                pygame.draw.rect(self.screen, bg_col, rect, border_radius=12)
                border_col = b["color"] if is_hover else (50, 55, 75)
                pygame.draw.rect(self.screen, border_col, rect, width=2 if is_hover else 1, border_radius=12)

                # Teks Tombol
                t_surf = self.font_btn.render(b["title"], True, COLOR_TEXT_WHITE)
                d_surf = self.font_desc.render(b["desc"], True, COLOR_TEXT_MUTED)
                self.screen.blit(t_surf, (rect.x + 25, rect.y + 16))
                self.screen.blit(d_surf, (rect.x + 25, rect.y + 46))

                # Indikator panah di kanan
                arrow = self.font_btn.render(">", True, b["color"] if is_hover else (90, 95, 120))
                self.screen.blit(arrow, (rect.right - 35, rect.y + 26))

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return "quit"
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    for i, b in enumerate(buttons):
                        by = start_y + i * gap_y
                        bx = self.width // 2 - btn_w // 2
                        rect = pygame.Rect(bx, by, btn_w, btn_h)
                        if rect.collidepoint(event.pos):
                            return b["id"]
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_1:
                        return "song_select"
                    elif event.key == pygame.K_2:
                        return "visualizer"
                    elif event.key == pygame.K_3:
                        return "settings"
                    elif event.key in (pygame.K_4, pygame.K_ESCAPE):
                        return "quit"

            pygame.display.flip()
            self.clock.tick(60)

        return "quit"
