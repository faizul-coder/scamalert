# Activate OCR on the live ScamAlert app tonight

The OCR code is active in this package. It becomes active on the public app
only after version 1.2 is committed to the repository used by Streamlit
Community Cloud and the app has rebuilt.

## Deployment checklist

1. Back up the current repository or create a release tag for version 1.1.
2. Put the contents of this package at the repository root. In particular,
   verify that these files are not inside an extra ZIP folder:

   - `app.py`
   - `scamalert_core.py`
   - `scamalert_similarity.py`
   - `scamalert_ocr.py`
   - `requirements.txt`
   - `packages.txt`
   - `.streamlit/config.toml`
   - `data/reference_data.json`

3. Commit and push the changes.
4. In Streamlit Community Cloud, confirm the entry point is `app.py`, then
   reboot/redeploy the app if it has not started rebuilding automatically.
5. Wait for system packages and Python dependencies to finish installing.
6. Open the app in a private/incognito browser window. Do not present it until
   both green messages appear:

   - **✓ Data rujukan aktif**
   - **✓ OCR aktif**

## Five-minute acceptance test

1. Upload `demo_assets/01_risk_dark_chat.png` → extract → review → analyse.
   Expected category: **Sangat Tinggi** (exact score can vary slightly with the
   installed Tesseract version).
2. Upload `demo_assets/02_safety_light.png` → extract → review → analyse.
   Expected category: **Rendah**.
3. Use the built-in **Laporan mangsa + caj berulang** example. Expected category:
   **Sangat Tinggi**.
4. Paste `Please transfer RM50 now for lunch.` Expected category:
   **Sederhana**, not Tinggi.
5. Replace one uploaded image with the other without extracting it. Untouched
   OCR text from the first image should clear.

## If OCR is red

Do not continue an image demo. Use the built-in text examples; manual analysis
remains available. Check the Streamlit build log for installation of
`tesseract-ocr-msa` and verify that `packages.txt` is at the repository root.

Official reference:
https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/app-dependencies
