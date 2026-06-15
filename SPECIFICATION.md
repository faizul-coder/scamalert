# Spesifikasi Prototaip ScamAlert v0.2

## Nama Sistem
ScamAlert

## Nama Umum
Sistem Amaran Awal Penipuan Digital Berasaskan Analisis Bahasa

## Tujuan
Membantu pengguna mengenal pasti risiko mesej penipuan melalui analisis bahasa, lakuan pertuturan, ciri manipulasi dan perbandingan data scam dengan data kawalan.

## Fungsi Utama
1. Pengguna memasukkan teks mencurigakan.
2. Sistem mengesan komponen risiko R1-R6.
3. Sistem mengira skor risiko 0-100.
4. Sistem memaparkan tahap risiko.
5. Sistem mencadangkan jenis scam yang paling hampir.
6. Sistem highlight frasa berisiko.
7. Sistem memaparkan tindakan selamat.

## Kelebihan Empirikal
Sistem menggunakan dataset scam dan dataset kawalan bukan scam. Ini membolehkan sistem membezakan bahasa scam daripada bahasa promosi/harian yang hampir sama bentuknya.

## Fail Dataset
Nama fail dataset diselaraskan kepada:

```text
scamalert_dataset.xlsx
```

## Teknologi
- Streamlit
- Python
- Pandas
- Scikit-learn
- Excel sebagai dataset

## Nota Penamaan
Nama ScamAlert lebih umum dan tidak menggunakan nama ScamShield bagi mengelakkan kekeliruan dengan aplikasi atau inisiatif sedia ada.
