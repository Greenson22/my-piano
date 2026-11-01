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
    # Default: tanpa file MIDI, sehingga bisa langsung main manual
    selected_file = None

    volume = 100

    # State untuk Input Teks Velocity
    velocity_text = "1.0"
    typing_velocity = False
    drag_vol = False
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

        # --- 3. Control Volume & Input Velocity ---
        # Master Volume Slider
        screen.blit(font_sub.render(f"3. Master Volume: {volume} / 127", True, (0, 255, 200)), (40, 175))
        track_vol = pygame.Rect(40, 200, 400, 8)
        pygame.draw.rect(screen, (60, 70, 90), track_vol, border_radius=4)
        fill_vol = pygame.Rect(40, 200, int((volume / 127) * 400), 8)
        pygame.draw.rect(screen, (0, 255, 200), fill_vol, border_radius=4)
        pygame.draw.circle(screen, (255, 255, 255), (40 + fill_vol.width, 204), 10)

        # Input Teks Velocity Multiplier
        screen.blit(font_sub.render("4. Ketik Multiplier Velocity (cth: 0.5 - 2.0):", True, (0, 255, 200)), (480, 175))
        velo_box = pygame.Rect(480, 198, 150, 32)
        box_bg = (60, 80, 110) if typing_velocity else (40, 45, 60)
        border_col = (0, 255, 200) if typing_velocity else (100, 100, 120)
        pygame.draw.rect(screen, box_bg, velo_box, border_radius=6)
        pygame.draw.rect(screen, border_col, velo_box, width=2, border_radius=6)
        velo_surf = font_item.render(velocity_text, True, (255, 255, 255))
        screen.blit(velo_surf, (velo_box.x + 10, velo_box.y + 6))

        # --- 4. File MIDI ---
        screen.blit(font_sub.render("5. Pilih File MIDI (Folder ./midi/):", True, (0, 255, 200)), (40, 240))
        file_buttons = []
        # Opsi pertama (None) = main manual tanpa memutar file MIDI
        all_options = [None] + midi_files[:5]
        for i, filename in enumerate(all_options):
            col = i % 2
            row = i // 2
            btn_rect = pygame.Rect(40 + col * 440, 270 + row * 38, 420, 32)
            is_sel = (filename == selected_file)
            color = (0, 180, 140) if is_sel else ((60, 70, 90) if btn_rect.collidepoint(mouse_pos) else (40, 45, 60))
            pygame.draw.rect(screen, color, btn_rect, border_radius=6)
            pygame.draw.rect(screen, (0, 255, 200) if is_sel else (100, 100, 120), btn_rect, width=2, border_radius=6)

            if filename is None:
                label = "- Tanpa File MIDI (Main Sendiri) -"
            else:
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
                typing_velocity = velo_box.collidepoint(event.pos)
                if track_vol.collidepoint(event.pos):
                    drag_vol = True
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
                drag_vol = False
            elif event.type == pygame.MOUSEMOTION and drag_vol:
                rel_x = max(0, min(event.pos[0] - 40, 400))
                volume = int((rel_x / 400) * 127)
            elif event.type == pygame.KEYDOWN and typing_velocity:
                if event.key == pygame.K_RETURN:
                    typing_velocity = False
                elif event.key == pygame.K_BACKSPACE:
                    velocity_text = velocity_text[:-1]
                else:
                    if event.unicode.isdigit() or event.unicode == '.':
                        if len(velocity_text) < 5:
                            velocity_text += event.unicode

        pygame.display.flip()
        clock.tick(60)

    try:
        velocity_mult = float(velocity_text)
    except ValueError:
        velocity_mult = 1.0

    full_midi_path = os.path.join(MIDI_DIR, selected_file) if selected_file else None
    return selected_input, selected_output, full_midi_path, volume, velocity_mult
