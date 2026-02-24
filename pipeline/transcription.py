from faster_whisper import WhisperModel
import tempfile
import os
import torch

# Auto device detection
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

# Load once
model = WhisperModel(
    "base",
    device=DEVICE,
    compute_type="float16" if DEVICE == "cuda" else "int8"
)


def transcribe(audio_input):

    if isinstance(audio_input, str):
        audio_path = audio_input
    else:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
            tmp.write(audio_input.read())
            audio_path = tmp.name

    if not os.path.exists(audio_path):
        raise ValueError("Audio file not found")

    segments, _ = model.transcribe(
        audio_path,
        beam_size=5,
        vad_filter=True   # skip silence → faster
    )

    result = []

    for seg in segments:
        result.append({
            "start": seg.start,
            "end": seg.end,
            "text": seg.text
        })

    return result


