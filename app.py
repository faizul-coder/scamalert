import hashlib
import html

import streamlit as st

from scamalert_core import analyse_text, get_reference_status
from scamalert_ocr import (
    OCRInputError,
    OCRProcessingError,
    OCRUnavailableError,
    extract_text_from_image,
    get_ocr_status,
)


st.set_page_config(page_title="ScamAlert", page_icon="🛡️", layout="wide")

st.markdown(
    """
<style>
:root {
    --bg: #FAFAF8;
    --card: #FFFFFF;
    --ink: #111827;
    --muted: #5B6472;
    --line: #E5E7EB;
    --red: #C52B1E;
    --red-dark: #8B1E16;
    --red-soft: #FFF1F0;
    --amber-soft: #FFF7E6;
    --green: #146C43;
    --green-soft: #ECFDF3;
}
html, body, [class*="css"] { font-family: "Inter", "Segoe UI", sans-serif; }
.stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
    background: var(--bg) !important;
}
.block-container { max-width: 1080px; padding-top: 1.2rem; padding-bottom: 2.6rem; }
h1, h2, h3, h4, p, label, div, span { color: var(--ink); }
.hero-card { border-top:3px solid var(--red); padding:1.25rem 0 1.2rem 0; margin-bottom:1.1rem; }
.title-main { font-size:2.9rem; font-weight:850; line-height:1.08; margin:0 0 .65rem 0; }
.subtitle-main { color:var(--muted); font-size:1.12rem; line-height:1.65; margin:0; }
.section { border-top:1px solid var(--line); padding-top:1.5rem; }
.helper { color: var(--muted); line-height: 1.5; margin-top: -.35rem; margin-bottom:.8rem; }
.result-card { background:var(--card); border:1px solid var(--line); border-left-width:7px; border-radius:18px; padding:1.25rem 1.35rem; margin-top:1.2rem; }
.result-card.low { border-left-color:var(--green); background:var(--green-soft); }
.result-card.caution { border-left-color:#D48B11; background:var(--amber-soft); }
.result-card.high, .result-card.very_high { border-left-color:var(--red); background:var(--red-soft); }
.result-card.insufficient { border-left-color:#64748B; background:#F8FAFC; }
.result-label { color:var(--muted); font-size:.78rem; font-weight:850; letter-spacing:.06em; text-transform:uppercase; }
.result-level { font-size:2rem; font-weight:900; margin:.22rem 0 .3rem 0; }
.result-summary { color:#313946; font-size:1.02rem; line-height:1.5; }
.result-category { display:inline-block; margin-top:.7rem; padding:.38rem .62rem; border-radius:9px; background:rgba(255,255,255,.68); border:1px solid rgba(17,24,39,.10); font-weight:750; }
.reason-list { margin:.25rem 0 0 0; padding-left:1.2rem; }
.reason-list li { margin:.46rem 0; line-height:1.45; }
.action-box { background:#111827; color:white; border-radius:14px; padding:1rem 1.08rem; font-size:1rem; line-height:1.5; margin-top:.4rem; }
.action-box strong, .action-box span { color:white !important; }
.mini-grid { display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); gap:.75rem; margin:.75rem 0; }
.mini-card { background:white; border:1px solid var(--line); border-radius:12px; padding:.8rem; }
.mini-label { color:var(--muted); font-size:.76rem; font-weight:800; text-transform:uppercase; }
.mini-value { font-size:1.2rem; font-weight:850; margin-top:.2rem; }
.match { background:white; border:1px solid var(--line); border-radius:12px; padding:.75rem; margin:.55rem 0; }
.match-risk { border-left:4px solid var(--red); }
.match-control { border-left:4px solid var(--green); }
.match-head { font-weight:800; }
.match-text { color:#303846; line-height:1.45; margin-top:.3rem; }
.match-meta { color:var(--muted); font-size:.78rem; margin-top:.35rem; }
.footer-note { border-top:1px solid var(--line); color:var(--muted); font-size:.8rem; line-height:1.45; margin-top:1.5rem; padding-top:.8rem; }
.stTextArea textarea { background:white !important; color:var(--ink) !important; border:1px solid #AEB5BF !important; border-radius:12px !important; min-height:170px !important; }
.stTextArea textarea::placeholder { color:#707887 !important; opacity:1 !important; }
.stButton > button { background:var(--red) !important; color:#FFFFFF !important; border:none !important; border-radius:11px !important; font-weight:850 !important; padding:.72rem 1.25rem !important; }
.stButton > button *, .stButton > button p, .stButton > button span { color:#FFFFFF !important; }
.stButton > button:hover { background:var(--red-dark) !important; color:#FFFFFF !important; }
[data-testid="stFileUploaderDropzone"] { background:white !important; border:1px dashed #9CA3AF !important; border-radius:12px !important; }
[data-testid="stFileUploaderDropzone"] button { background:white !important; color:var(--ink) !important; border:1px solid #CBD0D8 !important; }
[data-testid="stFileUploaderDropzone"] button { font-size:0 !important; min-width:240px; }
[data-testid="stFileUploaderDropzone"] button > * { display:none !important; }
[data-testid="stFileUploaderDropzone"] button::after { content:"Muat naik gambar di sini"; display:block; font-size:1rem; line-height:1.25; color:#707887; font-weight:400; }
[data-testid="stFileUploaderDropzoneInstructions"] span,
[data-testid="stFileUploaderDropzoneInstructions"] small,
[data-testid="stFileUploaderDropzone"] small { color:var(--muted) !important; opacity:1 !important; }
div[data-baseweb="select"] > div { background:white !important; color:var(--ink) !important; }
div[data-baseweb="select"] * { color:var(--ink) !important; }
@media (max-width: 700px) {
    .title-main { font-size:2.45rem; }
    .block-container { padding-left:1rem; padding-right:1rem; }
    .mini-grid { grid-template-columns:1fr; }
}
</style>
""",
    unsafe_allow_html=True,
)


