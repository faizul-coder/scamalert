
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
DATA_PATH = Path(__file__).parent / "ScamAlert_Dataset_Kodbook_2000_v0_2.xlsx"

st.set_page_config(
    page_title="ScamAlert Web Prototype",
    page_icon="🛡️",
    layout="wide",
)

RISK_WEIGHTS = {
    "R1_Arahan_Wang_Data": 25,
    "R2_Janji_Dakwaan_Tidak_Realistik": 20,
    "R3_Penyamaran_Autoriti": 20,
    "R4_Tekanan_Masa": 15,
    "R5_Manipulasi_Emosi": 10,
    "R6_Bukti_Sosial_Legitimasi": 10,
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
        r"\btanpa semakan\b", r"\bmodal\b.*\bjadi\b", r"\bRM\d+.*RM\d+",
        r"\bdalam 24 jam\b", r"\bkeuntungan harian\b"
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
        r"\bpeluang terakhir\b", r"\btinggal\s+\d+\b"
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
    r"\bcawangan\b", r"\bcheckout\b", r"\binvois rasmi\b",
    r"\bjangan berkongsi\b", r"\btiada bayaran pendaftaran\b",
    r"\btidak akan meminta\b", r"\bsemak dahulu\b"
]


@st.cache_data
def load_data():
    if DATA_PATH is None:
        st.error("Fail dataset Excel tidak dijumpai. Sila upload fail scamalert_dataset.xlsx ke folder yang sama dengan app.py.")
        st.stop()
    xls = pd.ExcelFile(DATA_PATH)
    data = pd.read_excel(xls, "DATASET_UTAMA")
    kawalan = pd.read_excel(xls, "DATASET_KAWALAN_500")
    kodbook = pd.read_excel(xls, "KODBOOK_LEGEND")
    rubric = pd.read_excel(xls, "RUBRIK_SKOR_RISIKO")
    levels = pd.read_excel(xls, "TAHAP_RISIKO")
    contrast = pd.read_excel(xls, "PASANGAN_KONTRAS")
    tests = pd.read_excel(xls, "CONTOH_UJIAN_SISTEM")
    return data, kawalan, kodbook, rubric, levels, contrast, tests


def risk_level(score: int) -> str:
    if score >= 75:
        return "Sangat Tinggi"
    if score >= 50:
        return "Tinggi"
    if score >= 25:
        return "Sederhana"
    return "Rendah"


