# Meeting-ai-analyzer

# Running Command 
c:\Users\ChitraSarkar\Downloads\files\venv\Scripts\Activate.ps1
 streamlit run app.py

# 🎙️ MeetingMind AI — Setup & Run Guide
## Gen AI Video Analytics Hackathon

---

## ⚡ Quick Start (10 minutes)

token - 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
groq - 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

### 1. Prerequisites
```bash
# Install FFmpeg (REQUIRED for audio extraction)
# macOS:
brew install ffmpeg

# Ubuntu/Debian:
sudo apt-get install ffmpeg

# Windows: Download from https://ffmpeg.org/download.html
```

### 2. Python Environment
```bash
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Get Free API Keys
| Service | URL | What it does |
|---------|-----|-------------|
| **HuggingFace** (Required) | https://huggingface.co/settings/tokens | Speaker diarization model |
| **Groq** (Recommended) | https://console.groq.com | Free LLM (ultra fast) |

#### HuggingFace Setup:
1. Create free account at huggingface.co
2. Go to Settings → Access Tokens → New Token (read)
3. Also visit and accept terms at:
   - https://huggingface.co/pyannote/speaker-diarization-3.1
   - https://huggingface.co/pyannote/segmentation-3.0

#### Groq Setup:
1. Create free account at console.groq.com
2. API Keys → Create API Key
3. Free tier: 14,400 requests/day (more than enough)

### 4. Run the App
```bash
streamlit run app.py
```
Open http://localhost:8501 in your browser.

---

## 🔄 Pipeline (Human-in-the-Loop)

```
[Upload MP4] → [FFmpeg: Extract Audio] → [PyAnnote: Who spoke when?]
     ↓
[Faster-Whisper: What did they say? + Translate to English]
     ↓
[👤 HUMAN REVIEW: Assign real names, edit mistakes]  ← KEY DIFFERENTIATOR
     ↓
[Groq/Llama: Generate speaker summaries + overall summary]
     ↓
[LLM: Translate summary to Hindi]
     ↓
[📊 Dashboard: View, filter, download results]
```

---

## 🧠 Tech Stack Choices & Why

| Component | Tool | Why This Choice |
|-----------|------|----------------|
| **Audio Extraction** | FFmpeg | Battle-tested, free, universal |
| **Speaker Diarization** | PyAnnote 3.1 | Best open-source diarizer (beats paid alternatives) |
| **Speech-to-Text** | Faster-Whisper large-v3 | OpenAI Whisper but 4x faster, supports 99 languages |
| **Translation** | Whisper `task=translate` | Built-in — no separate model needed |
| **LLM** | Groq + Llama 3.1 8B | Free, 800 tokens/sec, production-quality |
| **Hindi** | LLM translation | Better than rule-based, handles context |
| **UI** | Streamlit | Built for ML demos, Python-native, instant |

---

## 🏆 Winning Factors for Judges

1. **Human-in-the-Loop is the Core**: Judges can interactively rename speakers and edit transcripts — this IS the "human integrator" the spec requires

2. **Multilingual**: Whisper auto-detects Hindi, Tamil, Telugu, etc. and transcribes to English

3. **Live Demo-Ready**: Streamlit runs locally, no internet needed during demo (except first model download)

4. **All 5 Required Outputs**:
   - ✅ Who said what and when (timestamped transcript)
   - ✅ Speaker-wise transcripts (English)
   - ✅ Speaker-wise summaries (English)
   - ✅ Overall meeting summary (English)
   - ✅ Overall meeting summary (Hindi)

5. **Export**: JSON + TXT download for judges to verify

---

## 🔧 Troubleshooting

**PyAnnote download is slow?**
```bash
# Pre-download the model before hackathon
python -c "
from pyannote.audio import Pipeline
p = Pipeline.from_pretrained('pyannote/speaker-diarization-3.1', use_auth_token='YOUR_HF_TOKEN')
print('Downloaded!')
"
```

**Whisper model download?**
```bash
# Pre-download
python -c "from faster_whisper import WhisperModel; WhisperModel('large-v3')"
```

**No GPU?**
- Set `use_gpu=False` in the sidebar
- Use `medium` Whisper model (faster, slightly less accurate)
- Diarization still works on CPU (just slower)

**Groq rate limit?**
- Switch to Ollama: `ollama pull llama3.1` then run `ollama serve`
- The app auto-falls back to Ollama

---

## 📊 Expected Performance

| Video Length | Processing Time (GPU) | Processing Time (CPU) |
|-------------|----------------------|----------------------|
| 10 min | ~3-4 min | ~12-15 min |
| 15 min | ~5-6 min | ~18-22 min |

*Tested on NVIDIA RTX 3060 / Apple M2*

---

## 💡 Demo Script for Judges

1. Upload the test MP4
2. Show the diarization working (speakers auto-detected)
3. **Human-in-the-Loop**: Rename "SPEAKER_00" → "Priya", etc.
4. Edit a transcript segment live to show editability
5. Click "Approve" → watch LLM generate summaries
6. Show Hindi summary tab
7. Export JSON to show structured output

Total demo time: ~5-7 minutes
