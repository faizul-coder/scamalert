import html
import re
from typing import Dict, List, Tuple

import streamlit as st

st.set_page_config(page_title="ScamAlert", page_icon="🛡️", layout="wide")

st.markdown(
    """
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
    --blue-soft: #EFF6FF;
    --blue-line: #BFDBFE;
    --blue-text: #1D4ED8;
}
html, body, [class*="css"] { font-family: "Inter", sans-serif; }
.stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
    background-color: var(--bg) !important;
    background-image: none !important;
}
.block-container {
    max-width: 1080px;
    padding-top: 1.2rem;
    padding-bottom: 3rem;
    position: relative;
    z-index: 1;
}
h1, h2, h3, h4, p, label, div, span { color: var(--ink); }
.hero-card, .panel-card {
    background: transparent;
    border: none;
    border-top: 1px solid var(--line);
    border-radius: 0;
    padding: 1.25rem 0 1.1rem 0;
    box-shadow: none;
}
.hero-card { border-top: 3px solid var(--red); margin-bottom: 1.1rem; }
.title-main {
    font-size: 2.9rem;
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
    border: 1px solid #EEF0F3;
    border-radius: 14px;
    padding: 1rem;
    height: 100%;
    box-shadow: none;
}
.module-card {
    background: #FFFFFF;
    border: 1px solid #EEF0F3;
    border-radius: 16px;
    padding: 1.05rem;
    height: 100%;
}
.module-title { font-size: 1.05rem; font-weight: 850; margin-bottom: 0.2rem; }
.module-caption { font-size: 0.9rem; color: var(--muted); line-height: 1.45; margin-bottom: 0.8rem; }
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
.tag-blue { background: var(--blue-soft); border-color: var(--blue-line); color: var(--blue-text); }
.tag-neutral { background: #F3F4F6; border-color: #E5E7EB; }
.stTextArea textarea {
    background: #FFFFFF !important;
    color: var(--ink) !important;
    border: 1px solid #E5E7EB !important;
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
    background: #FCFCFD;
    border: none;
    border-top: 1px solid var(--line);
    border-radius: 0;
    padding: 1rem 0 0 0;
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
.pathway {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    gap: 8px;
    margin-top: 0.7rem;
}
.move-step {
    background: #FFFFFF;
    border: 1px solid #FECACA;
    color: var(--red-dark);
    border-radius: 14px;
    padding: 0.55rem 0.75rem;
    font-size: 0.92rem;
    font-weight: 750;
}
.move-arrow {
    color: var(--muted);
    font-weight: 900;
}
.move-box {
    border-left: 4px solid var(--red);
    background: #FFFFFF;
    border-radius: 12px;
    padding: 0.85rem 0.95rem;
    margin: 0.65rem 0;
    border-top: 1px solid #EEF0F3;
    border-right: 1px solid #EEF0F3;
    border-bottom: 1px solid #EEF0F3;
}
.move-name { font-weight: 850; margin-bottom: 0.25rem; }
.move-function { color: var(--muted); font-size: 0.93rem; line-height: 1.45; }
.small-muted { color: var(--muted); font-size: 0.9rem; line-height: 1.45; }
.evidence-text {
    background: #FFFFFF;
    border: 1px solid #EEF0F3;
    border-radius: 14px;
    padding: 1rem;
    line-height: 1.6;
}
</style>
""",
    unsafe_allow_html=True,
)

# -----------------------------------------------------------------------------
# Dataset prototaip berbentuk pola: dibina daripada data ScamSpeech, ScamEmotion
# dan tambahan data ScamMove supaya aplikasi mempunyai tiga enjin analisis.
# -----------------------------------------------------------------------------
DIRECT_PATTERNS: Dict[str, Tuple[int, str]] = {
    r"berikan otp|masukkan otp|kongsi otp|hantar otp|kod otp": (35, "permintaan OTP"),
    r"kata laluan|password|pin keselamatan": (35, "permintaan kata laluan/PIN"),
    r"bayar caj proses|caj proses|bayar caj pengesahan|caj pengesahan": (30, "bayar caj proses/pengesahan"),
    r"bayar yuran|yuran pendaftaran|bayaran deposit|deposit rm": (28, "bayaran pendahuluan"),
    r"pindahkan wang|transfer wang|transfer rm|buat bayaran|bayar rm": (35, "arahan pindahan wang"),
    r"daftar sekarang|aktifkan akaun|sahkan akaun": (20, "arahan segera mendaftar/mengesahkan"),
    r"klik pautan|tekan pautan|buka pautan|link di bawah": (22, "arahan menekan pautan"),
    r"hantar kad pengenalan|nombor akaun|maklumat bank": (35, "permintaan data peribadi/kewangan"),
    r"akaun.*dibekukan|akaun.*disekat|akaun.*ditutup": (35, "ancaman akaun dibekukan/disekat"),
}

