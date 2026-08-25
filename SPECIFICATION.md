# ScamAlert Demo 1.2 — technical specification

## Purpose

Provide a prospect-facing, offline-capable early-warning demonstration for
Malay/English digital messages while keeping every source of evidence visible.

## Components

| Component | Implementation | Output |
|---|---|---|
| Screenshot OCR | local Tesseract CLI, `msa+eng`, grayscale + binary Pillow preprocessing, PSM 6/11 candidates | editable extracted text, mean OCR word confidence and visible warnings |
| Reference data | `data/reference_data.json` | 90 deduplicated binary templates plus audit metadata |
| Similarity | word TF-IDF 1–2 grams + character TF-IDF 3–5 grams, cosine similarity | risk/control matches, similarity and data index |
| Speech acts | transparent regular-expression rules | direct/indirect indicators and sub-score |
| Emotion | selected linguistic triggers with interaction rules | emotion indicators and sub-score |
| Strategic moves | M1–M6 ordered risk indicators | move path and sub-score |
| Fusion | evidence-dependent weighted average with critical safety floors | hybrid risk-indicator index |

## Fusion contract

- The linguistic rule index is always available.
- Reference data influence is zero when similarity is insufficient or when risk
  and control signals are ambiguous.
- Moderate/strong, non-ambiguous data evidence receives a continuous weight up
  to 55%.
- Moderate lexical similarity alone cannot move a non-critical rule result
  across the 50-point high-risk boundary; this reduces false escalation from
  ordinary payment wording in the small controlled reference set.
- Critical dangerous combinations such as an OTP request plus an account threat
  retain a documented minimum warning floor.
- Every result exposes the rule index, data index, data weight, best similarity,
  nearest risk references and nearest controls.

## Failure behaviour

- Missing, corrupt or inconsistent reference data produces a visible warning
  and rule-only mode; the failure is never silently presented as data-backed.
- Missing Tesseract/language data, invalid files, oversized images, timeouts and
  blank OCR results produce visible errors; manual text input remains available.
- OCR never triggers risk analysis automatically. The user reviews the editable
  text and explicitly clicks **Semak Mesej**.
- Empty input is rejected in the interface.
- Out-of-domain input causes the data layer to abstain.

## Security and privacy scope

- No message is transmitted by this code; analysis occurs within the running
  Streamlit process.
- Uploads are limited to 8 MB and 12 million decoded pixels. PNG and JPEG bytes
  are verified with Pillow, EXIF orientation is corrected and temporary OCR
  files are removed automatically.
- The demo should not be used with real OTPs, account numbers or identity data.
- Images and OCR text are not written to application logs or global caches.

## Validation status

The automated suite is a regression and wiring suite.  It does not replace an
independent, held-out validation study on adjudicated real-world messages.
