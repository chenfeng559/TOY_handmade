from pydub import AudioSegment

def convert_audio(input_file, output_file):
    # 读取 PCM 文件，指定格式
    audio = AudioSegment.from_file(input_file, format="raw", frame_rate=44100, channels=1, sample_width=2)
    
    # 转换为单声道
    audio = audio.set_channels(1)

    # 重采样到 16 kHz
    audio = audio.set_frame_rate(16000)

    # 导出为 PCM 格式
    audio.export(output_file, format="raw")

convert_audio("output.pcm", "pcm_16k.pcm")