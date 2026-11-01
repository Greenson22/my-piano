import mido
import pygame


def select_midi_port(screen: pygame.Surface, clock: pygame.time.Clock, width: int, height: int) -> str:
    """Menampilkan GUI interaktif untuk memilih perangkat MIDI input."""
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

                port_surf = font_item.render(f"{i + 1}. {port}", True, (255, 255, 255))
                screen.blit(port_surf, (btn_rect.x + 20, btn_rect.y + 10))

                buttons.append((btn_rect, port))

        # Tombol Refresh
        refresh_rect = pygame.Rect(width // 2 - 80, height - 80, 160, 40)
        is_refresh_hover = refresh_rect.collidepoint(mouse_pos)
        ref_color = (70, 80, 100) if is_refresh_hover else (50, 55, 70)

        pygame.draw.rect(screen, ref_color, refresh_rect, border_radius=6)
        refresh_surf = font_item.render("Refresh Port", True, (200, 200, 200))
        screen.blit(refresh_surf, (refresh_rect.x + (160 - refresh_surf.get_width()) // 2, refresh_rect.y + 8))

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
