# Spesifikasi ScamAlert Selangor v0.1

## Objektif

Membangunkan satu halaman aplikasi web yang membolehkan pengguna menyemak mesej mencurigakan dan menerima tiga lapisan analisis:

1. **ScamSpeech** – lakuan pertuturan, frasa berisiko dan skor risiko bahasa.
2. **ScamEmotion Trigger 6E** – pencetus emosi, intensiti emosi dan skor risiko emosi.
3. **ScamMove 6M** – gerakan wacana, strategi manipulasi dan skor risiko gerakan.

## Input

Pengguna boleh:

- memilih contoh mesej ujian; atau
- menampal mesej sendiri.

## Output

Aplikasi memaparkan:

- Skor Risiko Keseluruhan
- Tahap Risiko
- Padanan Data
- Frasa Berisiko
- Petanda Kawalan / Isyarat Sah
- Analisis ScamSpeech
- Analisis ScamEmotion Trigger 6E
- Analisis ScamMove 6M
- Cadangan Tindakan Selamat
- Contoh padanan data penipuan siber dan data kawalan sepadan

## Dataset Digabungkan

Aplikasi memuatkan tiga dataset:

1. `scamspeech_dataset.xlsx`
2. `scamemotion_dataset.xlsx`
3. `scammove_dataset.xlsx`

Setiap dataset mempunyai data penipuan siber dan data kawalan sepadan.

## Prinsip Reka Bentuk

- Satu halaman sahaja.
- Tiada landing page dalam app.
- Tiada tab yang banyak.
- Fokus kepada fungsi semakan mesej.
- Reka bentuk bersih, mudah digunakan dan sesuai untuk demo penilaian.

## Penafian

ScamAlert Selangor ialah prototaip amaran awal. Keputusan yang dipaparkan membantu pengguna membuat semakan awal dan tidak menggantikan pengesahan rasmi oleh pihak berkuasa.
