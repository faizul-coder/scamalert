"""Dependency-free, explainable text similarity for ScamAlert.

The module deliberately exposes a *reference-data index*, not a probability and
not a trained classifier.  It compares a query with curated risk and control
messages using two independently normalised TF-IDF spaces:

* word unigrams and bigrams (45% by default); and
* character 3-5 grams (55% by default).

Repeated variants of the same template are collapsed when the class-level
signal is calculated, so changing an amount or phone number cannot give a
template extra voting power merely because it appears many times in a source
workbook.
"""

from __future__ import annotations

import csv
import math
import re
import unicodedata
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Mapping, Sequence, Tuple


RISK_LABEL = "risk"
CONTROL_LABEL = "control"

_RISK_ALIASES = {
    "1",
    "true",
    "yes",
    "positive",
    "positif",
    "risk",
    "risky",
    "scam",
    "penipuan",
    "penipu",
}
_CONTROL_ALIASES = {
    "0",
    "false",
    "no",
    "negative",
    "negatif",
    "control",
    "kawalan",
    "safe",
    "selamat",
    "normal",
}

_URL_RE = re.compile(r"\b(?:https?://|hxxps?://|www\.)\S+", re.IGNORECASE)
_EMAIL_RE = re.compile(r"\b[\w.+-]+@[\w.-]+\.[a-z]{2,}\b", re.IGNORECASE)
_PHONE_RE = re.compile(r"(?<!\w)(?:\+?6?0?1\d[\s().-]*){8,12}(?!\w)")
_MONEY_RE = re.compile(
    r"(?<!\w)(?:rm|myr|usd|sgd|\$)\s*\d[\d.,]*(?:\s*(?:k|ribu|juta))?\b",
    re.IGNORECASE,
)
_PERCENT_RE = re.compile(r"(?<!\w)\d+(?:[.,]\d+)?\s*%")
_NUMBER_RE = re.compile(r"(?<!\w)\d+(?:[.,:/-]\d+)*(?!\w)")
_NON_WORD_RE = re.compile(r"[^\w\s]", re.UNICODE)
_UNDERSCORE_RE = re.compile(r"_+")
_SPACE_RE = re.compile(r"\s+")


def canonical_label(value: object) -> str:
    """Map common binary labels onto ``risk`` or ``control``.

    An unknown value is rejected rather than silently guessed.
    """

    label = str(value).strip().casefold()
    if label in _RISK_ALIASES:
        return RISK_LABEL
    if label in _CONTROL_ALIASES:
        return CONTROL_LABEL
    raise ValueError(f"Unsupported binary label: {value!r}")


def normalize_text(text: object) -> str:
    """Normalise Malay/English message text and delexicalise volatile values.

    URLs, e-mail addresses, phone-like numbers, money, percentages, and other
    numbers are replaced by stable lexical tokens.  This means, for example,
    that otherwise identical messages containing ``RM100`` and ``RM500`` share
    a template representation.
    """

    value = unicodedata.normalize("NFKC", "" if text is None else str(text))
    value = value.casefold()
    value = _URL_RE.sub(" urltoken ", value)
    value = _EMAIL_RE.sub(" emailtoken ", value)
    value = _PHONE_RE.sub(" phonetoken ", value)
    value = _MONEY_RE.sub(" moneytoken ", value)
    value = _PERCENT_RE.sub(" percenttoken ", value)
    value = _NUMBER_RE.sub(" numbertoken ", value)
    value = _UNDERSCORE_RE.sub(" ", value)
    value = _NON_WORD_RE.sub(" ", value)
    return _SPACE_RE.sub(" ", value).strip()


@dataclass(frozen=True)
class ReferenceRecord:
    """One unique controlled reference message."""

    record_id: str
    text: str
    label: str
    module: str = ""
    category: str = ""
    template_group: str = ""
    source_count: int = 1

    def __post_init__(self) -> None:
        object.__setattr__(self, "record_id", str(self.record_id).strip())
        object.__setattr__(self, "text", str(self.text).strip())
        object.__setattr__(self, "label", canonical_label(self.label))
        object.__setattr__(self, "source_count", max(1, int(self.source_count)))
        if not self.record_id:
            raise ValueError("record_id must not be empty")
        if not self.text:
            raise ValueError(f"text must not be empty for {self.record_id}")


