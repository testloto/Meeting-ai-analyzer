from transformers import pipeline
import torch

# Device detection
DEVICE = 0 if torch.cuda.is_available() else -1

# Load model once
summarizer = pipeline(
    "summarization",
    model="sshleifer/distilbart-cnn-12-6",
    device=DEVICE
)


def chunk_text(text, max_words=400):
    """
    Split text into word-based chunks (better for NLP).
    """
    words = text.split()
    chunks = []

    for i in range(0, len(words), max_words):
        chunk = " ".join(words[i:i + max_words])
        chunks.append(chunk)

    return chunks


def summarize_chunks(chunks, max_len=120):

    summaries = []

    for chunk in chunks:
        if len(chunk.strip()) == 0:
            continue

        try:
            result = summarizer(
                chunk,
                max_length=max_len,
                min_length=30,
                do_sample=False,
                truncation=True
            )

            summaries.append(result[0]["summary_text"])

        except Exception as e:
            print("Summarization error:", e)

    return " ".join(summaries)


def summarize_text(text):

    if len(text.strip()) == 0:
        return ""

    chunks = chunk_text(text)

    return summarize_chunks(chunks)


def speaker_wise_summary(speaker_text_dict):

    summaries = {}

    for speaker, text in speaker_text_dict.items():
        summaries[speaker] = summarize_text(text)

    return summaries


def overall_summary(full_text):
    return summarize_text(full_text)


def extract_action_items(text):
    """
    Lightweight action item extraction
    """

    sentences = text.split(".")
    actions = []

    keywords = ["will", "should", "need to", "action", "must", "plan"]

    for s in sentences:
        if any(k in s.lower() for k in keywords):
            actions.append(s.strip())

    return actions