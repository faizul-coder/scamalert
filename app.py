import html
import re
from pathlib import Path
from typing import Dict, List, Tuple

import pandas as pd
import streamlit as st

APP_TITLE = "ScamAlert Selangor"
DATA_DIR = Path(__file__).parent / "data"

st.set_page_config(
    page_title="ScamAlert Selangor",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# -----------------------------------------------------------------------------
# Visual style
# -----------------------------------------------------------------------------
st.markdown(
    """
    <style>
    [data-testid="stSidebar"] {display: none;}
    [data-testid="collapsedControl"] {display: none;}
    .block-container {padding-top: 2.4rem; padding-bottom: 2.4rem; max-width: 1200px;}
    .main-hero {
        border-radius: 26px;
        padding: 34px 38px;
        background: linear-gradient(135deg, #111111 0%, #1A1A1A 55%, #2A1010 100%);
        color: white;
        border: 1px solid rgba(255, 255, 255, 0.09);
        box-shadow: 0 18px 45px rgba(17, 24, 39, 0.15);
        margin-bottom: 22px;
    }
    .eyebrow {font-size: 0.86rem; letter-spacing: 0.12em; text-transform: uppercase; color: #FACC15; font-weight: 700; margin-bottom: 8px;}
    .hero-title {font-size: 3.2rem; line-height: 1.05; font-weight: 900; margin: 0 0 10px 0;}
    .hero-subtitle {font-size: 1.1rem; line-height: 1.55; max-width: 850px; color: #F3F4F6; margin: 0;}
    .soft-card {
        border-radius: 20px;
        padding: 22px;
        background: #FFFFFF;
        border: 1px solid #E5E7EB;
        box-shadow: 0 12px 34px rgba(17, 24, 39, 0.07);
        margin-bottom: 18px;
    }
    .result-card {
        border-radius: 20px;
        padding: 22px;
        background: #111111;
        color: white;
        border: 1px solid rgba(250, 204, 21, 0.35);
        box-shadow: 0 18px 45px rgba(17, 24, 39, 0.18);
        margin-bottom: 18px;
    }
    .metric-label {font-size: 0.82rem; color: #6B7280; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em;}
    .metric-value {font-size: 2rem; font-weight: 900; color: #111827; margin: 4px 0 0 0;}
    .metric-value-light {font-size: 2rem; font-weight: 900; color: #FFFFFF; margin: 4px 0 0 0;}
    .pill {
        display: inline-block;
        padding: 7px 12px;
        margin: 3px 5px 3px 0;
        border-radius: 999px;
        background: #FEF3C7;
        color: #78350F;
        font-weight: 700;
        font-size: 0.88rem;
        border: 1px solid #FDE68A;
    }
    .risk-pill {
        display: inline-block;
        padding: 8px 14px;
        border-radius: 999px;
        color: white;
        font-weight: 800;
        font-size: 0.95rem;
    }
    .risk-low {background: #15803D;}
    .risk-mid {background: #CA8A04;}
    .risk-high {background: #DC2626;}
    .risk-very {background: #7F1D1D;}
    .highlighted-text {
        font-size: 1.04rem;
        line-height: 1.85;
        background: #FAFAFA;
        border: 1px solid #E5E7EB;
        border-radius: 16px;
        padding: 16px;
        color: #111827;
    }
    mark {
        background: #FDE047;
        color: #111827;
        border-radius: 5px;
        padding: 2px 4px;
        font-weight: 800;
    }
    .mini-title {font-size: 1.08rem; font-weight: 900; margin-bottom: 6px; color: #111827;}
    .muted {color: #6B7280; font-size: 0.95rem; line-height: 1.55;}
    .action-box {
        border-left: 5px solid #DC2626;
        padding: 15px 17px;
        background: #FFF7ED;
        border-radius: 14px;
        color: #111827;
        font-weight: 700;
        margin-top: 8px;
    }
    div.stButton > button:first-child {
        background: #B91C1C;
        color: white;
        border: none;
        border-radius: 14px;
        padding: 0.78rem 1.4rem;
        font-weight: 900;
        width: 100%;
    }
    div.stButton > button:first-child:hover {background: #991B1B; color: white; border: none;}
    textarea, input, select {border-radius: 14px !important;}
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

scamspeech_fraud, scamspeech_control = load_dataset("scamspeech_dataset.xlsx")
scamemotion_fraud, scamemotion_control = load_dataset("scamemotion_dataset.xlsx")
scammove_fraud, scammove_control = load_dataset("scammove_dataset.xlsx")

# -----------------------------------------------------------------------------
# Lexicons and helper functions
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
    stop = {"dan", "atau", "yang", "untuk", "dengan", "dalam", "akan", "anda", "saya", "kami", "ini", "itu", "ke", "di", "dari", "pada", "telah", "sila"}
    words = re.findall(r"[a-zA-ZÀ-ÿ0-9]+", normalize(text))
    return {w for w in words if len(w) > 2 and w not in stop}

def best_match(df: pd.DataFrame, text: str, text_col: str = "Ayat_Ujaran") -> Dict[str, str]:
    if df.empty or text_col not in df.columns or not text.strip():
        return {"similarity": 0, "text": "Tiada padanan data dipaparkan.", "category": "-"}
    query = tokenize(text)
    if not query:
        return {"similarity": 0, "text": "Tiada padanan data dipaparkan.", "category": "-"}
    sample = df[[c for c in [text_col, "Label_Empirikal", "Jenis_Scam_Kawalan", "Pencetus_Emosi", "Gerakan_Dominan"] if c in df.columns]].copy()
    best_idx, best_score = 0, 0.0
    # Limit computation for fast Streamlit response while preserving representative matching
    for idx, row_text in enumerate(sample[text_col].astype(str).head(1500)):
        toks = tokenize(row_text)
        if not toks:
            continue
        overlap = len(query & toks)
        denom = max(1, len(query | toks))
        score = overlap / denom
        if score > best_score:
            best_score = score
            best_idx = idx
    row = sample.iloc[best_idx]
    cat = row.get("Jenis_Scam_Kawalan", row.get("Pencetus_Emosi", row.get("Gerakan_Dominan", "-")))
    return {
        "similarity": int(round(best_score * 100)),
        "text": str(row.get(text_col, "")),
        "category": str(cat),
    }

def highlight_phrases(text: str, phrases: List[str]) -> str:
    safe = html.escape(text)
    for phrase in sorted(set([p for p in phrases if p]), key=len, reverse=True):
        escaped = html.escape(phrase)
        pattern = re.compile(re.escape(escaped), flags=re.IGNORECASE)
        safe = pattern.sub(lambda m: f"<mark>{m.group(0)}</mark>", safe)
    return safe

# ScamSpeech lexicon
money_data = ["otp", "kata laluan", "password", "pin", "nombor kad", "akaun bank", "bayar", "caj proses", "yuran pendaftaran", "deposit", "transfer", "pindahan", "duit", "rm"]
unrealistic = ["modal berganda", "modal", "untung", "dijamin", "pulangan", "jadi rm", "bonus", "hadiah", "wang dilepaskan", "lulus", "diluluskan", "tanpa risiko"]
authority = ["pihak bank", "bank", "pegawai", "polis", "mahkamah", "lhdn", "kwsp", "syarikat", "admin", "pusat bantuan"]
urgency = ["segera", "sekarang", "hari ini", "24 jam", "15 minit", "5 minit", "slot terhad", "tinggal", "jika gagal", "akan dibekukan"]
emotion_words = ["takut", "cemas", "bimbang", "rugi", "hilang", "kasihan", "tolong", "malu", "bersalah", "tanggungjawab"]
social_proof = ["testimoni", "ramai sudah", "terbukti", "vip", "ahli", "sah", "lesen", "terjamin"]
control_signals = ["laman rasmi", "aplikasi rasmi", "emel rasmi", "invois rasmi", "terma dan syarat", "semak melalui saluran rasmi", "jangan kongsi otp", "syarikat berdaftar", "kaunter cawangan", "rujukan rasmi"]

# ScamEmotion lexicon
emotion_map = {
    "E1 Ketakutan": ["dibekukan", "disekat", "ditutup", "hilang", "polis", "mahkamah", "saman", "akaun akan", "aktiviti luar biasa"],
    "E2 Kecemasan dan Kesegeraan": ["segera", "sekarang", "15 minit", "24 jam", "hari ini", "jika gagal", "slot terhad", "tinggal"],
    "E3 Harapan dan Ganjaran": ["untung", "modal", "hadiah", "bonus", "ganjaran", "diluluskan", "wang dilepaskan", "pulangan", "vip"],
    "E4 Kepercayaan dan Keakraban": ["puan", "tuan", "kami bantu", "pegawai", "pihak bank", "admin", "rakan", "keluarga", "dipercayai"],
    "E5 Simpati dan Kasihan": ["tolong", "bantuan", "kasihan", "sakit", "kecemasan", "derma", "anak", "keluarga susah"],
    "E6 Malu, Bersalah dan Tanggungjawab": ["malu", "bersalah", "gagal", "nama", "tanggungjawab", "disenarai", "reputasi"],
}

# ScamMove lexicon
move_map = {
    "M1 Membina Identiti / Peranan": ["saya pegawai", "pihak bank", "admin", "wakil", "pegawai", "pusat bantuan", "syarikat"],
    "M2 Membina Kepercayaan / Kredibiliti": ["rasmi", "berdaftar", "terbukti", "lesen", "testimoni", "dipercayai", "selamat"],
    "M3 Mencipta Tarikan atau Krisis": ["akaun dibekukan", "aktiviti luar biasa", "peluang", "untung", "hadiah", "kerugian", "slot terhad"],
    "M4 Mengarahkan Tindakan": ["klik", "bayar", "hantar", "berikan", "daftar", "sahkan", "transfer", "hubungi"],
    "M5 Mengawal Komunikasi / Keputusan": ["jangan beritahu", "rahsia", "private", "whatsapp sahaja", "jangan hubungi", "ikut arahan"],
    "M6 Mengekalkan Eksploitasi": ["caj tambahan", "bayaran tambahan", "upgrade", "teruskan", "lagi rm", "proses seterusnya"],
}

def analyze_scamspeech(text: str) -> Dict[str, object]:
    components = {
        "Arahan wang / data sensitif": contains_any(text, money_data),
        "Janji tidak realistik": contains_any(text, unrealistic),
        "Penyamaran autoriti": contains_any(text, authority),
        "Tekanan masa": contains_any(text, urgency),
        "Manipulasi emosi": contains_any(text, emotion_words),
        "Bukti sosial / legitimasi palsu": contains_any(text, social_proof),
    }
    weights = {
        "Arahan wang / data sensitif": 24,
        "Janji tidak realistik": 18,
        "Penyamaran autoriti": 18,
        "Tekanan masa": 18,
        "Manipulasi emosi": 12,
        "Bukti sosial / legitimasi palsu": 10,
    }
    score = sum(weights[k] for k, v in components.items() if v)
    controls = contains_any(text, control_signals)
    if controls:
        score = max(0, score - min(25, 8 * len(controls)))
    score = int(min(score, 100))
    direct = bool(components["Arahan wang / data sensitif"] or contains_any(text, ["klik", "sahkan", "daftar", "hantar", "berikan", "hubungi"]))
    indirect = bool(components["Janji tidak realistik"] or components["Tekanan masa"] or components["Manipulasi emosi"] or components["Penyamaran autoriti"])
    if direct and indirect:
        lakuan = "Langsung dan Tidak Langsung"
    elif direct:
        lakuan = "Langsung"
    elif indirect:
        lakuan = "Tidak Langsung"
    else:
        lakuan = "Tiada lakuan berisiko jelas"
    if components["Arahan wang / data sensitif"]:
        searle = "Direktif"
    elif components["Janji tidak realistik"]:
        searle = "Komisif"
    elif components["Penyamaran autoriti"]:
        searle = "Representatif"
    elif components["Manipulasi emosi"]:
        searle = "Ekspresif tersirat"
    else:
        searle = "Representatif neutral"
    risky_phrases = []
    for values in components.values():
        risky_phrases.extend(values)
    return {
        "score": score,
        "level": risk_level(score),
        "components": components,
        "risky_phrases": sorted(set(risky_phrases)),
        "control_signals": controls,
        "lakuan": lakuan,
        "searle": searle,
    }

def analyze_scamemotion(text: str) -> Dict[str, object]:
    found = {label: contains_any(text, pats) for label, pats in emotion_map.items()}
    active = [label for label, pats in found.items() if pats]
    score = min(100, sum(15 for label in active) + (10 if len(active) >= 2 else 0) + (10 if contains_any(text, urgency) else 0))
    controls = contains_any(text, control_signals)
    if controls:
        score = max(0, score - min(20, 6 * len(controls)))
    phrases = []
    for values in found.values():
        phrases.extend(values)
    if score >= 75:
        intensity = "Sangat Tinggi"
    elif score >= 50:
        intensity = "Tinggi"
    elif score >= 25:
        intensity = "Sederhana"
    else:
        intensity = "Rendah"
    return {
        "score": int(score),
        "level": risk_level(int(score)),
        "active": active or ["Tiada pencetus emosi manipulatif yang jelas"],
        "phrases": sorted(set(phrases)),
        "intensity": intensity,
    }

def analyze_scammove(text: str) -> Dict[str, object]:
    found = {label: contains_any(text, pats) for label, pats in move_map.items()}
    active = [label for label, pats in found.items() if pats]
    score = min(100, sum(14 for label in active) + (14 if len(active) >= 3 else 0) + (8 if contains_any(text, ["bayar", "otp", "klik", "transfer"]) else 0))
    controls = contains_any(text, control_signals)
    if controls:
        score = max(0, score - min(20, 6 * len(controls)))
    phrases = []
    for values in found.values():
        phrases.extend(values)
    return {
        "score": int(score),
        "level": risk_level(int(score)),
        "active": active or ["Tiada gerakan manipulatif yang jelas"],
        "phrases": sorted(set(phrases)),
    }

def safe_action(overall_level: str) -> str:
    if overall_level == "Sangat Tinggi":
        return "Jangan kongsi OTP, kata laluan atau maklumat peribadi. Jangan tekan pautan dan jangan buat bayaran. Semak segera melalui saluran rasmi."
    if overall_level == "Tinggi":
        return "Jangan membuat bayaran atau berkongsi data sebelum pengesahan. Hubungi organisasi melalui laman rasmi atau nombor rasmi."
    if overall_level == "Sederhana":
        return "Terdapat beberapa petanda mencurigakan. Buat semakan lanjut melalui saluran rasmi sebelum bertindak."
    return "Risiko rendah dikesan, tetapi pengguna masih digalakkan menyemak kesahihan mesej melalui saluran rasmi."

def render_pills(items: List[str], fallback: str = "Tiada") -> str:
    if not items:
        return f"<span class='muted'>{fallback}</span>"
    return "".join(f"<span class='pill'>{html.escape(str(item))}</span>" for item in items)

# -----------------------------------------------------------------------------
# Header
# -----------------------------------------------------------------------------
st.markdown(
    f"""
    <div class="main-hero">
        <div class="eyebrow">AINS 2026 • Prototaip Aplikasi Web</div>
        <div class="hero-title">{APP_TITLE}</div>
        <p class="hero-subtitle">Satu mesej dianalisis melalui tiga lapisan: <b>ScamSpeech</b>, <b>ScamEmotion Trigger 6E</b> dan <b>ScamMove 6M</b>. Sistem memaparkan skor risiko, frasa berkaitan, padanan data dan cadangan tindakan selamat.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# -----------------------------------------------------------------------------
# Input area
# -----------------------------------------------------------------------------
examples = {
    "Tulis sendiri": "",
    "OTP + akaun dibekukan": "Pihak bank telah mengesan aktiviti luar biasa. Sila berikan OTP untuk sahkan identiti anda sekarang. Jika gagal, akaun anda akan dibekukan dalam 24 jam.",
    "Pelaburan tidak wujud": "Modal RM300 boleh jadi RM3,000 dalam 24 jam. Slot VIP tinggal 5 sahaja. Daftar sekarang.",
    "Pinjaman / bantuan palsu": "Pinjaman anda telah diluluskan. Bayar caj proses RM150 dahulu sebelum wang dilepaskan.",
    "Promosi aplikasi rasmi": "Nikmati promosi istimewa sehingga 20% untuk pembayaran bil melalui aplikasi rasmi. Tertakluk pada terma dan syarat. Maklumat lanjut di laman rasmi kami.",
    "Peringatan keselamatan sah": "Pihak bank mengingatkan pelanggan supaya tidak berkongsi OTP atau kata laluan dengan sesiapa. Semak maklumat melalui saluran rasmi sahaja.",
}

with st.container():
    st.markdown("<div class='soft-card'>", unsafe_allow_html=True)
    st.subheader("Semak Mesej")
    col_a, col_b = st.columns([0.34, 0.66])
    with col_a:
        choice = st.selectbox("Pilih contoh mesej", list(examples.keys()))
    with col_b:
        message = st.text_area(
            "Masukkan mesej untuk dianalisis",
            value=examples[choice],
            height=140,
            placeholder="Tampal mesej yang mencurigakan di sini…",
        )
    run = st.button("Semak Risiko")
    st.markdown("</div>", unsafe_allow_html=True)

if not run and not message.strip():
    st.info("Pilih contoh mesej atau tampal mesej sendiri, kemudian tekan **Semak Risiko**.")
    st.stop()

text = message.strip()
if not text:
    st.warning("Sila masukkan mesej untuk dianalisis.")
    st.stop()

speech = analyze_scamspeech(text)
emotion = analyze_scamemotion(text)
move = analyze_scammove(text)

overall_score = int(round((speech["score"] * 0.40) + (emotion["score"] * 0.30) + (move["score"] * 0.30)))
overall_level = risk_level(overall_score)
all_risky_phrases = sorted(set(speech["risky_phrases"] + emotion["phrases"] + move["phrases"]))
all_controls = speech["control_signals"]

if overall_score >= 50 and len(all_risky_phrases) >= max(1, len(all_controls)):
    data_match = "Lebih hampir kepada data penipuan siber"
elif overall_score <= 24 or len(all_controls) > len(all_risky_phrases):
    data_match = "Lebih hampir kepada data kawalan sepadan"
else:
    data_match = "Perlu semakan lanjut"

speech_fraud_match = best_match(scamspeech_fraud, text)
speech_control_match = best_match(scamspeech_control, text)
emotion_fraud_match = best_match(scamemotion_fraud, text)
move_fraud_match = best_match(scammove_fraud, text)

# -----------------------------------------------------------------------------
# Results
# -----------------------------------------------------------------------------
st.markdown("<div class='result-card'>", unsafe_allow_html=True)
st.markdown("### Keputusan Ringkas")
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown("<div class='metric-label'>Skor Risiko</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='metric-value-light'>{overall_score}/100</div>", unsafe_allow_html=True)
with col2:
    st.markdown("<div class='metric-label'>Tahap Risiko</div>", unsafe_allow_html=True)
    st.markdown(f"<span class='risk-pill {risk_class(overall_level)}'>{overall_level}</span>", unsafe_allow_html=True)
with col3:
    st.markdown("<div class='metric-label'>Padanan Data</div>", unsafe_allow_html=True)
    st.markdown(f"<div style='font-weight:900; color:#FACC15; font-size:1.15rem;'>{data_match}</div>", unsafe_allow_html=True)
with col4:
    st.markdown("<div class='metric-label'>Modul Aktif</div>", unsafe_allow_html=True)
    st.markdown("<div style='font-weight:900; color:#FFFFFF; font-size:1.15rem;'>ScamSpeech • ScamEmotion • ScamMove</div>", unsafe_allow_html=True)
st.markdown(f"<div class='action-box'>{html.escape(safe_action(overall_level))}</div>", unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<div class='soft-card'>", unsafe_allow_html=True)
st.markdown("### Teks dengan Frasa Berkaitan")
st.markdown(f"<div class='highlighted-text'>{highlight_phrases(text, all_risky_phrases + all_controls)}</div>", unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)

col_left, col_right = st.columns(2)
with col_left:
    st.markdown("<div class='soft-card'>", unsafe_allow_html=True)
    st.markdown("<div class='mini-title'>Frasa Berisiko Dikesan</div>", unsafe_allow_html=True)
    st.markdown(render_pills(all_risky_phrases, "Tiada frasa berisiko jelas dikesan."), unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
with col_right:
    st.markdown("<div class='soft-card'>", unsafe_allow_html=True)
    st.markdown("<div class='mini-title'>Petanda Kawalan / Isyarat Sah</div>", unsafe_allow_html=True)
    st.markdown(render_pills(all_controls, "Tiada petanda kawalan jelas dikesan."), unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<div class='soft-card'>", unsafe_allow_html=True)
st.markdown("### Tiga Lapisan Analisis")
mod1, mod2, mod3 = st.columns(3)
with mod1:
    st.markdown("<div class='mini-title'>ScamSpeech</div>", unsafe_allow_html=True)
    st.metric("Skor Bahasa", f"{speech['score']}/100")
    st.write(f"**Tahap:** {speech['level']}")
    st.write(f"**Lakuan:** {speech['lakuan']}")
    st.write(f"**Kategori:** {speech['searle']}")
with mod2:
    st.markdown("<div class='mini-title'>ScamEmotion Trigger 6E</div>", unsafe_allow_html=True)
    st.metric("Skor Emosi", f"{emotion['score']}/100")
    st.write(f"**Tahap:** {emotion['level']}")
    st.write(f"**Intensiti:** {emotion['intensity']}")
    st.write("**Pencetus:** " + ", ".join(emotion["active"][:3]))
with mod3:
    st.markdown("<div class='mini-title'>ScamMove 6M</div>", unsafe_allow_html=True)
    st.metric("Skor Gerakan", f"{move['score']}/100")
    st.write(f"**Tahap:** {move['level']}")
    st.write("**Gerakan:** " + ", ".join(move["active"][:3]))
st.markdown("</div>", unsafe_allow_html=True)

with st.expander("Lihat komponen risiko ScamSpeech"):
    rows = []
    for k, v in speech["components"].items():
        rows.append({"Komponen": k, "Dikesan": "Ya" if v else "Tidak", "Frasa": ", ".join(v) if v else "-"})
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

with st.expander("Lihat padanan contoh data"):
    st.markdown("**Padanan data ini digunakan sebagai rujukan konsep prototaip, bukan keputusan forensik rasmi.**")
    rows = [
        {"Sumber Data": "ScamSpeech - Penipuan Siber", "Padanan": f"{speech_fraud_match['similarity']}%", "Kategori": speech_fraud_match["category"], "Contoh Data": speech_fraud_match["text"]},
        {"Sumber Data": "ScamSpeech - Kawalan Sepadan", "Padanan": f"{speech_control_match['similarity']}%", "Kategori": speech_control_match["category"], "Contoh Data": speech_control_match["text"]},
        {"Sumber Data": "ScamEmotion - Penipuan Siber", "Padanan": f"{emotion_fraud_match['similarity']}%", "Kategori": emotion_fraud_match["category"], "Contoh Data": emotion_fraud_match["text"]},
        {"Sumber Data": "ScamMove - Penipuan Siber", "Padanan": f"{move_fraud_match['similarity']}%", "Kategori": move_fraud_match["category"], "Contoh Data": move_fraud_match["text"]},
    ]
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

st.markdown("<div class='soft-card'>", unsafe_allow_html=True)
st.markdown("### Nota Prototaip")
st.markdown(
    "<p class='muted'>ScamAlert Selangor ialah prototaip amaran awal. Keputusan yang dipaparkan membantu pengguna membuat semakan awal dan tidak menggantikan pengesahan rasmi oleh pihak berkuasa. Data yang digunakan ialah simulasi terkawal bagi tujuan pembangunan inovasi.</p>",
    unsafe_allow_html=True,
)
st.markdown("</div>", unsafe_allow_html=True)