@dataclass(frozen=True)
class SimilarityMatch:
    record_id: str
    label: str
    similarity: float
    text: str
    module: str
    category: str
    template_group: str
    source_count: int

    def as_dict(self) -> Dict[str, object]:
        return {
            "record_id": self.record_id,
            "label": self.label,
            "similarity": round(self.similarity, 6),
            "text": self.text,
            "module": self.module,
            "category": self.category,
            "template_group": self.template_group,
            "source_count": self.source_count,
        }


@dataclass(frozen=True)
class SimilarityResult:
    """Transparent evidence returned for one query.

    ``data_index`` is centred at 50.  Values above 50 mean the usable reference
    evidence leans toward risk; values below 50 mean it leans toward control.
    It is not a probability, confidence percentage, or model accuracy.
    """

    query: str
    normalized_query: str
    data_index: float
    risk_signal: float
    control_signal: float
    best_similarity: float
    signal_margin: float
    reliability: str
    usable_for_hybrid: bool
    recommended_hybrid_weight: float
    risk_matches: Tuple[SimilarityMatch, ...]
    control_matches: Tuple[SimilarityMatch, ...]

    def as_dict(self) -> Dict[str, object]:
        return {
            "query": self.query,
            "normalized_query": self.normalized_query,
            "data_index": round(self.data_index, 2),
            "risk_signal": round(self.risk_signal, 6),
            "control_signal": round(self.control_signal, 6),
            "best_similarity": round(self.best_similarity, 6),
            "signal_margin": round(self.signal_margin, 6),
            "reliability": self.reliability,
            "usable_for_hybrid": self.usable_for_hybrid,
            "recommended_hybrid_weight": round(self.recommended_hybrid_weight, 4),
            "risk_matches": [item.as_dict() for item in self.risk_matches],
            "control_matches": [item.as_dict() for item in self.control_matches],
        }


SparseVector = Dict[str, float]


def _tokens(normalized: str) -> List[str]:
    return re.findall(r"[^\W_]+", normalized, flags=re.UNICODE)


def _word_features(normalized: str) -> Counter[str]:
    tokens = _tokens(normalized)
    features: Counter[str] = Counter(f"w1:{token}" for token in tokens)
    features.update(
        f"w2:{tokens[index]}_{tokens[index + 1]}"
        for index in range(len(tokens) - 1)
    )
    return features


def _char_features(normalized: str, sizes: Sequence[int]) -> Counter[str]:
    padded = f" {normalized} "
    features: Counter[str] = Counter()
    for size in sizes:
        if len(padded) < size:
            continue
        features.update(
            f"c{size}:{padded[index:index + size]}"
            for index in range(len(padded) - size + 1)
        )
    return features


def _idf(counters: Sequence[Counter[str]]) -> Dict[str, float]:
    document_count = len(counters)
    frequency: Counter[str] = Counter()
    for counter in counters:
        frequency.update(counter.keys())
    return {
        feature: math.log((1.0 + document_count) / (1.0 + count)) + 1.0
        for feature, count in frequency.items()
    }


def _normalised_tfidf(counter: Counter[str], idf: Mapping[str, float]) -> SparseVector:
    vector = {
        feature: (1.0 + math.log(count)) * idf[feature]
        for feature, count in counter.items()
        if feature in idf and count > 0
    }
    magnitude = math.sqrt(sum(value * value for value in vector.values()))
    if not magnitude:
        return {}
    return {feature: value / magnitude for feature, value in vector.items()}


def _dot(left: Mapping[str, float], right: Mapping[str, float]) -> float:
    if len(left) > len(right):
        left, right = right, left
    return sum(value * right.get(feature, 0.0) for feature, value in left.items())


