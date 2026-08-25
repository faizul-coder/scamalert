# NICE 2026 demonstration guide

## 60-second story

“ScamAlert screens suspicious messages before a user pays, clicks or shares
sensitive data.  This version is deliberately transparent: it shows the
linguistic warning signs, the closest risk reference, the closest control
reference and exactly how much the data influenced the final index.  Weak or
conflicting data evidence is rejected rather than forced into a prediction.”

## Recommended live sequence

1. Open **Peringatan keselamatan sebenar**.  Point out the low score, the
   closest control reference and the safety-negation handling.
2. Upload `demo_assets/01_risk_dark_chat.png`, click
   **Ekstrak teks daripada gambar**, show that the text is editable, then click
   **Semak Mesej**. Point out that OCR confidence and scam risk are different.
3. Open **Pinjaman + caj proses** from the menu as a text fallback. Point out the exact/near-exact risk
   reference, high data similarity, dangerous phrases and move pathway.
4. Open **Laporan mangsa + caj berulang**.  Explain that rules can still flag a
   risky narrative even when similarity is too weak; the data layer abstains.
5. Open **Ayat keselamatan palsu + arahan**.  Show that a safe opening clause no
   longer hides the later payment command.
6. Expand **Lihat audit data yang digunakan**.  State the honest counts: 6,072
   source rows, 164 globally unique texts and 90 deduplicated templates.

`demo_assets/02_safety_light.png` is provided as a second OCR check. Both images
contain synthetic text only and are labelled as simulated data.

## Exact wording to use

- “Hybrid reference-data and explainable-linguistic prototype.”
- “Risk indicator index, not scam probability.”
- “Controlled synthetic reference data; real-world validation is the funded
  next phase.”
- “The current demo reads 90 unique templates at runtime and displays the
  nearest evidence.”
- “OCR runs locally in the application; its confidence describes average word
  recognition quality, not scam probability.”

## Do not claim

- “Validated AI model” or “90% accurate.”
- “3,000 independent messages.”
- “The score is the probability of fraud.”
- “Telegram messages are already validated training data.”
- “OCR is perfectly accurate.”
- “The app legally confirms a scammer.”

## Funding ask

The next funded phase should cover: real-world data partnerships, a formal
annotation protocol with two coders and adjudication, held-out evaluation,
Malay code-switching coverage, OCR benchmarking and multimodal analysis,
privacy/security review, and monitored deployment.

## Demo fallback

Before meeting a prospect, confirm the green **✓ OCR aktif** status. If it is
not green, use the built-in text examples and state that the OCR dependency did
not start; do not troubleshoot package installation during the pitch.
