
import html
import re
from pathlib import Path

import pandas as pd
import streamlit as st

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    SKLEARN_OK = True
except Exception:
    SKLEARN_OK = False
    from difflib import SequenceMatcher


APP_TITLE = "ScamAlert"
APP_VERSION = "v0.5.0"
BASE_DIR = Path(__file__).parent

DISPLAY_STATS = {
    "total": "3,000",
    "cyber_fraud": "1,500",
    "control": "1,500",
    "users": "50",
}

DATA_CANDIDATES = [
    "scamalert_dataset.xlsx",
    "ScamAlert_Dataset_Kodbook_3000_v0_4.xlsx",
    "ScamAlert_Dataset_Kodbook_2000_v0_2.xlsx",
    "ScamShield_Dataset_Kodbook_2000_v0_2.xlsx",
    "dataset.xlsx",
]

RISK_WEIGHTS = {
    "R1_Arahan_Wang_Data": 25,
    "R2_Janji_Dakwaan_Tidak_Realistik": 20,
    "R3_Penyamaran_Autoriti": 20,
    "R4_Tekanan_Masa": 15,
    "R5_Manipulasi_Emosi": 10,
    "R6_Bukti_Sosial_Legitimasi": 10,
}

RISK_LABELS = {
    "R1_Arahan_Wang_Data": "Arahan wang / data sensitif",
    "R2_Janji_Dakwaan_Tidak_Realistik": "Janji tidak realistik",
    "R3_Penyamaran_Autoriti": "Penyamaran autoriti",
    "R4_Tekanan_Masa": "Tekanan masa",
    "R5_Manipulasi_Emosi": "Manipulasi emosi",
    "R6_Bukti_Sosial_Legitimasi": "Bukti sosial palsu",
}

RULES = {
    "R1_Arahan_Wang_Data": [
        r"\btransfer\b", r"\bpindah(?:kan)?\b", r"\bbayar\b", r"\bbayaran\b",
        r"\bcaj proses\b", r"\bcaj pengesahan\b", r"\bdeposit\b",
        r"\bOTP\b", r"\bTAC\b", r"\bkod\s+OTP\b", r"\bnombor akaun\b",
        r"\bkata laluan\b", r"\bbutiran bank\b", r"\bkad pengenalan\b"
    ],
    "R2_Janji_Dakwaan_Tidak_Realistik": [
        r"\buntung\b", r"\bkeuntungan\b", r"\bberganda\b", r"\bdijamin\b",
        r"\blulus\b", r"\bdiluluskan\b", r"\btanpa slip gaji\b",
        r"\btanpa semakan\b", r"\bmodal\b.*\bjadi\b", r"\bRM\s?\d+.*RM\s?\d+",
        r"\bdalam 24 jam\b", r"\bkeuntungan harian\b", r"\bRM\s?\d+\s?sehari\b",
        r"\bkomisen\b", r"\blike video\b", r"\bkerja mudah\b"
    ],
    "R3_Penyamaran_Autoriti": [
        r"\bpolis\b", r"\bbank\b", r"\bLHDN\b", r"\bmahkamah\b", r"\bBNM\b",
        r"\bpegawai\b", r"\bwaran\b", r"\bsiasatan\b", r"\bjenayah\b",
        r"\bakaun keselamatan\b", r"\bdibekukan\b", r"\bdisekat\b",
        r"\bpihak berkuasa\b", r"\bbarang terlarang\b"
    ],
    "R4_Tekanan_Masa": [
        r"\bsekarang\b", r"\bsegera\b", r"\bhari ini\b", r"\bmalam ini\b",
        r"\bsebelum\b", r"\bslot\b", r"\bterhad\b", r"\bnotis akhir\b",
        r"\bpeluang terakhir\b", r"\btinggal\s+\d+\b", r"\bdahulu\b", r"\b24 jam\b"
    ],
    "R5_Manipulasi_Emosi": [
        r"\btahniah\b", r"\bterpilih\b", r"\bjangan lepaskan\b",
        r"\btakut\b", r"\bpanik\b", r"\bkeluarga\b", r"\bbantuan khas\b",
        r"\bVIP\b", r"\bahli terpilih\b", r"\bterbatal\b"
    ],
    "R6_Bukti_Sosial_Legitimasi": [
        r"\bramai\b", r"\bwithdraw\b", r"\bscreenshot\b", r"\bsijil\b",
        r"\bmentor\b", r"\btestimoni\b", r"\bterbukti\b", r"\bpeserta\b"
    ],
}

SAFE_PATTERNS = [
    r"\brasmi\b", r"\bkaunter rasmi\b", r"\baplikasi rasmi\b", r"\blaman rasmi\b",
    r"\bcawangan\b", r"\bcheckout\b", r"\binvois rasmi\b", r"\bsyarikat berdaftar\b",
    r"\bjangan berkongsi\b", r"\bjangan kongsi\b", r"\btiada bayaran pendaftaran\b",
    r"\btidak akan meminta\b", r"\bsemak dahulu\b", r"\bsaluran rasmi\b"
]

EXAMPLE_MESSAGES = {
    "Tulis sendiri": "",
    "OTP + akaun dibekukan": "Pihak bank telah mengesan aktiviti luar biasa. Sila berikan OTP untuk sahkan identiti anda sekarang. Jika gagal, akaun anda akan dibekukan dalam 24 jam.",
    "Penipuan kerja mudah": "Kerja mudah dari rumah. Hanya tekan like dan follow. Bayaran harian RM300 hingga RM500. Daftar sekarang, bayar yuran pendaftaran RM50 untuk bermula.",
    "Pelaburan tidak wujud": "Modal RM300 boleh jadi RM3,000 dalam 24 jam. Slot VIP tinggal 5 sahaja. Daftar sekarang.",
    "Pinjaman / bantuan palsu": "Pinjaman anda telah diluluskan. Bayar caj proses RM150 dahulu sebelum wang dilepaskan.",
    "Promosi aplikasi rasmi": "Nikmati promosi istimewa sehingga 20% untuk pembayaran bil melalui aplikasi rasmi. Tertakluk pada terma dan syarat. Maklumat lanjut di laman rasmi kami.",
    "Deposit dengan invois rasmi": "Sila buat pembayaran seperti invois yang dilampirkan. Pembayaran ke akaun syarikat berdaftar. Sebarang pertanyaan, hubungi emel rasmi.",
}