class ReferenceSimilarityEngine:
    """Fit and query a deterministic, explainable two-class reference index."""

    def __init__(
        self,
        records: Iterable[ReferenceRecord],
        *,
        word_weight: float = 0.45,
        char_weight: float = 0.55,
        char_sizes: Sequence[int] = (3, 4, 5),
        min_reliable_similarity: float = 0.22,
        strong_similarity: float = 0.58,
        ambiguity_margin: float = 0.04,
        max_hybrid_weight: float = 0.40,
    ) -> None:
        self.records = tuple(records)
        if not self.records:
            raise ValueError("At least one reference record is required")
        if len({record.record_id for record in self.records}) != len(self.records):
            raise ValueError("record_id values must be unique")
        labels = {record.label for record in self.records}
        if labels != {RISK_LABEL, CONTROL_LABEL}:
            raise ValueError("Reference data must contain both risk and control labels")
        if word_weight < 0 or char_weight < 0 or word_weight + char_weight <= 0:
            raise ValueError("Feature weights must be non-negative with a positive sum")
        total_weight = word_weight + char_weight
        self.word_weight = word_weight / total_weight
        self.char_weight = char_weight / total_weight
        self.char_sizes = tuple(sorted({int(size) for size in char_sizes if int(size) > 0}))
        if not self.char_sizes:
            raise ValueError("At least one positive character n-gram size is required")
        if not 0 <= min_reliable_similarity < strong_similarity <= 1:
            raise ValueError("Similarity thresholds must satisfy 0 <= min < strong <= 1")
        if not 0 <= ambiguity_margin <= 1:
            raise ValueError("ambiguity_margin must be in [0, 1]")
        if not 0 <= max_hybrid_weight <= 1:
            raise ValueError("max_hybrid_weight must be in [0, 1]")
        self.min_reliable_similarity = min_reliable_similarity
        self.strong_similarity = strong_similarity
        self.ambiguity_margin = ambiguity_margin
        self.max_hybrid_weight = max_hybrid_weight

        self._normalized = tuple(normalize_text(record.text) for record in self.records)
        word_counters = tuple(_word_features(text) for text in self._normalized)
        char_counters = tuple(_char_features(text, self.char_sizes) for text in self._normalized)
        self._word_idf = _idf(word_counters)
        self._char_idf = _idf(char_counters)
        self._word_vectors = tuple(
            _normalised_tfidf(counter, self._word_idf) for counter in word_counters
        )
        self._char_vectors = tuple(
            _normalised_tfidf(counter, self._char_idf) for counter in char_counters
        )
        self._template_groups = tuple(
            record.template_group.strip() or normalized
            for record, normalized in zip(self.records, self._normalized)
        )

    @classmethod
    def from_csv(
        cls,
        path: str | Path,
        *,
        id_column: str = "record_id",
        text_column: str = "text",
        label_column: str = "binary_label",
        module_column: str = "module",
        category_column: str = "category",
        template_column: str = "template_group",
        count_column: str = "source_count",
        **engine_options: object,
    ) -> "ReferenceSimilarityEngine":
        records = load_reference_csv(
            path,
            id_column=id_column,
            text_column=text_column,
            label_column=label_column,
            module_column=module_column,
            category_column=category_column,
            template_column=template_column,
            count_column=count_column,
        )
        return cls(records, **engine_options)

    def _similarities(self, normalized_query: str) -> List[float]:
        word_vector = _normalised_tfidf(
            _word_features(normalized_query), self._word_idf
        )
        char_vector = _normalised_tfidf(
            _char_features(normalized_query, self.char_sizes), self._char_idf
        )
        return [
            max(
                0.0,
                min(
                    1.0,
                    self.word_weight * _dot(word_vector, reference_word)
                    + self.char_weight * _dot(char_vector, reference_char),
                ),
            )
            for reference_word, reference_char in zip(
                self._word_vectors, self._char_vectors
            )
        ]

    def _class_matches(
        self,
        label: str,
        similarities: Sequence[float],
        top_k: int,
    ) -> Tuple[SimilarityMatch, ...]:
        # Keep only the best record per template group, preventing repeated
        # amount/name variants from acquiring multiple votes.
        best_by_template: Dict[str, Tuple[float, str, int]] = {}
        for index, (record, similarity, group) in enumerate(
            zip(self.records, similarities, self._template_groups)
        ):
            if record.label != label:
                continue
            candidate = (similarity, record.record_id, index)
            previous = best_by_template.get(group)
            if previous is None or (-candidate[0], candidate[1]) < (
                -previous[0],
                previous[1],
            ):
                best_by_template[group] = candidate

        ranked = sorted(
            best_by_template.values(), key=lambda item: (-item[0], item[1])
        )[:top_k]
        output: List[SimilarityMatch] = []
        for similarity, _, index in ranked:
            record = self.records[index]
            output.append(
                SimilarityMatch(
                    record_id=record.record_id,
                    label=record.label,
                    similarity=similarity,
                    text=record.text,
                    module=record.module,
                    category=record.category,
                    template_group=self._template_groups[index],
                    source_count=record.source_count,
                )
            )
        return tuple(output)

    @staticmethod
    def _class_signal(matches: Sequence[SimilarityMatch]) -> float:
        if not matches:
            return 0.0
        rank_weights = (1.0, 0.65, 0.40)
        selected = matches[: len(rank_weights)]
        weights = rank_weights[: len(selected)]
        weighted_mean = sum(
            match.similarity * weight for match, weight in zip(selected, weights)
        ) / sum(weights)
        # The closest example is primary, with limited corroboration from the
        # next two distinct templates.
        return 0.75 * selected[0].similarity + 0.25 * weighted_mean

    def query(self, text: object, *, top_k: int = 3) -> SimilarityResult:
        """Compare one message with risk/control references.

        ``top_k`` affects the evidence shown and the class signal, but at most
        three distinct templates contribute to a class signal.
        """

        query = "" if text is None else str(text)
        normalized = normalize_text(query)
        if not normalized:
            raise ValueError("Query contains no analysable text")
        if top_k < 1:
            raise ValueError("top_k must be at least 1")
        similarities = self._similarities(normalized)
        risk_matches = self._class_matches(RISK_LABEL, similarities, top_k)
        control_matches = self._class_matches(CONTROL_LABEL, similarities, top_k)
        risk_signal = self._class_signal(risk_matches)
        control_signal = self._class_signal(control_matches)
        best_similarity = max(
            risk_matches[0].similarity if risk_matches else 0.0,
            control_matches[0].similarity if control_matches else 0.0,
        )
        signal_margin = abs(risk_signal - control_signal)

        meets_similarity_threshold = best_similarity >= self.min_reliable_similarity
        if not meets_similarity_threshold:
            reliability = "insufficient"
        elif signal_margin < self.ambiguity_margin:
            reliability = "ambiguous"
        elif best_similarity >= self.strong_similarity:
            reliability = "strong"
        else:
            reliability = "moderate"
        usable = reliability in {"moderate", "strong"}

        similarity_strength = max(
            0.0,
            min(
                1.0,
                (best_similarity - self.min_reliable_similarity)
                / (self.strong_similarity - self.min_reliable_similarity),
            ),
        )
        if not usable:
            data_index = 50.0
            recommended_weight = 0.0
        else:
            dominant_signal = max(risk_signal, control_signal, 1e-12)
            contrast = (risk_signal - control_signal) / dominant_signal
            data_index = max(
                0.0, min(100.0, 50.0 + 50.0 * contrast * similarity_strength)
            )
            margin_strength = min(
                1.0, signal_margin / max(self.ambiguity_margin * 3.0, 1e-12)
            )
            recommended_weight = (
                self.max_hybrid_weight * similarity_strength * margin_strength
            )

        return SimilarityResult(
            query=query,
            normalized_query=normalized,
            data_index=data_index,
            risk_signal=risk_signal,
            control_signal=control_signal,
            best_similarity=best_similarity,
            signal_margin=signal_margin,
            reliability=reliability,
            usable_for_hybrid=usable,
            recommended_hybrid_weight=recommended_weight,
            risk_matches=risk_matches,
            control_matches=control_matches,
        )


