import html
import re
from pathlib import Path
from typing import Dict, List, Tuple

import pandas as pd
import streamlit as st

DATA_DIR = Path(__file__).parent / "data"

st.set_page_config(
    page_title="ScamAlert Selangor",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# -----------------------------------------------------------------------------
# Clean light UI
# -----------------------------------------------------------------------------
st.markdown(
    """
    <style>
    [data-testid="stSidebar"] {display: none;}
    [data-testid="collapsedControl"] {display: none;}
    .block-container {padding-top: 2rem; padding-bottom: 2.2rem; max-width: 1120px;}
    body {background: #F8F7F4;}
    .main .block-container {background: #F8F7F4;}
    .hero {
        background: #FFFFFF;
        border: 1px solid #E5E7EB;
        border-radius: 26px;
        padding: 34px 38px;
        box-shadow: 0 18px 42px rgba(17, 24, 39, 0.06);
        margin-bottom: 22px;
        position: relative;
        overflow: hidden;
    }
    .hero:before {
        content: "";
        position: absolute;
        left: 0; top: 0; bottom: 0;
        width: 8px;
        background: #B91C1C;
    }
    .hero h1 {
        color: #111827;
        font-size: 3.05rem;
        line-height: 1.05;
        margin: 0 0 13px 0;
        font-weight: 900;
        letter-spacing: -0.04em;
    }
    .hero p {
        color: #374151;
        font-size: 1.08rem;
        line-height: 1.62;
        max-width: 900px;
        margin: 0;
    }
    .section-card {
        background: #FFFFFF;
        border: 1px solid #E5E7EB;
        border-radius: 22px;
        padding: 24px;
        margin-bottom: 20px;
        box-shadow: 0 14px 34px rgba(17, 24, 39, 0.055);
    }
    .result-card {
        background: #FFFFFF;
        border: 1px solid #E5E7EB;
        border-radius: 22px;
        padding: 22px;
        min-height: 150px;
        box-shadow: 0 12px 28px rgba(17, 24, 39, 0.045);
    }
    .result-card-accent {
        background: #FFF7ED;
        border: 1px solid #FED7AA;
        border-radius: 22px;
        padding: 22px;
        min-height: 150px;
        box-shadow: 0 12px 28px rgba(17, 24, 39, 0.045);
    }
    .mini-label {
        color: #6B7280;
        font-size: 0.78rem;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        font-weight: 900;
        margin-bottom: 7px;
    }
    .big-value {
        color: #111827;
        font-size: 2.35rem;
        font-weight: 900;
        line-height: 1;
        margin-bottom: 8px;
    }
    .medium-value {
        color: #111827;
        font-size: 1.2rem;
        font-weight: 850;
        line-height: 1.35;
    }
    .muted {
        color: #6B7280;
        line-height: 1.55;
        font-size: 0.96rem;
    }
    .risk-pill {
        display: inline-block;
        padding: 9px 14px;
        border-radius: 999px;
        color: white;
        font-weight: 900;
        font-size: 0.98rem;
    }
    .risk-low {background: #15803D;}
    .risk-mid {background: #CA8A04;}
    .risk-high {background: #DC2626;}
    .risk-very {background: #7F1D1D;}
    .pill {
        display: inline-block;
        padding: 7px 12px;
        margin: 4px 6px 4px 0;
        border-radius: 999px;
        background: #FEF3C7;
        color: #78350F;
        font-weight: 800;
        font-size: 0.9rem;
        border: 1px solid #FDE68A;
    }
    .pill-red {
        display: inline-block;
        padding: 7px 12px;
        margin: 4px 6px 4px 0;
        border-radius: 999px;
        background: #FEE2E2;
        color: #7F1D1D;
        font-weight: 800;
        font-size: 0.9rem;
        border: 1px solid #FECACA;
    }
    .text-box {
        font-size: 1.02rem;
        line-height: 1.85;
        background: #FAFAFA;
        border: 1px solid #E5E7EB;
        border-radius: 16px;
        padding: 17px;
        color: #111827;
    }
    mark {
        background: #FACC15;
        color: #111827;
        border-radius: 6px;
        padding: 2px 5px;
        font-weight: 900;
    }
    .action-box {
        border-left: 5px solid #B91C1C;
        padding: 16px 18px;
        background: #FFF7ED;
        border-radius: 15px;
        color: #111827;
        font-weight: 800;
        line-height: 1.55;
    }
    .small-note {
        color: #6B7280;
        font-size: 0.9rem;
        line-height: 1.55;
    }
    div.stButton > button:first-child {
        background: #B91C1C;
        color: #FFFFFF;
        border: none;
        border-radius: 14px;
        padding: 0.8rem 1.35rem;
        font-weight: 900;
        min-width: 180px;
    }
    div.stButton > button:first-child:hover {
        background: #991B1B;
        color: #FFFFFF;
        border: none;
    }
    textarea {
        background-color: #FFFFFF !important;
        color: #111827 !important;
        border: 1px solid #D1D5DB !important;
        border-radius: 16px !important;
    }
    .stTextArea label, .stTextInput label {color: #111827 !important; font-weight: 800 !important;}
    h2, h3 {color: #111827 !important; letter-spacing: -0.02em;}
    </style>
    """,
    unsafe_allow_html=True,
)

# -----------------------------------------------------------------------------
# Data loading
# -----------------------------------------------------------------------------
@st.cache_data(show_spinner=False)
def load_dataset(filename: str) -> Tuple[pd.DataFrame, pd.DataFrame]:
    path = DATA_DIR / filename
    try:
        fraud = pd.read_excel(path, sheet_name="DATASET_UTAMA")
        control = pd.read_excel(path, sheet_name="DATASET_KAWALAN_1500")
        return fraud.fillna(""), control.fillna("")
    except Exception:
        return pd.DataFrame(), pd.DataFrame()

speech_fraud, speech_control = load_dataset("scamspeech_dataset.xlsx")
emotion_fraud, emotion_control = load_dataset("scamemotion_dataset.xlsx")

# -----------------------------------------------------------------------------
# Analysis helpers
# -----------------------------------------------------------------------------
def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower().strip())

