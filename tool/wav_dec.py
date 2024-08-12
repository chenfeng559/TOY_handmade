import wave

def get_wav_info(file_path):
    with wave.open(file_path, 'rb') as wav_file:
        channels = wav_file.getnchannels()
        sample_rate = wav_file.getframerate()
        bit_depth = wav_file.getsampwidth() * 8

    return sample_rate, channels, bit_depth

# 使用示例
file_path = 'tool\end.wav'
sample_rate, channels, bit_depth = get_wav_info(file_path)
print(f"Sample Rate: {sample_rate} Hz")
print(f"Channels: {channels}")
print(f"Bit Depth: {bit_depth} bits")

"""
start.wav
Sample Rate: 44100 Hz
Channels: 2
Bit Depth: 16 bits
"""


"""
end.wav
Sample Rate: 44100 Hz
Channels: 2
Bit Depth: 16 bits

"""