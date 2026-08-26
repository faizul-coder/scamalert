# ScamAlert NICE 2026 — Demo 1.3

ScamAlert ialah sistem amaran awal penipuan siber berasaskan Kecerdasan Buatan
(AI) yang menganalisis corak bahasa, manipulasi emosi dan gerakan strategi
pujukan dalam mesej digital sebelum pengguna berkongsi maklumat peribadi,
menekan pautan atau membuat transaksi kewangan.

Version 1.3 is the prospect-facing release. It keeps the existing local OCR,
deduplicated reference data and explainable linguistic analysis, while making
two major corrections:

1. the public interface now presents only the screening result, category and
   proposed action; and
2. the detector covers multi-cue paraphrases for parcel, refund, e-wallet,
   family impersonation, romance, investment, authority, phishing, remote
   access and task/job scams.

Messages without enough evidence are labelled **Bukti Tidak Mencukupi** rather
than being presented as confidently low risk.

## Run locally

```bash
python -m pip install -r requirements.txt
streamlit run app.py
```

OCR requires Tesseract and Malay/English language data. Streamlit Community
Cloud installs these from `packages.txt`.

## Public workflow

1. Paste a message, or upload one PNG/JPG/JPEG screenshot up to 8 MB.
2. A new screenshot is read automatically and its text appears in the editable
   message field.
3. Review the text and click **Semak Mesej**.
4. Read the screening level, category when available and **Cadangan Tindakan**.

OCR word count, recognition confidence, internal scores and reference matches
are not displayed in the public interface.

## Runtime evidence

- 6,072 source rows audited.
- 164 globally unique source texts: 116 risk and 48 control.
- 90 normalized templates used at runtime: 57 risk and 33 control.
- Repeated synthetic variants receive one template vote.
- The source is controlled synthetic data, not independent real-world ground
  truth.

The application combines evidence-dependent reference similarity with
linguistic rules. A strong, unambiguous reference may contribute at most 55%
of the internal screening index. Multi-cue safety floors prevent a dangerous
combination from being neutralised by superficial similarity to a control
message.

## Verification

```bash
python -m unittest discover -s tests -v
python smoke_test.py
python smoke_test_ocr_state.py
python smoke_test_ocr_ui.py
```

The release suite contains 34 automated test methods, including 34 open scam
paraphrases, 20 control/ordinary messages, abstention checks and OCR tests. The
suite is a regression check, not a population accuracy estimate.

## Important limitation

ScamAlert remains an early-warning prototype. It does not legally identify a
sender as a scammer and does not replace verification through a bank,
service provider or authority. Formal accuracy, precision and recall require a
separate, independently sampled and human-adjudicated held-out test set.
