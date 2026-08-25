# ScamAlert NICE 2026 — OCR + Hybrid Data-Backed Demo 1.2

This package corrects the central defect in the earlier prototype: the
application now loads and uses reference data at runtime. It combines a
deduplicated reference-similarity index with explainable linguistic rules and
local screenshot OCR.

## Run locally

```bash
python -m pip install -r requirements.txt
streamlit run app.py
```

OCR also requires the Tesseract executable and Malay/English language data. On
Debian/Ubuntu:

```bash
sudo apt-get install tesseract-ocr tesseract-ocr-eng tesseract-ocr-msa tesseract-ocr-osd
```

Streamlit Community Cloud installs these automatically from `packages.txt`.
The package does not send screenshots or extracted text to an external OCR API.
For the exact live-release sequence, follow `DEPLOY_TONIGHT.md`.

## Screenshot workflow

1. Upload one PNG/JPG/JPEG screenshot, maximum 8 MB.
2. Click **Ekstrak teks daripada gambar**.
3. Review and, if needed, correct the extracted text in the editable message
   box.
4. Click **Semak Mesej** to run the same hybrid analysis used for pasted text.

Two non-sensitive synthetic screenshots are included under `demo_assets/` for
pre-event testing and the live demonstration.

The average OCR word-confidence value measures text-recognition quality. It is not
the ScamAlert risk score. OCR failure is shown explicitly and never converted
into a low-risk result.

## What the application really uses

- 6,072 source rows audited across the three uploaded workbooks.
- 164 globally unique texts: 116 risk and 48 control.
- 90 normalized reference templates used at runtime: 57 risk and 33 control.
- One vote per normalized template; repeated synthetic variants do not receive
  additional weight.
- 83 unique texts have inconsistent source risk-level labels.  Those levels are
  retained for audit only and are not used as prediction targets.

The data are controlled synthetic examples, not real-world ground truth.  The
hybrid index is not a probability, a measured accuracy, or a legal conclusion.

## Runtime method

1. `data/reference_data.json` is opened when `scamalert_core.py` loads.
2. The reference matcher creates word 1–2 gram and character 3–5 gram TF-IDF
   representations in pure Python.
3. The closest distinct risk and control templates are compared.
4. Weak or ambiguous data evidence receives zero weight.
5. A strong, unambiguous match may contribute at most 55% of the hybrid index.
6. Linguistic rules provide separate, visible scores for speech acts, emotion
   triggers and strategic moves.

## Verification

```bash
python -m unittest discover -s tests -v
python smoke_test.py
python smoke_test_ocr_ui.py
```

The tests verify runtime loading, all 90 template connections, safe negation,
mixed safety-bait clauses, out-of-domain abstention, the `PIN`/`pinjaman`
boundary, deterministic similarity, OCR light/dark screenshots (including
coloured chat bubbles), victim and
safety messages, OCR failures, both analysis UI paths and stale-upload state.
Alignment with the
same controlled references is a wiring/regression check, not independent model
validation.

## Important limitations

- OCR quality varies with cropping, font size, blur and screenshot layout; users
  must review the extracted text before analysis.
- The Telegram corpus is not used for scoring because it has not been fully
  human-adjudicated.
- No claim of validated AI, population accuracy, recall or precision is made.
- Real-world validation requires independently sampled, adjudicated messages
  and a held-out evaluation design.
