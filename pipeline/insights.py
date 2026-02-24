from collections import defaultdict
from transformers import pipeline
import torch

# Device detection
DEVICE = 0 if torch.cuda.is_available() else -1

sentiment_model = pipeline(
    "sentiment-analysis",
    device=DEVICE
)


def talk_time(merged_segments):

    time_per_speaker = defaultdict(float)

    for seg in merged_segments:
        duration = seg["end"] - seg["start"]
        time_per_speaker[seg["speaker"]] += duration

    return dict(time_per_speaker)


def sentiment_per_speaker(speaker_text):

    sentiments = {}

    for speaker, text in speaker_text.items():

        if len(text.strip()) == 0:
            sentiments[speaker] = "Neutral"
            continue

        # Truncate text to reduce processing time
        short_text = text[:512]

        try:
            result = sentiment_model(short_text)[0]
            sentiments[speaker] = result["label"]

        except Exception:
            sentiments[speaker] = "Neutral"

    return sentiments