def match_card(match: dict, kind: str) -> str:
    similarity = float(match.get("similarity", 0.0)) * 100
    title = "Rujukan risiko" if kind == "risk" else "Rujukan kawalan"
    return f"""
    <div class="match match-{'risk' if kind == 'risk' else 'control'}">
      <div class="match-head">{title} · persamaan teks {similarity:.1f}%</div>
      <div class="match-text">“{html.escape(str(match.get('text', '')))}”</div>
      <div class="match-meta">{html.escape(str(match.get('category') or 'Kategori tidak dinyatakan'))}</div>
    </div>
    """


def list_html(items) -> str:
    values = list(items or ["Konteks belum mencukupi"])
    return '<ul class="reason-list">' + "".join(
        f"<li>{html.escape(str(item))}</li>" for item in values[:3]
    ) + "</ul>"


reference_status = get_reference_status()
ocr_status = get_ocr_status()

st.markdown(
    """
<div class="hero-card">
  <div class="title-main">ScamAlert</div>
  <p class="subtitle-main">ScamAlert ialah sistem amaran awal penipuan siber berasaskan Kecerdasan Buatan (AI) yang menganalisis corak bahasa, manipulasi emosi dan gerakan strategi pujukan dalam mesej digital sebelum pengguna berkongsi maklumat peribadi, menekan pautan atau membuat transaksi kewangan.</p>
</div>
""",
    unsafe_allow_html=True,
)

if not reference_status["loaded"]:
    st.error("Analisis data tidak dapat dimuatkan. Aplikasi menggunakan peraturan bahasa sahaja.")
if not ocr_status["available"]:
    st.warning("OCR tidak tersedia. Anda masih boleh menampal teks secara manual.")

st.markdown('<div class="section">', unsafe_allow_html=True)
st.markdown("## Semak Mesej Mencurigakan")

if "message_input" not in st.session_state:
    st.session_state["message_input"] = ""

# The uploader is executed before the text widget but displayed after it. This
# allows a new screenshot to populate the editable field in the same rerun.
text_input_area = st.container()
image_upload_area = st.container()

with image_upload_area:
    st.markdown('<div class="helper">atau</div>', unsafe_allow_html=True)
    uploaded_image = st.file_uploader(
        "Muat naik gambar di sini",
        type=["png", "jpg", "jpeg"],
        label_visibility="collapsed",
    )
    if uploaded_image is not None:
        image_bytes = uploaded_image.getvalue()
        image_key = hashlib.sha256(image_bytes).hexdigest()
        if st.session_state.get("ocr_upload_key") != image_key:
            previous_ocr = st.session_state.get("ocr_result") or {}
            if st.session_state.get("message_input") == previous_ocr.get("text"):
                st.session_state["message_input"] = ""
            st.session_state["ocr_upload_key"] = image_key
            st.session_state.pop("ocr_result", None)
            st.session_state.pop("ocr_error", None)
            st.session_state.pop("analysis_result", None)
            st.session_state.pop("analysis_text", None)
            if ocr_status["available"]:
                try:
                    with st.spinner("Membaca gambar…"):
                        ocr_result = extract_text_from_image(image_bytes)
                    st.session_state["ocr_result"] = ocr_result
                    st.session_state["message_input"] = ocr_result["text"]
                    st.toast("Teks gambar telah dimasukkan.", icon="✓")
                except (OCRUnavailableError, OCRInputError, OCRProcessingError) as exc:
                    st.session_state["ocr_error"] = str(exc)

        if st.session_state.get("ocr_error"):
            st.error(st.session_state["ocr_error"])
        elif (st.session_state.get("ocr_result") or {}).get("warning"):
            st.warning("Sebahagian teks gambar mungkin tidak tepat. Semak teks sebelum meneruskan.")

