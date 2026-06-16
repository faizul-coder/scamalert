# ScamAlert Web Prototype v0.4

ScamAlert ialah prototaip web amaran awal untuk membantu pengguna mengenal pasti mesej penipuan siber melalui analisis bahasa, skor risiko dan cadangan tindakan selamat.

## Perubahan v0.4

- Antara muka ditukar kepada tema cerah putih/hitam/merah supaya selari dengan landing page Canva.
- Warna tahap risiko dibaiki supaya teks lebih jelas dan kontras tinggi.
- Paparan keputusan ditukar kepada kad ringkasan: Skor Risiko, Tahap Risiko, Jenis Dikesan dan Padanan Data.
- Istilah awam dikemas kini kepada “penipuan siber” menggantikan “scam”, kecuali nama produk ScamAlert.
- Statistik naratif dikemas kini kepada 3,000 data prototaip: 1,500 data penipuan siber dan 1,500 data kawalan sepadan.
- Sidebar dijadikan lebih ringkas dan collapsed by default.

## Cara Deploy di Streamlit

1. Upload semua fail dalam folder ini ke GitHub repository.
2. Pastikan fail utama ialah `app.py`.
3. Pastikan fail dataset `scamalert_dataset.xlsx` berada dalam folder yang sama dengan `app.py`.
4. Deploy melalui Streamlit Community Cloud.

## Fail

- `app.py` — aplikasi Streamlit v0.4
- `scamalert_dataset.xlsx` — dataset prototaip
- `requirements.txt` — keperluan Python
- `.streamlit/config.toml` — konfigurasi tema Streamlit
- `SPECIFICATION.md` — ringkasan spesifikasi v0.4

## Nota

ScamAlert ialah prototaip amaran awal dan tidak menggantikan semakan rasmi. Pengguna digalakkan menyemak kesahihan mesej melalui saluran rasmi sebelum berkongsi maklumat peribadi, menekan pautan atau membuat bayaran.
