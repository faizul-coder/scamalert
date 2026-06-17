import re
import streamlit as st

st.set_page_config(page_title="ScamAlert Selangor", page_icon="🛡️", layout="wide")

st.markdown("""
<style>
:root {
    --bg: #F8F7F4;
    --card: #FFFFFF;
    --ink: #111827;
    --muted: #4B5563;
    --line: #E5E7EB;
    --red: #B91C1C;
    --red-dark: #7F1D1D;
    --red-soft: #FEE2E2;
    --yellow: #CA8A04;
    --yellow-soft: #FEF3C7;
    --green: #15803D;
    --green-soft: #DCFCE7;
}
html, body, [class*="css"] { font-family: "Inter", sans-serif; }
.stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
    background-color: var(--bg) !important;
}
.stApp::before {
    content: "";
    position: fixed;
    inset: 0;
    pointer-events: none;
    z-index: 0;
    background-image:
        linear-gradient(rgba(185, 28, 28, 0.085) 1.2px, transparent 1.2px),
        linear-gradient(90deg, rgba(185, 28, 28, 0.085) 1.2px, transparent 1.2px),
        radial-gradient(circle at 16% 18%, rgba(250, 204, 21, 0.24), transparent 20%),
        radial-gradient(circle at 84% 78%, rgba(185, 28, 28, 0.18), transparent 24%),
        repeating-linear-gradient(135deg, rgba(17, 24, 39, 0.035) 0 1px, transparent 1px 26px);
    background-size: 58px 58px, 58px 58px, 100% 100%, 100% 100%, 100% 100%;
    opacity: 0.95;
}
.stApp::after {
    content: "";
    position: fixed;
    right: -30px;
    top: 105px;
    width: 430px;
    height: 430px;
    pointer-events: none;
    z-index: 0;
    border-radius: 50%;
    border: 1.5px solid rgba(185, 28, 28, 0.20);
    box-shadow:
        inset 0 0 0 22px rgba(250, 204, 21, 0.07),
        inset 0 0 0 58px rgba(185, 28, 28, 0.055),
        0 0 0 1px rgba(250, 204, 21, 0.04);
}
.cyber-strip {
    height: 44px;
    margin: 0 0 1.1rem 0;
    border-radius: 18px;
    border: 1px solid rgba(185, 28, 28, 0.16);
    background:
        linear-gradient(90deg, rgba(185,28,28,0.11), rgba(250,204,21,0.08), rgba(185,28,28,0.04)),
        repeating-linear-gradient(90deg, transparent 0 32px, rgba(185,28,28,0.12) 32px 33px, transparent 33px 76px);
    box-shadow: 0 10px 26px rgba(17, 24, 39, 0.035);
}
.block-container {
    max-width: 980px;
    padding-top: 1.2rem;
    padding-bottom: 3rem;
    position: relative;
    z-index: 1;
}
h1, h2, h3, h4, p, label, div, span { color: var(--ink); }
.hero-card, .panel-card {
    background: rgba(255,255,255,0.96);
    backdrop-filter: blur(4px);
    border: 1px solid rgba(229, 231, 235, 0.95);
    border-radius: 22px;
    padding: 1.5rem 1.7rem;
    box-shadow: 0 12px 28px rgba(17,24,39,0.055);
}
.hero-card { border-left: 6px solid var(--red); margin-bottom: 1.25rem; }
.title-main {
    font-size: 2.85rem;
    font-weight: 850;
    margin: 0 0 0.65rem 0;
    line-height: 1.08;
    color: var(--ink);
}
.subtitle-main {
    font-size: 1.12rem;
    line-height: 1.65;
    color: var(--muted);
    margin: 0;
}
.helper-text { color: var(--muted); font-size: 1rem; margin-top: -0.3rem; margin-bottom: 0.8rem; }
.result-card {
    background: #FFFFFF;
    border: 1px solid var(--line);
    border-radius: 18px;
    padding: 1rem;
    height: 100%;
}
.result-label { font-size: 0.9rem; color: var(--muted); font-weight: 750; margin-bottom: 0.35rem; }
.result-value { font-size: 1.95rem; font-weight: 850; color: var(--ink); line-height: 1.15; }
.result-note { font-size: 0.92rem; color: var(--muted); margin-top: 0.45rem; line-height: 1.45; }
.badge {
    display: inline-block;
    padding: 0.38rem 0.78rem;
    border-radius: 999px;
    font-size: 0.92rem;
    font-weight: 750;
    border: 1px solid transparent;
    margin-top: 0.35rem;
}
.badge-low { background: var(--green-soft); color: var(--green); border-color: #BBF7D0; }
.badge-medium { background: var(--yellow-soft); color: var(--yellow); border-color: #FDE68A; }
.badge-high { background: var(--red-soft); color: var(--red); border-color: #FECACA; }
.badge-vhigh { background: #FDE8E8; color: var(--red-dark); border-color: #FCA5A5; }
.tag-wrap { display: flex; flex-wrap: wrap; gap: 10px; margin-top: 0.55rem; }
.tag {
    display: inline-block;
    padding: 0.5rem 0.8rem;
    border-radius: 12px;
    font-size: 0.95rem;
    font-weight: 650;
    border: 1px solid var(--line);
    color: var(--ink);
}
.tag-red { background: var(--red-soft); border-color: #FECACA; }
.tag-yellow { background: var(--yellow-soft); border-color: #FDE68A; }
.tag-green { background: var(--green-soft); border-color: #BBF7D0; }
.tag-neutral { background: #F3F4F6; border-color: #E5E7EB; }
.stTextArea textarea {
    background: #FFFFFF !important;
    color: var(--ink) !important;
    border: 1px solid #D1D5DB !important;
    border-radius: 16px !important;
    min-height: 180px !important;
    font-size: 1rem !important;
}
.stTextArea textarea::placeholder { color: #9CA3AF !important; }
.stButton > button {
    background: var(--red) !important;
    color: white !important;
    border: none !important;
    border-radius: 14px !important;
    padding: 0.7rem 1.3rem !important;
    font-weight: 750 !important;
    font-size: 1rem !important;
}
.stButton > button:hover { background: #991B1B !important; color: white !important; }
.subtle-note {
    background: #FCFCFD;
    border: 1px solid var(--line);
    border-radius: 16px;
    padding: 1rem 1.15rem;
    color: var(--muted);
    line-height: 1.55;
}
</style>
""", unsafe_allow_html=True)

