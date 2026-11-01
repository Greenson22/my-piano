import pygame
import mido
import threading
import colorsys

# ---------------------------------------------------------
# 1. SETUP & KELAS VISUAL NOT (OPTIMASI TUKANG TINDIH & OUTLINE)
# ---------------------------------------------------------
MIN_PITCH = 21
MAX_PITCH = 108
NOTE_NAMES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']

class VisualNote:
    def __init__(self, pitch, velocity, width, height):
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
        
        # -------------------------------------------------
        # OPTIMASI UKURAN FONT: RENTANG DIPERKECHIL (16px - 36px)
        # Agar tidak saling menutupi not di sebelahnya
        # -------------------------------------------------
        MIN_FONT_SIZE = 16
        MAX_FONT_SIZE = 36
        velo_normalized = max(1, min(velocity, 127)) / 127.0
        self.font_size = int(MIN_FONT_SIZE + velo_normalized * (MAX_FONT_SIZE - MIN_FONT_SIZE))
        
        self.font = pygame.font.SysFont("Arial", self.font_size, bold=True)
        
        # Status animasi
        self.is_releasing = False
        self.alpha = 255
        self.fall_speed = 3
        self.fade_speed = 8

    def release(self):
        self.is_releasing = True

    def update(self):
        if self.is_releasing:
            self.y += self.fall_speed
            self.alpha -= self.fade_speed
            if self.alpha < 0:
                self.alpha = 0

    def draw(self, surface):
        # Render outline (hitam) di 4 arah agar teks utama terpisah jelas saat bertumpukan
        outline_surface = self.font.render(self.name, True, (0, 0, 0))
        text_surface = self.font.render(self.name, True, self.color)
        
        w, h = text_surface.get_size()
        # Buat surface gabungan dengan padding 4px untuk outline
        combined_surface = pygame.Surface((w + 4, h + 4), pygame.SRCALPHA)
        
        # Gambar outline hitam di sekeliling
        for dx, dy in [(-2,0), (2,0), (0,-2), (0,2), (-1,-1), (1,1), (-1,1), (1,-1)]:
            combined_surface.blit(outline_surface, (dx + 2, dy + 2))
            
        # Gambar teks utama berwarna di tengah
        combined_surface.blit(text_surface, (2, 2))
        
        # Terapkan transparansi (alpha) untuk animasi memudar
        combined_surface.set_alpha(self.alpha)
        
        rect = combined_surface.get_rect(center=(self.x, self.y))
        surface.blit(combined_surface, rect)


# ---------------------------------------------------------
# 2. SETUP MIDO (MULTI-NOTE THREADING)
# ---------------------------------------------------------
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
                        active_notes[msg.note] = VisualNote(msg.note, msg.velocity, width, height)
                elif msg.type == 'note_off' or (msg.type == 'note_on' and msg.velocity == 0):
                    with notes_lock:
                        if msg.note in active_notes:
                            active_notes[msg.note].release()
    except Exception as e:
        print(f"Error MIDI: {e}")

WIDTH, HEIGHT = 1000, 600

thread = threading.Thread(target=midi_listener, args=(WIDTH, HEIGHT), daemon=True)
thread.start()


# ---------------------------------------------------------
# 3. RENDER LOOP PYGAME
# ---------------------------------------------------------
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Visualizer Not Piano (Optimasi Overlap & Outline)")

BG_COLOR = (15, 15, 20)
clock = pygame.time.Clock()
running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill(BG_COLOR)

    with notes_lock:
        for pitch, note in list(active_notes.items()):
            note.update()
            note.draw(screen)
            
            if note.alpha <= 0:
                del active_notes[pitch]

    pygame.display.flip()
    clock.tick(60)

pygame.quit()