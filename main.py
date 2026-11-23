
import asyncio
import subprocess
import math
from pathlib import Path
from datetime import date

import edge_tts
from PIL import Image, ImageDraw, ImageFont

W, H = 1080, 1920
FPS = 30
SCENE_SECONDS = 6
VOICE = "id-ID-ArdiNeural"

TOPICS = [
    {
        "title": "JANGAN BAGIKAN DATA PRIBADI KE AI",
        "scenes": [
            ("HATI-HATI SAAT MENGGUNAKAN AI", "Gunakan chatbot dengan bijak."),
            ("JAGA DATA PRIBADIMU", "Jangan kirim nomor KTP atau PIN."),
            ("RAHASIA TETAP RAHASIA", "Hindari membagikan kata sandi dan data rekening."),
            ("PERIKSA PRIVASI", "Setiap layanan AI punya kebijakan berbeda."),
            ("GUNAKAN AI DENGAN AMAN", "Samarkan informasi sensitif sebelum digunakan.")
        ],
        "voice": (
            "Hati-hati saat menggunakan kecerdasan buatan. "
            "Jangan sembarangan memasukkan nomor KTP, PIN, kata sandi, "
            "atau data rekening ke chatbot. Setiap layanan AI memiliki "
            "kebijakan privasi yang berbeda. Periksa pengaturannya dan "
            "samarkan informasi sensitif sebelum digunakan. "
            "Gunakan AI dengan cerdas dan tetap jaga privasimu. "
            "Ikuti AI Pintar untuk belajar teknologi."
        )
    },
    {
        "title": "AI BISA MEMBANTU PEKERJAAN",
        "scenes": [
            ("KERJA LEBIH CERDAS", "Manfaatkan AI sebagai alat bantu."),
            ("CARI IDE LEBIH CEPAT", "Minta AI membantu menemukan inspirasi."),
            ("SUSUN TULISAN", "Buat draf pesan dan laporan."),
            ("RINGKAS INFORMASI", "Pahami informasi yang panjang."),
            ("TETAP PERIKSA HASILNYA", "AI membantu, keputusan tetap di tanganmu.")
        ],
        "voice": (
            "Tahukah kamu? AI bisa membantu pekerjaan sehari-hari. "
            "Kamu bisa menggunakannya untuk mencari ide, menyusun tulisan, "
            "membuat draf laporan, dan merangkum informasi. "
            "Namun jangan langsung percaya semua jawabannya. "
            "Periksa kembali hasilnya sebelum digunakan. "
            "Gunakan teknologi untuk bekerja lebih cerdas. "
            "Ikuti AI Pintar untuk belajar AI dari dasar."
        )
    },
    {
        "title": "BELAJAR AI DARI DASAR",
        "scenes": [
            ("MULAI BELAJAR AI", "Tidak harus menjadi ahli teknologi."),
            ("TULIS PERTANYAAN", "Mulai dengan pertanyaan sederhana."),
            ("BERIKAN KONTEKS", "Jelaskan tujuan yang kamu inginkan."),
            ("PERIKSA JAWABAN", "Cek kembali informasi dari AI."),
            ("BELAJAR SETIAP HARI", "Sedikit demi sedikit menjadi lebih mahir.")
        ],
        "voice": (
            "Ingin belajar menggunakan kecerdasan buatan? "
            "Mulailah dengan pertanyaan sederhana. Jelaskan tujuanmu "
            "dan berikan konteks yang cukup agar AI memahami kebutuhanmu. "
            "Setelah mendapat jawaban, periksa kembali informasinya. "
            "Tidak perlu belajar semuanya sekaligus. "
            "Mulailah sedikit demi sedikit. "
            "Ikuti AI Pintar untuk belajar AI dari dasar."
        )
    }
]

def font(size, bold=False):
    paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    ]
    try:
        return ImageFont.truetype(paths[0 if bold else 1], size)
    except OSError:
        return ImageFont.load_default()

def wrap_text(draw, text, f, max_width):
    words = text.split()
    lines, line = [], ""
    for word in words:
        test = (line + " " + word).strip()
        if draw.textbbox((0, 0), test, font=f)[2] <= max_width:
            line = test
        else:
            if line:
                lines.append(line)
            line = word
    if line:
        lines.append(line)
    return lines

