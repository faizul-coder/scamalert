# ScamAlert Web Prototype v0.5.0

ScamAlert ialah prototaip web amaran awal untuk membantu pengguna mengenal pasti mesej mencurigakan berdasarkan analisis lakuan pertuturan langsung, lakuan pertuturan tidak langsung, skor risiko dan cadangan tindakan selamat.

## Perubahan v0.5.0

- Fail Excel sebenar telah dinaik taraf kepada **3,000 data**.
- Dataset kini seimbang:
  - **1,500 data penipuan siber**
  - **1,500 data kawalan sepadan**
- Data kawalan sepadan kini ditambah kepada tiga kategori utama:
  - Promosi / Transaksi Sah — 500
  - Hebahan Rasmi / Keselamatan Sah — 500
  - Pendidikan Kewangan / Kerjaya / Pelaburan Sah — 500
- Paparan Papan Pemuka kini selaras dengan kandungan sebenar Excel.
- Tab `Tentang ScamAlert` dikekalkan.
- Tema visual kekal hitam, putih dan merah.
- Hijau hanya digunakan untuk Risiko Rendah.
- Kuning hanya digunakan untuk Risiko Sederhana.
- Merah digunakan untuk Risiko Tinggi dan Sangat Tinggi.

## Struktur Dataset

| Label Empirikal | Jumlah |
|---|---:|
| Penipuan Siber | 1,500 |
| Bukan Penipuan Siber | 1,500 |
| **Jumlah** | **3,000** |

## Pecahan Kategori

| Kategori | Jumlah |
|---|---:|
| Pinjaman / Bantuan Palsu | 500 |
| Penyamaran Autoriti | 500 |
| Pelaburan Tidak Wujud | 500 |
| Promosi / Transaksi Sah | 500 |
| Hebahan Rasmi / Keselamatan Sah | 500 |
| Pendidikan Kewangan / Kerjaya / Pelaburan Sah | 500 |

## Nota

Dataset ini ialah simulasi terkawal untuk pembangunan dan ujian awal prototaip. Dataset ini bukan data rasmi agensi penguatkuasaan.
