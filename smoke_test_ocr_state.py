"""Verify that replacing an OCR upload cannot silently analyse stale OCR text."""

import importlib
import io
import sys
import types
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


def _font(size=38):
    path = Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf")
    return ImageFont.truetype(str(path), size) if path.exists() else ImageFont.load_default()


def _screenshot(text):
    image = Image.new("RGB", (1400, 460), "white")
    ImageDraw.Draw(image).multiline_text((60, 70), text, fill="black", font=_font(), spacing=20)
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    return buffer.getvalue()


class _Upload:
    def __init__(self, payload):
        self.payload = payload

    def getvalue(self):
        return self.payload


class _Context:
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, traceback):
        return False

    def metric(self, *args, **kwargs):
        return None


class _SessionState(dict):
    pass


runtime = {
    "upload": _screenshot("Bayar caj proses RM300 sekarang.\nWang akan dilepaskan hari ini."),
}
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
streamlit.file_uploader = lambda *args, **kwargs: _Upload(runtime["upload"])
streamlit.button = lambda *args, **kwargs: False
streamlit.text_area = lambda *args, **kwargs: streamlit.session_state["message_input"]
streamlit.columns = lambda spec, *args, **kwargs: [
    _Context() for _ in range(spec if isinstance(spec, int) else len(spec))
]
streamlit.expander = lambda *args, **kwargs: _Context()
streamlit.container = lambda *args, **kwargs: _Context()
streamlit.spinner = lambda *args, **kwargs: _Context()

sys.modules["streamlit"] = streamlit
app = importlib.import_module("app")
first_text = streamlit.session_state["message_input"]
assert first_text and first_text == streamlit.session_state["ocr_result"]["text"]

# Replacing the screenshot must automatically replace OCR text from image A;
# stale text must never be analysed as though it came from image B.
runtime["upload"] = _screenshot(
    "Pihak bank tidak pernah meminta OTP.\nJangan kongsi OTP dengan sesiapa."
)
importlib.reload(app)
second_text = streamlit.session_state["message_input"]
assert second_text == streamlit.session_state["ocr_result"]["text"]
assert second_text != first_text
assert "jangan kongsi" in second_text.lower()

print("OCR state smoke test passed: replacing an image replaced stale OCR text automatically.")
