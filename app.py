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


def risk_meter(score):
    """Render a compact, accessible 0-100 screening index."""
    value = max(0, min(100, int(score)))
    return f"""
<div class="meter-wrap" aria-label="Skor risiko {value} daripada 100">
  <div class="meter-score">{value}<span>/100</span></div>
  <div class="meter-zones">
    <span class="meter-pointer" style="left:{value}%"></span>
  </div>
  <div class="meter-scale"><span>0</span><span>25</span><span>50</span><span>75</span><span>100</span></div>
</div>
"""


def tag_html(items, css_class, empty_text):
    values = [str(item) for item in items if item] if items else [empty_text]
    tags = "".join(
        f'<span class="tag {css_class}">{html.escape(value)}</span>'
        for value in values
    )
    return f'<div class="tag-wrap">{tags}</div>'


def move_pathway_html(moves):
    if not moves:
        return '<div class="empty-analysis">Tiada gerakan penipuan yang ketara dikesan.</div>'
    pathway = []
    for index, move in enumerate(moves):
        if index:
            pathway.append('<span class="move-arrow">→</span>')
        pathway.append(
            f'<span class="move-step">{html.escape(move["name"])}</span>'
        )
    return '<div class="move-pathway">' + "".join(pathway) + "</div>"


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
.result-category { display:inline-block; margin-top:.35rem; padding:.38rem .62rem; border-radius:9px; background:rgba(255,255,255,.68); border:1px solid rgba(17,24,39,.10); font-weight:750; }
.action-box { background:#111827; color:white; border-radius:14px; padding:1rem 1.08rem; font-size:1rem; line-height:1.5; margin-top:.4rem; }
.action-box strong, .action-box span { color:white !important; }
.result-category-label { color:var(--muted); font-size:.82rem; font-weight:800; margin-top:.7rem; }
.analysis-section { border-top:1px solid var(--line); padding-top:1.25rem; margin-top:1.35rem; }
.analysis-section h3 { margin-top:0; }
.score-card { background:var(--card); border:1px solid var(--line); border-radius:16px; padding:1rem 1.1rem; }
.meter-wrap { margin-top:.3rem; }
.meter-score { font-size:1.9rem; font-weight:900; line-height:1.1; margin-bottom:.6rem; }
.meter-score span { color:var(--muted); font-size:1rem; font-weight:650; }
.meter-zones { position:relative; width:100%; height:10px; border-radius:999px; background:linear-gradient(90deg,#15803D 0%,#15803D 25%,#D48B11 25%,#D48B11 50%,#DC2626 50%,#DC2626 75%,#8B1E16 75%,#8B1E16 100%); }
.meter-pointer { position:absolute; top:-5px; width:7px; height:20px; border-radius:999px; background:#111827; box-shadow:0 0 0 2px #FFFFFF; transform:translateX(-50%); }
.meter-scale { display:flex; justify-content:space-between; color:var(--muted); font-size:.72rem; margin-top:.35rem; }
.analysis-grid { display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); gap:.8rem; }
.analysis-card { background:var(--card); border:1px solid var(--line); border-radius:16px; padding:1rem; min-height:120px; }
.analysis-title { font-size:1rem; font-weight:850; margin-bottom:.25rem; }
.analysis-caption { color:var(--muted); font-size:.86rem; line-height:1.45; }
.tag-wrap { display:flex; flex-wrap:wrap; gap:.45rem; margin-top:.7rem; }
.tag { display:inline-block; padding:.42rem .62rem; border-radius:10px; font-size:.88rem; font-weight:650; border:1px solid var(--line); }
.tag-red { background:var(--red-soft); border-color:#FECACA; }
.tag-amber { background:var(--amber-soft); border-color:#F5D394; }
.tag-blue { background:#EFF6FF; border-color:#BFDBFE; }
.move-pathway { display:flex; flex-wrap:wrap; align-items:center; gap:.45rem; margin:.7rem 0; }
.move-step { background:#FFFFFF; border:1px solid #FECACA; color:var(--red-dark); border-radius:11px; padding:.45rem .62rem; font-size:.88rem; font-weight:750; }
.move-arrow { color:var(--muted); font-weight:900; }
.move-box { border-left:4px solid var(--red); background:#FFFFFF; border-radius:12px; padding:.75rem .85rem; margin:.55rem 0; border-top:1px solid var(--line); border-right:1px solid var(--line); border-bottom:1px solid var(--line); }
.move-name { font-weight:850; margin-bottom:.2rem; }
.move-function, .empty-analysis { color:var(--muted); font-size:.9rem; line-height:1.45; }
.insufficient-message { color:var(--muted); line-height:1.55; margin-top:.35rem; }
.stTextArea textarea { background:white !important; color:var(--ink) !important; border:1px solid #AEB5BF !important; border-radius:12px !important; min-height:170px !important; font-size:.875rem !important; font-weight:400 !important; line-height:1.5 !important; }
.stTextArea textarea::placeholder { color:#707887 !important; opacity:1 !important; font-size:.875rem !important; font-weight:400 !important; line-height:1.5 !important; }
.stButton > button { background:var(--red) !important; color:#FFFFFF !important; border:none !important; border-radius:11px !important; font-weight:850 !important; padding:.72rem 1.25rem !important; }
.stButton > button *, .stButton > button p, .stButton > button span { color:#FFFFFF !important; }
.stButton > button:hover { background:var(--red-dark) !important; color:#FFFFFF !important; }
[data-testid="stFileUploaderDropzone"] { background:white !important; border:1px dashed #9CA3AF !important; border-radius:12px !important; }
[data-testid="stFileUploaderDropzone"] button { background:white !important; color:var(--ink) !important; border:1px solid #CBD0D8 !important; }
[data-testid="stFileUploaderDropzone"] button { font-size:0 !important; min-width:240px; }
[data-testid="stFileUploaderDropzone"] button > * { display:none !important; }
[data-testid="stFileUploaderDropzone"] button::after { content:"Muat naik gambar di sini"; display:block; font-size:.875rem; line-height:1.5; color:#707887; font-weight:400; }
[data-testid="stFileUploaderDropzoneInstructions"] span,
[data-testid="stFileUploaderDropzoneInstructions"] small,
[data-testid="stFileUploaderDropzone"] small { color:var(--muted) !important; opacity:1 !important; }
div[data-baseweb="select"] > div { background:white !important; color:var(--ink) !important; }
div[data-baseweb="select"] * { color:var(--ink) !important; }
@media (max-width: 700px) {
    .title-main { font-size:2.45rem; }
    .block-container { padding-left:1rem; padding-right:1rem; }
    .analysis-grid { grid-template-columns:1fr; }
}
</style>
""",
    unsafe_allow_html=True,
)


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
    decision_state = result["decision_state"]

    if decision_state == "insufficient":
        st.markdown(
            f"""
<div class="result-card insufficient">
  <div class="result-label">Keputusan saringan</div>
  <div class="result-level">Mesej Tidak Mencukupi</div>
  <div class="insufficient-message">Mesej ini terlalu pendek atau tidak mempunyai konteks yang mencukupi untuk diberikan skor risiko.</div>
</div>
""",
            unsafe_allow_html=True,
        )
    else:
        category = result["threat_category"]
        st.markdown(
            f"""
<div class="result-card {html.escape(decision_state)}">
  <div class="result-label">Keputusan saringan</div>
  <div class="result-level">{html.escape(display_level)}</div>
  <div class="result-category-label">Jenis Penipuan</div>
  <div class="result-category">{html.escape(category)}</div>
</div>
""",
            unsafe_allow_html=True,
        )

        st.markdown('<div class="analysis-section">', unsafe_allow_html=True)
        st.markdown("### Skor Risiko")
        st.markdown(
            f'<div class="score-card">{risk_meter(result["overall_score"])}</div>',
            unsafe_allow_html=True,
        )
        st.markdown("</div>", unsafe_allow_html=True)

        direct_tags = tag_html(
            result.get("direct_phrases", []),
            "tag-red",
            "Tiada frasa tersurat yang ketara dikesan",
        )
        indirect_tags = tag_html(
            result.get("indirect_phrases", []),
            "tag-amber",
            "Tiada frasa tersirat yang ketara dikesan",
        )
        emotion_tags = tag_html(
            result.get("emotion_phrases", []),
            "tag-blue",
            "Tiada pencetus emosi yang ketara dikesan",
        )
        st.markdown(
            f"""
<div class="analysis-section">
  <h3>Analisis Bahasa</h3>
  <div class="analysis-grid">
    <div class="analysis-card">
      <div class="analysis-title">Frasa Tersurat</div>
      <div class="analysis-caption">Arahan atau permintaan yang dinyatakan secara langsung.</div>
      {direct_tags}
    </div>
    <div class="analysis-card">
      <div class="analysis-title">Frasa Tersirat</div>
      <div class="analysis-caption">Tekanan, ancaman atau pujukan yang dibina secara tidak langsung.</div>
      {indirect_tags}
    </div>
    <div class="analysis-card">
      <div class="analysis-title">Pencetus Emosi</div>
      <div class="analysis-caption">Emosi yang digunakan untuk mempengaruhi tindakan penerima.</div>
      {emotion_tags}
    </div>
    <div class="analysis-card">
      <div class="analysis-title">Jenis Lakuan Pertuturan</div>
      <div class="analysis-caption">{html.escape(result.get("speech_type", "Tiada pola lakuan yang ketara"))}</div>
    </div>
  </div>
</div>
""",
            unsafe_allow_html=True,
        )

        moves = result.get("moves", [])
        st.markdown('<div class="analysis-section">', unsafe_allow_html=True)
        st.markdown("### Analisis Gerakan")
        st.markdown(move_pathway_html(moves), unsafe_allow_html=True)
        for move in moves:
            st.markdown(
                f"""
<div class="move-box">
  <div class="move-name">{html.escape(move["code"])} · {html.escape(move["name"])}</div>
  <div class="move-function">{html.escape(move["function"])}</div>
</div>
""",
                unsafe_allow_html=True,
            )
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("### Cadangan Tindakan")
    st.markdown(
        f'<div class="action-box"><strong>{html.escape(result["recommended_action"])}</strong></div>',
        unsafe_allow_html=True,
    )
