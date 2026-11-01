import mido
from dataclasses import dataclass
from typing import List

@dataclass
class MidiNoteEvent:
    pitch: int
    velocity: int
    start_time: float   # Dalam detik
    duration: float     # Dalam detik
    hand: str           # 'right' (melodi/treble) atau 'left' (bass/iringan)
    hit: bool = False   # Status apakah sudah ditekan oleh pemain


def parse_midi_file(filepath: str) -> List[MidiNoteEvent]:
    """
    Membaca file MIDI dan mengonversinya menjadi daftar MidiNoteEvent
    yang terurut berdasarkan waktu mulai (start_time).
    Secara cerdas membedakan tangan kanan (treble) dan tangan kiri (bass).
    """
    mid = mido.MidiFile(filepath)
    events: List[MidiNoteEvent] = []

    # Pendekatan 1: Jika file memiliki multi-track (umum pada file klasik piano)
    # Track 1 biasanya melodi tangan kanan, Track 2 biasanya tangan kiri.
    has_multiple_musical_tracks = len([t for t in mid.tracks if any(m.type == 'note_on' for m in t)]) > 1

    track_notes = []
    for track_idx, track in enumerate(mid.tracks):
        current_time = 0.0
        active_notes = {} # pitch -> (start_time, velocity)

        for msg in track:
            current_time += msg.time

            if msg.type == 'note_on' and msg.velocity > 0:
                active_notes[msg.note] = (current_time, msg.velocity)
            elif (msg.type == 'note_off') or (msg.type == 'note_on' and msg.velocity == 0):
                if msg.note in active_notes:
                    start_t, vel = active_notes.pop(msg.note)
                    duration = max(0.1, current_time - start_t)
                    track_notes.append({
                        'pitch': msg.note,
                        'velocity': vel,
                        'start_time': start_t,
                        'duration': duration,
                        'track_idx': track_idx
                    })

    # Urutkan berdasarkan waktu mulai
    track_notes.sort(key=lambda x: x['start_time'])

    # Tentukan pemisahan tangan:
    # 1. Jika ada track terpisah, track dengan rata-rata pitch lebih tinggi = right hand
    # 2. Jika single track, split berdasarkan Middle C (pitch 60)
    for note in track_notes:
        pitch = note['pitch']
        if pitch >= 60:
            hand = 'right'
        else:
            hand = 'left'

        events.append(MidiNoteEvent(
            pitch=pitch,
            velocity=note['velocity'],
            start_time=note['start_time'],
            duration=note['duration'],
            hand=hand
        ))

    return events
