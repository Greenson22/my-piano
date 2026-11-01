# Aturan & Panduan Pengembangan Proyek Piano

Dokumen ini adalah acuan utama bagi AI Agent dan developer dalam mengembangkan, memodifikasi, dan merawat codebase proyek ini.

---

## 1. Prinsip Utama Proyek
1. **Pertahankan Fitur Lama (Backward Compatibility):**
   - Mode visualizer nada asli yang sudah ada harus tetap berfungsi dan tidak boleh dirusak atau dihilangkan saat fitur baru ditambahkan.
2. **Keterbacaan & Modularitas:**
   - Pisahkan logika dengan jelas antara audio/MIDI, scene (layar), entity (objek gambar), dan utilitas.
   - Hindari menulis seluruh logika dalam satu file raksasa (*God Object/File*).
3. **Pembaruan Berkas Fitur:**
   - Setiap kali ada fitur baru yang direncanakan, sedang dikerjakan, atau selesai diimplementasikan, selalu perbarui file `.agent/feature.txt`.

---

## 2. Standar Struktur Direktori & Penempatan File
Struktur folder harus selalu dijaga rapi dan terorganisir sesuai skema berikut:

```text
piano/
├── .agent/                      # Aturan dan inventaris fitur
│   ├── rule.md
│   └── feature.txt
│
├── assets/                      # File eksternal non-kode
│   ├── soundfonts/              # Berkas instrumen (.sf2) untuk suara internal laptop
│   └── fonts/                   # Font kustom untuk antarmuka UI
│
├── midi/                        # Koleksi file lagu MIDI klasik
│   └── *.mid
│
├── src/                         # Seluruh kode sumber utama
│   ├── audio/                   # Urusan suara & MIDI (midi_io, midi_parser, sound_synth)
│   ├── entities/                # Komponen objek permainan (piano_keyboard, falling_note, visual_note, mascot)
│   ├── scenes/                  # Halaman tampilan antarmuka (main_menu, visualizer_scene, game_scene, settings_scene)
│   └── utils/                   # Fungsi bantuan & konstanta umum (constants.py, dsb.)
│
├── main.py                      # Titik masuk utama aplikasi (entry point)
└── requirements.txt             # Daftar dependensi library Python
```

---

## 3. Aturan Teknis Spesifik

### A. Audio & MIDI
- **Dual Output:** Dukung pemutaran suara melalui speaker internal laptop (via synth/SoundFont) dan/atau output ke perangkat MIDI eksternal.
- **Pilihan Suara:** Sediakan pengaturan untuk memilih preset suara piano (misal: Concert Grand, Bright Upright, Mellow Piano).
- **Thread Safety:** Penanganan input MIDI (`midi_listener`) dan playback harus berjalan pada thread non-blocking serta aman dari *race condition* (`threading.Lock`).

### B. Gameplay & Pembelajaran Piano Klasik
- **Visual Falling Notes (Synthesia-style):**
  - Balok not jatuh dari atas menuju tuts bawah secara proporsional terhadap tempo dan durasi not.
  - Pisahkan visualisasi/latihan antara tangan kiri (bass/iringan) dan tangan kanan (melodi) dengan warna berbeda.
- **Mode Belajar:**
  - *Wait Mode:* Lagu menunggu hingga pemain menekan tuts yang benar sebelum melanjutkan.
  - *Strict Rhythm Mode:* Lagu terus berjalan sesuai tempo dengan penilaian akurasi (*Perfect*, *Great*, *Miss*).
- **Pengatur Kecepatan:** Menyediakan kontrol tempo (50% - 100%) tanpa merusak nada/pitch.

### C. Maskot Karakter Bunga Matahari (Interactive Sunflower Companion)
- Karakter tanaman bunga matahari harus diletakkan secara modular di `src/entities/mascot.py`.
- Animasi harus halus (*smooth damping/interpolation/lerp*) dan reaktif terhadap:
  - Pitch nada (meliuk ke kiri untuk nada rendah, melompat/condong ke kanan untuk nada tinggi).
  - Velocity nada (ekspresi senang/kejutan/partikel saat dipukul forte).
  - Ketepatan nada (senyum bahagia saat not tepat, animasi bingung/menunggu saat wait mode).

### D. Visual & Estetika Antarmuka (UI)
- Menggunakan tema modern gelap (*dark minimalist / elegant synthwave*) agar tuts dan balok not terlihat kontras, elegan, dan nyaman di mata.
- Berikan efek visual yang memuaskan: kilau tuts saat ditekan (*key glow*), garis pemandu oktaf, serta partikel saat not tepat mengenai hit-line.
