import os
import threading
import mido
import pygame
from src.visual_note import VisualNote

active_notes = {}
notes_lock = threading.Lock()
stop_thread = False


def request_stop():
    global stop_thread
    stop_thread = True


def midi_listener(port_name: str, width: int, height: int):
    global stop_thread
    if not port_name:
        return
    try:
        with mido.open_input(port_name) as inport:
            while not stop_thread:
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
        print(f"Error MIDI Input: {e}")


def midi_player(midi_file_path: str, output_port_name: str, volume: int, velocity_mult: float, width: int, height: int):
    global stop_thread
    if not midi_file_path or not os.path.isfile(midi_file_path) or not output_port_name:
        return
    try:
        mid = mido.MidiFile(midi_file_path)
        vol_factor = volume / 127.0
        with mido.open_output(output_port_name) as outport:
            # Set Master Volume (CC 7)
            for channel in range(16):
                vol_msg = mido.Message('control_change', channel=channel, control=7, value=volume)
                outport.send(vol_msg)

            for msg in mid.play():
                if stop_thread:
                    break
                adjusted_msg = msg.copy()
                if adjusted_msg.type == 'note_on' and adjusted_msg.velocity > 0:
                    scaled_velo = int(adjusted_msg.velocity * velocity_mult)
                    final_velocity = int(scaled_velo * vol_factor)
                    adjusted_msg.velocity = max(1, min(final_velocity, 127))

                outport.send(adjusted_msg)

                if adjusted_msg.type == 'note_on' and adjusted_msg.velocity > 0:
                    with notes_lock:
                        active_notes[adjusted_msg.note] = VisualNote(adjusted_msg.note, adjusted_msg.velocity, width, height)
                elif adjusted_msg.type == 'note_off' or (adjusted_msg.type == 'note_on' and adjusted_msg.velocity == 0):
                    with notes_lock:
                        if adjusted_msg.note in active_notes:
                            active_notes[adjusted_msg.note].release()
    except Exception as e:
        print(f"Error MIDI Player / Output: {e}")
