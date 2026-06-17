
import re
import streamlit as st

st.set_page_config(
    page_title="ScamAlert Selangor",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
:root{
    --bg:#F8F7F4;
    --card:#FFFFFF;
    --ink:#111827;
    --muted:#4B5563;
    --line:#111827;
    --red:#B91C1C;
    --red-soft:#FEE2E2;
    --dark-red:#7F1D1D;
    --yellow:#CA8A04;
    --yellow-soft:#FEF3C7;
    --green:#15803D;
    --green-soft:#DCFCE7;
}
html, body, [data-testid="stAppViewContainer"]{
    background:var(--bg);
    color:var(--ink);
}
[data-testid="stHeader"]{
    background:rgba(248,247,244,0.92);
}
.block-container{
    max-width:1100px;
    padding-top:4.2rem;
    padding-bottom:4rem;
}
h1, h2, h3, h4, p, div, span, label{
    color:var(--ink);
}
.hero-card{
    background:var(--card);
    border:1.2px solid var(--line);
    border-left:8px solid var(--red);
    border-radius:22px;
    padding:30px 34px;
    margin-bottom:28px;
    box-shadow:0 6px 20px rgba(17,24,39,0.04);
}
.hero-title{
    font-size:44px;
    line-height:1.1;
    font-weight:800;
    letter-spacing:.2px;
    margin:0 0 16px 0;
}
.hero-text{
    font-size:17px;
    line-height:1.7;
    color:var(--muted);
    margin:0;
    max-width:920px;
}
.section-line{
    height:1px;
    background:var(--line);
    opacity:.25;
    margin:24px 0 34px 0;
}
.section-title{
    font-size:34px;
    font-weight:800;
    margin:0 0 10px 0;
}
.section-sub{
    font-size:16px;
    color:var(--muted);
    margin:0 0 18px 0;
}
.stTextArea textarea{
    background:#FFFFFF !important;
    color:var(--ink) !important;
    border:1.2px solid var(--line) !important;
    border-radius:16px !important;
    font-size:16px !important;
    min-height:155px !important;
}
.stTextArea textarea::placeholder{
    color:#9CA3AF !important;
}
.stButton>button{
    background:var(--red) !important;
    color:#FFFFFF !important;
    border:1.2px solid var(--line) !important;
    border-radius:14px !important;
    padding:.72rem 1.4rem !important;
    font-weight:700 !important;
}
.stButton>button:hover{
    background:#991B1B !important;
    border-color:var(--line) !important;
    color:#FFFFFF !important;
}
.card{
    background:var(--card);
    border:1.2px solid var(--line);
    border-radius:18px;
    padding:18px 18px;
    min-height:150px;
    box-shadow:0 4px 18px rgba(17,24,39,0.03);
}
.card-small{
    min-height:124px;
}
.card-title{
    color:var(--muted);
    font-size:14px;
    font-weight:800;
    margin-bottom:8px;
}
.card-value{
    font-size:28px;
    font-weight:800;
    margin-bottom:8px;
}
.card-note{
    color:var(--muted);
    font-size:14px;
    line-height:1.6;
}
.risk-pill{
    display:inline-block;
    padding:8px 14px;
    border-radius:999px;
    border:1.2px solid var(--line);
    font-weight:800;
    font-size:14px;
}
.pill-low{background:var(--green-soft); color:var(--green);}
.pill-mid{background:var(--yellow-soft); color:var(--yellow);}
.pill-high{background:var(--red-soft); color:var(--red);}
.pill-very{background:#FECACA; color:var(--dark-red);}
.meter-track{
    width:100%;
    height:18px;
    background:#F3F4F6;
    border:1.2px solid var(--line);
    border-radius:999px;
    overflow:hidden;
    margin:12px 0 8px 0;
}
.meter-fill{
    height:100%;
    border-right:1.2px solid var(--line);
}
.meter-labels{
    display:flex;
    justify-content:space-between;
    color:var(--muted);
    font-size:12px;
    margin-top:4px;
}
.chip{
    display:inline-block;
    background:#FFFFFF;
    border:1.2px solid var(--line);
    border-radius:999px;
    padding:9px 13px;
    margin:5px 6px 5px 0;
    font-weight:700;
    font-size:14px;
}
.chip-risk{background:var(--red-soft); color:var(--dark-red);}
.chip-emotion{background:var(--yellow-soft); color:#713F12;}
.chip-safe{background:var(--green-soft); color:var(--green);}
.notice{
    background:#FFFFFF;
    border:1.2px solid var(--line);
    border-radius:18px;
    padding:18px 20px;
    line-height:1.7;
    color:var(--ink);
}
.result-grid{
    display:grid;
    grid-template-columns:repeat(4, 1fr);
    gap:16px;
    margin-bottom:16px;
}
.analysis-grid{
    display:grid;
    grid-template-columns:repeat(2, 1fr);
    gap:16px;
    margin-bottom:22px;
}
@media (max-width: 900px){
    .result-grid, .analysis-grid{
        grid-template-columns:1fr;
    }
    .hero-title{font-size:34px;}
}
</style>
""", unsafe_allow_html=True)

DIRECT_PATTERNS = {
    "permintaan OTP": [r"\botp\b", r"masukkan otp", r"berikan otp", r"kongsi otp", r"kod keselamatan"],
    "permintaan kata laluan": [r"kata laluan", r"password", r"pin"],
    "arahan bayaran": [r"bayar", r"caj proses", r"yuran pendaftaran", r"deposit", r"wang dilepaskan"],
    "arahan tekan pautan": [r"tekan pautan", r"klik pautan", r"link", r"pautan"],
    "arahan daftar segera": [r"daftar sekarang", r"mohon sekarang", r"hubungi segera"],
}

INDIRECT_PATTERNS = {
    "ancaman tersirat": [r"akaun.*dibekukan", r"akaun.*disekat", r"jika gagal", r"aktiviti luar biasa"],
    "desakan masa": [r"sekarang", r"segera", r"24 jam", r"hari ini", r"slot terhad", r"terhad"],
    "janji ganjaran": [r"pulangan", r"keuntungan", r"modal.*jadi", r"rm\d+.*rm\d+", r"ganjaran", r"hadiah"],
    "penyamaran autoriti": [r"pihak bank", r"pegawai", r"jabatan", r"pihak rasmi", r"akaun syarikat"],
}

EMOTION_PATTERNS = {
    "Ketakutan": [r"dibekukan", r"disekat", r"digantung", r"jika gagal", r"aktiviti luar biasa"],
    "Kecemasan": [r"segera", r"sekarang", r"24 jam", r"hari ini", r"cepat", r"terhad"],
    "Harapan": [r"pulangan", r"keuntungan", r"hadiah", r"diluluskan", r"ganjaran", r"modal.*jadi"],
    "Kepercayaan": [r"pihak bank", r"rasmi", r"pegawai", r"jabatan", r"syarikat berdaftar"],
    "Simpati": [r"bantu", r"sumbangan", r"kesusahan", r"kecemasan keluarga"],
    "Rasa Bersalah": [r"jangan kecewakan", r"tanggungjawab", r"tolong segera", r"demi keluarga"],
}

CONTROL_PATTERNS = {
    "saluran rasmi": [r"saluran rasmi", r"laman rasmi", r"aplikasi rasmi", r"emel rasmi"],
    "peringatan keselamatan": [r"jangan kongsi otp", r"jangan berkongsi otp", r"jangan kongsi kata laluan"],
    "syarat sah": [r"tertakluk pada terma", r"terma dan syarat", r"invois rasmi"],
    "maklumat semakan": [r"semak maklumat", r"semak kesahihan", r"maklumat lanjut"],
}

def find_hits(text, pattern_dict):
    hits = []
    lowered = text.lower()
    for label, patterns in pattern_dict.items():
        for pat in patterns:
            if re.search(pat, lowered, flags=re.IGNORECASE):
                hits.append(label)
                break
    return hits

def compute_scores(text):
    lowered = text.lower()
    direct_hits = find_hits(text, DIRECT_PATTERNS)
    indirect_hits = find_hits(text, INDIRECT_PATTERNS)
    emotion_hits = find_hits(text, EMOTION_PATTERNS)
    control_hits = find_hits(text, CONTROL_PATTERNS)

    speech_score = 0
    speech_score += 18 * len(direct_hits)
    speech_score += 16 * len(indirect_hits)

    emotion_score = 0
    emotion_score += 16 * len(emotion_hits)

    # Strong high-risk combinations
    has_otp = bool(re.search(r"\botp\b|kata laluan|password|pin|kod keselamatan", lowered))
    has_threat = bool(re.search(r"akaun.*dibekukan|akaun.*disekat|jika gagal|aktiviti luar biasa", lowered))
    has_urgency = bool(re.search(r"segera|sekarang|24 jam|hari ini", lowered))
    has_payment = bool(re.search(r"bayar|caj proses|yuran pendaftaran|deposit", lowered))
    has_unrealistic_gain = bool(re.search(r"pulangan|keuntungan|modal.*jadi|rm\d+.*rm\d+", lowered))

    if has_otp and has_threat:
        speech_score += 28
        emotion_score += 20
    if has_otp and has_urgency:
        speech_score += 24
        emotion_score += 18
    if has_payment and has_urgency:
        speech_score += 20
    if has_unrealistic_gain and has_urgency:
        speech_score += 18
        emotion_score += 16

    # Control signals reduce risk, but not when direct sensitive requests appear
    if control_hits and not (has_otp and not re.search(r"jangan kongsi otp|jangan berkongsi otp", lowered)):
        speech_score -= 18 * len(control_hits)
        emotion_score -= 10 * len(control_hits)

    speech_score = max(0, min(100, speech_score))
    emotion_score = max(0, min(100, emotion_score))
    overall = round((speech_score * 0.58) + (emotion_score * 0.42))

    # Force very high for OTP + threat + urgency
    if has_otp and has_threat and has_urgency:
        speech_score = max(speech_score, 92)
        emotion_score = max(emotion_score, 86)
        overall = max(overall, 92)

    return overall, speech_score, emotion_score, direct_hits, indirect_hits, emotion_hits, control_hits

def risk_level(score):
    if score >= 75:
        return "Sangat Tinggi"
    if score >= 50:
        return "Tinggi"
    if score >= 25:
        return "Sederhana"
    return "Rendah"

def risk_class(level):
    return {
        "Rendah": "pill-low",
        "Sederhana": "pill-mid",
        "Tinggi": "pill-high",
        "Sangat Tinggi": "pill-very",
    }.get(level, "pill-mid")

def risk_color(level):
    return {
        "Rendah": "#15803D",
        "Sederhana": "#CA8A04",
        "Tinggi": "#DC2626",
        "Sangat Tinggi": "#7F1D1D",
    }.get(level, "#CA8A04")

def padanan(score, control_hits):
    if control_hits and score < 45:
        return "Lebih hampir kepada data kawalan sepadan"
    if score >= 50:
        return "Lebih hampir kepada data penipuan siber"
    return "Memerlukan semakan lanjut"

def action_text(level):
    if level == "Rendah":
        return "Risiko rendah dikesan. Namun begitu, pengguna masih digalakkan menyemak kesahihan mesej melalui saluran rasmi."
    if level == "Sederhana":
        return "Terdapat beberapa ciri mencurigakan. Semak sumber mesej dan elakkan membuat bayaran atau menekan pautan sebelum pengesahan lanjut."
    if level == "Tinggi":
        return "Mesej menunjukkan ciri manipulatif yang kuat. Jangan berkongsi maklumat peribadi, jangan membuat bayaran dan semak melalui saluran rasmi."
    return "Mesej ini menunjukkan risiko yang sangat tinggi. Jangan kongsi kata laluan atau OTP, jangan tekan pautan, jangan buat sebarang transaksi kewangan dan segera semak dengan pihak rasmi."

def meter_html(score, title, note=""):
    level = risk_level(score)
    color = risk_color(level)
    return f"""
    <div class="card">
        <div class="card-title">{title}</div>
        <div class="card-value">{score}/100</div>
        <div class="meter-track"><div class="meter-fill" style="width:{score}%; background:{color};"></div></div>
        <div class="meter-labels"><span>0</span><span>25</span><span>50</span><span>75</span><span>100</span></div>
        <div class="card-note">{note}</div>
    </div>
    """

def chip_list(items, cls="chip"):
    if not items:
        return '<span class="chip">Tiada frasa dikesan</span>'
    return "".join([f'<span class="{cls}">{x}</span>' for x in items])

st.markdown("""
<div class="hero-card">
    <div class="hero-title">ScamAlert Selangor</div>
    <p class="hero-text">ScamAlert Selangor ialah prototaip aplikasi web amaran awal yang membantu pengguna menyemak mesej mencurigakan sebelum berkongsi maklumat peribadi, menekan pautan atau membuat sebarang transaksi kewangan.</p>
</div>
<div class="section-line"></div>
""", unsafe_allow_html=True)

st.markdown('<div class="section-title">Semak Mesej Mencurigakan</div>', unsafe_allow_html=True)
st.markdown('<p class="section-sub">Tampal mesej yang diterima untuk semakan awal.</p>', unsafe_allow_html=True)

message = st.text_area(
    "Masukkan mesej di sini",
    placeholder="Tampal mesej di sini…",
    label_visibility="collapsed",
    height=160
)

submitted = st.button("Semak Risiko")

if submitted and message.strip():
    overall, speech_score, emotion_score, direct_hits, indirect_hits, emotion_hits, control_hits = compute_scores(message)

    overall_level = risk_level(overall)
    speech_level = risk_level(speech_score)
    emotion_level = risk_level(emotion_score)

    st.markdown('<div class="section-line"></div>', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Keputusan Analisis</div>', unsafe_allow_html=True)

    st.markdown('<div class="result-grid">', unsafe_allow_html=True)
    st.markdown(meter_html(overall, "Skor Risiko Keseluruhan", "Gabungan analisis lakuan pertuturan dan analisis emosi."), unsafe_allow_html=True)
    st.markdown(f"""
    <div class="card card-small">
        <div class="card-title">Tahap Risiko Keseluruhan</div>
        <span class="risk-pill {risk_class(overall_level)}">{overall_level}</span>
        <div class="card-note" style="margin-top:12px;">Keputusan keseluruhan sistem.</div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown(f"""
    <div class="card card-small">
        <div class="card-title">Padanan Data Keseluruhan</div>
        <div style="font-weight:800; line-height:1.5;">{padanan(overall, control_hits)}</div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown(f"""
    <div class="card card-small">
        <div class="card-title">Pencetus Emosi Dikesan</div>
        <div style="font-weight:800; line-height:1.6;">{", ".join(emotion_hits) if emotion_hits else "Tiada pencetus emosi yang jelas"}</div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="analysis-grid">', unsafe_allow_html=True)
    st.markdown(f"""
    <div class="card">
        <div class="card-title">Analisis Lakuan Pertuturan</div>
        <div class="card-value">{speech_score}/100</div>
        <div class="meter-track"><div class="meter-fill" style="width:{speech_score}%; background:{risk_color(speech_level)};"></div></div>
        <span class="risk-pill {risk_class(speech_level)}">{speech_level}</span>
        <div class="card-note" style="margin-top:12px;">
            {"Gabungan Lakuan Pertuturan Langsung dan Tidak Langsung" if direct_hits and indirect_hits else ("Lakuan Pertuturan Langsung" if direct_hits else ("Lakuan Pertuturan Tidak Langsung" if indirect_hits else "Tiada lakuan berisiko yang jelas"))}<br>
            {padanan(speech_score, control_hits)}
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="card">
        <div class="card-title">Analisis Emosi</div>
        <div class="card-value">{emotion_score}/100</div>
        <div class="meter-track"><div class="meter-fill" style="width:{emotion_score}%; background:{risk_color(emotion_level)};"></div></div>
        <span class="risk-pill {risk_class(emotion_level)}">{emotion_level}</span>
        <div class="card-note" style="margin-top:12px;">{padanan(emotion_score, control_hits)}</div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="section-line"></div>', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Frasa Dikesan</div>', unsafe_allow_html=True)

    st.markdown(f"""
    <div class="notice">
        <h3>Frasa Lakuan Pertuturan Langsung</h3>
        {chip_list(direct_hits, "chip chip-risk")}
        <h3 style="margin-top:22px;">Frasa Lakuan Pertuturan Tidak Langsung</h3>
        {chip_list(indirect_hits, "chip chip-risk")}
        <h3 style="margin-top:22px;">Frasa Pencetus Emosi</h3>
        {chip_list(emotion_hits, "chip chip-emotion")}
        <h3 style="margin-top:22px;">Petanda Kawalan / Isyarat Sah</h3>
        {chip_list(control_hits, "chip chip-safe") if control_hits else '<span class="chip chip-safe">Tiada petanda kawalan yang jelas</span>'}
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="section-line"></div>', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Cadangan Tindakan Selamat</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="notice">{action_text(overall_level)}</div>', unsafe_allow_html=True)

    st.markdown('<div class="section-line"></div>', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Penafian</div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="notice">
    ScamAlert Selangor ialah prototaip amaran awal dan tidak menggantikan semakan rasmi. Pengguna digalakkan menyemak kesahihan mesej melalui saluran rasmi sebelum berkongsi maklumat peribadi, menekan pautan atau membuat sebarang transaksi kewangan.
    </div>
    """, unsafe_allow_html=True)

elif submitted and not message.strip():
    st.warning("Sila masukkan mesej terlebih dahulu.")
