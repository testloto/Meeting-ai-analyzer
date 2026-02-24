from collections import defaultdict


def merge_transcript(diarization_segments, whisper_segments):

    merged = []
    speaker_text = defaultdict(str)

    d_index = 0
    d_len = len(diarization_segments)

    for w in whisper_segments:

        start = w["start"]
        end = w["end"]
        text = w["text"]

        speaker = "Unknown"

        while d_index < d_len:
            d = diarization_segments[d_index]

            if d["start"] <= start <= d["end"]:
                speaker = d["speaker"]
                break

            if start > d["end"]:
                d_index += 1
            else:
                break

        merged.append({
            "speaker": speaker,
            "start": start,
            "end": end,
            "text": text
        })

        speaker_text[speaker] += " " + text

    return merged, speaker_text