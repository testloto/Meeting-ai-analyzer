import subprocess
from config import AUDIO_PATH


def extract_audio(video_path):
    cmd = [
        "ffmpeg",
        "-y",                     # overwrite
        "-i", video_path,
        "-vn",
        "-acodec", "pcm_s16le",
        "-ar", "16000",
        "-ac", "1",
        "-threads", "4",          # use CPU threads
        AUDIO_PATH
    ]

    process = subprocess.run(
        cmd,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

    if process.returncode != 0:
        raise RuntimeError("Audio extraction failed")

    return AUDIO_PATH