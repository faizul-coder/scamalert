# ScamAlert Web Prototype v0.2

Prototaip aplikasi web untuk mengesan risiko mesej penipuan berdasarkan dataset Excel.

## Nama Sistem
ScamAlert

## Fail Penting
- app.py
- scamalert_dataset.xlsx
- requirements.txt
- README.md
- SPECIFICATION.md

## Cara Jalankan Secara Lokal

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Cara Deploy di Streamlit
Upload semua fail ke GitHub repository yang sama:
- app.py
- scamalert_dataset.xlsx
- requirements.txt
- README.md
- SPECIFICATION.md

Kemudian deploy melalui Streamlit Community Cloud dengan main file path:

```text
app.py
```

## Nota
App ini kini akan mencari fail dataset dengan beberapa nama:
- scamalert_dataset.xlsx
- scamalert.xlsx
- dataset.xlsx
- mana-mana fail .xlsx dalam folder yang sama

Jadi, jika nama Excel diubah kepada `scamalert.xlsx`, app masih boleh membaca fail tersebut.
