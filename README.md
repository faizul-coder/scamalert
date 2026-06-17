# ScamAlert Selangor Streamlit Prototype v0.1

**ScamAlert Selangor** ialah aplikasi web induk yang menggabungkan tiga modul analisis bahasa penipuan siber:

1. **ScamSpeech** – analisis lakuan pertuturan langsung dan tidak langsung.
2. **ScamEmotion Trigger 6E** – analisis pencetus emosi dan manipulasi emosi.
3. **ScamMove 6M** – analisis gerakan wacana dan strategi bahasa.

Versi ini direka sebagai **satu halaman Streamlit sahaja**. Landing page boleh digunakan untuk penerangan lengkap, manakala aplikasi ini hanya memfokuskan demonstrasi fungsi.

## Struktur Fail

```text
ScamAlert_Selangor_Streamlit_v0_1/
├── app.py
├── requirements.txt
├── README.md
├── SPECIFICATION.md
├── .streamlit/
│   └── config.toml
└── data/
    ├── scamspeech_dataset.xlsx
    ├── scamemotion_dataset.xlsx
    └── scammove_dataset.xlsx
```

## Cara Deploy di Streamlit Community Cloud

1. Cipta satu repository baharu di GitHub.
2. Upload semua fail dalam folder ini ke repository tersebut.
3. Pastikan `app.py`, `requirements.txt`, folder `.streamlit` dan folder `data` berada dalam root repository.
4. Buka Streamlit Community Cloud.
5. Pilih repository GitHub, branch dan fail utama `app.py`.
6. Klik **Deploy**.

## Nota Penting

- Data dalam fail Excel ialah **simulasi terkawal prototaip**.
- Aplikasi ini ialah alat amaran awal dan tidak menggantikan semakan rasmi oleh pihak berkuasa.
- Tujuan utama versi ini ialah demonstrasi inovasi untuk pembentangan, pameran dan penilaian awal.
