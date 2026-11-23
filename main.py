import asyncio
import subprocess
from pathlib import Path
from datetime import date
from PIL import Image, ImageDraw, ImageFont
import edge_tts

# AI PINTAR - pembuat video edukasi vertikal otomatis
W, H = 1080, 1920
FPS = 30
VOICE = "id-ID-ArdiNeural"
SCENE_COUNT = 5

TOPICS = [
    {
        "title": "JANGAN BAGIKAN DATA PRIBADI KE AI",
        "scenes": [
            ("GUNAKAN CHATBOT DENGAN BIJAK", "AI bisa membantu, tetapi tetap perlu waspada."),
            ("JAGA DATA PRIBADI", "Jangan masukkan nomor KTP, PIN, atau kata sandi."),
            ("RAHASIA TETAP RAHASIA", "Hindari membagikan data rekening dan dokumen rahasia."),
            ("PERIKSA PRIVASI", "Setiap layanan AI punya kebijakan data yang berbeda."),
            ("GUNAKAN AI DENGAN AMAN", "Samarkan informasi sensitif sebelum digunakan.")
        ],
        "voice": (
            "Hati-hati saat menggunakan kecerdasan buatan. "
            "Jangan sembarangan memasukkan nomor KTP, PIN, kata sandi, "
            "atau data rekening ke chatbot. Setiap layanan AI memiliki "
            "kebijakan privasi yang berbeda. Periksa pengaturannya dan "
            "samarkan informasi sensitif sebelum digunakan. "
            "Gunakan AI dengan cerdas dan tetap jaga privasimu. "
            "Ikuti AI PINTAR untuk belajar teknologi."
        ),
        "caption": "Jangan sembarangan membagikan data pribadi ke chatbot AI. "
                   "Lindungi KTP, PIN, kata sandi, dan data rekening. "
                   "Gunakan AI dengan aman! #AIPINTAR #TipsAI #KeamananDigital"
    },
    {
        "title": "AI BISA MEMBANTU PEKERJAAN",
        "scenes": [
            ("KERJA LEBIH CERDAS", "Manfaatkan AI sebagai alat bantu."),
            ("CARI IDE LEBIH CEPAT", "Minta AI membantu menemukan inspirasi."),
            ("SUSUN TULISAN", "Buat draf pesan, laporan, dan rangkuman."),
            ("RINGKAS INFORMASI", "Pahami informasi panjang dengan lebih mudah."),
            ("TETAP PERIKSA HASILNYA", "AI membantu, keputusan tetap di tanganmu.")
        ],
        "voice": (
            "Tahukah kamu? AI bisa membantu pekerjaan sehari-hari. "
            "Kamu bisa menggunakannya untuk mencari ide, menyusun tulisan, "
            "membuat draf laporan, dan merangkum informasi. Namun, jangan "
            "langsung percaya semua jawabannya. Periksa kembali hasilnya "
            "sebelum digunakan. Gunakan teknologi untuk bekerja lebih cerdas. "
            "Ikuti AI PINTAR untuk belajar AI dari dasar."
        ),
        "caption": "AI bisa membantu pekerjaan sehari-hari, mulai dari mencari ide "
                   "hingga merangkum informasi. Tetap periksa hasilnya! "
                   "#AIPINTAR #BelajarAI #Produktivitas"
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
            "Tidak perlu belajar semuanya sekaligus. Mulailah sedikit demi "
            "sedikit. Ikuti AI PINTAR untuk belajar AI dari dasar."
        ),
        "caption": "Belajar AI tidak harus rumit. Mulai dari pertanyaan sederhana, "
                   "berikan konteks, lalu periksa jawabannya. #AIPINTAR #BelajarAI"
    },
    {
        "title": "CARA MEMBUAT PROMPT AI YANG BAGUS",
        "scenes": [
            ("MULAI DENGAN TUJUAN", "Jelaskan apa yang ingin kamu buat."),
            ("BERIKAN KONTEKS", "Ceritakan kebutuhan dan situasimu."),
            ("TENTUKAN FORMAT", "Minta AI menjawab dalam format tertentu."),
            ("BERIKAN CONTOH", "Contoh membantu AI memahami keinginanmu."),
            ("PERIKSA HASIL", "Periksa dan perbaiki jawaban AI.")
        ],
        "voice": (
            "Ingin mendapatkan jawaban AI yang lebih bagus? "
            "Mulailah dengan menjelaskan tujuanmu. Berikan konteks yang jelas "
            "dan tentukan format jawaban. Jika perlu, berikan contoh agar AI "
            "lebih memahami keinginanmu. Terakhir, periksa kembali hasilnya. "
            "Ikuti AI PINTAR untuk belajar teknologi."
        ),
        "caption": "Rahasia prompt yang baik: tujuan jelas, konteks cukup, format tepat, "
                   "dan periksa hasilnya. #AIPINTAR #PromptAI #TipsAI"
    },
    {
        "title": "KENALI PENIPUAN DENGAN AI",
        "scenes": [
            ("WASPADA PENIPUAN DIGITAL", "Jangan mudah percaya pesan mencurigakan."),
            ("SUARA BISA DITIRU", "Teknologi AI dapat meniru suara."),
            ("PERIKSA IDENTITAS", "Hubungi orang tersebut melalui nomor lain."),
            ("JANGAN KIRIM UANG", "Pastikan kebenaran sebelum bertransaksi."),
            ("SELALU WASPADA", "Lindungi diri dan keluarga.")
        ],
        "voice": (
            "Tahukah kamu? Teknologi AI bisa digunakan untuk meniru suara. "
            "Karena itu, jangan langsung percaya jika menerima telepon "
            "atau pesan yang meminta uang. Periksa identitas melalui nomor "
            "lain sebelum bertindak. Tetap waspada dan ikuti AI PINTAR."
        ),
        "caption": "Waspada penipuan digital. Suara bisa ditiru dengan AI. "
                   "Selalu verifikasi sebelum mengirim uang. "
                   "#AIPINTAR #KeamananDigital #LiterasiDigital"
    },
    {
        "title": "AI BISA MEMBUAT KESALAHAN",
        "scenes": [
            ("AI TIDAK SELALU BENAR", "Jawaban AI bisa mengandung kesalahan."),
            ("PERIKSA INFORMASI", "Jangan langsung percaya semua jawaban."),
            ("CARI SUMBER", "Bandingkan dengan sumber tepercaya."),
            ("GUNAKAN AKAL SEHAT", "Nilai informasi sebelum digunakan."),
            ("PAKAI AI DENGAN BIJAK", "AI membantu, manusia tetap memutuskan.")
        ],
        "voice": (
            "Jangan menganggap semua jawaban AI pasti benar. "
            "AI bisa memberikan informasi yang keliru. Periksa fakta "
            "dan bandingkan dengan sumber tepercaya. Gunakan penilaianmu "
            "sebelum mengambil keputusan. Ikuti AI PINTAR untuk belajar AI."
        ),
        "caption": "AI bisa keliru. Periksa fakta dan bandingkan jawaban dengan "
                   "sumber tepercaya sebelum digunakan. #AIPINTAR #TipsAI"
    }
]

