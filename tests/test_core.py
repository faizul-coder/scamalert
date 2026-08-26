import json
import unittest
from pathlib import Path

from scamalert_core import (
    DATA_PATH,
    ENGINE_BUILD,
    analyse_text,
    get_reference_status,
    load_reference_bundle,
)


class ScamAlertCoreTests(unittest.TestCase):
    def test_engine_build_is_current(self):
        self.assertEqual(ENGINE_BUILD, "2026-08-26-aid-phishing-v2")

    def test_reference_data_is_loaded_with_audited_counts(self):
        status = get_reference_status()
        self.assertTrue(status["loaded"])
        stats = status["statistics"]
        self.assertEqual(stats["source_rows"], 6072)
        self.assertEqual(stats["exact_unique_messages"], 164)
        self.assertEqual(stats["normalized_templates"], 90)
        self.assertEqual(stats["templates_by_label"], {"control": 33, "risk": 57})

    def test_missing_reference_file_fails_loudly(self):
        with self.assertRaises(FileNotFoundError):
            load_reference_bundle(Path("data/does-not-exist.json"))

    def test_every_reference_template_is_read_and_directionally_aligned(self):
        # This is a runtime wiring/regression check on the same controlled
        # references, not an independent estimate of model accuracy.
        payload = json.loads(DATA_PATH.read_text(encoding="utf-8"))
        for row in payload["templates"]:
            result = analyse_text(row["representative_text"])
            if row["binary_label"] == "risk":
                self.assertGreaterEqual(result["overall_score"], 50, row["template_id"])
                self.assertEqual(result["risk_matches"][0]["record_id"], row["template_id"])
            else:
                self.assertLess(result["overall_score"], 50, row["template_id"])
                self.assertEqual(result["control_matches"][0]["record_id"], row["template_id"])

    def test_victim_report_with_repeated_payment_is_high(self):
        messages = [
            "Saya sudah bayar dua kali, tetapi mereka masih minta deposit tambahan "
            "untuk keluarkan duit hari ini.",
            "Saya telah pindahkan wang dan sekarang dia meminta caj tambahan.",
            "Saya dah bayar dua kali tetapi dia minta bayar lagi.",
            "Saya dah bayar semalam. Mereka minta duit lagi.",
            "Saya telah pindahkan RM500. Ejen itu masih meminta caj tambahan.",
        ]
        for message in messages:
            result = analyse_text(message)
            self.assertGreaterEqual(result["overall_score"], 68, message)
            self.assertIn("bayaran", result["threat_category"].lower())

    def test_safety_negations_stay_low(self):
        messages = [
            "Pihak bank tidak pernah meminta OTP. Jangan kongsi OTP, PIN atau kata "
            "laluan dengan sesiapa. Semak melalui aplikasi rasmi.",
            "Jangan berikan maklumat bank sekarang. Semak melalui aplikasi rasmi.",
            "Jangan hantar kad pengenalan sekarang. Hubungi portal rasmi.",
            "Bank tidak pernah meminta maklumat bank atau nombor akaun melalui mesej.",
        ]
        for message in messages:
            self.assertLessEqual(analyse_text(message)["overall_score"], 24, message)

    def test_english_and_code_switch_critical_messages_are_high(self):
        messages = [
            "Your bank detected unusual activity. Send your OTP now. If you do not, "
            "your account will be frozen in 15 minutes.",
            "Your loan has been approved. Pay a processing fee of RM300 now before "
            "the money is released today.",
            "Your loan dah approved. Make payment RM300 sekarang. Then kami release "
            "duit hari ini.",
        ]
        for message in messages:
            self.assertGreaterEqual(analyse_text(message)["overall_score"], 50, message)

    def test_english_victim_report_is_high(self):
        messages = [
            "I already paid twice, but they still ask for another deposit to release my money today.",
            "I already paid them twice. They still demand another deposit before they will release my money today.",
            "I paid yesterday. Now they want more money.",
            "I have already sent RM500. The agent keeps requesting an additional fee.",
        ]
        for message in messages:
            self.assertGreaterEqual(analyse_text(message)["overall_score"], 68, message)

    def test_completed_victim_experiences_are_high(self):
        messages = [
            "Semalam saya menerima mesej kononnya daripada syarikat kurier. Saya "
            "telah menekan pautan itu, memasukkan nombor kad dan memberikan kod OTP "
            "sebelum wang RM1,200 hilang daripada akaun.",
            "Saya sudah ditipu. Saya klik pautan yang dihantar dan beri OTP, kemudian "
            "duit dalam akaun saya lesap.",
            "Saya dah memasukkan OTP dan membuat pindahan RM900. Wang itu hilang "
            "selepas transaksi tersebut.",
            "Kami telah memasang AnyDesk selepas orang yang mengaku pegawai bank "
            "menghubungi kami. Wang dalam akaun kemudian dikeluarkan.",
            "I clicked the courier link, entered my card number and shared the OTP. "
            "The money was taken from my account.",
            "I was scammed after I provided my password and transferred USD500. "
            "The funds are now gone.",
        ]
        for message in messages:
            result = analyse_text(message)
            self.assertGreaterEqual(result["overall_score"], 75, message)
            self.assertIn(result["display_level"], {"Tinggi", "Sangat Tinggi"})

    def test_completed_benign_actions_do_not_become_high(self):
        messages = [
            "Saya telah membuka portal rasmi universiti dan menghantar tugasan.",
            "Saya memasukkan nombor kad pada portal rasmi bank untuk membayar bil.",
            "Saya tidak menekan pautan dan tidak memberikan OTP kepada sesiapa.",
            "Dalam simulasi keselamatan, tiada wang hilang dan tiada OTP sebenar digunakan.",
            "I entered my student number on the official university portal.",
        ]
        for message in messages:
            self.assertLess(analyse_text(message)["overall_score"], 50, message)

    def test_english_safety_warning_stays_low(self):
        message = (
            "The bank will never ask for your OTP. Do not share your OTP or PIN with "
            "anyone. Verify through the official app."
        )
        self.assertLessEqual(analyse_text(message)["overall_score"], 24)

    def test_ordinary_urgent_payments_do_not_cross_high_risk_boundary(self):
        messages = [
            "Please transfer RM50 now for lunch.",
            "Tolong transfer RM50 sekarang untuk bayar makan tengah hari.",
            "Sila bayar deposit sewa rumah RM500 hari ini seperti dalam perjanjian.",
            "Saya dah bayar bil semalam, tapi masih kena bayar caj tambahan hari ini.",
            "Please make a payment RM500 today for the registered company invoice.",
        ]
        for message in messages:
            self.assertLess(analyse_text(message)["overall_score"], 50, message)

    def test_safety_bait_does_not_mask_later_dangerous_command(self):
        messages = [
            "Jangan bayar caj proses kepada orang lain, bayar deposit RM500 kepada saya sekarang.",
            "Jangan klik pautan lain, klik pautan ini sekarang untuk tebus hadiah.",
            "Tidak perlu bayaran caj proses; cuma deposit RM300 sekarang.",
        ]
        for message in messages:
            self.assertGreaterEqual(analyse_text(message)["overall_score"], 50, message)

    def test_out_of_domain_message_abstains(self):
        result = analyse_text("Fotosintesis klorofil galaksi kuantum dibincangkan esok.")
        self.assertEqual(result["data_reliability"], "insufficient")
        self.assertEqual(result["data_weight"], 0.0)
        self.assertLessEqual(result["overall_score"], 24)

    def test_pinjaman_does_not_trigger_pin_request(self):
        result = analyse_text(
            "Permohonan pinjaman sedang diproses. Semak status melalui portal rasmi bank."
        )
        self.assertLessEqual(result["overall_score"], 24)
        self.assertNotIn("permintaan kata laluan/PIN", result["direct_phrases"])

    def test_fake_cash_aid_link_is_very_high(self):
        message = (
            "TERKINI: PERMOHONAN BANTUAN TUNAI (SARA FASA 1 2025) KINI "
            "TELAH DIBUKA UNTUK RAKYAT MALAYSIA SEBANYAK RM150-RM300. "
            "SEMAK SEKARANG: https://new-malaysia.info-ind.com/bantuan26/ "
            "Semak Status. Isi Nombor. Code Verification."
        )
        result = analyse_text(message)
        self.assertGreaterEqual(result["overall_score"], 75)
        self.assertEqual(result["display_level"], "Sangat Tinggi")
        self.assertEqual(
            result["threat_category"],
            "Risiko bantuan tunai palsu atau pancingan data",
        )
        self.assertIn("arahan menyemak segera", result["direct_phrases"])
        self.assertIn("desakan masa", result["indirect_phrases"])
        self.assertIn("E2 Kecemasan", result["emotions"])
        self.assertIn("M5", [move["code"] for move in result["moves"]])

    def test_official_cash_aid_notice_does_not_receive_fake_aid_floor(self):
        message = (
            "Maklumat Bantuan Tunai: semak status melalui portal rasmi "
            "https://bantuantunai.hasil.gov.my. Tiada bayaran dan jangan kongsi OTP."
        )
        result = analyse_text(message)
        self.assertLess(result["overall_score"], 50)
        self.assertNotEqual(
            result["threat_category"],
            "Risiko bantuan tunai palsu atau pancingan data",
        )


if __name__ == "__main__":
    unittest.main()