DIRECT_PATTERNS = {
    r"berikan otp|masukkan otp|kongsi otp": (35, "permintaan OTP"),
    r"bayar caj proses|caj proses": (30, "bayar caj proses"),
    r"bayar yuran|yuran pendaftaran": (25, "bayaran pendahuluan"),
    r"pindahkan wang|transfer wang": (35, "arahan pindahan wang"),
    r"daftar sekarang": (15, "arahan segera mendaftar"),
    r"klik pautan|tekan pautan": (20, "arahan menekan pautan"),
    r"akaun dibekukan": (25, "ancaman akaun dibekukan"),
}
INDIRECT_PATTERNS = {
    r"jika gagal": (15, "ancaman tersirat"),
    r"segera|sekarang": (10, "desakan masa"),
    r"24 jam|hari ini|sebelum jam": (12, "had masa"),
    r"slot terhad|tinggal \d+|terhad": (15, "kelangkaan palsu"),
    r"risiko rendah|jamin|dijamin": (15, "jaminan tidak realistik"),
    r"pulangan tinggi|untung besar|modal.*jadi": (18, "janji keuntungan"),
}
EMOTION_PATTERNS = {
    "Ketakutan": [r"akaun dibekukan", r"disenarai hitam", r"aktiviti luar biasa", r"tindakan undang-undang", r"polis"],
    "Kecemasan": [r"segera", r"sekarang", r"24 jam", r"hari ini", r"sebelum jam"],
    "Harapan": [r"untung", r"ganjaran", r"bonus", r"pulangan", r"diluluskan", r"hadiah"],
    "Kepercayaan": [r"bank", r"pegawai", r"rasmi", r"syarikat berdaftar", r"invois"],
    "Simpati": [r"bantu", r"sumbangan", r"anak sakit", r"kesusahan"],
    "Rasa Bersalah": [r"jika anda tidak", r"anda punca", r"tolong saya", r"jangan kecewakan"],
}
CONTROL_PATTERNS = {
    r"melalui aplikasi rasmi": "saluran rasmi",
    r"tertakluk pada terma dan syarat": "terma dan syarat",
    r"jangan kongsi otp": "peringatan keselamatan",
    r"hubungi emel rasmi": "emel rasmi",
    r"akaun syarikat berdaftar": "akaun syarikat berdaftar",
    r"invois rasmi|invois yang dilampirkan": "invois rasmi",
    r"saluran rasmi": "saluran rasmi",
}

