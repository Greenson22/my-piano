import pygame
import mido
import threading
import colorsys

# ---------------------------------------------------------
# 1. KELAS VISUAL NOT (EFEK OUTLINE, GRADASI, FONT DYNAMIC)
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
        
        # Rentang Font (16px - 36px)
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
        outline_surface = self.font.render(self.name, True, (0, 0, 0))
        text_surface = self.font.render(self.name, True, self.color)
        
        w, h = text_surface.get_size()
        combined_surface = pygame.Surface((w + 4, h + 4), pygame.SRCALPHA)
        
        # Outline hitam di sekeliling
        for dx, dy in [(-2,0), (2,0), (0,-2), (0,2), (-1,-1), (1,1), (-1,1), (1,-1)]:
            combined_surface.blit(outline_surface, (dx + 2, dy + 2))
            
        combined_surface.blit(text_surface, (2, 2))
        combined_surface.set_alpha(self.alpha)
        
        rect = combined_surface.get_rect(center=(self.x, self.y))
        surface.blit(combined_surface, rect)


# ---------------------------------------------------------
# 2. GLOBAL VARIABLES & LISTENER THREADING
# ---------------------------------------------------------
active_notes = {}
notes_lock = threading.Lock()
stop_thread = False

def midi_listener(port_name, width, height):
    global stop_thread
    try:
        print(f"Membuka port MIDI: {port_name}")
        with mido.open_input(port_name) as inport:
            while not stop_thread:
                # Menggunakan poll() agar thread dapat dihentikan dengan rapi saat window ditutup
                for msg in inport.iter_pending():
                    if msg.type == 'note_on' and msg.velocity > 0:
                        with notes_lock:
                            active_notes[msg.note] = VisualNote(msg.note, msg.velocity, width, height)
                    elif msg.type == 'note_off' or (msg.type == 'note_on' and msg.velocity == 0):
                        with notes_lock:
                            if msg.note in active_notes:
                                active_notes[msg.note].release()
                pygame.time.wait(1)
    except Exception as e:
        print(f"Error MIDI: {e}")


# ---------------------------------------------------------
# 3. GUI SELEKSI PORT MIDI (PYGAME SCREEN)
# ---------------------------------------------------------
def select_midi_port(screen, clock, width, height):
    font_title = pygame.font.SysFont("Arial", 28, bold=True)
    font_item = pygame.font.SysFont("Arial", 20)
    
    ports = mido.get_input_names()
    selected_port = None
    
    while selected_port is None:
        screen.fill((20, 22, 30))
        
        # Judul
        title_surf = font_title.render("Pilih Perangkat Input MIDI Piano Anda", True, (255, 255, 255))
        screen.blit(title_surf, (width // 2 - title_surf.get_width() // 2, 40))
        
        buttons = []
        mouse_pos = pygame.mouse.get_pos()
        
        if not ports:
            empty_surf = font_item.render("Tidak ada perangkat MIDI terdeteksi!", True, (255, 100, 100))
            screen.blit(empty_surf, (width // 2 - empty_surf.get_width() // 2, 180))
        else:
            # Tampilkan daftar port sebagai tombol
            start_y = 120
            for i, port in enumerate(ports):
                btn_rect = pygame.Rect(width // 2 - 250, start_y + i * 55, 500, 45)
                is_hover = btn_rect.collidepoint(mouse_pos)
                
                color = (0, 180, 140) if is_hover else (40, 45, 60)
                pygame.draw.rect(screen, color, btn_rect, border_radius=8)
                pygame.draw.rect(screen, (0, 255, 200), btn_rect, width=2, border_radius=8)
                
                port_surf = font_item.render(f"{i+1}. {port}", True, (255, 255, 255))
                screen.blit(port_surf, (btn_rect.x + 20, btn_rect.y + 10))
                
                buttons.append((btn_rect, port))

        # Tombol Refresh
        refresh_rect = pygame.Rect(width // 2 - 80, height - 80, 160, 40)
        is_refresh_hover = refresh_rect.collidepoint(mouse_pos)
        ref_color = (70, 80, 100) if is_refresh_hover else (50, 55, 70)
        
        pygame.draw.rect(screen, ref_color, refresh_rect, border_radius=6)
        refresh_surf = font_item.render("Refresh Port", True, (200, 200, 200))
        screen.blit(refresh_surf, (refresh_rect.x + (160 - refresh_surf.get_width())//2, refresh_rect.y + 8))

        # Event Handler GUI Seleksi
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                # Klik pada opsi port
                for btn_rect, port_name in buttons:
                    if btn_rect.collidepoint(event.pos):
                        selected_port = port_name
                # Klik tombol Refresh
                if refresh_rect.collidepoint(event.pos):
                    ports = mido.get_input_names()

        pygame.display.flip()
        clock.tick(60)
        
    return selected_port


# ---------------------------------------------------------
# 4. MAIN PROGRAM & RENDER LOOP
# ---------------------------------------------------------
def main():
    global stop_thread
    
    pygame.init()
    WIDTH, HEIGHT = 1000, 600
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Visualizer Not Piano MIDI")
    clock = pygame.time.Clock()

    # 1. Pilih Port via GUI
    chosen_port = select_midi_port(screen, clock, WIDTH, HEIGHT)

    # 2. Jalankan Thread MIDI Listener untuk Port yang Dipilih
    thread = threading.Thread(target=midi_listener, args=(chosen_port, WIDTH, HEIGHT), daemon=True)
    thread.start()

    # 3. Visualizer Loop
    BG_COLOR = (15, 15, 20)
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                stop_thread = True
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

if __name__ == "__main__":
    main()