INDIRECT_PATTERNS: Dict[str, Tuple[int, str]] = {
    r"jika gagal|kalau gagal|sekiranya gagal|jika tidak": (18, "ancaman tersirat"),
    r"segera|sekarang|serta-merta|akhir hari ini": (12, "desakan masa"),
    r"24 jam|15 minit|30 minit|hari ini|sebelum jam|pukul \d+": (17, "had masa"),
    r"slot terhad|tinggal \d+|kuota terhad|tempat terhad": (18, "kelangkaan palsu"),
    r"risiko rendah|jamin|dijamin|tanpa risiko": (18, "jaminan tidak realistik"),
    r"pulangan tinggi|untung besar|modal.*jadi|wang.*dilepaskan|keuntungan harian": (22, "janji keuntungan"),
    r"terpilih|layak menerima|permohonan.*diluluskan|peluang khas": (15, "peluang eksklusif"),
}

EMOTION_PATTERNS: Dict[str, List[str]] = {
    "E1 Ketakutan": [
        r"akaun.*dibekukan", r"akaun.*disekat", r"disenarai hitam", r"aktiviti luar biasa",
        r"tindakan undang-undang", r"polis", r"pihak berkuasa", r"kehilangan akses",
    ],
    "E2 Kecemasan": [r"segera", r"sekarang", r"24 jam", r"15 minit", r"30 minit", r"hari ini", r"sebelum jam"],
    "E3 Harapan Keuntungan": [r"untung", r"ganjaran", r"bonus", r"pulangan", r"diluluskan", r"hadiah", r"wang.*dilepaskan"],
    "E4 Kepercayaan Palsu": [r"bank", r"pegawai", r"rasmi", r"syarikat berdaftar", r"lesen", r"invois", r"suruhanjaya"],
    "E5 Simpati": [r"bantu", r"sumbangan", r"anak sakit", r"kesusahan", r"derma", r"kecemasan keluarga"],
    "E6 Rasa Bersalah": [r"jika anda tidak", r"anda punca", r"tolong saya", r"jangan kecewakan", r"harap kerjasama"],
}

CONTROL_PATTERNS: Dict[str, str] = {
    r"melalui aplikasi rasmi|aplikasi rasmi": "saluran rasmi",
    r"tertakluk pada terma dan syarat|terma dan syarat": "terma dan syarat",
    r"jangan kongsi otp|tidak berkongsi otp|jangan berkongsi otp": "peringatan keselamatan OTP",
    r"jangan kongsi kata laluan|jangan berkongsi kata laluan": "peringatan keselamatan kata laluan",
    r"hubungi emel rasmi|emel rasmi|alamat emel rasmi": "emel rasmi",
    r"akaun syarikat berdaftar": "akaun syarikat berdaftar",
    r"invois rasmi|invois yang dilampirkan|resit rasmi": "invois/resit rasmi",
    r"saluran rasmi|laman rasmi|portal rasmi|kaunter rasmi": "saluran rasmi",
    r"semak dahulu|membuat semakan|semakan melalui": "semakan rasmi",
}

