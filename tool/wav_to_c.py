import wave

def audio_to_c_file(input_file, output_file):
    with wave.open(input_file, 'rb') as wav_file:
        channels = wav_file.getnchannels()
        sample_rate = wav_file.getframerate()
        bit_depth = wav_file.getsampwidth() * 8
        data = wav_file.readframes(wav_file.getnframes())

    with open(output_file, "w") as f:
        f.write("// WAV file information\n")
        f.write(f"// Channels: {channels}\n")
        f.write(f"// Sample Rate: {sample_rate} Hz\n")
        f.write(f"// Bit Depth: {bit_depth} bits\n\n")
        f.write("const unsigned char audioData[] = {\n")

        for i, byte in enumerate(data):
            if i % 12 == 0:
                f.write("\n    ")
            f.write(f"0x{byte:02x}, ")

        f.write("\n};\n")
        f.write(f"const unsigned int audioDataSize = {len(data)};\n")

# 使用示例
audio_to_c_file("tool\start.wav", "audio_data.c")