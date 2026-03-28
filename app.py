"""
MeetingMind AI — v4 Final
==========================
FIXES & NEW FEATURES:
  ✦ Date/time extracted directly from video metadata → shown in Calendar
  ✦ Multilingual FIXED — correct gTTS language codes, robust translation
  ✦ Hindi summary ALWAYS generated (dedicated tab, never missing)
  ✦ Summary audio FIXED — TTS saved, verified, played in every tab
  ✦ Plotly analytics charts (talk time, words, timeline, radar)
  ✦ MOM (Minutes of Meeting) with action items table
  ✦ Emoji-based Meeting Health gauge
  ✦ Per-segment clickable audio clips
  ✦ Auto speaker name detection from video metadata
"""

import streamlit as st
import os, re, json, subprocess, tempfile, time, base64
from pathlib import Path
from datetime import datetime

st.set_page_config(
    page_title="MeetingMind AI",
    page_icon="🎙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ──────────────────────────────────────────────────────────────────────────────
# CSS
# ──────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&family=Outfit:wght@300;400;500;600;700&display=swap');

:root{
  --bg:#070b14; --surface:#0d1220; --card:#131929; --card2:#1a2235;
  --accent:#00e5ff; --accent2:#8b5cf6; --accent3:#10b981; --accent4:#f59e0b;
  --text:#e2e8f0; --muted:#64748b; --border:#1e2d47;
}
*{box-sizing:border-box;}
.stApp{background:var(--bg);color:var(--text);font-family:'Outfit',sans-serif;}
.stApp header,.stApp footer{background:transparent!important;}

.hero-title{
  font-family:'JetBrains Mono',monospace;font-size:3rem;font-weight:700;
  background:linear-gradient(135deg,#00e5ff 0%,#8b5cf6 50%,#10b981 100%);
  -webkit-background-clip:text;-webkit-text-fill-color:transparent;
  background-clip:text;letter-spacing:-2px;line-height:1;
}
.hero-sub{
  font-family:'JetBrains Mono',monospace;font-size:0.7rem;
  color:var(--muted);letter-spacing:4px;text-transform:uppercase;margin-top:4px;
}
.step-card{
  background:linear-gradient(135deg,var(--card),var(--card2));
  border:1px solid var(--border);border-radius:16px;
  padding:1.4rem 1.8rem;margin:0.8rem 0;position:relative;overflow:hidden;
}
.step-card::before{
  content:'';position:absolute;top:0;left:0;width:4px;height:100%;
  background:linear-gradient(180deg,#00e5ff,#8b5cf6,#10b981);
}
.step-number{
  font-family:'JetBrains Mono',monospace;font-size:0.6rem;
  color:#00e5ff;letter-spacing:3px;text-transform:uppercase;margin-bottom:0.4rem;
}
.metric-box{
  background:var(--card2);border:1px solid var(--border);
  border-radius:12px;padding:1.1rem;text-align:center;
  transition:transform 0.2s,border-color 0.2s;
}
.metric-box:hover{transform:translateY(-2px);border-color:var(--accent);}
.metric-val{font-family:'JetBrains Mono',monospace;font-size:1.7rem;font-weight:700;color:#00e5ff;}
.metric-label{font-size:0.68rem;color:var(--muted);text-transform:uppercase;letter-spacing:1.5px;margin-top:2px;}
.summary-box{
  background:linear-gradient(135deg,rgba(0,229,255,0.04),rgba(139,92,246,0.04));
  border:1px solid rgba(0,229,255,0.18);border-radius:14px;padding:1.5rem;margin:0.8rem 0;
}
.hindi-box{
  background:linear-gradient(135deg,rgba(255,153,0,0.06),rgba(19,136,8,0.06));
  border:1px solid rgba(255,153,0,0.3);border-radius:14px;
  padding:1.5rem;margin:0.8rem 0;font-size:1.05rem;line-height:2;
}
.health-ring-wrap{text-align:center;padding:1.5rem 0;}
.health-score-num{font-family:'JetBrains Mono',monospace;font-size:5rem;font-weight:700;line-height:1;}
.health-label{font-size:0.75rem;color:var(--muted);letter-spacing:3px;text-transform:uppercase;margin-top:6px;}
.health-emoji{font-size:2.5rem;}
.speaker-chip{
  display:inline-block;padding:5px 14px;border-radius:20px;
  font-size:0.78rem;font-weight:600;margin:2px;font-family:'JetBrains Mono',monospace;
}
.lang-badge{
  display:inline-block;padding:3px 10px;border-radius:12px;
  font-family:'JetBrains Mono',monospace;font-size:0.65rem;
  background:rgba(0,229,255,0.12);color:#00e5ff;
  border:1px solid rgba(0,229,255,0.3);margin-left:8px;vertical-align:middle;
}
.name-detected-badge{
  background:rgba(16,185,129,0.15);border:1px solid rgba(16,185,129,0.4);
  border-radius:6px;padding:0.3rem 0.7rem;font-size:0.7rem;color:#10b981;
  font-family:'JetBrains Mono',monospace;display:inline-block;margin-left:0.5rem;vertical-align:middle;
}
.name-manual-badge{
  background:rgba(245,158,11,0.15);border:1px solid rgba(245,158,11,0.4);
  border-radius:6px;padding:0.3rem 0.7rem;font-size:0.7rem;color:#f59e0b;
  font-family:'JetBrains Mono',monospace;display:inline-block;margin-left:0.5rem;vertical-align:middle;
}
.stButton>button{
  background:linear-gradient(135deg,#00e5ff,#8b5cf6)!important;
  color:#0a0e1a!important;border:none!important;border-radius:10px!important;
  font-family:'JetBrains Mono',monospace!important;font-size:0.78rem!important;
  letter-spacing:1px!important;padding:0.65rem 1.6rem!important;font-weight:700!important;
}
.pipeline-status{
  font-family:'JetBrains Mono',monospace;font-size:0.72rem;
  padding:0.3rem 0.9rem;border-radius:20px;display:inline-block;margin-bottom:4px;
}
.status-done{background:#10b98120;color:#10b981;border:1px solid #10b98150;}
.status-running{background:#00e5ff20;color:#00e5ff;border:1px solid #00e5ff50;}
.status-pending{background:#64748b20;color:#64748b;border:1px solid #64748b50;}
.warning-box{background:rgba(245,158,11,0.09);border:1px solid rgba(245,158,11,0.3);border-radius:10px;padding:0.9rem 1.1rem;font-size:0.85rem;color:#fbbf24;}
.info-box{background:rgba(0,229,255,0.06);border:1px solid rgba(0,229,255,0.22);border-radius:10px;padding:0.9rem 1.1rem;font-size:0.85rem;color:#7dd3fc;margin:0.5rem 0;}
.timestamp-summary-box{background:linear-gradient(135deg,rgba(245,158,11,0.07),rgba(239,68,68,0.04));border:1px solid rgba(245,158,11,0.3);border-radius:14px;padding:1.5rem;margin:1rem 0;}
.audio-badge{font-family:'JetBrains Mono',monospace;font-size:0.58rem;letter-spacing:2px;color:#00e5ff;opacity:0.7;margin-bottom:3px;}
div[data-testid="stFileUploadDropzone"]{background:var(--card)!important;border:2px dashed rgba(0,229,255,0.35)!important;border-radius:14px!important;}
.stProgress>div>div{background:linear-gradient(90deg,#00e5ff,#8b5cf6)!important;}
.stSelectbox>div,.stTextInput>div>div{background:var(--card)!important;}
</style>
""", unsafe_allow_html=True)

# ──────────────────────────────────────────────────────────────────────────────
# Constants
# ──────────────────────────────────────────────────────────────────────────────
SPEAKER_COLORS = [
    ("#00e5ff","#001f2e"),("#8b5cf6","#160a2e"),("#10b981","#0a1e14"),
    ("#f59e0b","#1e1400"),("#ef4444","#1e0808"),("#ec4899","#1e0814"),
]

# gTTS supported language codes (verified)
OUTPUT_LANGUAGES = {
    "English":    ("en","en"),
    "Hindi":      ("hi","hi"),
    "Spanish":    ("es","es"),
    "French":     ("fr","fr"),
    "German":     ("de","de"),
    "Arabic":     ("ar","ar"),
    "Portuguese": ("pt","pt"),
    "Japanese":   ("ja","ja"),
    "Chinese":    ("zh","zh-CN"),
    "Tamil":      ("ta","ta"),
    "Telugu":     ("te","te"),
    "Bengali":    ("bn","bn"),
    "Marathi":    ("mr","mr"),
    "Kannada":    ("kn","kn"),
    "Gujarati":   ("gu","gu"),
    "Russian":    ("ru","ru"),
    "Korean":     ("ko","ko"),
    "Italian":    ("it","it"),
}
# llm_code -> for prompt   tts_code -> for gTTS

HEALTH_EMOJIS = {
    (90,100):("🏆","Exceptional","#10b981"),
    (75, 89):("🌟","Excellent",  "#10b981"),
    (60, 74):("✅","Good",       "#22c55e"),
    (45, 59):("👍","Fair",       "#f59e0b"),
    (30, 44):("⚠️","Needs Work", "#f97316"),
    (0,  29):("🚨","Poor",       "#ef4444"),
}

def get_health_emoji(score_num):
    try:
        s = int(score_num)
        for (lo,hi),(emoji,label,color) in HEALTH_EMOJIS.items():
            if lo <= s <= hi:
                return emoji, label, color
    except Exception:
        pass
    return "❓","Unknown","#64748b"

def get_speaker_color(idx):
    return SPEAKER_COLORS[idx % len(SPEAKER_COLORS)]

def fmt_time(seconds):
    m,s = divmod(int(seconds),60)
    h,m = divmod(m,60)
    return f"{h:02d}:{m:02d}:{s:02d}" if h else f"{m:02d}:{s:02d}"

# ──────────────────────────────────────────────────────────────────────────────
# Audio helpers
# ──────────────────────────────────────────────────────────────────────────────
def extract_audio_clip(audio_path, start, end):
    try:
        dur = max(0.1, end - start)
        r = subprocess.run(
            ["ffmpeg","-y","-ss",str(start),"-t",str(dur),
             "-i",audio_path,"-ac","1","-ar","16000","-f","wav","pipe:1"],
            capture_output=True, timeout=30
        )
        return r.stdout if r.returncode == 0 and r.stdout else None
    except Exception:
        return None

def audio_bytes_to_b64(data):
    return base64.b64encode(data).decode()

def make_tts(text: str, tts_lang_code: str) -> str | None:
    """
    Generate TTS audio. tts_lang_code must be a valid gTTS language code.
    Returns file path or None on failure.
    """
    if not text or not text.strip():
        return None
    # Strip markdown-style bold markers
    clean = re.sub(r"\*\*[^*]*\*\*:?\s*", "", text)
    clean = re.sub(r"\|[^|]+\|", " ", clean)   # strip table cells
    clean = clean.strip()[:700]
    if not clean:
        return None
    try:
        from gtts import gTTS
        tts = gTTS(text=clean, lang=tts_lang_code, slow=False)
        path = os.path.join(
            tempfile.gettempdir(),
            f"mm4_tts_{tts_lang_code}_{abs(hash(clean[:50]))}.mp3"
        )
        tts.save(path)
        # Verify file actually has content
        if os.path.exists(path) and os.path.getsize(path) > 500:
            return path
        return None
    except Exception as e:
        return None

def play_tts_section(text: str, tts_code: str, label: str = ""):
    """Helper: generate + display TTS player with a label."""
    if not text:
        return
    path = make_tts(text, tts_code)
    if path and os.path.exists(path):
        if label:
            st.markdown(f"🔊 **{label}**")
        st.audio(path, format="audio/mp3")

# ──────────────────────────────────────────────────────────────────────────────
# Date extraction from video (NEW)
# ──────────────────────────────────────────────────────────────────────────────
def extract_dates_from_video(video_path: str) -> dict:
    """
    Extract date/time information embedded in the video file.
    Returns dict with keys: recording_date, creation_time, modified_time, raw_tags
    """
    result = {
        "recording_date": None,
        "creation_time":  None,
        "modified_time":  None,
        "duration_secs":  None,
        "raw_tags":       {},
    }
    try:
        r = subprocess.run(
            ["ffprobe","-v","quiet","-print_format","json",
             "-show_format","-show_streams", video_path],
            capture_output=True, text=True, timeout=30
        )
        meta = json.loads(r.stdout)
        fmt  = meta.get("format", {})

        # Duration
        try:
            result["duration_secs"] = float(fmt.get("duration", 0))
        except Exception:
            pass

        # Tags
        all_tags = {}
        if "tags" in fmt:
            all_tags.update({k.lower(): v for k,v in fmt["tags"].items()})
        for stream in meta.get("streams", []):
            if "tags" in stream:
                all_tags.update({k.lower(): v for k,v in stream["tags"].items()})
        result["raw_tags"] = all_tags

        # Look for date/time fields
        date_keys = [
            "creation_time","date","recording_date","date_recorded",
            "encoded_date","tagged_date","com.apple.quicktime.creationdate",
            "com.android.version",
        ]
        for key in date_keys:
            val = all_tags.get(key,"")
            if val:
                # Try to parse ISO format  2024-03-15T10:30:00.000000Z
                for fmt_str in [
                    "%Y-%m-%dT%H:%M:%S.%fZ","%Y-%m-%dT%H:%M:%SZ",
                    "%Y-%m-%dT%H:%M:%S","%Y-%m-%d %H:%M:%S",
                    "%Y-%m-%d","%d/%m/%Y","%m/%d/%Y",
                ]:
                    try:
                        dt = datetime.strptime(val[:len(fmt_str)+4].strip(), fmt_str)
                        result["creation_time"] = dt.strftime("%B %d, %Y at %I:%M %p")
                        result["recording_date"] = dt.strftime("%Y-%m-%d")
                        break
                    except Exception:
                        continue
                if result["creation_time"]:
                    break

        # File system fallback
        if not result["creation_time"]:
            try:
                mtime = os.path.getmtime(video_path)
                dt = datetime.fromtimestamp(mtime)
                result["modified_time"] = dt.strftime("%B %d, %Y at %I:%M %p")
            except Exception:
                pass

    except Exception:
        pass

    # Filename date fallback
    if not result["recording_date"]:
        stem = Path(video_path).stem
        # Match YYYY-MM-DD or YYYYMMDD
        m = re.search(r"(\d{4}[-_]?\d{2}[-_]?\d{2})", stem)
        if m:
            raw = m.group(1).replace("-","").replace("_","")
            try:
                dt = datetime.strptime(raw, "%Y%m%d")
                result["recording_date"] = dt.strftime("%Y-%m-%d")
                result["creation_time"]  = dt.strftime("%B %d, %Y")
            except Exception:
                pass

    return result

# ──────────────────────────────────────────────────────────────────────────────
# Speaker name extraction from metadata
# ──────────────────────────────────────────────────────────────────────────────
def extract_speaker_names_from_video(video_path):
    detected = {}
    try:
        r = subprocess.run(
            ["ffprobe","-v","quiet","-print_format","json",
             "-show_format","-show_streams",video_path],
            capture_output=True, text=True, timeout=30
        )
        meta = json.loads(r.stdout)
        all_tags = {}
        if "format" in meta and "tags" in meta["format"]:
            all_tags.update({k.lower(): v for k,v in meta["format"]["tags"].items()})
        for stream in meta.get("streams",[]):
            if "tags" in stream:
                all_tags.update({k.lower(): v for k,v in stream["tags"].items()})
        for key in ["participants","attendees","speakers","comment","description","artist","author"]:
            val = all_tags.get(key,"")
            if not val:
                continue
            for part in re.split(r"[,;\|\n]+", val):
                part = part.strip()
                if 2 <= len(part) <= 40 and re.match(r"^[A-Za-z][A-Za-z'\- \.]+$", part):
                    idx = len(detected)
                    detected[f"SPEAKER_{idx:02d}"] = part
    except Exception:
        pass
    if not detected:
        stem = re.sub(
            r"(zoom|teams|meet|webex|recording|meeting|\d{4}[-_]\d{2}[-_]\d{2}|\d{8})",
            "", Path(video_path).stem, flags=re.IGNORECASE
        )
        for i, tok in enumerate([
            t.strip(" .") for t in re.split(r"[_\-&\s]+", stem)
            if re.match(r"^[A-Z][a-zA-Z']{1,19}$", t.strip(" ."))
        ]):
            detected[f"SPEAKER_{i:02d}"] = tok
    return detected

def resolve_speaker_name(label, detected, fallback_idx):
    if label in detected:
        return detected[label], True
    m = re.search(r"(\d+)$", label)
    if m:
        keys = list(detected.keys())
        idx = int(m.group(1))
        if idx < len(keys):
            return detected[keys[idx]], True
    return f"Participant {fallback_idx+1}", False

# ──────────────────────────────────────────────────────────────────────────────
# LLM helpers
# ──────────────────────────────────────────────────────────────────────────────
def call_llm(prompt: str, cfg: dict, max_tokens: int = 1200) -> str:
    groq_key = cfg.get("groq_key","")
    if groq_key:
        try:
            from groq import Groq
            r = Groq(api_key=groq_key).chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[{"role":"user","content":prompt}],
                max_tokens=max_tokens,
                temperature=0.3,
            )
            return r.choices[0].message.content.strip()
        except Exception as e:
            st.warning(f"Groq: {e}")
    try:
        import requests
        r = requests.post(
            "http://localhost:11434/api/generate",
            json={"model":"llama3.1","prompt":prompt,"stream":False},
            timeout=120
        )
        return r.json()["response"].strip()
    except Exception as e:
        return f"[LLM unavailable: {e}]"

def translate_to_language(text: str, lang_name: str, cfg: dict) -> str:
    """Translate text to the given language using LLM. Returns translated text."""
    if not text or lang_name == "English":
        return text
    prompt = (
        f"You are a professional translator. Translate the following text into {lang_name}.\n"
        f"Rules:\n"
        f"- Return ONLY the translated text\n"
        f"- Do NOT add any preamble, explanation or notes\n"
        f"- Preserve all formatting: bullet points (•/-), newlines, bold markers (**)\n"
        f"- Preserve numbers, timestamps, and proper nouns\n"
        f"- If text is already in {lang_name}, return it unchanged\n\n"
        f"Text to translate:\n{text[:3500]}"
    )
    translated = call_llm(prompt, cfg, max_tokens=2000)
    # Safety: if translation returned an error placeholder, return original
    if translated.startswith("[LLM unavailable"):
        return text
    return translated

def generate_hindi_summary(overall_en: str, cfg: dict) -> str:
    """Always generate Hindi summary using dedicated prompt (more reliable than generic translate)."""
    prompt = (
        f"Aap ek professional meeting analyst hain. Neeche diye gaye English meeting summary ko\n"
        f"Hinglish mein translate karein (Hindi + English mix, Roman script mein likhen).\n\n"
        f"Rules:\n"
        f"- Sirf translated text return karein\n"
        f"- Bullet points aur formatting preserve karein\n"
        f"- Natural conversational Hinglish use karein\n\n"
        f"English Summary:\n{overall_en[:2500]}\n\n"
        f"Hinglish Translation:"
    )
    return call_llm(prompt, cfg, max_tokens=1500)

def extract_dates_from_transcript(full_transcript: str, cfg: dict) -> str:
    """Ask LLM to find any dates/deadlines mentioned in the transcript."""
    prompt = (
        f"Extract ALL dates, deadlines, timeframes, and scheduled events mentioned in this transcript.\n"
        f"Format as a bullet list. If none found, write 'No specific dates mentioned in the discussion.'\n"
        f"Include: meeting dates, project deadlines, follow-up dates, delivery dates, etc.\n\n"
        f"Transcript:\n{full_transcript[:5000]}"
    )
    return call_llm(prompt, cfg, max_tokens=600)

# ──────────────────────────────────────────────────────────────────────────────
# Session State
# ──────────────────────────────────────────────────────────────────────────────
KEYS = [
    "stage","diarization","transcripts","speaker_names","summaries",
    "video_path","audio_path","pause_timestamp","pause_summary",
    "detected_speaker_names","speaker_name_source","seg_audio_cache",
    "output_lang","video_date_info","config",
]
for k in KEYS:
    if k not in st.session_state:
        st.session_state[k] = None

if st.session_state.stage is None:               st.session_state.stage = "upload"
if st.session_state.detected_speaker_names is None: st.session_state.detected_speaker_names = {}
if st.session_state.speaker_name_source is None:    st.session_state.speaker_name_source = {}
if st.session_state.seg_audio_cache is None:        st.session_state.seg_audio_cache = {}
if st.session_state.output_lang is None:            st.session_state.output_lang = "English"
if st.session_state.video_date_info is None:        st.session_state.video_date_info = {}

# ──────────────────────────────────────────────────────────────────────────────
# Sidebar
# ──────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="hero-title">Meeting<br>Mind</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-sub">Gen AI · v4 · Multilingual</div>', unsafe_allow_html=True)
    st.markdown("---")

    st.markdown("**⚙️ Configuration**")
    hf_token      = st.text_input("HuggingFace Token", type="password",
                                   help="Required for PyAnnote diarization")
    groq_key      = st.text_input("Groq API Key", type="password",
                                   help="Free at console.groq.com")
    whisper_model = st.selectbox("Whisper Model", ["large-v3","medium","small","base"])
    use_gpu       = st.checkbox("Use GPU (CUDA)", value=False)

    st.markdown("---")
    st.markdown("**🌐 Output Language**")
    sel_lang = st.selectbox(
        "All summaries translated to:",
        list(OUTPUT_LANGUAGES.keys()), index=0,
        help="Choose language for summaries, MOM, health analysis, etc."
    )
    st.session_state.output_lang = sel_lang
    llm_lang_code, tts_lang_code = OUTPUT_LANGUAGES[sel_lang]
    st.markdown(
        f'<div class="info-box">🌐 Output: <strong>{sel_lang}</strong><br>'
        f'🔊 TTS voice: <strong>{tts_lang_code}</strong><br>'
        f'📝 Hindi summary always included</div>',
        unsafe_allow_html=True
    )

    st.markdown("---")
    st.markdown("**📊 Pipeline**")
    stages = [
        ("upload","Video Upload"),("diarize","Diarization"),
        ("human_loop","Human Review"),("summarize","AI Summaries"),("output","Results"),
    ]
    cur   = st.session_state.stage
    order = [s[0] for s in stages]
    cidx  = order.index(cur) if cur in order else 0
    for i,(sid,sname) in enumerate(stages):
        css  = "status-done" if i<cidx else ("status-running" if i==cidx else "status-pending")
        icon = "✓" if i<cidx else ("▶" if i==cidx else "○")
        st.markdown(f'<div class="pipeline-status {css}">{icon} {sname}</div>',
                    unsafe_allow_html=True)
        st.markdown("")

# ══════════════════════════════════════════════════════════════════════════════
# STAGE 1 — Upload
# ══════════════════════════════════════════════════════════════════════════════
if st.session_state.stage == "upload":
    st.markdown('<div class="hero-title">AI Meeting Analyzer</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="hero-sub">Multilingual · Date Extraction · Hindi Always · Audio Clips · Charts · MOM</div>',
        unsafe_allow_html=True
    )
    st.markdown("<br>", unsafe_allow_html=True)

    c1,c2,c3,c4,c5 = st.columns(5)
    for col,val,lbl in [
        (c1,"18+","Languages"),(c2,"📅","Date Extract"),
        (c3,"🎵","Audio Clips"),(c4,"📊","Charts"),(c5,"📋","MOM"),
    ]:
        with col:
            st.markdown(
                f'<div class="metric-box"><div class="metric-val">{val}</div>'
                f'<div class="metric-label">{lbl}</div></div>',
                unsafe_allow_html=True
            )

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(
        '<div class="step-card"><div class="step-number">Step 01 / Upload</div>'
        '<h3 style="margin:0.3rem 0">Upload Meeting Video</h3>'
        '<p style="color:#64748b;font-size:0.9rem;margin:0">MP4 · MKV · MOV · AVI · WEBM</p></div>',
        unsafe_allow_html=True
    )
    st.markdown(
        f'<div class="info-box">'
        f'📅 <strong>Date Extraction</strong> — recording date pulled from video metadata automatically<br>'
        f'🌐 <strong>Output Language:</strong> {st.session_state.output_lang} (change in sidebar)<br>'
        f'🇮🇳 <strong>Hindi Summary</strong> always generated in a dedicated tab<br>'
        f'🔊 <strong>TTS Audio</strong> in every summary section</div>',
        unsafe_allow_html=True
    )

    uploaded = st.file_uploader("", type=["mp4","mkv","mov","avi","webm"],
                                  label_visibility="collapsed")
    if uploaded:
        tmp = tempfile.mkdtemp()
        vpath = os.path.join(tmp, uploaded.name)
        with open(vpath,"wb") as f: f.write(uploaded.read())
        st.session_state.video_path = vpath

        with st.spinner("🔍 Scanning metadata & extracting dates..."):
            detected  = extract_speaker_names_from_video(vpath)
            date_info = extract_dates_from_video(vpath)
            st.session_state.detected_speaker_names = detected
            st.session_state.video_date_info        = date_info

        # Show what we found
        info_parts = [f"✓ **{uploaded.name}** ({uploaded.size//1024//1024} MB)"]
        if detected:
            info_parts.append(f"👥 Speakers: **{', '.join(detected.values())}**")
        if date_info.get("creation_time"):
            info_parts.append(f"📅 Recorded: **{date_info['creation_time']}**")
        elif date_info.get("modified_time"):
            info_parts.append(f"📅 Modified: **{date_info['modified_time']}**")
        st.success(" · ".join(info_parts))

        col1,col2 = st.columns([3,1])
        with col1:
            st.video(vpath)
        with col2:
            st.markdown("**Settings**")
            max_speakers = st.slider("Max Speakers",2,8,5)
            language     = st.selectbox(
                "Primary Language",
                ["auto-detect","en","hi","ta","te","mr","bn","gu","es","fr","de","ar","zh","ja"]
            )
            st.session_state.config = {
                "max_speakers": max_speakers, "language": language,
                "whisper_model": whisper_model, "use_gpu": use_gpu,
                "hf_token": hf_token, "groq_key": groq_key,
            }

        if st.button("🚀 START ANALYSIS"):
            if not hf_token:
                st.markdown('<div class="warning-box">⚠️ HuggingFace token required.</div>',
                            unsafe_allow_html=True)
            else:
                st.session_state.stage = "diarize"
                st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
# STAGE 2 — Diarization + Transcription
# ══════════════════════════════════════════════════════════════════════════════
elif st.session_state.stage == "diarize":
    st.markdown(
        '<div class="step-card"><div class="step-number">Step 02 / Processing</div>'
        '<h3 style="margin:0.3rem 0">Audio · Diarization · Transcription</h3></div>',
        unsafe_allow_html=True
    )
    progress = st.progress(0)
    status   = st.empty()

    vpath          = st.session_state.video_path
    cfg            = st.session_state.config or {}
    detected_names = st.session_state.detected_speaker_names or {}

    # 1. Audio extraction
    status.markdown("**[1/4]** Extracting audio...")
    progress.progress(10)
    audio_path = vpath.replace(Path(vpath).suffix, "_audio.wav")
    try:
        subprocess.run(
            ["ffmpeg","-i",vpath,"-ac","1","-ar","16000","-vn","-y",audio_path],
            check=True, capture_output=True
        )
        st.session_state.audio_path = audio_path
        progress.progress(25)
    except Exception as e:
        st.error(f"FFmpeg: {e}"); st.stop()

    # 2. Diarization
    status.markdown("**[2/4]** Speaker diarization (PyAnnote)...")
    progress.progress(35)
    try:
        from pyannote.audio import Pipeline
        import torch
        device = "cuda" if cfg.get("use_gpu") and torch.cuda.is_available() else "cpu"
        pipe = Pipeline.from_pretrained(
            "pyannote/speaker-diarization-3.1",
            use_auth_token=cfg["hf_token"]
        )
        pipe.to(torch.device(device))
        dia = pipe(audio_path, max_speakers=cfg.get("max_speakers",5))
        segments = [{"start":round(t.start,2),"end":round(t.end,2),"speaker":s}
                    for t,_,s in dia.itertracks(yield_label=True)]
        st.session_state.diarization = segments
        n_spk = len(set(s["speaker"] for s in segments))
        status.markdown(f"**[2/4]** ✓ {n_spk} speakers found")
        progress.progress(55)
    except ImportError:
        st.error("pip install pyannote.audio"); st.stop()
    except Exception as e:
        st.error(f"Diarization: {e}"); st.stop()

    # Name resolution
    unique_speakers = sorted(set(s["speaker"] for s in segments))
    spk_display = {}; spk_source = {}
    for idx, lbl in enumerate(unique_speakers):
        name, auto = resolve_speaker_name(lbl, detected_names, idx)
        spk_display[lbl] = name
        spk_source[lbl]  = "auto" if auto else "manual"
    st.session_state.speaker_name_source = spk_source

    # 3. Transcription
    status.markdown("**[3/4]** Transcribing with Faster-Whisper...")
    progress.progress(60)
    try:
        from faster_whisper import WhisperModel
        m_size  = cfg.get("whisper_model","large-v3")
        compute = "float16" if cfg.get("use_gpu") else "int8"
        model   = WhisperModel(m_size, device="auto", compute_type=compute)
        lang    = cfg.get("language","auto-detect")
        lang    = None if lang=="auto-detect" else lang
        chunks, _ = model.transcribe(
            audio_path, language=lang, task="translate",
            beam_size=5, vad_filter=True, word_timestamps=True
        )
        all_words = []
        for chunk in chunks:
            if chunk.words: all_words.extend(chunk.words)
            else:
                all_words.append(
                    type('W',(object,),{'start':chunk.start,'end':chunk.end,'word':chunk.text})()
                )

        def best_spk(ws, we, segs):
            b, mo = "Unknown", 0
            for seg in segs:
                ov = max(0, min(we,seg['end'])-max(ws,seg['start']))
                if ov > mo: mo,b = ov,seg['speaker']
            return b

        transcribed = []; cur_spk=None; cur_txt=[]; cur_s=cur_e=0
        for w in all_words:
            ws = best_spk(w.start, w.end, segments)
            if ws == "Unknown": continue
            if cur_spk is None: cur_spk=ws; cur_s=w.start
            if ws != cur_spk:
                if cur_txt:
                    transcribed.append({
                        "start":cur_s,"end":cur_e,"speaker":cur_spk,
                        "original_speaker":cur_spk,
                        "display_name":spk_display.get(cur_spk,cur_spk),
                        "text":"".join(cur_txt).strip()
                    })
                cur_spk=ws; cur_s=w.start; cur_txt=[w.word]
            else:
                cur_txt.append(w.word)
            cur_e = w.end
        if cur_txt:
            transcribed.append({
                "start":cur_s,"end":cur_e,"speaker":cur_spk,
                "original_speaker":cur_spk,
                "display_name":spk_display.get(cur_spk,cur_spk),
                "text":"".join(cur_txt).strip()
            })

        st.session_state.transcripts   = transcribed
        st.session_state.speaker_names = {l:spk_display[l] for l in unique_speakers}
        status.markdown(f"**[4/4]** ✓ {len(transcribed)} utterances transcribed")
        progress.progress(100)
    except Exception as e:
        st.error(f"Transcription: {e}"); st.stop()

    time.sleep(0.4)
    st.session_state.stage = "human_loop"
    st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
# STAGE 3 — Human Review
# ══════════════════════════════════════════════════════════════════════════════
elif st.session_state.stage == "human_loop":
    st.markdown(
        '<div class="step-card"><div class="step-number">Step 03 / Review</div>'
        '<h3 style="margin:0.3rem 0">Confirm Speaker Names</h3></div>',
        unsafe_allow_html=True
    )
    transcripts = st.session_state.transcripts or []
    name_source = st.session_state.speaker_name_source or {}
    pre_filled  = st.session_state.speaker_names or {}
    if not transcripts: st.warning("No transcripts."); st.stop()

    speakers = sorted(set(t["speaker"] for t in transcripts))
    auto_c   = sum(1 for s in speakers if name_source.get(s)=="auto")
    parts    = []
    if auto_c:          parts.append(f'<span class="name-detected-badge">✓ AUTO: {auto_c}</span>')
    if len(speakers)-auto_c: parts.append(f'<span class="name-manual-badge">✎ MANUAL: {len(speakers)-auto_c}</span>')
    if parts: st.markdown("&nbsp;"+"".join(parts), unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    cols = st.columns(min(len(speakers),3))
    speaker_names = {}
    for i, spk in enumerate(speakers):
        color,bg = get_speaker_color(i)
        is_auto  = name_source.get(spk)=="auto"
        badge    = ('<span class="name-detected-badge">✓ auto</span>' if is_auto
                    else '<span class="name-manual-badge">✎ enter</span>')
        with cols[i % min(len(speakers),3)]:
            sample = next((t["text"][:80]+"..." for t in transcripts
                           if t["speaker"]==spk and len(t.get("text",""))>10),"")
            st.markdown(
                f'<div style="background:{bg};border:1px solid {color}44;border-radius:12px;'
                f'padding:1rem;margin-bottom:0.5rem;">'
                f'<span class="speaker-chip" style="background:{color}22;color:{color};'
                f'border:1px solid {color}55;">{spk}</span>{badge}'
                f'<div style="font-size:0.72rem;color:#64748b;margin:0.5rem 0;font-style:italic;">"{sample}"</div>'
                f'</div>',
                unsafe_allow_html=True
            )
            default = pre_filled.get(spk, f"Participant {i+1}")
            speaker_names[spk] = st.text_input(f"Name for {spk}", value=default, key=f"name_{spk}")

    st.markdown("---")
    st.markdown("### 📝 Transcript Preview")
    show_n = st.slider("Segments to show", 5, max(5,len(transcripts)), min(20,len(transcripts)))
    edited = []
    for i, seg in enumerate(transcripts[:show_n]):
        name = speaker_names.get(seg["speaker"], seg["speaker"])
        with st.expander(f"[{fmt_time(seg['start'])}→{fmt_time(seg['end'])}] {name}", expanded=(i<3)):
            et = st.text_area("", value=seg["text"], key=f"seg_{i}", height=70,
                              label_visibility="collapsed")
            edited.append({**seg,"text":et,"display_name":name})
    for seg in transcripts[show_n:]:
        edited.append({**seg,"display_name":speaker_names.get(seg["speaker"],seg["speaker"])})

    c1,c2 = st.columns(2)
    with c1:
        if st.button("✅ APPROVE & GENERATE"):
            st.session_state.speaker_names = speaker_names
            st.session_state.transcripts   = edited
            st.session_state.stage         = "summarize"
            st.rerun()
    with c2:
        if st.button("🔄 Re-run Diarization"):
            st.session_state.stage = "diarize"; st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
# STAGE 4 — Summarization
# ══════════════════════════════════════════════════════════════════════════════
elif st.session_state.stage == "summarize":
    st.markdown(
        '<div class="step-card"><div class="step-number">Step 04 / Generating</div>'
        '<h3 style="margin:0.3rem 0">AI Summaries · Hindi · MOM · TTS · Translation</h3></div>',
        unsafe_allow_html=True
    )
    transcripts = st.session_state.transcripts
    cfg         = st.session_state.config or {}
    lang_name   = st.session_state.output_lang or "English"
    llm_code, tts_code = OUTPUT_LANGUAGES.get(lang_name, ("en","en"))

    progress = st.progress(0)
    status   = st.empty()

    full_transcript = "\n".join(
        f"[{fmt_time(t['start'])}] {t.get('display_name',t['speaker'])}: {t['text']}"
        for t in transcripts
    )
    spk_utterances = {}
    for t in transcripts:
        spk_utterances.setdefault(t.get("display_name",t["speaker"]),[]).append(t["text"])

    # ── [1] Speaker profiles (English first) ─────────────────────────────────
    status.markdown("**[1/10]** Speaker profiles (English)..."); progress.progress(10)
    speaker_summaries_en = {}; speaker_action_items = {}
    for name in spk_utterances:
        r = call_llm(
            f"Meeting analyst. Participant: {name}\n"
            f"Write 3-5 sentences about their contribution.\n"
            f"List their Action Items (bullet points or 'None').\n"
            f"State their emotional tone (1-2 words).\n\n"
            f"Format EXACTLY:\n"
            f"**Summary:** [text]\n\n"
            f"**Action Items:**\n[list or None]\n\n"
            f"**Tone:** [word]\n\n"
            f"Transcript:\n{full_transcript[:3500]}",
            cfg
        )
        if "**Summary:**" in r and "**Action Items:**" in r:
            sp   = r.split("**Action Items:**")[0].replace("**Summary:**","").strip()
            rest = r.split("**Action Items:**")[1]
            acts, tone = (rest.split("**Tone:**")+[""])[:2]
            speaker_summaries_en[name]   = f"**Summary:** {sp}\n\n**Tone:** {tone.strip()}"
            speaker_action_items[name]   = acts.strip()
        else:
            speaker_summaries_en[name]   = r
            speaker_action_items[name]   = "None identified."

    # ── [2] Overall English summary ───────────────────────────────────────────
    status.markdown("**[2/10]** Overall summary (English)..."); progress.progress(20)
    overall_en = call_llm(
        f"Analyse this meeting transcript and provide:\n"
        f"1. Executive Summary (3-4 sentences)\n"
        f"2. Key Decisions Made\n"
        f"3. Action Items (all participants)\n"
        f"4. Main Topics Discussed\n\n"
        f"Transcript:\n{full_transcript[:4500]}",
        cfg, max_tokens=1400
    )

    # ── [3] Hindi summary (ALWAYS) ────────────────────────────────────────────
    status.markdown("**[3/10]** Hindi summary (always)..."); progress.progress(30)
    hindi_summary = generate_hindi_summary(overall_en, cfg)

    # ── [4] Translate summary to selected language ────────────────────────────
    status.markdown(f"**[4/10]** Translating summary to {lang_name}..."); progress.progress(38)
    overall_translated = (
        overall_en if lang_name == "English"
        else translate_to_language(overall_en, lang_name, cfg)
    )
    # Translate speaker summaries
    speaker_summaries_translated = {}
    for name, summary in speaker_summaries_en.items():
        speaker_summaries_translated[name] = (
            summary if lang_name == "English"
            else translate_to_language(summary, lang_name, cfg)
        )

    # ── [5] Health score ──────────────────────────────────────────────────────
    status.markdown("**[5/10]** Meeting health score..."); progress.progress(46)
    health_en = call_llm(
        f"Rate this meeting on 5 criteria (each scored /20 with emoji):\n"
        f"1. ⚖️ Participation Balance\n"
        f"2. 😊 Sentiment / Positivity\n"
        f"3. 🔇 Interruption Level\n"
        f"4. ⏸ Silence / Dead Time\n"
        f"5. ⚔️ Conflict Level\n\n"
        f"Format each as:\n[Emoji] [Criteria]: [Score]/20 — [1-2 sentence explanation]\n\n"
        f"Then on a NEW LINE write exactly: OVERALL_SCORE: [total]/100\n\n"
        f"Transcript:\n{full_transcript[:4000]}",
        cfg, max_tokens=900
    )
    health_translated = (
        health_en if lang_name == "English"
        else translate_to_language(health_en, lang_name, cfg)
    )

    # ── [6] MOM ───────────────────────────────────────────────────────────────
    status.markdown("**[6/10]** Minutes of Meeting (MOM)..."); progress.progress(54)
    date_info   = st.session_state.video_date_info or {}
    rec_date    = date_info.get("creation_time") or date_info.get("modified_time") or "N/A"
    dur_secs    = date_info.get("duration_secs")
    dur_str     = fmt_time(dur_secs) if dur_secs else "N/A"
    attendees   = ", ".join(spk_utterances.keys())

    mom_en = call_llm(
        f"Generate formal Minutes of Meeting (MOM).\n\n"
        f"**MEETING DETAILS**\n"
        f"Recording Date: {rec_date}\n"
        f"Duration: {dur_str}\n"
        f"Attendees: {attendees}\n"
        f"Facilitator: [most active speaker from transcript]\n\n"
        f"**AGENDA ITEMS DISCUSSED**\n[numbered list of topics covered]\n\n"
        f"**KEY DISCUSSIONS**\n[summarize each major point with speaker attribution]\n\n"
        f"**DECISIONS MADE**\n[numbered list]\n\n"
        f"**ACTION ITEMS**\n"
        f"| # | Action Item | Assigned To | Target Date |\n"
        f"|---|-------------|-------------|-------------|\n"
        f"[fill rows from transcript]\n\n"
        f"**FOLLOW-UP ITEMS**\n[unresolved items]\n\n"
        f"**NEXT STEPS**\n[post-meeting actions]\n\n"
        f"Transcript:\n{full_transcript[:5500]}",
        cfg, max_tokens=1800
    )
    mom_translated = (
        mom_en if lang_name == "English"
        else translate_to_language(mom_en, lang_name, cfg)
    )

    # ── [7] Email ─────────────────────────────────────────────────────────────
    status.markdown("**[7/10]** Follow-up email..."); progress.progress(62)
    email_en = call_llm(
        f"Write a professional follow-up email covering:\n"
        f"- Thank you note\n- Executive summary\n"
        f"- Action items grouped by person\n- Professional closing\n\n"
        f"Transcript:\n{full_transcript[:4000]}",
        cfg, max_tokens=900
    )
    email_translated = (
        email_en if lang_name == "English"
        else translate_to_language(email_en, lang_name, cfg)
    )

    # ── [8] Title + Calendar (with video dates + transcript dates) ────────────
    status.markdown("**[8/10]** Title & calendar dates..."); progress.progress(70)
    transcript_dates = extract_dates_from_transcript(full_transcript, cfg)

    meta_r = call_llm(
        f"From this transcript:\n"
        f"1. Create a catchy Meeting Title (max 6 words)\n"
        f"Format:\n**TITLE:** [title]\n\n"
        f"Transcript:\n{full_transcript[:2000]}",
        cfg, max_tokens=200
    )
    meeting_title = "Meeting Analysis Complete"
    if "**TITLE:**" in meta_r:
        meeting_title = meta_r.split("**TITLE:**")[1].strip().split("\n")[0].strip()

    # Build calendar section combining video metadata dates + transcript dates
    calendar_parts = []
    if date_info.get("creation_time"):
        calendar_parts.append(f"📅 **Recording Date:** {date_info['creation_time']}")
    if date_info.get("modified_time") and not date_info.get("creation_time"):
        calendar_parts.append(f"📅 **File Date:** {date_info['modified_time']}")
    if dur_secs:
        calendar_parts.append(f"⏱ **Meeting Duration:** {dur_str}")
    calendar_parts.append("\n**Dates & Deadlines Mentioned in Meeting:**")
    calendar_parts.append(transcript_dates)

    calendar_text    = "\n".join(calendar_parts)
    calendar_translated = (
        calendar_text if lang_name == "English"
        else translate_to_language(calendar_text, lang_name, cfg)
    )

    # ── [9] Generate all TTS audio ────────────────────────────────────────────
    status.markdown("**[9/10]** Generating TTS audio files..."); progress.progress(78)

    # English TTS (always en)
    tts_overall_en = make_tts(overall_en, "en")

    # Hindi TTS
    tts_hindi = make_tts(hindi_summary, "hi")

    # Selected language TTS
    tts_overall_lang   = make_tts(overall_translated, tts_code)
    tts_health_lang    = make_tts(health_translated,  tts_code)
    tts_email_lang     = make_tts(email_translated,   tts_code)
    tts_mom_lang       = make_tts(mom_translated,     tts_code)
    tts_calendar_lang  = make_tts(calendar_translated, tts_code)

    # Per-speaker TTS
    speaker_tts = {}
    for name, summary in speaker_summaries_translated.items():
        p = make_tts(summary, tts_code)
        if p: speaker_tts[name] = p

    # Action items TTS
    action_tts = {}
    for name, items in speaker_action_items.items():
        items_t = (items if lang_name=="English"
                   else translate_to_language(items, lang_name, cfg))
        p = make_tts(f"Action items for {name}: {items_t}", tts_code)
        if p: action_tts[name] = p
        speaker_action_items[name] = items_t  # store translated version

    # ── [10] Finalize ─────────────────────────────────────────────────────────
    status.markdown("**[10/10]** Finalizing..."); progress.progress(95)
    time.sleep(0.2)
    progress.progress(100)

    st.session_state.summaries = {
        # Content
        "overall_en":           overall_en,
        "overall_translated":   overall_translated,
        "hindi_summary":        hindi_summary,
        "speaker_summaries":    speaker_summaries_translated,
        "speaker_action_items": speaker_action_items,
        "health_en":            health_en,
        "health_translated":    health_translated,
        "mom":                  mom_translated,
        "follow_up_email":      email_translated,
        "meeting_title":        meeting_title,
        "calendar_text":        calendar_translated,
        # TTS paths
        "tts_overall_en":       tts_overall_en,
        "tts_overall_lang":     tts_overall_lang,
        "tts_hindi":            tts_hindi,
        "tts_health_lang":      tts_health_lang,
        "tts_email_lang":       tts_email_lang,
        "tts_mom_lang":         tts_mom_lang,
        "tts_calendar_lang":    tts_calendar_lang,
        "speaker_tts":          speaker_tts,
        "action_tts":           action_tts,
        # Meta
        "lang_name":            lang_name,
        "tts_code":             tts_code,
        "date_info":            date_info,
    }
    st.session_state.stage = "output"
    st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
# STAGE 5 — Output
# ══════════════════════════════════════════════════════════════════════════════
elif st.session_state.stage == "output":
    try:
        import plotly.graph_objects as go
        PLOTLY = True
    except ImportError:
        PLOTLY = False

    transcripts = st.session_state.transcripts or []
    summaries   = st.session_state.summaries   or {}
    name_source = st.session_state.speaker_name_source or {}
    audio_path  = st.session_state.audio_path
    cfg         = st.session_state.config or {}
    date_info   = st.session_state.video_date_info or {}

    lang_name = summaries.get("lang_name","English")
    tts_code  = summaries.get("tts_code","en")
    llm_code, _ = OUTPUT_LANGUAGES.get(lang_name, ("en","en"))

    speakers     = sorted(set(t.get("display_name",t["speaker"]) for t in transcripts))
    raw_speakers = sorted(set(t["speaker"] for t in transcripts))
    total_dur    = max(t["end"] for t in transcripts) if transcripts else 0

    # Parse health score
    health_num = "N/A"
    for line in summaries.get("health_en","").split("\n"):
        if "OVERALL_SCORE:" in line:
            try:
                health_num = line.split("OVERALL_SCORE:")[1].split("/100")[0].strip()
            except Exception:
                pass
    h_emoji, h_label, h_color = get_health_emoji(health_num)

    # ── Header + metrics ──────────────────────────────────────────────────────
    st.markdown(
        f'<div class="step-card"><div class="step-number">Step 05 / Results</div>'
        f'<h3 style="margin:0.3rem 0">{summaries.get("meeting_title","Meeting Analysis")}'
        f'<span class="lang-badge">🌐 {lang_name}</span></h3>'
        f'</div>',
        unsafe_allow_html=True
    )

    m1,m2,m3,m4,m5,m6 = st.columns(6)
    for col,val,lbl,extra in [
        (m1, fmt_time(total_dur), "Duration",   ""),
        (m2, len(speakers),       "Speakers",   ""),
        (m3, len(transcripts),    "Utterances", ""),
        (m4, sum(len(t["text"].split()) for t in transcripts), "Words", ""),
        (m5, f"{h_emoji} {health_num}", "Health", f'style="border-color:{h_color}"'),
        (m6, lang_name,           "Language",   ""),
    ]:
        with col:
            st.markdown(
                f'<div class="metric-box" {extra}>'
                f'<div class="metric-val" style="font-size:1.4rem;">{val}</div>'
                f'<div class="metric-label">{lbl}</div></div>',
                unsafe_allow_html=True
            )

    # Show recording date in header if available
    if date_info.get("creation_time"):
        st.markdown(
            f'<div class="info-box" style="margin-top:0.5rem;">📅 <strong>Recording Date:</strong> '
            f'{date_info["creation_time"]}</div>',
            unsafe_allow_html=True
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Tabs ──────────────────────────────────────────────────────────────────
    tabs = st.tabs([
        "📝 Transcript","📊 Analytics","❤️ Health","👤 Profiles",
        "✅ Actions","📋 Summary","🇮🇳 Hindi","📋 MOM",
        "📅 Calendar","📧 Email","💬 Chat"
    ])

    # ═════════════════════════════════════════════════════
    # TAB 0 — Transcript + Audio
    # ═════════════════════════════════════════════════════
    with tabs[0]:
        st.markdown("### 📝 Meeting Transcript")

        # JS bridge for master audio seek
        st.markdown("""<img src="x" onerror="
            window.parent.jumpToAudio=function(s){
                var a=window.parent.document.querySelector('audio');
                if(a){a.currentTime=s;a.play();}
            };
            function attachPause(){
                var a=window.parent.document.querySelector('audio');
                if(a&&!a._pl){
                    a._pl=true;
                    a.addEventListener('pause',function(){
                        var t=Math.floor(a.currentTime);
                        if(t>1){
                            var inp=window.parent.document.getElementById('pause_ts_input');
                            if(inp){
                                var setter=Object.getOwnPropertyDescriptor(
                                    window.parent.HTMLInputElement.prototype,'value').set;
                                setter.call(inp,String(t));
                                inp.dispatchEvent(new Event('input',{bubbles:true}));
                            }
                        }
                    });
                }
            }
            var iv=setInterval(function(){
                attachPause();
                if(window.parent.document.querySelector('audio'))clearInterval(iv);
            },500);
        " style="display:none;">""", unsafe_allow_html=True)

        pause_ts_str = st.text_input("","",key="pause_ts_input",label_visibility="collapsed")

        if audio_path and os.path.exists(audio_path):
            st.audio(audio_path, format="audio/wav")
            st.markdown(
                '<div class="info-box">💡 <strong>Pause audio</strong> → auto-summary at that moment '
                '· <strong>Click block</strong> → seek master player '
                '· <strong>🎵 Load Clip</strong> → inline per-segment audio</div>',
                unsafe_allow_html=True
            )

        # Pause-at-timestamp
        if pause_ts_str and pause_ts_str.strip().isdigit():
            pt = int(pause_ts_str.strip())
            if st.session_state.pause_timestamp != pt:
                st.session_state.pause_timestamp = pt
                st.session_state.pause_summary   = None
                relevant = [t for t in transcripts if t["start"] <= pt]
                if relevant:
                    partial = "\n".join(
                        f"[{fmt_time(t['start'])}] {t.get('display_name',t['speaker'])}: {t['text']}"
                        for t in relevant
                    )
                    prompt = (
                        f"Expert meeting analyst. User paused at {fmt_time(pt)}.\n"
                        f"Provide:\n1. Quick Summary (2-3 sentences)\n"
                        f"2. Key Points So Far (3-5 bullets)\n"
                        f"3. Most Active Speaker and focus\n"
                        f"4. Pending / Unresolved Items\n\n"
                        f"Transcript up to pause:\n{partial[:4000]}"
                    )
                    result_en = call_llm(prompt, cfg)
                    ts_summary = (result_en if lang_name=="English"
                                  else translate_to_language(result_en, lang_name, cfg))
                    st.session_state.pause_summary = ts_summary

        if st.session_state.pause_timestamp and st.session_state.pause_summary:
            ts_txt = st.session_state.pause_summary
            st.markdown(
                f'<div class="timestamp-summary-box">'
                f'<div style="font-family:JetBrains Mono,monospace;font-size:1rem;'
                f'color:#f59e0b;font-weight:700;margin-bottom:0.6rem;">'
                f'⏸ {fmt_time(st.session_state.pause_timestamp)} — Summary ({lang_name})</div>'
                f'<p style="color:#e2e8f0;line-height:1.8;white-space:pre-wrap;">{ts_txt}</p></div>',
                unsafe_allow_html=True
            )
            play_tts_section(ts_txt, tts_code, f"Listen to timestamp summary ({lang_name})")

        st.markdown("---")
        mc1,mc2 = st.columns([2,1])
        with mc1:
            manual_ts = st.number_input("Manual timestamp (seconds)", 0,
                                         int(total_dur) if total_dur else 3600, 0, 5)
        with mc2:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("📋 Summary at Timestamp"):
                if manual_ts > 0:
                    st.session_state.pause_timestamp = manual_ts
                    relevant = [t for t in transcripts if t["start"] <= manual_ts]
                    if relevant:
                        partial = "\n".join(
                            f"[{fmt_time(t['start'])}] {t.get('display_name',t['speaker'])}: {t['text']}"
                            for t in relevant
                        )
                        r_en = call_llm(
                            f"Summarise meeting up to {fmt_time(manual_ts)} with key points, "
                            f"active speakers, pending items.\n\nTranscript:\n{partial[:4000]}", cfg
                        )
                        st.session_state.pause_summary = (
                            r_en if lang_name=="English"
                            else translate_to_language(r_en, lang_name, cfg)
                        )
                    st.rerun()

        st.markdown("---")
        txt_dl = "\n".join(
            f"[{fmt_time(t['start'])}] {t.get('display_name',t['speaker'])}: {t['text']}"
            for t in transcripts
        )
        st.download_button("📥 Download Transcript", txt_dl,
                           file_name="transcript.txt", mime="text/plain")
        st.markdown("---")

        sel_spk = st.multiselect("Filter speakers:", speakers, default=speakers)
        _, c_btn = st.columns([4,1])
        with c_btn:
            if st.button("🗑 Clear Clip Cache"):
                st.session_state.seg_audio_cache = {}
                st.rerun()

        for si, t in enumerate(transcripts):
            name = t.get("display_name", t["speaker"])
            if name not in sel_spk: continue
            orig  = t.get("original_speaker", t["speaker"])
            idx   = raw_speakers.index(orig) if orig in raw_speakers else 0
            color,_ = get_speaker_color(idx)
            st_t, en_t = t["start"], t["end"]
            is_before = (st.session_state.pause_timestamp is not None
                         and en_t <= st.session_state.pause_timestamp)
            op = "1" if (is_before or st.session_state.pause_timestamp is None) else "0.35"
            bs = (f"5px solid {color}"
                  if (is_before or st.session_state.pause_timestamp is None)
                  else f"3px solid {color}44")
            src_tag = (
                ' <span style="font-size:0.58rem;background:#10b98120;color:#10b981;'
                'border:1px solid #10b98150;border-radius:8px;padding:1px 6px;">✓ auto</span>'
                if name_source.get(orig,"manual")=="auto" else ""
            )

            st.markdown(
                f'''<div style="display:flex;gap:14px;padding:14px;margin-bottom:3px;
                    border-radius:12px 12px 0 0;cursor:pointer;background:#131929;
                    border:1px solid #1e2d47;border-left:{bs};opacity:{op};transition:background 0.15s;"
                    onclick="window.parent.jumpToAudio({st_t})"
                    onmouseover="this.style.background='#1a2540'"
                    onmouseout="this.style.background='#131929'">
                  <div style="min-width:65px;color:#64748b;font-family:'JetBrains Mono',monospace;
                       font-size:0.75rem;">{fmt_time(st_t)}<br>
                    <span style="opacity:0.5;font-size:0.65rem;">→{fmt_time(en_t)}</span></div>
                  <div style="flex-grow:1;">
                    <div style="color:{color};font-weight:700;font-size:0.72rem;
                         text-transform:uppercase;margin-bottom:4px;">{name}{src_tag}</div>
                    <div style="color:#e2e8f0;font-size:0.93rem;line-height:1.6;">{t["text"]}</div>
                  </div>
                  <div style="color:#00e5ff;opacity:0.35;font-size:0.9rem;align-self:center;">▶</div>
                </div>''',
                unsafe_allow_html=True
            )

            ck = str(si)
            if ck in st.session_state.seg_audio_cache:
                b64 = st.session_state.seg_audio_cache[ck]
                st.markdown(
                    f'<div style="background:#0d1220;border:1px solid #1e2d47;border-top:none;'
                    f'border-radius:0 0 12px 12px;padding:6px 14px 10px;margin-bottom:10px;">'
                    f'<div class="audio-badge" style="color:{color};">🎵 SEGMENT AUDIO</div>'
                    f'<audio controls preload="auto" style="width:100%;height:32px;">'
                    f'<source src="data:audio/wav;base64,{b64}" type="audio/wav"></audio></div>',
                    unsafe_allow_html=True
                )
            else:
                bc, _ = st.columns([1,5])
                with bc:
                    if audio_path and os.path.exists(audio_path):
                        if st.button("🎵 Load Clip", key=f"lc_{si}"):
                            with st.spinner("Extracting clip..."):
                                clip = extract_audio_clip(audio_path, st_t, en_t)
                                if clip:
                                    st.session_state.seg_audio_cache[ck] = audio_bytes_to_b64(clip)
                                    st.rerun()
                                else:
                                    st.warning("Clip extraction failed.")

    # ═════════════════════════════════════════════════════
    # TAB 1 — Analytics
    # ═════════════════════════════════════════════════════
    with tabs[1]:
        st.markdown("### 📊 Meeting Analytics")
        if not PLOTLY:
            st.warning("Install plotly: `pip install plotly`")
        else:
            spk_time  = {}
            spk_words = {}
            turn_cnt  = {}
            for t in transcripts:
                n = t.get("display_name", t["speaker"])
                spk_time[n]  = spk_time.get(n,0)  + (t["end"]-t["start"])
                spk_words[n] = spk_words.get(n,0) + len(t["text"].split())
                turn_cnt[n]  = turn_cnt.get(n,0)  + 1

            c1,c2 = st.columns(2)
            with c1:
                fig = go.Figure(go.Pie(
                    labels=list(spk_time.keys()),
                    values=[round(v,1) for v in spk_time.values()],
                    hole=0.55,
                    marker=dict(
                        colors=[get_speaker_color(i)[0] for i in range(len(spk_time))],
                        line=dict(color="#070b14",width=2)
                    ),
                    textfont=dict(family="JetBrains Mono",size=11),
                ))
                fig.update_layout(
                    title=dict(text="🎙 Talk Time",font=dict(color="#e2e8f0",size=15,family="JetBrains Mono")),
                    paper_bgcolor="#131929",plot_bgcolor="#131929",
                    font=dict(color="#e2e8f0"),legend=dict(font=dict(color="#e2e8f0")),
                    margin=dict(t=50,b=20,l=20,r=20)
                )
                st.plotly_chart(fig, use_container_width=True)
            with c2:
                fig = go.Figure(go.Bar(
                    x=list(spk_words.keys()), y=list(spk_words.values()),
                    marker_color=[get_speaker_color(i)[0] for i in range(len(spk_words))],
                    text=list(spk_words.values()), textposition="outside",
                    textfont=dict(family="JetBrains Mono",color="#e2e8f0",size=10)
                ))
                fig.update_layout(
                    title=dict(text="📝 Word Count",font=dict(color="#e2e8f0",size=15,family="JetBrains Mono")),
                    paper_bgcolor="#131929",plot_bgcolor="#131929",font=dict(color="#e2e8f0"),
                    xaxis=dict(color="#e2e8f0",gridcolor="#1e2d47"),
                    yaxis=dict(color="#e2e8f0",gridcolor="#1e2d47"),
                    margin=dict(t=50,b=20,l=20,r=20)
                )
                st.plotly_chart(fig, use_container_width=True)

            # Gantt timeline
            st.markdown("#### 🕐 Speaking Timeline")
            spk_color_map = {
                t.get("display_name",t["speaker"]): get_speaker_color(
                    raw_speakers.index(t.get("original_speaker",t["speaker"]))
                    if t.get("original_speaker",t["speaker"]) in raw_speakers else 0
                )[0]
                for t in transcripts
            }
            fig_g = go.Figure()
            shown = set()
            for t in transcripts[:100]:
                n   = t.get("display_name",t["speaker"])
                clr = spk_color_map.get(n,"#00e5ff")
                sl  = n not in shown; shown.add(n)
                fig_g.add_trace(go.Bar(
                    x=[t["end"]-t["start"]], y=[n], base=[t["start"]],
                    orientation="h", name=n, showlegend=sl,
                    marker_color=clr,
                    hovertemplate=f"<b>{n}</b><br>{fmt_time(t['start'])}→{fmt_time(t['end'])}<extra></extra>"
                ))
            fig_g.update_layout(
                barmode="overlay",
                title=dict(text="Speaking Timeline",font=dict(color="#e2e8f0",size=14,family="JetBrains Mono")),
                paper_bgcolor="#131929",plot_bgcolor="#131929",font=dict(color="#e2e8f0"),
                xaxis=dict(title="Seconds",color="#e2e8f0",gridcolor="#1e2d47"),
                yaxis=dict(color="#e2e8f0",gridcolor="#1e2d47"),
                legend=dict(font=dict(color="#e2e8f0")),
                height=max(280, len(speakers)*60),
                margin=dict(t=50,b=40,l=20,r=20)
            )
            st.plotly_chart(fig_g, use_container_width=True)

            c3,c4 = st.columns(2)
            with c3:
                durs = [round(t["end"]-t["start"],1) for t in transcripts]
                fig = go.Figure(go.Histogram(
                    x=durs, nbinsx=20, marker_color="#8b5cf6", opacity=0.85,
                    hovertemplate="Duration: %{x}s<br>Count: %{y}<extra></extra>"
                ))
                fig.update_layout(
                    title=dict(text="⏱ Utterance Duration",font=dict(color="#e2e8f0",size=14,family="JetBrains Mono")),
                    paper_bgcolor="#131929",plot_bgcolor="#131929",font=dict(color="#e2e8f0"),
                    xaxis=dict(title="Seconds",color="#e2e8f0",gridcolor="#1e2d47"),
                    yaxis=dict(title="Count",color="#e2e8f0",gridcolor="#1e2d47"),
                    margin=dict(t=50,b=40,l=20,r=20)
                )
                st.plotly_chart(fig, use_container_width=True)
            with c4:
                fig = go.Figure(go.Bar(
                    x=list(turn_cnt.keys()), y=list(turn_cnt.values()),
                    marker_color=[get_speaker_color(i)[0] for i in range(len(turn_cnt))],
                    text=list(turn_cnt.values()), textposition="outside",
                    textfont=dict(family="JetBrains Mono",color="#e2e8f0",size=10)
                ))
                fig.update_layout(
                    title=dict(text="🔄 Turn Count",font=dict(color="#e2e8f0",size=14,family="JetBrains Mono")),
                    paper_bgcolor="#131929",plot_bgcolor="#131929",font=dict(color="#e2e8f0"),
                    xaxis=dict(color="#e2e8f0",gridcolor="#1e2d47"),
                    yaxis=dict(color="#e2e8f0",gridcolor="#1e2d47"),
                    margin=dict(t=50,b=40,l=20,r=20)
                )
                st.plotly_chart(fig, use_container_width=True)

            if len(speakers) >= 3:
                st.markdown("#### 🕸 Participation Radar")
                spk_list  = list(spk_time.keys())
                def norm(v): mx=max(v) if max(v)>0 else 1; return [x/mx*100 for x in v]
                tv = [spk_time.get(s,0) for s in spk_list]
                wv = [spk_words.get(s,0) for s in spk_list]
                cv = [turn_cnt.get(s,0) for s in spk_list]
                fig = go.Figure()
                for i, spk in enumerate(spk_list):
                    fig.add_trace(go.Scatterpolar(
                        r=[norm(tv)[i],norm(wv)[i],norm(cv)[i],norm(tv)[i]],
                        theta=["Talk Time","Word Count","Turn Count","Talk Time"],
                        fill="toself", name=spk,
                        line_color=get_speaker_color(i)[0], opacity=0.7
                    ))
                fig.update_layout(
                    polar=dict(bgcolor="#131929",
                               radialaxis=dict(visible=True,color="#64748b",gridcolor="#1e2d47"),
                               angularaxis=dict(color="#e2e8f0")),
                    paper_bgcolor="#131929",font=dict(color="#e2e8f0"),
                    legend=dict(font=dict(color="#e2e8f0")),
                    title=dict(text="Participation Radar (normalised)",
                               font=dict(color="#e2e8f0",size=14,family="JetBrains Mono")),
                    margin=dict(t=60,b=40)
                )
                st.plotly_chart(fig, use_container_width=True)

    # ═════════════════════════════════════════════════════
    # TAB 2 — Health
    # ═════════════════════════════════════════════════════
    with tabs[2]:
        st.markdown(
            f'### ❤️ Meeting Health <span class="lang-badge">🌐 {lang_name}</span>',
            unsafe_allow_html=True
        )
        st.markdown(
            f'<div class="health-ring-wrap">'
            f'<div class="health-emoji">{h_emoji}</div>'
            f'<div class="health-score-num" style="color:{h_color};">{health_num}</div>'
            f'<div class="health-label">/ 100 · {h_label}</div></div>',
            unsafe_allow_html=True
        )
        if PLOTLY:
            try:
                fig = go.Figure(go.Indicator(
                    mode="gauge+number", value=int(health_num),
                    domain={"x":[0,1],"y":[0,1]},
                    gauge={
                        "axis":{"range":[0,100],"tickcolor":"#64748b",
                                "tickfont":{"color":"#e2e8f0","family":"JetBrains Mono"}},
                        "bar":{"color":h_color,"thickness":0.25},
                        "bgcolor":"#131929","bordercolor":"#1e2d47",
                        "steps":[{"range":[0,30],"color":"#1e0a0a"},
                                  {"range":[30,60],"color":"#1e1400"},
                                  {"range":[60,100],"color":"#0a1e14"}],
                        "threshold":{"line":{"color":h_color,"width":4},
                                     "thickness":0.75,"value":int(health_num)}
                    },
                    number={"font":{"color":h_color,"size":48,"family":"JetBrains Mono"},"suffix":"/100"}
                ))
                fig.update_layout(paper_bgcolor="#131929",font=dict(color="#e2e8f0"),
                                   height=280, margin=dict(t=30,b=30,l=30,r=30))
                st.plotly_chart(fig, use_container_width=True)
            except Exception:
                pass

        tts_h = summaries.get("tts_health_lang")
        if tts_h and os.path.exists(tts_h):
            st.markdown(f"🔊 **Listen — Health Analysis ({lang_name}):**")
            st.audio(tts_h, format="audio/mp3")
        else:
            # Regenerate on the fly if missing
            path = make_tts(summaries.get("health_translated",""), tts_code)
            if path:
                st.markdown(f"🔊 **Listen — Health Analysis ({lang_name}):**")
                st.audio(path, format="audio/mp3")

        st.markdown(
            f'<div class="summary-box"><p style="line-height:1.95;color:#e2e8f0;white-space:pre-wrap;">'
            f'{summaries.get("health_translated","Not generated.")}</p></div>',
            unsafe_allow_html=True
        )

    # ═════════════════════════════════════════════════════
    # TAB 3 — Speaker Profiles
    # ═════════════════════════════════════════════════════
    with tabs[3]:
        st.markdown(
            f'### 👤 Speaker Profiles <span class="lang-badge">🌐 {lang_name}</span>',
            unsafe_allow_html=True
        )
        speaker_tts = summaries.get("speaker_tts",{})
        for i,(name,summary) in enumerate(summaries.get("speaker_summaries",{}).items()):
            color,_ = get_speaker_color(i)
            st.markdown(
                f'<span class="speaker-chip" style="background:{color}22;color:{color};'
                f'border:1px solid {color}55;font-size:0.9rem;">{name}</span>',
                unsafe_allow_html=True
            )
            p = speaker_tts.get(name)
            if p and os.path.exists(p):
                st.markdown(f"🔊 **Listen — {name}'s profile ({lang_name}):**")
                st.audio(p, format="audio/mp3")
            else:
                # Regenerate
                rp = make_tts(summary, tts_code)
                if rp:
                    st.markdown(f"🔊 **Listen — {name}'s profile ({lang_name}):**")
                    st.audio(rp, format="audio/mp3")
            st.markdown(summary)
            st.markdown("---")

    # ═════════════════════════════════════════════════════
    # TAB 4 — Action Items
    # ═════════════════════════════════════════════════════
    with tabs[4]:
        st.markdown(
            f'### ✅ Action Items <span class="lang-badge">🌐 {lang_name}</span>',
            unsafe_allow_html=True
        )
        action_tts = summaries.get("action_tts",{})
        for i,(name,items) in enumerate(summaries.get("speaker_action_items",{}).items()):
            color,_ = get_speaker_color(i)
            st.markdown(
                f'<div class="summary-box">'
                f'<span class="speaker-chip" style="background:{color}22;color:{color};'
                f'border:1px solid {color}55;font-size:0.9rem;">{name}</span>'
                f'<p style="margin-top:0.8rem;line-height:1.75;color:#e2e8f0;">{items}</p></div>',
                unsafe_allow_html=True
            )
            p = action_tts.get(name)
            if p and os.path.exists(p):
                st.audio(p, format="audio/mp3")
            else:
                rp = make_tts(f"Actions for {name}: {items}", tts_code)
                if rp: st.audio(rp, format="audio/mp3")

    # ═════════════════════════════════════════════════════
    # TAB 5 — Summary (selected language)
    # ═════════════════════════════════════════════════════
    with tabs[5]:
        st.markdown(
            f'### 📋 Meeting Summary <span class="lang-badge">🌐 {lang_name}</span>',
            unsafe_allow_html=True
        )

        # ── Audio players — FIXED: always attempt to play ────────────────────
        tts_lang_path = summaries.get("tts_overall_lang")
        tts_en_path   = summaries.get("tts_overall_en")

        if tts_lang_path and os.path.exists(tts_lang_path) and os.path.getsize(tts_lang_path) > 500:
            st.markdown(f"🔊 **Listen — Summary in {lang_name}:**")
            st.audio(tts_lang_path, format="audio/mp3")
        else:
            # Regenerate on the fly
            regen = make_tts(summaries.get("overall_translated",""), tts_code)
            if regen:
                st.markdown(f"🔊 **Listen — Summary in {lang_name}:**")
                st.audio(regen, format="audio/mp3")

        if lang_name != "English":
            if tts_en_path and os.path.exists(tts_en_path) and os.path.getsize(tts_en_path) > 500:
                st.markdown("🔊 **Listen — Original English:**")
                st.audio(tts_en_path, format="audio/mp3")
            else:
                regen_en = make_tts(summaries.get("overall_en",""), "en")
                if regen_en:
                    st.markdown("🔊 **Listen — Original English:**")
                    st.audio(regen_en, format="audio/mp3")

        st.markdown(
            f'<div class="summary-box"><p style="line-height:1.95;color:#e2e8f0;white-space:pre-wrap;">'
            f'{summaries.get("overall_translated","Not generated")}</p></div>',
            unsafe_allow_html=True
        )

        if lang_name != "English":
            with st.expander("📖 Original English"):
                st.markdown(
                    f'<div class="summary-box"><p style="line-height:1.9;color:#e2e8f0;white-space:pre-wrap;">'
                    f'{summaries.get("overall_en","")}</p></div>',
                    unsafe_allow_html=True
                )

    # ═════════════════════════════════════════════════════
    # TAB 6 — Hindi Summary (ALWAYS)
    # ═════════════════════════════════════════════════════
    with tabs[6]:
        st.markdown(
            '### 🇮🇳 Hindi / Hinglish Summary <span class="lang-badge">हिंदी · Hinglish</span>',
            unsafe_allow_html=True
        )
        hindi_text = summaries.get("hindi_summary","")

        # Hindi TTS audio
        tts_hindi_path = summaries.get("tts_hindi")
        if tts_hindi_path and os.path.exists(tts_hindi_path) and os.path.getsize(tts_hindi_path) > 500:
            st.markdown("🔊 **सुनें (Listen in Hindi):**")
            st.audio(tts_hindi_path, format="audio/mp3")
        else:
            regen_hi = make_tts(hindi_text, "hi")
            if regen_hi:
                st.markdown("🔊 **सुनें (Listen in Hindi):**")
                st.audio(regen_hi, format="audio/mp3")

        st.markdown(
            f'<div class="hindi-box">'
            f'<p style="line-height:2;color:#e2e8f0;white-space:pre-wrap;">{hindi_text}</p></div>',
            unsafe_allow_html=True
        )
        st.download_button("📥 Download Hindi Summary", hindi_text,
                           file_name="hindi_summary.txt", mime="text/plain")

    # ═════════════════════════════════════════════════════
    # TAB 7 — MOM
    # ═════════════════════════════════════════════════════
    with tabs[7]:
        st.markdown(
            f'### 📋 Minutes of Meeting (MOM) <span class="lang-badge">🌐 {lang_name}</span>',
            unsafe_allow_html=True
        )
        mom_text = summaries.get("mom","Not generated.")

        tts_mom_path = summaries.get("tts_mom_lang")
        if tts_mom_path and os.path.exists(tts_mom_path) and os.path.getsize(tts_mom_path) > 500:
            st.markdown(f"🔊 **Listen — MOM ({lang_name}):**")
            st.audio(tts_mom_path, format="audio/mp3")
        else:
            regen_m = make_tts(mom_text, tts_code)
            if regen_m:
                st.markdown(f"🔊 **Listen — MOM ({lang_name}):**")
                st.audio(regen_m, format="audio/mp3")

        st.markdown(
            f'<div class="summary-box" style="border-color:rgba(139,92,246,0.35);'
            f'background:linear-gradient(135deg,rgba(139,92,246,0.05),rgba(0,229,255,0.03));">'
            f'<p style="line-height:1.95;color:#e2e8f0;white-space:pre-wrap;">{mom_text}</p></div>',
            unsafe_allow_html=True
        )
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M")
        col_d1, col_d2 = st.columns(2)
        with col_d1:
            st.download_button("📥 Download MOM (.txt)", mom_text,
                               file_name="minutes_of_meeting.txt", mime="text/plain")
        with col_d2:
            md_mom = f"# Minutes of Meeting\n_Generated: {now_str} | Language: {lang_name}_\n\n{mom_text}"
            st.download_button("📥 Download MOM (.md)", md_mom,
                               file_name="minutes_of_meeting.md", mime="text/markdown")

    # ═════════════════════════════════════════════════════
    # TAB 8 — Calendar
    # ═════════════════════════════════════════════════════
    with tabs[8]:
        st.markdown(
            f'### 📅 Calendar & Dates <span class="lang-badge">🌐 {lang_name}</span>',
            unsafe_allow_html=True
        )
        cal_text = summaries.get("calendar_text","No dates found.")

        tts_cal_path = summaries.get("tts_calendar_lang")
        if tts_cal_path and os.path.exists(tts_cal_path) and os.path.getsize(tts_cal_path) > 500:
            st.markdown(f"🔊 **Listen — Calendar ({lang_name}):**")
            st.audio(tts_cal_path, format="audio/mp3")
        else:
            regen_c = make_tts(cal_text, tts_code)
            if regen_c:
                st.markdown(f"🔊 **Listen — Calendar ({lang_name}):**")
                st.audio(regen_c, format="audio/mp3")

        st.markdown(
            f'<div class="summary-box" style="border-color:rgba(139,92,246,0.3);">'
            f'<p style="line-height:1.9;color:#e2e8f0;white-space:pre-wrap;">{cal_text}</p></div>',
            unsafe_allow_html=True
        )

    # ═════════════════════════════════════════════════════
    # TAB 9 — Email
    # ═════════════════════════════════════════════════════
    with tabs[9]:
        st.markdown(
            f'### 📧 Follow-up Email <span class="lang-badge">🌐 {lang_name}</span>',
            unsafe_allow_html=True
        )
        email_text = summaries.get("follow_up_email","Not generated")

        tts_em_path = summaries.get("tts_email_lang")
        if tts_em_path and os.path.exists(tts_em_path) and os.path.getsize(tts_em_path) > 500:
            st.markdown(f"🔊 **Listen — Email ({lang_name}):**")
            st.audio(tts_em_path, format="audio/mp3")
        else:
            regen_e = make_tts(email_text, tts_code)
            if regen_e:
                st.markdown(f"🔊 **Listen — Email ({lang_name}):**")
                st.audio(regen_e, format="audio/mp3")

        st.text_area("Copy and send:", value=email_text, height=350)
        recipients = st.text_input("Recipient emails:", "team@example.com")
        import urllib.parse
        ml = (f"mailto:{recipients}?subject=Meeting+Follow-up"
              f"&body={urllib.parse.quote(email_text)}")
        st.markdown(
            f'<a href="{ml}" target="_blank">'
            f'<button style="background:linear-gradient(135deg,#10b981,#00e5ff);color:#070b14;'
            f'border:none;border-radius:10px;font-family:JetBrains Mono,monospace;'
            f'font-size:0.85rem;padding:0.65rem 1.5rem;font-weight:700;cursor:pointer;">'
            f'✉️ Open Email Client</button></a>',
            unsafe_allow_html=True
        )

    # ═════════════════════════════════════════════════════
    # TAB 10 — Chat
    # ═════════════════════════════════════════════════════
    with tabs[10]:
        st.markdown(
            f'### 💬 Chat with Meeting AI <span class="lang-badge">🌐 {lang_name}</span>',
            unsafe_allow_html=True
        )
        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []

        for msg in st.session_state.chat_history:
            icon = "👤" if msg["role"]=="user" else "🤖"
            st.markdown(f"**{icon} {msg['role'].capitalize()}**: {msg['content']}")
            if msg["role"] == "assistant":
                p = make_tts(msg["content"], tts_code)
                if p: st.audio(p, format="audio/mp3")

        query = st.chat_input(f"Ask about the meeting (reply in {lang_name})...")
        if query:
            st.session_state.chat_history.append({"role":"user","content":query})
            with st.spinner("Thinking..."):
                ft = "\n".join(
                    f"[{fmt_time(t['start'])}] {t.get('display_name',t['speaker'])}: {t['text']}"
                    for t in transcripts
                )
                answer_en = call_llm(
                    f"You are a meeting assistant. Answer ONLY from the transcript.\n\n"
                    f"Transcript:\n{ft[:6000]}\n\nQuestion: {query}\nAnswer:",
                    cfg, 800
                )
                answer = (answer_en if lang_name=="English"
                          else translate_to_language(answer_en, lang_name, cfg))
                st.session_state.chat_history.append({"role":"assistant","content":answer})
            st.rerun()

    # ── Export footer ──────────────────────────────────────────────────────────
    st.markdown("---")
    e1,e2,e3,e4,e5 = st.columns(5)
    with e1:
        export = {
            "generated_at": datetime.now().isoformat(),
            "language":     lang_name,
            "speakers":     speakers,
            "transcript":   transcripts,
            "date_info":    {k:v for k,v in (st.session_state.video_date_info or {}).items()
                             if k != "raw_tags"},
            "summaries":    {k:v for k,v in summaries.items() if not k.startswith("tts_")},
        }
        st.download_button("⬇️ JSON",
            data=json.dumps(export,indent=2,ensure_ascii=False),
            file_name="meeting_analysis.json", mime="application/json")
    with e2:
        lines = [f"MEETING ANALYSIS — {lang_name}","="*50,"","TRANSCRIPT","─"*30]
        for t in transcripts:
            lines.append(f"[{fmt_time(t['start'])}] {t.get('display_name',t['speaker'])}: {t['text']}")
        lines += ["","SUMMARY","─"*30, summaries.get("overall_translated","")]
        lines += ["","HINDI SUMMARY","─"*30, summaries.get("hindi_summary","")]
        lines += ["","MINUTES OF MEETING","─"*30, summaries.get("mom","")]
        st.download_button("⬇️ Full Report",
            "\n".join(lines), file_name="meeting_report.txt", mime="text/plain")
    with e3:
        st.download_button("⬇️ MOM",
            summaries.get("mom",""), file_name="mom.txt", mime="text/plain")
    with e4:
        st.download_button("⬇️ Hindi",
            summaries.get("hindi_summary",""), file_name="hindi_summary.txt", mime="text/plain")
    with e5:
        if st.button("🔁 New Analysis"):
            for k in KEYS: st.session_state[k] = None
            if "chat_history" in st.session_state: del st.session_state["chat_history"]
            st.session_state.stage = "upload"
            st.rerun()