def make_scene(title, subtitle, index):
    palettes = [
        ((8, 20, 55), (20, 70, 130)),
        ((12, 35, 65), (20, 95, 115)),
        ((25, 20, 70), (65, 45, 125)),
        ((8, 45, 65), (15, 100, 125)),
        ((12, 25, 65), (30, 65, 145))
    ]
    top, bottom = palettes[index % len(palettes)]
    img = Image.new("RGB", (W, H))
    pix = img.load()

    for y in range(H):
        t = y / H
        c = tuple(int(top[i] * (1-t) + bottom[i] * t) for i in range(3))
        for x in range(W):
            pix[x, y] = c

    d = ImageDraw.Draw(img, "RGBA")

    # Futuristic decorative shapes
    d.ellipse((690, 170, 1180, 660), outline=(70, 190, 255, 75), width=8)
    d.ellipse((-200, 1100, 400, 1700), outline=(80, 170, 255, 55), width=7)
    d.rounded_rectangle((55, 90, 1025, 1800), radius=55,
                        outline=(90, 190, 255, 100), width=5)

    # Brand
    d.text((100, 125), "AI PINTAR", font=font(58, True),
           fill=(100, 200, 255))
    d.text((100, 220), f"BELAJAR AI  •  {index+1}/5",
           font=font( thirty := 30, True), fill=(190, 220, 255))

    # Scene number
    d.rounded_rectangle((100, 390, 290, 580), radius=40,
                        fill=(20, 115, 190, 180))
    d.text((150, 425), f"{index+1:02d}", font=font(85, True),
           fill="white")

    # Main title
    title_font = font(76, True)
    lines = wrap_text(d, title, title_font, 820)
    y = 700
    for line in lines:
        d.text((100, y), line, font=title_font, fill="white",
               stroke_width=1, stroke_fill=(10, 30, 60))
        y += 105

    # Subtitle panel
    d.rounded_rectangle((95, 1130, 985, 1510), radius=38,
                        fill=(5, 20, 45, 210),
                        outline=(80, 180, 255, 180), width=4)

    sub_font = font(46, True)
    sub_lines = wrap_text(d, subtitle, sub_font, 780)
    y = 1220
    for line in sub_lines:
        d.text((145, y), line, font=sub_font, fill=(225, 240, 255))
        y += 75

    d.text((100, 1650), "Ikuti AI PINTAR untuk belajar teknologi",
           font=font( thirty := 30), fill=(170, 210, 255))
    return img

async def main():
    topic = TOPICS[date.today().toordinal() % len(TOPICS)]

    Path("output").mkdir(exist_ok=True)
    Path("scenes").mkdir(exist_ok=True)

    voice_file = "output/narasi.mp3"
    communicate = edge_tts.Communicate(
        topic["voice"], VOICE, rate="-5%"
    )
    await communicate.save(voice_file)

    clips = []
    for i, (title, subtitle) in enumerate(topic["scenes"]):
        image_file = f"scenes/scene_{i+1}.png"
        make_scene(title, subtitle, i).save(image_file)

        clip_file = f"scenes/clip_{i+1}.mp4"
        subprocess.run([
            "ffmpeg", "-y", "-loop", "1", "-i", image_file,
            "-vf",
            "zoompan=z='min(zoom+0.0005,1.04)':"
            "d=180:s=1080x1920:fps=30,format=yuv420p",
            "-t", str(SCENE_SECONDS),
            "-c:v", "libx264", "-preset", "ultrafast",
            "-an", clip_file
        ], check=True, stdout=subprocess.DEVNULL,
           stderr=subprocess.DEVNULL)
        clips.append(clip_file)

    with open("scenes/list.txt", "w") as f:
        for clip in clips:
            f.write(f"file '{Path(clip).resolve()}'\n")

    subprocess.run([
        "ffmpeg", "-y", "-f", "concat", "-safe", "0",
        "-i", "scenes/list.txt", "-i", voice_file,
        "-map", "0:v:0", "-map", "1:a:0",
        "-vf", "scale=1080:1920,format=yuv420p",
        "-af", "apad", "-t", "30",
        "-r", str(FPS), "-c:v", "libx264",
        "-preset", "ultrafast", "-crf", "23",
        "-c:a", "aac", "-b:a", "128k",
        "-movflags", "+faststart",
        "output/ai_pintar_video.mp4"
    ], check=True)

    print("Video AI PINTAR berhasil dibuat!")

if __name__ == "__main__":
    asyncio.run(main())
