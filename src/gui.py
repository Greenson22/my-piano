import os
import mido
import pygame

MIDI_DIR = "./midi"

def get_midi_files() -> list[str]:
    """Mengambil daftar berkas .mid/.midi dari folder ./midi/."""
    if not os.path.exists(MIDI_DIR):
        os.makedirs(MIDI_DIR)
    
    files = [
        f for f in os.listdir(MIDI_DIR) 
        if f.lower().endswith(('.mid', '.midi'))
    ]
    return sorted(files)

def select_midi_config(screen: pygame.Surface, clock: pygame.time.Clock, width: int, height: int):
    """GUI interaktif untuk memilih port, file MIDI, dan mengatur volume."""
    font_title = pygame.font.SysFont("Arial", 26, bold=True)
    font_sub = pygame.font.SysFont("Arial", 18, bold=True)
    font_item = pygame.font.SysFont("Arial", 16)

    input_ports = mido.get_input_names()
    output_ports = mido.get_output_names()
    midi_files = get_midi_files()

    selected_input = input_ports[0] if input_ports else None
    selected_output = output_ports[0] if output_ports else None
    selected_file = midi_files[0] if midi_files else None
    
    # Scale Volume (0 hingga 127 - Standar MIDI)
    volume = 100 
    dragging_slider = False

    config_done = False

    while not config_done:
        screen.fill((20, 22, 30))
        mouse_pos = pygame.mouse.get_pos()

        # Judul Utama
        title_surf = font_title.render("Pengaturan MIDI & Piano Konfigurasi", True, (255, 255, 255))
        screen.blit(title_surf, (width // 2 - title_surf.get_width() // 2, 15))

        # --- Section 1: MIDI Input Port ---
        in_title = font_sub.render("1. Pilih Port MIDI Input (Dari Piano/Keyboard):", True, (0, 255, 200))
        screen.blit(in_title, (50, 60))
        
        in_buttons = []
        if not input_ports:
            screen.blit(font_item.render("- Tidak ada input terdeteksi -", True, (255, 100, 100)), (60, 90))
        else:
            for i, port in enumerate(input_ports[:3]):
                btn_rect = pygame.Rect(50 + i * 300, 90, 280, 32)
                is_sel = (port == selected_input)
                color = (0, 180, 140) if is_sel else ((60, 70, 90) if btn_rect.collidepoint(mouse_pos) else (40, 45, 60))
                pygame.draw.rect(screen, color, btn_rect, border_radius=6)
                pygame.draw.rect(screen, (0, 255, 200) if is_sel else (100, 100, 120), btn_rect, width=2, border_radius=6)
                screen.blit(font_item.render(f"{port[:25]}...", True, (255, 255, 255)), (btn_rect.x + 10, btn_rect.y + 6))
                in_buttons.append((btn_rect, port))

        # --- Section 2: MIDI Output Port ---
        out_title = font_sub.render("2. Pilih Port MIDI Output (Ke Piano Elektrik):", True, (0, 255, 200))
        screen.blit(out_title, (50, 140))
        
        out_buttons = []
        if not output_ports:
            screen.blit(font_item.render("- Tidak ada output terdeteksi -", True, (255, 100, 100)), (60, 170))
        else:
            for i, port in enumerate(output_ports[:3]):
                btn_rect = pygame.Rect(50 + i * 300, 170, 280, 32)
                is_sel = (port == selected_output)
                color = (0, 180, 140) if is_sel else ((60, 70, 90) if btn_rect.collidepoint(mouse_pos) else (40, 45, 60))
                pygame.draw.rect(screen, color, btn_rect, border_radius=6)
                pygame.draw.rect(screen, (0, 255, 200) if is_sel else (100, 100, 120), btn_rect, width=2, border_radius=6)
                screen.blit(font_item.render(f"{port[:25]}...", True, (255, 255, 255)), (btn_rect.x + 10, btn_rect.y + 6))
                out_buttons.append((btn_rect, port))

        # --- Section 3: Pengaturan Volume MIDI ---
        vol_title = font_sub.render(f"3. Volume MIDI Output: {volume} / 127", True, (0, 255, 200))
        screen.blit(vol_title, (50, 220))
        
        # Track Slider
        slider_track = pygame.Rect(50, 250, 400, 10)
        pygame.draw.rect(screen, (60, 70, 90), slider_track, border_radius=5)
        
        # Fill Active Track
        fill_width = int((volume / 127) * 400)
        fill_rect = pygame.Rect(50, 250, fill_width, 10)
        pygame.draw.rect(screen, (0, 255, 200), fill_rect, border_radius=5)

        # Handle Circle Slider
        handle_x = 50 + fill_width
        handle_center = (handle_x, 255)
        pygame.draw.circle(screen, (255, 255, 255), handle_center, 12)
        pygame.draw.circle(screen, (0, 180, 140), handle_center, 8)

        # --- Section 4: Daftar File MIDI ---
        file_title = font_sub.render("4. Pilih Berkas File MIDI (Folder ./midi/):", True, (0, 255, 200))
        screen.blit(file_title, (50, 280))
        
        file_buttons = []
        if not midi_files:
            empty_msg = f"- Tidak ada berkas .mid/.midi di folder {MIDI_DIR} - "
            screen.blit(font_item.render(empty_msg, True, (255, 100, 100)), (60, 310))
        else:
            for i, filename in enumerate(midi_files[:6]):
                col = i % 2
                row = i // 2
                btn_rect = pygame.Rect(50 + col * 440, 310 + row * 40, 420, 34)
                is_sel = (filename == selected_file)
                color = (0, 180, 140) if is_sel else ((60, 70, 90) if btn_rect.collidepoint(mouse_pos) else (40, 45, 60))
                pygame.draw.rect(screen, color, btn_rect, border_radius=6)
                pygame.draw.rect(screen, (0, 255, 200) if is_sel else (100, 100, 120), btn_rect, width=2, border_radius=6)
                
                label = filename if len(filename) <= 38 else f"{filename[:35]}..."
                screen.blit(font_item.render(label, True, (255, 255, 255)), (btn_rect.x + 10, btn_rect.y + 6))
                file_buttons.append((btn_rect, filename))

        # --- Tombol Refresh & Mulai ---
        refresh_rect = pygame.Rect(width // 2 - 210, height - 65, 180, 45)
        ref_hover = refresh_rect.collidepoint(mouse_pos)
        pygame.draw.rect(screen, (70, 80, 100) if ref_hover else (50, 55, 70), refresh_rect, border_radius=8)
        ref_surf = font_item.render("Refresh", True, (220, 220, 220))
        screen.blit(ref_surf, (refresh_rect.x + (180 - ref_surf.get_width()) // 2, refresh_rect.y + 12))

        start_rect = pygame.Rect(width // 2 + 30, height - 65, 180, 45)
        start_hover = start_rect.collidepoint(mouse_pos)
        pygame.draw.rect(screen, (0, 200, 120) if start_hover else (0, 150, 90), start_rect, border_radius=8)
        start_surf = font_sub.render("MULAI", True, (255, 255, 255))
        screen.blit(start_surf, (start_rect.x + (180 - start_surf.get_width()) // 2, start_rect.y + 10))

        # Event Handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                # Klik pada slider volume
                handle_rect = pygame.Rect(handle_x - 12, 243, 24, 24)
                if slider_track.collidepoint(event.pos) or handle_rect.collidepoint(event.pos):
                    dragging_slider = True

                for btn_rect, port in in_buttons:
                    if btn_rect.collidepoint(event.pos):
                        selected_input = port
                
                for btn_rect, port in out_buttons:
                    if btn_rect.collidepoint(event.pos):
                        selected_output = port

                for btn_rect, filename in file_buttons:
                    if btn_rect.collidepoint(event.pos):
                        selected_file = filename

                if refresh_rect.collidepoint(event.pos):
                    input_ports = mido.get_input_names()
                    output_ports = mido.get_output_names()
                    midi_files = get_midi_files()

                if start_rect.collidepoint(event.pos):
                    config_done = True

            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                dragging_slider = False

            elif event.type == pygame.MOUSEMOTION and dragging_slider:
                rel_x = max(0, min(event.pos[0] - 50, 400))
                volume = int((rel_x / 400) * 127)

        pygame.display.flip()
        clock.tick(60)

    full_midi_path = os.path.join(MIDI_DIR, selected_file) if selected_file else None
    return selected_input, selected_output, full_midi_path, volume