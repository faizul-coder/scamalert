"""Exercise the complete screenshot -> editable text -> analysis UI path."""

import importlib
import io
import sys
import types
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


def _font(size=42):
    for path in (
        Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
        Path("/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf"),
    ):
        if path.exists():
            return ImageFont.truetype(str(path), size)
    return ImageFont.load_default()


image = Image.new("RGB", (1500, 600), "white")
draw = ImageDraw.Draw(image)
draw.multiline_text(
    (70, 80),
    "Saya sudah bayar dua kali.\n"
    "Mereka masih minta deposit tambahan\n"
    "untuk keluarkan duit hari ini.",
    fill="black",
    font=_font(),
    spacing=24,
)
buffer = io.BytesIO()
image.save(buffer, format="PNG")


class _Upload:
    def getvalue(self):
        return buffer.getvalue()


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
streamlit.session_state = _SessionState(message_input="")
streamlit.set_page_config = lambda *args, **kwargs: None
streamlit.markdown = lambda *args, **kwargs: None
streamlit.caption = lambda *args, **kwargs: None
streamlit.info = lambda *args, **kwargs: None
streamlit.warning = lambda *args, **kwargs: None
streamlit.error = lambda *args, **kwargs: None
streamlit.success = lambda *args, **kwargs: None
streamlit.toast = lambda *args, **kwargs: None
streamlit.image = lambda *args, **kwargs: None
streamlit.selectbox = lambda *args, **kwargs: args[1][0]
streamlit.file_uploader = lambda *args, **kwargs: _Upload()
streamlit.button = lambda *args, **kwargs: True
streamlit.text_area = lambda *args, **kwargs: streamlit.session_state["message_input"]
streamlit.columns = lambda spec, *args, **kwargs: [
    _Context() for _ in range(spec if isinstance(spec, int) else len(spec))
]
streamlit.expander = lambda *args, **kwargs: _Context()
streamlit.container = lambda *args, **kwargs: _Context()
streamlit.spinner = lambda *args, **kwargs: _Context()

sys.modules["streamlit"] = streamlit
importlib.import_module("app")

visible_text = streamlit.session_state.get("message_input", "")
assert visible_text == streamlit.session_state["ocr_result"]["text"]
assert "deposit tambahan" in visible_text.lower()

from scamalert_core import analyse_text

result = analyse_text(visible_text)
assert result["overall_score"] >= 50, result
print(
    "OCR UI smoke test passed: screenshot text populated the editable field "
    f"and produced {result['overall_score']}/100 ({result['overall_level']})."
)