def contains_any(text: str, patterns: List[str]) -> List[str]:
    t = normalize(text)
    found = []
    for p in patterns:
        if normalize(p) in t and p not in found:
            found.append(p)
    return found

def risk_level(score: int) -> str:
    if score >= 75:
        return "Sangat Tinggi"
    if score >= 50:
        return "Tinggi"
    if score >= 25:
        return "Sederhana"
    return "Rendah"

def risk_class(level: str) -> str:
    return {
        "Rendah": "risk-low",
        "Sederhana": "risk-mid",
        "Tinggi": "risk-high",
        "Sangat Tinggi": "risk-very",
    }.get(level, "risk-mid")

def tokenize(text: str) -> set:
    stop = {"dan", "atau", "yang", "untuk", "dengan", "dalam", "akan", "anda", "saya", "kami", "ini", "itu", "ke", "di", "dari", "pada", "telah", "sila", "the", "and"}
    words = re.findall(r"[a-zA-ZÀ-ÿ0-9]+", normalize(text))
    return {w for w in words if len(w) > 2 and w not in stop}

def best_match(df: pd.DataFrame, text: str, text_col: str = "Ayat_Ujaran") -> Dict[str, object]:
    if df.empty or text_col not in df.columns or not text.strip():
        return {"similarity": 0, "category": "-"}
    query = tokenize(text)
    if not query:
        return {"similarity": 0, "category": "-"}
    useful_cols = [c for c in [text_col, "Label_Empirikal", "Jenis_Scam_Kawalan", "Pencetus_Emosi"] if c in df.columns]
    sample = df[useful_cols].copy()
    best_idx, best_score = 0, 0.0
    for idx, row_text in enumerate(sample[text_col].astype(str).head(1500)):
        toks = tokenize(row_text)
        if not toks:
            continue
        score = len(query & toks) / max(1, len(query | toks))
        if score > best_score:
            best_score = score
            best_idx = idx
    row = sample.iloc[best_idx]
    category = row.get("Jenis_Scam_Kawalan", row.get("Pencetus_Emosi", "-"))
    return {"similarity": int(round(best_score * 100)), "category": str(category)}

def data_match_phrase(risk_score: int, fraud_sim: int, control_sim: int) -> str:
    if risk_score >= 50 or fraud_sim > control_sim + 3:
        return "Lebih hampir kepada data penipuan siber"
    if risk_score <= 24 or control_sim >= fraud_sim:
        return "Lebih hampir kepada data kawalan sepadan"
    return "Memerlukan semakan lanjut"

