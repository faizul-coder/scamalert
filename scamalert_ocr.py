"""Local OCR support for ScamAlert screenshots.

Images are processed inside the running application with Tesseract.  No image
or extracted text is sent to an external API by this module.
"""

from __future__ import annotations

import csv
import io
import re
import shutil
import subprocess
import tempfile
import warnings
from functools import lru_cache
from pathlib import Path
from statistics import mean
from typing import Dict, Iterable, List, Tuple

from PIL import Image, ImageFilter, ImageOps, ImageStat, UnidentifiedImageError


MAX_UPLOAD_BYTES = 8 * 1024 * 1024
MAX_IMAGE_PIXELS = 12_000_000
OCR_TIMEOUT_SECONDS = 12
SUPPORTED_FORMATS = {"PNG", "JPEG"}

Image.MAX_IMAGE_PIXELS = MAX_IMAGE_PIXELS


class OCRUnavailableError(RuntimeError):
    """Raised when the Tesseract executable or language data are unavailable."""


class OCRInputError(ValueError):
    """Raised when an upload is not a safe, supported image."""


class OCRProcessingError(RuntimeError):
    """Raised when OCR runs but cannot return usable text."""


@lru_cache(maxsize=4)
def get_ocr_status(tesseract_command: str = "tesseract") -> Dict[str, object]:
    executable = shutil.which(tesseract_command)
    if not executable:
        return {
            "available": False,
            "executable": None,
            "languages": [],
            "selected_language": None,
            "error": "Enjin Tesseract tidak ditemui.",
        }

    try:
        version_run = subprocess.run(
            [executable, "--version"],
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        )
        language_run = subprocess.run(
            [executable, "--list-langs"],
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        return {
            "available": False,
            "executable": executable,
            "languages": [],
            "selected_language": None,
            "error": f"Tesseract tidak dapat dimulakan: {exc}",
        }

    languages = sorted(
        line.strip()
        for line in language_run.stdout.splitlines()
        if line.strip() and not line.lower().startswith("list of available")
    )
    if "msa" in languages and "eng" in languages:
        selected_language = "msa+eng"
    elif "msa" in languages:
        selected_language = "msa"
    elif "eng" in languages:
        selected_language = "eng"
    else:
        selected_language = None

    version_line = (version_run.stdout or version_run.stderr).splitlines()
    available = bool(selected_language and version_run.returncode == 0)
    return {
        "available": available,
        "executable": executable,
        "languages": languages,
        "selected_language": selected_language,
        "version": version_line[0].strip() if version_line else "unknown",
        "error": None if available else "Tiada data bahasa OCR Melayu atau Inggeris.",
    }


def _open_and_preprocess(image_bytes: bytes) -> Tuple[Image.Image, Dict[str, object]]:
    if not image_bytes:
        raise OCRInputError("Fail imej kosong.")
    if len(image_bytes) > MAX_UPLOAD_BYTES:
        raise OCRInputError("Saiz gambar melebihi had 8 MB.")

    try:
        # Treat Pillow's decompression-bomb warning as a hard failure before
        # decoding.  An 8 MB compressed upload can otherwise expand into an
        # unexpectedly large in-memory image.
        with warnings.catch_warnings():
            warnings.simplefilter("error", Image.DecompressionBombWarning)
            with Image.open(io.BytesIO(image_bytes)) as probe:
                image_format = (probe.format or "").upper()
                probe.verify()
            image = Image.open(io.BytesIO(image_bytes))
            image.load()
    except (Image.DecompressionBombError, Image.DecompressionBombWarning) as exc:
        raise OCRInputError(
            "Resolusi gambar terlalu besar untuk diproses dengan selamat."
        ) from exc
    except (UnidentifiedImageError, OSError, ValueError) as exc:
        raise OCRInputError("Fail yang dimuat naik bukan gambar yang sah.") from exc

    if image_format not in SUPPORTED_FORMATS:
        raise OCRInputError("Format gambar tidak disokong. Gunakan PNG, JPG atau JPEG.")

    image = ImageOps.exif_transpose(image)
    original_width, original_height = image.size
    if original_width < 80 or original_height < 80:
        raise OCRInputError("Resolusi gambar terlalu kecil untuk OCR.")
    if original_width * original_height > MAX_IMAGE_PIXELS:
        raise OCRInputError("Resolusi gambar terlalu besar untuk diproses dengan selamat.")

    if "A" in image.getbands():
        rgba = image.convert("RGBA")
        background = Image.new("RGBA", rgba.size, "white")
        background.alpha_composite(rgba)
        image = background.convert("RGB")
    else:
        image = image.convert("RGB")

    image = ImageOps.grayscale(image)
    image = ImageOps.autocontrast(image, cutoff=1)

    # Dark-mode chat screenshots work better after inversion.
    mean_brightness = float(ImageStat.Stat(image).mean[0])
    inverted = mean_brightness < 105
    if inverted:
        image = ImageOps.invert(image)

    width, height = image.size
    if width < 1500:
        scale = min(2.5, 1500 / width)
        image = image.resize(
            (max(1, round(width * scale)), max(1, round(height * scale))),
            Image.Resampling.LANCZOS,
        )
    elif width > 3200:
        scale = 3200 / width
        image = image.resize(
            (3200, max(1, round(height * scale))),
            Image.Resampling.LANCZOS,
        )

    image = ImageOps.expand(image.filter(ImageFilter.SHARPEN), border=24, fill="white")
    return image, {
        "format": image_format,
        "original_size": [original_width, original_height],
        "processed_size": list(image.size),
        "dark_mode_inverted": inverted,
        "upload_bytes": len(image_bytes),
    }


def _parse_tsv(tsv_text: str) -> Tuple[str, List[float], int]:
    reader = csv.DictReader(io.StringIO(tsv_text), delimiter="\t")
    lines: Dict[Tuple[str, str, str, str], List[Tuple[int, str]]] = {}
    confidences: List[float] = []
    word_count = 0

    for row in reader:
        text = (row.get("text") or "").strip()
        if not text:
            continue
        try:
            confidence = float(row.get("conf") or -1)
        except ValueError:
            confidence = -1
        if confidence >= 0:
            confidences.append(confidence)
        key = (
            row.get("page_num") or "0",
            row.get("block_num") or "0",
            row.get("par_num") or "0",
            row.get("line_num") or "0",
        )
        try:
            word_number = int(row.get("word_num") or 0)
        except ValueError:
            word_number = 0
        lines.setdefault(key, []).append((word_number, text))
        word_count += 1

    output_lines = [
        " ".join(word for _, word in sorted(words, key=lambda item: item[0]))
        for words in lines.values()
    ]
    text = "\n".join(line for line in output_lines if line.strip())
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text).strip()
    return text, confidences, word_count


