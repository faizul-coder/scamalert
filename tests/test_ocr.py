import io
import subprocess
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from PIL import Image, ImageDraw, ImageFont

from scamalert_core import analyse_text
from scamalert_ocr import (
    OCRInputError,
    OCRProcessingError,
    OCRUnavailableError,
    _run_tesseract,
    extract_text_from_image,
    get_ocr_status,
)


def _font(size=46):
    candidates = [
        Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
        Path("/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf"),
    ]
    for candidate in candidates:
        if candidate.exists():
            return ImageFont.truetype(str(candidate), size)
    return ImageFont.load_default()


def _image_bytes(lines, *, dark=False):
    background = "#111827" if dark else "white"
    foreground = "white" if dark else "black"
    image = Image.new("RGB", (1500, 620), background)
    draw = ImageDraw.Draw(image)
    draw.multiline_text(
        (70, 80),
        "\n".join(lines),
        fill=foreground,
        font=_font(),
        spacing=24,
    )
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    return buffer.getvalue()


def _dark_chat_bubble_bytes():
    image = Image.new("RGB", (1080, 1500), (12, 25, 35))
    draw = ImageDraw.Draw(image)
    font = _font(31)
    bubbles = [
        ((65, 120, 930, 410), "Permohonan pinjaman anda diluluskan.\nBayar caj proses RM300 sekarang."),
        ((150, 500, 1015, 790), "Wang RM5,000 akan dilepaskan\nhari ini selepas bayaran."),
    ]
    for box, text in bubbles:
        draw.rounded_rectangle(box, radius=28, fill=(0, 92, 75))
        draw.multiline_text(
            (box[0] + 35, box[1] + 45),
            text,
            fill="white",
            font=font,
            spacing=18,
        )
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    return buffer.getvalue()


@unittest.skipUnless(get_ocr_status()["available"], "Tesseract not installed")
class OCRIntegrationTests(unittest.TestCase):
    def test_light_scam_screenshot_flows_into_high_risk_analysis(self):
        image_bytes = _image_bytes(
            [
                "Permohonan pinjaman anda telah diluluskan.",
                "Bayar caj proses RM300 sekarang.",
                "Wang akan dilepaskan hari ini.",
            ]
        )
        ocr = extract_text_from_image(image_bytes)
        normalized = ocr["text"].lower()
        self.assertIn("bayar", normalized)
        self.assertIn("caj proses", normalized)
        self.assertGreaterEqual(ocr["word_count"], 8)
        result = analyse_text(ocr["text"])
        self.assertGreaterEqual(result["overall_score"], 50)

    def test_dark_safety_screenshot_is_inverted_and_stays_low(self):
        image_bytes = _image_bytes(
            [
                "Pihak bank tidak pernah meminta OTP.",
                "Jangan kongsi OTP atau PIN dengan sesiapa.",
                "Semak melalui aplikasi rasmi.",
            ],
            dark=True,
        )
        ocr = extract_text_from_image(image_bytes)
        self.assertTrue(ocr["dark_mode_inverted"])
        self.assertIn("jangan kongsi", ocr["text"].lower())
        result = analyse_text(ocr["text"])
        self.assertLessEqual(result["overall_score"], 24)

    def test_victim_report_screenshot_receives_high_warning(self):
        image_bytes = _image_bytes(
            [
                "Saya sudah bayar dua kali.",
                "Mereka masih minta deposit tambahan",
                "untuk keluarkan duit hari ini.",
            ]
        )
        ocr = extract_text_from_image(image_bytes)
        self.assertIn("deposit tambahan", ocr["text"].lower())
        result = analyse_text(ocr["text"])
        self.assertGreaterEqual(result["overall_score"], 50)

    def test_dark_coloured_chat_bubbles_use_binary_candidate(self):
        ocr = extract_text_from_image(_dark_chat_bubble_bytes())
        self.assertEqual(ocr["preprocessing"], "binary")
        self.assertIn("caj proses", ocr["text"].lower())
        result = analyse_text(ocr["text"])
        self.assertGreaterEqual(result["overall_score"], 50)

    def test_invalid_image_is_rejected(self):
        with self.assertRaises(OCRInputError):
            extract_text_from_image(b"this is not an image")

    def test_tiny_image_is_rejected(self):
        buffer = io.BytesIO()
        Image.new("RGB", (40, 40), "white").save(buffer, format="PNG")
        with self.assertRaises(OCRInputError):
            extract_text_from_image(buffer.getvalue())

    def test_blank_image_does_not_produce_a_risk_score(self):
        buffer = io.BytesIO()
        Image.new("RGB", (1200, 500), "white").save(buffer, format="PNG")
        with self.assertRaises(OCRProcessingError):
            extract_text_from_image(buffer.getvalue())

    def test_decompression_bomb_dimensions_are_rejected(self):
        buffer = io.BytesIO()
        Image.new("RGB", (4000, 4000), "white").save(buffer, format="PNG")
        with self.assertRaises(OCRInputError):
            extract_text_from_image(buffer.getvalue())


class OCRAvailabilityTests(unittest.TestCase):
    def test_missing_tesseract_fails_explicitly(self):
        command = "definitely-not-a-real-tesseract-command"
        self.assertFalse(get_ocr_status(command)["available"])
        with self.assertRaises(OCRUnavailableError):
            extract_text_from_image(b"not-used", tesseract_command=command)

    @patch("scamalert_ocr.subprocess.run")
    def test_tesseract_runtime_failure_is_explicit(self, run):
        run.return_value = SimpleNamespace(
            returncode=1,
            stdout="",
            stderr="Error opening data file",
        )
        with self.assertRaises(OCRProcessingError):
            _run_tesseract(Path("unused.png"), "tesseract", "eng", 6)

    @patch("scamalert_ocr.subprocess.run")
    def test_tesseract_timeout_is_explicit(self, run):
        run.side_effect = subprocess.TimeoutExpired(cmd="tesseract", timeout=12)
        with self.assertRaises(OCRProcessingError):
            _run_tesseract(Path("unused.png"), "tesseract", "eng", 6)


if __name__ == "__main__":
    unittest.main()
