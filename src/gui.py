import os
import mido
import pygame

MIDI_DIR = "./midi"

def get_midi_files() -> list[str]:
    if not os.path.exists(MIDI_DIR):
        os.makedirs(MIDI_DIR)
    files = [f for f in os.listdir(MIDI_DIR) if f.lower().endswith(('.mid', '.midi'))]
    return sorted(files)

def select_midi_config(screen: pygame.Surface, clock: pygame.time.Clock, width: int, height: int):
    font_title = pygame.font.SysFont("Arial", 24, bold=True)
    font_sub = pygame.font.SysFont("Arial", 16, bold=True)
    font_item = pygame.font.SysFont("Arial", 15)

    input_ports = mido.get_input_names()
    output_ports = mido.get_output_names()
    midi_files = get_midi_files()

    selected_input = input_ports[0] if input_ports else None
    selected_output = output_ports[0] if output_ports else None
    selected_file = midi_files[0] if midi_files else None
    
    volume = 100 
    velocity_mult = 1.0  # Pengali Velocity (0.5x - 2.0x)
    
    drag_vol = False
    drag_velo = False
    config_done = False

    while not config_done:
        screen.fill((20, 22, 30))
        mouse_pos = pygame.mouse.get_pos()

        # Judul Utama
        title_surf = font_title.render("Pengaturan MIDI & Piano Konfigurasi", True, (255, 255, 255))
        screen.blit(title_surf, (width // 2 - title_surf.get_width() // 2, 10))

        # --- 1. MIDI Input Port ---
        screen.blit(font_sub.render("1. Port Input MIDI:", True, (0, 255, 200)), (40, 45))
        in_buttons = []
        if not input_ports:
            screen.blit(font_item.render("- Tidak ada input terdeteksi -", True, (255, 100, 100)), (50, 70))
        else:
            for i, port in enumerate(input_ports[:3]):
                btn_rect = pygame.Rect(40 + i * 300, 70, 280, 30)
                is_sel = (port == selected_input)
                color = (0, 180, 140) if is_sel else ((60, 70, 90) if btn_rect.collidepoint(mouse_pos) else (40, 45, 60))
                pygame.draw.rect(screen, color, btn_rect, border_radius=6)
                pygame.draw.rect(screen, (0, 255, 200) if is_sel else (100, 100, 120), btn_rect, width=2, border_radius=6)
                screen.blit(font_item.render(f"{port[:25]}...", True, (255, 255, 255)), (btn_rect.x + 10, btn_rect.y + 5))
                in_buttons.append((btn_rect, port))

        # --- 2. MIDI Output Port ---
        screen.blit(font_sub.render("2. Port Output MIDI (Ke Piano Elektrik):", True, (0, 255, 200)), (40, 110))
        out_buttons = []
        if not output_ports:
            screen.blit(font_item.render("- Tidak ada output terdeteksi -", True, (255, 100, 100)), (50, 135))
        else:
            for i, port in enumerate(output_ports[:3]):
                btn_rect = pygame.Rect(40 + i * 300, 135, 280, 30)
                is_sel = (port == selected_output)
                color = (0, 180, 140) if is_sel else ((60, 70, 90) if btn_rect.collidepoint(mouse_pos) else (40, 45, 60))
                pygame.draw.rect(screen, color, btn_rect, border_radius=6)
                pygame.draw.rect(screen, (0, 255, 200) if is_sel else (100, 100, 120), btn_rect, width=2, border_radius=6)
                screen.blit(font_item.render(f"{port[:25]}...", True, (255, 255, 255)), (btn_rect.x + 10, btn_rect.y + 5))
                out_buttons.append((btn_rect, port))

        # --- 3. Slider Volume & Velocity ---
        # Master Volume
        screen.blit(font_sub.render(f"3. Master Volume: {volume} / 127", True, (0, 255, 200)), (40, 175))
        track_vol = pygame.Rect(40, 200, 400, 8)
        pygame.draw.rect(screen, (60, 70, 90), track_vol, border_radius=4)
        fill_vol = pygame.Rect(40, 200, int((volume / 127) * 400), 8)
        pygame.draw.rect(screen, (0, 255, 200), fill_vol, border_radius=4)
        pygame.draw.circle(screen, (255, 255, 255), (40 + fill_vol.width, 204), 10)

        # Velocity Multiplier
        screen.blit(font_sub.render(f"4. Sensitivitas Velocity: {velocity_mult:.1f}x", True, (0, 255, 200)), (480, 175))
        track_velo = pygame.Rect(480, 200, 400, 8)
        pygame.draw.rect(screen, (60, 70, 90), track_velo, border_radius=4)
        velo_ratio = (velocity_mult - 0.5) / 1.5  # Rentang 0.5x s/d 2.0x
        fill_velo = pygame.Rect(480, 200, int(velo_ratio * 400), 8)
        pygame.draw.rect(screen, (0, 255, 200), fill_velo, border_radius=4)
        pygame.draw.circle(screen, (255, 255, 255), (480 + fill_velo.width, 204), 10)

        # --- 4. File MIDI ---
        screen.blit(font_sub.render("5. Pilih File MIDI (Folder ./midi/):", True, (0, 255, 200)), (40, 225))
        file_buttons = []
        if not midi_files:
            screen.blit(font_item.render(f"- Tidak ada berkas di {MIDI_DIR} -", True, (255, 100, 100)), (50, 255))
        else:
            for i, filename in enumerate(midi_files[:6]):
                col = i % 2
                row = i // 2
                btn_rect = pygame.Rect(40 + col * 440, 255 + row * 38, 420, 32)
                is_sel = (filename == selected_file)
                color = (0, 180, 140) if is_sel else ((60, 70, 90) if btn_rect.collidepoint(mouse_pos) else (40, 45, 60))
                pygame.draw.rect(screen, color, btn_rect, border_radius=6)
                pygame.draw.rect(screen, (0, 255, 200) if is_sel else (100, 100, 120), btn_rect, width=2, border_radius=6)
                label = filename if len(filename) <= 38 else f"{filename[:35]}..."
                screen.blit(font_item.render(label, True, (255, 255, 255)), (btn_rect.x + 10, btn_rect.y + 6))
                file_buttons.append((btn_rect, filename))

        # --- Tombol Refresh & Mulai ---
        refresh_rect = pygame.Rect(width // 2 - 210, height - 60, 180, 40)
        pygame.draw.rect(screen, (70, 80, 100) if refresh_rect.collidepoint(mouse_pos) else (50, 55, 70), refresh_rect, border_radius=8)
        ref_surf = font_item.render("Refresh", True, (220, 220, 220))
        screen.blit(ref_surf, (refresh_rect.x + (180 - ref_surf.get_width()) // 2, refresh_rect.y + 10))

        start_rect = pygame.Rect(width // 2 + 30, height - 60, 180, 40)
        pygame.draw.rect(screen, (0, 200, 120) if start_rect.collidepoint(mouse_pos) else (0, 150, 90), start_rect, border_radius=8)
        start_surf = font_sub.render("MULAI", True, (255, 255, 255))
        screen.blit(start_surf, (start_rect.x + (180 - start_surf.get_width()) // 2, start_rect.y + 8))

        # Event Handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if track_vol.collidepoint(event.pos):
                    drag_vol = True
                elif track_velo.collidepoint(event.pos):
                    drag_velo = True

                for btn_rect, port in in_buttons:
                    if btn_rect.collidepoint(event.pos): selected_input = port
                for btn_rect, port in out_buttons:
                    if btn_rect.collidepoint(event.pos): selected_output = port
                for btn_rect, filename in file_buttons:
                    if btn_rect.collidepoint(event.pos): selected_file = filename

                if refresh_rect.collidepoint(event.pos):
                    input_ports = mido.get_input_names()
                    output_ports = mido.get_output_names()
                    midi_files = get_midi_files()

                if start_rect.collidepoint(event.pos):
                    config_done = True

            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                drag_vol = False
                drag_velo = False

            elif event.type == pygame.MOUSEMOTION:
                if drag_vol:
                    rel_x = max(0, min(event.pos[0] - 40, 400))
                    volume = int((rel_x / 400) * 127)
                elif drag_velo:
                    rel_x = max(0, min(event.pos[0] - 480, 400))
                    velocity_mult = round(0.5 + (rel_x / 400) * 1.5, 2)

        pygame.display.flip()
        clock.tick(60)

    full_midi_path = os.path.join(MIDI_DIR, selected_file) if selected_file else None
    return selected_input, selected_output, full_midi_path, volume, velocity_mult