def load_reference_csv(
    path: str | Path,
    *,
    id_column: str = "record_id",
    text_column: str = "text",
    label_column: str = "binary_label",
    module_column: str = "module",
    category_column: str = "category",
    template_column: str = "template_group",
    count_column: str = "source_count",
) -> List[ReferenceRecord]:
    """Load references from a UTF-8 CSV with strict required-column checks."""

    records: List[ReferenceRecord] = []
    with Path(path).open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        fields = set(reader.fieldnames or ())
        required = {id_column, text_column, label_column}
        missing = required - fields
        if missing:
            raise ValueError(f"Missing required CSV columns: {sorted(missing)}")
        for line_number, row in enumerate(reader, start=2):
            raw_count = row.get(count_column, "")
            try:
                source_count = int(raw_count) if str(raw_count).strip() else 1
            except ValueError as exc:
                raise ValueError(
                    f"Invalid {count_column!r} at CSV line {line_number}"
                ) from exc
            try:
                records.append(
                    ReferenceRecord(
                        record_id=row.get(id_column, ""),
                        text=row.get(text_column, ""),
                        label=row.get(label_column, ""),
                        module=row.get(module_column, "") if module_column in fields else "",
                        category=(
                            row.get(category_column, "") if category_column in fields else ""
                        ),
                        template_group=(
                            row.get(template_column, "") if template_column in fields else ""
                        ),
                        source_count=source_count,
                    )
                )
            except ValueError as exc:
                raise ValueError(f"Invalid reference at CSV line {line_number}: {exc}") from exc
    return records