with text_input_area:
    message = st.text_area(
        "Mesej",
        label_visibility="collapsed",
        placeholder="Masukkan mesej di sini",
        key="message_input",
    )

check = st.button("Semak Mesej", type="primary")
st.markdown("</div>", unsafe_allow_html=True)

if check and message.strip():
    st.session_state["analysis_result"] = analyse_text(message)
    st.session_state["analysis_text"] = message
elif check:
    st.warning("Masukkan mesej atau muat naik gambar terlebih dahulu.")

result = None
if st.session_state.get("analysis_text") == message:
    result = st.session_state.get("analysis_result")

if result:
    display_level = result["display_level"]
    category = result["threat_category"]
    category_html = ""
    if category != "Tiada kategori ancaman yang jelas":
        category_html = f'<div class="result-category">{html.escape(category)}</div>'

    st.markdown(
        f"""
<div class="result-card {html.escape(result['decision_state'])}">
  <div class="result-label">Keputusan saringan</div>
  <div class="result-level">{html.escape(display_level)}</div>
  <div class="result-summary">{html.escape(result['decision_summary'])}</div>
  {category_html}
</div>
""",
        unsafe_allow_html=True,
    )

    st.markdown("### Mengapa keputusan ini diberikan?")
    st.markdown(list_html(result["risk_reasons"]), unsafe_allow_html=True)

    st.markdown("### Tindakan disarankan")
    st.markdown(
        f'<div class="action-box"><strong>{html.escape(result["recommended_action"])}</strong></div>',
        unsafe_allow_html=True,
    )

    with st.expander("Lihat butiran analisis"):
        st.markdown(
            f"""
<div class="mini-grid">
  <div class="mini-card"><div class="mini-label">Indeks dalaman</div><div class="mini-value">{result['overall_score']}/100</div></div>
  <div class="mini-card"><div class="mini-label">Peraturan bahasa</div><div class="mini-value">{result['rule_score']}/100</div></div>
  <div class="mini-card"><div class="mini-label">Indeks rujukan</div><div class="mini-value">{result['data_index']:.1f}/100</div></div>
  <div class="mini-card"><div class="mini-label">Persamaan terbaik</div><div class="mini-value">{result['best_similarity'] * 100:.1f}%</div></div>
</div>
""",
            unsafe_allow_html=True,
        )
        st.markdown(
            f"""
- **Lakuan pertuturan:** {result['speech_score']}/100 · {html.escape(result['speech_type'])}
- **Pencetus emosi:** {result['emotion_score']}/100
- **Gerakan strategi:** {result['move_score']}/100
- **Penggunaan data rujukan:** {result['data_weight'] * 100:.1f}%
            """
        )
        st.caption(
            "Skor ialah indeks saringan yang boleh dijelaskan, bukan kebarangkalian "
            "bahawa pengirim ialah penipu."
        )

        if result["risk_matches"] or result["control_matches"]:
            st.markdown("#### Rujukan teks terdekat")
            if result["risk_matches"]:
                st.markdown(match_card(result["risk_matches"][0], "risk"), unsafe_allow_html=True)
            if result["control_matches"]:
                st.markdown(match_card(result["control_matches"][0], "control"), unsafe_allow_html=True)

        if st.session_state.get("ocr_result"):
            ocr_result = st.session_state["ocr_result"]
            st.markdown("#### Maklumat OCR")
            st.caption(
                f'{ocr_result["word_count"]} perkataan diekstrak · '
                f'keyakinan bacaan {ocr_result["confidence"]:.1f}% · '
                f'bahasa {ocr_result["language"]}'
            )

    with st.expander("Had sistem dan privasi"):
        st.markdown(
            "ScamAlert ialah prototaip amaran awal berasaskan peraturan linguistik dan "
            "data rujukan terkawal. Ia belum menggantikan semakan bank, penyedia "
            "perkhidmatan atau pihak berkuasa. OCR boleh tersalah membaca imej; semak "
            "teks sebelum membuat keputusan."
        )
    st.markdown(
        '<div class="footer-note">Saringan awal sahaja. Jangan klik, bayar atau berkongsi OTP sebelum pengesahan melalui saluran rasmi.</div>',
        unsafe_allow_html=True,
    )
