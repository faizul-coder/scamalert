# ScamAlert Demo 1.3 — QA report

Date: 2026-08-26

## Automated result

- Python compile check: passed.
- Unit/regression test methods: 38/38 passed.
- Open scam paraphrases: 36/36 reached the high-risk boundary.
- Control and ordinary messages: 22/22 remained below the high-risk boundary.
- Unknown neutral messages: 3/3 returned **Bukti Tidak Mencukupi**.
- Pasted-text UI smoke path: passed.
- Conditional result UI: passed for high-risk, assessed low-risk and
  insufficient-evidence paths.
- Screenshot → editable text → analysis path: passed.
- Replacement screenshot automatically replaced stale OCR text: passed.
- Streamlit runtime component test: no exceptions; one text area, one primary
  button and one uploader in the main flow, with no initial expander.
- Original ScamAlert product description: restored verbatim and verified.
- Light-theme and input contrast configuration: active.
- Uploader button exposes one Malay label only; the default label is hidden.
- Uploader label uses regular weight and the same muted tone as the message
  placeholder.
- Message placeholder and uploader label are both explicitly set to 0.875 rem,
  regular weight and 1.5 line height.
- Assessed results display risk score, explicit phrases, implicit phrases,
  emotional triggers, move analysis, scam type and **Cadangan Tindakan**.
- Insufficient-evidence results display only a concise notice and
  **Cadangan Tindakan**, without score, phrase, emotion, move or scam-type
  panels.
- Decision reason list, technical expanders and safety footer remain absent.

## Scenario coverage exercised

- Parcel/delivery fee and redelivery-link scams.
- Refund and tax-refund scams.
- Family/known-contact impersonation using a new number.
- Romance and emergency requests.
- E-wallet and account takeover.
- Bank/email phishing.
- Fake cash-aid notices combining a stated amount, urgent application language
  and a non-government link.
- Guaranteed investment and crypto return claims.
- Police, court, bank and tax-authority impersonation.
- Job/task/top-up scams.
- Remote-access software requests.
- Victim reports containing repeated or relayed dangerous requests.
- Completed victim experiences using past-tense actions such as clicking a
  link, entering card details, sharing an OTP and reporting lost money.

## False-escalation checks

- Official safety warnings remain low.
- Legitimate parcel/refund messages with no fee remain below high.
- Explicit investment-risk disclosures remain below high.
- Lunch transfer, contracted rent deposit and registered-company invoice remain
  below high.
- Family, romance and parcel vocabulary alone do not create a high warning.
- Cash-aid information on an official government portal is not given the
  fake-aid high-risk floor.
- The OCR success toast and selected-file pill are hidden from the compact
  public interface.

## OCR checks

- Light and dark screenshots are read.
- Coloured chat bubbles use a binary candidate when needed.
- Blank, invalid, tiny and excessive-resolution images fail visibly.
- OCR never converts a processing failure into a low-risk decision.
- OCR runs automatically once per new upload and populates editable text.

## Interpretation boundary

The open-message set was designed for regression testing and is not an
independent prevalence-weighted evaluation sample. No validated accuracy,
precision, recall or population-performance claim is made.
