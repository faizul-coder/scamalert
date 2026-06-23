# ScamAlert Streamlit v0.8.1 Integrated

Versi ini menggabungkan tiga enjin analisis dalam satu halaman:
- **Makna tersurat dan makna tersirat** (berasaskan ScamSpeech)
- **Pencetus emosi** (berasaskan ScamEmotion)
- **Gerakan strategi penipuan** (berasaskan ScamMove)

## Penambahbaikan v0.8.1
- Nama aplikasi diseragamkan kepada **ScamAlert**.
- Label teknikal seperti `ScamSpeech`, `ScamEmotion` dan `ScamMove` ditukar kepada bahasa yang lebih mesra pengguna.
- Ditambah logik pengesanan untuk pola **bayaran sebelum pengeluaran wang**, contohnya: `bayar dulu sebelum keluarkan duit`.
- Ditambah paparan **Peta Gerakan Penipuan** bagi menunjukkan urutan strategi scam.
- Paparan kad analisis diringkaskan dan dibersihkan untuk mengelakkan paparan HTML mentah.

## Cara jalankan

```bash
pip install -r requirements.txt
streamlit run app.py
```
