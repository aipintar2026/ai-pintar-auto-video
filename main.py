
import asyncio
import os
import subprocess
from datetime import date
from pathlib import Path

import edge_tts
from PIL import Image, ImageDraw, ImageFont

WIDTH, HEIGHT = 1080, 1920

TOPICS = [
    {
        "title": "JANGAN BAGIKAN DATA PRIBADI KE AI",
        "lines": [
            "Jangan masukkan nomor KTP atau PIN.",
            "Jangan bagikan kata sandi dan data rekening.",
            "Periksa kebijakan privasi layanan AI.",
            "Samarkan informasi sensitif sebelum digunakan."
        ],
        "voice": (
            "Hati-hati menggunakan kecerdasan buatan. "
            "Jangan masukkan nomor KTP, PIN, kata sandi, "
            "atau data rekening ke chatbot. Periksa kebijakan "
            "privasi dan samarkan informasi sensitif. "
            "Gunakan AI dengan cerdas dan aman."
        )
    },
    {
        "title": "AI BISA MEMBANTU PEKERJAAN",
        "lines": [
            "Membantu mencari ide.",
            "Menyusun tulisan dan laporan.",
            "Merangkum informasi.",
            "Periksa hasilnya sebelum digunakan."
        ],
        "voice": (
            "Tahukah kamu? AI bisa membantu pekerjaan sehari-hari. "
            "AI dapat mencari ide, menyusun tulisan, dan merangkum "
            "informasi. Namun, periksa kembali hasilnya sebelum digunakan."
        )
    },
    {
        "title": "BELAJAR AI DARI DASAR",
        "lines": [
            "Mulai dengan pertanyaan sederhana.",
            "Jelaskan tujuan yang kamu inginkan.",
            "Berikan konteks yang cukup.",
            "Periksa jawaban AI."
        ],
        "voice": (
            "Ingin belajar menggunakan AI? Mulailah dengan "
            "pertanyaan sederhana. Jelaskan tujuanmu, berikan "
            "konteks yang cukup, lalu periksa jawaban AI."
        )
    }
]


def get_font(size):
    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf"
    ]
    for path in candidates:
        if os.path.exists(path):
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def make_scene(title, text, index, total):
    img = Image.new("RGB", (WIDTH, HEIGHT), (8, 18, 42))
    draw = ImageDraw.Draw(img)

    draw.ellipse((650, 150, 1250, 750), fill=(13, 58, 112))
    draw.ellipse((-250, 1150, 450, 1850), fill=(12, 42, 90))

    draw.rounded_rectangle(
        (65, 100, 1015, 1820),
        radius=55,
        outline=(35, 145, 255),
        width=8
    )

    draw.text((100, 155), "AI PINTAR",
              font=get_font(58), fill=(70, 180, 255))

    draw.text((100, 300), f"PELAJARAN {index + 1}/{total}",
              font=get_font(34), fill=(180, 210, 255))

    draw.multiline_text(
        (100, 500), title, font=get_font(70),
        fill="white", spacing=24
    )

    draw.rounded_rectangle(
        (100, 850, 980, 1450),
        radius=35, fill=(15, 42, 78),
        outline=(35, 145, 255), width=4
    )

    draw.multiline_text(
        (155, 1030), text, font=get_font(55),
        fill=(235, 245, 255), spacing=30
    )

    draw.text((100, 1650), "Belajar AI dari dasar!",
              font=get_font(42), fill=(70, 180, 255))

    return img


async def main():
    topic = TOPICS[date.today().toordinal() % len(TOPICS)]

    Path("output").mkdir(exist_ok=True)
    Path("scenes").mkdir(exist_ok=True)

    voice_file = "output/narasi.mp3"

    communicate = edge_tts.Communicate(
        topic["voice"],
        voice="id-ID-ArdiNeural",
        rate="-5%"
    )
    await communicate.save(voice_file)

    scene_files = []

    for i, line in enumerate(topic["lines"]):
        filename = f"scenes/scene_{i:02d}.png"
        make_scene(
            topic["title"], line, i, len(topic["lines"])
        ).save(filename)
        scene_files.append(filename)

    with open("scenes/list.txt", "w", encoding="utf-8") as f:
        for filename in scene_files:
            f.write(f"file '{os.path.abspath(filename)}'\n")
            f.write("duration 7\n")
        f.write(f"file '{os.path.abspath(scene_files[-1])}'\n")

    subprocess.run([
        "ffmpeg", "-y",
        "-f", "concat", "-safe", "0",
        "-i", "scenes/list.txt",
        "-i", voice_file,
        "-vf", "fps=30,format=yuv420p",
        "-c:v", "libx264",
        "-preset", "ultrafast",
        "-c:a", "aac",
        "-shortest",
        "-movflags", "+faststart",
        "output/ai_pintar_video.mp4"
    ], check=True)

    print("Video berhasil dibuat!")


if __name__ == "__main__":
    asyncio.run(main())
