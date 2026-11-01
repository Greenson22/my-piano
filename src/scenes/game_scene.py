import os
import pygame
from ..audio.chunk_manager import chunk_manager
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
    Layar Utama Permainan & Pembelajaran Piano Klasik dengan Chunking Manager:
    - Chunking Manager: Simpan, pilih/jump, ubah nama, tambah, dan reset chunk.
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

        # Timeline diletakkan di bawah HUD atas agar tampilan layar tuts bersih dan lega
        self.timeline_rect = pygame.Rect(40, 75, self.width - 80, 8)

        # Waktu & Progress
        self.current_time = 0.0
        self.is_paused = False
        self.is_dragging_timeline = False
        self.score = 0
        self.combo = 0
        self.accuracy_text = ""
        self.accuracy_timer = 0.0

        # Maskot Bunga Matahari di samping kanan tuts piano
        self.mascot = MascotSunflower(x=self.width - 100, y=self.height - 110, base_radius=38)

        # Muat Not Balok dari File MIDI
        if not midi_path or not os.path.exists(midi_path):
            midi_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "midi")
            files = [os.path.join(midi_dir, f) for f in os.listdir(midi_dir) if f.endswith(".mid")]
            midi_path = files[0] if files else ""

        self.midi_path = midi_path
        self.all_events = parse_midi_file(midi_path) if midi_path else []

        # Hitung durasi total lagu
        self.total_duration = 0.0
        if self.all_events:
            self.total_duration = max(ev.start_time + ev.duration for ev in self.all_events) + 2.0
        self.total_duration = max(10.0, self.total_duration)

        # Buat Falling Note entities
        self.falling_notes = []
        for ev in self.all_events:
            x = self.keyboard.get_pitch_x(ev.pitch)
            fn = FallingNote(ev, x=x, width=18.0)
            self.falling_notes.append(fn)

        # Inisialisasi Chunk Manager
        self.chunks = chunk_manager.get_chunks_for_song(self.midi_path, self.total_duration)
        self.active_chunk_idx = 0

        # Pengaturan Game & Kecepatan
        self.mode = "wait"        # "wait" atau "rhythm"
        self.hand_filter = "all"   # "all", "right", "left"
        self.speed = 1.0           # 0.5, 0.75, 1.0, 1.25
        self.pixels_per_sec = 140.0

        # Status Chunking
        self.chunk_enabled = False
        self.chunk_repeat_count = 0
        self.chunk_scroll_offset = 0  # Halaman/offset scroll daftar chunking
        self._sync_chunk_bounds()

        # Modal/Overlay Dialog State
        self.show_chunk_menu = False
        self.show_confirm_reset = False
        self.renaming_chunk_idx = None
        self.rename_text = ""

        # Font
        self.font_hud = pygame.font.SysFont("Segoe UI", 16, bold=True)
        self.font_score = pygame.font.SysFont("Segoe UI", 22, bold=True)
        self.font_big = pygame.font.SysFont("Segoe UI", 28, bold=True)
        self.font_time = pygame.font.SysFont("Segoe UI", 12, bold=True)
        self.font_modal = pygame.font.SysFont("Segoe UI", 15, bold=True)
        self.font_modal_sub = pygame.font.SysFont("Segoe UI", 13)

        # Register callback MIDI hardware jika ada
        midi_manager.register_callback(self.on_midi_input)

    def _sync_chunk_bounds(self):
        """Menyelaraskan batas chunk_start dan chunk_end dengan chunk yang aktif."""
        if self.chunks and 0 <= self.active_chunk_idx < len(self.chunks):
            cur = self.chunks[self.active_chunk_idx]
            self.chunk_start = cur["start"]
            self.chunk_end = cur["end"]
        else:
            self.chunk_start = 0.0
            self.chunk_end = min(8.0, self.total_duration)

    def jump_to_chunk(self, chunk_index: int):
        """Langsung melompat ke awal chunk tertentu dan mengaktifkannya."""
        if 0 <= chunk_index < len(self.chunks):
            self.active_chunk_idx = chunk_index
            self._sync_chunk_bounds()
            self.chunk_enabled = True
            self.chunk_repeat_count = 0
            self.seek_to_time(self.chunk_start)
            self.accuracy_text = f"LOMPAT KE: {self.chunks[chunk_index]['name']}"
            self.accuracy_timer = 1.5

    def seek_to_time(self, target_time: float):
        """Memindahkan playback ke detik tertentu dan mereset status hit not balok."""
        self.current_time = max(0.0, min(self.total_duration, target_time))
        for fn in self.falling_notes:
            if fn.event.start_time >= self.current_time - 0.05:
                fn.event.hit = False
            else:
                fn.event.hit = True

    def on_midi_input(self, event_type: str, pitch: int, velocity: int):
        if event_type == 'note_on' and velocity > 0:
            self.handle_press(pitch, velocity)
        elif event_type == 'note_off':
            self.handle_release(pitch)

    def handle_press(self, pitch: int, velocity: int = 90):
        self.keyboard.press_key(pitch)
        synth_instance.play_note(pitch, velocity)
        midi_manager.send_note_on(pitch, velocity)

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

                # 1. Handle Input saat Rename Modal Aktif
                if self.renaming_chunk_idx is not None:
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_RETURN:
                            if self.rename_text.strip():
                                chunk_manager.rename_chunk(self.midi_path, self.renaming_chunk_idx, self.rename_text.strip())
                                self.chunks = chunk_manager.get_chunks_for_song(self.midi_path, self.total_duration)
                            self.renaming_chunk_idx = None
                        elif event.key == pygame.K_ESCAPE:
                            self.renaming_chunk_idx = None
                        elif event.key == pygame.K_BACKSPACE:
                            self.rename_text = self.rename_text[:-1]
                        else:
                            if len(self.rename_text) < 32 and event.unicode:
                                self.rename_text += event.unicode
                    continue

                # 2. Handle Input saat Konfirmasi Reset Aktif
                if self.show_confirm_reset:
                    if event.type == pygame.KEYDOWN:
                        if event.key in (pygame.K_y, pygame.K_RETURN):
                            self.chunks = chunk_manager.reset_chunks_for_song(self.midi_path, self.total_duration)
                            self.active_chunk_idx = 0
                            self._sync_chunk_bounds()
                            self.show_confirm_reset = False
                        elif event.key in (pygame.K_n, pygame.K_ESCAPE):
                            self.show_confirm_reset = False
                    elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                        # Modal dialog click handling handled in draw_confirm_modal
                        pass
                    continue

                # 3. Handle Input Normal Game
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        if self.show_chunk_menu:
                            self.show_chunk_menu = False
                        else:
                            midi_manager.unregister_callback(self.on_midi_input)
                            return "main_menu"
                    elif event.key == pygame.K_SPACE:
                        self.is_paused = not self.is_paused
                    elif event.key == pygame.K_UP and self.show_chunk_menu:
                        # Scroll list chunk ke atas
                        self.chunk_scroll_offset = max(0, self.chunk_scroll_offset - 1)
                    elif event.key == pygame.K_DOWN and self.show_chunk_menu:
                        # Scroll list chunk ke bawah
                        max_scroll = max(0, len(self.chunks) - 6)
                        self.chunk_scroll_offset = min(max_scroll, self.chunk_scroll_offset + 1)
                    elif event.key == pygame.K_s:
                        # Ganti Kecepatan Tempo (Speed Slider 50% -> 75% -> 100% -> 125%)
                        speeds = [0.5, 0.75, 1.0, 1.25]
                        cur_idx = speeds.index(self.speed) if self.speed in speeds else 2
                        self.speed = speeds[(cur_idx + 1) % len(speeds)]
                        self.accuracy_text = f"TEMPO: {int(self.speed * 100)}%"
                        self.accuracy_timer = 1.0
                    elif event.key == pygame.K_m:
                        # Buka / Tutup Daftar Chunking Manager Modal
                        self.show_chunk_menu = not self.show_chunk_menu
                    elif event.key == pygame.K_c:
                        # Toggle Chunking Mode On/Off
                        self.chunk_enabled = not self.chunk_enabled
                        if self.chunk_enabled:
                            if self.current_time < self.chunk_start or self.current_time > self.chunk_end:
                                self.seek_to_time(self.chunk_start)
                    elif event.key == pygame.K_n:
                        # Lompat ke Chunk Berikutnya
                        if self.chunks:
                            self.jump_to_chunk((self.active_chunk_idx + 1) % len(self.chunks))
                    elif event.key == pygame.K_p:
                        # Lompat ke Chunk Sebelumnya
                        if self.chunks:
                            self.jump_to_chunk((self.active_chunk_idx - 1) % len(self.chunks))
                    elif event.key == pygame.K_a:
                        # Set Titik Mulai Chunking (Point A)
                        self.chunk_start = max(0.0, self.current_time)
                        if self.chunk_end <= self.chunk_start:
                            self.chunk_end = min(self.total_duration, self.chunk_start + 4.0)
                        self.chunk_enabled = True
                        chunk_manager.update_chunk_bounds(self.midi_path, self.active_chunk_idx, self.chunk_start, self.chunk_end)
                    elif event.key == pygame.K_b:
                        # Set Titik Akhir Chunking (Point B)
                        self.chunk_end = min(self.total_duration, max(self.chunk_start + 1.0, self.current_time))
                        self.chunk_enabled = True
                        chunk_manager.update_chunk_bounds(self.midi_path, self.active_chunk_idx, self.chunk_start, self.chunk_end)
                    elif event.key == pygame.K_r:
                        # Reset pengulangan ke awal chunk
                        self.seek_to_time(self.chunk_start if self.chunk_enabled else 0.0)
                        self.chunk_repeat_count = 0
                    elif event.key == pygame.K_LEFT:
                        self.seek_to_time(self.current_time - 3.0)
                    elif event.key == pygame.K_RIGHT:
                        self.seek_to_time(self.current_time + 3.0)
                    elif event.key == pygame.K_TAB:
                        self.mode = "rhythm" if self.mode == "wait" else "wait"
                    elif event.key == pygame.K_h:
                        order = ["all", "right", "left"]
                        self.hand_filter = order[(order.index(self.hand_filter) + 1) % len(order)]
                    elif event.key in KEYBOARD_MAP:
                        self.handle_press(KEYBOARD_MAP[event.key], 95)
                elif event.type == pygame.KEYUP:
                    if event.key in KEYBOARD_MAP:
                        self.handle_release(KEYBOARD_MAP[event.key])

                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    # Klik tombol Chunk Menu di HUD
                    btn_chunk_rect = pygame.Rect(self.width - 240, 22, 180, 36)
                    if btn_chunk_rect.collidepoint(event.pos):
                        self.show_chunk_menu = not self.show_chunk_menu
                        continue

                    # Klik di dalam daftar Chunking Menu
                    if self.show_chunk_menu:
                        # Handle klik di daftar chunk modal
                        modal_w, modal_h = 480, 340
                        modal_x = self.width // 2 - modal_w // 2
                        modal_y = self.height // 2 - modal_h // 2
                        modal_rect = pygame.Rect(modal_x, modal_y, modal_w, modal_h)

                        if modal_rect.collidepoint(event.pos):
                            # Cek tombol Reset Chunking
                            btn_rst = pygame.Rect(modal_x + 20, modal_y + modal_h - 48, 140, 32)
                            if btn_rst.collidepoint(event.pos):
                                self.show_confirm_reset = True
                                continue

                            # Cek tombol Tambah Bagian Baru
                            btn_add = pygame.Rect(modal_x + 175, modal_y + modal_h - 48, 160, 32)
                            if btn_add.collidepoint(event.pos):
                                new_c = chunk_manager.add_custom_chunk(
                                    self.midi_path, self.current_time, min(self.total_duration, self.current_time + 6.0)
                                )
                                self.chunks = chunk_manager.get_chunks_for_song(self.midi_path, self.total_duration)
                                self.jump_to_chunk(len(self.chunks) - 1)
                                continue

                            # Cek tombol Tutup
                            btn_cls = pygame.Rect(modal_right := modal_x + modal_w - 110, modal_y + modal_h - 48, 90, 32)
                            if btn_cls.collidepoint(event.pos):
                                self.show_chunk_menu = False
                                continue

                            # Cek klik item chunk untuk jump / rename
                            for rel_i, ch in enumerate(self.chunks[self.chunk_scroll_offset : self.chunk_scroll_offset + 6]):
                                i = self.chunk_scroll_offset + rel_i
                                iy = modal_y + 60 + rel_i * 36
                                item_rect = pygame.Rect(modal_x + 20, iy, modal_w - 110, 30)
                                edit_rect = pygame.Rect(modal_x + modal_w - 85, iy, 65, 30)

                                if edit_rect.collidepoint(event.pos):
                                    self.renaming_chunk_idx = i
                                    self.rename_text = ch["name"]
                                    break
                                elif item_rect.collidepoint(event.pos):
                                    self.jump_to_chunk(i)
                                    self.show_chunk_menu = False
                                    break
                            continue
                        else:
                            self.show_chunk_menu = False

                    # Deteksi klik di timeline bar
                    click_rect = pygame.Rect(
                        self.timeline_rect.x, self.timeline_rect.y - 8,
                        self.timeline_rect.width, self.timeline_rect.height + 16
                    )
                    if click_rect.collidepoint(event.pos):
                        self.is_dragging_timeline = True
                        rel_x = max(0.0, min(1.0, (event.pos[0] - self.timeline_rect.x) / self.timeline_rect.width))
                        self.seek_to_time(rel_x * self.total_duration)

                elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                    self.is_dragging_timeline = False
                elif event.type == pygame.MOUSEWHEEL and self.show_chunk_menu:
                    # Scroll mouse wheel pada daftar chunk
                    max_scroll = max(0, len(self.chunks) - 6)
                    self.chunk_scroll_offset = max(0, min(max_scroll, self.chunk_scroll_offset - event.y))
                elif event.type == pygame.MOUSEMOTION and self.is_dragging_timeline:
                    rel_x = max(0.0, min(1.0, (event.pos[0] - self.timeline_rect.x) / self.timeline_rect.width))
                    self.seek_to_time(rel_x * self.total_duration)

            # Update Logika Waktu
            if not self.is_paused and not self.show_chunk_menu and not self.show_confirm_reset:
                must_wait = False
                target_pitches = set()
                if self.mode == "wait":
                    for fn in self.falling_notes:
                        if fn.event.hit:
                            continue
                        if self.hand_filter != "all" and fn.event.hand != self.hand_filter:
                            continue
                        if self.current_time >= fn.event.start_time - 0.02:
                            must_wait = True
                            target_pitches.add(fn.event.pitch)

                self.keyboard.set_target_keys(target_pitches)

                if not must_wait:
                    self.current_time += dt * self.speed

                # Logika Loop Chunking: Jika mencapai titik akhir chunk_end, ulangi otomatis ke chunk_start
                if self.chunk_enabled and self.current_time >= self.chunk_end:
                    self.chunk_repeat_count += 1
                    self.seek_to_time(self.chunk_start)
                    self.mascot.expression = "excited"
                    cur_name = self.chunks[self.active_chunk_idx]["name"] if self.chunks else "Chunk"
                    self.accuracy_text = f"LOOP #{self.chunk_repeat_count}: {cur_name}"
                    self.accuracy_timer = 1.0

            # Update Maskot & HUD Timer
            self.mascot.update(dt)
            if self.accuracy_timer > 0:
                self.accuracy_timer -= dt

            # ---------------- DRAWING ----------------
            self.screen.fill(COLOR_BG_DARK)

            # 1. Garis Target (Hit Line) yang Bercahaya
            pygame.draw.line(self.screen, (0, 210, 255), (40, int(self.hit_line_y)), (self.width - 200, int(self.hit_line_y)), 3)
            pygame.draw.line(self.screen, (100, 240, 255), (40, int(self.hit_line_y) - 1), (self.width - 200, int(self.hit_line_y) - 1), 1)

            # 1b. Render Timeline Bar Interaktif (Seek Bar di Bawah HUD)
            progress = max(0.0, min(1.0, self.current_time / self.total_duration))
            pygame.draw.rect(self.screen, (30, 34, 50), self.timeline_rect, border_radius=4)

            # Gambar highlight area A-B di timeline jika Chunking aktif
            if self.chunk_enabled:
                cA_ratio = max(0.0, min(1.0, self.chunk_start / self.total_duration))
                cB_ratio = max(0.0, min(1.0, self.chunk_end / self.total_duration))
                chunk_x = self.timeline_rect.x + (cA_ratio * self.timeline_rect.width)
                chunk_w = max(4.0, (cB_ratio - cA_ratio) * self.timeline_rect.width)
                chunk_rect = pygame.Rect(int(chunk_x), self.timeline_rect.y - 2, int(chunk_w), self.timeline_rect.height + 4)
                pygame.draw.rect(self.screen, (255, 193, 7), chunk_rect, border_radius=4)
                pygame.draw.line(self.screen, (255, 235, 59), (int(chunk_x), self.timeline_rect.y - 4), (int(chunk_x), self.timeline_rect.bottom + 4), 2)
                pygame.draw.line(self.screen, (255, 235, 59), (int(chunk_x + chunk_w), self.timeline_rect.y - 4), (int(chunk_x + chunk_w), self.timeline_rect.bottom + 4), 2)

            filled_w = int(self.timeline_rect.width * progress)
            if filled_w > 0:
                fill_rect = pygame.Rect(self.timeline_rect.x, self.timeline_rect.y, filled_w, self.timeline_rect.height)
                pygame.draw.rect(self.screen, COLOR_ACCENT_BLUE, fill_rect, border_radius=4)

            handle_x = int(self.timeline_rect.x + filled_w)
            handle_y = int(self.timeline_rect.centery)
            pygame.draw.circle(self.screen, (255, 255, 255), (handle_x, handle_y), 6)
            pygame.draw.circle(self.screen, COLOR_ACCENT_BLUE, (handle_x, handle_y), 3)

            # Format teks menit:detik & info chunking aktif di bawah timeline
            cur_m, cur_s = divmod(int(self.current_time), 60)
            tot_m, tot_s = divmod(int(self.total_duration), 60)
            c_name = self.chunks[self.active_chunk_idx]["name"] if self.chunks else "Bagian"
            chunk_status_txt = f" | CHUNK [C]: {'ON' if self.chunk_enabled else 'OFF'} ({c_name} - Loop #{self.chunk_repeat_count})"
            time_str = f"Waktu: {cur_m:02d}:{cur_s:02d} / {tot_m:02d}:{tot_s:02d}{chunk_status_txt}"
            txt_t = self.font_time.render(time_str, True, (255, 215, 0) if self.chunk_enabled else COLOR_TEXT_MUTED)
            self.screen.blit(txt_t, (self.timeline_rect.x, self.timeline_rect.bottom + 4))

            # 2. Gambar Balok-Balok Nada yang Jatuh (dibatasi di bawah bar waktu dan di atas tuts piano)
            fall_top = 100
            fall_h = int(self.hit_line_y) - fall_top
            self.screen.set_clip(pygame.Rect(0, fall_top, self.width, fall_h))
            for fn in self.falling_notes:
                if self.hand_filter != "all" and fn.event.hand != self.hand_filter:
                    continue
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
            mode_lbl = "WAIT" if self.mode == "wait" else "RHYTHM"
            txt_mode = self.font_hud.render(f"Mode [TAB]: {mode_lbl}", True, COLOR_TEXT_WHITE)

            hand_lbl = "DUAL" if self.hand_filter == "all" else ("KANAN" if self.hand_filter == "right" else "KIRI")
            txt_hand = self.font_hud.render(f"Tangan [H]: {hand_lbl}", True, COLOR_ACCENT_PINK)

            speed_lbl = f"{int(self.speed * 100)}%"
            txt_spd = self.font_hud.render(f"Tempo [S]: {speed_lbl}", True, (0, 230, 118))

            self.screen.blit(txt_score, (55, 26))
            self.screen.blit(txt_combo, (185, 26))
            self.screen.blit(txt_mode, (320, 28))
            self.screen.blit(txt_hand, (530, 28))
            self.screen.blit(txt_spd, (715, 28))

            # Tombol Kelola Chunking di HUD
            btn_chunk_rect = pygame.Rect(self.width - 240, 22, 180, 36)
            is_hover_c = btn_chunk_rect.collidepoint(mx, my)
            pygame.draw.rect(self.screen, (255, 179, 0) if is_hover_c else (210, 140, 0), btn_chunk_rect, border_radius=6)
            txt_btn_c = self.font_modal.render("Kelola Chunk [M] 📋", True, (20, 20, 25))
            self.screen.blit(txt_btn_c, (btn_chunk_rect.centerx - txt_btn_c.get_width() // 2, btn_chunk_rect.centery - txt_btn_c.get_height() // 2))

            # 6. Text Akurasi Animatif (PERFECT! / GREAT!)
            if self.accuracy_timer > 0:
                acc_color = (0, 230, 118) if "PERFECT" in self.accuracy_text else (255, 215, 0)
                txt_acc = self.font_big.render(self.accuracy_text, True, acc_color)
                self.screen.blit(txt_acc, (self.width // 2 - txt_acc.get_width() // 2, int(self.hit_line_y) - 60))

            # 7. Render Modal Chunking Menu
            if self.show_chunk_menu:
                self._draw_chunk_modal(mx, my)

            # 8. Render Modal Konfirmasi Reset
            if self.show_confirm_reset:
                self._draw_confirm_reset_modal(mx, my)

            # 9. Render Modal Ubah Nama Chunk
            if self.renaming_chunk_idx is not None:
                self._draw_rename_modal()

            # Indikator Pause
            if self.is_paused and not self.show_chunk_menu and not self.show_confirm_reset:
                pause_txt = self.font_big.render("PAUSED (Tekan [SPASI] untuk Melanjutkan)", True, (255, 80, 80))
                self.screen.blit(pause_txt, (self.width // 2 - pause_txt.get_width() // 2, self.height // 2 - 40))

            pygame.display.flip()

        midi_manager.unregister_callback(self.on_midi_input)
        return "main_menu"

    def _draw_chunk_modal(self, mx: int, my: int):
        """Menggambar dialog popup Chunking Manager (Jump, Rename, Add, Reset)."""
        dim_surf = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        dim_surf.fill((0, 0, 0, 150))
        self.screen.blit(dim_surf, (0, 0))

        modal_w, modal_h = 500, 360
        modal_x = self.width // 2 - modal_w // 2
        modal_y = self.height // 2 - modal_h // 2
        modal_rect = pygame.Rect(modal_x, modal_y, modal_w, modal_h)

        pygame.draw.rect(self.screen, (22, 24, 34), modal_rect, border_radius=12)
        pygame.draw.rect(self.screen, COLOR_ACCENT_GOLD, modal_rect, width=2, border_radius=12)

        # Judul Modal
        t_title = self.font_score.render("Daftar Chunking / Bagian Latihan", True, COLOR_TEXT_WHITE)
        t_sub = self.font_modal_sub.render("Klik nama untuk LOMPAT LANGSUNG ke bagian, atau klik [Ubah] untuk ganti nama", True, COLOR_TEXT_MUTED)
        self.screen.blit(t_title, (modal_x + 20, modal_y + 16))
        self.screen.blit(t_sub, (modal_x + 20, modal_y + 44))

        # List Bagian Chunking dengan Pagination / Scroll
        visible_chunks = self.chunks[self.chunk_scroll_offset : self.chunk_scroll_offset + 6]
        for rel_i, ch in enumerate(visible_chunks):
            i = self.chunk_scroll_offset + rel_i
            iy = modal_y + 70 + rel_i * 38
            item_rect = pygame.Rect(modal_x + 20, iy, modal_w - 110, 32)
            edit_rect = pygame.Rect(modal_x + modal_w - 85, iy, 65, 32)

            is_cur = (i == self.active_chunk_idx and self.chunk_enabled)
            h_item = item_rect.collidepoint(mx, my)
            h_edit = edit_rect.collidepoint(mx, my)

            bg_col = (45, 50, 70) if (h_item or is_cur) else (30, 33, 46)
            border_c = (0, 210, 255) if is_cur else ((70, 75, 100) if h_item else (45, 48, 65))
            pygame.draw.rect(self.screen, bg_col, item_rect, border_radius=6)
            pygame.draw.rect(self.screen, border_c, item_rect, width=1, border_radius=6)

            txt_ch = self.font_modal.render(f"▶ {ch['name']}", True, (255, 235, 59) if is_cur else COLOR_TEXT_WHITE)
            self.screen.blit(txt_ch, (item_rect.x + 10, item_rect.y + 6))

            # Edit Button
            pygame.draw.rect(self.screen, (55, 60, 85) if h_edit else (38, 42, 60), edit_rect, border_radius=6)
            pygame.draw.rect(self.screen, (100, 110, 140), edit_rect, width=1, border_radius=6)
            txt_ed = self.font_modal_sub.render("Ubah ✎", True, COLOR_ACCENT_BLUE)
            self.screen.blit(txt_ed, (edit_rect.centerx - txt_ed.get_width() // 2, edit_rect.centery - txt_ed.get_height() // 2))

            # Indikator Scroll Bar jika lebih dari 6 chunk
            if len(self.chunks) > 6:
                scroll_info = self.font_modal_sub.render(f"Halaman {self.chunk_scroll_offset + 1} - {min(len(self.chunks), self.chunk_scroll_offset + 6)} dari {len(self.chunks)} (Scroll [▲][▼] / Roda Mouse)", True, (130, 140, 165))
                self.screen.blit(scroll_info, (modal_x + 20, modal_y + modal_h - 72))

        # Bottom Bar: Tombol Reset, Tambah, Tutup
        btn_rst = pygame.Rect(modal_x + 20, modal_y + modal_h - 48, 140, 34)
        btn_add = pygame.Rect(modal_x + 170, modal_y + modal_h - 48, 175, 34)
        btn_cls = pygame.Rect(modal_x + modal_w - 110, modal_y + modal_h - 48, 90, 34)

        # Reset button
        h_rst = btn_rst.collidepoint(mx, my)
        pygame.draw.rect(self.screen, (200, 40, 60) if h_rst else (140, 30, 45), btn_rst, border_radius=6)
        t_rst = self.font_modal_sub.render("Reset Chunk ↺", True, COLOR_TEXT_WHITE)
        self.screen.blit(t_rst, (btn_rst.centerx - t_rst.get_width() // 2, btn_rst.centery - t_rst.get_height() // 2))

        # Add button
        h_add = btn_add.collidepoint(mx, my)
        pygame.draw.rect(self.screen, (0, 160, 210) if h_add else (0, 110, 160), btn_add, border_radius=6)
        t_add = self.font_modal_sub.render("+ Buat Dari Posisi Ini", True, COLOR_TEXT_WHITE)
        self.screen.blit(t_add, (btn_add.centerx - t_add.get_width() // 2, btn_add.centery - t_add.get_height() // 2))

        # Close button
        h_cls = btn_cls.collidepoint(mx, my)
        pygame.draw.rect(self.screen, (60, 65, 85) if h_cls else (40, 45, 60), btn_cls, border_radius=6)
        t_cls = self.font_modal_sub.render("Tutup [ESC]", True, COLOR_TEXT_WHITE)
        self.screen.blit(t_cls, (btn_cls.centerx - t_cls.get_width() // 2, btn_cls.centery - t_cls.get_height() // 2))

    def _draw_confirm_reset_modal(self, mx: int, my: int):
        """Modal konfirmasi sebelum melakukan reset chunking ke default."""
        dim_surf = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        dim_surf.fill((0, 0, 0, 180))
        self.screen.blit(dim_surf, (0, 0))

        cw, ch = 440, 180
        cx = self.width // 2 - cw // 2
        cy = self.height // 2 - ch // 2
        rect = pygame.Rect(cx, cy, cw, ch)

        pygame.draw.rect(self.screen, (28, 20, 25), rect, border_radius=12)
        pygame.draw.rect(self.screen, (255, 70, 70), rect, width=2, border_radius=12)

        t_warn = self.font_score.render("Konfirmasi Reset Chunking?", True, (255, 90, 90))
        t_desc = self.font_modal_sub.render("Semua nama kustom & potongan chunk lagu ini akan direset ke bawaan.", True, COLOR_TEXT_WHITE)
        self.screen.blit(t_warn, (cx + 20, cy + 22))
        self.screen.blit(t_desc, (cx + 20, cy + 58))

        btn_yes = pygame.Rect(cx + 40, cy + 110, 160, 40)
        btn_no = pygame.Rect(cx + cw - 200, cy + 110, 160, 40)

        h_yes = btn_yes.collidepoint(mx, my)
        h_no = btn_no.collidepoint(mx, my)

        pygame.draw.rect(self.screen, (220, 40, 60) if h_yes else (170, 30, 45), btn_yes, border_radius=6)
        t_y = self.font_modal.render("Ya, Reset [Y]", True, COLOR_TEXT_WHITE)
        self.screen.blit(t_y, (btn_yes.centerx - t_y.get_width() // 2, btn_yes.centery - t_y.get_height() // 2))

        pygame.draw.rect(self.screen, (60, 65, 85) if h_no else (40, 45, 60), btn_no, border_radius=6)
        t_n = self.font_modal.render("Batal [N]", True, COLOR_TEXT_WHITE)
        self.screen.blit(t_n, (btn_no.centerx - t_n.get_width() // 2, btn_no.centery - t_n.get_height() // 2))

    def _draw_rename_modal(self):
        """Modal input teks untuk mengganti nama chunk yang dipilih."""
        dim_surf = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        dim_surf.fill((0, 0, 0, 180))
        self.screen.blit(dim_surf, (0, 0))

        rw, rh = 460, 170
        rx = self.width // 2 - rw // 2
        ry = self.height // 2 - rh // 2
        r_rect = pygame.Rect(rx, ry, rw, rh)

        pygame.draw.rect(self.screen, (24, 27, 40), r_rect, border_radius=12)
        pygame.draw.rect(self.screen, COLOR_ACCENT_BLUE, r_rect, width=2, border_radius=12)

        t_rn = self.font_score.render("Ubah Nama Bagian (Chunk)", True, COLOR_TEXT_WHITE)
        t_sub = self.font_modal_sub.render("Ketik nama baru lalu tekan [ENTER] untuk menyimpan, [ESC] batal:", True, COLOR_TEXT_MUTED)
        self.screen.blit(t_rn, (rx + 25, ry + 18))
        self.screen.blit(t_sub, (rx + 25, ry + 50))

        # Input box
        in_rect = pygame.Rect(rx + 25, ry + 85, rw - 50, 40)
        pygame.draw.rect(self.screen, (15, 17, 26), in_rect, border_radius=6)
        pygame.draw.rect(self.screen, (80, 120, 200), in_rect, width=1, border_radius=6)

        t_txt = self.font_modal.render(self.rename_text + " |", True, (255, 235, 59))
        self.screen.blit(t_txt, (in_rect.x + 12, in_rect.centery - t_txt.get_height() // 2))
