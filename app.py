import hashlib
import html

import streamlit as st

from scamalert_core import (
    SCAMMOVE_CONTROL_EXAMPLES,
    SCAMMOVE_SCAM_EXAMPLES,
    analyse_text,
    get_reference_status,
)
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
    --bg: #F7F7F5;
    --card: #FFFFFF;
    --ink: #111827;
    --muted: #4B5563;
    --line: #E5E7EB;
    --red: #B91C1C;
    --red-dark: #7F1D1D;
    --red-soft: #FEE2E2;
    --amber: #B45309;
    --amber-soft: #FEF3C7;
    --green: #15803D;
    --green-soft: #DCFCE7;
    --blue: #1D4ED8;
    --blue-soft: #EFF6FF;
}
html, body, [class*="css"] { font-family: "Inter", "Segoe UI", sans-serif; }
.stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
    background: var(--bg) !important;
}
.block-container { max-width: 1120px; padding-top: 1.2rem; padding-bottom: 3rem; }
h1, h2, h3, h4, p, label, div, span { color: var(--ink); }
.hero {
    border-top: 4px solid var(--red);
    border-bottom: 1px solid var(--line);
    padding: 1.35rem 0 1.25rem 0;
    margin-bottom: 1rem;
}
.eyebrow { color: var(--red); font-size: .82rem; font-weight: 850; letter-spacing: .08em; text-transform: uppercase; }
.title { font-size: 3rem; font-weight: 900; line-height: 1.05; margin: .2rem 0 .55rem 0; }
.subtitle { max-width: 900px; color: var(--muted); font-size: 1.08rem; line-height: 1.6; }
.status-good, .status-bad {
    border-radius: 14px;
    padding: .95rem 1rem;
    margin: .8rem 0 1rem 0;
    line-height: 1.5;
}
.status-good { background: var(--green-soft); border: 1px solid #BBF7D0; color: #14532D; }
.status-bad { background: var(--red-soft); border: 1px solid #FECACA; color: var(--red-dark); }
.panel { border-top: 1px solid var(--line); padding: 1.2rem 0 .8rem 0; margin-top: .5rem; }
.helper { color: var(--muted); line-height: 1.55; margin-top: -.3rem; }
.card {
    height: 100%;
    background: var(--card);
    border: 1px solid #EAECF0;
    border-radius: 15px;
    padding: 1rem;
}
.label { color: var(--muted); font-size: .84rem; font-weight: 800; text-transform: uppercase; letter-spacing: .03em; }
.value { font-size: 1.8rem; font-weight: 900; line-height: 1.15; margin-top: .35rem; }
.note { color: var(--muted); font-size: .9rem; line-height: 1.45; margin-top: .45rem; }
.badge { display: inline-block; border-radius: 999px; padding: .4rem .75rem; font-weight: 800; margin-top: .45rem; }
.low { color: var(--green); background: var(--green-soft); border: 1px solid #BBF7D0; }
.medium { color: var(--amber); background: var(--amber-soft); border: 1px solid #FDE68A; }
.high { color: var(--red); background: var(--red-soft); border: 1px solid #FECACA; }
.very-high { color: var(--red-dark); background: #FDE8E8; border: 1px solid #FCA5A5; }
.meter { margin-top: .65rem; }
.meter-score { font-size: 1.75rem; font-weight: 900; margin-bottom: .45rem; }
.meter-bar { position: relative; height: 10px; border-radius: 99px; background: linear-gradient(90deg,#15803D 0 25%,#CA8A04 25% 50%,#DC2626 50% 75%,#7F1D1D 75% 100%); }
.meter-pointer { position:absolute; top:-5px; width:7px; height:20px; border-radius:99px; background:#111827; box-shadow:0 0 0 2px white; transform:translateX(-50%); }
.meter-scale { display:flex; justify-content:space-between; color:var(--muted); font-size:.7rem; margin-top:.3rem; }
.tag-wrap { display:flex; flex-wrap:wrap; gap:8px; margin:.4rem 0 .8rem 0; }
.tag { padding:.42rem .7rem; border-radius:10px; font-size:.9rem; font-weight:650; border:1px solid var(--line); }
.tag-red { background:var(--red-soft); border-color:#FECACA; }
.tag-amber { background:var(--amber-soft); border-color:#FDE68A; }
.tag-blue { background:var(--blue-soft); border-color:#BFDBFE; color:var(--blue); }
.tag-green { background:var(--green-soft); border-color:#BBF7D0; color:var(--green); }
.path { display:flex; flex-wrap:wrap; align-items:center; gap:7px; margin:.65rem 0; }
.move { background:white; border:1px solid #FECACA; color:var(--red-dark); border-radius:12px; padding:.48rem .7rem; font-weight:750; }
.arrow { color:var(--muted); font-weight:900; }
.callout { border-left:4px solid var(--red); background:white; border-radius:10px; padding:.8rem .9rem; margin:.55rem 0; border-top:1px solid #EEF0F3; border-right:1px solid #EEF0F3; border-bottom:1px solid #EEF0F3; }
.match { background:white; border:1px solid #E5E7EB; border-radius:13px; padding:.85rem; margin:.55rem 0; }
.match-risk { border-left:4px solid var(--red); }
.match-control { border-left:4px solid var(--green); }
.match-head { font-weight:850; }
.match-text { color:#1F2937; line-height:1.5; margin-top:.35rem; }
.match-meta { color:var(--muted); font-size:.82rem; margin-top:.4rem; }
.disclaimer { background:#FCFCFD; border-top:1px solid var(--line); padding:1rem 0; color:var(--muted); line-height:1.55; }
.stTextArea textarea { background:white !important; color:var(--ink) !important; border:1px solid #D1D5DB !important; border-radius:12px !important; min-height:180px !important; }
.stButton > button { background:var(--red) !important; color:white !important; border:none !important; border-radius:12px !important; font-weight:800 !important; padding:.7rem 1.3rem !important; }
.stButton > button:hover { background:#991B1B !important; }
[data-testid="stFileUploaderDropzone"] { background:white !important; border:1px dashed #9CA3AF !important; border-radius:12px !important; }
@media (max-width: 700px) { .title { font-size:2.3rem; } .block-container { padding-left:1rem; padding-right:1rem; } }
</style>
""",
    unsafe_allow_html=True,
)


def badge_class(level: str) -> str:
    return {
        "Rendah": "low",
        "Sederhana": "medium",
        "Tinggi": "high",
        "Sangat Tinggi": "very-high",
    }.get(level, "medium")


def meter(score: int) -> str:
    score = max(0, min(100, int(score)))
    return f"""
    <div class="meter">
      <div class="meter-score">{score}/100</div>
      <div class="meter-bar"><span class="meter-pointer" style="left:{score}%;"></span></div>
      <div class="meter-scale"><span>0</span><span>25</span><span>50</span><span>75</span><span>100</span></div>
    </div>
    """


def tags(items, css_class: str) -> str:
    values = items or ["Tiada petanda yang ketara"]
    return '<div class="tag-wrap">' + "".join(
        f'<span class="tag {css_class}">{html.escape(str(item))}</span>' for item in values
    ) + "</div>"


def move_path(moves) -> str:
    if not moves:
        return '<div class="note">Tiada urutan gerakan berisiko yang ketara.</div>'
    pieces = []
    for index, move in enumerate(moves):
        if index:
            pieces.append('<span class="arrow">→</span>')
        pieces.append(f'<span class="move">{html.escape(move["name"])}</span>')
    return '<div class="path">' + "".join(pieces) + "</div>"


def match_card(match: dict, kind: str) -> str:
    similarity = float(match.get("similarity", 0.0)) * 100
    title = "Rujukan risiko" if kind == "risk" else "Rujukan kawalan"
    category = match.get("category") or "Kategori tidak dinyatakan"
    module = match.get("module") or "Modul tidak dinyatakan"
    return f"""
    <div class="match match-{'risk' if kind == 'risk' else 'control'}">
      <div class="match-head">{title} · persamaan teks {similarity:.1f}%</div>
      <div class="match-text">“{html.escape(str(match.get('text', '')))}”</div>
      <div class="match-meta">ID {html.escape(str(match.get('record_id', '')))} · {html.escape(module)} · {html.escape(category)}</div>
    </div>
    """


DEMO_EXAMPLES = {
    "Masukkan mesej sendiri": "",
    "Penyamaran bank + OTP": "Pihak bank mengesan aktiviti luar biasa. Berikan OTP sekarang. Jika gagal, akaun anda akan dibekukan dalam 15 minit.",
    "Pinjaman + caj proses": "Permohonan pinjaman anda telah diluluskan. Bayar caj proses RM30 dahulu sebelum wang RM500 dilepaskan hari ini.",
    "Laporan mangsa + caj berulang": "Saya sudah bayar dua kali, tetapi mereka masih minta deposit tambahan untuk keluarkan duit hari ini.",
    "Peringatan keselamatan sebenar": "Pihak bank tidak pernah meminta OTP. Jangan kongsi OTP, PIN atau kata laluan dengan sesiapa. Semak melalui aplikasi rasmi.",
    "Ayat keselamatan palsu + arahan": "Jangan bayar caj proses kepada orang lain, tetapi bayar deposit RM500 kepada saya sekarang.",
}


def load_demo_message():
    st.session_state["message_input"] = DEMO_EXAMPLES.get(
        st.session_state.get("demo_choice", ""), ""
    )
    st.session_state.pop("ocr_image_key", None)
    st.session_state.pop("ocr_result", None)
    st.session_state.pop("ocr_error", None)


st.markdown(
    """
<div class="hero">
  <div class="eyebrow">NICE 2026 · Demo 1.2 · Data + linguistik + OCR</div>
  <div class="title">ScamAlert</div>
  <div class="subtitle">Saringan awal mesej digital yang membaca teks atau tangkapan layar, membandingkannya dengan korpus rujukan unik dan menggabungkannya dengan peraturan linguistik yang boleh dijelaskan. Keputusan ialah indeks petanda risiko, bukan kebarangkalian atau pengesahan rasmi.</div>
</div>
""",
    unsafe_allow_html=True,
)


reference_status = get_reference_status()
if reference_status["loaded"]:
    stats = reference_status["statistics"]
    st.markdown(
        f"""
        <div class="status-good"><strong>✓ Data rujukan aktif.</strong>
        Enjin memuatkan {stats['normalized_templates']} templat unik
        ({stats['templates_by_label']['risk']} risiko, {stats['templates_by_label']['control']} kawalan)
        daripada {stats['exact_unique_messages']} teks unik global. Pendua sintetik tidak menerima undi tambahan.</div>
        """,
        unsafe_allow_html=True,
    )
    with st.expander("Lihat audit data yang digunakan"):
        st.markdown(
            f"""
- **{stats['source_rows']:,}** baris sumber telah diaudit.
- **{stats['exact_unique_messages']}** teks unik global: **{stats['exact_unique_by_label']['risk']} risiko** dan **{stats['exact_unique_by_label']['control']} kawalan**.
- **{stats['normalized_templates']}** templat digunakan untuk padanan: satu undi bagi setiap templat.
- **{stats['exact_level_conflicts']}** teks mempunyai label tahap risiko yang bercanggah; sebab itu tahap asal tidak digunakan sebagai sasaran skor.
- Status sumber: data simulasi terkawal, **belum** data ground truth dunia sebenar.
            """
        )
else:
    st.markdown(
        f'<div class="status-bad"><strong>Data rujukan gagal dimuatkan.</strong> Aplikasi berada dalam mod peraturan sahaja. {html.escape(str(reference_status.get("error") or ""))}</div>',
        unsafe_allow_html=True,
    )

ocr_status = get_ocr_status()
if ocr_status["available"]:
    language_label = "Bahasa Melayu + Inggeris" if ocr_status["selected_language"] == "msa+eng" else "Inggeris/teks Rumi"
    st.markdown(
        f'<div class="status-good"><strong>✓ OCR aktif.</strong> Teks dalam PNG/JPG akan diekstrak secara setempat menggunakan {html.escape(language_label)}, kemudian dimasukkan ke ruangan mesej untuk disemak sebelum analisis.</div>',
        unsafe_allow_html=True,
    )
else:
    st.markdown(
        f'<div class="status-bad"><strong>OCR tidak tersedia.</strong> Tampal teks secara manual. {html.escape(str(ocr_status.get("error") or ""))}</div>',
        unsafe_allow_html=True,
    )


st.markdown('<div class="panel">', unsafe_allow_html=True)
st.markdown("## Semak mesej mencurigakan")
st.markdown('<div class="helper">Pilih contoh demonstrasi atau tampal mesej sendiri. Elakkan memasukkan OTP, nombor akaun atau data peribadi sebenar ketika pameran.</div>', unsafe_allow_html=True)
st.selectbox(
    "Contoh demonstrasi",
    list(DEMO_EXAMPLES.keys()),
    key="demo_choice",
    on_change=load_demo_message,
)
if "message_input" not in st.session_state:
    st.session_state["message_input"] = ""

# Containers are created in display order, while OCR is executed before the
# text widget is instantiated.  This lets extracted text safely populate the
# editable text area without mutating an already-created Streamlit widget.
text_input_area = st.container()
image_upload_area = st.container()

with image_upload_area:
    st.markdown("**atau muat naik gambar di bawah:**")
    uploaded_image = st.file_uploader(
        "Muat naik gambar di sini",
        type=["png", "jpg", "jpeg"],
        label_visibility="collapsed",
    )
    if uploaded_image is not None:
        image_bytes = uploaded_image.getvalue()
        image_key = hashlib.sha256(image_bytes).hexdigest()

        # A new upload must never inherit the result or error from a previous
        # screenshot.  Manual text is preserved until the user explicitly asks
        # OCR to replace it.
        if st.session_state.get("ocr_upload_key") != image_key:
            previous_ocr = st.session_state.get("ocr_result") or {}
            if st.session_state.get("message_input") == previous_ocr.get("text"):
                st.session_state["message_input"] = ""
            st.session_state["ocr_upload_key"] = image_key
            st.session_state.pop("ocr_image_key", None)
            st.session_state.pop("ocr_result", None)
            st.session_state.pop("ocr_error", None)

        extract_clicked = st.button(
            "Ekstrak teks daripada gambar",
            key=f"ocr_extract_{image_key[:16]}",
            disabled=not bool(ocr_status["available"]),
        )
        if extract_clicked:
            try:
                with st.spinner("Membaca teks daripada gambar…"):
                    ocr_result = extract_text_from_image(image_bytes)
                st.session_state["ocr_image_key"] = image_key
                st.session_state["ocr_result"] = ocr_result
                st.session_state["message_input"] = ocr_result["text"]
                st.session_state.pop("ocr_error", None)
            except (OCRUnavailableError, OCRInputError, OCRProcessingError) as exc:
                st.session_state["ocr_image_key"] = image_key
                st.session_state["ocr_error"] = str(exc)
                st.session_state.pop("ocr_result", None)

        if st.session_state.get("ocr_image_key") == image_key and st.session_state.get("ocr_error"):
            st.error(st.session_state["ocr_error"])
            st.caption("Input manual masih boleh digunakan; kegagalan OCR tidak menghasilkan skor risiko.")
        elif st.session_state.get("ocr_image_key") == image_key and st.session_state.get("ocr_result"):
            ocr_result = st.session_state["ocr_result"]
            st.success(
                f'Teks OCR berjaya diekstrak: {ocr_result["word_count"]} perkataan, '
                f'purata keyakinan OCR perkataan {ocr_result["confidence"]:.1f}%.'
            )
            st.caption(
                "Semak dan betulkan teks dalam ruangan mesej sebelum menekan Semak Mesej. "
                "Keyakinan OCR bukan keyakinan bahawa mesej itu penipuan."
            )
            if ocr_result.get("warning"):
                st.warning(ocr_result["warning"])
        else:
            st.caption("Klik Ekstrak teks, kemudian semak hasilnya dalam ruangan mesej sebelum analisis.")
        with st.expander("Lihat gambar dan butiran OCR"):
            st.image(uploaded_image, use_container_width=True)
            if st.session_state.get("ocr_image_key") == image_key and st.session_state.get("ocr_result"):
                ocr_result = st.session_state["ocr_result"]
                st.caption(
                    f'Bahasa: {ocr_result["language"]} · Kaedah susun atur: PSM {ocr_result["psm"]} · '
                    f'Prapemprosesan: {ocr_result["preprocessing"]} · '
                    f'Resolusi diproses: {ocr_result["processed_size"][0]} × {ocr_result["processed_size"][1]}'
                )

with text_input_area:
    st.markdown("**Masukkan mesej di bawah:**")
    message = st.text_area(
        "Mesej",
        label_visibility="collapsed",
        placeholder="Tampal teks mesej di sini…",
        key="message_input",
    )

check = st.button("Semak Mesej")
st.markdown("</div>", unsafe_allow_html=True)


if check and message.strip():
    result = analyse_text(message)

    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.markdown("## Keputusan keseluruhan")
    col1, col2, col3 = st.columns([1.1, 0.9, 1.2])
    with col1:
        st.markdown(
            f'<div class="card"><div class="label">Indeks Petanda Risiko Hibrid</div>{meter(result["overall_score"])}<div class="note">Gabungan peraturan linguistik dan padanan data apabila bukti mencukupi.</div></div>',
            unsafe_allow_html=True,
        )
    with col2:
        st.markdown(
            f'<div class="card"><div class="label">Tahap Saringan</div><div class="badge {badge_class(result["overall_level"])}">{html.escape(result["overall_level"])}</div><div class="note">Indeks, bukan peratus kemungkinan.</div></div>',
            unsafe_allow_html=True,
        )
    with col3:
        st.markdown(
            f'<div class="card"><div class="label">Kategori Petanda</div><div class="note" style="font-size:1rem;font-weight:800;color:#111827;">{html.escape(result["threat_category"])}</div><div class="note">Amaran awal; semak melalui pihak rasmi.</div></div>',
            unsafe_allow_html=True,
        )
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.markdown("## Bagaimana indeks dibentuk")
    a, b, c, d = st.columns(4)
    a.metric("Peraturan linguistik", f'{result["rule_score"]}/100')
    b.metric("Indeks rujukan data", f'{result["data_index"]:.1f}/100')
    c.metric("Berat data digunakan", f'{result["data_weight"] * 100:.1f}%')
    d.metric("Persamaan terbaik", f'{result["best_similarity"] * 100:.1f}%')
    st.info(result["data_message"] + ". Nilai persamaan ialah kesamaan teks, bukan keyakinan bahawa mesej itu penipuan.")
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.markdown("## Bukti padanan data masa nyata")
    st.markdown('<div class="helper">Aplikasi menunjukkan rujukan risiko dan kawalan terdekat yang benar-benar dibaca daripada fail data. Hanya padanan sederhana atau kuat mempengaruhi indeks hibrid.</div>', unsafe_allow_html=True)
    risk_col, control_col = st.columns(2)
    with risk_col:
        st.markdown("### Risiko terdekat")
        if result["risk_matches"]:
            for item in result["risk_matches"][:2]:
                st.markdown(match_card(item, "risk"), unsafe_allow_html=True)
        else:
            st.caption("Tiada rujukan risiko tersedia.")
    with control_col:
        st.markdown("### Kawalan terdekat")
        if result["control_matches"]:
            for item in result["control_matches"][:2]:
                st.markdown(match_card(item, "control"), unsafe_allow_html=True)
        else:
            st.caption("Tiada rujukan kawalan tersedia.")
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.markdown("## Tiga lapisan linguistik")
    speech_col, emotion_col, move_col = st.columns(3)
    with speech_col:
        st.markdown(
            f'<div class="card"><div class="label">Lakuan Langsung / Tidak Langsung</div>{meter(result["speech_score"])}<div class="badge {badge_class(result["speech_level"])}">{result["speech_level"]}</div><div class="note">{html.escape(result["speech_type"])}</div></div>',
            unsafe_allow_html=True,
        )
    with emotion_col:
        emotion_text = ", ".join(result["emotions"]) if result["emotions"] else "Tiada pencetus ketara"
        st.markdown(
            f'<div class="card"><div class="label">Pencetus Emosi</div>{meter(result["emotion_score"])}<div class="badge {badge_class(result["emotion_level"])}">{result["emotion_level"]}</div><div class="note">{html.escape(emotion_text)}</div></div>',
            unsafe_allow_html=True,
        )
    with move_col:
        st.markdown(
            f'<div class="card"><div class="label">Gerakan Strategi</div>{meter(result["move_score"])}<div class="badge {badge_class(result["move_level"])}">{result["move_level"]}</div><div class="note">{html.escape(result["move_match"])}</div></div>',
            unsafe_allow_html=True,
        )
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.markdown("## Peta gerakan dan petanda")
    st.markdown(move_path(result["moves"]), unsafe_allow_html=True)
    for move in result["moves"]:
        st.markdown(
            f'<div class="callout"><strong>{html.escape(move["code"])} · {html.escape(move["name"])}</strong><div class="note">{html.escape(move["function"])}</div></div>',
            unsafe_allow_html=True,
        )
    st.markdown("#### Arahan / makna tersurat")
    st.markdown(tags(result["direct_phrases"], "tag-red"), unsafe_allow_html=True)
    st.markdown("#### Pujukan / makna tersirat")
    st.markdown(tags(result["indirect_phrases"], "tag-amber"), unsafe_allow_html=True)
    st.markdown("#### Pencetus emosi")
    st.markdown(tags(result["emotion_phrases"], "tag-blue"), unsafe_allow_html=True)
    st.markdown("#### Isyarat keselamatan linguistik")
    st.markdown(tags(result["control_phrases"], "tag-green"), unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    guidance = {
        "Rendah": "Petanda rendah dikesan, tetapi sahkan sumber melalui saluran rasmi jika mesej melibatkan wang atau data peribadi.",
        "Sederhana": "Ada petanda yang memerlukan semakan. Jangan bayar, klik pautan atau berkongsi data sebelum pengesahan bebas.",
        "Tinggi": "Petanda manipulatif kuat. Hentikan tindakan, jangan bayar atau kongsi data, dan hubungi pihak rasmi.",
        "Sangat Tinggi": "Petanda sangat kuat. Jangan kongsi OTP/PIN, jangan tekan pautan dan jangan buat bayaran; hubungi bank atau pihak berkuasa melalui saluran rasmi.",
    }
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.markdown("## Cadangan tindakan selamat")
    st.markdown(f'<div class="callout">{html.escape(guidance[result["overall_level"]])}</div>', unsafe_allow_html=True)
    st.caption(result["control_message"])
    st.markdown("</div>", unsafe_allow_html=True)

    with st.expander("Lihat contoh struktur gerakan"):
        st.markdown("**Struktur mesej berisiko**")
        for item in SCAMMOVE_SCAM_EXAMPLES:
            st.markdown(f"- {item}")
        st.markdown("**Struktur mesej kawalan**")
        for item in SCAMMOVE_CONTROL_EXAMPLES:
            st.markdown(f"- {item}")

    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.markdown("## Penafian")
    st.markdown(
        '<div class="disclaimer">ScamAlert ialah prototaip saringan hibrid menggunakan data simulasi terkawal dan peraturan linguistik. Ia belum model AI yang divalidasi, belum mengukur ketepatan populasi, dan tidak mengesahkan bahawa seseorang atau organisasi melakukan penipuan. OCR boleh tersalah membaca imej; semak teks yang diekstrak sebelum analisis. Keputusan tidak menggantikan semakan bank, penyedia perkhidmatan atau pihak berkuasa.</div>',
        unsafe_allow_html=True,
    )
    st.markdown("</div>", unsafe_allow_html=True)

elif check and not message.strip():
    st.warning("Sila tampal teks mesej atau muat naik gambar yang mengandungi teks terlebih dahulu.")
