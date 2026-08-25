"""Create synthetic, non-sensitive screenshots for the NICE live demo."""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "demo_assets"


def font(size, bold=False):
    filename = "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"
    path = Path("/usr/share/fonts/truetype/dejavu") / filename
    return ImageFont.truetype(str(path), size) if path.exists() else ImageFont.load_default()


def dark_risk():
    image = Image.new("RGB", (1080, 1400), (12, 25, 35))
    draw = ImageDraw.Draw(image)
    draw.rectangle((0, 0, 1080, 110), fill=(20, 45, 55))
    draw.text((45, 32), "ScamAlert · tangkapan layar simulasi", fill="white", font=font(30, True))
    draw.rounded_rectangle((65, 155, 970, 465), radius=28, fill=(0, 92, 75))
    draw.multiline_text(
        (105, 205),
        "Permohonan pinjaman anda diluluskan.\nBayar caj proses RM300 sekarang.",
        fill="white",
        font=font(34),
        spacing=24,
    )
    draw.text((760, 410), "10:24 PM", fill=(195, 230, 220), font=font(23))
    draw.rounded_rectangle((150, 540, 1015, 850), radius=28, fill=(0, 92, 75))
    draw.multiline_text(
        (190, 590),
        "Wang RM5,000 akan dilepaskan\nhari ini selepas bayaran.",
        fill="white",
        font=font(34),
        spacing=24,
    )
    draw.text((810, 795), "10:25 PM", fill=(195, 230, 220), font=font(23))
    draw.text((65, 1260), "DATA SIMULASI · BUKAN MESEJ SEBENAR", fill=(185, 200, 205), font=font(25, True))
    image.save(OUTPUT / "01_risk_dark_chat.png", format="PNG", optimize=True)


def light_safety():
    image = Image.new("RGB", (1080, 1200), (240, 244, 247))
    draw = ImageDraw.Draw(image)
    draw.rectangle((0, 0, 1080, 110), fill=(25, 70, 105))
    draw.text((45, 32), "ScamAlert · tangkapan layar simulasi", fill="white", font=font(30, True))
    draw.rounded_rectangle((65, 160, 1015, 600), radius=28, fill="white", outline=(205, 214, 220), width=3)
    draw.multiline_text(
        (110, 220),
        "Pihak bank tidak pernah meminta OTP.\n"
        "Jangan kongsi OTP atau PIN dengan sesiapa.\n"
        "Semak melalui aplikasi rasmi.",
        fill=(18, 30, 40),
        font=font(34),
        spacing=28,
    )
    draw.text((65, 1070), "DATA SIMULASI · BUKAN MESEJ SEBENAR", fill=(80, 95, 105), font=font(25, True))
    image.save(OUTPUT / "02_safety_light.png", format="PNG", optimize=True)


if __name__ == "__main__":
    OUTPUT.mkdir(parents=True, exist_ok=True)
    dark_risk()
    light_safety()
    print(f"Created demo screenshots in {OUTPUT}")
