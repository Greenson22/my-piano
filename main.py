import pygame
import mido
import threading
import time

# ---------------------------------------------------------
# 1. SETUP & KONSTRUKTOR KELAS VISUAL NOT
# ---------------------------------------------------------
# Rentang pitch standar piano 88 tuts (A0 = 21, C8 = 108)
MIN_PITCH = 21
MAX_PITCH = 108
NOTE_NAMES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']

class VisualNote:
    def __init__(self, pitch, velocity, width, height):
        self.pitch = pitch
        self.velocity = velocity
        
        # Konversi pitch ke nama not (misal: C4)
        octave = (pitch // 12) - 1
        self.name = f"{NOTE_NAMES[pitch % 12]}{octave}"
        
        # Hitung posisi awal berdasarkan pitch
        clamped_pitch = max(MIN_PITCH, min(pitch, MAX_PITCH))
        normalized = (clamped_pitch - MIN_PITCH) / (MAX_PITCH - MIN_PITCH)
        
        # X: Pitch rendah di kiri, pitch tinggi di kanan
        self.x = int(60 + normalized * (width - 120))
        # Y: Pitch tinggi di atas, pitch rendah di bawah
        self.y = int((height - 120) * (1 - normalized)) + 60
        
        # Status animasi & transparansi (Alpha: 255 = pekat, 0 = transparan)
        self.is_releasing = False
        self.alpha = 255
        self.fall_speed = 3  # Kecepatan jatuh saat dilepas
        self.fade_speed = 8  # Kecepatan memudar

    def release(self):
        self.is_releasing = True

    def update(self):
        # Jika tombol sudah dilepas, jalankan animasi jatuh & memudar
        if self.is_releasing:
            self.y += self.fall_speed
            self.alpha -= self.fade_speed
            if self.alpha < 0:
                self.alpha = 0

    def draw(self, surface, font):
        # Render teks ke Surface sementara agar bisa menerapkan efek transparansi (Alpha)
        text_surface = font.render(self.name, True, (0, 255, 200))
        temp_surface = pygame.Surface(text_surface.get_size(), pygame.SRCALPHA)
        temp_surface.blit(text_surface, (0, 0))
        temp_surface.set_alpha(self.alpha)
        
        rect = temp_surface.get_rect(center=(self.x, self.y))
        surface.blit(temp_surface, rect)


# ---------------------------------------------------------
# 2. SETUP MIDO (MULTI-NOTE THREADING)
# ---------------------------------------------------------
# Dictionary untuk menyimpan not yang sedang aktif/ditekan: {pitch: VisualNote}
active_notes = {}
notes_lock = threading.Lock()

def midi_listener(width, height):
    try:
        inputs = mido.get_input_names()
        if not inputs:
            print("Perangkat MIDI tidak ditemukan!")
            return
            
        input_name = inputs[0]
        print(f"Terhubung ke MIDI: {input_name}")
        
        with mido.open_input(input_name) as inport:
            for msg in inport:
                if msg.type == 'note_on' and msg.velocity > 0:
                    with notes_lock:
                        # Tambahkan not baru saat tuts ditekan
                        active_notes[msg.note] = VisualNote(msg.note, msg.velocity, width, height)
                elif msg.type == 'note_off' or (msg.type == 'note_on' and msg.velocity == 0):
                    with notes_lock:
                        # Tandai not untuk mulai animasi lepas/jatuh saat tuts dilepas
                        if msg.note in active_notes:
                            active_notes[msg.note].release()
    except Exception as e:
        print(f"Error MIDI: {e}")

WIDTH, HEIGHT = 1000, 600

thread = threading.Thread(target=midi_listener, args=(WIDTH, HEIGHT), daemon=True)
thread.start()


# ---------------------------------------------------------
# 3. SETUP PYGAME & RENDER LOOP
# ---------------------------------------------------------
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Visualizer Multi-Note & Animasi Piano")

FONT = pygame.font.SysFont("Arial", 28, bold=True)
BG_COLOR = (15, 15, 20)
clock = pygame.time.Clock()
running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill(BG_COLOR)

    with notes_lock:
        # Iterasi copy dari list nilai agar aman saat menghapus elemen yang sudah hilang
        for pitch, note in list(active_notes.items()):
            note.update()
            note.draw(screen, FONT)
            
            # Hapus not dari memori jika animasi fade out sudah selesai (alpha <= 0)
            if note.alpha <= 0:
                del active_notes[pitch]

    pygame.display.flip()
    clock.tick(60)

pygame.quit()