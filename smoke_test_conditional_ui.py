"""Verify that detailed analysis is conditional on sufficient evidence."""

import importlib
import sys
import types


class _Context:
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, traceback):
        return False


class _SessionState(dict):
    pass


streamlit = types.ModuleType("streamlit")
streamlit.session_state = _SessionState()
streamlit.set_page_config = lambda *args, **kwargs: None
streamlit.caption = lambda *args, **kwargs: None
streamlit.info = lambda *args, **kwargs: None
streamlit.warning = lambda *args, **kwargs: None
streamlit.error = lambda *args, **kwargs: None
streamlit.success = lambda *args, **kwargs: None
streamlit.toast = lambda *args, **kwargs: None
streamlit.image = lambda *args, **kwargs: None
streamlit.selectbox = lambda *args, **kwargs: args[1][0] if len(args) > 1 else None
streamlit.file_uploader = lambda *args, **kwargs: None
streamlit.button = lambda *args, **kwargs: True
streamlit.columns = lambda spec, *args, **kwargs: [
    _Context() for _ in range(spec if isinstance(spec, int) else len(spec))
]
streamlit.expander = lambda *args, **kwargs: _Context()
streamlit.container = lambda *args, **kwargs: _Context()
streamlit.spinner = lambda *args, **kwargs: _Context()
sys.modules["streamlit"] = streamlit


DETAIL_LABELS = (
    "Skor Risiko",
    "Frasa Tersurat",
    "Frasa Tersirat",
    "Pencetus Emosi",
    "Analisis Gerakan",
    "Jenis Penipuan",
)


def render_for(message):
    rendered = []
    streamlit.session_state = _SessionState(message_input=message)
    streamlit.markdown = lambda body, *args, **kwargs: rendered.append(str(body))
    streamlit.text_area = lambda *args, **kwargs: streamlit.session_state["message_input"]
    sys.modules.pop("app", None)
    importlib.import_module("app")
    return "\n".join(rendered), streamlit.session_state["analysis_result"]


insufficient_text, insufficient_result = render_for("Baik.")
assert insufficient_result["decision_state"] == "insufficient"
assert "Mesej Tidak Mencukupi" in insufficient_text
assert "terlalu pendek" in insufficient_text
assert "Cadangan Tindakan" in insufficient_text
for label in DETAIL_LABELS:
    assert label not in insufficient_text, label


low_text, low_result = render_for(
    "Pihak bank tidak pernah meminta OTP. Jangan kongsi OTP atau PIN dan semak melalui aplikasi rasmi."
)
assert low_result["decision_state"] == "low"
assert "Cadangan Tindakan" in low_text
for label in DETAIL_LABELS:
    assert label in low_text, label


print(
    "Conditional UI smoke test passed: insufficient evidence is concise and "
    "a low-risk assessed message retains the full analysis."
)