def _quality_score(text: str, confidences: Iterable[float], word_count: int) -> float:
    confidence_values = list(confidences)
    average_confidence = mean(confidence_values) if confidence_values else 0.0
    alphanumeric = sum(character.isalnum() for character in text)
    visible = max(1, sum(not character.isspace() for character in text))
    readable_ratio = alphanumeric / visible
    return average_confidence + min(word_count, 80) * 0.12 + readable_ratio * 5


def _run_tesseract(
    image_path: Path,
    executable: str,
    language: str,
    page_segmentation_mode: int,
) -> Dict[str, object]:
    try:
        process = subprocess.run(
            [
                executable,
                str(image_path),
                "stdout",
                "-l",
                language,
                "--oem",
                "1",
                "--psm",
                str(page_segmentation_mode),
                "tsv",
            ],
            capture_output=True,
            text=True,
            timeout=OCR_TIMEOUT_SECONDS,
            check=False,
        )
    except subprocess.TimeoutExpired as exc:
        raise OCRProcessingError("OCR mengambil masa terlalu lama dan dihentikan.") from exc
    except OSError as exc:
        raise OCRUnavailableError("Enjin OCR tidak dapat dimulakan.") from exc

    if process.returncode != 0:
        detail = (process.stderr or "").strip().splitlines()
        raise OCRProcessingError(
            "OCR gagal memproses gambar."
            + (f" {detail[-1]}" if detail else "")
        )

    text, confidences, word_count = _parse_tsv(process.stdout)
    average_confidence = mean(confidences) if confidences else 0.0
    return {
        "text": text,
        "confidence": round(float(average_confidence), 1),
        "word_count": int(word_count),
        "psm": int(page_segmentation_mode),
        "quality_score": _quality_score(text, confidences, word_count),
    }


def extract_text_from_image(
    image_bytes: bytes,
    *,
    tesseract_command: str = "tesseract",
) -> Dict[str, object]:
    status = get_ocr_status(tesseract_command)
    if not status["available"]:
        raise OCRUnavailableError(str(status.get("error") or "Enjin OCR tidak tersedia."))

    image, image_metadata = _open_and_preprocess(image_bytes)
    with tempfile.TemporaryDirectory(prefix="scamalert-ocr-") as directory:
        image_path = Path(directory) / "prepared.png"
        image.save(image_path, format="PNG", optimize=True)
        first = _run_tesseract(
            image_path,
            str(status["executable"]),
            str(status["selected_language"]),
            6,
        )
        first["preprocessing"] = "grayscale"

        # A binary candidate is essential for dark chat interfaces with coloured
        # message bubbles: grayscale alone can leave too little contrast between
        # white text and the bubble after inversion.
        binary_path = Path(directory) / "prepared_binary.png"
        binary_image = image.point(lambda value: 255 if value > 100 else 0)
        binary_image.save(binary_path, format="PNG", optimize=True)
        binary = _run_tesseract(
            binary_path,
            str(status["executable"]),
            str(status["selected_language"]),
            11,
        )
        binary["preprocessing"] = "binary"
        candidates = [first, binary]

    best = max(candidates, key=lambda item: float(item["quality_score"]))
    text = str(best["text"]).strip()
    if len(re.sub(r"\W", "", text, flags=re.UNICODE)) < 5:
        raise OCRProcessingError(
            "Tiada teks yang mencukupi dapat dibaca. Cuba gambar yang lebih jelas atau tampal teks secara manual."
        )

    warning_messages = []
    if float(best["confidence"]) < 45:
        warning_messages.append(
            "Purata keyakinan OCR perkataan rendah. Semak dan betulkan teks sebelum analisis."
        )
    if status["selected_language"] == "eng":
        warning_messages.append(
            "Model Bahasa Melayu tidak tersedia pada pelayan ini; OCR menggunakan model Inggeris untuk teks Rumi."
        )

    return {
        "text": text,
        "confidence": best["confidence"],
        "word_count": best["word_count"],
        "language": status["selected_language"],
        "psm": best["psm"],
        "preprocessing": best["preprocessing"],
        "warning": " ".join(warning_messages) or None,
        **image_metadata,
    }
