# ScamAlert v0.8.3

ScamAlert ialah prototaip aplikasi web amaran awal penipuan siber berasaskan Kecerdasan Buatan (AI).

## Pembetulan v0.8.3

- Menggunakan bahasa Melayu sepenuhnya dalam paparan pengguna.
- Istilah teknikal berbahasa Inggeris digantikan dengan istilah mesra pengguna:
  - penipuan siber / penipuan digital / penipuan
  - penipu
  - gerakan strategi penipuan
- Menambah pilihan **Muat Naik Tangkapan Layar Perbualan**.
- Tangkapan layar boleh dimuat naik sebagai rujukan visual.
- Analisis risiko prototaip ini masih dijalankan berdasarkan teks mesej yang ditampal dalam kotak input.
- Memastikan input seperti **“bayar dulu sebelum keluarkan duit”** diklasifikasikan sebagai risiko tinggi / sangat tinggi.
- Tiga kad analisis menggunakan label mesra pengguna:
  - **Makna Tersurat dan Makna Tersirat**
  - **Pencetus Emosi**
  - **Gerakan Strategi Penipuan**

## Cara jalankan

```bash
pip install -r requirements.txt
streamlit run app.py
```