SCAMMOVE_PATTERNS = [
    {
        "code": "M1",
        "name": "Bina Kepercayaan",
        "function": "Mewujudkan kredibiliti awal melalui penyamaran autoriti, bukti sosial atau imej institusi.",
        "patterns": [r"bank", r"pegawai", r"wakil", r"syarikat berdaftar", r"lesen", r"suruhanjaya", r"testimoni", r"ramai pelanggan"],
        "weight": 16,
    },
    {
        "code": "M2",
        "name": "Tawar Peluang",
        "function": "Menarik minat pengguna dengan tawaran bantuan, pinjaman, kerja, hadiah atau pelaburan khas.",
        "patterns": [r"terpilih", r"layak", r"peluang", r"bantuan", r"pinjaman", r"pelaburan", r"program khas", r"hadiah"],
        "weight": 16,
    },
    {
        "code": "M3",
        "name": "Janji Ganjaran",
        "function": "Membina harapan melalui janji pulangan, bonus, keuntungan atau wang yang akan dilepaskan.",
        "patterns": [r"pulangan", r"untung", r"bonus", r"modal.*jadi", r"dijamin", r"tanpa risiko", r"wang.*dilepaskan", r"keuntungan"],
        "weight": 20,
    },
    {
        "code": "M4",
        "name": "Tekanan Masa",
        "function": "Mendesak pengguna supaya bertindak cepat tanpa semakan lanjut.",
        "patterns": [r"segera", r"sekarang", r"hari ini", r"slot terhad", r"tinggal \d+", r"sebelum jam", r"24 jam", r"15 minit", r"30 minit"],
        "weight": 18,
    },
    {
        "code": "M5",
        "name": "Arahan Bayaran/Data",
        "function": "Menggerakkan pengguna untuk membayar, menekan pautan atau menyerahkan data sensitif.",
        "patterns": [r"\bbayar\b", r"buat bayaran", r"bayaran deposit", r"bayaran pengesahan", r"caj proses", r"caj pengesahan", r"deposit", r"transfer", r"pindahan", r"otp", r"kata laluan", r"kad pengenalan", r"nombor akaun", r"klik pautan", r"tekan pautan"],
        "weight": 26,
    },
    {
        "code": "M6",
        "name": "Penguncian Mangsa",
        "function": "Menghalang mangsa daripada berundur melalui ancaman, kerahsiaan atau risiko kehilangan peluang.",
        "patterns": [r"jangan batalkan", r"jangan beritahu", r"rahsia", r"sulit", r"akaun.*dibekukan", r"akaun.*disekat", r"disenarai hitam", r"tindakan undang-undang", r"terlepas peluang"],
        "weight": 24,
    },
]

SCAMMOVE_CONTROL_PATTERNS: Dict[str, str] = {
    r"semak.*saluran rasmi|saluran rasmi|laman rasmi|aplikasi rasmi|portal rasmi": "Kawalan: semakan melalui saluran rasmi",
    r"jangan.*otp|tidak.*otp|jangan.*kata laluan|tidak.*kata laluan": "Kawalan: peringatan keselamatan data",
    r"terma dan syarat|invois rasmi|resit rasmi|emel rasmi|kaunter rasmi": "Kawalan: bukti transaksi sah",
    r"tidak perlu bayaran pendahuluan|tiada bayaran pendahuluan|tiada caj proses": "Kawalan: tiada desakan bayaran awal",
}

SCAMMOVE_SCAM_EXAMPLES = [
    "Bina Kepercayaan → Tawar Peluang → Janji Ganjaran → Tekanan Masa → Arahan Bayaran",
    "Penyamaran Autoriti → Ancaman Akaun → Tekanan Masa → Permintaan OTP",
    "Tawar Bantuan → Kelulusan Palsu → Caj Proses → Penguncian Mangsa",
]

SCAMMOVE_CONTROL_EXAMPLES = [
    "Maklumat Rasmi → Terma dan Syarat → Saluran Semakan",
    "Peringatan Keselamatan → Jangan Kongsi OTP → Hubungi Saluran Rasmi",
    "Invois Rasmi → Akaun Syarikat Berdaftar → Resit Melalui Emel Rasmi",
]


def risk_level(score: int) -> str:
    if score <= 24:
        return "Rendah"
    if score <= 49:
        return "Sederhana"
    if score <= 74:
        return "Tinggi"
    return "Sangat Tinggi"


def badge_class(level: str) -> str:
    return {
        "Rendah": "badge-low",
        "Sederhana": "badge-medium",
        "Tinggi": "badge-high",
        "Sangat Tinggi": "badge-vhigh",
    }.get(level, "badge-medium")


