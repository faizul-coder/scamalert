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
    --line: #111827;
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
    background-image: none !important;
}
.block-container {
    max-width: 980px;
    padding-top: 1.2rem;
    padding-bottom: 3rem;
    position: relative;
    z-index: 1;
}
h1, h2, h3, h4, p, label, div, span { color: var(--ink); }
.hero-card {
    background: #FFFFFF;
    border: 2px solid var(--line);
    border-left: 8px solid var(--red);
    border-radius: 18px;
    padding: 1.55rem 1.8rem;
    margin-bottom: 1.3rem;
    box-shadow: 0 0 0 1px rgba(17,24,39,0.02);
}
.panel-card {
    background: transparent;
    border: none;
    border-top: 1px solid rgba(17,24,39,0.16);
    border-radius: 0;
    padding: 1.25rem 0 1.1rem 0;
    box-shadow: none;
}
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
.result-grid-top {
    display: grid;
    grid-template-columns: repeat(4, minmax(0, 1fr));
    gap: 18px;
    align-items: stretch;
    margin-top: 0.7rem;
    margin-bottom: 22px;
}
.result-grid-bottom {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 18px;
    align-items: stretch;
    margin-top: 8px;
}
.result-card {
    background: #FFFFFF;
    border: 1px solid var(--line);
    border-radius: 14px;
    padding: 1rem;
    min-height: 158px;
    box-sizing: border-box;
    box-shadow: none;
}
.result-card.result-tall {
    min-height: 210px;
}
@media (max-width: 900px) {
    .result-grid-top,
    .result-grid-bottom {
        grid-template-columns: 1fr;
    }
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
    border: 1px solid var(--line) !important;
    border-radius: 12px !important;
    min-height: 180px !important;
    font-size: 1rem !important;
}
.stTextArea textarea::placeholder { color: #9CA3AF !important; }
.stTextArea textarea:focus {
    border: 1px solid var(--red) !important;
    box-shadow: 0 0 0 1px rgba(185, 28, 28, 0.08) !important;
    outline: none !important;
}
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
.stButton > button * { color: #FFFFFF !important; }
.subtle-note {
    background: #FFFFFF;
    border: 1px solid var(--line);
    border-radius: 14px;
    padding: 1rem 1.15rem;
    color: var(--muted);
    line-height: 1.55;
}

.meter-wrap { margin-top: 0.2rem; }
.meter-score {
    font-size: 1.85rem;
    font-weight: 850;
    color: var(--ink);
    line-height: 1.1;
    margin-bottom: 0.55rem;
}
.meter-zones {
    position: relative;
    width: 100%;
    height: 10px;
    border-radius: 999px;
    background: linear-gradient(90deg,
        #15803D 0%, #15803D 24%,
        #CA8A04 24%, #CA8A04 49%,
        #DC2626 49%, #DC2626 74%,
        #7F1D1D 74%, #7F1D1D 100%);
    opacity: 0.92;
}
.meter-pointer {
    position: absolute;
    top: -5px;
    width: 7px;
    height: 20px;
    border-radius: 999px;
    background: #111827;
    box-shadow: 0 0 0 2px #FFFFFF;
    transform: translateX(-50%);
}
.meter-scale {
    display: flex;
    justify-content: space-between;
    color: var(--muted);
    font-size: 0.72rem;
    margin-top: 0.35rem;
}

</style>
""", unsafe_allow_html=True)

DIRECT_PATTERNS = {
    r"\botp\b|kod keselamatan|tac|pin\b|kata laluan|password": (45, "permintaan OTP/kata laluan"),
    r"\bbayar\b|buat bayaran|bayaran|rm\s?\d+|ringgit": (25, "arahan bayaran"),
    r"caj.*(proses|pemprosesan)|caj pemprosesan|yuran.*(pendaftaran|pemprosesan)|bayaran pendahuluan|deposit": (35, "caj/yuran pendahuluan"),
    r"klik pautan|tekan pautan|link\b|pautan": (25, "arahan menekan pautan"),
    r"daftar sekarang|mohon sekarang|hubungi segera|whatsapp segera": (18, "arahan segera"),
    r"masukkan|sahkan|kemas kini|kemaskini|isi borang|lengkapkan maklumat": (18, "arahan pengesahan/maklumat"),
    r"pindahkan wang|transfer wang|pengeluaran wang|wang dilepaskan|dana dilepaskan|dana dikreditkan|duit dilepaskan": (30, "arahan berkaitan wang"),
}

INDIRECT_PATTERNS = {
    r"jika gagal|kalau gagal|sekiranya gagal": (18, "ancaman tersirat"),
    r"segera|sekarang|24 jam|15 minit|5 minit|hari ini|sebelum jam": (18, "desakan masa"),
    r"slot terhad|tinggal \d+|peluang terhad|tawaran terhad|tempat terhad": (16, "kelangkaan palsu"),
    r"risiko rendah|jamin|dijamin|confirm|pasti lulus": (18, "jaminan tidak realistik"),
    r"pulangan tinggi|untung besar|modal.*jadi|keuntungan berganda|wang berganda": (24, "janji keuntungan tidak realistik"),
    r"akaun.*dibekukan|akaun.*disekat|akaun.*ditutup|aktiviti luar biasa": (30, "ancaman akaun"),
    r"sebelum.*pengeluaran wang|sebelum.*wang.*dilepaskan|sebelum.*duit.*dilepaskan|sebelum.*dana.*dilepaskan|sebelum.*dana.*dikreditkan|pengeluaran wang.*dilakukan|pengeluaran wang.*dibuat": (40, "syarat sebelum pengeluaran wang"),
    r"pinjaman.*diluluskan|bantuan.*diluluskan|permohonan.*lulus": (24, "kelulusan kewangan mencurigakan"),
    r"kerja mudah|kerja dari rumah|bayaran harian|komisen harian": (20, "kerja mudah mencurigakan"),
    r"anda terpilih|menang hadiah|hadiah tunai|ganjaran tunai": (22, "hadiah/ganjaran mencurigakan"),
}

EMOTION_PATTERNS = {
    "Ketakutan": [
        r"akaun.*dibekukan", r"akaun.*disekat", r"akaun.*ditutup",
        r"jika gagal", r"aktiviti luar biasa", r"tindakan undang-undang",
        r"disenarai hitam", r"polis"
    ],
    "Kecemasan": [
        r"segera", r"sekarang", r"24 jam", r"hari ini", r"sebelum jam",
        r"slot terhad", r"tawaran terhad"
    ],
    "Harapan": [
        r"untung", r"ganjaran", r"bonus", r"pulangan", r"diluluskan",
        r"hadiah", r"pengeluaran wang", r"wang dilepaskan", r"dana dikreditkan",
        r"duit dilepaskan", r"modal.*jadi"
    ],
    "Kepercayaan": [
        r"bank", r"pegawai", r"rasmi", r"syarikat berdaftar",
        r"invois", r"jabatan", r"pihak berkuasa"
    ],
    "Simpati": [
        r"bantu", r"sumbangan", r"anak sakit", r"kesusahan", r"kecemasan keluarga"
    ],
    "Rasa Bersalah": [
        r"jika anda tidak", r"anda punca", r"tolong saya", r"jangan kecewakan",
        r"tanggungjawab"
    ],
}

CONTROL_PATTERNS = {
    r"melalui aplikasi rasmi": "saluran rasmi",
    r"tertakluk pada terma dan syarat": "terma dan syarat",
    r"jangan kongsi otp|jangan berkongsi otp|tidak berkongsi otp": "peringatan keselamatan",
    r"jangan kongsi kata laluan|tidak berkongsi kata laluan": "peringatan keselamatan",
    r"hubungi emel rasmi": "emel rasmi",
    r"akaun syarikat berdaftar": "akaun syarikat berdaftar",
    r"invois rasmi|invois yang dilampirkan": "invois rasmi",
    r"saluran rasmi|laman rasmi|portal rasmi": "saluran rasmi",
    r"semak kesahihan|semak maklumat|maklumat lanjut": "semakan rasmi",
}

def risk_level(score: int) -> str:
    if score <= 24: return "Rendah"
    if score <= 49: return "Sederhana"
    if score <= 74: return "Tinggi"
    return "Sangat Tinggi"

def badge_class(level: str) -> str:
    return {"Rendah":"badge-low", "Sederhana":"badge-medium", "Tinggi":"badge-high", "Sangat Tinggi":"badge-vhigh"}.get(level, "badge-medium")

def risk_meter(score: int) -> str:
    score = max(0, min(100, int(score)))
    return (
        f'<div class="meter-wrap">'
        f'<div class="meter-score">{score}/100</div>'
        f'<div class="meter-zones"><span class="meter-pointer" style="left:{score}%;"></span></div>'
        f'<div class="meter-scale"><span>0</span><span>25</span><span>50</span><span>75</span><span>100</span></div>'
        f'</div>'
    )

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
    if score >= 60:
        return "Lebih hampir kepada data penipuan siber"
    if has_control and score <= 35:
        return "Lebih hampir kepada data kawalan sepadan"
    return "Memerlukan semakan lanjut"

def analyse_text(message: str):
    text = message.strip().lower()

    direct_score, direct_labels = find_matches(text, DIRECT_PATTERNS)
    indirect_score, indirect_labels = find_matches(text, INDIRECT_PATTERNS)
    control_score, control_labels = find_matches(text, {k: (8, v) for k, v in CONTROL_PATTERNS.items()})
    emotion_score, emotions = analyse_emotions(text)

    has_control = bool(control_labels)

    # Core pattern indicators
    has_sensitive_data = bool(re.search(r"\botp\b|kod keselamatan|tac|pin\b|kata laluan|password|nombor kad|maklumat peribadi", text, flags=re.I))
    has_authority = bool(re.search(r"pihak bank|bank|pegawai|jabatan|pihak berkuasa|rasmi", text, flags=re.I))
    has_account_threat = bool(re.search(r"akaun.*dibekukan|akaun.*disekat|akaun.*ditutup|aktiviti luar biasa|jika gagal|kalau gagal", text, flags=re.I))
    has_time_pressure = bool(re.search(r"segera|sekarang|24 jam|15 minit|5 minit|hari ini|slot terhad|tawaran terhad", text, flags=re.I))

    has_money_request = bool(re.search(r"\bbayar\b|buat bayaran|bayaran|rm\s?\d+|ringgit|deposit|transfer|pindahan", text, flags=re.I))
    has_processing_fee = bool(re.search(r"caj pemprosesan|caj proses|caj|pemprosesan|yuran pemprosesan|yuran pendaftaran|bayaran pendahuluan", text, flags=re.I))
    has_release_condition = bool(re.search(r"sebelum.*pengeluaran wang|sebelum.*wang.*dilepaskan|sebelum.*duit.*dilepaskan|sebelum.*dana.*dilepaskan|sebelum.*dana.*dikreditkan|pengeluaran wang.*dilakukan|pengeluaran wang.*dibuat|wang.*dilepaskan|duit.*dilepaskan", text, flags=re.I))

    has_loan = bool(re.search(r"pinjaman|bantuan|wang diluluskan|permohonan.*lulus|telah diluluskan", text, flags=re.I))
    has_unrealistic_gain = bool(re.search(r"modal.*jadi|untung|pulangan tinggi|keuntungan berganda|dijamin|bonus|hadiah|ganjaran", text, flags=re.I))
    has_job_scam = bool(re.search(r"kerja mudah|kerja dari rumah|bayaran harian|komisen harian|like dan follow|tugasan mudah", text, flags=re.I))
    has_prize = bool(re.search(r"anda terpilih|menang hadiah|hadiah tunai|ganjaran tunai|tahniah", text, flags=re.I))
    has_link_or_form = bool(re.search(r"klik pautan|tekan pautan|link\b|isi borang|lengkapkan maklumat|sahkan maklumat", text, flags=re.I))

    has_safety_warning = bool(re.search(r"jangan.*(otp|kata laluan|password)|tidak berkongsi|jangan berkongsi|saluran rasmi|laman rasmi|aplikasi rasmi|terma dan syarat|invois rasmi", text, flags=re.I))

    # Base score
    speech_score = max(0, min(100, direct_score + indirect_score))
    if has_safety_warning and not (has_money_request and has_processing_fee):
        # Safety reminders should not be penalized merely because they mention OTP or password.
        speech_score = max(0, speech_score - control_score - 25)
        emotion_score = max(0, emotion_score - 10)
    else:
        speech_score = max(0, speech_score - control_score)

    overall_score = int(min(100, round(speech_score * 0.6 + emotion_score * 0.4)))

    # Pattern-based minimum risk rules.
    # These prevent clearly risky messages from being classified as low merely because wording varies.
    if has_sensitive_data and has_account_threat and has_time_pressure:
        direct_labels += ["permintaan data sensitif"]
        indirect_labels += ["ancaman akaun", "desakan masa"]
        speech_score = max(speech_score, 90)
        emotion_score = max(emotion_score, 78)
        overall_score = max(overall_score, 92)

    elif has_money_request and has_processing_fee and has_release_condition:
        direct_labels += ["arahan bayaran"]
        indirect_labels += ["syarat sebelum pengeluaran wang"]
        if "Harapan" not in emotions:
            emotions.append("Harapan")
            emotion_score = min(100, emotion_score + 18)
        speech_score = max(speech_score, 88)
        emotion_score = max(emotion_score, 58)
        overall_score = max(overall_score, 84)

    elif has_loan and has_money_request and has_processing_fee:
        direct_labels += ["arahan bayaran"]
        indirect_labels += ["kelulusan kewangan mencurigakan"]
        if "Harapan" not in emotions:
            emotions.append("Harapan")
            emotion_score = min(100, emotion_score + 18)
        speech_score = max(speech_score, 82)
        emotion_score = max(emotion_score, 54)
        overall_score = max(overall_score, 80)

    elif has_unrealistic_gain and (has_time_pressure or has_money_request):
        indirect_labels += ["janji keuntungan tidak realistik"]
        if "Harapan" not in emotions:
            emotions.append("Harapan")
            emotion_score = min(100, emotion_score + 18)
        speech_score = max(speech_score, 76)
        emotion_score = max(emotion_score, 54)
        overall_score = max(overall_score, 76)

    elif has_job_scam and (has_processing_fee or has_money_request):
        direct_labels += ["arahan bayaran"]
        indirect_labels += ["kerja mudah mencurigakan"]
        speech_score = max(speech_score, 76)
        overall_score = max(overall_score, 76)

    elif has_prize and (has_link_or_form or has_sensitive_data):
        direct_labels += ["arahan pengesahan/maklumat"]
        indirect_labels += ["hadiah/ganjaran mencurigakan"]
        speech_score = max(speech_score, 82)
        emotion_score = max(emotion_score, 56)
        overall_score = max(overall_score, 80)

    elif has_authority and (has_sensitive_data or has_link_or_form):
        direct_labels += ["arahan pengesahan/maklumat"]
        indirect_labels += ["penyamaran autoriti"]
        speech_score = max(speech_score, 78)
        overall_score = max(overall_score, 78)

    elif has_money_request and has_processing_fee:
        direct_labels += ["arahan bayaran"]
        speech_score = max(speech_score, 68)
        overall_score = max(overall_score, 68)

    if has_safety_warning and not (has_money_request and has_processing_fee) and overall_score < 50:
        overall_score = min(overall_score, 20)
        speech_score = min(speech_score, 20)
        emotion_score = min(emotion_score, 15)

    direct_labels = list(dict.fromkeys(direct_labels))
    indirect_labels = list(dict.fromkeys(indirect_labels))
    emotions = list(dict.fromkeys(emotions))
    control_labels = list(dict.fromkeys(control_labels))

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
  <p class="subtitle-main">ScamAlert Selangor ialah sistem amaran awal penipuan siber berasaskan Kecerdasan Buatan (AI) yang menganalisis corak bahasa, manipulasi emosi dan strategi pujukan dalam mesej digital untuk membantu rakyat Malaysia mengenal pasti risiko penipuan sebelum kerugian berlaku.</p>
</div>
""", unsafe_allow_html=True)

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
    level = result["overall_level"]
    emo_text = ", ".join(result["emotions"]) if result["emotions"] else "Tiada pencetus emosi yang ketara"

    result_html = f"""<div class="result-grid-top">
<div class="result-card">
<div class="result-label">Skor Risiko Keseluruhan</div>
{risk_meter(result["overall_score"])}
<div class="result-note">Gabungan analisis lakuan pertuturan dan analisis emosi</div>
</div>
<div class="result-card">
<div class="result-label">Tahap Risiko Keseluruhan</div>
<div class="badge {badge_class(level)}">{level}</div>
<div class="result-note">Keputusan keseluruhan sistem</div>
</div>
<div class="result-card">
<div class="result-label">Padanan Data Keseluruhan</div>
<div class="result-note" style="color:#111827;font-weight:750;">{result["overall_match"]}</div>
</div>
<div class="result-card">
<div class="result-label">Pencetus Emosi Dikesan</div>
<div class="result-note" style="color:#111827;font-weight:750;">{emo_text}</div>
</div>
</div>
<div class="result-grid-bottom">
<div class="result-card result-tall">
<div class="result-label">Analisis Lakuan Pertuturan</div>
{risk_meter(result["speech_score"])}
<div class="badge {badge_class(result["speech_level"])}">{result["speech_level"]}</div>
<div class="result-note">{result["speech_type"]}</div>
<div class="result-note">{result["speech_match"]}</div>
</div>
<div class="result-card result-tall">
<div class="result-label">Analisis Emosi</div>
{risk_meter(result["emotion_score"])}
<div class="badge {badge_class(result["emotion_level"])}">{result["emotion_level"]}</div>
<div class="result-note">{result["emotion_match"]}</div>
</div>
</div>"""
    st.markdown(result_html, unsafe_allow_html=True)
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
        "Sangat Tinggi": "Mesej ini menunjukkan risiko yang sangat tinggi. Jangan kongsi kata laluan, jangan tekan pautan, jangan buat sebarang transaksi kewangan dan segera semak dengan pihak rasmi.",
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