def load_font(size, bold=False):
    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold
        else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf" if bold
        else "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf"
    ]
    for path in candidates:
        if Path(path).exists():
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()

def wrap_text(draw, text, font, max_width):
    words = text.split()
    lines, line = [], ""
    for word in words:
        test = (line + " " + word).strip()
        if draw.textbbox((0, 0), test, font=font)[2] <= max_width:
            line = test
        else:
            if line:
                lines.append(line)
            line = word
    if line:
        lines.append(line)
    return lines

def make_scene(index, title, subtitle, out_path):
    image = Image.new("RGB", (W, H), (8, 18, 42))
    pixels = image.load()
    # Latar gradasi biru gelap ke biru
    for y in range(H):
        t = y / H
        color = (int(7 + 7*t), int(18 + 28*t), int(43 + 55*t))
        for x in range(W):
            pixels[x, y] = color

    draw = ImageDraw.Draw(image)
    # Elemen dekoratif futuristik
    draw.ellipse((760, -170, 1250, 320), outline=(30, 105, 180), width=8)
    draw.ellipse((-220, 1420, 300, 1940), outline=(25, 85, 150), width=8)
    draw.rounded_rectangle((70, 90, 1010, 180), radius=35,
                           fill=(18, 55, 100), outline=(65, 150, 230), width=3)
    draw.text((110, 112), "AI PINTAR  |  BELAJAR AI DARI DASAR",
              font=load_font( thirty := 30, True), fill=(230, 245, 255))

    # Panel utama
    draw.rounded_rectangle((65, 390, 1015, 1450), radius=55,
                           fill=(13, 35, 70), outline=(45, 130, 205), width=5)
    draw.rounded_rectangle((105, 455, 975, 475), radius=10,
                           fill=(40, 160, 255))
    draw.text((110, 535), f"0{index + 1} / 05",
              font=load_font(38, True), fill=(100, 195, 255))

    title_font = load_font(66, True)
    title_lines = wrap_text(draw, title, title_font, 820)
    y = 680
    for line in title_lines[:4]:
        draw.text((110, y), line, font=title_font, fill=(255, 255, 255))
        y += 92

    sub_font = load_font(43, False)
    sub_lines = wrap_text(draw, subtitle, sub_font, 820)
    y += 70
    for line in sub_lines[:4]:
        draw.text((110, y), line, font=sub_font, fill=(190, 220, 245))
        y += 66

    draw.rounded_rectangle((105, 1550, 975, 1690), radius=35,
                           fill=(20, 90, 155))
    draw.text((145, 1590), "Ikuti AI PINTAR untuk tips AI",
              font=load_font(34, True), fill=(255, 255, 255))
    draw.text((110, 1790), "Konten edukasi • Gunakan AI dengan bijak",
              font=load_font(27), fill=(165, 195, 220))
    image.save(out_path, quality=95)

