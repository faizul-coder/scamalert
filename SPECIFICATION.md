# Spesifikasi ScamAlert Selangor v0.2

## Tujuan

Membangunkan satu halaman aplikasi web yang membolehkan pengguna menyemak mesej mencurigakan dan menerima keputusan risiko awal berdasarkan:

1. Analisis lakuan pertuturan.
2. Analisis emosi.

## Prinsip Reka Bentuk

- Satu halaman sahaja.
- Tiada landing page dalam app.
- Tiada tab.
- Tiada contoh mesej dropdown.
- Tiada ScamMove dalam versi ini.
- Tema cerah: latar putih lembut, teks hitam, merah untuk amaran, kuning untuk sorotan frasa.
- Fokus kepada kefahaman pengguna awam.

## Aliran Pengguna

1. Pengguna memasukkan mesej.
2. Pengguna menekan butang **Semak Risiko**.
3. Sistem memaparkan keputusan analisis.
4. Sistem menyerlahkan frasa yang berkaitan.
5. Sistem mencadangkan tindakan selamat.

## Paparan Utama

1. Header Utama
2. Bahagian Input
3. Keputusan Analisis
4. Frasa Dikesan
5. Cadangan Tindakan Selamat
6. Penafian

## Dataset

- `scamspeech_dataset.xlsx`: 1,500 data penipuan siber + 1,500 data kawalan.
- `scamemotion_dataset.xlsx`: 1,500 data penipuan siber + 1,500 data kawalan.

Jumlah keseluruhan: 6,000 data prototaip.

## Penafian

ScamAlert Selangor ialah prototaip amaran awal dan tidak menggantikan semakan rasmi. Pengguna digalakkan menyemak kesahihan mesej melalui saluran rasmi sebelum berkongsi maklumat peribadi, menekan pautan atau membuat sebarang transaksi kewangan.
