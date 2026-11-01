import math
import numpy as np
import pygame

class SoundSynth:
    """
    Synthesizer audio internal berbasis additive/physical-modeling sampling
    yang menghasilkan suara langsung dari speaker laptop tanpa file eksternal besar.
    Mendukung beberapa preset karakter suara piano:
    1. Grand Piano (akustik hangat, harmonik kaya)
    2. Bright Upright (renyah, tajam, cocok untuk pop/klasik ringan)
    3. Mellow Piano (lembut, warm, cocok untuk nocturne/ballad)
    4. Electric Piano / Rhodes (halus, dengan modulasi bell tone)
    """

    PRESETS = [
        "Concert Grand Piano",
        "Bright Upright Piano",
        "Mellow Piano",
        "Electric Piano (Rhodes)"
    ]

    def __init__(self, sample_rate=44100):
        self.sample_rate = sample_rate
        self.preset_idx = 0
        self.volume = 0.8
        self.cache = {}

        # Pastikan pygame.mixer sudah diinisialisasi
        if not pygame.mixer.get_init():
            pygame.mixer.pre_init(frequency=sample_rate, size=-16, channels=2, buffer=512)
            pygame.mixer.init()

        pygame.mixer.set_num_channels(32)

    @property
    def current_preset_name(self) -> str:
        return self.PRESETS[self.preset_idx]

    def cycle_preset(self, direction=1):
        self.preset_idx = (self.preset_idx + direction) % len(self.PRESETS)
        self.cache.clear()
        return self.current_preset_name

    def set_preset_by_index(self, index: int):
        self.preset_idx = index % len(self.PRESETS)
        self.cache.clear()

    def set_volume(self, vol: float):
        self.volume = max(0.0, min(1.0, vol))

    def _generate_sound(self, pitch: int, preset_type: str) -> pygame.mixer.Sound:
        """Sintesis sample waveform piano multi-harmonik."""
        freq = 440.0 * (2.0 ** ((pitch - 69) / 12.0))
        duration = 2.4 # detik

        # Nada tinggi berdurasi lebih singkat secara alami
        if pitch > 72:
            duration = max(0.9, 2.4 - (pitch - 72) * 0.04)

        num_samples = int(self.sample_rate * duration)
        t = np.linspace(0, duration, num_samples, False)

        # Karakter harmonik berdasarkan preset
        if preset_type == "Bright Upright Piano":
            harmonics = [(1, 1.0), (2, 0.65), (3, 0.45), (4, 0.25), (5, 0.15), (6, 0.08)]
            decay_rate = 3.2
        elif preset_type == "Mellow Piano":
            harmonics = [(1, 1.0), (2, 0.35), (3, 0.12), (4, 0.03)]
            decay_rate = 2.0
        elif preset_type == "Electric Piano (Rhodes)":
            harmonics = [(1, 0.9), (2, 0.2), (3, 0.4), (7, 0.12)]
            decay_rate = 2.4
        else: # Concert Grand Piano
            harmonics = [(1, 1.0), (2, 0.5), (3, 0.3), (4, 0.18), (5, 0.08), (6, 0.04)]
            decay_rate = 2.6

        wave = np.zeros(num_samples, dtype=np.float32)
        for h, weight in harmonics:
            # Sedikit inharmonicity piano akustik
            h_freq = freq * h * math.sqrt(1 + 0.0003 * (h ** 2))
            wave += weight * np.sin(2 * np.pi * h_freq * t)

        # Envelope ADSR realistis untuk piano
        # Attack sangat cepat (< 5ms)
        attack_len = int(self.sample_rate * 0.005)
        if attack_len > 0:
            attack_env = np.linspace(0, 1, attack_len, dtype=np.float32)
            wave[:attack_len] *= attack_env

        # Exponential decay
        decay_env = np.exp(-decay_rate * t).astype(np.float32)
        wave *= decay_env

        # Normalisasi ke 16-bit PCM Stereo
        max_val = np.max(np.abs(wave))
        if max_val > 0:
            wave = (wave / max_val) * 32000.0

        samples_16 = wave.astype(np.int16)
        stereo_samples = np.column_stack((samples_16, samples_16))

        sound = pygame.sndarray.make_sound(stereo_samples)
        return sound

    def play_note(self, pitch: int, velocity: int = 80):
        """Membunyikan nada tertentu sesuai velocity."""
        if pitch < 21 or pitch > 108:
            return

        cache_key = (pitch, self.preset_idx)
        if cache_key not in self.cache:
            self.cache[cache_key] = self._generate_sound(pitch, self.current_preset_name)

        sound = self.cache[cache_key]
        vol = (velocity / 127.0) * self.volume
        channel = pygame.mixer.find_channel(True)
        if channel:
            channel.set_volume(vol)
            channel.play(sound)


# Instansiasi singleton synth global
synth_instance = SoundSynth()
