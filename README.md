# ScamAlert Web Prototype v0.4.4

ScamAlert ialah prototaip web amaran awal untuk membantu pengguna mengenal pasti mesej mencurigakan berdasarkan analisis lakuan pertuturan langsung, lakuan pertuturan tidak langsung, skor risiko dan cadangan tindakan selamat.

## Perubahan v0.4.4

- Antara muka berasaskan visual infografik.
- Sidebar disorokkan dan navigasi dipindahkan kepada tab di bahagian atas.
- Tema diselarikan dengan landing page Canva: hitam, putih dan merah.
- Hijau digunakan hanya untuk Risiko Rendah.
- Kuning digunakan hanya untuk Risiko Sederhana.
- Merah digunakan untuk Risiko Tinggi dan Sangat Tinggi.
- Teks antara muka dikemas kini kepada istilah “penipuan siber”.
- Kad statistik dikemas kini kepada 3,000 data prototaip, 1,500 data penipuan siber dan 1,500 data kawalan sepadan.
- Halaman Rumah, Analisis Mesej, Perbandingan Empirikal, Papan Pemuka serta Buku Kod dan Rubrik Skor ditambah baik dengan elemen infografik.

## Nota Dataset

Paparan dashboard menggunakan naratif konseptual v0.4: 1,500 data penipuan siber dan 1,500 data kawalan sepadan. Fail dataset semasa digunakan untuk memastikan fungsi prototaip berjalan. Dataset sebenar 3,000 baris boleh dijana semula kemudian untuk menyelaraskan kandungan dalaman dengan naratif metodologi.

## Cara Deploy

1. Upload semua fail ke GitHub repo Streamlit.
2. Pastikan `app.py`, `requirements.txt`, `scamalert_dataset.xlsx` dan folder `.streamlit` berada dalam repo.
3. Streamlit Community Cloud akan redeploy secara automatik.

## Perubahan v0.4.5

- Membetulkan isu bahagian atas paparan yang terselindung di bawah header tetap Streamlit.
- Menambah padding atas dan spacer supaya tab navigasi dan hero section tidak bertindih dengan toolbar Streamlit.
- Menukar latar header Streamlit kepada warna cerah supaya selari dengan tema hitam, putih dan merah.

## Perubahan v0.4.6

- Memaksa semua widget input Streamlit menggunakan latar putih, teks hitam dan border merah.
- Menghapuskan kesan warna biru/gelap pada selectbox dan text area.
- Menetapkan tema Streamlit kepada `base = "light"`.
- Butang `Semak Risiko` dipaksa menggunakan teks putih di atas latar merah.
- Warna antara muka diperkemas kepada hitam, putih dan merah sahaja kecuali hijau untuk Risiko Rendah dan kuning untuk Risiko Sederhana.

## Perubahan v0.4.7

- Membetulkan isu kod HTML `<div class=...>` yang terpapar dalam Papan Pemuka.
- Graf custom kini dirender sebagai infografik sebenar, bukan kod mentah.
- Memaksa latar utama aplikasi kepada putih sepenuhnya.