def highlight_phrases(text: str, phrases: List[str]) -> str:
    safe = html.escape(text)
    for phrase in sorted(set([p for p in phrases if p]), key=len, reverse=True):
        escaped = html.escape(phrase)
        pattern = re.compile(re.escape(escaped), flags=re.IGNORECASE)
        safe = pattern.sub(lambda m: f"<mark>{m.group(0)}</mark>", safe)
    return safe

def render_pills(items: List[str], red: bool = False, fallback: str = "Tiada dikesan") -> str:
    if not items:
        return f"<span class='small-note'>{fallback}</span>"
    cls = "pill-red" if red else "pill"
    return "".join(f"<span class='{cls}'>{html.escape(str(item))}</span>" for item in sorted(set(items)))

# Lexicons
money_data = ["otp", "kata laluan", "password", "pin", "akaun bank", "nombor kad", "bayar", "caj proses", "yuran pendaftaran", "deposit", "transfer", "pindahan", "duit", "rm"]
directive = ["klik", "sahkan", "daftar", "hantar", "berikan", "hubungi", "bayar", "masukkan", "isi", "tekan"]
unrealistic = ["modal berganda", "modal", "untung", "dijamin", "pulangan", "jadi rm", "bonus", "hadiah", "wang dilepaskan", "diluluskan", "tanpa risiko"]
authority = ["pihak bank", "bank", "pegawai", "polis", "mahkamah", "lhdn", "kwsp", "syarikat", "admin", "pusat bantuan"]
urgency = ["segera", "sekarang", "hari ini", "24 jam", "15 minit", "5 minit", "slot terhad", "tinggal", "jika gagal", "akan dibekukan"]
implicit_pressure = ["jika gagal", "akan dibekukan", "slot terhad", "tinggal", "peluang terakhir", "wang dilepaskan", "dijamin", "terpilih", "vip"]
control_signals = ["laman rasmi", "aplikasi rasmi", "emel rasmi", "invois rasmi", "terma dan syarat", "saluran rasmi", "jangan kongsi otp", "syarikat berdaftar", "kaunter cawangan", "rujukan rasmi"]
emotion_map = {
    "Ketakutan": ["dibekukan", "disekat", "ditutup", "hilang", "polis", "mahkamah", "saman", "akaun akan", "aktiviti luar biasa"],
    "Kecemasan": ["segera", "sekarang", "15 minit", "24 jam", "hari ini", "jika gagal", "slot terhad", "tinggal"],
    "Harapan": ["untung", "modal", "hadiah", "bonus", "ganjaran", "diluluskan", "wang dilepaskan", "pulangan", "vip"],
    "Kepercayaan": ["puan", "tuan", "kami bantu", "pegawai", "pihak bank", "admin", "rakan", "keluarga", "dipercayai"],
    "Simpati": ["tolong", "bantuan", "kasihan", "sakit", "kecemasan", "derma", "anak", "keluarga susah"],
    "Rasa Bersalah": ["malu", "bersalah", "gagal", "nama", "tanggungjawab", "disenarai", "reputasi"],
}

def analyze_speech(text: str) -> Dict[str, object]:
    direct_phrases = sorted(set(contains_any(text, directive + money_data)))
    indirect_phrases = sorted(set(contains_any(text, unrealistic + authority + urgency + implicit_pressure)))
    control = contains_any(text, control_signals)
    score = 0
    if direct_phrases:
        score += 32
    if contains_any(text, money_data):
        score += 20
    if contains_any(text, unrealistic):
        score += 18
    if contains_any(text, authority):
        score += 14
    if contains_any(text, urgency):
        score += 16
    if control:
        score = max(0, score - min(30, 8 * len(control)))
    score = min(100, int(score))
    if direct_phrases and indirect_phrases:
        speech_type = "Gabungan lakuan pertuturan langsung dan tidak langsung"
    elif direct_phrases:
        speech_type = "Lakuan pertuturan langsung"
    elif indirect_phrases:
        speech_type = "Lakuan pertuturan tidak langsung"
    else:
        speech_type = "Tiada lakuan berisiko jelas"
    fraud_match = best_match(speech_fraud, text)
    control_match = best_match(speech_control, text)
    return {
        "score": score,
        "level": risk_level(score),
        "match": data_match_phrase(score, fraud_match["similarity"], control_match["similarity"]),
        "speech_type": speech_type,
        "direct_phrases": direct_phrases,
        "indirect_phrases": indirect_phrases,
        "control_signals": control,
    }

