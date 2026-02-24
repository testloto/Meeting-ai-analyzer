import streamlit as st
import tempfile
import subprocess
import os
import threading

from pipeline.transcription import transcribe
from pipeline.diarization import diarize
from pipeline.merger import merge_transcript
from pipeline.summarizer import (
    speaker_wise_summary,
    overall_summary,
    extract_action_items
)
from pipeline.translation import translate_to_hindi
from pipeline.insights import talk_time, sentiment_per_speaker


# -----------------------------
# File Helpers
# -----------------------------

def save_uploaded_file(uploaded_file):
    suffix = os.path.splitext(uploaded_file.name)[1]

    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(uploaded_file.read())
        return tmp.name


def convert_to_wav(input_path):
    output_path = input_path + ".wav"

    command = [
        "ffmpeg",
        "-y",
        "-i", input_path,
        "-ac", "1",
        "-ar", "16000",
        "-threads", "4",
        output_path
    ]

    subprocess.run(
        command,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

    return output_path


# -----------------------------
# Streamlit UI
# -----------------------------

st.title("MeetSage AI — Meeting Intelligence")

uploaded = st.file_uploader(
    "Upload Meeting Audio / Video",
    type=["wav", "mp3", "mp4", "m4a"]
)

if uploaded:

    progress = st.progress(0)
    status = st.empty()

    with st.spinner("Processing meeting..."):

        # Save file
        status.text("Saving file...")
        input_path = save_uploaded_file(uploaded)
        progress.progress(10)

        # Convert audio
        status.text("Converting audio...")
        audio_path = convert_to_wav(input_path)
        progress.progress(20)

        # -----------------------------
        # Parallel Transcription + Diarization
        # -----------------------------

        results = {
          "whisper": None,
          "diarization": None
}

        def run_transcription():
         results["whisper"] = transcribe(audio_path)
 
        def run_diarization():
         results["diarization"] = diarize(audio_path)

        status.text("Running AI models...")

        t1 = threading.Thread(target=run_transcription)
        t2 = threading.Thread(target=run_diarization)

        t1.start()
        t2.start()

        t1.join()
        progress.progress(50)

        t2.join()
        progress.progress(70)

        whisper_segments = results["whisper"]
        diarization_segments = results["diarization"]

        # Merge
        status.text("Merging speaker data...")
        merged, speaker_text = merge_transcript(
            diarization_segments,
            whisper_segments
        )

        full_text = " ".join([m["text"] for m in merged])
        progress.progress(80)

        # Summaries
        status.text("Generating summaries...")
        speaker_summaries = speaker_wise_summary(speaker_text)
        overall = overall_summary(full_text)
        progress.progress(90)

        # Translation
        status.text("Translating...")
        hindi_summary = translate_to_hindi(overall)

        # Insights
        talk = talk_time(merged)
        sentiment = sentiment_per_speaker(speaker_text)

        progress.progress(100)
        status.text("Done!")

    # Cleanup temp files
    try:
        os.remove(input_path)
        os.remove(audio_path)
    except:
        pass

    # ---------------- UI ---------------- #

    st.success("Processing Complete ✅")

    st.header("Speaker Wise Transcript")

    for m in merged:
        st.write(
            f"[{m['start']:.2f}-{m['end']:.2f}] "
            f"{m['speaker']}: {m['text']}"
        )

    st.header("Speaker Wise Summaries")

    for sp, summ in speaker_summaries.items():
        st.subheader(sp)
        st.write(summ)

    st.header("Overall Meeting Summary (English)")
    st.write(overall)

    st.header("Overall Meeting Summary (Hindi)")
    st.write(hindi_summary)

    st.header("Insights")

    st.write("Talk Time:", talk)
    st.write("Sentiment:", sentiment)

    st.header("Action Items")

    actions = extract_action_items(full_text)

    for a in actions:
        st.write("-", a)