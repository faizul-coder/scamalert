# OCR method and deployment note

## Runtime

`scamalert_ocr.py` calls the local Tesseract executable through a fixed
subprocess argument list. It selects `msa+eng` when both Malay and English data
are installed, falling back visibly to either available language. No external
OCR service is called.

The image pipeline verifies PNG/JPEG bytes, applies EXIF orientation, flattens
transparency onto white, converts to grayscale, increases contrast, inverts
dark-mode screenshots, resizes conservatively, sharpens and adds a white border.
Two candidates are compared: grayscale with Tesseract PSM 6, and a binary
threshold image with PSM 11. The binary candidate recovers white text inside
coloured bubbles on dark chat interfaces. Each OCR process has a 12-second
timeout.

## Safety limits

- Upload: maximum 8 MB.
- Decoded image: maximum 12 million pixels.
- Accepted formats: PNG and JPEG.
- Pillow decompression-bomb warnings/errors are rejected.
- Temporary files are isolated and deleted automatically.
- Images and extracted text are not stored in a global cache or application log.

## Decision contract

OCR extraction and scam-risk analysis are separate actions. Extracted text is
placed in the same editable message box used for pasted text. The user reviews
it and clicks **Semak Mesej**. OCR failure or blank OCR output never becomes a
low-risk score.

OCR confidence is the mean Tesseract word confidence. It describes recognition
quality only; it is not a probability of fraud and is not directly used as the
ScamAlert risk index.

## Deployment

`requirements.txt` installs Pillow and Streamlit. `packages.txt` installs the
Tesseract engine plus Malay (`msa`), English (`eng`) and orientation (`osd`)
language data on Streamlit Community Cloud. `.streamlit/config.toml` enforces
the 8 MB upload limit.
