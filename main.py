import pygame
import mido
import threading

# ---------------------------------------------------------
# 1. SETUP MIDO (MEMBACA PIANO DI BACKGROUND THREAD)
# ---------------------------------------------------------
current_note_info = None  # Menyimpan data not terakhir yang ditekan

def midi_listener():
    global current_note_info
    try:
        inputs = mido.get_input_names()
        if not inputs:
            print("Tidak ada perangkat MIDI terdeteksi!")
            return
        
        # Mengambil perangkat MIDI pertama yang terhubung
        input_name = inputs[0]
        print(f"Terhubung ke MIDI: {input_name}")
        
        # Konversi angka MIDI note ke nama not musik (C, C#, D, dst.)
        NOTE_NAMES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']

        with mido.open_input(input_name) as inport:
            for msg in inport:
                if msg.type == 'note_on' and msg.velocity > 0:
                    note_number = msg.note
                    octave = (note_number // 12) - 1
                    note_name = f"{NOTE_NAMES[note_number % 12]}{octave}"
                    
                    # Simpan not & nomor pitch untuk dihitung posisinya di layar
                    current_note_info = {
                        "name": note_name,
                        "pitch": note_number
                    }
    except Exception as e:
        print(f"Error MIDI: {e}")

# Jalankan pendengar MIDI di thread terpisah agar tidak mengunci Pygame
thread = threading.Thread(target=midi_listener, daemon=True)
thread.start()


# ---------------------------------------------------------
# 2. SETUP PYGAME (DISPLAY & UI)
# ---------------------------------------------------------
pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Visualizer Not Piano")

FONT = pygame.font.SysFont("Arial", 36, bold=True)
BG_COLOR = (20, 20, 20)      # Background hitam/gelap
TEXT_COLOR = (0, 255, 200)   # Warna teks hijau toska

clock = pygame.time.Clock()
running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Bersihkan layar (UI Kosong)
    screen.fill(BG_COLOR)

    # Jika ada not piano yang ditekan
    if current_note_info is not None:
        pitch = current_note_info["pitch"]
        text_surface = FONT.render(current_note_info["name"], True, TEXT_COLOR)
        
        # Standar piano 88-key berada di rentang pitch MIDI 21 (A0) hingga 108 (C8)
        MIN_PITCH = 21
        MAX_PITCH = 108
        
        # Batasi pitch agar tidak keluar dari skala rentang
        clamped_pitch = max(MIN_PITCH, min(pitch, MAX_PITCH))
        
        # Normalisasi ke rentang 0.0 sampai 1.0
        normalized = (clamped_pitch - MIN_PITCH) / (MAX_PITCH - MIN_PITCH)
        
        # Hitung posisi Y: Pitch tinggi -> Y kecil (Atas), Pitch rendah -> Y besar (Bawah)
        # Diberi margin 50px dari atas dan bawah agar teks tidak terpotong
        pos_y = int((HEIGHT - 100) * (1 - normalized)) + 50
        pos_x = WIDTH // 2  # Posisikan horizontal di tengah layar
        
        text_rect = text_surface.get_rect(center=(pos_x, pos_y))
        screen.blit(text_surface, text_rect)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()