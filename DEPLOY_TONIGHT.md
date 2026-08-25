# Deploy ScamAlert 1.3 tonight

Version 1.2 is already the live backup. Upload version 1.3 only after retaining
that backup or its commit reference.

## Upload to GitHub

1. Open the root of `faizul-coder/scamalert` on branch `main`.
2. Click **Add file** → **Upload files**.
3. Drag every item inside this package into the upload page. Do not upload the
   ZIP itself and do not place the files inside an extra folder.
4. Confirm that these items will be replaced or added at repository root:

   - `app.py`
   - `scamalert_core.py`
   - `scamalert_similarity.py`
   - `scamalert_ocr.py`
   - `requirements.txt`
   - `packages.txt`
   - `.streamlit/config.toml`
   - `data/reference_data.json`
   - `tests/test_open_messages_v13.py`

5. Enter commit message: `Aktifkan ScamAlert 1.3 untuk demo NICE 2026`.
6. Click **Commit changes**.
7. Wait for Streamlit Community Cloud to rebuild, then use **Manage app** →
   **Reboot app** only if the new release does not appear automatically.

## Acceptance check before showing anyone

1. The page must open with **ScamAlert**, the original product description and
   **Semak Mesej Mencurigakan**.
2. The first task area should contain only the message box, **atau**, the image
   uploader and the compact **Semak Mesej** button.
3. Paste `Mak, telefon saya rosak. Ini nombor baharu. Tolong transfer RM1,850
   sekarang ke akaun kawan, jangan telefon nombor lama.` Expected: **Tinggi**.
4. Paste `Jangan kongsi OTP dengan sesiapa. Hubungi bank melalui nombor rasmi
   jika anda menerima permintaan mencurigakan.` Expected: **Rendah**.
5. Paste `Saya sedang membaca buku di perpustakaan.` Expected:
   **Bukti Tidak Mencukupi**, not Rendah.
6. Upload `demo_assets/01_risk_dark_chat.png`. OCR should run automatically;
   review the populated text and click **Semak Mesej**. Expected: high warning.
7. Confirm that the OCR success box, word count, raw index cards, move examples
   and long disclaimer are absent from the main flow.
8. Confirm that red buttons have white, legible text.

If OCR is unavailable, the app will show a warning. Continue the pitch by
pasting the prepared text cases; text analysis remains available.
