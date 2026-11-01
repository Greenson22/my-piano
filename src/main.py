import os
import sys
import threading

import pygame

# Izinkan aplikasi dijalankan langsung (`python src/main.py`) maupun
# sebagai modul (`python -m src.main`) dengan memastikan root proyek
# berada di sys.path sehingga paket `src` dapat diimpor.
if __package__ in (None, ""):
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.gui import select_midi_port
from src.midi_handler import active_notes, midi_listener, notes_lock, request_stop


def main():
    pygame.init()
    width, height = 1000, 600
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption("Visualizer Not Piano MIDI")
    clock = pygame.time.Clock()

    # 1. Pilih Port via GUI
    chosen_port = select_midi_port(screen, clock, width, height)

    # 2. Jalankan Thread MIDI Listener untuk Port yang Dipilih
    thread = threading.Thread(target=midi_listener, args=(chosen_port, width, height), daemon=True)
    thread.start()

    # 3. Visualizer Loop
    bg_color = (15, 15, 20)
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                request_stop()
                running = False

        screen.fill(bg_color)

        with notes_lock:
            for pitch, note in list(active_notes.items()):
                note.update()
                note.draw(screen)

                if note.alpha <= 0:
                    del active_notes[pitch]

        pygame.display.flip()
        clock.tick(60)

    thread.join(timeout=1)
    pygame.quit()


if __name__ == "__main__":
    main()
