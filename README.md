# ScamAlert Selangor Streamlit v0.7.3 Plain Clean

Pembetulan v0.7.3:
- Skor risiko dipaparkan dalam bentuk meter.
- Border kad diringkaskan supaya tidak terlalu tebal.
- Kad utama menggunakan garis lurus ringkas, bukan border berat.
- Kotak input menggunakan border halus.

## Cara jalankan

```bash
pip install -r requirements.txt
streamlit run app.py
```


## Patch v0.7.9
- Header ber-outline dengan ayat baharu.
- Cadangan Tindakan Selamat dan Penafian ber-outline.
- Logik advance-fee scam ditambah.
- Meter skor dan susun atur utama dikekalkan.


## v0.8.2 Scoring Engine
- Enjin skor risiko diperkukuh supaya tidak terlalu bergantung pada kata kunci sempit.
- Pola advance-fee scam, pinjaman palsu, pelaburan palsu, kerja palsu, hadiah palsu, OTP dan penyamaran autoriti diberi tahap risiko minimum.
- Ayat seperti “Sila bayar RM100 caj pemprosesan sebelum pengeluaran wang dilakukan” tidak lagi jatuh sebagai risiko rendah.
- UI/meter/layout dikekalkan daripada versi sebelumnya.


## v0.8.3 No Overlap
- Bahagian Keputusan Analisis ditukar kepada CSS grid supaya kotak skor risiko tidak bertindih dengan kotak Analisis Lakuan Pertuturan.
- Logik skor v0.8.2 dikekalkan.
