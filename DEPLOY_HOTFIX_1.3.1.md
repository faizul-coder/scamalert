# Pasang hotfix ScamAlert 1.3.1

Hotfix ini mesti memasang **dua fail serentak**:

- `app.py`
- `scamalert_core.py`

Jangan gantikan `app.py` sahaja. `app.py` baharu akan menyekat analisis jika
`scamalert_core.py` lama masih berada pada pelayan supaya skor salah tidak
dipaparkan secara senyap.

## Langkah GitHub

1. Nyahzip `ScamAlert_Hotfix_1.3.1_UPLOAD_DUA_FAIL.zip`.
2. Buka repositori `faizul-coder/scamalert` pada cabang `main`.
3. Tekan **Add file** → **Upload files**.
4. Seret **kedua-dua** fail `app.py` dan `scamalert_core.py` ke akar repositori.
5. Pastikan GitHub menunjukkan kedua-dua fail akan digantikan, bukan dimasukkan
   ke dalam folder baharu.
6. Masukkan mesej komit `Hotfix ScamAlert 1.3.1` dan tekan **Commit changes**.
7. Tunggu Streamlit selesai memasang semula aplikasi, kemudian lakukan muat
   semula keras pada halaman aplikasi (`Cmd+Shift+R` pada Mac).
8. Muat naik semula gambar dan tekan **Semak Mesej**.

## Keputusan semakan rujukan

Imej `IMG_4710.jpg` telah diuji terus melalui OCR dan enjin dalam pakej ini.
Keputusan yang dijangka ialah:

- skor risiko: `84/100`;
- tahap: `Sangat Tinggi`;
- jenis: `Risiko bantuan tunai palsu atau pancingan data`;
- frasa tersurat: `arahan menyemak segera`;
- frasa tersirat: `desakan masa`;
- pencetus emosi: `E2 Kecemasan`;
- gerakan: `Tawar Peluang → Tekanan Masa → Arahan Bayaran/Data`.

Jika pelayan masih mempunyai enjin lama, aplikasi akan memaparkan amaran
kemas kini tidak lengkap dan tidak akan menghasilkan skor yang mengelirukan.
