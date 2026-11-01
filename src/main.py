import os
import sys
import threading
import pygame

if __package__ in (None, ""):
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.gui import select_midi_config
from src.midi_handler import active_notes, midi_listener, midi_player, notes_lock, request_stop

def main():
    pygame.init()
    width, height = 1000, 600
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption("Visualizer & Controller Piano MIDI")
    clock = pygame.time.Clock()

    # 1. Pilih Port, File, dan Volume via GUI
    chosen_input, chosen_output, midi_file, chosen_volume = select_midi_config(screen, clock, width, height)

    # 2. Thread Input Manual
    if chosen_input:
        in_thread = threading.Thread(target=midi_listener, args=(chosen_input, width, height), daemon=True)
        in_thread.start()

    # 3. Thread Player dengan Kontrol Volume
    if chosen_output and midi_file:
        out_thread = threading.Thread(
            target=midi_player, 
            args=(midi_file, chosen_output, chosen_volume, width, height), 
            daemon=True
        )
        out_thread.start()

    # 4. Main Visualizer Loop
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

    pygame.quit()

if __name__ == "__main__":
    main()