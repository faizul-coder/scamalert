# ScamAlert Streamlit v0.8.2

ScamAlert ialah prototaip aplikasi web amaran awal penipuan siber berasaskan Kecerdasan Buatan (AI).

## Pembetulan v0.8.2

- Membetulkan isu skor rendah untuk input seperti **“bayar dulu sebelum keluarkan duit”**.
- Menambah rule khusus untuk pola **bayaran sebelum pengeluaran wang**.
- Menukar label teknikal pada tiga kad analisis kepada bahasa mesra pengguna:
  - **Makna Tersurat dan Makna Tersirat**
  - **Pencetus Emosi**
  - **Gerakan Strategi Penipuan**
- Menukar tajuk **ScamMove Mapper** kepada **Peta Gerakan Penipuan**.
- Mengelakkan paparan HTML mentah dalam tiga kad analisis dengan struktur HTML satu baris yang lebih stabil untuk Streamlit.

## Cara jalankan

```bash
pip install -r requirements.txt
streamlit run app.py
```