async def create_voice(text, output_file):
    communicator = edge_tts.Communicate(
        text=text,
        voice=VOICE,
        rate="+0%",
        volume="+0%"
    )
    await communicator.save(str(output_file))

def run():
    root = Path(__file__).resolve().parent
    output_dir = root / "output"
    work_dir = root / "work"
    output_dir.mkdir(exist_ok=True)
    work_dir.mkdir(exist_ok=True)

    # Topik berganti otomatis berdasarkan hari dalam tahun
    topic = TOPICS[date.today().timetuple().tm_yday % len(TOPICS)]
    audio_file = work_dir / "narration.mp3"
    asyncio.run(create_voice(topic["voice"], audio_file))

    # Durasi suara dibaca dari FFprobe
    probe = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", str(audio_file)],
        capture_output=True, text=True, check=True
    )
    total_duration = float(probe.stdout.strip()) + 1.0
    scene_duration = total_duration / SCENE_COUNT

    image_files = []
    for i, (heading, subtitle) in enumerate(topic["scenes"]):
        image_file = work_dir / f"scene_{i:02d}.png"
        make_scene(i, heading, subtitle, image_file)
        image_files.append(image_file)

    concat_file = work_dir / "images.txt"
    with concat_file.open("w", encoding="utf-8") as f:
        for image_file in image_files:
            safe_path = str(image_file.resolve()).replace("'", "'\\''")
            f.write(f"file '{safe_path}'\n")
            f.write(f"duration {scene_duration:.3f}\n")
        # Ulangi frame terakhir agar durasi frame terakhir terbaca oleh concat
        safe_path = str(image_files[-1].resolve()).replace("'", "'\\''")
        f.write(f"file '{safe_path}'\n")

    video_file = output_dir / "ai_pintar_video.mp4"
    subprocess.run([
        "ffmpeg", "-y",
        "-f", "concat", "-safe", "0", "-i", str(concat_file),
        "-i", str(audio_file),
        "-map", "0:v:0", "-map", "1:a:0",
        "-vf", f"fps={FPS},format=yuv420p",
        "-c:v", "libx264", "-preset", "ultrafast", "-crf", "23",
        "-c:a", "aac", "-b:a", "128k",
        "-shortest", "-movflags", "+faststart",
        str(video_file)
    ], check=True)

    (output_dir / "caption.txt").write_text(
        topic["caption"], encoding="utf-8"
    )
    print(f"Video berhasil dibuat: {video_file}")
    print(f"Topik: {topic['title']}")

if __name__ == "__main__":
    run()