def analyze_emotion(text: str) -> Dict[str, object]:
    detected = {label: contains_any(text, pats) for label, pats in emotion_map.items()}
    triggers = [label for label, vals in detected.items() if vals]
    emotion_phrases = []
    for vals in detected.values():
        emotion_phrases.extend(vals)
    score = min(100, (len(triggers) * 18) + (12 if contains_any(text, urgency) else 0) + (8 if len(triggers) >= 2 else 0))
    control = contains_any(text, control_signals)
    if control:
        score = max(0, score - min(25, 7 * len(control)))
    score = int(score)
    fraud_match = best_match(emotion_fraud, text)
    control_match = best_match(emotion_control, text)
    return {
        "score": score,
        "level": risk_level(score),
        "match": data_match_phrase(score, fraud_match["similarity"], control_match["similarity"]),
        "triggers": triggers or ["Tiada pencetus emosi manipulatif yang jelas"],
        "emotion_phrases": sorted(set(emotion_phrases)),
    }

def safe_action(level: str) -> str:
    if level == "Sangat Tinggi":
        return "Mesej ini menunjukkan risiko yang sangat tinggi. Jangan kongsi kata laluan, jangan tekan pautan, jangan buat bayaran dan segera semak dengan pihak rasmi."
    if level == "Tinggi":
        return "Mesej menunjukkan ciri manipulatif yang kuat. Jangan berkongsi maklumat peribadi, jangan membuat bayaran dan semak melalui saluran rasmi."
    if level == "Sederhana":
        return "Terdapat beberapa ciri mencurigakan. Semak sumber mesej dan elakkan membuat bayaran atau menekan pautan sebelum pengesahan lanjut."
    return "Risiko rendah dikesan. Namun begitu, pengguna masih digalakkan menyemak kesahihan mesej melalui saluran rasmi."

