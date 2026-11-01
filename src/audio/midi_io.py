import threading
import mido
from typing import Callable, Optional

class MidiManager:
    """Mengelola koneksi perangkat input dan output MIDI fisik."""

    def __init__(self):
        self.input_port_name: Optional[str] = None
        self.output_port_name: Optional[str] = None
        self.input_port = None
        self.output_port = None

        self.running = False
        self.listener_thread: Optional[threading.Thread] = None
        self.note_callbacks = [] # list of callback(event_type, pitch, velocity)

    def get_available_inputs(self):
        try:
            return mido.get_input_names()
        except Exception:
            return []

    def get_available_outputs(self):
        try:
            return mido.get_output_names()
        except Exception:
            return []

    def register_callback(self, cb: Callable):
        if cb not in self.note_callbacks:
            self.note_callbacks.append(cb)

    def unregister_callback(self, cb: Callable):
        if cb in self.note_callbacks:
            self.note_callbacks.remove(cb)

    def start_input_listener(self, port_name: str):
        self.stop_input_listener()
        self.input_port_name = port_name
        self.running = True

        def _listen():
            try:
                with mido.open_input(port_name) as inport:
                    self.input_port = inport
                    for msg in inport:
                        if not self.running:
                            break
                        if msg.type == 'note_on':
                            if msg.velocity > 0:
                                for cb in self.note_callbacks:
                                    cb('note_on', msg.note, msg.velocity)
                            else:
                                for cb in self.note_callbacks:
                                    cb('note_off', msg.note, 0)
                        elif msg.type == 'note_off':
                            for cb in self.note_callbacks:
                                cb('note_off', msg.note, 0)
            except Exception as e:
                print(f"[MidiManager] Error di listener: {e}")

        self.listener_thread = threading.Thread(target=_listen, daemon=True)
        self.listener_thread.start()

    def stop_input_listener(self):
        self.running = False
        if self.input_port:
            try:
                self.input_port.close()
            except Exception:
                pass
            self.input_port = None

    def open_output(self, port_name: str):
        self.close_output()
        self.output_port_name = port_name
        try:
            self.output_port = mido.open_output(port_name)
        except Exception as e:
            print(f"[MidiManager] Gagal membuka output port: {e}")
            self.output_port = None

    def send_note_on(self, pitch: int, velocity: int = 64):
        if self.output_port:
            try:
                self.output_port.send(mido.Message('note_on', note=pitch, velocity=velocity))
            except Exception:
                pass

    def send_note_off(self, pitch: int):
        if self.output_port:
            try:
                self.output_port.send(mido.Message('note_off', note=pitch, velocity=0))
            except Exception:
                pass

    def close_output(self):
        if self.output_port:
            try:
                self.output_port.close()
            except Exception:
                pass
            self.output_port = None


# Instansiasi global
midi_manager = MidiManager()
