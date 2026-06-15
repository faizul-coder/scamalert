# ScamShield Web Prototype v0.1

Prototaip aplikasi web untuk mengesan risiko mesej scam berdasarkan dataset Excel ScamShield.

## Cara Jalankan Secara Lokal

1. Pasang Python 3.10 atau ke atas.
2. Buka folder ini dalam terminal.
3. Jalankan arahan:

```bash
pip install -r requirements.txt
streamlit run app.py
```

4. Browser akan membuka aplikasi ScamShield.

## Fungsi Utama

- Semak teks mencurigakan
- Skor risiko 0-100
- Tahap risiko: rendah, sederhana, tinggi, sangat tinggi
- Jenis scam yang hampir
- Highlight frasa berisiko
- Perbandingan empirikal scam vs bukan scam
- Dashboard dataset
- Kodbook dan rubrik risiko

## Nota

Keputusan sistem ialah amaran awal, bukan pengesahan rasmi. Untuk versi pertandingan, web ini boleh dihubungkan dengan landing page Canva.
