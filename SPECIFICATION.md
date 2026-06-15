# Spesifikasi Prototaip ScamShield v1

## Nama Sistem
ScamShield Web Prototype

## Tujuan
Membantu pengguna mengenal pasti risiko mesej scam berdasarkan analisis bahasa, lakuan pertuturan, ciri manipulasi dan perbandingan data scam dengan data kawalan.

## Pengguna Sasaran
- Pelajar
- Ibu bapa
- Warga emas
- Komuniti B40
- Peniaga kecil
- Pengguna media sosial

## Fungsi Minimum
1. Pengguna tampal mesej mencurigakan.
2. Sistem mengesan komponen risiko R1-R6.
3. Sistem mengira skor 0-100.
4. Sistem menentukan tahap risiko.
5. Sistem mencadangkan jenis scam.
6. Sistem highlight frasa berisiko.
7. Sistem memaparkan tindakan selamat.

## Kelebihan Empirikal
Sistem tidak bergantung kepada kata kunci tunggal. Dataset mengandungi 1,500 data scam dan 500 data kawalan bukan scam. Perbandingan empirikal digunakan untuk mengurangkan false positive terhadap bahasa promosi/harian.

## Teknologi
- Streamlit
- Python
- Pandas
- Scikit-learn
- Excel sebagai dataset awal

## Kedudukan Canva
Canva digunakan sebagai landing page dan bahan visual. Streamlit digunakan sebagai enjin semakan teks.
