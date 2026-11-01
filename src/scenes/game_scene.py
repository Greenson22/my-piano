import os
import pygame
from ..audio.sound_synth import synth_instance
from ..audio.midi_io import midi_manager
from ..audio.midi_parser import parse_midi_file
from ..entities.piano_keyboard import PianoKeyboard
from ..entities.falling_note import FallingNote
from ..entities.mascot import MascotSunflower
from ..utils.constants import (
    COLOR_BG_DARK, COLOR_TEXT_WHITE, COLOR_TEXT_MUTED,
    COLOR_ACCENT_BLUE, COLOR_ACCENT_PINK, COLOR_ACCENT_GOLD,
    COLOR_RIGHT_HAND, COLOR_LEFT_HAND
)

# Pemetaan tombol keyboard laptop ke pitch MIDI (C3 ke E5)
KEYBOARD_MAP = {
    pygame.K_z: 48, pygame.K_s: 49, pygame.K_x: 50, pygame.K_d: 51,
    pygame.K_c: 52, pygame.K_v: 53, pygame.K_g: 54, pygame.K_b: 55,
    pygame.K_h: 56, pygame.K_n: 57, pygame.K_j: 58, pygame.K_m: 59,
    pygame.K_q: 60, pygame.K_2: 61, pygame.K_w: 62, pygame.K_3: 63,
    pygame.K_e: 64, pygame.K_r: 65, pygame.K_5: 66, pygame.K_t: 67,
    pygame.K_6: 68, pygame.K_y: 69, pygame.K_7: 70, pygame.K_u: 71,
    pygame.K_i: 72, pygame.K_9: 73, pygame.K_o: 74, pygame.K_0: 75,
    pygame.K_p: 76
}