def risk_level(score: int) -> str:
    if score <= 24: return "Rendah"
    if score <= 49: return "Sederhana"
    if score <= 74: return "Tinggi"
    return "Sangat Tinggi"

def badge_class(level: str) -> str:
    return {"Rendah":"badge-low", "Sederhana":"badge-medium", "Tinggi":"badge-high", "Sangat Tinggi":"badge-vhigh"}.get(level, "badge-medium")

def find_matches(text: str, pattern_dict: dict):
    labels, score = [], 0
    for pattern, payload in pattern_dict.items():
        if re.search(pattern, text, flags=re.I):
            if isinstance(payload, tuple):
                weight, label = payload
                score += weight
                labels.append(label)
            else:
                labels.append(payload)
    return score, list(dict.fromkeys(labels))

def analyse_emotions(text: str):
    emotions, score = [], 0
    for emotion, patterns in EMOTION_PATTERNS.items():
        if any(re.search(p, text, flags=re.I) for p in patterns):
            emotions.append(emotion)
            score += 18
    return min(score, 100), emotions

def match_phrase(score: int, has_control: bool):
    if score >= 60: return "Lebih hampir kepada data penipuan siber"
    if has_control and score <= 35: return "Lebih hampir kepada data kawalan sepadan"
    return "Memerlukan semakan lanjut"

def analyse_text(message: str):
    text = message.strip().lower()
    direct_score, direct_labels = find_matches(text, DIRECT_PATTERNS)
    indirect_score, indirect_labels = find_matches(text, INDIRECT_PATTERNS)
    control_score, control_labels = find_matches(text, {k: (8, v) for k, v in CONTROL_PATTERNS.items()})
    emotion_score, emotions = analyse_emotions(text)
    speech_score = max(0, min(100, direct_score + indirect_score - control_score))
    overall_score = int(min(100, round(speech_score * 0.6 + emotion_score * 0.4)))
    if direct_labels and indirect_labels:
        speech_type = "Gabungan Lakuan Pertuturan Langsung dan Tidak Langsung"
    elif direct_labels:
        speech_type = "Lakuan Pertuturan Langsung"
    elif indirect_labels:
        speech_type = "Lakuan Pertuturan Tidak Langsung"
    else:
        speech_type = "Tiada pola lakuan yang ketara"
    return {
        "overall_score": overall_score,
        "overall_level": risk_level(overall_score),
        "overall_match": match_phrase(overall_score, bool(control_labels)),
        "speech_score": speech_score,
        "speech_level": risk_level(speech_score),
        "speech_match": match_phrase(speech_score, bool(control_labels)),
        "speech_type": speech_type,
        "emotion_score": emotion_score,
        "emotion_level": risk_level(emotion_score),
        "emotion_match": match_phrase(emotion_score, bool(control_labels)),
        "emotions": emotions,
        "direct_phrases": direct_labels,
        "indirect_phrases": indirect_labels,
        "emotion_phrases": emotions,
        "control_phrases": control_labels,
    }

st.markdown("""
<div class="hero-card">
  <div class="title-main">ScamAlert Selangor</div>
  <p class="subtitle-main">ScamAlert Selangor ialah prototaip aplikasi web amaran awal yang membantu pengguna menyemak mesej mencurigakan sebelum berkongsi maklumat peribadi, menekan pautan atau membuat bayaran.</p>
</div>
""", unsafe_allow_html=True)

st.markdown('<div class="cyber-strip"></div>', unsafe_allow_html=True)

st.markdown('<div class="panel-card">', unsafe_allow_html=True)
st.markdown("## Semak Mesej Mencurigakan")
st.markdown('<p class="helper-text">Tampal mesej yang diterima untuk semakan awal.</p>', unsafe_allow_html=True)
message = st.text_area("Mesej", label_visibility="collapsed", placeholder="Tampal mesej di sini…", key="message_input")
check = st.button("Semak Risiko")
st.markdown('</div>', unsafe_allow_html=True)

