"""Core analysis for the ScamAlert NICE 2026 hybrid prototype.

This module combines two explicitly separate signals:

1. explainable linguistic rules; and
2. similarity to a deduplicated controlled reference corpus.

The returned 0-100 values are screening indices.  They are not probabilities,
accuracy estimates, or legal determinations that a sender is a scammer.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple

from scamalert_similarity import ReferenceRecord, ReferenceSimilarityEngine


DATA_PATH = Path(__file__).resolve().parent / "data" / "reference_data.json"


DIRECT_PATTERNS: Dict[str, Tuple[int, str]] = {
    r"\b(?:berikan|beri|masukkan|kongsi|hantar|dedahkan|send|share|provide|enter|reveal)\s+(?:(?:kod|your|the)\s+)?(?:otp|tac|one[ -]time password)\b": (35, "permintaan OTP/TAC"),
    r"\b(?:berikan|beri|masukkan|kongsi|hantar|dedahkan|send|share|provide|enter|reveal)\s+(?:(?:your|the)\s+)?(?:kata laluan|password|pin)\b": (35, "permintaan kata laluan/PIN"),
    r"\b(?:bayar|buat bayaran|pay)\s+(?:(?:the|a|your)\s+)?(?:caj proses|caj pengesahan|processing fee|verification fee)\b|\b(?:caj (?:proses|pengesahan)|processing fee|verification fee)\b": (30, "bayar caj proses/pengesahan"),
    r"\b(?:bayar\s+|pay\s+)?(?:yuran pendaftaran|registration fee|deposit)(?:\s+rm)?\b|\b(?:bayaran deposit|deposit payment)\b": (28, "bayaran pendahuluan"),
    r"\b(?:bayar|buat bayaran|pay)[^.!?;:]{0,45}(?:sebelum|untuk|before|to)\s+(?:keluarkan|pengeluaran|withdraw|release)|\b(?:caj|bayaran|withdrawal) (?:pengeluaran|fee)\b|\b(?:aktifkan pengeluaran|activate (?:the )?withdrawal)\b": (45, "bayaran sebelum pengeluaran wang"),
    r"\b(?:pindahkan|transfer|send)\s+(?:(?:the|your)\s+)?(?:wang|duit|money|funds|rm)|\b(?:buat bayaran|make (?:a )?payment)\b|\b(?:bayar|pay)\s+rm\b|\b(?:bayar\s+(?:dulu|dahulu)|pay\s+(?:first|now|upfront))\b": (35, "arahan pindahan wang"),
    r"\b(?:daftar|aktifkan akaun|sahkan akaun|register|activate (?:your )?account|verify (?:your )?account)\s+(?:segera|sekarang|hari ini|urgently|now|today|immediately)\b": (20, "arahan segera mendaftar/mengesahkan"),
    r"\b(?:klik|tekan|buka|click|tap|open)\s+(?:(?:the|this)\s+)?(?:pautan|link)(?:\s+(?:ini|di bawah|below))?\b": (22, "arahan menekan pautan"),
    r"\b(?:semak\s+sekarang|check\s+now)\b": (22, "arahan menyemak segera"),
    r"\b(?:isi|masukkan|enter|fill(?:\s+in)?)[^.!?;:]{0,35}(?:nombor|number|kod pengesahan|verification code)\b": (30, "permintaan nombor/kod pengesahan"),
    r"\b(?:hantar|berikan|beri|masukkan|kongsi|dedahkan|send|provide|enter|share|reveal)[^.!?;:]{0,40}(?:maklumat bank|butiran bank|kad pengenalan|nombor akaun|maklumat peribadi|bank details|identity card|account number|personal information)\b": (35, "permintaan data peribadi/kewangan"),
    r"\b(?:akaun|account)[^.!?;:]{0,35}(?:dibekukan|disekat|ditutup|frozen|blocked|suspended|closed)\b": (35, "ancaman akaun dibekukan/disekat"),
}


INDIRECT_PATTERNS: Dict[str, Tuple[int, str]] = {
    r"\b(?:jika|kalau|sekiranya)\s+(?:gagal|tidak)|\bjika anda tidak\b|\bif (?:you )?(?:fail|do not|don't)\b": (18, "ancaman tersirat"),
    r"\b(?:segera|sekarang|serta-merta|akhir hari ini|urgent|urgently|now|immediately|by end of today)\b": (12, "desakan masa"),
    r"\b(?:24 (?:jam|hours)|15 (?:minit|minutes)|30 (?:minit|minutes)|5 (?:minit|minutes)|hari ini|today|before (?:\d+|noon|midnight)|sebelum (?:jam|pukul)|pukul \d+)\b": (17, "had masa"),
    r"\b(?:(?:slot|kuota|tempat) terhad|limited (?:slots|places|quota))\b|\b(?:tinggal|only) \d+(?: left)?\b": (18, "kelangkaan palsu"),
    r"\b(?:risiko rendah|dijamin|tanpa risiko|jaminan untung|low risk|guaranteed|no risk|guaranteed profit)\b": (18, "jaminan tidak realistik"),
    r"\b(?:pulangan tinggi|untung besar|keuntungan harian|high returns?|big profits?|daily profits?|wang[^.!?;:]{0,25}dilepaskan|money[^.!?;:]{0,30}(?:released|unlocked)|keluarkan duit|pengeluaran wang|release (?:your )?(?:money|funds))\b|\bmodal[^.!?;:]{0,20}jadi\b": (22, "janji/pelepasan wang"),
    r"\b(?:terpilih|layak menerima|peluang khas|selected|eligible|special opportunity)\b|\b(?:permohonan|application)[^.!?;:]{0,30}(?:diluluskan|approved)\b": (15, "peluang eksklusif"),
    r"\b(?:jangan beritahu sesiapa|rahsia antara kita|keep (?:this|it) secret|do not tell anyone|don't tell anyone)\b": (22, "arahan merahsiakan urusan"),
    r"\b(?:nombor baru|telefon rosak|phone (?:is )?(?:broken|lost)|new (?:phone|number))\b": (18, "perubahan identiti atau nombor secara tiba-tiba"),
}


# Scenario signals extend the linguistic layer beyond the small controlled
# reference set.  A scenario is only elevated when several independent cues
# co-occur (for example parcel + fee + link), not from one keyword alone.
SCENARIO_PATTERNS: Dict[str, str] = {
    "url": r"(?:https?://|hxxps?://|www\.|\b(?:bit\.ly|tinyurl\.com|t\.me)/\S+|\b[a-z0-9][a-z0-9-]{2,}\.(?:com|net|org|my|xyz|top|site|online|live|link)(?:/\S*)?)",
    "click_or_login": r"\b(?:klik|tekan|buka|layari|log masuk|login|sign in|click|tap|open|visit|verify|sahkan|kemas kini|update|semak|check|mohon|apply|isi|fill)\b",
    "money_request": r"\b(?:bayar|bayaran|buat bayaran|pindah(?:kan)?|transfer|bank in|duitnow|top ?up|reload|deposit|caj|yuran|fee|payment|pay|send money|pinjam(?:kan)? duit|bantu[^.!?;:]{0,20}(?:wang|duit))\b",
    "fee": r"\b(?:caj|yuran|fee|tax|cukai|kastam|customs|clearance|insurans|insurance|processing|pengesahan|verification|penghantaran|delivery charge)\b",
    "amount": r"(?:\b(?:rm|myr|usd|sgd)\s*\d|\$\s*\d|\b\d+(?:[.,]\d+)?\s*%|\b\d+\s*(?:kali|x|ganda)\b)",
    "sensitive": r"\b(?:otp|tac|pin|kata laluan|password|nombor akaun|account number|maklumat bank|bank details|kad pengenalan|ic|identity card|cvv|nombor kad|card number|butiran kad|card details)\b",
    "sensitive_request": r"\b(?:berikan|beri|masukkan|kongsi|hantar|dedahkan|isi|provide|enter|share|send|reveal|submit)[^.!?;:]{0,45}(?:otp|tac|pin|kata laluan|password|nombor akaun|account number|maklumat bank|bank details|kad pengenalan|identity card|cvv|butiran kad|card details)\b|\b(?:otp|tac|pin|kata laluan|password|nombor akaun|account number|maklumat bank|bank details|kad pengenalan|identity card|cvv|butiran kad|card details)[^.!?;:]{0,25}(?:diperlukan|diminta|required|requested)\b",
    "account_threat": r"\b(?:akaun|account|emel|email|mailbox|wallet|dompet)[^.!?;:]{0,45}(?:dibekukan|disekat|ditutup|digantung|ditamatkan|frozen|blocked|suspended|closed|disabled|terminated)\b",
    "consequence": r"\b(?:ditahan|tertahan|dibatalkan|disekat|gagal dihantar|dirampas|denda|saman|tangkap|waran|tindakan mahkamah|tindakan undang-undang|held|on hold|cancelled|blocked|failed delivery|seized|fine|arrest|warrant|court action|legal action)\b",
    "urgency": r"\b(?:segera|sekarang|serta-merta|hari ini|urgent|urgently|now|immediately|today|dalam \d+ (?:minit|jam)|within \d+ (?:minutes?|hours?))\b",
    "parcel": r"\b(?:parcel|bungkusan|pakej penghantaran|kurier|courier|delivery|penghantaran|pos malaysia|j&t|dhl|fedex|kastam|customs)\b",
    "refund": r"\b(?:refund|bayaran balik|pemulangan wang|wang dikembalikan|rebat|lebihan bayaran|tax refund|pulangan cukai|tuntut semula|claim refund)\b",
    "ewallet": r"\b(?:e-?wallet|dompet digital|touch\s*['n’]?\s*go|tng|boost|shopeepay|grabpay|bigpay|mae)\b",
    "investment": r"\b(?:pelaburan|melabur|investment|invest|crypto|kripto|forex|trading|dagangan|saham|bitcoin|usdt|portfolio|pakej pelaburan)\b",
    "gain": r"\b(?:dijamin|jaminan|tanpa risiko|guaranteed|no risk|untung|keuntungan|profit|pulangan|return|dividen|gandakan|double|pasif|passive income)\b",
    "job": r"\b(?:kerja sambilan|part[ -]?time job|jawatan|job|tugasan|task|komisen|commission|like dan follow|like and follow|product boosting|merchant task)\b",
    "family_identity": r"\b(?:mak|mama|ibu|ayah|abah|papa|adik|abang|kakak|anak|suami|isteri|family|mum|mom|dad|father|mother|brother|sister|son|daughter|wife|husband)\b",
    "identity_change": r"\b(?:ini nombor baru|save nombor (?:baru|ini)|telefon (?:saya )?(?:rosak|hilang)|phone (?:is )?(?:broken|lost)|new (?:phone|number)|guna nombor kawan)\b",
    "romance": r"\b(?:sayang|dear|darling|honey|love you|cinta|kekasih|tunang|fianc[eé]|pasangan|kenal (?:dalam talian|online)|online partner)\b",
    "emergency": r"\b(?:kecemasan|emergency|hospital|kemalangan|accident|sakit|operation|pembedahan|visa|tiket|ticket|terkandas|stranded)\b",
    "authority": r"\b(?:bank|bnm|bank negara|pdrm|polis|mahkamah|lhdn|hasil|mcmc|skmm|kwsp|epf|perkeso|socso|kastam|customs|pegawai|officer|mahkamah|court|kerajaan|government)\b",
    "benefit": r"\b(?:bantuan(?:\s+tunai)?|sumbangan tunai rahmah|subsidi|geran|cash aid|cash assistance|financial assistance|government aid)\b|\bsara\s+(?:fasa|202\d)\b|\bstr(?:\s+202\d)?\b",
    "application_action": r"\b(?:permohonan|mohon|semak\s+(?:sekarang|status|kelayakan)|isi\s+(?:nombor|maklumat|borang)|code verification|kod pengesahan|application|apply|check\s+(?:now|status|eligibility)|fill\s+(?:in|out))\b",
    "government_domain": r"https?://(?:[a-z0-9-]+\.)*gov\.my(?:[/:]|$)",
    "official_source": r"\b(?:portal|laman|aplikasi|saluran)\s+rasmi\b|\bofficial\s+(?:portal|website|app|application|channel)\b",
    "remote_access": r"\b(?:anydesk|teamviewer|quicksupport|remote access|screen sharing|kongsi skrin|perkongsian skrin)\b",
    "secrecy": r"\b(?:jangan beritahu|jangan maklumkan|rahsia|sulit|secret|confidential|do not tell|don't tell|keep (?:this|it) secret)\b",
    "victim_report": r"\b(?:dia|mereka|admin|ejen|agen|penjual|scammer|penipu|he|she|they|agent|seller)[^.!?]{0,55}(?:minta|meminta|suruh|menyuruh|desak|janji|ask|asked|asking|told|demand|promised)\b|\b(?:saya|kami|i|we)[^.!?]{0,50}(?:diminta|disuruh|didesak|was asked|were asked|was told|were told)\b",
    "victim_marker": r"\b(?:saya|kami|i|we)\b[^.!?]{0,70}\b(?:ditipu|terpedaya|terkena tipu|menjadi mangsa|jadi mangsa|scammed|defrauded|fooled|tricked)\b",
    "victim_action": r"\b(?:saya|kami|i|we)\b[^.!?]{0,90}\b(?:klik|menekan|tekan|membuka|buka|melayari|memasukkan|masukkan|mengisi|isi|memberikan|berikan|beri|berkongsi|kongsi|menghantar|hantar|membayar|bayar|memindahkan|pindahkan|transfer|memasang|pasang|clicked|tapped|opened|visited|entered|submitted|provided|shared|sent|paid|transferred|installed)\b",
    "loss_outcome": r"\b(?:wang|duit|baki|money|funds|balance)\b[^.!?]{0,55}\b(?:hilang|lesap|dicuri|dikeluarkan|dipindahkan|ditolak|gone|missing|stolen|taken|withdrawn|transferred|deducted|drained)\b|\b(?:rm|myr|usd|sgd|\$)\s*\d[^.!?]{0,35}\b(?:hilang|lesap|dicuri|gone|missing|stolen|taken|withdrawn|deducted|drained)\b|\b(?:kehilangan|kerugian|lost)\b[^.!?]{0,35}\b(?:rm|myr|usd|sgd|wang|duit|money|funds)\b",
    "loss_denial": r"\b(?:tiada|tidak ada|tak ada|no)\b[^.!?]{0,25}\b(?:wang|duit|money|funds)\b[^.!?]{0,25}\b(?:hilang|lesap|gone|missing|stolen|taken)\b",
    "impersonation_report": r"\b(?:kononnya|menyamar sebagai|mengaku sebagai|pretending to be|claimed to be|impersonat(?:ed|ing))\b",
}


def analyse_scenarios(text: str) -> dict:
    """Identify multi-cue scam scenarios and return a conservative score floor."""

    flags = {
        name: bool(re.search(pattern, text, flags=re.I))
        for name, pattern in SCENARIO_PATTERNS.items()
    }
    if flags["loss_denial"]:
        flags["loss_outcome"] = False
    floor = 0
    category = ""
    reasons: List[str] = []

    def elevate(score: int, label: str, *evidence: str) -> None:
        nonlocal floor, category
        if score > floor:
            floor = score
            category = label
        reasons.extend(evidence)

    dangerous_action = flags["money_request"] or flags["sensitive_request"] or flags["click_or_login"]
    non_official_url = (
        flags["url"]
        and not flags["government_domain"]
        and not flags["official_source"]
    )

    # Fake-aid phishing commonly combines a public-benefit claim, a cash
    # amount, an instruction to check/apply and a non-government link. No
    # single cue is sufficient; the high floor only applies to the complete
    # combination so genuine notices on official portals stay low.
    if (
        flags["benefit"]
        and flags["application_action"]
        and flags["amount"]
        and non_official_url
    ):
        elevate(
            84,
            "Risiko bantuan tunai palsu atau pancingan data",
            "Dakwaan bantuan tunai atau kelayakan digunakan untuk menarik perhatian",
            "Jumlah wang tertentu ditonjolkan",
            "Pengguna diarahkan menyemak atau mengisi maklumat melalui pautan bukan domain kerajaan",
        )
    elif (
        flags["benefit"]
        and flags["application_action"]
        and flags["urgency"]
        and non_official_url
    ):
        elevate(
            78,
            "Risiko bantuan tunai palsu atau pancingan data",
            "Dakwaan bantuan disertai arahan segera",
            "Pautan yang diberikan bukan domain kerajaan",
        )

    if flags["sensitive_request"] and (
        flags["authority"] or flags["account_threat"] or flags["ewallet"]
    ) and (flags["click_or_login"] or flags["url"] or flags["consequence"]):
        elevate(
            86,
            "Risiko penyamaran dan pengambilalihan akaun",
            "Permintaan data akses atau kewangan sensitif",
            "Penyamaran institusi atau ancaman terhadap akaun",
        )

    if flags["authority"] and (flags["account_threat"] or flags["consequence"]) and dangerous_action:
        elevate(
            80,
            "Risiko penyamaran autoriti",
            "Nama institusi atau autoriti digunakan untuk membina kepercayaan",
            "Ancaman atau akibat digunakan untuk mendesak tindakan",
        )

    if flags["parcel"] and flags["fee"] and (
        flags["money_request"] or flags["url"] or flags["click_or_login"]
    ):
        elevate(
            76,
            "Risiko penghantaran atau bungkusan palsu",
            "Dakwaan bungkusan disertai caj atau bayaran",
            "Pengguna diarahkan bertindak melalui mesej",
        )
    elif flags["parcel"] and flags["url"] and flags["consequence"]:
        elevate(
            68,
            "Risiko penghantaran atau bungkusan palsu",
            "Dakwaan bungkusan bermasalah",
            "Pautan tidak disahkan diberikan",
        )

    if flags["refund"] and (
        flags["fee"] or flags["sensitive_request"] or flags["url"] or flags["click_or_login"]
    ):
        elevate(
            74,
            "Risiko bayaran balik atau tuntutan palsu",
            "Janji bayaran balik atau tuntutan wang",
            "Bayaran, pautan atau maklumat peribadi diminta",
        )

    if flags["ewallet"] and (
        flags["sensitive_request"] or flags["account_threat"] or flags["url"]
    ) and flags["click_or_login"]:
        elevate(
            78,
            "Risiko e-dompet atau pengambilalihan akaun",
            "Akaun e-dompet dijadikan sasaran",
            "Pengesahan melalui pautan atau data akses diminta",
        )

    if flags["family_identity"] and flags["identity_change"] and (
        flags["money_request"] or flags["amount"]
    ):
        elevate(
            74,
            "Risiko penyamaran ahli keluarga",
            "Identiti keluarga dan nombor baharu digunakan",
            "Permintaan wang dibuat tanpa pengesahan bebas",
        )

    if flags["romance"] and flags["emergency"] and flags["money_request"]:
        elevate(
            74,
            "Risiko percintaan atau kecemasan palsu",
            "Hubungan emosi digunakan untuk membina kepercayaan",
            "Kecemasan disertai permintaan wang",
        )

    if flags["investment"] and flags["gain"] and (
        flags["money_request"] or flags["amount"] or flags["urgency"]
    ):
        elevate(
            74,
            "Risiko pelaburan atau pulangan palsu",
            "Janji keuntungan atau pulangan tidak realistik",
            "Pelaburan dikaitkan dengan wang atau tindakan segera",
        )

    if flags["job"] and flags["money_request"]:
        elevate(
            70,
            "Risiko kerja sambilan atau tugasan palsu",
            "Tawaran kerja atau komisen digunakan",
            "Bayaran, deposit atau tambah nilai diminta",
        )

    if non_official_url and flags["click_or_login"] and (
        flags["account_threat"] or flags["authority"] or flags["parcel"]
        or flags["refund"] or flags["ewallet"]
    ):
        elevate(
            76,
            "Risiko pautan palsu atau pancingan data",
            "Pautan atau log masuk diminta",
            "Identiti perkhidmatan digunakan untuk meyakinkan pengguna",
        )

    if flags["remote_access"] and (flags["authority"] or flags["money_request"]):
        elevate(
            82,
            "Risiko akses jauh kepada peranti",
            "Aplikasi kawalan jauh diminta",
            "Arahan dikaitkan dengan autoriti atau transaksi",
        )

    retrospective_victim = flags["victim_action"] and (
        flags["victim_marker"]
        or flags["loss_outcome"]
        or flags["impersonation_report"]
    )
    retrospective_risk_cue = (
        flags["sensitive"]
        or flags["money_request"]
        or flags["url"]
        or flags["remote_access"]
        or flags["amount"]
        or flags["loss_outcome"]
    )
    if retrospective_victim and retrospective_risk_cue:
        elevate(
            78,
            category or "Risiko kehilangan wang atau penyalahgunaan data",
            "Mesej melaporkan tindakan berisiko yang telah berlaku",
            "Data sensitif, wang atau kesan kerugian dikenal pasti",
        )

    if flags["victim_report"] and (
        flags["money_request"] or flags["sensitive_request"] or flags["remote_access"]
    ):
        elevate(
            68,
            category or "Risiko bayaran berulang atau permintaan tambahan",
            "Mesej melaporkan permintaan daripada pihak lain",
            "Permintaan berisiko kekal dikesan walaupun dituturkan oleh mangsa",
        )

    if flags["secrecy"] and dangerous_action:
        elevate(
            max(68, floor),
            category or "Mesej berisiko dengan arahan merahsiakan urusan",
            "Penerima diarahkan merahsiakan urusan",
        )

    # Generic evidence is useful to explain a result even when no named
    # scenario reaches a high-risk floor.
    if flags["money_request"]:
        reasons.append("Permintaan bayaran atau pindahan wang")
    if flags["sensitive_request"]:
        reasons.append("OTP, kata laluan atau maklumat kewangan disebut")
    if flags["url"] and flags["click_or_login"]:
        reasons.append("Pautan atau log masuk diminta")

    return {
        "floor": min(100, floor),
        "category": category,
        "reasons": unique(reasons),
        "flags": flags,
    }


EMOTION_PATTERNS: Dict[str, List[str]] = {
    "E1 Ketakutan": [
        r"akaun[^.!?;:]{0,30}(?:dibekukan|disekat)",
        r"account[^.!?;:]{0,35}(?:frozen|blocked|suspended|closed)",
        r"disenarai hitam",
        r"blacklisted",
        r"aktiviti luar biasa",
        r"unusual activity|suspicious activity",
        r"tindakan undang-undang",
        r"legal action",
        r"kehilangan akses",
        r"lose access|loss of access",
    ],
    "E2 Kecemasan": [r"\bsegera\b", r"\bsekarang\b", r"\b24 jam\b", r"\b15 minit\b", r"\b30 minit\b", r"\bhari ini\b", r"\burgent(?:ly)?\b", r"\bnow\b", r"\bimmediately\b", r"\btoday\b", r"\b15 minutes\b", r"\b30 minutes\b", r"\b24 hours\b"],
    "E3 Harapan Keuntungan": [r"\buntung\b", r"\bganjaran\b", r"\bbonus\b", r"\bpulangan\b", r"\bhadiah\b", r"\bprofit\b", r"\breward\b", r"\breturns?\b", r"\bprize\b", r"wang[^.!?;:]{0,25}dilepaskan", r"(?:money|funds)[^.!?;:]{0,30}(?:released|unlocked)"],
    "E4 Pembinaan Kepercayaan": [
        r"jangan risau",
        r"do not worry|don't worry",
        r"percayakan saya",
        r"trust me",
        r"saya (?:akan )?bantu",
        r"i (?:will|can) help",
        r"(?:bank|pegawai|pihak berkuasa)[^.!?;:]{0,40}(?:otp|tac|bayar|pautan|akaun[^.!?;:]{0,15}(?:beku|sekat))",
        r"(?:bank|officer|authority)[^.!?;:]{0,45}(?:otp|password|pay|link|account[^.!?;:]{0,18}(?:frozen|blocked))",
        r"(?:lesen|suruhanjaya|syarikat berdaftar)[^.!?;:]{0,45}(?:pelaburan|untung|pulangan|deposit)",
        r"(?:licensed|commission|registered company)[^.!?;:]{0,50}(?:investment|profit|return|deposit)",
    ],
    "E5 Simpati": [r"\bsumbangan\b", r"anak sakit", r"\bkesusahan\b", r"\bderma\b", r"kecemasan keluarga", r"\bdonation\b", r"sick child", r"family emergency", r"hardship"],
    "E6 Rasa Bersalah": [r"jika anda tidak", r"anda punca", r"tolong saya", r"jangan kecewakan", r"harap kerjasama", r"if you do not", r"your fault", r"help me", r"do not disappoint", r"need your cooperation"],
}


CONTROL_PATTERNS: Dict[str, str] = {
    r"\b(?:melalui )?(?:aplikasi|portal|laman|saluran|kaunter) rasmi\b|\b(?:official (?:app|application|portal|website|channel|counter)|through (?:the )?official (?:app|application|portal|website|channel))\b": "saluran rasmi",
    r"\btertakluk (?:pada|kepada) terma dan syarat\b|\bterma dan syarat\b|\bterms and conditions\b": "terma dan syarat",
    r"\b(?:jangan|tidak|tak)[^.!?;:]{0,45}(?:kongsi|berkongsi|meminta|minta)[^.!?;:]{0,25}(?:otp|tac|pin|kata laluan|password)\b|\b(?:do not|don't|never|will never)[^.!?;:]{0,45}(?:share|send|provide|ask|request)[^.!?;:]{0,30}(?:otp|one[ -]time password|pin|password)\b": "peringatan keselamatan akses",
    r"\b(?:jangan|tidak|tak)[^.!?;:]{0,45}(?:maklumat bank|kad pengenalan|nombor akaun|maklumat peribadi)\b|\b(?:do not|don't|never)[^.!?;:]{0,45}(?:bank details|identity card|account number|personal information)\b": "peringatan keselamatan data peribadi",
    r"\b(?:emel|alamat emel) rasmi\b|\bofficial (?:email|email address)\b": "emel rasmi",
    r"\bakaun syarikat berdaftar\b|\bregistered company account\b": "akaun syarikat berdaftar",
    r"\b(?:invois|resit) rasmi\b|\binvois syarikat berdaftar\b|\bofficial (?:invoice|receipt)\b|\b(?:registered company|company) invoice\b|\binvoice (?:from|for) (?:a |the )?registered company\b": "invois/resit rasmi",
    r"\b(?:semak dahulu|membuat semakan|semakan melalui|sahkan melalui)\b|\b(?:verify|check|confirm) (?:first|through|via)[^.!?;:]{0,25}(?:official|bank|provider)\b": "semakan rasmi",
    r"\b(?:tanpa|tiada|tidak perlu)[^.!?;:]{0,25}(?:bayaran|caj|deposit|yuran)\b|\b(?:no|without)[^.!?;:]{0,20}(?:payment|fee|deposit|charge)\b": "tiada bayaran awal",
    r"\b(?:pelaburan|investment)[^.!?;:]{0,55}(?:risiko|kerugian|kehilangan modal|risk|loss|lose money)\b|\b(?:modal|nilai pelaburan|investment value)[^.!?;:]{0,45}(?:boleh turun|mungkin rugi|may fall|may decline|may be lost)\b": "pendedahan risiko pelaburan",
}


# Only the preventive act itself is replaced.  These patterns deliberately do
# not consume text beyond a comma, semicolon, contrast marker, or later command.
SENSITIVE_ITEM = (
    r"(?:otp|tac|pin|kata laluan|password|maklumat bank|butiran bank|"
    r"kad pengenalan|nombor akaun|maklumat peribadi|one[ -]time password|"
    r"bank details|identity card|account number|personal information)"
)
PREVENTIVE_PATTERNS: List[Tuple[str, str]] = [
    (
        rf"\b(?:tiada|tidak ada|tak ada|no)\s+(?:sebarang\s+|any\s+)?(?:nombor\s+|kod\s+)?{SENSITIVE_ITEM}\s+(?:diminta|diperlukan|required|requested)\b",
        "penegasan bahawa data sensitif tidak diminta",
    ),
    (
        rf"\b(?:jangan|usah|elakkan|hindari)\s+(?:sesekali\s+)?(?:kongsi|berkongsi|berikan|beri|masukkan|hantar|dedahkan)\s+(?:sebarang\s+)?(?:nombor\s+|kod\s+)?{SENSITIVE_ITEM}(?:\s*(?:atau|dan)\s*(?:nombor\s+|kod\s+)?{SENSITIVE_ITEM})*\b",
        "peringatan supaya tidak berkongsi data sensitif",
    ),
    (
        rf"\b(?:[\w]+\s+)?(?:tidak|tak)\s+(?:pernah\s+|akan\s+)?(?:meminta|minta|kongsi|berkongsi|berikan|memberikan|masukkan|hantar|dedahkan)\s+(?:sebarang\s+)?(?:nombor\s+|kod\s+)?{SENSITIVE_ITEM}(?:\s*(?:atau|dan)\s*(?:nombor\s+|kod\s+)?{SENSITIVE_ITEM})*\b",
        "penegasan bahawa data sensitif tidak diminta",
    ),
    (
        r"\b(?:jangan|usah|elakkan|hindari)\s+(?:(?:membuat|buat)\s+)?(?:bayar|bayaran|transfer|pindahan)(?:\s+(?:apa-apa|sebarang))?(?:\s+(?:caj proses|caj pengesahan|deposit|yuran|wang|duit))?\b",
        "peringatan supaya tidak membuat bayaran",
    ),
    (
        r"\b(?:tidak|tak)\s+(?:perlu\s+)?(?:(?:membuat|buat)\s+)?(?:bayaran|pembayaran|deposit|caj|yuran)(?:\s+(?:caj proses|caj pengesahan|pendahuluan|awal))?\b",
        "penegasan bahawa bayaran tidak perlu dibuat",
    ),
    (
        r"\b(?:tanpa|tiada|tidak perlu)\s+(?:sebarang\s+)?(?:bayaran|caj|deposit|yuran)(?:\s+(?:pendahuluan|awal|proses|pengesahan))?\b",
        "penegasan bahawa bayaran awal tidak diperlukan",
    ),
    (
        r"\b(?:jangan|usah|elakkan|hindari)\s+(?:menekan|tekan|klik|membuka|buka)\s+(?:sebarang\s+)?(?:pautan|link)\b",
        "peringatan supaya tidak menekan pautan",
    ),
    (
        rf"\b(?:do not|don't|never)\s+(?:ever\s+)?(?:share|send|provide|enter|reveal)\s+(?:(?:your|any|the)\s+)?(?:number\s+|code\s+)?{SENSITIVE_ITEM}(?:\s*(?:or|and)\s*(?:(?:your|any|the)\s+)?(?:number\s+|code\s+)?{SENSITIVE_ITEM})*\b",
        "peringatan supaya tidak berkongsi data sensitif",
    ),
    (
        rf"\b(?:does not|doesn't|will never|would never|never)\s+(?:ask|request)\s+(?:you\s+)?(?:for\s+|to share\s+|to send\s+)?(?:(?:your|any|the)\s+)?{SENSITIVE_ITEM}(?:\s*(?:or|and)\s*(?:(?:your|any|the)\s+)?{SENSITIVE_ITEM})*\b",
        "penegasan bahawa data sensitif tidak diminta",
    ),
    (
        r"\b(?:do not|don't|never)\s+(?:make\s+)?(?:pay|payment|transfer)(?:\s+(?:any|a|the))?(?:\s+(?:processing fee|verification fee|deposit|fee|money|funds))?\b",
        "peringatan supaya tidak membuat bayaran",
    ),
    (
        r"\b(?:no|without|do not need|don't need)\s+(?:any\s+)?(?:payment|fee|deposit|charge)(?:\s+(?:upfront|in advance|processing|verification))?\b",
        "penegasan bahawa bayaran awal tidak diperlukan",
    ),
    (
        r"\b(?:do not|don't|never)\s+(?:click|tap|open)\s+(?:any\s+|the\s+|this\s+)?(?:link|url)\b",
        "peringatan supaya tidak menekan pautan",
    ),
]


SCAMMOVE_PATTERNS = [
    {
        "code": "M1",
        "name": "Bina Kepercayaan",
        "function": "Mewujudkan kredibiliti awal melalui autoriti, bukti sosial atau imej institusi.",
        "patterns": [r"\bbank\b", r"\bpegawai\b", r"\bofficer\b", r"\bauthority\b", r"\bwakil\b", r"\brepresentative\b", r"syarikat berdaftar", r"registered company", r"\blesen\b", r"\blicen[cs]ed\b", r"\bsuruhanjaya\b", r"\bcommission\b", r"\btestimoni(?:al)?\b", r"ramai pelanggan", r"many customers"],
        "weight": 16,
    },
    {
        "code": "M2",
        "name": "Tawar Peluang",
        "function": "Menarik minat melalui bantuan, pinjaman, kerja, hadiah atau pelaburan khas.",
        "patterns": [r"\bterpilih\b", r"\bselected\b", r"\blayak\b", r"\beligible\b", r"\bpeluang\b", r"\bopportunity\b", r"\bbantuan\b", r"\baid\b", r"\bpinjaman\b", r"\bloan\b", r"\bpelaburan\b", r"\binvestment\b", r"program khas", r"special (?:program|programme)", r"\bhadiah\b", r"\bprize\b"],
        "weight": 16,
    },
    {
        "code": "M3",
        "name": "Janji Ganjaran",
        "function": "Membina harapan melalui janji pulangan, bonus, keuntungan atau pelepasan wang.",
        "patterns": [r"\bpulangan\b", r"\breturns?\b", r"\buntung\b", r"\bprofits?\b", r"\bbonus\b", r"modal[^.!?;:]{0,20}jadi", r"\bdijamin\b", r"\bguaranteed\b", r"tanpa risiko", r"no risk", r"wang[^.!?;:]{0,25}dilepaskan", r"(?:money|funds)[^.!?;:]{0,30}(?:released|unlocked)", r"\bkeuntungan\b", r"\bearnings?\b"],
        "weight": 20,
    },
    {
        "code": "M4",
        "name": "Tekanan Masa",
        "function": "Mendesak pengguna bertindak cepat tanpa semakan lanjut.",
        "patterns": [r"\bsegera\b", r"\burgent(?:ly)?\b", r"\bsekarang\b", r"\bnow\b", r"\bimmediately\b", r"\bhari ini\b", r"\btoday\b", r"slot terhad", r"limited slots", r"tinggal \d+", r"only \d+ left", r"sebelum (?:jam|pukul)", r"\bbefore (?:\d+|noon|midnight)\b", r"\b24 (?:jam|hours)\b", r"\b15 (?:minit|minutes)\b", r"\b30 (?:minit|minutes)\b"],
        "weight": 18,
    },
    {
        "code": "M5",
        "name": "Arahan Bayaran/Data",
        "function": "Menggerakkan pengguna untuk membayar, menekan pautan atau menyerahkan data sensitif.",
        "patterns": [r"\bbayar\b", r"\bpay\b", r"buat bayaran", r"make (?:a )?payment", r"bayaran deposit", r"deposit payment", r"bayaran pengesahan", r"verification (?:payment|fee)", r"caj proses", r"processing fee", r"caj pengesahan", r"verification fee", r"\bdeposit\b", r"\btransfer\b", r"\bpindahan\b", r"\b(?:otp|tac|pin)\b", r"one[ -]time password", r"kata laluan", r"\bpassword\b", r"kad pengenalan", r"identity card", r"nombor akaun", r"account number", r"maklumat bank", r"bank details", r"klik pautan", r"tekan pautan", r"click (?:the |this )?link", r"\bsemak sekarang\b", r"\bcheck now\b", r"\bisi (?:nombor|maklumat|borang)\b", r"\bcode verification\b", r"aktifkan pengeluaran", r"activate (?:the )?withdrawal"],
        "weight": 26,
    },
    {
        "code": "M6",
        "name": "Penguncian Mangsa",
        "function": "Menghalang pengguna berundur melalui ancaman, kerahsiaan atau risiko kehilangan peluang.",
        "patterns": [r"jangan batalkan", r"do not cancel|don't cancel", r"jangan beritahu", r"do not tell|don't tell", r"\brahsia\b", r"\bsecret\b", r"\bsulit\b", r"\bconfidential\b", r"(?:akaun|account)[^.!?;:]{0,35}(?:dibekukan|disekat|frozen|blocked|suspended)", r"disenarai hitam", r"blacklisted", r"tindakan undang-undang", r"legal action", r"terlepas peluang", r"miss (?:the |this )?opportunity", r"keluarkan duit", r"withdraw (?:your )?(?:money|funds)", r"\bpengeluaran\b", r"\bwithdrawal\b"],
        "weight": 24,
    },
]


SCAMMOVE_CONTROL_PATTERNS: Dict[str, str] = {
    r"\b(?:saluran|laman|aplikasi|portal|kaunter) rasmi\b|\bofficial (?:channel|website|app|application|portal|counter)\b": "Kawalan: semakan melalui saluran rasmi",
    r"\b(?:jangan|tidak|tak)[^.!?;:]{0,50}(?:otp|tac|pin|kata laluan|password|maklumat bank|kad pengenalan|nombor akaun)\b|\b(?:do not|don't|never|will never)[^.!?;:]{0,50}(?:otp|one[ -]time password|pin|password|bank details|identity card|account number)\b": "Kawalan: peringatan keselamatan data",
    r"\b(?:terma dan syarat|invois rasmi|invois syarikat berdaftar|resit rasmi|emel rasmi|terms and conditions|official invoice|official receipt|official email|registered company invoice|company invoice)\b": "Kawalan: bukti transaksi sah",
    r"\b(?:tidak perlu|tiada|tanpa)[^.!?;:]{0,25}(?:bayaran|caj|deposit|yuran)\b|\b(?:no|without|do not need|don't need)[^.!?;:]{0,25}(?:payment|fee|deposit|charge)\b": "Kawalan: tiada desakan bayaran awal",
}


SCAMMOVE_SCAM_EXAMPLES = [
    "Bina Kepercayaan → Tawar Peluang → Janji Ganjaran → Tekanan Masa → Arahan Bayaran",
    "Penyamaran Autoriti → Ancaman Akaun → Tekanan Masa → Permintaan OTP",
    "Tawar Bantuan → Kelulusan Palsu → Caj Proses → Penguncian Mangsa",
]

SCAMMOVE_CONTROL_EXAMPLES = [
    "Maklumat Rasmi → Terma dan Syarat → Saluran Semakan",
    "Peringatan Keselamatan → Jangan Kongsi OTP → Hubungi Saluran Rasmi",
    "Invois Rasmi → Akaun Syarikat Berdaftar → Resit Melalui Emel Rasmi",
]


def unique(items: Iterable[str]) -> List[str]:
    return list(dict.fromkeys(item for item in items if item))


def risk_level(score: int) -> str:
    if score <= 24:
        return "Rendah"
    if score <= 49:
        return "Sederhana"
    if score <= 74:
        return "Tinggi"
    return "Sangat Tinggi"


def find_matches(text: str, pattern_dict: Dict[str, object]) -> Tuple[int, List[str]]:
    labels: List[str] = []
    score = 0
    for pattern, payload in pattern_dict.items():
        if not re.search(pattern, text, flags=re.I):
            continue
        if isinstance(payload, tuple):
            weight, label = payload
            score += int(weight)
            labels.append(str(label))
        else:
            labels.append(str(payload))
    return score, unique(labels)


def mask_preventive_phrases(text: str) -> Tuple[str, List[str]]:
    masked = text
    labels: List[str] = []
    for pattern, label in PREVENTIVE_PATTERNS:
        if re.search(pattern, masked, flags=re.I):
            labels.append(label)
            masked = re.sub(pattern, " __peringatan_keselamatan__ ", masked, flags=re.I)
    return masked, unique(labels)


def analyse_emotions(text: str) -> Tuple[int, List[str]]:
    emotions: List[str] = []
    score = 0
    for emotion, patterns in EMOTION_PATTERNS.items():
        if any(re.search(pattern, text, flags=re.I) for pattern in patterns):
            emotions.append(emotion)
            score += 18
    if "E1 Ketakutan" in emotions and "E2 Kecemasan" in emotions:
        score += 12
    if "E3 Harapan Keuntungan" in emotions and "E4 Pembinaan Kepercayaan" in emotions:
        score += 8
    return min(score, 100), emotions


def analyse_moves(text: str, control_text: str = "") -> Tuple[int, List[dict], List[str]]:
    detected: List[dict] = []
    move_score = 0
    for move in SCAMMOVE_PATTERNS:
        if any(re.search(pattern, text, flags=re.I) for pattern in move["patterns"]):
            detected.append(move)
            move_score += int(move["weight"])

    control_source = control_text or text
    control_score, control_labels = find_matches(
        control_source,
        {pattern: (10, label) for pattern, label in SCAMMOVE_CONTROL_PATTERNS.items()},
    )
    move_codes = [move["code"] for move in detected]
    if len(detected) >= 4:
        move_score += 16
    if "M4" in move_codes and "M5" in move_codes:
        move_score += 18
    if all(code in move_codes for code in ["M1", "M3", "M4", "M5"]):
        move_score += 18
    if "M5" in move_codes and "M6" in move_codes:
        move_score += 12

    move_score = max(0, min(100, move_score - control_score))
    if move_score < 25 and control_labels:
        detected = []
    return move_score, detected, control_labels


def match_phrase(score: int, has_control: bool) -> str:
    if score >= 75:
        return "Ciri risiko bahasa sangat kuat"
    if score >= 50:
        return "Ciri risiko bahasa kuat"
    if score >= 25:
        return "Beberapa petanda memerlukan semakan"
    if has_control:
        return "Petanda keselamatan atau konteks rasmi dikesan"
    return "Tiada petanda risiko yang kuat dikesan"


def classify_threat(text: str, score: int) -> str:
    if score < 25:
        return "Tiada kategori ancaman yang jelas"
    if re.search(r"\b(?:parcel|bungkusan|kurier|courier|delivery|penghantaran|pos malaysia|j&t|dhl|fedex|kastam|customs)\b", text, flags=re.I):
        return "Risiko penghantaran atau bungkusan palsu"
    if re.search(r"\b(?:refund|bayaran balik|pemulangan wang|rebat|lebihan bayaran|tax refund|pulangan cukai)\b", text, flags=re.I):
        return "Risiko bayaran balik atau tuntutan palsu"
    if re.search(r"\b(?:e-?wallet|dompet digital|touch\s*['n’]?\s*go|tng|boost|shopeepay|grabpay|bigpay|mae)\b", text, flags=re.I):
        return "Risiko e-dompet atau pengambilalihan akaun"
    if re.search(r"\b(?:ini nombor baru|save nombor (?:baru|ini)|telefon (?:saya )?(?:rosak|hilang)|new (?:phone|number))\b", text, flags=re.I):
        return "Risiko penyamaran ahli keluarga atau kenalan"
    if re.search(r"\b(?:sayang|darling|honey|love you|kekasih|tunang|fianc[eé]|pasangan)\b", text, flags=re.I):
        return "Risiko percintaan atau kecemasan palsu"
    if re.search(r"\b(?:anydesk|teamviewer|quicksupport|remote access|kongsi skrin)\b", text, flags=re.I):
        return "Risiko akses jauh kepada peranti"
    if re.search(r"(?:https?://|www\.|\b[a-z0-9][a-z0-9-]{2,}\.(?:com|net|my|xyz|top|site|online|live|link))", text, flags=re.I) and re.search(r"\b(?:klik|tekan|buka|layari|log masuk|login|sign in|verify|sahkan)\b", text, flags=re.I):
        return "Risiko pautan palsu atau pancingan data"
    if re.search(r"(?:bayar|pay)[^.!?;:]{0,45}(?:keluar|pengeluaran|withdraw|release)|caj pengeluaran|bayaran pengeluaran|withdrawal fee|release fee|aktifkan pengeluaran|activate (?:the )?withdrawal", text, flags=re.I):
        return "Risiko bayaran sebelum pengeluaran wang"
    if re.search(r"\b(?:bayar|pay|payment|deposit|transfer|pindahkan|pindahan)\b|caj proses|caj pengesahan|yuran pendaftaran|processing fee|verification fee|registration fee", text, flags=re.I):
        return "Risiko bayaran pendahuluan / transaksi mencurigakan"
    if re.search(r"\b(?:otp|tac|pin)\b|one[ -]time password|kata laluan|password|maklumat bank|bank details|kad pengenalan|identity card|nombor akaun|account number|(?:akaun|account)[^.!?;:]{0,35}(?:dibekukan|disekat|frozen|blocked|suspended)", text, flags=re.I):
        return "Risiko penyamaran autoriti / pengambilalihan akaun"
    if re.search(r"\b(?:pelaburan|investment|pulangan|returns?|untung|profits?|keuntungan|earnings?)\b|modal[^.!?;:]{0,20}jadi", text, flags=re.I):
        return "Risiko pelaburan / pulangan palsu"
    if re.search(r"\b(?:pinjaman|loan|bantuan|aid|dana|fund|caj proses|caj pengesahan|processing fee|verification fee)\b|(?:permohonan|application)[^.!?;:]{0,30}(?:diluluskan|approved)", text, flags=re.I):
        return "Risiko pinjaman atau bantuan palsu"
    if re.search(r"\b(?:kerja|job|jawatan|position|gaji|salary|komisen|commission|tugasan|task)\b", text, flags=re.I):
        return "Risiko kerja / komisen palsu"
    if score >= 60:
        return "Mesej berisiko tinggi dengan unsur manipulasi"
    return "Tiada kategori ancaman yang jelas"


def control_message(category: str) -> str:
    lower = category.lower()
    if "pelaburan" in lower:
        return "Mesej pelaburan yang sah menerangkan risiko, dokumen dan saluran semakan tanpa menjanjikan keuntungan segera."
    if "pengeluaran" in lower:
        return "Pihak sah tidak meminta bayaran tambahan semata-mata untuk melepaskan pengeluaran wang."
    if "pinjaman" in lower or "bantuan" in lower:
        return "Bantuan atau pinjaman sah tidak mendesak caj proses sebelum wang dilepaskan dan menyediakan portal semakan rasmi."
    if "akaun" in lower or "autoriti" in lower:
        return "Pihak sah tidak meminta OTP, kata laluan atau PIN melalui mesej dan memberi saluran pengesahan rasmi."
    return "Mesej sah memberi ruang untuk semakan, menerangkan terma dan tidak memaksa bayaran atau tindakan segera."


def load_reference_bundle(path: Path | str = DATA_PATH) -> dict:
    data_path = Path(path)
    with data_path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)

    statistics = payload.get("statistics") or {}
    templates = payload.get("templates") or []
    if statistics.get("normalized_templates") != len(templates):
        raise ValueError("Reference template count does not match metadata")
    if not templates:
        raise ValueError("Reference data contains no templates")

    records = [
        ReferenceRecord(
            record_id=row["template_id"],
            text=row["representative_text"],
            label=row["binary_label"],
            module=" + ".join(row.get("modules") or []),
            category="; ".join(row.get("expected_categories") or []),
            template_group=row["template_id"],
            source_count=int(row.get("source_occurrences") or 1),
        )
        for row in templates
    ]
    # An exact/near-exact, non-ambiguous reference may contribute at most 55%
    # of the hybrid index.  Weaker matches receive proportionally less weight;
    # insufficient or ambiguous matches receive zero weight.
    engine = ReferenceSimilarityEngine(records, max_hybrid_weight=0.55)
    return {
        "engine": engine,
        "statistics": statistics,
        "schema_version": payload.get("schema_version", "unknown"),
        "source_status": payload.get("source_status", "unknown"),
        "methodology_note": payload.get("methodology_note", ""),
        "path": str(data_path),
    }


try:
    REFERENCE_BUNDLE: Optional[dict] = load_reference_bundle()
    REFERENCE_ERROR: Optional[str] = None
except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError) as exc:
    REFERENCE_BUNDLE = None
    REFERENCE_ERROR = f"{type(exc).__name__}: {exc}"


def get_reference_status() -> dict:
    if REFERENCE_BUNDLE is None:
        return {"loaded": False, "error": REFERENCE_ERROR, "statistics": {}}
    return {
        "loaded": True,
        "error": None,
        "statistics": REFERENCE_BUNDLE["statistics"],
        "schema_version": REFERENCE_BUNDLE["schema_version"],
        "source_status": REFERENCE_BUNDLE["source_status"],
        "methodology_note": REFERENCE_BUNDLE["methodology_note"],
    }


def analyse_rules(message: str) -> dict:
    original_text = message.strip().lower()
    risk_text, preventive_labels = mask_preventive_phrases(original_text)
    direct_score, direct_labels = find_matches(risk_text, DIRECT_PATTERNS)
    indirect_score, indirect_labels = find_matches(risk_text, INDIRECT_PATTERNS)
    control_score, control_labels = find_matches(
        original_text,
        {pattern: (8, label) for pattern, label in CONTROL_PATTERNS.items()},
    )
    emotion_score, emotions = analyse_emotions(risk_text)
    move_score, moves, move_control_labels = analyse_moves(risk_text, original_text)
    scenario = analyse_scenarios(risk_text)

    speech_score = max(0, min(100, direct_score + indirect_score - control_score))
    overall_score = int(min(100, round(speech_score * 0.35 + emotion_score * 0.30 + move_score * 0.35)))

    has_otp = bool(re.search(r"\b(?:otp|tac|pin)\b|one[ -]time password|kata laluan|password", risk_text, flags=re.I))
    has_sensitive_request = bool(re.search(r"(?:hantar|berikan|beri|masukkan|kongsi|dedahkan|send|provide|enter|share|reveal)[^.!?;:]{0,40}(?:maklumat bank|butiran bank|kad pengenalan|nombor akaun|maklumat peribadi|bank details|identity card|account number|personal information)", risk_text, flags=re.I))
    has_account_threat = bool(re.search(r"(?:akaun|account)[^.!?;:]{0,35}(?:dibekukan|disekat|ditutup|frozen|blocked|suspended|closed)", risk_text, flags=re.I))
    has_time_pressure = bool(re.search(r"\b(?:segera|sekarang|urgent|urgently|now|immediately|24 (?:jam|hours)|15 (?:minit|minutes)|30 (?:minit|minutes)|5 (?:minit|minutes)|hari ini|today)\b|jika gagal|kalau gagal|if (?:you )?(?:fail|do not|don't)|sebelum (?:pukul|jam)|within \d+ (?:minutes?|hours?)|before (?:noon|midnight|\d+)", risk_text, flags=re.I))
    has_money_request = bool(re.search(r"\b(?:bayar|pay|payment|deposit|transfer|pindahkan|pindahan)\b|make (?:a )?payment|caj proses|caj pengesahan|yuran pendaftaran|processing fee|verification fee|registration fee|withdrawal fee", risk_text, flags=re.I))
    has_unrealistic_gain = bool(re.search(r"modal[^.!?;:]{0,20}jadi|\b(?:untung|profit|pulangan tinggi|high returns?|dijamin|guaranteed|bonus|hadiah|prize)\b|(?:wang|money|funds)[^.!?;:]{0,30}(?:dilepaskan|released|unlocked)", risk_text, flags=re.I))
    has_benefit_release = bool(re.search(r"(?:wang|money|funds)[^.!?;:]{0,35}(?:dilepaskan|released|unlocked)|(?:permohonan|application)[^.!?;:]{0,30}(?:diluluskan|approved)|\b(?:pinjaman|loan|bantuan|aid|dana|funds?)\b", risk_text, flags=re.I))
    has_withdrawal_release = bool(re.search(r"keluarkan duit|\bpengeluaran\b|\bwithdraw(?:al)?\b|release (?:your )?(?:money|funds)|aktifkan pengeluaran|activate (?:the )?withdrawal|caj pengeluaran|bayaran pengeluaran|withdrawal fee|release fee", risk_text, flags=re.I))
    has_job_offer = bool(re.search(r"\b(?:kerja|job|jawatan|position|komisen|commission|tugasan|task)\b|like dan follow|tekan like|like and follow|click like", risk_text, flags=re.I))
    has_promised_earnings = bool(re.search(r"bayaran harian|gaji harian|komisen harian|daily (?:payment|salary|commission|earnings)|rm\s*\d+[^.!?;:]{0,20}(?:sehari|harian|per day|daily)", risk_text, flags=re.I))
    has_prior_payment = bool(
        re.search(
            r"\b(?:sudah|telah|dah|already|previously)\b[^.!?]{0,55}\b(?:bayar|paid|sent|transfer(?:red)?|pindahkan)\b|\b(?:saya|kami|i|we)\b[^.!?]{0,35}\b(?:bayar|paid|sent|transfer(?:red)?|pindahkan)\b[^.!?]{0,35}\b(?:semalam|yesterday|earlier|before|twice|dua kali)\b",
            risk_text,
            flags=re.I,
        )
    )
    has_followup_payment_demand = bool(
        re.search(
            r"\b(?:mereka|dia|admin|ejen|agen|penjual|pihak itu|they|he|she|agent|seller|the person)\b[^.!?]{0,65}\b(?:minta|meminta|desak|mendesak|mahu|nak|ask(?:ing|ed)?|demand(?:ing|ed)?|request(?:ing|ed)?|want(?:s|ed|ing)?|keeps? requesting)\b[^.!?]{0,55}\b(?:bayar|payment|pay|caj|fee|charge|deposit|wang|duit|money|funds)\b|\b(?:masih|lagi|again|still|now)\b[^.!?]{0,30}\b(?:diminta|disuruh|asked|told)\b[^.!?]{0,35}\b(?:bayar|pay|payment|caj|fee|deposit|wang|duit|money)\b",
            risk_text,
            flags=re.I,
        )
    )
    has_repeat_payment = has_prior_payment and has_followup_payment_demand
    has_safety_bait_payment = bool(
        re.search(
            r"__peringatan_keselamatan__[^.!?]{0,75}(?:\b(?:tetapi|namun|but|however|cuma|only)\b|[,;])[^.!?]{0,90}\b(?:bayar|pay|payment|deposit|transfer|pindahan|caj|fee)\b",
            risk_text,
            flags=re.I,
        )
    )

    critical_risk = False
    critical_floor = 0
    if has_otp and has_account_threat and has_time_pressure:
        speech_score, emotion_score, move_score, overall_score = (
            max(speech_score, 90), max(emotion_score, 82), max(move_score, 90), max(overall_score, 94)
        )
        critical_risk = True
        critical_floor = 90
    elif has_otp and has_time_pressure:
        speech_score, move_score, overall_score = max(speech_score, 84), max(move_score, 84), max(overall_score, 86)
        critical_risk = True
        critical_floor = 82
    elif has_sensitive_request and has_time_pressure:
        speech_score, move_score, overall_score = max(speech_score, 82), max(move_score, 82), max(overall_score, 84)
        critical_risk = True
        critical_floor = 80
    elif has_money_request and has_time_pressure and has_unrealistic_gain:
        speech_score, emotion_score, move_score, overall_score = (
            max(speech_score, 76), max(emotion_score, 70), max(move_score, 86), max(overall_score, 84)
        )
        critical_risk = True
        critical_floor = 80
    elif has_money_request and has_account_threat:
        speech_score, move_score, overall_score = max(speech_score, 78), max(move_score, 84), max(overall_score, 84)
        critical_risk = True
        critical_floor = 80
    elif has_money_request and has_withdrawal_release:
        speech_score, emotion_score, move_score, overall_score = (
            max(speech_score, 78), max(emotion_score, 45), max(move_score, 84), max(overall_score, 82)
        )
        critical_risk = True
        critical_floor = 78
    elif has_money_request and has_benefit_release:
        speech_score, move_score, overall_score = max(speech_score, 74), max(move_score, 76), max(overall_score, 76)
        critical_risk = True
        critical_floor = 72
    elif has_safety_bait_payment and has_money_request and has_time_pressure:
        speech_score, move_score, overall_score = max(speech_score, 68), max(move_score, 74), max(overall_score, 72)
        critical_risk = True
        critical_floor = 68
    elif has_repeat_payment:
        speech_score, move_score, overall_score = max(speech_score, 70), max(move_score, 74), max(overall_score, 72)
        critical_risk = True
        critical_floor = 68
    elif has_job_offer and has_money_request and (has_time_pressure or has_promised_earnings):
        speech_score, move_score, overall_score = max(speech_score, 70), max(move_score, 74), max(overall_score, 72)
        critical_risk = True
        critical_floor = 68

    # Named scenarios provide a conservative minimum only when several cues
    # co-occur.  This catches paraphrases outside the small reference corpus
    # without treating a lone word such as "parcel" or "bank" as proof.
    scenario_floor = int(scenario["floor"])
    if scenario_floor:
        overall_score = max(overall_score, scenario_floor)
        move_score = max(move_score, min(86, scenario_floor))
        if scenario_floor >= 68:
            critical_risk = True
            critical_floor = max(critical_floor, scenario_floor)

    if direct_labels and indirect_labels:
        speech_type = "Gabungan lakuan pertuturan langsung dan tidak langsung"
    elif direct_labels:
        speech_type = "Lakuan pertuturan langsung"
    elif indirect_labels:
        speech_type = "Lakuan pertuturan tidak langsung"
    else:
        speech_type = "Tiada pola lakuan yang ketara"

    result = {
        "rule_score": int(overall_score),
        "overall_score": int(overall_score),
        "overall_level": risk_level(int(overall_score)),
        "speech_score": int(speech_score),
        "speech_level": risk_level(int(speech_score)),
        "speech_type": speech_type,
        "speech_match": match_phrase(int(speech_score), bool(control_labels)),
        "emotion_score": int(emotion_score),
        "emotion_level": risk_level(int(emotion_score)),
        "emotion_match": match_phrase(int(emotion_score), bool(control_labels)),
        "move_score": int(move_score),
        "move_level": risk_level(int(move_score)),
        "move_match": match_phrase(int(move_score), bool(move_control_labels)),
        "emotions": emotions,
        "moves": moves,
        "direct_phrases": direct_labels,
        "indirect_phrases": indirect_labels,
        "emotion_phrases": emotions,
        "control_phrases": unique(control_labels + move_control_labels + preventive_labels),
        "risk_reasons": unique(
            scenario["reasons"]
            + direct_labels
            + indirect_labels
            + [move["name"] for move in moves]
        ),
        "scenario_flags": scenario["flags"],
        "scenario_category": scenario["category"],
        "critical_risk": critical_risk,
        "critical_floor": critical_floor,
        "risk_text": risk_text,
    }
    result["threat_category"] = scenario["category"] or classify_threat(
        risk_text, result["rule_score"]
    )
    result["control_message"] = control_message(result["threat_category"])
    return result


def _reference_message(data_result: object) -> str:
    reliability = getattr(data_result, "reliability", "insufficient")
    if reliability == "strong":
        return "Padanan rujukan kuat dan digunakan dalam indeks hibrid"
    if reliability == "moderate":
        return "Padanan rujukan sederhana dan digunakan dengan berat terhad"
    if reliability == "ambiguous":
        return "Padanan risiko dan kawalan bercanggah; isyarat data diketepikan"
    return "Tiada padanan rujukan mencukupi; isyarat data diketepikan"


def analyse_text(message: str, bundle: Optional[dict] = REFERENCE_BUNDLE) -> dict:
    result = analyse_rules(message)
    rule_score = result["rule_score"]

    if bundle is None:
        result.update(
            {
                "data_loaded": False,
                "data_error": REFERENCE_ERROR,
                "data_index": 50.0,
                "data_weight": 0.0,
                "data_reliability": "unavailable",
                "data_message": "Data rujukan tidak dimuatkan; indeks menggunakan peraturan linguistik sahaja",
                "best_similarity": 0.0,
                "risk_matches": [],
                "control_matches": [],
            }
        )
        hybrid_score = rule_score
    else:
        data_result = bundle["engine"].query(message, top_k=3)
        weight = float(data_result.recommended_hybrid_weight)
        hybrid_score = int(round((1.0 - weight) * rule_score + weight * data_result.data_index))

        # With a small controlled reference set, a merely moderate lexical
        # resemblance (for example, an ordinary request to transfer lunch
        # money) must not by itself cross the high-risk boundary. Exact/strong
        # references and critical multi-signal rules remain able to do so.
        if (
            not result["critical_risk"]
            and rule_score < 50
            and data_result.reliability != "strong"
        ):
            hybrid_score = min(hybrid_score, 49)

        # A dangerous multi-signal combination must not be neutralised by a
        # superficially similar safety sentence in the small reference corpus.
        if result["critical_risk"]:
            hybrid_score = max(hybrid_score, result["critical_floor"])

        result.update(
            {
                "data_loaded": True,
                "data_error": None,
                "data_index": round(float(data_result.data_index), 1),
                "data_weight": round(weight, 3),
                "data_reliability": data_result.reliability,
                "data_message": _reference_message(data_result),
                "best_similarity": round(float(data_result.best_similarity), 4),
                "risk_signal": round(float(data_result.risk_signal), 4),
                "control_signal": round(float(data_result.control_signal), 4),
                "risk_matches": [match.as_dict() for match in data_result.risk_matches],
                "control_matches": [match.as_dict() for match in data_result.control_matches],
            }
        )

        if (
            result["threat_category"] == "Tiada kategori ancaman yang jelas"
            and data_result.usable_for_hybrid
            and data_result.data_index > 60
            and data_result.risk_matches
        ):
            category = data_result.risk_matches[0].category.split(";")[0].strip()
            if category:
                result["threat_category"] = f"Serupa dengan rujukan risiko: {category}"

    result["overall_score"] = max(0, min(100, int(hybrid_score)))
    result["overall_level"] = risk_level(result["overall_score"])
    result["overall_match"] = result["data_message"]
    result["control_message"] = control_message(result["threat_category"])

    control_evidence = bool(result.get("control_phrases")) or (
        result.get("data_reliability") in {"moderate", "strong"}
        and float(result.get("control_signal", 0.0))
        > float(result.get("risk_signal", 0.0)) + 0.04
    )
    score = result["overall_score"]
    if score <= 24 and not control_evidence:
        result["display_level"] = "Bukti Tidak Mencukupi"
        result["decision_state"] = "insufficient"
        result["decision_summary"] = (
            "Mesej ini terlalu umum atau terlalu ringkas untuk diberikan label rendah dengan yakin."
        )
        result["risk_reasons"] = ["Konteks atau petanda linguistik belum mencukupi"]
    elif score <= 24:
        result["display_level"] = "Rendah"
        result["decision_state"] = "low"
        result["decision_summary"] = "Tiada petanda risiko ketara dalam konteks yang dianalisis."
        result["risk_reasons"] = ["Isyarat keselamatan atau saluran rasmi dikesan"]
    elif score <= 49:
        result["display_level"] = "Perlu Berhati-hati"
        result["decision_state"] = "caution"
        result["decision_summary"] = "Beberapa petanda memerlukan pengesahan lanjut."
    elif score <= 74:
        result["display_level"] = "Tinggi"
        result["decision_state"] = "high"
        result["decision_summary"] = "Beberapa petanda penipuan yang kuat telah dikesan."
    else:
        result["display_level"] = "Sangat Tinggi"
        result["decision_state"] = "very_high"
        result["decision_summary"] = "Gabungan petanda penipuan yang sangat kuat telah dikesan."

    result["recommended_action"] = {
        "insufficient": "Dapatkan konteks penuh dan sahkan pengirim melalui saluran rasmi sebelum bertindak.",
        "low": "Terus berwaspada jika mesej kemudian meminta wang, pautan atau maklumat peribadi.",
        "caution": "Jangan klik pautan, membuat bayaran atau berkongsi maklumat sebelum pengesahan bebas.",
        "high": "Hentikan tindakan dan hubungi organisasi berkaitan melalui nombor atau aplikasi rasmi.",
        "very_high": "Jangan klik, bayar atau berkongsi OTP. Putuskan komunikasi dan buat pengesahan rasmi.",
    }[result["decision_state"]]
    return result
