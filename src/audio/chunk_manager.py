import os
import json
import hashlib
from typing import List, Dict, Any

class ChunkManager:
    """
    Mengelola penyimpanan, pembuatan, pengeditan nama, dan penghapusan
    data Chunking (potongan birama latihan) untuk setiap lagu MIDI.
    Data disimpan secara persisten di file chunks.json.
    """

    def __init__(self, data_file: str = "chunks.json"):
        self.data_file = data_file
        self.chunks_data: Dict[str, List[Dict[str, Any]]] = {}
        self.load()

    def _get_song_key(self, midi_path: str) -> str:
        """Membuat ID unik berbasis nama file atau path lagu."""
        return os.path.basename(midi_path)

    def load(self):
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    self.chunks_data = json.load(f)
            except Exception:
                self.chunks_data = {}
        else:
            self.chunks_data = {}

    def save(self):
        try:
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(self.chunks_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"[ChunkManager] Gagal menyimpan chunk: {e}")

    def get_chunks_for_song(self, midi_path: str, total_duration: float) -> List[Dict[str, Any]]:
        key = self._get_song_key(midi_path)
        if key not in self.chunks_data or not self.chunks_data[key]:
            # Buat chunk default otomatis jika belum ada (misal dibagi per 8 detik)
            default_chunks = []
            chunk_len = 8.0
            cur = 0.0
            idx = 1
            while cur < total_duration:
                end_t = min(total_duration, cur + chunk_len)
                default_chunks.append({
                    "id": idx,
                    "name": f"Bagian {idx} ({int(cur)}s - {int(end_t)}s)",
                    "start": round(cur, 2),
                    "end": round(end_t, 2)
                })
                cur = end_t
                idx += 1
            self.chunks_data[key] = default_chunks
            self.save()

        return self.chunks_data[key]

    def add_custom_chunk(self, midi_path: str, start: float, end: float, name: str = None) -> Dict[str, Any]:
        key = self._get_song_key(midi_path)
        if key not in self.chunks_data:
            self.chunks_data[key] = []

        chunk_list = self.chunks_data[key]
        idx = len(chunk_list) + 1
        if not name:
            name = f"Bagian {idx} ({int(start)}s - {int(end)}s)"

        new_chunk = {
            "id": idx,
            "name": name,
            "start": round(start, 2),
            "end": round(end, 2)
        }
        chunk_list.append(new_chunk)
        self.save()
        return new_chunk

    def rename_chunk(self, midi_path: str, chunk_index: int, new_name: str):
        key = self._get_song_key(midi_path)
        if key in self.chunks_data and 0 <= chunk_index < len(self.chunks_data[key]):
            self.chunks_data[key][chunk_index]["name"] = new_name
            self.save()

    def update_chunk_bounds(self, midi_path: str, chunk_index: int, start: float, end: float):
        key = self._get_song_key(midi_path)
        if key in self.chunks_data and 0 <= chunk_index < len(self.chunks_data[key]):
            self.chunks_data[key][chunk_index]["start"] = round(start, 2)
            self.chunks_data[key][chunk_index]["end"] = round(end, 2)
            self.save()

    def reset_chunks_for_song(self, midi_path: str, total_duration: float):
        key = self._get_song_key(midi_path)
        if key in self.chunks_data:
            del self.chunks_data[key]
        return self.get_chunks_for_song(midi_path, total_duration)


chunk_manager = ChunkManager()