class GameScene:
    """
    Layar Utama Permainan & Pembelajaran Piano Klasik:
    - Falling notes (Synthesia style)
    - Mode 'Wait for Me' (menunggu tuts benar) & Strict Rhythm
    - Pemisahan tangan kanan / kiri
    - Maskot bunga matahari interaktif
    - Suara langsung dari speaker laptop
    """

    def __init__(self, screen, clock, midi_path: str = None):
        self.screen = screen
        self.clock = clock
        self.width, self.height = screen.get_size()

        # Posisi Tuts Piano di bagian bawah
        kb_height = 135
        kb_y = self.height - kb_height - 10
        self.keyboard = PianoKeyboard(x=40, y=kb_y, width=self.width - 240, height=kb_height)
        self.hit_line_y = float(kb_y)

        # Maskot Bunga Matahari di samping kanan tuts piano
        self.mascot = MascotSunflower(x=self.width - 100, y=self.height - 110, base_radius=38)

        # Muat Not Balok dari File MIDI
        if not midi_path or not os.path.exists(midi_path):
            midi_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "midi")
            files = [os.path.join(midi_dir, f) for f in os.listdir(midi_dir) if f.endswith(".mid")]
            midi_path = files[0] if files else ""

        self.midi_path = midi_path
        self.all_events = parse_midi_file(midi_path) if midi_path else []

        # Buat Falling Note entities
        self.falling_notes = []
        for ev in self.all_events:
            x = self.keyboard.get_pitch_x(ev.pitch)
            fn = FallingNote(ev, x=x, width=18.0)
            self.falling_notes.append(fn)

        # Pengaturan Game & Kecepatan
        self.mode = "wait"        # "wait" atau "rhythm"
        self.hand_filter = "all"   # "all", "right", "left"
        self.speed = 1.0           # 0.5 sampai 1.2
        self.pixels_per_sec = 140.0

        # Waktu & Progress
        self.current_time = 0.0
        self.is_paused = False
        self.score = 0
        self.combo = 0
        self.accuracy_text = ""
        self.accuracy_timer = 0.0

        # Font
        self.font_hud = pygame.font.SysFont("Segoe UI", 16, bold=True)
        self.font_score = pygame.font.SysFont("Segoe UI", 22, bold=True)
        self.font_big = pygame.font.SysFont("Segoe UI", 28, bold=True)

        # Register callback MIDI hardware jika ada
        midi_manager.register_callback(self.on_midi_input)

    def on_midi_input(self, event_type: str, pitch: int, velocity: int):
        if event_type == 'note_on' and velocity > 0:
            self.handle_press(pitch, velocity)
        elif event_type == 'note_off':
            self.handle_release(pitch)

    def handle_press(self, pitch: int, velocity: int = 90):
        self.keyboard.press_key(pitch)
        synth_instance.play_note(pitch, velocity)
        midi_manager.send_note_on(pitch, velocity)

        # Evaluasi Hit pada nada yang sedang aktif di hit line
        hit_found = False
        for fn in self.falling_notes:
            if fn.event.hit:
                continue
            if self.hand_filter != "all" and fn.event.hand != self.hand_filter:
                continue

            time_diff = abs(fn.event.start_time - self.current_time)
            if fn.event.pitch == pitch and time_diff < 0.28:
                fn.event.hit = True
                hit_found = True
                self.combo += 1
                self.score += int(100 * self.speed)
                self.accuracy_text = "PERFECT!" if time_diff < 0.1 else "GREAT!"
                self.accuracy_timer = 0.8
                self.mascot.on_note_event(pitch, velocity, "hit")
                break

        if not hit_found:
            self.mascot.on_note_event(pitch, velocity, "neutral")

    def handle_release(self, pitch: int):
        self.keyboard.release_key(pitch)
        midi_manager.send_note_off(pitch)

    def run(self) -> str:
        running = True
        while running:
            dt = self.clock.tick(60) / 1000.0
            mx, my = pygame.mouse.get_pos()

            # Event loop Pygame
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    midi_manager.unregister_callback(self.on_midi_input)
                    return "quit"
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        midi_manager.unregister_callback(self.on_midi_input)
                        return "main_menu"
                    elif event.key == pygame.K_SPACE:
                        self.is_paused = not self.is_paused
                    elif event.key == pygame.K_TAB:
                        # Ganti Mode Latihan (Wait vs Rhythm)
                        self.mode = "rhythm" if self.mode == "wait" else "wait"
                    elif event.key == pygame.K_h:
                        # Ganti Filter Tangan
                        order = ["all", "right", "left"]
                        self.hand_filter = order[(order.index(self.hand_filter) + 1) % len(order)]
                    elif event.key in KEYBOARD_MAP:
                        self.handle_press(KEYBOARD_MAP[event.key], 95)
                elif event.type == pygame.KEYUP:
                    if event.key in KEYBOARD_MAP:
                        self.handle_release(KEYBOARD_MAP[event.key])

            # Update Logika Waktu
            if not self.is_paused:
                # Cek jika mode Wait: Apakah ada not yang harus ditekan tepat sekarang?
                must_wait = False
                target_pitches = set()
                if self.mode == "wait":
                    for fn in self.falling_notes:
                        if fn.event.hit:
                            continue
                        if self.hand_filter != "all" and fn.event.hand != self.hand_filter:
                            continue
                        # Jika not sudah mencapai garis hit (selisih < 0.05 detik)
                        if self.current_time >= fn.event.start_time - 0.02:
                            must_wait = True
                            target_pitches.add(fn.event.pitch)

                self.keyboard.set_target_keys(target_pitches)

                if not must_wait:
                    self.current_time += dt * self.speed

            # Update Maskot & HUD Timer
            self.mascot.update(dt)
            if self.accuracy_timer > 0:
                self.accuracy_timer -= dt

            # ---------------- DRAWING ----------------
            self.screen.fill(COLOR_BG_DARK)

            # 1. Garis Target (Hit Line) yang Bercahaya
            pygame.draw.line(self.screen, (0, 210, 255), (40, int(self.hit_line_y)), (self.width - 200, int(self.hit_line_y)), 3)
            pygame.draw.line(self.screen, (100, 240, 255), (40, int(self.hit_line_y) - 1), (self.width - 200, int(self.hit_line_y) - 1), 1)

        # 2. Gambar Balok-Balok Nada yang Jatuh (dibatasi di bawah HUD)
        hud_bottom = 75
        self.screen.set_clip(pygame.Rect(0, hud_bottom, self.width, self.height - hud_bottom))
        for fn in self.falling_notes:
            if self.hand_filter != "all" and fn.event.hand != self.hand_filter:
                continue
            # Jangan gambar yang sudah lewat jauh atau sudah ditekan
            if fn.event.hit and (self.current_time > fn.event.start_time + fn.event.duration):
                continue
            fn.draw(self.screen, self.current_time, self.pixels_per_sec, self.hit_line_y)
        self.screen.set_clip(None)

            # 3. Gambar Tuts Piano
            self.keyboard.draw(self.screen)

            # 4. Gambar Maskot Bunga Matahari
            self.mascot.draw(self.screen)

            # 5. Render HUD / Status Panel Atas
            hud_bg = pygame.Rect(40, 15, self.width - 80, 50)
            pygame.draw.rect(self.screen, (24, 26, 38), hud_bg, border_radius=8)
            pygame.draw.rect(self.screen, (50, 55, 75), hud_bg, width=1, border_radius=8)

            txt_score = self.font_score.render(f"Skor: {self.score}", True, COLOR_ACCENT_GOLD)
            txt_combo = self.font_score.render(f"Combo: {self.combo}x", True, COLOR_ACCENT_BLUE)
            mode_lbl = "WAIT MODE (Tunggu Tuts Benar)" if self.mode == "wait" else "STRICT RHYTHM MODE"
            txt_mode = self.font_hud.render(f"Mode [TAB]: {mode_lbl}", True, COLOR_TEXT_WHITE)

            hand_lbl = "KEDUA TANGAN" if self.hand_filter == "all" else ("KANAN SAJA" if self.hand_filter == "right" else "KIRI SAJA")
            txt_hand = self.font_hud.render(f"Tangan [H]: {hand_lbl}", True, COLOR_ACCENT_PINK)

            self.screen.blit(txt_score, (55, 26))
            self.screen.blit(txt_combo, (220, 26))
            self.screen.blit(txt_mode, (380, 28))
            self.screen.blit(txt_hand, (760, 28))

            # 6. Text Akurasi Animatif (PERFECT! / GREAT!)
            if self.accuracy_timer > 0:
                acc_color = (0, 230, 118) if "PERFECT" in self.accuracy_text else (255, 215, 0)
                txt_acc = self.font_big.render(self.accuracy_text, True, acc_color)
                self.screen.blit(txt_acc, (self.width // 2 - txt_acc.get_width() // 2, int(self.hit_line_y) - 60))

            # Indikator Pause
            if self.is_paused:
                pause_txt = self.font_big.render("PAUSED (Tekan [SPASI] untuk Melanjutkan)", True, (255, 80, 80))
                self.screen.blit(pause_txt, (self.width // 2 - pause_txt.get_width() // 2, self.height // 2 - 40))

            pygame.display.flip()

        midi_manager.unregister_callback(self.on_midi_input)
        return "main_menu"