def risk_meter(score: int) -> str:
    score = max(0, min(100, int(score)))
    return f"""
    <div class="meter-wrap">
        <div class="meter-score">{score}/100</div>
        <div class="meter-zones"><span class="meter-pointer" style="left:{score}%;"></span></div>
        <div class="meter-scale"><span>0</span><span>25</span><span>50</span><span>75</span><span>100</span></div>
    </div>
    """


def unique(items: List[str]) -> List[str]:
    return list(dict.fromkeys(items))


def find_matches(text: str, pattern_dict: Dict[str, object]):
    labels, score = [], 0
    for pattern, payload in pattern_dict.items():
        if re.search(pattern, text, flags=re.I):
            if isinstance(payload, tuple):
                weight, label = payload
                score += weight
                labels.append(label)
            else:
                labels.append(str(payload))
    return score, unique(labels)


def analyse_emotions(text: str):
    emotions, score = [], 0
    for emotion, patterns in EMOTION_PATTERNS.items():
        if any(re.search(p, text, flags=re.I) for p in patterns):
            emotions.append(emotion)
            score += 18
    if "E1 Ketakutan" in emotions and "E2 Kecemasan" in emotions:
        score += 12
    if "E3 Harapan Keuntungan" in emotions and "E4 Kepercayaan Palsu" in emotions:
        score += 8
    return min(score, 100), emotions


def analyse_moves(text: str):
    detected = []
    move_score = 0
    for move in SCAMMOVE_PATTERNS:
        matched_patterns = [p for p in move["patterns"] if re.search(p, text, flags=re.I)]
        if matched_patterns:
            detected.append(move)
            move_score += int(move["weight"])

    control_score, control_labels = find_matches(text, {k: (10, v) for k, v in SCAMMOVE_CONTROL_PATTERNS.items()})

    move_codes = [m["code"] for m in detected]
    if len(detected) >= 4:
        move_score += 16
    if "M4" in move_codes and "M5" in move_codes:
        move_score += 18
    if all(code in move_codes for code in ["M1", "M3", "M4", "M5"]):
        move_score += 18
    if "M5" in move_codes and "M6" in move_codes:
        move_score += 12

    move_score = max(0, min(100, move_score - control_score))
    return move_score, detected, control_labels


def match_phrase(score: int, has_control: bool) -> str:
    if score >= 60:
        return "Lebih hampir kepada data penipuan siber"
    if has_control and score <= 40:
        return "Lebih hampir kepada data kawalan sepadan"
    return "Memerlukan semakan lanjut"


def classify_threat(text: str, result: dict) -> str:
    if re.search(r"otp|kata laluan|password|pin|akaun.*dibekukan|akaun.*disekat", text, flags=re.I):
        return "Penyamaran autoriti / pengambilalihan akaun"
    if re.search(r"pelaburan|pulangan|untung|modal.*jadi|keuntungan", text, flags=re.I):
        return "Penipuan pelaburan / pulangan palsu"
    if re.search(r"pinjaman|bantuan|dana|diluluskan|caj proses|caj pengesahan", text, flags=re.I):
        return "Penipuan pinjaman atau bantuan palsu"
    if re.search(r"kerja|jawatan|gaji|komisen|tugasan", text, flags=re.I):
        return "Penipuan kerja / komisen palsu"
    if result["overall_score"] >= 60:
        return "Mesej berisiko tinggi dengan unsur manipulasi"
    return "Tiada kategori ancaman yang jelas"


def control_message(category: str) -> str:
    if "pelaburan" in category.lower():
        return "Mesej pelaburan yang sah biasanya menyediakan maklumat syarikat, risiko, dokumen rasmi dan saluran semakan tanpa menjanjikan keuntungan segera."
    if "pinjaman" in category.lower() or "bantuan" in category.lower():
        return "Mesej bantuan atau pinjaman yang sah tidak mendesak bayaran caj proses sebelum wang dilepaskan dan biasanya merujuk portal rasmi."
    if "akaun" in category.lower() or "autoriti" in category.lower():
        return "Amaran keselamatan yang sah lazimnya mengingatkan pengguna supaya tidak berkongsi OTP, kata laluan atau PIN dengan sesiapa."
    return "Mesej yang sah biasanya memberi ruang semakan, menyatakan saluran rasmi dan tidak memaksa bayaran atau tindakan segera."