if check and message.strip():
    result = analyse_text(message)
    st.markdown('<div class="panel-card">', unsafe_allow_html=True)
    st.markdown("## Keputusan Analisis")
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f'<div class="result-card"><div class="result-label">Skor Risiko Keseluruhan</div><div class="result-value">{result["overall_score"]}/100</div><div class="result-note">Gabungan analisis lakuan pertuturan dan analisis emosi</div></div>', unsafe_allow_html=True)
    with c2:
        level = result["overall_level"]
        st.markdown(f'<div class="result-card"><div class="result-label">Tahap Risiko Keseluruhan</div><div class="badge {badge_class(level)}">{level}</div><div class="result-note">Keputusan keseluruhan sistem</div></div>', unsafe_allow_html=True)
    with c3:
        st.markdown(f'<div class="result-card"><div class="result-label">Padanan Data Keseluruhan</div><div class="result-note" style="color:#111827;font-weight:750;">{result["overall_match"]}</div></div>', unsafe_allow_html=True)
    with c4:
        emo_text = ", ".join(result["emotions"]) if result["emotions"] else "Tiada pencetus emosi yang ketara"
        st.markdown(f'<div class="result-card"><div class="result-label">Pencetus Emosi Dikesan</div><div class="result-note" style="color:#111827;font-weight:750;">{emo_text}</div></div>', unsafe_allow_html=True)
    c5, c6 = st.columns(2)
    with c5:
        st.markdown(f'<div class="result-card"><div class="result-label">Analisis Lakuan Pertuturan</div><div class="result-value">{result["speech_score"]}/100</div><div class="badge {badge_class(result["speech_level"])}">{result["speech_level"]}</div><div class="result-note">{result["speech_type"]}</div><div class="result-note">{result["speech_match"]}</div></div>', unsafe_allow_html=True)
    with c6:
        st.markdown(f'<div class="result-card"><div class="result-label">Analisis Emosi</div><div class="result-value">{result["emotion_score"]}/100</div><div class="badge {badge_class(result["emotion_level"])}">{result["emotion_level"]}</div><div class="result-note">{result["emotion_match"]}</div></div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="panel-card">', unsafe_allow_html=True)
    st.markdown("## Frasa Dikesan")
    sections = [
        ("Frasa Lakuan Pertuturan Langsung", result["direct_phrases"] or ["Tiada frasa langsung yang ketara"], "tag-red"),
        ("Frasa Lakuan Pertuturan Tidak Langsung", result["indirect_phrases"] or ["Tiada frasa tidak langsung yang ketara"], "tag-yellow"),
        ("Frasa Pencetus Emosi", result["emotion_phrases"] or ["Tiada frasa emosi yang ketara"], "tag-neutral"),
        ("Petanda Kawalan / Isyarat Sah", result["control_phrases"] or ["Tiada petanda kawalan yang jelas"], "tag-green"),
    ]
    for title, tags, cls in sections:
        st.markdown(f"#### {title}")
        st.markdown('<div class="tag-wrap">' + ''.join([f'<span class="tag {cls}">{t}</span>' for t in tags]) + '</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    guidance = {
        "Rendah": "Risiko rendah dikesan. Namun begitu, pengguna masih digalakkan menyemak kesahihan mesej melalui saluran rasmi.",
        "Sederhana": "Terdapat beberapa ciri mencurigakan. Semak sumber mesej dan elakkan membuat bayaran atau menekan pautan sebelum pengesahan lanjut.",
        "Tinggi": "Mesej menunjukkan ciri manipulatif yang kuat. Jangan berkongsi maklumat peribadi, jangan membuat bayaran dan semak melalui saluran rasmi.",
        "Sangat Tinggi": "Mesej ini menunjukkan risiko yang sangat tinggi. Jangan kongsi kata laluan, jangan tekan pautan, jangan buat bayaran dan segera semak dengan pihak rasmi.",
    }
    st.markdown('<div class="panel-card">', unsafe_allow_html=True)
    st.markdown("## Cadangan Tindakan Selamat")
    st.markdown(f'<div class="subtle-note">{guidance[result["overall_level"]]}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="panel-card">', unsafe_allow_html=True)
    st.markdown("## Penafian")
    st.markdown('<div class="subtle-note">ScamAlert Selangor ialah prototaip amaran awal dan tidak menggantikan semakan rasmi. Pengguna digalakkan menyemak kesahihan mesej melalui saluran rasmi sebelum berkongsi maklumat peribadi, menekan pautan atau membuat sebarang transaksi kewangan.</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
elif check and not message.strip():
    st.warning("Sila masukkan mesej terlebih dahulu.")
