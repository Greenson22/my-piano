import mido
from dataclasses import dataclass
from typing import List

@dataclass
class MidiNoteEvent:
    pitch: int
    velocity: int
    start_time: float   # Dalam detik riil
    duration: float     # Dalam detik riil
    hand: str           # 'right' (melodi/treble) atau 'left' (bass/iringan)
    hit: bool = False   # Status apakah sudah ditekan oleh pemain


def parse_midi_file(filepath: str) -> List[MidiNoteEvent]:
    """
    Membaca file MIDI dan mengonversinya menjadi daftar MidiNoteEvent
    yang terurut berdasarkan waktu mulai riil (detik).
    """
    mid = mido.MidiFile(filepath)
    events: List[MidiNoteEvent] = []

    # Iterasi pesan terurut waktu riil menggunakan mid.play() / generator delta time terkonversi
    # mido mengonversi ticks ke detik saat melakukan iterasi terhadap mid (real-time delta)
    current_time = 0.0
    active_notes = {}  # pitch -> (start_time, velocity)
    all_raw_notes = []

    for msg in mid:
        current_time += msg.time

        if msg.type == 'note_on' and msg.velocity > 0:
            # Jika ada nada sama yang belum di-off-kan, selesaikan dulu
            if msg.note in active_notes:
                start_t, vel = active_notes.pop(msg.note)
                all_raw_notes.append({
                    'pitch': msg.note,
                    'velocity': vel,
                    'start_time': start_t,
                    'duration': max(0.12, current_time - start_t)
                })
            active_notes[msg.note] = (current_time, msg.velocity)

        elif (msg.type == 'note_off') or (msg.type == 'note_on' and msg.velocity == 0):
            if msg.note in active_notes:
                start_t, vel = active_notes.pop(msg.note)
                all_raw_notes.append({
                    'pitch': msg.note,
                    'velocity': vel,
                    'start_time': start_t,
                    'duration': max(0.12, current_time - start_t)
                })

    # Tangani sisa note yang belum ada note_off
    for pitch, (start_t, vel) in active_notes.items():
        all_raw_notes.append({
            'pitch': pitch,
            'velocity': vel,
            'start_time': start_t,
            'duration': 0.3
        })

    # Urutkan berdasarkan waktu mulai riil
    all_raw_notes.sort(key=lambda x: x['start_time'])

    # Normalisasi waktu mulai: jika nada pertama mulai setelah jeda panjang, beri lead time 1.5 detik
    if all_raw_notes:
        first_time = all_raw_notes[0]['start_time']
        lead_in = 1.8
        offset = max(0.0, first_time - lead_in)
        for n in all_raw_notes:
            n['start_time'] = max(0.0, n['start_time'] - offset)

    for n in all_raw_notes:
        pitch = n['pitch']
        # Tangan kanan jika pitch >= 60 (Middle C), selain itu tangan kiri
        hand = 'right' if pitch >= 60 else 'left'
        events.append(MidiNoteEvent(
            pitch=pitch,
            velocity=n['velocity'],
            start_time=n['start_time'],
            duration=n['duration'],
            hand=hand
        ))

    return events