def move_pathway_html(moves: List[dict]) -> str:
    if not moves:
        return '<div class="small-muted">Tiada urutan gerakan scam yang ketara.</div>'
    chunks = []
    for i, move in enumerate(moves):
        if i > 0:
            chunks.append('<span class="move-arrow">→</span>')
        chunks.append(f'<span class="move-step">{html.escape(move["name"])}</span>')
    return '<div class="pathway">' + ''.join(chunks) + '</div>'


def tag_html(items: List[str], cls: str) -> str:
    safe_items = [html.escape(x) for x in (items or ["Tiada petanda yang ketara"])]
    return '<div class="tag-wrap">' + ''.join([f'<span class="tag {cls}">{t}</span>' for t in safe_items]) + '</div>'


def analyse_text(message: str):
    text = message.strip().lower()
    direct_score, direct_labels = find_matches(text, DIRECT_PATTERNS)
    indirect_score, indirect_labels = find_matches(text, INDIRECT_PATTERNS)
    control_score, control_labels = find_matches(text, {k: (8, v) for k, v in CONTROL_PATTERNS.items()})
    emotion_score, emotions = analyse_emotions(text)
    move_score, moves, move_control_labels = analyse_moves(text)

    speech_score = max(0, min(100, direct_score + indirect_score - control_score))
    overall_score = int(min(100, round(speech_score * 0.35 + emotion_score * 0.30 + move_score * 0.35)))

    has_otp = bool(re.search(r"otp|kata laluan|password|pin", text, flags=re.I))
    has_account_threat = bool(re.search(r"akaun.*dibekukan|akaun.*disekat|akaun.*ditutup", text, flags=re.I))
    has_time_pressure = bool(re.search(r"segera|sekarang|24 jam|15 minit|30 minit|5 minit|jika gagal|kalau gagal", text, flags=re.I))
    has_money_request = bool(re.search(r"bayar|caj proses|caj pengesahan|yuran pendaftaran|deposit|transfer|pindahan", text, flags=re.I))
    has_unrealistic_gain = bool(re.search(r"modal.*jadi|untung|pulangan tinggi|dijamin|bonus|hadiah|wang.*dilepaskan", text, flags=re.I))
    has_benefit_release = bool(re.search(r"wang.*dilepaskan|permohonan.*diluluskan|pinjaman|bantuan|dana", text, flags=re.I))

    # Peraturan kritikal prototaip: kombinasi data sensitif, tekanan masa,
    # ancaman akaun, bayaran awal dan janji tidak realistik dikategorikan tinggi.
    if has_otp and has_account_threat and has_time_pressure:
        speech_score = max(speech_score, 90)
        emotion_score = max(emotion_score, 82)
        move_score = max(move_score, 90)
        overall_score = max(overall_score, 94)
    elif has_otp and has_time_pressure:
        speech_score = max(speech_score, 84)
        move_score = max(move_score, 84)
        overall_score = max(overall_score, 86)
    elif has_money_request and has_time_pressure and has_unrealistic_gain:
        speech_score = max(speech_score, 76)
        emotion_score = max(emotion_score, 70)
        move_score = max(move_score, 86)
        overall_score = max(overall_score, 84)
    elif has_money_request and has_account_threat:
        speech_score = max(speech_score, 78)
        move_score = max(move_score, 84)
        overall_score = max(overall_score, 84)
    elif has_money_request and has_benefit_release:
        speech_score = max(speech_score, 74)
        move_score = max(move_score, 76)
        overall_score = max(overall_score, 76)

    if direct_labels and indirect_labels:
        speech_type = "Gabungan Lakuan Pertuturan Langsung dan Tidak Langsung"
    elif direct_labels:
        speech_type = "Lakuan Pertuturan Langsung"
    elif indirect_labels:
        speech_type = "Lakuan Pertuturan Tidak Langsung"
    else:
        speech_type = "Tiada pola lakuan yang ketara"

    overall_level = risk_level(overall_score)
    result = {
        "overall_score": overall_score,
        "overall_level": overall_level,
        "speech_score": speech_score,
        "speech_level": risk_level(speech_score),
        "speech_type": speech_type,
        "speech_match": match_phrase(speech_score, bool(control_labels)),
        "emotion_score": emotion_score,
        "emotion_level": risk_level(emotion_score),
        "emotion_match": match_phrase(emotion_score, bool(control_labels)),
        "move_score": move_score,
        "move_level": risk_level(move_score),
        "move_match": match_phrase(move_score, bool(move_control_labels)),
        "emotions": emotions,
        "moves": moves,
        "direct_phrases": direct_labels,
        "indirect_phrases": indirect_labels,
        "emotion_phrases": emotions,
        "control_phrases": unique(control_labels + move_control_labels),
    }
    result["threat_category"] = classify_threat(text, result)
    result["overall_match"] = match_phrase(overall_score, bool(result["control_phrases"]))
    result["control_message"] = control_message(result["threat_category"])
    return result


