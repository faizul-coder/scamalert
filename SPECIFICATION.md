# SPECIFICATION

Nama aplikasi: ScamAlert  
Versi: v0.8.0 Integrated  
Jenis: Prototaip aplikasi web amaran awal penipuan siber  
Platform: Streamlit

## Tujuan aplikasi

ScamAlert membantu pengguna menyemak mesej mencurigakan melalui tiga lapisan analisis wacana:

1. **ScamSpeech** — mengenal pasti fungsi bahasa dalam mesej, termasuk lakuan pertuturan langsung dan tidak langsung.
2. **ScamEmotion** — mengenal pasti pencetus emosi manipulatif berdasarkan kerangka 6E.
3. **ScamMove** — memetakan urutan gerakan strategi penipuan daripada bina kepercayaan kepada arahan tindakan.

## Pembetulan v0.8.0

- Nama aplikasi ditukar daripada ScamAlert Selangor kepada ScamAlert.
- Analisis keseluruhan dikira berdasarkan tiga komponen: ScamSpeech, ScamEmotion dan ScamMove.
- ScamMove ditambah sebagai modul ketiga dengan skor, tahap risiko, laluan gerakan dan ringkasan fungsi wacana.
- Data prototaip ScamMove dimasukkan untuk membezakan corak penipuan dan corak kawalan.
- Paparan keputusan distrukturkan semula supaya lebih sesuai untuk demonstrasi inovasi akademik.

## Struktur halaman

1. Header utama
2. Input mesej
3. Keputusan keseluruhan
4. Tiga enjin analisis
   - ScamSpeech
   - ScamEmotion
   - ScamMove
5. ScamMove Mapper
6. Frasa dan petanda dikesan
7. Padanan data kawalan sepadan
8. Cadangan tindakan selamat
9. Asas data ScamMove prototaip
10. Penafian

## Logik skor ringkas

- ScamSpeech: skor berdasarkan lakuan pertuturan langsung, tidak langsung dan petanda kawalan.
- ScamEmotion: skor berdasarkan pencetus emosi 6E.
- ScamMove: skor berdasarkan bilangan dan urutan move strategik yang dikesan.
- Skor keseluruhan: gabungan berwajaran ScamSpeech, ScamEmotion dan ScamMove.

## Tahap risiko

- 0–24: Rendah
- 25–49: Sederhana
- 50–74: Tinggi
- 75–100: Sangat Tinggi

## Nota penggunaan

Aplikasi ini ialah prototaip amaran awal. Keputusan sistem tidak menggantikan semakan rasmi oleh pihak berkuasa, institusi kewangan atau organisasi berkaitan.
