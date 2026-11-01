import mido

# 1. Tampilkan daftar perangkat MIDI yang terhubung
print("Perangkat MIDI terdeteksi:")
print(mido.get_input_names())

# 2. Buka koneksi ke piano Anda (ganti nama sesuai hasil print di atas)
# Contoh: input_name = 'Yamaha Digital Piano 0'
try:
    input_name = mido.get_input_names()[0]
    with mido.open_input(input_name) as inport:
        print(f"\nTerhubung ke: {input_name}")
        print("Silakan tekan tuts piano Anda...\n")
        
        for msg in inport:
            if msg.type == 'note_on' and msg.velocity > 0:
                print(f"Not Ditekan -> Pitch: {msg.note} | Kecepatan/Kekuatan: {msg.velocity}")
            elif msg.type == 'note_off' or (msg.type == 'note_on' and msg.velocity == 0):
                print(f"Not Dilepas -> Pitch: {msg.note}")

except IndexError:
    print("Piano belum terdeteksi. Pastikan kabel sudah terpasang dengan benar.")