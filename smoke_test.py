"""Offline smoke test for environments without Streamlit installed.

The stub exercises the complete UI path with one high-risk message.  Functional
analysis tests live under ``tests/``.
"""

import importlib
import sys
import types


class _Context:
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, traceback):
        return False

    def metric(self, *args, **kwargs):
        return None


class _SessionState(dict):
    pass


streamlit = types.ModuleType("streamlit")
rendered_markdown = []
streamlit.session_state = _SessionState(
    message_input=(
        "Pihak bank mengesan aktiviti luar biasa. Berikan OTP sekarang. "
        "Jika gagal, akaun anda akan dibekukan dalam 15 minit."
    )
)
streamlit.set_page_config = lambda *args, **kwargs: None
streamlit.markdown = lambda body, *args, **kwargs: rendered_markdown.append(str(body))
streamlit.caption = lambda *args, **kwargs: None
streamlit.info = lambda *args, **kwargs: None
streamlit.warning = lambda *args, **kwargs: None
streamlit.error = lambda *args, **kwargs: None
streamlit.success = lambda *args, **kwargs: None
streamlit.toast = lambda *args, **kwargs: None
streamlit.image = lambda *args, **kwargs: None
streamlit.selectbox = lambda *args, **kwargs: args[1][0] if len(args) > 1 else None
streamlit.text_area = lambda *args, **kwargs: streamlit.session_state["message_input"]
streamlit.file_uploader = lambda *args, **kwargs: None
streamlit.button = lambda *args, **kwargs: True
streamlit.columns = lambda spec, *args, **kwargs: [
    _Context() for _ in range(spec if isinstance(spec, int) else len(spec))
]
streamlit.expander = lambda *args, **kwargs: _Context()
streamlit.container = lambda *args, **kwargs: _Context()
streamlit.spinner = lambda *args, **kwargs: _Context()

sys.modules["streamlit"] = streamlit
importlib.import_module("app")
rendered_text = "\n".join(rendered_markdown)
assert '[data-testid^="stFileUploaderFile"] {' in rendered_text
assert 'visibility:hidden !important;' in rendered_text
assert '[data-testid="stFileUploaderDropzone"] button {' in rendered_text
result = streamlit.session_state["analysis_result"]
for required_label in (
    "Skor Risiko",
    "Frasa Tersurat",
    "Frasa Tersirat",
    "Pencetus Emosi",
    "Analisis Gerakan",
    "Jenis Penipuan",
    "Cadangan Tindakan",
):
    assert required_label in rendered_text, required_label
assert result["threat_category"] in rendered_text
assert "Jenis Lakuan Pertuturan" not in rendered_text
assert rendered_text.count("Analisis Gerakan") == 1
assert result["decision_summary"] not in rendered_text
assert result["risk_reasons"][0] not in rendered_text
for removed_label in (
    "Mengapa keputusan ini diberikan?",
    "Tindakan disarankan",
    "Lihat butiran analisis",
    "Had sistem dan privasi",
    "Saringan awal sahaja.",
):
    assert removed_label not in rendered_text, removed_label
print("UI smoke test passed: data loaded and complete result path rendered.")
