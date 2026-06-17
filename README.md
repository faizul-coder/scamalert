# ScamAlert Selangor Streamlit Prototype v0.2

**ScamAlert Selangor** ialah prototaip aplikasi web amaran awal yang membantu pengguna menyemak mesej mencurigakan sebelum berkongsi maklumat peribadi, menekan pautan atau membuat bayaran.

Versi v0.2 ialah aplikasi **satu halaman sahaja**. Landing page boleh digunakan untuk penerangan lengkap, manakala aplikasi ini memfokuskan fungsi semakan mesej.

## Enjin Analisis

Versi ini menggunakan dua enjin dalaman:

1. **ScamSpeech** – analisis lakuan pertuturan langsung dan tidak langsung.
2. **ScamEmotion Trigger 6E** – analisis pencetus emosi.

**ScamMove tidak dimasukkan dalam versi aplikasi web ini** untuk mengekalkan paparan yang bersih dan mudah difahami pengguna awam.

## Dataset

Aplikasi memuatkan dua dataset:

1. `data/scamspeech_dataset.xlsx` – 3,000 data prototaip
2. `data/scamemotion_dataset.xlsx` – 3,000 data prototaip

Jumlah keseluruhan: **6,000 data prototaip**

- 3,000 data penipuan siber
- 3,000 data kawalan sepadan

## Struktur Fail

```text
ScamAlert_Selangor_Streamlit_v0_2/
├── app.py
├── requirements.txt
├── README.md
├── SPECIFICATION.md
├── .streamlit/
│   └── config.toml
└── data/
    ├── scamspeech_dataset.xlsx
    └── scamemotion_dataset.xlsx
```

## Cara Deploy

1. Cipta repository baharu di GitHub.
2. Upload semua fail dalam folder ini ke repository tersebut.
3. Pastikan `app.py`, `requirements.txt`, folder `.streamlit` dan folder `data` berada dalam root repository.
4. Deploy di Streamlit Community Cloud.
5. Pilih fail utama: `app.py`.

## Nota

Data yang digunakan ialah simulasi terkawal bagi tujuan pembangunan prototaip inovasi. Keputusan aplikasi ialah amaran awal dan tidak menggantikan semakan rasmi.
