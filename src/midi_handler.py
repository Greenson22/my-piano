import threading
import mido
import pygame
from src.visual_note import VisualNote

# Variabel global untuk state not dan kontrol thread
active_notes = {}
notes_lock = threading.Lock()
stop_thread = False


def request_stop():
    """Meminta worker thread MIDI berhenti dengan rapi."""
    global stop_thread
    stop_thread = True


def midi_listener(port_name: str, width: int, height: int):
    """Worker thread untuk mendengarkan event MIDI dari port yang dipilih."""
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
