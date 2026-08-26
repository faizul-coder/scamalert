"""Open-phrasing regression set for ScamAlert 1.3.

These messages are not used as reference templates.  They exercise paraphrases
across common scam situations and ordinary/control contexts.  Passing this
suite is a regression check, not an estimate of population accuracy.
"""

import unittest

from scamalert_core import analyse_text


RISK_MESSAGES = [
    "J&T: parcel gagal dihantar. Klik https://jnt-redelivery.top dan bayar RM1.50 dalam 2 jam.",
    "Bungkusan luar negara ditahan kastam. Transfer caj pelepasan RM250 sekarang.",
    "Your delivery is on hold. Pay the customs fee at https://delivery-clearance.xyz today.",
    "Pos Malaysia: alamat tidak lengkap. Kemas kini di pos-track-check.my hari ini atau parcel dibatalkan.",
    "LHDN mahu memulangkan lebihan cukai. Isi butiran bank di https://hasil-refund.top untuk tuntutan.",
    "Refund pembelian anda diluluskan tetapi caj pengesahan RM25 perlu dibayar dahulu.",
    "Anda terlebih bayar bil. Masukkan nombor akaun pada pautan ini supaya wang dikembalikan.",
    "Your tax refund expires today. Click tax-return-check.xyz and submit your bank details.",
    "Mak, ini nombor baru sebab telefon rosak. Tolong transfer RM800 sekarang.",
    "Abang guna nombor kawan kerana telefon hilang. Bank in RM600 untuk kecemasan sekarang.",
    "Dad, this is my new number because my phone is broken. Please send RM500 urgently.",
    "Ibu, save nombor baru ini. Adik perlukan duit untuk bayar hospital hari ini.",
    "Sayang, saya terkandas di luar negara dan perlukan wang untuk hospital. Transfer sekarang.",
    "Tunang awak kemalangan. Bayar deposit pembedahan RM3,000 dengan segera.",
    "Darling, I had an accident. Please send money for the hospital immediately.",
    "Hadiah daripada kekasih anda ditahan kastam. Bayar cukai RM450 untuk pelepasan.",
    "Akaun Touch n Go anda akan disekat. Klik pautan ini dan masukkan OTP segera.",
    "Your Boost wallet will be disabled. Sign in at boost-security-check.xyz and enter your password.",
    "Your mailbox will be disabled today. Sign in at mail-security-check.xyz to keep access.",
    "Maybank mengesan transaksi pelik. Sahkan akaun melalui pautan ini dan berikan TAC sekarang.",
    "Pelaburan kripto dijamin untung 20% seminggu. Mulakan dengan RM100 hari ini.",
    "Robot forex tanpa risiko boleh gandakan modal. Deposit RM500 sekarang untuk bermula.",
    "Pakej USDT memberi pulangan 5 kali ganda dalam tujuh hari. Bank in RM300 hari ini.",
    "Guaranteed crypto returns of 30% every week. Deposit USD100 today to start.",
    "Saya pegawai polis. Bayar kompaun melalui DuitNow sekarang atau waran tangkap dikeluarkan.",
    "Pegawai LHDN memaklumkan tunggakan cukai. Transfer bayaran hari ini atau tindakan mahkamah bermula.",
    "Court notice: click court-case-check.xyz and submit your identity card to avoid arrest.",
    "Saya pegawai bank. Pasang AnyDesk supaya saya boleh selamatkan wang dalam akaun anda.",
    "Kerja sambilan TikTok: top up RM100 untuk buka tugasan dan dapat komisen hari ini.",
    "Product boosting task tersedia. Bayar deposit dahulu untuk keluarkan komisen.",
    "Jawatan dari rumah diluluskan. Yuran pendaftaran RM80 perlu dibayar sekarang.",
    "Complete one more merchant task and reload RM200 to unlock all your commission.",
    "Saya sudah transfer semalam tetapi ejen itu masih menyuruh saya bayar caj tambahan.",
    "Mereka minta saya berikan OTP kononnya untuk pulangkan wang yang hilang.",
    "Saya telah menekan pautan kurier, memasukkan nombor kad dan memberikan OTP "
    "sebelum wang RM1,200 hilang daripada akaun.",
    "I clicked the fake delivery link, entered my card number and shared the OTP. "
    "The money was taken from my account.",
]


NON_HIGH_MESSAGES = [
    "Parcel anda akan dihantar esok. Tiada bayaran diperlukan dan status boleh disemak melalui aplikasi rasmi.",
    "Bungkusan sudah tiba di kaunter dan boleh diambil dengan kad pengenalan; tiada bayaran dikenakan.",
    "Bayaran balik akan dikreditkan secara automatik. Tiada caj dan tiada maklumat bank diminta.",
    "Nilai pelaburan boleh naik atau turun dan modal mungkin mengalami kerugian.",
    "Permohonan kerja diterima melalui portal rasmi dan tiada yuran pendaftaran dikenakan.",
    "Mak, saya sudah sampai rumah. Jumpa selepas makan malam.",
    "Tolong transfer RM20 sekarang untuk makan tengah hari tadi.",
    "Sila bayar deposit sewa seperti yang dinyatakan dalam kontrak rumah.",
    "Bayaran invois perlu dibuat ke akaun syarikat berdaftar seperti dalam pesanan pembelian.",
    "Pihak bank tidak pernah meminta OTP. Jangan klik pautan dan semak melalui aplikasi rasmi.",
    "Jangan kongsi kata laluan e-wallet dengan sesiapa. Hubungi pusat bantuan rasmi.",
    "Mesyuarat fakulti dipindahkan ke bilik seminar pada pukul tiga petang.",
    "Selamat pagi. Semoga urusan hari ini dipermudahkan.",
    "Temu janji doktor ditetapkan pada hari Isnin jam sepuluh pagi.",
    "Resit pembelian dalam talian telah dihantar melalui emel rasmi kedai.",
    "Sila buka portal rasmi universiti untuk menghantar tugasan sebelum kelas esok.",
    "Penyata akaun bank bulan ini tersedia dalam aplikasi rasmi.",
    "Kurier mengesahkan bahawa parcel sudah selamat dihantar kepada penerima.",
    "I love you. See you for dinner tonight.",
    "Mak, nombor telefon saya masih sama. Saya cuma mahu bertanya khabar.",
    "Saya telah membuka portal rasmi universiti dan menghantar tugasan.",
    "I entered my student number on the official university portal.",
]


class OpenMessageRegressionTests(unittest.TestCase):
    def test_common_scam_paraphrases_are_high(self):
        for message in RISK_MESSAGES:
            with self.subTest(message=message):
                result = analyse_text(message)
                self.assertGreaterEqual(result["overall_score"], 50)
                self.assertIn(result["display_level"], {"Tinggi", "Sangat Tinggi"})

    def test_control_and_ordinary_messages_do_not_become_high(self):
        for message in NON_HIGH_MESSAGES:
            with self.subTest(message=message):
                result = analyse_text(message)
                self.assertLess(result["overall_score"], 50)

    def test_unknown_text_abstains_instead_of_claiming_low(self):
        messages = [
            "Fotosintesis klorofil akan dibincangkan esok.",
            "Saya sedang membaca buku di perpustakaan.",
            "Boleh kita berbincang semula minggu hadapan?",
        ]
        for message in messages:
            with self.subTest(message=message):
                result = analyse_text(message)
                self.assertEqual(result["display_level"], "Bukti Tidak Mencukupi")


if __name__ == "__main__":
    unittest.main()