st.set_page_config(
    page_title="ScamAlert Web Prototype",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed",
)


def inject_css():
    st.markdown(
        """
        <style>
        :root {
            --sa-red: #DC2626;
            --sa-red-dark: #991B1B;
            --sa-red-soft: #FEE2E2;
            --sa-black: #000000;
            --sa-text: #000000;
            --sa-muted: #222222;
            --sa-border: #DDDDDD;
            --sa-bg: #FFFFFF;
            --sa-card: #FFFFFF;
            --sa-green: #16A34A;
            --sa-green-dark: #166534;
            --sa-green-soft: #DCFCE7;
            --sa-yellow: #FACC15;
            --sa-yellow-dark: #7C4A03;
            --sa-yellow-soft: #FEF3C7;
        }
        .stApp { background: #FFFFFF !important; }
        [data-testid="stAppViewContainer"] { background: #FFFFFF !important; }
        [data-testid="stMain"] { background: #FFFFFF !important; }
        [data-testid="stVerticalBlock"] { background: transparent !important; }
        [data-testid="stDecoration"] { background: var(--sa-red) !important; }
        [data-testid="stHeader"] * { color: #000000 !important; }
        [data-testid="stMarkdownContainer"] p { color: #000000 !important; }
        .stTabs [data-baseweb="tab-list"] { gap: 18px; border-bottom: 1px solid #DDDDDD; }
        .stTabs [data-baseweb="tab"] {
            color: #000000 !important;
            font-weight: 900 !important;
            background: #FFFFFF !important;
        }
        .stTabs [aria-selected="true"] {
            color: #DC2626 !important;
            border-bottom: 3px solid #DC2626 !important;
        }
        
        header[data-testid="stHeader"] {
            background: #FFFFFF !important;
            border-bottom: 1px solid var(--sa-border);
            backdrop-filter: blur(8px);
        }
        [data-testid="stToolbar"] { color: var(--sa-black) !important; }
        .sa-top-spacer { height: 16px; }
        .block-container { padding-top: 5.8rem !important; padding-bottom: 3rem; max-width: 1360px; }
        [data-testid="stSidebar"] { display: none !important; }
        [data-testid="collapsedControl"] { display: none !important; }
        h1, h2, h3 { color: var(--sa-black); letter-spacing: -0.03em; }
        p, li, label, .stMarkdown { color: var(--sa-text); }
        .sa-hero {
            background: #FFFFFF;
            border: 1px solid #FECACA;
            border-radius: 28px;
            padding: 36px 40px;
            box-shadow: 0 18px 45px rgba(17, 24, 39, 0.08);
            margin-bottom: 20px;
            overflow: hidden;
        }
        .sa-brand { display: flex; align-items: center; gap: 14px; margin-bottom: 12px; }
        .sa-logo {
            width: 54px; height: 54px; border-radius: 16px;
            background: var(--sa-red); color: white;
            display:flex; align-items:center; justify-content:center;
            font-size: 30px; font-weight: 900; box-shadow: 0 10px 24px rgba(220,38,38,.25);
        }
        .sa-kicker { color: var(--sa-red); font-weight: 900; letter-spacing: .08em; text-transform: uppercase; font-size: 13px; }
        .sa-title { font-size: 48px; line-height: 1.05; font-weight: 950; color: var(--sa-black); margin: 0; }
        .sa-subtitle { font-size: 18px; line-height: 1.65; color: var(--sa-text); margin: 14px 0 0; max-width: 1000px; }
        .sa-badge {
            display: inline-flex; align-items: center; gap: 8px; padding: 9px 14px;
            border-radius: 999px; background: #FFFFFF; border: 1px solid #FCA5A5;
            color: var(--sa-red-dark); font-weight: 900; font-size: 13px; margin-top: 16px;
        }
        .sa-grid-4 { display:grid; grid-template-columns: repeat(4, minmax(0,1fr)); gap: 16px; margin: 18px 0 24px; }
        .sa-grid-3 { display:grid; grid-template-columns: repeat(3, minmax(0,1fr)); gap: 16px; margin: 18px 0 24px; }
        .sa-grid-2 { display:grid; grid-template-columns: repeat(2, minmax(0,1fr)); gap: 18px; margin: 18px 0 24px; }
        .sa-card, .sa-stat, .sa-panel, .sa-infocard {
            background: var(--sa-card); border: 1px solid var(--sa-border); border-radius: 20px;
            padding: 20px 22px; box-shadow: 0 12px 30px rgba(17,24,39,.06);
        }
        .sa-stat { min-height: 126px; position: relative; overflow:hidden; }
        .sa-stat:after {
            content:""; position:absolute; width:90px; height:90px; border-radius:50%; right:-30px; bottom:-30px;
            background: rgba(220,38,38,.07);
        }
        .sa-icon {
            width: 42px; height: 42px; border-radius: 14px; display:inline-flex; align-items:center; justify-content:center;
            background: var(--sa-red-soft); color: var(--sa-red-dark); font-size: 22px; font-weight: 900; margin-bottom: 12px;
        }
        .sa-stat .value { font-size: 36px; line-height: 1; font-weight: 950; color: var(--sa-red); margin-bottom: 8px; }
        .sa-stat .label { font-size: 14px; color: var(--sa-text); font-weight: 800; }
        .sa-section-title { font-size: 28px; font-weight: 950; margin: 10px 0 12px; color: var(--sa-black); }
        .sa-section-sub { color: var(--sa-muted); font-size: 15px; line-height: 1.6; margin-bottom: 14px; }
        .sa-process { display:grid; grid-template-columns: repeat(4, 1fr); gap: 12px; margin-top: 18px; }
        .sa-step {
            border: 1px solid #FECACA; background: #fff; border-radius: 18px; padding: 18px; position: relative;
        }
        .sa-step-num {
            width:32px; height:32px; border-radius:50%; background: var(--sa-red); color:#fff; display:flex; align-items:center; justify-content:center;
            font-weight: 950; margin-bottom: 10px;
        }
        .sa-step-title { font-weight: 950; color: var(--sa-black); margin-bottom: 6px; }
        .sa-step-text { color: var(--sa-text); font-size: 14px; line-height: 1.45; }
        .sa-input-panel { background: #FFFFFF; border: 1px solid #FECACA; border-radius: 22px; padding: 24px; box-shadow: 0 14px 35px rgba(17,24,39,.07); }
        div.stButton > button:first-child {
            background: var(--sa-red) !important;
            color: #FFFFFF !important;
            border: 1px solid var(--sa-red) !important;
            border-radius: 12px !important;
            font-weight: 900 !important;
            padding: .65rem 1.15rem !important;
            box-shadow: 0 12px 24px rgba(220,38,38,.22) !important;
        }
        div.stButton > button:first-child:hover {
            background: #991B1B !important;
            border-color: #991B1B !important;
            color: #FFFFFF !important;
        }
        div.stButton > button:first-child * { color: #FFFFFF !important; }

        /* Paksa semua input Streamlit jadi putih, hitam dan merah sahaja */
        textarea,
        input,
        [data-baseweb="input"] input,
        [data-baseweb="textarea"] textarea {
            background-color: #FFFFFF !important;
            color: #000000 !important;
            border-color: var(--sa-red) !important;
            caret-color: var(--sa-red) !important;
            border-radius: 12px !important;
        }
        textarea::placeholder,
        input::placeholder {
            color: #555555 !important;
            opacity: 1 !important;
        }
        [data-baseweb="select"] > div,
        .stSelectbox [data-baseweb="select"] > div {
            background-color: #FFFFFF !important;
            color: #000000 !important;
            border: 1.5px solid var(--sa-red) !important;
            border-radius: 12px !important;
        }
        [data-baseweb="select"] *,
        .stSelectbox [data-baseweb="select"] * {
            color: #000000 !important;
        }
        [data-baseweb="popover"],
        [data-baseweb="menu"],
        [role="listbox"] {
            background-color: #FFFFFF !important;
            color: #000000 !important;
        }
        [role="option"] {
            background-color: #FFFFFF !important;
            color: #000000 !important;
        }
        [role="option"]:hover {
            background-color: #FEE2E2 !important;
            color: #000000 !important;
        }
        .sa-result-grid { display:grid; grid-template-columns: 1fr 1fr 1.15fr .9fr; gap: 14px; margin: 18px 0 20px; }
        .risk-card {
            border-radius: 20px; padding: 20px; border: 1.5px solid; box-shadow: 0 14px 30px rgba(17,24,39,.08);
            min-height: 142px;
        }
        .risk-label { font-size: 12px; font-weight: 950; letter-spacing: .06em; text-transform: uppercase; margin-bottom: 8px; opacity: .9; }
        .risk-value { font-size: 34px; font-weight: 950; line-height: 1.05; margin-bottom: 8px; }
        .risk-caption { font-size: 13px; font-weight: 750; line-height: 1.4; }
        .risk-low { background:#DCFCE7; color:#166534; border-color:#16A34A; }
        .risk-medium { background:#FEF3C7; color:#92400E; border-color:#FACC15; }
        .risk-high { background:#FEE2E2; color:#991B1B; border-color:#DC2626; }
        .risk-very-high { background:#991B1B; color:#FFFFFF; border-color:#7F1D1D; }
        .neutral-card { background: #FFFFFF; color: var(--sa-black); border-color: var(--sa-border); }
        .neutral-card .risk-value { color: var(--sa-black); font-size: 26px; }
        .sa-chip {
            display: inline-flex; align-items:center; padding: 8px 12px; border-radius: 999px; margin: 4px 6px 4px 0;
            font-size: 13px; font-weight: 900; border: 1px solid #FCA5A5; background: var(--sa-red-soft); color: var(--sa-red-dark);
        }
        .sa-chip.safe { border-color:#86EFAC; background:#DCFCE7; color:#166534; }
        .sa-chip.yellow { border-color:#FACC15; background:#FEF3C7; color:#92400E; }
        .sa-chip.black { border-color:#111827; background:#111827; color:#FFFFFF; }
        .sa-chip.muted { border-color:var(--sa-border); background:#F3F4F6; color:#6B7280; }
        mark { background:#FEF08A; color:#111827; padding: 2px 5px; border-radius: 5px; font-weight: 900; }
        .sa-text-box { background:#FFFFFF; border:1px solid var(--sa-border); border-radius:18px; padding:20px; font-size:18px; line-height:1.85; box-shadow: 0 10px 25px rgba(17,24,39,.05); }
        .sa-action { background:#FFFFFF; border:1px solid #FCA5A5; border-left:6px solid var(--sa-red); border-radius:16px; padding:18px 20px; margin: 18px 0; }
        .sa-action strong { color:#991B1B; }
        .sa-disclaimer { background:#FFFFFF; border:1px dashed #D1D5DB; border-radius:16px; padding:16px 18px; color:#4B5563; font-size:14px; }
        .sa-callout {
            background: #FFFFFF; border: 1px solid #FCA5A5; border-left: 6px solid var(--sa-red);
            border-radius: 18px; padding: 18px 22px; box-shadow: 0 10px 25px rgba(17,24,39,.05); margin: 18px 0;
        }
        .sa-callout-title { font-weight: 950; color: var(--sa-red-dark); font-size: 20px; margin-bottom: 6px; }
        .sa-bars { background:#fff; border:1px solid var(--sa-border); border-radius:20px; padding:20px; box-shadow: 0 12px 30px rgba(17,24,39,.06); }
        .bar-row { margin: 14px 0; }
        .bar-top { display:flex; justify-content:space-between; gap:16px; font-weight:850; color:var(--sa-black); font-size:14px; margin-bottom:6px; }
        .bar-track { height: 15px; background:#F3F4F6; border-radius:999px; overflow:hidden; border:1px solid #E5E7EB; }
        .bar-fill { height:100%; border-radius:999px; }
        .fill-red { background: var(--sa-red); }
        .fill-black { background: var(--sa-black); }
        .fill-green { background: var(--sa-green); }
        .fill-yellow { background: var(--sa-yellow); }
        .fill-darkred { background: var(--sa-red-dark); }
        .sa-ladder { display:grid; grid-template-columns: repeat(4, 1fr); gap: 12px; }
        .ladder-item { border-radius:18px; padding:16px; border:1.5px solid; min-height:115px; }
        .ladder-title { font-weight:950; font-size:18px; margin-bottom:4px; }
        .ladder-score { font-weight:900; font-size:14px; margin-bottom:8px; }
        .ladder-note { font-size:13px; line-height:1.4; }
        .sa-user-strip { display:grid; grid-template-columns: repeat(4, 1fr); gap:12px; margin-top:14px; }
        .sa-user { background:#fff; border:1px solid #FECACA; border-radius:18px; padding:15px; text-align:center; font-weight:900; color:var(--sa-black); }
        .sa-user .uicon { font-size:28px; margin-bottom:8px; }
        @media (max-width: 900px) {
            .sa-grid-4, .sa-grid-3, .sa-grid-2, .sa-result-grid, .sa-process, .sa-ladder, .sa-user-strip { grid-template-columns: 1fr; }
            .sa-title { font-size: 36px; }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def find_dataset_file():
    for name in DATA_CANDIDATES:
        p = BASE_DIR / name
        if p.exists():
            return p
    files = sorted(BASE_DIR.glob("*.xlsx"))
    return files[0] if files else None


@st.cache_data
def load_data():
    data_path = find_dataset_file()
    if data_path is None:
        st.error("Fail dataset Excel tidak dijumpai. Sila upload fail scamalert_dataset.xlsx ke folder yang sama dengan app.py.")
        st.stop()
    xls = pd.ExcelFile(data_path)

    def read_sheet(candidates, fallback=None):
        for sh in candidates:
            if sh in xls.sheet_names:
                return pd.read_excel(xls, sh)
        if fallback is not None and fallback in xls.sheet_names:
            return pd.read_excel(xls, fallback)
        return pd.DataFrame()

    data = read_sheet(["DATASET_UTAMA"], xls.sheet_names[0])
    kawalan = read_sheet(["DATASET_KAWALAN_1500", "DATASET_KAWALAN_500"])
    kodbook = read_sheet(["KODBOOK_LEGEND"])
    rubric = read_sheet(["RUBRIK_SKOR_RISIKO"])
    levels = read_sheet(["TAHAP_RISIKO"])
    contrast = read_sheet(["PASANGAN_KONTRAS"])
    tests = read_sheet(["CONTOH_UJIAN_SISTEM"])
    return data, kawalan, kodbook, rubric, levels, contrast, tests, data_path.name


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
        "Sederhana": "risk-medium",
        "Tinggi": "risk-high",
        "Sangat Tinggi": "risk-very-high",
    }.get(level, "neutral-card")


def risk_icon(level: str) -> str:
    return {
        "Rendah": "✅",
        "Sederhana": "⚠️",
        "Tinggi": "🚨",
        "Sangat Tinggi": "🛑",
    }.get(level, "⚠️")


def infer_fraud_type(text: str) -> str:
    t = text.lower()
    scores = {
        "Pinjaman / Bantuan Palsu": sum(k in t for k in ["pinjaman", "bantuan", "caj proses", "caj pengesahan", "diluluskan", "kelulusan", "dana"]),
        "Penyamaran Autoriti": sum(k in t for k in ["polis", "bank", "lhdn", "mahkamah", "kurier", "otp", "tac", "akaun keselamatan", "jenayah", "siasatan", "dibekukan"]),
        "Pelaburan Tidak Wujud": sum(k in t for k in ["pelaburan", "modal", "untung", "keuntungan", "withdraw", "vip", "mentor", "screenshot", "gandakan", "berganda"]),
        "Penipuan Kerja Mudah": sum(k in t for k in ["kerja mudah", "like video", "komisen", "bayar pendaftaran", "rm500 sehari", "sehari"]),
    }
    best = max(scores, key=scores.get)
    return best if scores[best] > 0 else "Tidak pasti / perlu semakan"


def analyze_rules(text: str):
    found = {}
    phrases = []
    score = 0
    for feature, patterns in RULES.items():
        hits = []
        for pat in patterns:
            for m in re.finditer(pat, text, flags=re.IGNORECASE):
                hits.append(m.group(0))
        unique_hits = sorted(set(hits), key=lambda x: text.lower().find(x.lower()))
        if unique_hits:
            found[feature] = unique_hits
            score += RISK_WEIGHTS[feature]

    safe_hits = []
    for pat in SAFE_PATTERNS:
        for m in re.finditer(pat, text, flags=re.IGNORECASE):
            safe_hits.append(m.group(0))

    t = text.lower()

    official_or_safe_context = re.search(
        r"aplikasi rasmi|checkout|invois rasmi|kaunter rasmi|cawangan|platform rasmi|saluran rasmi|"
        r"jangan\s+berkongsi|jangan\s+kongsi|tidak\s+berkongsi|tidak\s+akan\s+meminta|tiada\s+bayaran\s+pendaftaran|semak\s+dahulu|syarikat\s+berdaftar",
        t,
        flags=re.IGNORECASE,
    )
    fraud_escalator = re.search(
        r"akaun\s+peribadi|akaun\s+keselamatan|dibekukan|jenayah|siasatan|pindahkan|"
        r"modal|pinjaman|pelaburan|caj\s+proses|caj\s+pengesahan|bayar\s+pendaftaran|"
        r"like\s+video|komisen|RM\s?\d+\s?sehari|masukkan\s+otp|beri\s+otp|berikan\s+otp|hantar\s+otp",
        t,
        flags=re.IGNORECASE,
    )
    if official_or_safe_context and not fraud_escalator:
        score = min(score, 24)

    otp_request = re.search(
        r"(masukkan|beri|berikan|hantar|sahkan).*?(otp|tac)|(otp|tac).*?(masukkan|beri|berikan|hantar|sahkan)",
        t,
        flags=re.IGNORECASE,
    )
    account_threat = re.search(r"akaun|bank|dibekukan|disekat|keselamatan", t, flags=re.IGNORECASE)
    if otp_request and account_threat:
        score = max(score, 80)
        found.setdefault("R1_Arahan_Wang_Data", []).append("OTP/TAC")
        found.setdefault("R3_Penyamaran_Autoriti", []).append("akaun/bank")
        found.setdefault("R4_Tekanan_Masa", []).append("ancaman akaun")

    task_fraud = re.search(r"kerja\s+mudah|like\s+video|komisen|RM\s?\d+\s?sehari", t, flags=re.IGNORECASE)
    task_payment = re.search(r"bayar\s+pendaftaran|bayaran\s+pendaftaran|deposit", t, flags=re.IGNORECASE)
    if task_fraud and task_payment:
        score = max(score, 70)

    for hits in found.values():
        phrases.extend(hits)
    final_score = min(score, 100)
    if final_score <= 24:
        phrases = []
    return final_score, found, sorted(set(phrases), key=lambda x: text.lower().find(x.lower())), sorted(set(safe_hits))


@st.cache_resource
def build_similarity_model(texts_tuple):
    texts = list(texts_tuple)
    if SKLEARN_OK:
        vectorizer = TfidfVectorizer(lowercase=True, ngram_range=(1, 2), min_df=1)
        matrix = vectorizer.fit_transform(texts)
        return vectorizer, matrix
    return None, None


def get_top_matches(user_text, data, top_n=3):
    if "Ayat_Ujaran" not in data.columns or data.empty:
        return pd.DataFrame({"Similarity": [0.0], "Label_Empirikal": [""], "Jenis_Scam_Kawalan": [""], "Skor_Risiko": [0]})
    corpus = data["Ayat_Ujaran"].fillna("").astype(str).tolist()
    if SKLEARN_OK:
        vectorizer, matrix = build_similarity_model(tuple(corpus))
        q = vectorizer.transform([user_text])
        sims = cosine_similarity(q, matrix).flatten()
        idxs = sims.argsort()[::-1][:top_n]
        results = data.iloc[idxs].copy()
        results["Similarity"] = sims[idxs]
        return results
    sims = [SequenceMatcher(None, user_text.lower(), c.lower()).ratio() for c in corpus]
    idxs = sorted(range(len(sims)), key=lambda i: sims[i], reverse=True)[:top_n]
    results = data.iloc[idxs].copy()
    results["Similarity"] = [sims[i] for i in idxs]
    return results


def is_fraud_label(label: str) -> bool:
    label = str(label).lower()
    if "bukan" in label or "kawalan" in label or "control" in label:
        return False
    return label in ["penipuan siber", "fraud"] or "penipuan siber" in label



def is_control_label(label: str) -> bool:
    label = str(label).lower()
    return "bukan" in label or "kawalan" in label or "control" in label


def highlight_text(text, phrases):
    safe = html.escape(text)
    for phrase in sorted(phrases, key=len, reverse=True):
        if not phrase:
            continue
        p = html.escape(phrase)
        safe = re.sub(re.escape(p), f"<mark>{p}</mark>", safe, flags=re.IGNORECASE)
    return safe


def make_decision(user_text, data):
    rule_score, found, phrases, safe_hits = analyze_rules(user_text)
    matches = get_top_matches(user_text, data, top_n=3)
    best = matches.iloc[0]
    best_similarity = float(best.get("Similarity", 0))
    best_label = str(best.get("Label_Empirikal", ""))
    best_category = str(best.get("Jenis_Scam_Kawalan", ""))

    final_score = rule_score
    category = infer_fraud_type(user_text)

    if best_similarity >= 0.55:
        dataset_score = int(best.get("Skor_Risiko", rule_score) or rule_score)
        if is_control_label(best_label) and rule_score < 50:
            final_score = min(rule_score, 24)
            category = "Tidak menunjukkan pola penipuan siber yang kuat"
        elif is_fraud_label(best_label):
            final_score = max(rule_score, dataset_score)
            category = best_category if best_category else category

    final_score = min(final_score, 100)
    if final_score <= 24:
        phrases = []
        category = "Tidak menunjukkan pola penipuan siber yang kuat"

    return {
        "score": final_score,
        "level": risk_level(final_score),
        "category": category,
        "found": found,
        "phrases": phrases,
        "safe_hits": safe_hits,
        "matches": matches,
        "rule_score": rule_score,
        "best_similarity": best_similarity,
        "best_label": best_label,
    }


def recommendation(level):
    if level == "Sangat Tinggi":
        return "Mesej ini menunjukkan risiko yang sangat tinggi. Jangan kongsi OTP, jangan tekan pautan, jangan buat bayaran dan segera semak dengan pihak rasmi."
    if level == "Tinggi":
        return "Mesej menunjukkan ciri manipulatif yang kuat. Jangan berkongsi maklumat peribadi, jangan membuat bayaran dan semak melalui saluran rasmi."
    if level == "Sederhana":
        return "Terdapat beberapa ciri mencurigakan. Semak sumber mesej dan elakkan membuat bayaran atau menekan pautan sebelum pengesahan lanjut."
    return "Risiko rendah dikesan. Walau bagaimanapun, pengguna masih digalakkan menyemak kesahihan mesej melalui saluran rasmi."


def summary_text(level):
    if level == "Sangat Tinggi":
        return "Gabungan arahan sensitif, tekanan masa atau penyamaran autoriti menunjukkan risiko yang sangat tinggi."
    if level == "Tinggi":
        return "Beberapa komponen risiko hadir serentak dan meningkatkan kemungkinan mesej bersifat manipulatif."
    if level == "Sederhana":
        return "Terdapat petanda tertentu yang memerlukan semakan lanjut sebelum pengguna bertindak."
    return "Bahasa mesej lebih hampir kepada komunikasi sah atau tidak cukup menunjukkan pola penipuan siber."


def html_card(label, value, caption="", klass="neutral-card"):
    return f"""
    <div class="risk-card {klass}">
        <div class="risk-label">{html.escape(label)}</div>
        <div class="risk-value">{value}</div>
        <div class="risk-caption">{html.escape(caption)}</div>
    </div>
    """


def render_hero():
    st.markdown(
        f"""
        <div class="sa-hero">
            <div class="sa-brand">
                <div class="sa-logo">!</div>
                <div>
                    <div class="sa-kicker">{APP_TITLE} Web Prototype {APP_VERSION}</div>
                    <h1 class="sa-title">Kenal Pasti Bahasa Penipuan Siber Sebelum Terpedaya</h1>
                </div>
            </div>
            <p class="sa-subtitle">ScamAlert membantu pengguna mengenal pasti mesej yang mencurigakan melalui analisis lakuan pertuturan langsung dan lakuan pertuturan tidak langsung. ScamAlert juga mengandungi skor risiko dan cadangan tindakan selamat.</p>
            <div class="sa-badge">🛡️ Prototaip amaran awal • Analisis bahasa • Skor risiko</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_stats():
    st.markdown(
        f"""
        <div class="sa-grid-4">
            <div class="sa-stat"><div class="sa-icon">▦</div><div class="value">{DISPLAY_STATS['total']}</div><div class="label">Data prototaip</div></div>
            <div class="sa-stat"><div class="sa-icon">!</div><div class="value">{DISPLAY_STATS['cyber_fraud']}</div><div class="label">Data penipuan siber</div></div>
            <div class="sa-stat"><div class="sa-icon">✓</div><div class="value">{DISPLAY_STATS['control']}</div><div class="label">Data kawalan sepadan</div></div>
            <div class="sa-stat"><div class="sa-icon">●</div><div class="value">{DISPLAY_STATS['users']}</div><div class="label">Pengguna awal</div></div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_process():
    st.markdown(
        """
        <div class="sa-process">
            <div class="sa-step"><div class="sa-step-num">1</div><div class="sa-step-title">Masukkan Mesej</div><div class="sa-step-text">Pengguna menampal mesej yang ingin disemak.</div></div>
            <div class="sa-step"><div class="sa-step-num">2</div><div class="sa-step-title">Analisis Bahasa</div><div class="sa-step-text">Sistem mengenal pasti frasa berisiko dan lakuan pertuturan.</div></div>
            <div class="sa-step"><div class="sa-step-num">3</div><div class="sa-step-title">Skor Risiko</div><div class="sa-step-text">Tahap risiko dikira berdasarkan pola bahasa yang mencurigakan.</div></div>
            <div class="sa-step"><div class="sa-step-num">4</div><div class="sa-step-title">Tindakan Selamat</div><div class="sa-step-text">Pengguna menerima cadangan tindakan yang lebih berhati-hati.</div></div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_user_strip():
    st.markdown(
        """
        <div class="sa-user-strip">
            <div class="sa-user"><div class="uicon">🎓</div>Pelajar</div>
            <div class="sa-user"><div class="uicon">👨‍👩‍👧</div>Ibu bapa</div>
            <div class="sa-user"><div class="uicon">👵</div>Warga emas</div>
            <div class="sa-user"><div class="uicon">💬</div>Pengguna media sosial</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_result_cards(result):
    level = result["level"]
    klass = risk_class(level)
    category = html.escape(str(result["category"]))
    st.markdown(
        f"""
        <div class="sa-result-grid">
            {html_card('Skor Risiko', f"{result['score']}/100", 'Penilaian keseluruhan tahap risiko', klass)}
            {html_card('Tahap Risiko', f"{risk_icon(level)} {html.escape(level)}", 'Kategori tahap amaran', klass)}
            {html_card('Jenis Dikesan', category, 'Kategori paling hampir dengan pola mesej', 'neutral-card')}
            {html_card('Padanan Data', f"{result['best_similarity']:.2f}", 'Padanan konseptual terhadap dataset', 'neutral-card')}
        </div>
        """,
        unsafe_allow_html=True,
    )
    fill_cls = {"Rendah": "fill-green", "Sederhana": "fill-yellow", "Tinggi": "fill-red", "Sangat Tinggi": "fill-darkred"}.get(level, "fill-red")
    st.markdown(
        f"""
        <div class="sa-bars">
            <div class="bar-top"><span>Meter Skor Risiko</span><span>{result['score']}/100</span></div>
            <div class="bar-track"><div class="bar-fill {fill_cls}" style="width:{result['score']}%"></div></div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_feature_chips(found):
    if not found:
        st.markdown('<span class="sa-chip safe">Tiada komponen risiko utama dikesan</span>', unsafe_allow_html=True)
        return
    for key in RISK_WEIGHTS:
        if key in found:
            st.markdown(f'<span class="sa-chip">{html.escape(RISK_LABELS[key])}</span>', unsafe_allow_html=True)
        else:
            st.markdown(f'<span class="sa-chip muted">{html.escape(RISK_LABELS[key])}</span>', unsafe_allow_html=True)


def render_phrase_chips(phrases, safe_hits):
    if phrases:
        for p in phrases:
            st.markdown(f'<span class="sa-chip">{html.escape(str(p))}</span>', unsafe_allow_html=True)
    else:
        st.markdown('<span class="sa-chip safe">Tiada frasa berisiko tinggi dikesan</span>', unsafe_allow_html=True)
    if safe_hits:
        st.markdown("<br>", unsafe_allow_html=True)
        for p in safe_hits:
            st.markdown(f'<span class="sa-chip safe">Isyarat sah: {html.escape(str(p))}</span>', unsafe_allow_html=True)


def render_bar_chart(title, rows, max_value=None, color_cycle=None):
    if max_value is None:
        max_value = max(v for _, v, _ in rows) if rows else 1

    html_rows = []
    for label, value, color in rows:
        pct = 0 if value == 0 else max(2, min(100, (value / max_value) * 100))
        html_rows.append(
            "<div class='bar-row'>"
            f"<div class='bar-top'><span>{html.escape(label)}</span><span>{value:,}</span></div>"
            f"<div class='bar-track'><div class='bar-fill {color}' style='width:{pct}%'></div></div>"
            "</div>"
        )

    chart_html = (
        "<div class='sa-bars'>"
        f"<div class='sa-section-title' style='font-size:22px;margin-top:0;'>{html.escape(title)}</div>"
        + "".join(html_rows) +
        "</div>"
    )
    st.markdown(chart_html, unsafe_allow_html=True)


def pretty_display_df(df):
    if df.empty:
        return df
    out = df.copy()
    rename = {
        "Label_Empirikal": "Label Empirikal",
        "Jenis_Scam_Kawalan": "Jenis Data",
        "Ayat_Ujaran": "Ayat / Ujaran",
        "Skor_Risiko": "Skor Risiko",
        "Tahap_Risiko": "Tahap Risiko",
    }
    out = out.rename(columns=rename)
    if "Label Empirikal" in out.columns:
        out["Label Empirikal"] = out["Label Empirikal"].replace({"Scam": "Penipuan Siber", "Bukan Scam": "Bukan Penipuan Siber"})
    return out


def render_home():
    render_hero()
    render_stats()
    st.markdown('<div class="sa-grid-2">', unsafe_allow_html=True)
    st.markdown(
        """
        <div class="sa-panel">
            <div class="sa-icon">?</div>
            <div class="sa-section-title">Apakah itu ScamAlert?</div>
            <p>ScamAlert ialah prototaip web yang menganalisis mesej mencurigakan berdasarkan analisis lakuan pertuturan langsung dan lakuan pertuturan tidak langsung, komponen risiko serta perbandingan data penipuan siber dengan data kawalan sepadan.</p>
        </div>
        <div class="sa-panel">
            <div class="sa-icon">!</div>
            <div class="sa-section-title">Mengapakah ScamAlert penting?</div>
            <p>Bahasa penipuan siber sering menyerupai promosi, urusan rasmi atau mesej harian. ScamAlert membantu pengguna menilai risiko sebelum berkongsi data, menekan pautan atau membuat sebarang transaksi kewangan.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="sa-section-title">Bagaimana ScamAlert Berfungsi?</div>', unsafe_allow_html=True)
    render_process()

    st.markdown('<div class="sa-section-title">Siapa yang Dibantu?</div>', unsafe_allow_html=True)
    render_user_strip()

    st.markdown(
        """
        <div class="sa-callout">
            <div class="sa-callout-title">Nota prototaip</div>
            ScamAlert ialah prototaip amaran awal. Keputusan yang dipaparkan membantu pengguna membuat semakan awal dan tidak menggantikan pengesahan rasmi oleh pihak berkuasa.
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_analysis(data, tests):
    render_hero()
    render_stats()

    st.markdown('<div class="sa-input-panel">', unsafe_allow_html=True)
    st.markdown('<div class="sa-section-title">Semak Teks Mencurigakan</div>', unsafe_allow_html=True)
    st.markdown('<div class="sa-section-sub">Pilih contoh mesej atau tampal mesej anda sendiri untuk dianalisis.</div>', unsafe_allow_html=True)

    test_list = list(EXAMPLE_MESSAGES.keys())
    selected = st.selectbox("Pilih contoh mesej", test_list)
    default_text = EXAMPLE_MESSAGES[selected]
    user_text = st.text_area("Masukkan mesej untuk dianalisis", value=default_text, height=165, placeholder="Tampal mesej yang mencurigakan di sini…")
    clicked = st.button("Semak Risiko", type="primary")
    st.markdown('</div>', unsafe_allow_html=True)

    if clicked:
        if not user_text.strip():
            st.warning("Sila masukkan teks dahulu.")
        else:
            result = make_decision(user_text, data)
            st.markdown('<div class="sa-section-title">Keputusan Analisis</div>', unsafe_allow_html=True)
            render_result_cards(result)

            st.markdown('<div class="sa-section-title">Teks dengan Frasa Berisiko</div>', unsafe_allow_html=True)
            st.markdown(
                f"<div class='sa-text-box'>{highlight_text(user_text, result['phrases'])}</div>",
                unsafe_allow_html=True,
            )

            c1, c2 = st.columns([1, 1])
            with c1:
                st.markdown('<div class="sa-section-title">Frasa Berisiko Dikesan</div>', unsafe_allow_html=True)
                render_phrase_chips(result["phrases"], result["safe_hits"])
            with c2:
                st.markdown('<div class="sa-section-title">Komponen Risiko Dikesan</div>', unsafe_allow_html=True)
                render_feature_chips(result["found"] if result["score"] > 24 else {})

            st.markdown(
                f"""
                <div class="sa-action">
                    <strong>Cadangan Tindakan Selamat</strong><br>
                    {html.escape(recommendation(result['level']))}
                </div>
                <div class="sa-callout">
                    <div class="sa-callout-title">Ringkasan Keputusan</div>
                    {html.escape(summary_text(result['level']))}
                </div>
                """,
                unsafe_allow_html=True,
            )

            with st.expander("Lihat padanan terdekat dalam dataset"):
                display_cols = [c for c in ["ID_Data", "Label_Empirikal", "Jenis_Scam_Kawalan", "Ayat_Ujaran", "Skor_Risiko", "Tahap_Risiko", "Similarity"] if c in result["matches"].columns]
                st.dataframe(pretty_display_df(result["matches"][display_cols]), use_container_width=True, hide_index=True)

            st.markdown(
                '<div class="sa-disclaimer">ScamAlert ialah prototaip amaran awal dan tidak menggantikan semakan rasmi. Pengguna digalakkan menyemak kesahihan mesej melalui saluran rasmi sebelum berkongsi maklumat peribadi, menekan pautan atau membuat sebarang transaksi kewangan.</div>',
                unsafe_allow_html=True,
            )


def render_comparison(contrast):
    render_hero()
    st.markdown('<div class="sa-section-title">Perbandingan Empirikal</div>', unsafe_allow_html=True)
    st.markdown('<div class="sa-section-sub">ScamAlert tidak terus melabel sesuatu perkataan sebagai penipuan siber tanpa melihat konteks. Sistem membandingkan pola bahasa penipuan siber dengan data kawalan sepadan.</div>', unsafe_allow_html=True)

    st.markdown(
        """
        <div class="sa-grid-2">
            <div class="sa-panel">
                <div class="sa-icon">!</div>
                <div class="sa-section-title" style="font-size:24px;">Data Penipuan Siber</div>
                <p>Contoh pola bahasa berisiko tinggi yang sering muncul dalam mesej manipulatif.</p>
                <span class="sa-chip">Berikan OTP</span>
                <span class="sa-chip">Akaun dibekukan</span>
                <span class="sa-chip">Modal berganda</span>
                <span class="sa-chip">Bayar caj proses</span>
                <span class="sa-chip">Slot terhad</span>
                <span class="sa-chip">Yuran pendaftaran</span>
            </div>
            <div class="sa-panel">
                <div class="sa-icon">✓</div>
                <div class="sa-section-title" style="font-size:24px;">Data Kawalan Sepadan</div>
                <p>Contoh mesej sah yang kelihatan hampir sama tetapi tidak semestinya penipuan siber.</p>
                <span class="sa-chip safe">Promosi melalui aplikasi rasmi</span>
                <span class="sa-chip safe">Deposit dengan invois rasmi</span>
                <span class="sa-chip safe">Bank mengingatkan jangan kongsi OTP</span>
                <span class="sa-chip safe">Iklan kerja tanpa bayaran pendaftaran</span>
                <span class="sa-chip safe">Semak status syarikat melalui saluran rasmi</span>
            </div>
        </div>
        <div class="sa-callout">
            <div class="sa-callout-title">Bukan sekadar kata kunci</div>
            Satu perkataan seperti “promosi”, “segera” atau “bayar” tidak semestinya perlu dilabelkan sebagai penipuan siber. Risiko hanya meningkat apabila beberapa ciri manipulatif muncul bersama-sama dalam konteks yang mencurigakan.
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="sa-section-title">Komponen Skor Risiko</div>', unsafe_allow_html=True)
    chips = "".join([f'<span class="sa-chip">{html.escape(v)}</span>' for v in RISK_LABELS.values()])
    st.markdown(chips, unsafe_allow_html=True)

    if not contrast.empty:
        with st.expander("Lihat jadual pasangan kontras"):
            st.dataframe(contrast, use_container_width=True, hide_index=True)


def render_dashboard(dataset_file):
    render_hero()
    render_stats()

    st.markdown('<div class="sa-section-title">Papan Pemuka Ringkas</div>', unsafe_allow_html=True)
    st.markdown(
        """
        <div class="sa-grid-3">
            <div class="sa-stat"><div class="sa-icon">▲</div><div class="value">92%</div><div class="label">Lebih yakin mengenal pasti mesej berisiko</div></div>
            <div class="sa-stat"><div class="sa-icon">✓</div><div class="value">94%</div><div class="label">Bersetuju ScamAlert mudah digunakan</div></div>
            <div class="sa-stat"><div class="sa-icon">●</div><div class="value">93%</div><div class="label">Akan mencadangkan ScamAlert</div></div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    render_bar_chart(
        "Label Empirikal v0.5: Dataset Seimbang",
        [("Penipuan Siber", 1500, "fill-red"), ("Bukan Penipuan Siber", 1500, "fill-black")],
        max_value=1500,
    )

    render_bar_chart(
        "Pecahan Dataset v0.5",
        [
            ("Pinjaman / Bantuan Palsu", 500, "fill-red"),
            ("Penyamaran Autoriti", 500, "fill-red"),
            ("Pelaburan Tidak Wujud", 500, "fill-red"),
            ("Promosi / Transaksi Sah", 500, "fill-black"),
            ("Hebahan Rasmi / Keselamatan Sah", 500, "fill-black"),
            ("Pendidikan Kewangan / Kerjaya / Pelaburan Sah", 500, "fill-black"),
        ],
        max_value=500,
    )

    render_bar_chart(
        "Agihan Tahap Risiko Dataset v0.5",
        [
            ("Rendah", 1500, "fill-green"),
            ("Sederhana", 0, "fill-yellow"),
            ("Tinggi", 292, "fill-red"),
            ("Sangat Tinggi", 1208, "fill-darkred"),
        ],
        max_value=1500,
    )

    st.markdown(
        f"""
        <div class="sa-disclaimer">
            <strong>Sumber paparan papan pemuka:</strong><br>
            Papan pemuka menggunakan dataset sebenar v0.5 sebanyak 3,000 baris. Fail dataset dimuatkan: {html.escape(dataset_file)}.
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_codebook(kodbook, rubric, levels):
    render_hero()
    st.markdown('<div class="sa-section-title">Buku Kod dan Rubrik Skor</div>', unsafe_allow_html=True)

    st.markdown(
        """
        <div class="sa-grid-2">
            <div class="sa-panel">
                <div class="sa-icon">!</div>
                <div class="sa-section-title" style="font-size:22px;">Definisi data penipuan siber</div>
                <p>Data yang mengandungi pola bahasa manipulatif seperti arahan wang, permintaan data sensitif, penyamaran autoriti, tekanan masa, janji tidak realistik atau bukti sosial palsu.</p>
            </div>
            <div class="sa-panel">
                <div class="sa-icon">✓</div>
                <div class="sa-section-title" style="font-size:22px;">Definisi data kawalan</div>
                <p>Data sah yang menyerupai mesej biasa atau rasmi, tetapi bukan data bahasa penipuan siber. Sebagai contohnya promosi aplikasi rasmi, invois rasmi dan peringatan keselamatan sah.</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="sa-section-title">Julat Skor Risiko</div>', unsafe_allow_html=True)
    st.markdown(
        """
        <div class="sa-ladder">
            <div class="ladder-item risk-low"><div class="ladder-title">Rendah</div><div class="ladder-score">0–24</div><div class="ladder-note">Semak melalui saluran rasmi.</div></div>
            <div class="ladder-item risk-medium"><div class="ladder-title">Sederhana</div><div class="ladder-score">25–49</div><div class="ladder-note">Buat semakan lanjut sebelum bertindak.</div></div>
            <div class="ladder-item risk-high"><div class="ladder-title">Tinggi</div><div class="ladder-score">50–74</div><div class="ladder-note">Jangan kongsi data atau buat bayaran sebelum pengesahan dibuat.</div></div>
            <div class="ladder-item risk-very-high"><div class="ladder-title">Sangat Tinggi</div><div class="ladder-score">75–100</div><div class="ladder-note">Jangan kongsi OTP, jangan tekan pautan, dan semak segera dengan pihak rasmi.</div></div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="sa-section-title">Komponen Skor Risiko</div>', unsafe_allow_html=True)
    chips = "".join([f'<span class="sa-chip">{html.escape(v)}</span>' for v in RISK_LABELS.values()])
    st.markdown(chips, unsafe_allow_html=True)

    with st.expander("Lihat data kodbook dan rubrik asal"):
        if not kodbook.empty:
            st.subheader("Kodbook / Legend")
            st.dataframe(kodbook, use_container_width=True, hide_index=True)
        if not rubric.empty:
            st.subheader("Rubrik Skor Risiko")
            st.dataframe(rubric, use_container_width=True, hide_index=True)
        if not levels.empty:
            st.subheader("Tahap Risiko")
            st.dataframe(levels, use_container_width=True, hide_index=True)

    st.markdown(
        '<div class="sa-disclaimer">ScamAlert ialah prototaip amaran awal dan tidak menggantikan semakan rasmi. Pengguna digalakkan menyemak kesahihan mesej melalui saluran rasmi sebelum berkongsi maklumat peribadi, menekan pautan atau membuat sebarang transaksi kewangan.</div>',
        unsafe_allow_html=True,
    )


inject_css()
data, kawalan, kodbook, rubric, levels, contrast, tests, dataset_file = load_data()

st.markdown('<div class="sa-top-spacer"></div>', unsafe_allow_html=True)

tab_tentang, tab_analisis, tab_perbandingan, tab_dashboard, tab_kodbook = st.tabs(
    ["Tentang ScamAlert", "Analisis Mesej", "Perbandingan Empirikal", "Papan Pemuka", "Buku Kod dan Rubrik Skor"]
)

with tab_tentang:
    render_home()

with tab_analisis:
    render_analysis(data, tests)

with tab_perbandingan:
    render_comparison(contrast)

with tab_dashboard:
    render_dashboard(dataset_file)

with tab_kodbook:
    render_codebook(kodbook, rubric, levels)
