# ScamAlert reference-similarity engine

This is a deterministic, pure-Python component for a small controlled corpus.
It is a reference matcher, **not** a probability model and **not** a claim of
validated accuracy.

## API

```python
from scamalert_similarity import ReferenceSimilarityEngine

engine = ReferenceSimilarityEngine.from_csv("data/reference_unique.csv")
result = engine.query(user_message, top_k=3)

result.data_index                 # 0-100 contrast index, neutral at 50
result.reliability                # insufficient / ambiguous / moderate / strong
result.recommended_hybrid_weight  # evidence-dependent; app cap documented below
result.risk_matches               # nearest distinct risk templates
result.control_matches            # nearest distinct control templates
```

Required CSV columns are `record_id`, `text`, and `binary_label`. Optional
columns are `module`, `category`, `template_group`, and `source_count`.

## Method

1. NFKC/case normalization and replacement of URLs, contacts, amounts and
   numbers with stable tokens.
2. Separate TF-IDF spaces for word 1-2 grams and character 3-5 grams.
3. Weighted cosine similarity: 45% word and 55% character by default.
4. Only the closest record in each `template_group` may contribute, preventing
   repeated amount/name variants from receiving extra votes.
5. Up to three distinct templates form each class signal; the nearest template
   carries most weight.
6. If the best cosine is below `0.22`, or the risk/control signal margin is
   below `0.04`, the data index is fixed at neutral 50 and its recommended
   hybrid weight is zero.
7. Otherwise:

   ```text
   contrast = (risk_signal - control_signal) / max(risk_signal, control_signal)
   strength = clip((best_similarity - 0.22) / (0.58 - 0.22), 0, 1)
   data_index = 50 + 50 * contrast * strength
   ```

The reusable engine defaults to a maximum hybrid weight of 0.40.  ScamAlert
Demo 1.3 explicitly configures the cap to 0.55 so that an exact, unambiguous
reference can materially affect the hybrid index.  Weaker matches receive a
proportionally smaller weight; ambiguous and insufficient matches receive zero.

The thresholds are explicit configuration values and should eventually
be calibrated on independently adjudicated messages. They are safe engineering
defaults for a transparent prototype, not empirically validated cut-offs.

## Tests

```bash
cd agent_similarity
python -m unittest -v
```

The tests cover delexicalisation, deterministic ties, template collapsing,
risk/control direction, out-of-domain abstention, ambiguity, and CSV loading.
