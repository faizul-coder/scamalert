# Data audit used by ScamAlert Demo 1.2 (data schema 1.1)

## Correct unit counts

| Unit | Total | Risk | Control |
|---|---:|---:|---:|
| Source rows audited | 6,072 | — | — |
| Unique records within each module/sheet | 167 | 116 | 51 |
| Globally unique texts | 164 | 116 | 48 |
| Normalized templates used for matching | 90 | 57 | 33 |

The difference between 167 and 164 is caused by three control messages that
appear in both ScamEmotion and ScamMove.  Global text counts therefore remove
those cross-module overlaps.

## Duplication

- ScamSpeech: 3,000 source rows but 83 exact unique texts and 30 normalized
  templates; 97.23% of rows repeat an existing exact text.
- ScamEmotion: 3,000 source rows but 54 exact unique texts and 39 normalized
  templates; 98.20% of rows repeat an existing exact text.
- ScamMove: 36 risk rows and 36 control rows, producing 18 and 12 exact unique
  texts respectively; after normalization, 12 risk and 12 control templates.
- `DATASET_KAWALAN_1500` in ScamSpeech duplicates the 1,500 control rows already
  present in `DATASET_UTAMA` and is not counted a second time.

## Label quality

Binary risk/control labels have no normalized cross-class conflicts.  However,
83 of 164 globally unique texts have more than one source risk-level label.
The application therefore uses only binary class identity for reference
matching.  Source levels and scores are not treated as ground truth.

## Methodological status

These records are controlled synthetic examples.  They are useful for runtime
wiring, demonstration and rule regression, but cannot estimate real-world
accuracy.  Independent adjudication and held-out evaluation are required before
claims about model performance.
