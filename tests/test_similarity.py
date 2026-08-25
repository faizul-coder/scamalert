import csv
import tempfile
import unittest
from pathlib import Path

from scamalert_similarity import (
    CONTROL_LABEL,
    RISK_LABEL,
    ReferenceRecord,
    ReferenceSimilarityEngine,
    normalize_text,
)


def sample_records():
    return [
        ReferenceRecord(
            "R1",
            "Bayar RM100 hari ini untuk tebus hadiah anda",
            "risk",
            module="speech",
            category="bayaran_awal",
        ),
        ReferenceRecord(
            "R2",
            "Bayar RM500 hari ini untuk tebus hadiah anda",
            "scam",
            module="speech",
            category="bayaran_awal",
        ),
        ReferenceRecord(
            "R3",
            "Kongsi OTP sekarang supaya akaun tidak disekat",
            "positive",
            module="move",
            category="kelayakan",
        ),
        ReferenceRecord(
            "C1",
            "Jangan bayar apa-apa caj untuk menerima hadiah",
            "control",
            module="speech",
            category="amaran",
        ),
        ReferenceRecord(
            "C2",
            "Jangan sesekali kongsi OTP atau kata laluan",
            "safe",
            module="move",
            category="amaran",
        ),
        ReferenceRecord(
            "C3",
            "Mesyuarat kita bermula pada pukul tiga petang",
            "0",
            module="emotion",
            category="harian",
        ),
    ]


class SimilarityEngineTests(unittest.TestCase):
    def test_normalization_is_unicode_aware_and_delexicalizes_values(self):
        left = normalize_text("BAYAR RM100 di https://contoh.my — sekarang!")
        right = normalize_text("bayar RM500 di www.contoh.my sekarang")
        self.assertEqual(left, right)
        self.assertIn("moneytoken", left)
        self.assertIn("urltoken", left)

    def test_exact_template_match_is_deterministic(self):
        engine = ReferenceSimilarityEngine(sample_records())
        first = engine.query("Bayar RM900 hari ini untuk tebus hadiah anda")
        second = engine.query("Bayar RM900 hari ini untuk tebus hadiah anda")
        self.assertEqual(first.as_dict(), second.as_dict())
        self.assertEqual(first.risk_matches[0].record_id, "R1")
        self.assertAlmostEqual(first.risk_matches[0].similarity, 1.0, places=8)
        self.assertGreater(first.data_index, 50.0)
        self.assertEqual(first.reliability, "strong")

    def test_repeated_amount_variants_count_as_one_template(self):
        engine = ReferenceSimilarityEngine(sample_records())
        result = engine.query("Bayar RM800 hari ini untuk tebus hadiah anda", top_k=3)
        risk_ids = [match.record_id for match in result.risk_matches]
        self.assertIn("R1", risk_ids)
        self.assertNotIn("R2", risk_ids)

    def test_control_warning_leans_control(self):
        engine = ReferenceSimilarityEngine(sample_records())
        result = engine.query("Jangan kongsi OTP atau kata laluan dengan sesiapa")
        self.assertEqual(result.control_matches[0].record_id, "C2")
        self.assertLess(result.data_index, 50.0)
        self.assertTrue(result.usable_for_hybrid)

    def test_out_of_domain_input_is_neutral_and_insufficient(self):
        engine = ReferenceSimilarityEngine(sample_records())
        result = engine.query("Fotosintesis klorofil galaksi kuantum")
        self.assertEqual(result.reliability, "insufficient")
        self.assertFalse(result.usable_for_hybrid)
        self.assertEqual(result.data_index, 50.0)
        self.assertEqual(result.recommended_hybrid_weight, 0.0)

    def test_identical_cross_class_references_are_ambiguous(self):
        engine = ReferenceSimilarityEngine(
            [
                ReferenceRecord("R", "Sila hubungi pegawai kami", RISK_LABEL),
                ReferenceRecord("C", "Sila hubungi pegawai kami", CONTROL_LABEL),
            ]
        )
        result = engine.query("Sila hubungi pegawai kami")
        self.assertEqual(result.reliability, "ambiguous")
        self.assertFalse(result.usable_for_hybrid)
        self.assertAlmostEqual(result.data_index, 50.0, places=8)
        self.assertAlmostEqual(result.recommended_hybrid_weight, 0.0, places=8)

    def test_csv_loader_and_aliases(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "references.csv"
            with path.open("w", encoding="utf-8", newline="") as handle:
                writer = csv.DictWriter(
                    handle,
                    fieldnames=["record_id", "text", "binary_label", "module"],
                )
                writer.writeheader()
                writer.writerow(
                    {
                        "record_id": "R",
                        "text": "Kongsi TAC sekarang",
                        "binary_label": "1",
                        "module": "speech",
                    }
                )
                writer.writerow(
                    {
                        "record_id": "C",
                        "text": "Jangan kongsi TAC",
                        "binary_label": "0",
                        "module": "speech",
                    }
                )
            engine = ReferenceSimilarityEngine.from_csv(path)
            result = engine.query("Kongsi TAC sekarang")
            self.assertEqual(result.risk_matches[0].record_id, "R")

    def test_blank_query_is_rejected(self):
        engine = ReferenceSimilarityEngine(sample_records())
        with self.assertRaises(ValueError):
            engine.query("   !!!  ")


if __name__ == "__main__":
    unittest.main()
