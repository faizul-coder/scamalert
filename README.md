# ScamAlert Streamlit v0.8.0 Integrated

ScamAlert ialah prototaip aplikasi web amaran awal penipuan siber berasaskan Kecerdasan Buatan (AI). Versi ini menggabungkan tiga enjin analisis dalam satu paparan:

1. **ScamSpeech** — mengesan lakuan pertuturan langsung dan tidak langsung.
2. **ScamEmotion** — mengesan pencetus emosi 6E seperti ketakutan, kecemasan, harapan keuntungan dan kepercayaan palsu.
3. **ScamMove** — memetakan gerakan strategi scam seperti bina kepercayaan, tawar peluang, janji ganjaran, tekanan masa, arahan bayaran/data dan penguncian mangsa.

## Pembetulan v0.8.0

- Semua rujukan nama lama telah diseragamkan kepada **ScamAlert**.
- Keputusan keseluruhan kini menggabungkan ScamSpeech, ScamEmotion dan ScamMove.
- Menambah paparan **ScamMove Mapper** dalam bentuk laluan gerakan beranak panah.
- Menambah data prototaip ScamMove untuk padanan data penipuan dan data kawalan.
- Menambah kategori ancaman dan padanan data kawalan sepadan.
- Mengekalkan gaya visual putih, kemas, minimal dan profesional.

## Cara jalankan

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Fail utama

- `app.py` — aplikasi Streamlit utama.
- `requirements.txt` — keperluan Python minimum.
- `SPECIFICATION.md` — spesifikasi struktur dan fungsi aplikasi.
- `scamspeech_dataset.xlsx` — dataset sokongan ScamSpeech.
- `scamemotion_dataset.xlsx` — dataset sokongan ScamEmotion.
- `scammove_dataset.xlsx` — dataset sokongan ScamMove.
