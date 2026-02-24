from pyannote.audio import Pipeline
import torch

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

pipeline = None


def get_pipeline():
    global pipeline
    if pipeline is None:
        pipeline = Pipeline.from_pretrained(
            "pyannote/speaker-diarization",
            use_auth_token="YOUR_TOKEN"
        )
        pipeline.to(torch.device(DEVICE))
    return pipeline


def diarize(audio_file):

    pipe = get_pipeline()

    diarization = pipe({"audio": audio_file})

    speakers = []

    for turn, _, speaker in diarization.itertracks(yield_label=True):
        speakers.append({
            "start": turn.start,
            "end": turn.end,
            "speaker": speaker
        })

    return speakers