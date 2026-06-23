# SPECIFICATION

Nama aplikasi: ScamAlert  
Versi: v0.8.2  
Jenis: Prototaip aplikasi web amaran awal penipuan siber

## Struktur analisis pengguna

1. **Makna Tersurat dan Makna Tersirat**  
   Mengesan arahan jelas, permintaan bayaran, permintaan data serta pujukan tersirat.

2. **Pencetus Emosi**  
   Mengesan emosi seperti ketakutan, kecemasan, harapan keuntungan dan kepercayaan palsu.

3. **Gerakan Strategi Penipuan**  
   Memetakan langkah mesej scam daripada pancingan awal kepada arahan bayaran, data atau penguncian mangsa.

## Rule baharu v0.8.2

Frasa seperti:

- bayar dulu sebelum keluarkan duit
- bayar dahulu sebelum keluarkan duit
- bayar dulu untuk keluarkan duit
- caj pengeluaran
- bayaran pengeluaran
- aktifkan pengeluaran

akan diklasifikasikan sebagai pola **bayaran sebelum pengeluaran wang** dan dinaikkan kepada kategori risiko tinggi / sangat tinggi.

## Struktur halaman

1. Header utama
2. Input mesej
3. Keputusan keseluruhan
4. Tiga Enjin Analisis
5. Peta Gerakan Penipuan
6. Frasa dan Petanda Dikesan
7. Padanan Data Kawalan Sepadan
8. Cadangan Tindakan Selamat
9. Penafian