def infer_scam_type(text: str) -> str:
    t = text.lower()
    scores = {
        "Pinjaman/Bantuan Palsu": sum(k in t for k in ["pinjaman", "bantuan", "caj proses", "caj pengesahan", "diluluskan", "kelulusan", "dana"]),
        "Penyamaran Autoriti": sum(k in t for k in ["polis", "bank", "lhdn", "mahkamah", "kurier", "otp", "tac", "akaun keselamatan", "jenayah", "siasatan", "dibekukan"]),
        "Pelaburan Tidak Wujud": sum(k in t for k in ["pelaburan", "modal", "untung", "keuntungan", "withdraw", "vip", "mentor", "screenshot", "gandakan"]),
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

    # Empirical protection: reduce over-detection for official/safety messages.
    # If safe language appears and there is no direct request for money/data, cap score.
    has_critical = "R1_Arahan_Wang_Data" in found and not re.search(r"jangan\s+berkongsi|tidak\s+akan\s+meminta", text, flags=re.IGNORECASE)
    if safe_hits and not has_critical and score <= 35:
        score = min(score, 24)

    for hits in found.values():
        phrases.extend(hits)
    return min(score, 100), found, sorted(set(phrases), key=lambda x: text.lower().find(x.lower())), sorted(set(safe_hits))


@st.cache_resource
def build_similarity_model(texts_tuple):
    texts = list(texts_tuple)
    if SKLEARN_OK:
        vectorizer = TfidfVectorizer(lowercase=True, ngram_range=(1, 2), min_df=1)
        matrix = vectorizer.fit_transform(texts)
        return vectorizer, matrix
    return None, None


def get_top_matches(user_text, data, top_n=3):
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


def highlight_text(text, phrases):
    safe = html.escape(text)
    for phrase in sorted(phrases, key=len, reverse=True):
        if not phrase:
            continue
        p = html.escape(phrase)
        safe = re.sub(re.escape(p), f"<mark>{p}</mark>", safe, flags=re.IGNORECASE)
    return safe


def describe_features(found):
    labels = {
        "R1_Arahan_Wang_Data": "R1: Arahan wang/data sensitif",
        "R2_Janji_Dakwaan_Tidak_Realistik": "R2: Janji/dakwaan tidak realistik",
        "R3_Penyamaran_Autoriti": "R3: Penyamaran autoriti",
        "R4_Tekanan_Masa": "R4: Tekanan masa/desakan",
        "R5_Manipulasi_Emosi": "R5: Manipulasi emosi",
        "R6_Bukti_Sosial_Legitimasi": "R6: Bukti sosial/legitimasi palsu",
    }
    return [{"Komponen": labels[k], "Frasa Dikesan": ", ".join(v), "Markah": RISK_WEIGHTS[k]} for k, v in found.items()]


def make_decision(user_text, data):
    rule_score, found, phrases, safe_hits = analyze_rules(user_text)
    matches = get_top_matches(user_text, data, top_n=3)
    best = matches.iloc[0]
    best_similarity = float(best["Similarity"])
    best_label = str(best["Label_Empirikal"])
    best_category = str(best["Jenis_Scam_Kawalan"])

    final_score = rule_score
    category = infer_scam_type(user_text)

    # Similarity layer: use dataset only when similarity is meaningful.
    if best_similarity >= 0.55:
        dataset_score = int(best["Skor_Risiko"])
        if best_label == "Bukan Scam" and rule_score < 50:
            final_score = min(rule_score, 24)
            category = "Tidak menunjukkan pola scam kuat"
        elif best_label == "Scam":
            final_score = max(rule_score, dataset_score)
            category = best_category

    final_score = min(final_score, 100)
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


def render_badge(level):
    colors = {
        "Rendah": "#E8F5E9",
        "Sederhana": "#FFF8E1",
        "Tinggi": "#FBE9E7",
        "Sangat Tinggi": "#FFEBEE",
    }
    border = {
        "Rendah": "#43A047",
        "Sederhana": "#F9A825",
        "Tinggi": "#E64A19",
        "Sangat Tinggi": "#C62828",
    }
    return f"""
    <div style="padding:16px;border-radius:12px;background:{colors[level]};border:1px solid {border[level]};">
        <b>Tahap Risiko:</b> {level}
    </div>
    """


data, kawalan, kodbook, rubric, levels, contrast, tests = load_data()

st.sidebar.title("🛡️ ScamAlert")
page = st.sidebar.radio(
    "Navigasi",
    ["Home", "Semak Teks", "Perbandingan Empirikal", "Dashboard", "Kodbook & Rubrik"],
)

st.sidebar.caption("Prototaip v0.1 untuk tujuan pertandingan inovasi. Keputusan ialah amaran awal, bukan pengesahan rasmi.")

if page == "Home":
    st.title("🛡️ ScamAlert Web Prototype")
    st.subheader("Kenali bahasa scam sebelum terpedaya")
    st.write(
        """
        ScamAlert ialah prototaip aplikasi web yang menganalisis mesej mencurigakan
        berdasarkan **lakuan pertuturan**, **pola manipulasi**, **skor risiko** dan
        **perbandingan data scam dengan data kawalan bukan scam**.
        """
    )
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Jumlah Data", len(data))
    c2.metric("Data Scam", int((data["Label_Empirikal"] == "Scam").sum()))
    c3.metric("Data Kawalan", int((data["Label_Empirikal"] == "Bukan Scam").sum()))
    c4.metric("Jenis Scam Utama", 3)
    st.info("Mula dengan halaman **Semak Teks** untuk menguji mesej WhatsApp, Telegram, SMS atau media sosial.")

elif page == "Semak Teks":
    st.title("Semak Teks Mencurigakan")

    example_options = ["Tulis sendiri"] + tests["Mesej_Ujian"].dropna().astype(str).tolist()
    selected = st.selectbox("Pilih contoh ujian atau tulis sendiri", example_options)
    default_text = "" if selected == "Tulis sendiri" else selected

    user_text = st.text_area("Tampal mesej di sini", value=default_text, height=170)

    if st.button("Semak Risiko", type="primary"):
        if not user_text.strip():
            st.warning("Sila masukkan teks dahulu.")
        else:
            result = make_decision(user_text, data)
            st.markdown(render_badge(result["level"]), unsafe_allow_html=True)

            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Skor Risiko", f"{result['score']}/100")
            m2.metric("Jenis Dikesan", result["category"])
            m3.metric("Skor Rules", f"{result['rule_score']}/100")
            m4.metric("Padanan Data", f"{result['best_similarity']:.2f}")

            st.subheader("Teks dengan frasa berisiko")
            st.markdown(
                f"<div style='font-size:18px;line-height:1.7'>{highlight_text(user_text, result['phrases'])}</div>",
                unsafe_allow_html=True,
            )

            st.subheader("Komponen Risiko Dikesan")
            feature_rows = describe_features(result["found"])
            if feature_rows:
                st.dataframe(pd.DataFrame(feature_rows), use_container_width=True, hide_index=True)
            else:
                st.success("Tiada komponen risiko utama yang kuat dikesan.")

            if result["safe_hits"]:
                st.caption("Faktor penurun risiko dikesan: " + ", ".join(result["safe_hits"]))

            st.subheader("Penjelasan")
            if result["score"] >= 75:
                st.error("Mesej ini mengandungi gabungan ciri yang sangat berisiko. Jangan pindahkan wang atau beri data sensitif.")
            elif result["score"] >= 50:
                st.warning("Mesej ini berisiko tinggi. Semak sumber rasmi sebelum bertindak.")
            elif result["score"] >= 25:
                st.info("Mesej ini mempunyai unsur mencurigakan. Jangan bertindak terburu-buru.")
            else:
                st.success("Mesej ini tidak menunjukkan pola scam yang kuat berdasarkan rules prototaip.")

            st.subheader("Cadangan Tindakan Selamat")
            st.write("- Jangan pindahkan wang kepada akaun tidak dikenali.")
            st.write("- Jangan berkongsi OTP, TAC, kata laluan atau maklumat perbankan.")
            st.write("- Semak melalui saluran rasmi, bukan pautan daripada mesej mencurigakan.")
            st.write("- Simpan bukti mesej jika berasa terancam atau sudah membuat transaksi.")

            with st.expander("Padanan terdekat dalam dataset"):
                display_cols = ["ID_Data", "Label_Empirikal", "Jenis_Scam_Kawalan", "Ayat_Ujaran", "Skor_Risiko", "Tahap_Risiko", "Similarity"]
                st.dataframe(result["matches"][display_cols], use_container_width=True, hide_index=True)

elif page == "Perbandingan Empirikal":
    st.title("Perbandingan Empirikal: Scam vs Bukan Scam")
    st.write(
        """
        Bahagian ini menunjukkan bahawa ScamAlert tidak melabel sesuatu ayat sebagai scam
        hanya kerana ada perkataan seperti "promosi", "segera" atau "bayar".
        Sistem melihat gabungan ciri risiko dan konteks tindakan.
        """
    )
    st.dataframe(contrast, use_container_width=True, hide_index=True)

elif page == "Dashboard":
    st.title("Dashboard Dataset")
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Label Empirikal")
        st.bar_chart(data["Label_Empirikal"].value_counts())
    with col2:
        st.subheader("Tahap Risiko")
        st.bar_chart(data["Tahap_Risiko"].value_counts())

    st.subheader("Jenis Scam/Kawalan")
    st.bar_chart(data["Jenis_Scam_Kawalan"].value_counts())

    st.subheader("Data Ringkas")
    st.dataframe(data[["ID_Data", "Label_Empirikal", "Jenis_Scam_Kawalan", "Ayat_Ujaran", "Skor_Risiko", "Tahap_Risiko"]].head(100), use_container_width=True, hide_index=True)

elif page == "Kodbook & Rubrik":
    st.title("Kodbook & Rubrik Risiko")
    st.subheader("Kodbook / Legend")
    st.dataframe(kodbook, use_container_width=True, hide_index=True)

    st.subheader("Rubrik Skor Risiko")
    st.dataframe(rubric, use_container_width=True, hide_index=True)

    st.subheader("Tahap Risiko")
    st.dataframe(levels, use_container_width=True, hide_index=True)
