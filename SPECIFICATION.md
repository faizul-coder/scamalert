# ScamAlert Demo 1.3 — technical specification

## Public decision states

| State | Meaning |
|---|---|
| Sangat Tinggi | multiple strong risk cues co-occur |
| Tinggi | strong risk combination detected |
| Perlu Berhati-hati | some cues require independent verification |
| Rendah | low internal score plus identifiable control/safety evidence |
| Bukti Tidak Mencukupi | low score without enough evidence to claim low risk |

## Detection components

| Component | Implementation |
|---|---|
| OCR | local Tesseract, Malay/English, grayscale/inversion/binary candidates |
| Reference data | 90 deduplicated binary templates with audit metadata |
| Similarity | word 1–2 gram and character 3–5 gram TF-IDF cosine similarity |
| Linguistic layer | direct/indirect acts, emotion triggers and strategic moves |
| Scenario layer | multi-cue rules for nine common scam families plus victim reports |
| Fusion | evidence-dependent weighting with dangerous-combination floors |
| Abstention | insufficient evidence is distinct from a low-risk decision |

## Public interface contract

- The main path contains one editable text area, one optional uploader and one
  **Semak mesej** button.
- A new screenshot triggers OCR automatically; the user reviews the editable
  text before analysis.
- The public result contains only the screening state, category when available
  and **Cadangan Tindakan**.
- Decision explanations, scores, similarity, linguistic subscores, nearest
  references, OCR details, technical expanders and the safety footer are not
  rendered in the public interface.

## Failure and privacy behaviour

- Missing reference data produces a visible rule-only warning.
- Missing OCR dependencies or invalid images produce a visible error; manual
  input remains usable.
- Uploads are limited to 8 MB and 12 million decoded pixels.
- Images and text remain within the running Streamlit process and are not sent
  to an external OCR API by this code.
- Empty input is rejected.

## Validation status

Automated tests establish reproducible wiring and regression behaviour. They
do not replace independent validation using human-adjudicated real-world data.
