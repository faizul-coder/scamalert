# ScamAlert Demo 1.2 — QA report

Date: 2026-08-25

## Automated result

- Python compile check: passed.
- Core, similarity and OCR unit tests: 31/31 passed.
- Pasted-text UI-path smoke test: passed.
- Screenshot → editable text → analysis UI-path smoke test: passed.
- Screenshot replacement / stale OCR-state smoke test: passed.
- Reference metadata reconciliation: passed.
- Runtime template connectivity: 90/90 templates returned themselves as the
  nearest same-class reference.
- Runtime exact-text connectivity: 164/164 globally unique source texts were
  directionally aligned with their binary source class at the 50-point screening
  boundary.

The two connectivity results use the same controlled references that build the
index.  They prove that the data are loaded and influence runtime results; they
are not independent accuracy, recall or precision estimates.

## Safety regressions passed

- `pinjaman` does not trigger the word-boundary rule for `PIN`.
- “Jangan kongsi OTP” remains low risk.
- Safety warnings for bank details, identity cards and account numbers remain
  low risk.
- A safety opening clause does not mask a later payment or link command.
- Repeated-payment narratives from a victim receive a high warning.
- Out-of-domain text causes the data layer to abstain with zero weight.
- Missing reference data raises a visible failure condition rather than a silent
  data-backed claim.

## OCR regressions passed

- Clear Malay/English risk screenshot produces editable text and a high warning.
- A victim report about repeated payment produces a high warning after OCR.
- A dark-mode safety warning is inverted, read and remains low risk.
- Invalid, tiny, blank and excessive-resolution images are rejected visibly.
- Missing Tesseract, OCR runtime failure and OCR timeout do not produce a risk
  score or disable manual input.
- Mean OCR word confidence is kept separate from the ScamAlert risk index.
- Dark screenshots with coloured chat bubbles are recovered through the binary
  OCR candidate.

## Bilingual and false-positive regressions passed

- English bank/OTP scam, English loan/fee scam and Malay-English code-switching
  all cross the high-risk boundary.
- English and Malay victim reports with an explicit repeated-payment demand
  cross the high-risk boundary.
- English safety negations remain low.
- Ordinary lunch transfer, rental deposit and bill-payment examples do not
  cross the high-risk boundary solely because they contain money plus urgency.
- A registered-company invoice payment remains below the high-risk boundary.

## Remaining validation gap

No independent real-world test set is available.  External performance claims
must wait for human-adjudicated data, held-out evaluation and error analysis.

## Independent adversarial retest

A separate code-review/test pass reproduced and verified the following after
the final fixes: dark coloured chat bubbles 89/Sangat Tinggi; English scam
93/Sangat Tinggi; code-switch 75/Sangat Tinggi; English safety warning 8/Rendah;
five natural multi-sentence Malay/English victim reports 71–72/Tinggi; and a
legitimate registered-company invoice request 45/Sederhana. These are targeted
regression examples, not estimates of population accuracy.