st.markdown(
    """
<div class="hero-card">
  <div class="title-main">ScamAlert</div>
  <p class="subtitle-main">ScamAlert ialah sistem amaran awal penipuan siber berasaskan Kecerdasan Buatan (AI) yang menganalisis corak bahasa, manipulasi emosi dan gerakan strategi pujukan dalam mesej digital sebelum pengguna berkongsi maklumat peribadi, menekan pautan atau membuat transaksi kewangan.</p>
</div>
""",
    unsafe_allow_html=True,
)

st.markdown('<div class="panel-card">', unsafe_allow_html=True)
st.markdown("## Semak Mesej Mencurigakan")
st.markdown('<p class="helper-text">Tampal mesej WhatsApp, Telegram, SMS atau e-mel yang mencurigakan untuk semakan awal.</p>', unsafe_allow_html=True)
message = st.text_area("Mesej", label_visibility="collapsed", placeholder="Tampal mesej di sini…", key="message_input")
check = st.button("Semak Risiko")
st.markdown('</div>', unsafe_allow_html=True)

if check and message.strip():
    result = analyse_text(message)

    st.markdown('<div class="panel-card">', unsafe_allow_html=True)
    st.markdown("## Keputusan Keseluruhan")
    c1, c2, c3 = st.columns([1.1, 0.9, 1.2])
    with c1:
        st.markdown(
            f'<div class="result-card"><div class="result-label">Skor Risiko Keseluruhan</div>{risk_meter(result["overall_score"])}<div class="result-note">Gabungan ScamSpeech, ScamEmotion dan ScamMove.</div></div>',
            unsafe_allow_html=True,
        )
    with c2:
        level = result["overall_level"]
        st.markdown(
            f'<div class="result-card"><div class="result-label">Tahap Risiko</div><div class="badge {badge_class(level)}">{level}</div><div class="result-note">{html.escape(result["overall_match"])}</div></div>',
            unsafe_allow_html=True,
        )
    with c3:
        st.markdown(
            f'<div class="result-card"><div class="result-label">Kategori Ancaman</div><div class="result-note" style="color:#111827;font-weight:750;">{html.escape(result["threat_category"])}</div><div class="result-note">Keputusan ini ialah amaran awal, bukan pengesahan rasmi.</div></div>',
            unsafe_allow_html=True,
        )
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="panel-card">', unsafe_allow_html=True)
    st.markdown("## Tiga Enjin Analisis")
    s_col, e_col, m_col = st.columns(3)
    with s_col:
        st.markdown(
            f"""
            <div class="module-card">
                <div class="module-title">ScamSpeech</div>
                <div class="module-caption">Menganalisis lakuan pertuturan langsung dan tidak langsung.</div>
                {risk_meter(result["speech_score"])}
                <div class="badge {badge_class(result["speech_level"])}">{result["speech_level"]}</div>
                <div class="result-note">{html.escape(result["speech_type"])}</div>
                <div class="result-note">{html.escape(result["speech_match"])}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with e_col:
        emo_text = ", ".join(result["emotions"]) if result["emotions"] else "Tiada pencetus emosi yang ketara"
        st.markdown(
            f"""
            <div class="module-card">
                <div class="module-title">ScamEmotion</div>
                <div class="module-caption">Mengesan pencetus emosi 6E yang digunakan untuk memujuk atau menekan pengguna.</div>
                {risk_meter(result["emotion_score"])}
                <div class="badge {badge_class(result["emotion_level"])}">{result["emotion_level"]}</div>
                <div class="result-note">{html.escape(emo_text)}</div>
                <div class="result-note">{html.escape(result["emotion_match"])}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with m_col:
        st.markdown(
            f"""
            <div class="module-card">
                <div class="module-title">ScamMove</div>
                <div class="module-caption">Memetakan gerakan strategi scam daripada bina kepercayaan kepada arahan tindakan.</div>
                {risk_meter(result["move_score"])}
                <div class="badge {badge_class(result["move_level"])}">{result["move_level"]}</div>
                <div class="result-note">{html.escape(result["move_match"])}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="panel-card">', unsafe_allow_html=True)
    st.markdown("## ScamMove Mapper")
    st.markdown('<p class="helper-text">Paparan ini menunjukkan laluan gerakan wacana yang membentuk strategi penipuan.</p>', unsafe_allow_html=True)
    st.markdown(move_pathway_html(result["moves"]), unsafe_allow_html=True)
    if result["moves"]:
        for move in result["moves"]:
            st.markdown(
                f"""
                <div class="move-box">
                    <div class="move-name">{html.escape(move["code"])} · {html.escape(move["name"])}</div>
                    <div class="move-function">{html.escape(move["function"])}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="panel-card">', unsafe_allow_html=True)
    st.markdown("## Frasa dan Petanda Dikesan")
    sections = [
        ("ScamSpeech: Frasa Lakuan Langsung", result["direct_phrases"], "tag-red"),
        ("ScamSpeech: Frasa Lakuan Tidak Langsung", result["indirect_phrases"], "tag-yellow"),
        ("ScamEmotion: Pencetus Emosi", result["emotion_phrases"], "tag-blue"),
        ("ScamMove: Gerakan Strategi", [m["name"] for m in result["moves"]], "tag-red"),
        ("Data Kawalan / Isyarat Sah", result["control_phrases"], "tag-green"),
    ]
    for title, tags, cls in sections:
        st.markdown(f"#### {title}")
        st.markdown(tag_html(tags, cls), unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="panel-card">', unsafe_allow_html=True)
    st.markdown("## Padanan Data Kawalan Sepadan")
    st.markdown(f'<div class="subtle-note">{html.escape(result["control_message"])}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    guidance = {
        "Rendah": "Risiko rendah dikesan. Namun begitu, pengguna masih digalakkan menyemak kesahihan mesej melalui saluran rasmi.",
        "Sederhana": "Terdapat beberapa ciri mencurigakan. Semak sumber mesej dan elakkan membuat bayaran, menekan pautan atau berkongsi maklumat peribadi sebelum pengesahan lanjut.",
        "Tinggi": "Mesej menunjukkan ciri manipulatif yang kuat. Jangan berkongsi maklumat peribadi, jangan membuat bayaran dan semak melalui saluran rasmi.",
        "Sangat Tinggi": "Mesej ini menunjukkan risiko yang sangat tinggi. Jangan kongsi OTP, kata laluan atau PIN, jangan tekan pautan, jangan buat bayaran dan segera semak dengan pihak rasmi.",
    }
    st.markdown('<div class="panel-card">', unsafe_allow_html=True)
    st.markdown("## Cadangan Tindakan Selamat")
    st.markdown(f'<div class="subtle-note">{html.escape(guidance[result["overall_level"]])}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    with st.expander("Lihat asas data ScamMove prototaip"):
        st.markdown("**Contoh data penipuan ScamMove**")
        for item in SCAMMOVE_SCAM_EXAMPLES:
            st.markdown(f"- {item}")
        st.markdown("**Contoh data kawalan ScamMove**")
        for item in SCAMMOVE_CONTROL_EXAMPLES:
            st.markdown(f"- {item}")

    st.markdown('<div class="panel-card">', unsafe_allow_html=True)
    st.markdown("## Penafian")
    st.markdown('<div class="subtle-note">ScamAlert ialah prototaip amaran awal dan tidak menggantikan semakan rasmi. Pengguna digalakkan menyemak kesahihan mesej melalui saluran rasmi sebelum berkongsi maklumat peribadi, menekan pautan atau membuat sebarang transaksi kewangan.</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
elif check and not message.strip():
    st.warning("Sila masukkan mesej terlebih dahulu.")
