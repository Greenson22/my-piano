import pygame
from ..audio.sound_synth import synth_instance
from ..audio.midi_io import midi_manager
from ..utils.constants import (
    COLOR_BG_DARK, COLOR_BG_CARD, COLOR_TEXT_WHITE,
    COLOR_TEXT_MUTED, COLOR_ACCENT_BLUE, COLOR_ACCENT_GOLD
)

class SettingsScene:
    """Halaman Pengaturan Suara Laptop, Preset Piano, dan MIDI Port."""

    def __init__(self, screen, clock):
        self.screen = screen
        self.clock = clock
        self.width, self.height = screen.get_size()

        self.font_title = pygame.font.SysFont("Segoe UI", 32, bold=True)
        self.font_label = pygame.font.SysFont("Segoe UI", 18, bold=True)
        self.font_val = pygame.font.SysFont("Segoe UI", 16)

        self.input_ports = midi_manager.get_available_inputs()
        self.output_ports = midi_manager.get_available_outputs()
        self.sel_in_idx = 0
        self.sel_out_idx = 0

    def run(self) -> str:
        running = True
        while running:
            self.screen.fill(COLOR_BG_DARK)
            mx, my = pygame.mouse.get_pos()

            # Render Judul
            title = self.font_title.render("Pengaturan Suara & MIDI", True, COLOR_TEXT_WHITE)
            self.screen.blit(title, (50, 40))

            # 1. Preset Suara Laptop
            card_preset = pygame.Rect(50, 110, self.width - 100, 110)
            pygame.draw.rect(self.screen, COLOR_BG_CARD, card_preset, border_radius=10)
            lbl = self.font_label.render("1. Karakter Suara Laptop (Internal Synth)", True, COLOR_ACCENT_BLUE)
            self.screen.blit(lbl, (card_preset.x + 20, card_preset.y + 15))

            preset_name = synth_instance.current_preset_name
            p_txt = self.font_val.render(f"Pilihan Saat Ini:  [ {preset_name} ]", True, COLOR_TEXT_WHITE)
            self.screen.blit(p_txt, (card_preset.x + 20, card_preset.y + 55))

            # Tombol Ganti Preset
            btn_prev = pygame.Rect(card_preset.right - 260, card_preset.y + 50, 110, 38)
            btn_next = pygame.Rect(card_preset.right - 130, card_preset.y + 50, 110, 38)

            for btn, label in [(btn_prev, "< Suara Lain"), (btn_next, "Suara Lain >")]:
                hover = btn.collidepoint(mx, my)
                pygame.draw.rect(self.screen, (50, 55, 75) if hover else (35, 40, 55), btn, border_radius=6)
                pygame.draw.rect(self.screen, COLOR_ACCENT_BLUE if hover else (80, 85, 110), btn, 1, border_radius=6)
                bt = self.font_val.render(label, True, COLOR_TEXT_WHITE)
                self.screen.blit(bt, (btn.centerx - bt.get_width() // 2, btn.centery - bt.get_height() // 2))

            # 2. Perangkat Input MIDI
            card_in = pygame.Rect(50, 240, self.width - 100, 110)
            pygame.draw.rect(self.screen, COLOR_BG_CARD, card_in, border_radius=10)
            lbl_in = self.font_label.render("2. Keyboard / Piano MIDI Input", True, COLOR_ACCENT_GOLD)
            self.screen.blit(lbl_in, (card_in.x + 20, card_in.y + 15))

            cur_in_name = self.input_ports[self.sel_in_idx] if self.input_ports else "Tidak ada perangkat terdeteksi (Gunakan Keyboard PC)"
            txt_in = self.font_val.render(f"Device: {cur_in_name}", True, COLOR_TEXT_MUTED)
            self.screen.blit(txt_in, (card_in.x + 20, card_in.y + 55))

            # 3. Info Keyboard PC
            card_info = pygame.Rect(50, 370, self.width - 100, 140)
            pygame.draw.rect(self.screen, COLOR_BG_CARD, card_info, border_radius=10)
            lbl_info = self.font_label.render("3. Kontrol Tombol Cepat Keyboard Laptop / Komputer", True, (0, 230, 118))
            self.screen.blit(lbl_info, (card_info.x + 20, card_info.y + 15))

            keys_help = [
                "• Baris tuts putih: Z, X, C, V, B, N, M, Q, W, E, R, T, Y, U",
                "• Baris tuts hitam (#): S, D, G, H, J, 2, 3, 5, 6, 7",
                "• Suara piano internal otomatis aktif saat bermain!",
                "• Tekan [ESC] kapan saja untuk kembali ke Menu Utama."
            ]
            for i, h_text in enumerate(keys_help):
                ht = self.font_val.render(h_text, True, COLOR_TEXT_MUTED)
                self.screen.blit(ht, (card_info.x + 20, card_info.y + 45 + (i * 22)))

            # Tombol Kembali
            btn_back = pygame.Rect(50, self.height - 70, 140, 42)
            hover_back = btn_back.collidepoint(mx, my)
            pygame.draw.rect(self.screen, (220, 50, 70) if hover_back else (160, 40, 55), btn_back, border_radius=8)
            bt_txt = self.font_label.render("Kembali [ESC]", True, COLOR_TEXT_WHITE)
            self.screen.blit(bt_txt, (btn_back.centerx - bt_txt.get_width() // 2, btn_back.centery - bt_txt.get_height() // 2))

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return "quit"
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return "main_menu"
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if btn_back.collidepoint(event.pos):
                        return "main_menu"
                    if btn_prev.collidepoint(event.pos):
                        synth_instance.cycle_preset(-1)
                        # Mainkan nada C4 untuk demo suara
                        synth_instance.play_note(60, 100)
                    elif btn_next.collidepoint(event.pos):
                        synth_instance.cycle_preset(1)
                        synth_instance.play_note(60, 100)

            pygame.display.flip()
            self.clock.tick(60)

        return "main_menu"
