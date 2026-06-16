# Spesifikasi ScamAlert Web Prototype v0.4.4

## Objektif

Versi v0.4.4 menaik taraf ScamAlert kepada antara muka visual infografik yang lebih selari dengan landing page Canva dan lebih sesuai untuk demonstrasi pertandingan inovasi.

## Struktur Halaman

1. Tentang ScamAlert
2. Analisis Mesej
3. Perbandingan Empirikal
4. Papan Pemuka
5. Buku Kod dan Rubrik Skor

## Identiti Visual

- Tema utama: hitam, putih dan merah.
- Hijau: hanya untuk Risiko Rendah.
- Kuning: hanya untuk Risiko Sederhana.
- Merah: Risiko Tinggi dan Sangat Tinggi.
- Sidebar disorokkan untuk mengelakkan isu teks tidak jelas.

## Dataset Naratif

- 3,000 data prototaip.
- 1,500 data penipuan siber.
- 1,500 data kawalan sepadan.
- 50 pengguna awal.

## Paparan Keputusan

Kad keputusan terdiri daripada:

1. Skor Risiko
2. Tahap Risiko
3. Jenis Dikesan
4. Padanan Data

## Julat Risiko

- 0–24: Rendah
- 25–49: Sederhana
- 50–74: Tinggi
- 75–100: Sangat Tinggi

## Komponen Risiko

1. Arahan wang / data sensitif
2. Janji tidak realistik
3. Penyamaran autoriti
4. Tekanan masa
5. Manipulasi emosi
6. Bukti sosial palsu

## Penafian

ScamAlert ialah prototaip amaran awal dan tidak menggantikan semakan rasmi. Pengguna digalakkan menyemak kesahihan mesej melalui saluran rasmi sebelum berkongsi maklumat peribadi, menekan pautan atau membuat sebarang transaksi kewangan.

## Pembetulan v0.4.5

Bahagian atas paparan diberi ruang tambahan kerana Streamlit mempunyai header tetap di bahagian atas. Tanpa ruang tambahan, tab navigasi boleh kelihatan terselindung di bawah toolbar Streamlit. Versi ini menambah `padding-top` pada `.block-container`, menambah spacer kecil sebelum tab, dan menjadikan header Streamlit berwarna cerah.

## Pembetulan v0.4.6

Versi ini membetulkan isu warna gelap/biru pada widget Streamlit seperti selectbox dan text area. Semua input dipaksa menggunakan latar putih, teks hitam dan border merah. Tema asas turut ditukar kepada `base = "light"` supaya aplikasi kekal dalam palet hitam, putih dan merah.

## Pembetulan v0.4.7

Versi ini membetulkan fungsi `render_bar_chart` supaya HTML tidak ditafsir sebagai blok kod Markdown. Semua carta custom kini dipaparkan sebagai infografik bar yang bersih. Latar utama aplikasi turut dipaksa kepada putih sepenuhnya.

## Perubahan v0.4.8

- Tab `Rumah` digantikan kepada `Tentang ScamAlert`.
