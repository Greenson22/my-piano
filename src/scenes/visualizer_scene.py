import os
import pygame
from ..audio.sound_synth import synth_instance
from ..audio.midi_io import midi_manager
from ..visual_note import VisualNote
from ..utils.constants import COLOR_BG_DARK, COLOR_TEXT_WHITE, COLOR_TEXT_MUTED

# Map tombol keyboard PC untuk uji coba visualizer tanpa kabel MIDI fisik
KEYBOARD_MAP = {
    pygame.K_z: 48, pygame.K_s: 49, pygame.K_x: 50, pygame.K_d: 51,
    pygame.K_c: 52, pygame.K_v: 53, pygame.K_g: 54, pygame.K_b: 55,
    pygame.K_h: 56, pygame.K_n: 57, pygame.K_j: 58, pygame.K_m: 59,
    pygame.K_q: 60, pygame.K_2: 61, pygame.K_w: 62, pygame.K_3: 63,
    pygame.K_e: 64, pygame.K_r: 65, pygame.K_5: 66, pygame.K_t: 67,
    pygame.K_6: 68, pygame.K_y: 69, pygame.K_7: 70, pygame.K_u: 71,
    pygame.K_i: 72, pygame.K_9: 73, pygame.K_o: 74, pygame.K_0: 75,
    pygame.K_p: 76
}

class VisualizerScene:
    """Mode Asli Proyek (Free Play Visualizer) yang tetap dipertahankan."""

    def __init__(self, screen, clock):
        self.screen = screen
        self.clock = clock
        self.width, self.height = screen.get_size()
        self.active_visual_notes = {}

        self.font_info = pygame.font.SysFont("Segoe UI", 16)
        midi_manager.register_callback(self.on_midi_event)

    def on_midi_event(self, event_type: str, pitch: int, velocity: int):
        if event_type == 'note_on' and velocity > 0:
            synth_instance.play_note(pitch, velocity)
            self.active_visual_notes[pitch] = VisualNote(pitch, velocity, self.width, self.height)
        elif event_type == 'note_off':
            if pitch in self.active_visual_notes:
                self.active_visual_notes[pitch].release()

    def run(self) -> str:
        running = True
        while running:
            self.screen.fill(COLOR_BG_DARK)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    midi_manager.unregister_callback(self.on_midi_event)
                    return "quit"
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        midi_manager.unregister_callback(self.on_midi_event)
                        return "main_menu"
                    elif event.key in KEYBOARD_MAP:
                        p = KEYBOARD_MAP[event.key]
                        self.on_midi_event('note_on', p, 90)
                elif event.type == pygame.KEYUP:
                    if event.key in KEYBOARD_MAP:
                        p = KEYBOARD_MAP[event.key]
                        self.on_midi_event('note_off', p, 0)

            # Update & Gambar Visual Notes
            for pitch, note in list(self.active_visual_notes.items()):
                note.update()
                note.draw(self.screen)
                if note.alpha <= 0:
                    del self.active_visual_notes[pitch]

            # Info text
            txt = self.font_info.render("Mode Visualizer Bebas (Tekan [ESC] untuk kembali ke Menu)", True, COLOR_TEXT_MUTED)
            self.screen.blit(txt, (20, 20))

            pygame.display.flip()
            self.clock.tick(60)

        midi_manager.unregister_callback(self.on_midi_event)
        return "main_menu"