# -----------------------------------------------------------------------------
# Interface
# -----------------------------------------------------------------------------
st.markdown(
    """
    <div class="hero">
      <h1>ScamAlert Selangor</h1>
      <p>ScamAlert Selangor ialah prototaip aplikasi web amaran awal yang membantu pengguna menyemak mesej mencurigakan sebelum berkongsi maklumat peribadi, menekan pautan atau membuat bayaran.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown("<div class='section-card'>", unsafe_allow_html=True)
st.subheader("Semak Mesej Mencurigakan")
st.markdown("<p class='muted'>Masukkan mesej yang diterima untuk menilai tahap risiko bahasa penipuan siber.</p>", unsafe_allow_html=True)
message = st.text_area(
    "Masukkan mesej di sini",
    height=150,
    placeholder="Contoh: Tampal mesej SMS, WhatsApp, Telegram atau media sosial yang mencurigakan di sini…",
)
run = st.button("Semak Risiko")
st.markdown("</div>", unsafe_allow_html=True)

if not run and not message.strip():
    st.info("Masukkan mesej mencurigakan, kemudian tekan **Semak Risiko**.")
    st.stop()

if not message.strip():
    st.warning("Sila masukkan mesej untuk dianalisis.")
    st.stop()

text = message.strip()
speech = analyze_speech(text)
emotion = analyze_emotion(text)
overall_score = int(round((speech["score"] * 0.55) + (emotion["score"] * 0.45)))
overall_level = risk_level(overall_score)

if overall_score >= 50 or ("penipuan siber" in speech["match"].lower()) or ("penipuan siber" in emotion["match"].lower()):
    overall_match = "Lebih hampir kepada data penipuan siber"
elif overall_score <= 24 and ("kawalan" in speech["match"].lower() or "kawalan" in emotion["match"].lower()):
    overall_match = "Lebih hampir kepada data kawalan sepadan"
else:
    overall_match = "Memerlukan semakan lanjut"

all_highlights = speech["direct_phrases"] + speech["indirect_phrases"] + emotion["emotion_phrases"] + speech["control_signals"]

st.markdown("<div class='section-card'>", unsafe_allow_html=True)
st.subheader("Keputusan Analisis")
st.markdown("<p class='muted'>Keputusan ini memaparkan skor risiko keseluruhan serta pecahan risiko mengikut analisis lakuan pertuturan dan analisis emosi.</p>", unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)
with col1:
    st.markdown("<div class='result-card-accent'>", unsafe_allow_html=True)
    st.markdown("<div class='mini-label'>Skor Risiko Keseluruhan</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='big-value'>{overall_score}/100</div>", unsafe_allow_html=True)
    st.markdown(f"<span class='risk-pill {risk_class(overall_level)}'>{overall_level}</span>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
with col2:
    st.markdown("<div class='result-card'>", unsafe_allow_html=True)
    st.markdown("<div class='mini-label'>Padanan Data Keseluruhan</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='medium-value'>{overall_match}</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
with col3:
    st.markdown("<div class='result-card'>", unsafe_allow_html=True)
    st.markdown("<div class='mini-label'>Cadangan Awal</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='medium-value'>{safe_action(overall_level)}</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

sub1, sub2 = st.columns(2)
with sub1:
    st.markdown("<div class='result-card'>", unsafe_allow_html=True)
    st.markdown("<div class='mini-label'>Analisis Lakuan Pertuturan</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='big-value'>{speech['score']}/100</div>", unsafe_allow_html=True)
    st.markdown(f"<span class='risk-pill {risk_class(speech['level'])}'>{speech['level']}</span>", unsafe_allow_html=True)
    st.markdown(f"<p class='muted'><b>Lakuan:</b> {html.escape(speech['speech_type'])}<br><b>Padanan:</b> {html.escape(speech['match'])}</p>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
with sub2:
    st.markdown("<div class='result-card'>", unsafe_allow_html=True)
    st.markdown("<div class='mini-label'>Analisis Emosi</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='big-value'>{emotion['score']}/100</div>", unsafe_allow_html=True)
    st.markdown(f"<span class='risk-pill {risk_class(emotion['level'])}'>{emotion['level']}</span>", unsafe_allow_html=True)
    st.markdown(f"<p class='muted'><b>Pencetus:</b> {html.escape(', '.join(emotion['triggers']))}<br><b>Padanan:</b> {html.escape(emotion['match'])}</p>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<div class='section-card'>", unsafe_allow_html=True)
st.subheader("Frasa Dikesan")
st.markdown("<p class='muted'>Bahagian ini menunjukkan frasa dalam mesej yang menyumbang kepada keputusan analisis.</p>", unsafe_allow_html=True)
st.markdown(f"<div class='text-box'>{highlight_phrases(text, all_highlights)}</div>", unsafe_allow_html=True)

f1, f2 = st.columns(2)
with f1:
    st.markdown("<div class='mini-label'>Frasa Lakuan Pertuturan Langsung</div>", unsafe_allow_html=True)
    st.markdown(render_pills(speech["direct_phrases"], red=True), unsafe_allow_html=True)
    st.markdown("<br><div class='mini-label'>Frasa Lakuan Pertuturan Tidak Langsung</div>", unsafe_allow_html=True)
    st.markdown(render_pills(speech["indirect_phrases"], red=True), unsafe_allow_html=True)
with f2:
    st.markdown("<div class='mini-label'>Frasa Pencetus Emosi</div>", unsafe_allow_html=True)
    st.markdown(render_pills(emotion["emotion_phrases"], red=False), unsafe_allow_html=True)
    st.markdown("<br><div class='mini-label'>Petanda Kawalan / Isyarat Sah</div>", unsafe_allow_html=True)
    st.markdown(render_pills(speech["control_signals"], red=False, fallback="Tiada petanda kawalan jelas dikesan"), unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<div class='section-card'>", unsafe_allow_html=True)
st.subheader("Cadangan Tindakan Selamat")
st.markdown(f"<div class='action-box'>{html.escape(safe_action(overall_level))}</div>", unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<div class='section-card'>", unsafe_allow_html=True)
st.subheader("Penafian")
st.markdown(
    "<p class='small-note'>ScamAlert Selangor ialah prototaip amaran awal dan tidak menggantikan semakan rasmi. Pengguna digalakkan menyemak kesahihan mesej melalui saluran rasmi sebelum berkongsi maklumat peribadi, menekan pautan atau membuat sebarang transaksi kewangan.</p>",
    unsafe_allow_html=True,
)
st.markdown("</div>", unsafe_allow_html=True)
