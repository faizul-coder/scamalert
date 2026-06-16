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
APP_VERSION = "v0.4"
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
    r"\bjangan berkongsi\b", r"\btiada bayaran pendaftaran\b",
    r"\btidak akan meminta\b", r"\bsemak dahulu\b", r"\bsaluran rasmi\b"
]

EXTRA_TESTS = [
    "Masukkan OTP untuk mengelakkan akaun bank anda dibekukan.",
    "Kerja mudah dari rumah. Like video dapat RM500 sehari. Bayar pendaftaran dahulu.",
    "Promosi tamat malam ini. Bayaran dibuat melalui aplikasi rasmi.",
    "Sila bayar deposit tempahan kek selepas invois rasmi dikeluarkan oleh kedai.",
    "Modal RM100 boleh jadi RM1,000 dalam masa sehari. Slot terhad, daftar sekarang.",
    "Pihak bank mengingatkan pelanggan supaya tidak berkongsi nombor OTP dengan sesiapa.",
]


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
            --sa-black: #111827;
            --sa-text: #374151;
            --sa-muted: #6B7280;
            --sa-border: #E5E7EB;
            --sa-bg: #F8FAFC;
            --sa-card: #FFFFFF;
            --sa-green: #16A34A;
            --sa-green-soft: #DCFCE7;
            --sa-amber: #F59E0B;
            --sa-amber-soft: #FEF3C7;
            --sa-orange: #F97316;
            --sa-orange-soft: #FED7AA;
        }
        .stApp { background: var(--sa-bg); }
        .block-container { padding-top: 2rem; padding-bottom: 3rem; max-width: 1320px; }
        div[data-testid="stSidebar"] { background: #FFFFFF; border-right: 1px solid var(--sa-border); }
        h1, h2, h3 { color: var(--sa-black); letter-spacing: -0.03em; }
        p, li, label, .stMarkdown { color: var(--sa-text); }
        .sa-hero {
            background: linear-gradient(135deg, #FFFFFF 0%, #FFF7F7 48%, #FFFFFF 100%);
            border: 1px solid #FECACA;
            border-radius: 24px;
            padding: 34px 38px;
            box-shadow: 0 18px 45px rgba(17, 24, 39, 0.08);
            margin-bottom: 22px;
            position: relative;
            overflow: hidden;
        }
        .sa-hero:after {
            content: "";
            position: absolute;
            right: -80px;
            top: -80px;
            width: 260px;
            height: 260px;
            background: radial-gradient(circle, rgba(220,38,38,0.10) 0%, rgba(220,38,38,0) 68%);
            pointer-events: none;
        }
        .sa-brand { display: flex; align-items: center; gap: 12px; margin-bottom: 12px; }
        .sa-shield {
            width: 44px; height: 44px; border-radius: 14px;
            background: var(--sa-red); color: white; display:flex; align-items:center; justify-content:center;
            font-size: 24px; font-weight: 900; box-shadow: 0 10px 24px rgba(220,38,38,.25);
        }
        .sa-kicker { color: var(--sa-red); font-weight: 800; letter-spacing: .08em; text-transform: uppercase; font-size: 13px; }
        .sa-title { font-size: 48px; line-height: 1.05; font-weight: 900; color: var(--sa-black); margin: 0; }
        .sa-subtitle { font-size: 18px; line-height: 1.6; color: var(--sa-text); margin: 14px 0 0; max-width: 880px; }
        .sa-badge {
            display: inline-flex; align-items: center; gap: 8px; padding: 9px 14px;
            border-radius: 999px; background: #FFFFFF; border: 1px solid #FCA5A5;
            color: var(--sa-red-dark); font-weight: 800; font-size: 13px; margin-top: 16px;
        }
        .sa-grid { display:grid; grid-template-columns: repeat(4, minmax(0,1fr)); gap: 16px; margin: 18px 0 24px; }
        .sa-stat, .sa-card, .sa-panel {
            background: var(--sa-card); border: 1px solid var(--sa-border); border-radius: 18px;
            padding: 18px 20px; box-shadow: 0 12px 30px rgba(17,24,39,.06);
        }
        .sa-stat .value { font-size: 34px; line-height: 1; font-weight: 900; color: var(--sa-red); margin-bottom: 6px; }
        .sa-stat .label { font-size: 14px; color: var(--sa-text); font-weight: 700; }
        .sa-section-title { font-size: 28px; font-weight: 900; margin: 8px 0 10px; color: var(--sa-black); }
        .sa-small { color: var(--sa-muted); font-size: 14px; }
        .sa-input-panel { background: #FFFFFF; border: 1px solid #FECACA; border-radius: 20px; padding: 22px; box-shadow: 0 14px 35px rgba(17,24,39,.07); }
        div.stButton > button:first-child {
            background: var(--sa-red); color: white; border: 1px solid var(--sa-red); border-radius: 12px;
            font-weight: 800; padding: .65rem 1.15rem; box-shadow: 0 12px 24px rgba(220,38,38,.22);
        }
        div.stButton > button:first-child:hover { background: #B91C1C; border-color: #B91C1C; color: white; }
        textarea, input, .stSelectbox div[data-baseweb="select"] > div {
            border-radius: 12px !important;
        }
        .sa-result-grid { display:grid; grid-template-columns: 1.05fr 1.1fr 1.1fr .9fr; gap: 14px; margin: 18px 0 20px; }
        .risk-card {
            border-radius: 18px; padding: 20px; border: 1.5px solid; box-shadow: 0 14px 30px rgba(17,24,39,.08);
            min-height: 128px;
        }
        .risk-label { font-size: 13px; font-weight: 900; letter-spacing: .06em; text-transform: uppercase; margin-bottom: 8px; opacity: .9; }
        .risk-value { font-size: 36px; font-weight: 950; line-height: 1.05; margin-bottom: 6px; }
        .risk-caption { font-size: 13px; font-weight: 700; }
        .risk-low { background:#DCFCE7; color:#166534; border-color:#22C55E; }
        .risk-medium { background:#FEF3C7; color:#92400E; border-color:#F59E0B; }
        .risk-high { background:#FED7AA; color:#9A3412; border-color:#F97316; }
        .risk-very-high { background:#FEE2E2; color:#991B1B; border-color:#DC2626; }
        .neutral-card { background: #FFFFFF; color: var(--sa-black); border-color: var(--sa-border); }
        .neutral-card .risk-value { color: var(--sa-black); }
        .sa-chip {
            display: inline-flex; align-items:center; padding: 7px 11px; border-radius: 999px; margin: 4px 6px 4px 0;
            font-size: 13px; font-weight: 800; border: 1px solid #FCA5A5; background: var(--sa-red-soft); color: var(--sa-red-dark);
        }
        .sa-chip.safe { border-color:#86EFAC; background:#DCFCE7; color:#166534; }
        .sa-chip.muted { border-color:var(--sa-border); background:#F3F4F6; color:#6B7280; }
        mark { background:#FEF08A; color:#111827; padding: 2px 5px; border-radius: 5px; font-weight: 850; }
        .sa-text-box { background:#FFFFFF; border:1px solid var(--sa-border); border-radius:18px; padding:20px; font-size:18px; line-height:1.85; box-shadow: 0 10px 25px rgba(17,24,39,.05); }
        .sa-action { background:#FFF7ED; border:1px solid #FDBA74; border-left:6px solid #F97316; border-radius:16px; padding:18px 20px; }
        .sa-action strong { color:#9A3412; }
        .sa-disclaimer { background:#FFFFFF; border:1px dashed #D1D5DB; border-radius:16px; padding:16px 18px; color:#4B5563; font-size:14px; }
        .sa-two-col { display:grid; grid-template-columns: 1fr 1fr; gap:18px; margin-top:14px; }
        .sa-compare-title { font-weight: 900; font-size:20px; margin-bottom:12px; }
        @media (max-width: 900px) {
            .sa-grid, .sa-result-grid, .sa-two-col { grid-template-columns: 1fr; }
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
        r"jangan\s+berkongsi|tidak\s+berkongsi|tidak\s+akan\s+meminta|tiada\s+bayaran\s+pendaftaran|semak\s+dahulu|syarikat\s+berdaftar",
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
    else:
        sims = [SequenceMatcher(None, user_text.lower(), c.lower()).ratio() for c in corpus]
        idxs = sorted(range(len(sims)), key=lambda i: sims[i], reverse=True)[:top_n]
        results = data.iloc[idxs].copy()
        results["Similarity"] = [sims[i] for i in idxs]
        return results


def is_fraud_label(label: str) -> bool:
    label = str(label).lower()
    return label in ["scam", "penipuan siber", "fraud"] or "scam" in label or "penipuan" in label


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
        return "Mesej ini menunjukkan risiko yang sangat tinggi. Jangan kongsi OTP, jangan tekan pautan, jangan buat bayaran dan semak segera melalui saluran rasmi."
    if level == "Tinggi":
        return "Mesej ini berisiko tinggi. Jangan berkongsi maklumat peribadi atau membuat bayaran sebelum pengesahan rasmi dibuat."
    if level == "Sederhana":
        return "Terdapat beberapa ciri mencurigakan. Semak sumber mesej dan elakkan bertindak terburu-buru."
    return "Risiko rendah dikesan. Walau bagaimanapun, pengguna masih digalakkan menyemak kesahihan mesej melalui saluran rasmi."


def render_hero():
    st.markdown(
        f"""
        <div class="sa-hero">
            <div class="sa-brand">
                <div class="sa-shield">!</div>
                <div>
                    <div class="sa-kicker">{APP_TITLE} Web Prototype {APP_VERSION}</div>
                    <h1 class="sa-title">Kenal Pasti Bahasa Penipuan Siber Sebelum Terpedaya</h1>
                </div>
            </div>
            <p class="sa-subtitle">ScamAlert membantu pengguna mengenal pasti mesej yang mencurigakan melalui analisis bahasa, skor risiko dan cadangan tindakan selamat.</p>
            <div class="sa-badge">🛡️ Prototaip amaran awal • Analisis bahasa • Skor risiko</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_stats():
    st.markdown(
        f"""
        <div class="sa-grid">
            <div class="sa-stat"><div class="value">{DISPLAY_STATS['total']}</div><div class="label">Data prototaip</div></div>
            <div class="sa-stat"><div class="value">{DISPLAY_STATS['cyber_fraud']}</div><div class="label">Data penipuan siber</div></div>
            <div class="sa-stat"><div class="value">{DISPLAY_STATS['control']}</div><div class="label">Data kawalan sepadan</div></div>
            <div class="sa-stat"><div class="value">{DISPLAY_STATS['users']}</div><div class="label">Pengguna awal</div></div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def html_card(label, value, caption="", klass="neutral-card"):
    return f"""
    <div class="risk-card {klass}">
        <div class="risk-label">{html.escape(label)}</div>
        <div class="risk-value">{value}</div>
        <div class="risk-caption">{html.escape(caption)}</div>
    </div>
    """


def render_result_cards(result):
    level = result["level"]
    klass = risk_class(level)
    category = html.escape(str(result["category"]))
    st.markdown(
        f"""
        <div class="sa-result-grid">
            {html_card('Skor Risiko', f"{result['score']}/100", 'Skor keseluruhan', klass)}
            {html_card('Tahap Risiko', f"{risk_icon(level)} {html.escape(level)}", 'Keputusan amaran awal', klass)}
            {html_card('Jenis Dikesan', category, 'Kategori paling hampir', 'neutral-card')}
            {html_card('Padanan Data', f"{result['best_similarity']:.2f}", 'Kesamaan dengan dataset', 'neutral-card')}
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
            st.markdown(f'<span class="sa-chip safe">Faktor selamat: {html.escape(str(p))}</span>', unsafe_allow_html=True)


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


inject_css()
data, kawalan, kodbook, rubric, levels, contrast, tests, dataset_file = load_data()

st.sidebar.markdown("### 🛡️ ScamAlert")
st.sidebar.caption(f"Prototaip Web {APP_VERSION}")
page = st.sidebar.radio(
    "Navigasi",
    ["Home", "Analisis Mesej", "Perbandingan Empirikal", "Dashboard", "Kodbook & Rubrik"],
)
st.sidebar.markdown("---")
st.sidebar.caption("ScamAlert ialah prototaip amaran awal, bukan pengesahan rasmi.")

if page == "Home":
    render_hero()
    render_stats()
    st.markdown('<div class="sa-two-col">', unsafe_allow_html=True)
    st.markdown(
        """
        <div class="sa-panel">
            <div class="sa-section-title">Apa itu ScamAlert?</div>
            <p>ScamAlert ialah prototaip web yang menganalisis mesej mencurigakan berdasarkan pola bahasa, komponen risiko dan perbandingan data penipuan siber dengan data kawalan sepadan.</p>
        </div>
        <div class="sa-panel">
            <div class="sa-section-title">Mengapa penting?</div>
            <p>Bahasa penipuan siber sering menyerupai promosi, urusan rasmi atau mesej harian. ScamAlert membantu pengguna menilai risiko sebelum berkongsi data, menekan pautan atau membuat bayaran.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown('</div>', unsafe_allow_html=True)
    st.info("Pergi ke halaman **Analisis Mesej** untuk mencuba prototaip.")

elif page == "Analisis Mesej":
    render_hero()
    render_stats()

    st.markdown('<div class="sa-input-panel">', unsafe_allow_html=True)
    st.markdown('<div class="sa-section-title">Semak Teks Mencurigakan</div>', unsafe_allow_html=True)
    st.caption("Pilih contoh ujian atau tampal mesej sendiri untuk mendapatkan skor risiko dan cadangan tindakan selamat.")

    test_list = EXTRA_TESTS.copy()
    if not tests.empty and "Mesej_Ujian" in tests.columns:
        test_list += tests["Mesej_Ujian"].dropna().astype(str).tolist()
    # Remove duplicates while preserving order
    seen = set()
    test_list = [x for x in test_list if not (x in seen or seen.add(x))]

    example_options = ["Tulis sendiri"] + test_list
    selected = st.selectbox("Pilih contoh ujian atau tulis sendiri", example_options)
    default_text = "" if selected == "Tulis sendiri" else selected
    user_text = st.text_area("Masukkan mesej untuk dianalisis", value=default_text, height=165, placeholder="Tampal mesej WhatsApp, Telegram, SMS atau media sosial yang mencurigakan di sini…")
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
                st.markdown('<div class="sa-section-title">Frasa Dikesan</div>', unsafe_allow_html=True)
                render_phrase_chips(result["phrases"], result["safe_hits"])
            with c2:
                st.markdown('<div class="sa-section-title">Komponen Risiko</div>', unsafe_allow_html=True)
                render_feature_chips(result["found"] if result["score"] > 24 else {})

            st.markdown(
                f"""
                <div class="sa-action">
                    <strong>Cadangan Tindakan Selamat</strong><br>
                    {html.escape(recommendation(result['level']))}
                </div>
                """,
                unsafe_allow_html=True,
            )

            with st.expander("Lihat padanan terdekat dalam dataset"):
                display_cols = [c for c in ["ID_Data", "Label_Empirikal", "Jenis_Scam_Kawalan", "Ayat_Ujaran", "Skor_Risiko", "Tahap_Risiko", "Similarity"] if c in result["matches"].columns]
                st.dataframe(pretty_display_df(result["matches"][display_cols]), use_container_width=True, hide_index=True)

            st.markdown(
                '<div class="sa-disclaimer">ScamAlert ialah prototaip amaran awal dan tidak menggantikan semakan rasmi. Pengguna digalakkan menyemak kesahihan mesej melalui saluran rasmi sebelum berkongsi maklumat peribadi, menekan pautan atau membuat bayaran.</div>',
                unsafe_allow_html=True,
            )

elif page == "Perbandingan Empirikal":
    render_hero()
    st.markdown('<div class="sa-section-title">Perbandingan Empirikal</div>', unsafe_allow_html=True)
    st.write(
        "ScamAlert membandingkan pola bahasa penipuan siber dengan data kawalan sepadan supaya sistem tidak terus melabel perkataan seperti ‘promosi’, ‘segera’ atau ‘bayar’ sebagai berisiko tanpa melihat konteks."
    )
    st.markdown('<div class="sa-two-col">', unsafe_allow_html=True)
    st.markdown(
        """
        <div class="sa-panel">
            <div class="sa-compare-title" style="color:#991B1B;">Data Penipuan Siber</div>
            <span class="sa-chip">Berikan OTP</span>
            <span class="sa-chip">Akaun dibekukan</span>
            <span class="sa-chip">Modal berganda</span>
            <span class="sa-chip">Bayar caj proses</span>
            <span class="sa-chip">Slot terhad</span>
        </div>
        <div class="sa-panel">
            <div class="sa-compare-title" style="color:#166534;">Data Kawalan Sepadan</div>
            <span class="sa-chip safe">Promosi melalui aplikasi rasmi</span>
            <span class="sa-chip safe">Deposit dengan invois rasmi</span>
            <span class="sa-chip safe">Jangan kongsi OTP</span>
            <span class="sa-chip safe">Tiada bayaran pendaftaran</span>
            <span class="sa-chip safe">Semak saluran rasmi</span>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown('</div>', unsafe_allow_html=True)
    if not contrast.empty:
        st.subheader("Jadual pasangan kontras")
        st.dataframe(contrast, use_container_width=True, hide_index=True)

elif page == "Dashboard":
    render_hero()
    render_stats()
    st.markdown('<div class="sa-section-title">Dashboard Ringkas</div>', unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(html_card("Keyakinan pengguna", "92%", "Lebih yakin mengenal pasti mesej berisiko", "neutral-card"), unsafe_allow_html=True)
    with c2:
        st.markdown(html_card("Kebolehgunaan", "94%", "Bersetuju ScamAlert mudah digunakan", "neutral-card"), unsafe_allow_html=True)
    with c3:
        st.markdown(html_card("Cadangan penggunaan", "93%", "Akan mencadangkan ScamAlert", "neutral-card"), unsafe_allow_html=True)

    if "Label_Empirikal" in data.columns:
        st.subheader("Label Empirikal dalam Dataset Semasa")
        st.bar_chart(data["Label_Empirikal"].replace({"Scam": "Penipuan Siber", "Bukan Scam": "Bukan Penipuan Siber"}).value_counts())
    if "Tahap_Risiko" in data.columns:
        st.subheader("Tahap Risiko")
        st.bar_chart(data["Tahap_Risiko"].value_counts())
    if "Jenis_Scam_Kawalan" in data.columns:
        st.subheader("Jenis Data")
        st.bar_chart(data["Jenis_Scam_Kawalan"].value_counts())

    st.caption(f"Fail dataset dimuatkan: {dataset_file}")

elif page == "Kodbook & Rubrik":
    render_hero()
    st.markdown('<div class="sa-section-title">Kodbook & Rubrik Risiko</div>', unsafe_allow_html=True)

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
        '<div class="sa-disclaimer">ScamAlert ialah prototaip amaran awal. Keputusan sistem membantu pengguna mengenal pasti risiko awal, tetapi tidak menggantikan semakan rasmi.</div>',
        unsafe_allow_html=True,
    )
