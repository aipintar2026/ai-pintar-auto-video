import asyncio
import json
import os
import random
import time
import subprocess
import urllib.parse
import urllib.request
import urllib.error
from pathlib import Path
from datetime import date
from PIL import Image, ImageDraw, ImageFont
import edge_tts

# AI PINTAR — edukasi sederhana 30-45 detik dengan footage bergerak dari Pixabay
W, H, FPS = 1080, 1920, 30
VOICE = "id-ID-ArdiNeural"
API_URL = "https://pixabay.com/api/videos/"

TOPICS = [
    {
        "title": "JANGAN BAGIKAN DATA PRIBADI KE AI",
        "queries": ["person using smartphone", "cyber security computer", "digital privacy technology", "computer data protection", "person using laptop"],
        "scenes": [
            ("GUNAKAN CHATBOT DENGAN BIJAK", "AI bisa membantu, tetapi tetap perlu waspada."),
            ("JAGA DATA PRIBADI", "Jangan masukkan nomor KTP, PIN, atau kata sandi."),
            ("RAHASIA TETAP RAHASIA", "Hindari membagikan data rekening dan dokumen rahasia."),
            ("PERIKSA PRIVASI", "Setiap layanan AI punya kebijakan data yang berbeda."),
            ("GUNAKAN AI DENGAN AMAN", "Samarkan informasi sensitif sebelum digunakan.")
        ],
        "voice": "Saat menggunakan chatbot AI, jangan langsung memasukkan semua informasi pribadi. Hindari membagikan nomor KTP, PIN, kata sandi, alamat lengkap, atau data rekening. Informasi seperti ini bisa berisiko jika tersebar atau digunakan dengan cara yang tidak tepat. Sebelum memakai sebuah layanan AI, baca pengaturan dan kebijakan privasinya. Jika perlu menjelaskan masalah, samarkan nama dan data sensitif terlebih dahulu. Ingat, AI boleh membantu pekerjaanmu, tetapi keamanan data tetap tanggung jawab kita. Ikuti AI PINTAR untuk belajar AI dengan aman.",
        "caption": "Jangan sembarangan membagikan data pribadi ke chatbot AI. Lindungi KTP, PIN, kata sandi, dan data rekening. Gunakan AI dengan aman! #AIPINTAR #TipsAI #KeamananDigital"
    },
    {
        "title": "AI BISA MEMBANTU PEKERJAAN",
        "queries": ["person working on laptop office", "artificial intelligence technology", "typing on computer keyboard", "business data computer screen", "person using computer"],
        "scenes": [
            ("KERJA LEBIH CERDAS", "Manfaatkan AI sebagai alat bantu."),
            ("CARI IDE LEBIH CEPAT", "Minta AI membantu menemukan inspirasi."),
            ("SUSUN TULISAN", "Buat draf pesan, laporan, dan rangkuman."),
            ("RINGKAS INFORMASI", "Pahami informasi panjang dengan lebih mudah."),
            ("TETAP PERIKSA HASILNYA", "AI membantu, keputusan tetap di tanganmu.")
        ],
        "voice": "AI dapat membantu pekerjaan sehari-hari, bukan hanya untuk menjawab pertanyaan. Kamu bisa memakainya untuk mencari ide, membuat kerangka laporan, menyusun pesan, merangkum bacaan, atau menyiapkan daftar pekerjaan. Agar hasilnya lebih sesuai, jelaskan tujuan, konteks, dan bentuk jawaban yang kamu inginkan. Misalnya, minta AI membuat rangkuman dalam lima poin dengan bahasa sederhana. Setelah itu, baca dan periksa kembali hasilnya. AI adalah alat bantu, bukan pengganti penilaian manusia. Gunakan waktumu lebih efektif bersama AI. Ikuti AI PINTAR untuk belajar dari dasar.",
        "caption": "AI bisa membantu pekerjaan sehari-hari, mulai dari mencari ide hingga merangkum informasi. Tetap periksa hasilnya! #AIPINTAR #BelajarAI #Produktivitas"
    },
    {
        "title": "BELAJAR AI DARI DASAR",
        "queries": ["student learning computer", "person studying laptop", "technology education computer", "typing laptop close up", "person watching computer screen"],
        "scenes": [
            ("MULAI BELAJAR AI", "Tidak harus menjadi ahli teknologi."),
            ("TULIS PERTANYAAN", "Mulai dengan pertanyaan sederhana."),
            ("BERIKAN KONTEKS", "Jelaskan tujuan yang kamu inginkan."),
            ("PERIKSA JAWABAN", "Cek kembali informasi dari AI."),
            ("BELAJAR SETIAP HARI", "Sedikit demi sedikit menjadi lebih mahir.")
        ],
        "voice": "Belajar kecerdasan buatan tidak harus dimulai dengan istilah teknis yang sulit. Kamu bisa mulai dari hal sederhana, seperti bertanya cara membuat jadwal, merangkum tulisan, atau mencari ide. Jelaskan tujuanmu dengan kalimat yang jelas, lalu berikan sedikit konteks agar AI memahami kebutuhanmu. Jika jawabannya belum sesuai, tambahkan informasi atau perbaiki pertanyaanmu. Jangan lupa memeriksa fakta, karena AI juga bisa keliru. Cobalah satu fitur baru setiap hari dan pelajari manfaatnya untuk kegiatan sehari-hari. Ikuti AI PINTAR, kita belajar AI sedikit demi sedikit.",
        "caption": "Belajar AI tidak harus rumit. Mulai dari pertanyaan sederhana, berikan konteks, lalu periksa jawabannya. #AIPINTAR #BelajarAI"
    },
    {
        "title": "CARA MEMBUAT PROMPT AI YANG BAGUS",
        "queries": ["person typing laptop", "artificial intelligence computer screen", "computer programming code", "person working at desk computer", "technology digital interface"],
        "scenes": [
            ("MULAI DENGAN TUJUAN", "Jelaskan apa yang ingin kamu buat."),
            ("BERIKAN KONTEKS", "Ceritakan kebutuhan dan situasimu."),
            ("TENTUKAN FORMAT", "Minta AI menjawab dalam format tertentu."),
            ("BERIKAN CONTOH", "Contoh membantu AI memahami keinginanmu."),
            ("PERIKSA HASIL", "Periksa dan perbaiki jawaban AI.")
        ],
        "voice": "Ingin mendapatkan jawaban AI yang lebih sesuai? Buat prompt atau instruksi yang jelas. Pertama, jelaskan tujuan yang ingin dicapai. Kedua, berikan konteks, misalnya siapa pembacanya dan untuk kebutuhan apa. Ketiga, tentukan bentuk jawaban, seperti daftar, tabel, atau langkah-langkah. Kamu juga bisa memberi contoh gaya bahasa yang diinginkan. Jika hasil pertama belum tepat, jangan langsung menyerah. Beri koreksi yang spesifik dan minta AI memperbaikinya. Terakhir, periksa kembali informasi penting sebelum digunakan. Semakin jelas instruksimu, semakin mudah AI memahami kebutuhanmu. Ikuti AI PINTAR untuk tips berikutnya.",
        "caption": "Rahasia prompt yang baik: tujuan jelas, konteks cukup, format tepat, dan periksa hasilnya. #AIPINTAR #PromptAI #TipsAI"
    },
    {
        "title": "KENALI PENIPUAN DENGAN AI",
        "queries": ["cyber security warning computer", "person using smartphone phone call", "online scam cybersecurity", "digital security lock computer", "person checking smartphone"],
        "scenes": [
            ("WASPADA PENIPUAN DIGITAL", "Jangan mudah percaya pesan mencurigakan."),
            ("SUARA BISA DITIRU", "Teknologi AI dapat meniru suara."),
            ("PERIKSA IDENTITAS", "Hubungi orang tersebut melalui nomor lain."),
            ("JANGAN KIRIM UANG", "Pastikan kebenaran sebelum bertransaksi."),
            ("SELALU WASPADA", "Lindungi diri dan keluarga.")
        ],
        "voice": "Teknologi AI bisa digunakan untuk membuat suara tiruan dan membantu penipu menyamar sebagai orang lain. Karena itu, jangan langsung percaya pada telepon atau pesan yang terdengar mendesak, meskipun suaranya mirip keluarga atau teman. Jika ada permintaan uang, kode OTP, atau informasi rahasia, berhenti sejenak. Hubungi orang tersebut melalui nomor yang sudah kamu kenal, bukan nomor yang menghubungimu. Buat kata sandi keluarga untuk keadaan darurat dan selalu periksa kebenaran cerita. Jangan terburu-buru mengambil keputusan. Bagikan informasi ini agar orang terdekat juga waspada. Ikuti AI PINTAR untuk belajar keamanan digital.",
        "caption": "Waspada penipuan digital. Suara bisa ditiru dengan AI. Selalu verifikasi sebelum mengirim uang. #AIPINTAR #KeamananDigital #LiterasiDigital"
    },
    {
        "title": "AI BISA MEMBUAT KESALAHAN",
        "queries": ["artificial intelligence technology computer", "person researching on laptop", "computer data analysis", "person reading computer screen", "technology digital information"],
        "scenes": [
            ("AI TIDAK SELALU BENAR", "Jawaban AI bisa mengandung kesalahan."),
            ("PERIKSA INFORMASI", "Jangan langsung percaya semua jawaban."),
            ("CARI SUMBER", "Bandingkan dengan sumber tepercaya."),
            ("GUNAKAN AKAL SEHAT", "Nilai informasi sebelum digunakan."),
            ("PAKAI AI DENGAN BIJAK", "AI membantu, manusia tetap memutuskan.")
        ],
        "voice": "Jawaban dari AI tidak selalu benar, meskipun terdengar yakin dan disampaikan dengan bahasa yang rapi. AI bisa salah memahami pertanyaan, menggunakan informasi yang sudah lama, atau membuat detail yang sebenarnya tidak ada. Karena itu, jangan langsung menyalin jawabannya untuk tugas, pekerjaan, atau keputusan penting. Periksa fakta utama melalui sumber yang tepercaya, terutama angka, tanggal, nama, dan aturan. Jika topiknya penting, bandingkan lebih dari satu sumber. Gunakan AI untuk membantu memahami informasi, tetapi tetap gunakan penilaianmu sendiri. Ingat, tanggung jawab atas keputusan akhir ada pada manusia. Ikuti AI PINTAR untuk belajar AI secara bijak.",
        "caption": "AI bisa keliru. Periksa fakta dan bandingkan jawaban dengan sumber tepercaya sebelum digunakan. #AIPINTAR #TipsAI"
    }
]

def run_cmd(args):
    subprocess.run(args, check=True)

def get_font(size, bold=False):
    paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf"
    ]
    for p in paths:
        if Path(p).exists():
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()

def wrap(draw, text, font, max_width):
    words, lines, current = text.split(), [], ""
    for word in words:
        candidate = (current + " " + word).strip()
        if draw.textbbox((0, 0), candidate, font=font)[2] <= max_width:
            current = candidate
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines

def make_overlay(number, heading, subtitle, path):
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    # Panel transparan agar footage tetap terlihat
    d.rounded_rectangle((55, 95, 1025, 250), 38, fill=(5, 20, 45, 205), outline=(60, 165, 255, 235), width=4)
    d.text((95, 145), "AI PINTAR • EDUKASI AI", font=get_font( thirty := 30, True), fill=(235, 247, 255, 255))
    d.rounded_rectangle((55, 1190, 1025, 1665), 45, fill=(4, 18, 42, 215), outline=(55, 145, 225, 240), width=4)
    d.text((100, 1235), f"0{number} / 05", font=get_font(34, True), fill=(90, 195, 255, 255))
    y = 1300
    for line in wrap(d, heading, get_font(54, True), 850)[:3]:
        d.text((100, y), line, font=get_font(54, True), fill=(255, 255, 255, 255))
        y += 68
    y += 20
    for line in wrap(d, subtitle, get_font(36), 850)[:3]:
        d.text((100, y), line, font=get_font(36), fill=(205, 230, 250, 255))
        y += 48
    d.rounded_rectangle((55, 1740, 1025, 1840), 28, fill=(12, 80, 145, 220))
    d.text((95, 1770), "Ikuti AI PINTAR untuk tips AI", font=get_font(34, True), fill=(255, 255, 255, 255))
    im.save(path)

def pixabay_video(api_key, query, destination, used_ids):
    """Unduh klip Pixabay yang belum dipakai; coba beberapa hasil dan retry jaringan."""
    params = urllib.parse.urlencode({
        "key": api_key,
        "q": query,
        "per_page": 50,
        "video_type": "film",
        "safesearch": "true"
    })
    url = API_URL + "?" + params
    last_error = None

    for attempt in range(1, 4):
        try:
            request = urllib.request.Request(
                url, headers={"User-Agent": "AI-PINTAR-Video/1.0"}
            )
            with urllib.request.urlopen(request, timeout=45) as response:
                data = json.loads(response.read().decode("utf-8"))

            hits = data.get("hits", [])
            candidates = [
                hit for hit in hits
                if str(hit.get("id", "")) not in used_ids
                and any(
                    hit.get("videos", {}).get(size, {}).get("url")
                    for size in ("medium", "large", "small")
                )
            ]
            random.shuffle(candidates)

            for hit in candidates:
                formats = hit.get("videos", {})
                selected = (
                    formats.get("medium")
                    or formats.get("large")
                    or formats.get("small")
                )
                if not selected or not selected.get("url"):
                    continue

                video_request = urllib.request.Request(
                    selected["url"], headers={"User-Agent": "Mozilla/5.0"}
                )
                try:
                    with urllib.request.urlopen(video_request, timeout=90) as response:
                        video_data = response.read()
                except Exception as download_error:
                    print(f"Footage ID {hit.get('id')} gagal diunduh; mencoba hasil lain.")
                    last_error = download_error
                    continue

                if len(video_data) > 100_000:
                    Path(destination).write_bytes(video_data)
                    clip_id = str(hit.get("id", ""))
                    if clip_id:
                        used_ids.add(clip_id)
                    print(f"FOOTAGE TERPILIH: ID {clip_id or 'tidak tersedia'}")
                    return clip_id

            if not candidates:
                raise RuntimeError(
                    f"Tidak ditemukan footage baru untuk '{query}' yang belum pernah dipakai. "
                    "Riwayat klip tetap dipertahankan agar tidak mengulang footage."
                )
            raise RuntimeError(
                f"Semua footage yang ditemukan gagal diunduh untuk pencarian: {query}"
            )

        except urllib.error.HTTPError as error:
            detail = error.read().decode("utf-8", errors="replace")
            print(f"PIXABAY HTTP ERROR: {error.code}")
            print(f"PIXABAY DETAIL: {detail[:1000]}")
            if error.code not in (429, 500, 502, 503, 504):
                raise RuntimeError(
                    f"Pixabay menolak permintaan (HTTP {error.code})."
                ) from error
            last_error = error
        except (urllib.error.URLError, TimeoutError, ConnectionError) as error:
            print(f"PIXABAY CONNECTION ERROR percobaan {attempt}/3: {error}")
            last_error = error

        if attempt < 3:
            time.sleep(attempt * 4)

    raise RuntimeError(f"Pixabay gagal setelah 3 percobaan: {last_error}")



def validate_topics():
    """Memeriksa kelengkapan struktur topik sebelum produksi."""
    if not TOPICS:
        raise RuntimeError("QC GAGAL: daftar TOPICS kosong.")

    for index, topic in enumerate(TOPICS, start=1):
        required = ("title", "queries", "scenes", "voice", "caption")
        missing = [key for key in required if not topic.get(key)]
        if missing:
            raise RuntimeError(
                f"QC GAGAL: topik ke-{index} tidak memiliki: {', '.join(missing)}"
            )

        if len(topic["scenes"]) != 5 or len(topic["queries"]) != 5:
            raise RuntimeError(
                f"QC GAGAL: topik '{topic['title']}' harus memiliki "
                "tepat 5 scenes dan 5 queries."
            )

        for scene_number, scene in enumerate(topic["scenes"], start=1):
            if not isinstance(scene, (tuple, list)) or len(scene) != 2:
                raise RuntimeError(
                    f"QC GAGAL: format adegan {scene_number} pada "
                    f"topik '{topic['title']}' tidak valid."
                )
            if not all(str(part).strip() for part in scene):
                raise RuntimeError(
                    f"QC GAGAL: judul/subjudul adegan {scene_number} "
                    f"pada topik '{topic['title']}' kosong."
                )

    print(f"QC STRUKTUR: {len(TOPICS)} topik lengkap, masing-masing 5 adegan.")


def quality_control_video(video_path):
    """Memeriksa file MP4 final: durasi, resolusi, dan audio."""
    video_path = Path(video_path)

    if not video_path.exists():
        raise RuntimeError("QC GAGAL: file MP4 tidak ditemukan.")
    if video_path.stat().st_size < 100_000:
        raise RuntimeError("QC GAGAL: ukuran MP4 terlalu kecil atau file kosong.")

    probe = subprocess.run(
        [
            "ffprobe", "-v", "error",
            "-show_entries", "format=duration:stream=codec_type,width,height",
            "-of", "json", str(video_path)
        ],
        capture_output=True, text=True, check=True
    )
    metadata = json.loads(probe.stdout)
    duration = float(metadata.get("format", {}).get("duration", 0))
    streams = metadata.get("streams", [])

    video_streams = [x for x in streams if x.get("codec_type") == "video"]
    audio_streams = [x for x in streams if x.get("codec_type") == "audio"]

    if not video_streams:
        raise RuntimeError("QC GAGAL: stream video tidak ditemukan.")
    if not audio_streams:
        raise RuntimeError("QC GAGAL: audio/narasi tidak ditemukan.")

    video_stream = video_streams[0]
    width = int(video_stream.get("width", 0))
    height = int(video_stream.get("height", 0))

    if (width, height) != (1080, 1920):
        raise RuntimeError(
            f"QC GAGAL: resolusi {width}x{height}; target 1080x1920."
        )
    if not 30 <= duration <= 46:
        raise RuntimeError(
            f"QC GAGAL: durasi akhir {duration:.1f} detik; target 30–45 detik "
            "dengan toleransi render."
        )

    print("QC VIDEO: LULUS")
    print(f"QC DURASI: {duration:.1f} detik")
    print(f"QC RESOLUSI: {width}x{height}")
    print("QC AUDIO: ditemukan")
    print(f"QC UKURAN FILE: {video_path.stat().st_size / (1024 * 1024):.1f} MB")


async def create_voice(text, output_file):
    """Buat narasi dengan retry jika layanan Edge TTS sementara tidak terjangkau."""
    last_error = None
    for attempt in range(1, 4):
        try:
            await edge_tts.Communicate(
                text=text, voice=VOICE, rate="+0%", volume="+0%"
            ).save(str(output_file))
            if Path(output_file).exists() and Path(output_file).stat().st_size > 10_000:
                print(f"EDGE TTS: narasi berhasil dibuat pada percobaan {attempt}.")
                return
            raise RuntimeError("File audio tidak terbentuk atau terlalu kecil.")
        except Exception as error:
            last_error = error
            print(f"EDGE TTS gagal pada percobaan {attempt}/3: {error}")
            if attempt < 3:
                await asyncio.sleep(attempt * 5)
    raise RuntimeError(f"Edge TTS gagal setelah 3 percobaan: {last_error}")

def main():
    validate_topics()
    api_key = os.environ.get("PIXABAY_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError("Secret PIXABAY_API_KEY belum tersedia di GitHub Actions.")
    root = Path(__file__).resolve().parent
    output_dir, work_dir = root / "output", root / "work"
    output_dir.mkdir(exist_ok=True)
    work_dir.mkdir(exist_ok=True)

    # Riwayat footage disimpan di .cache dan dipulihkan oleh GitHub Actions cache.
    history_dir = root / ".cache"
    history_dir.mkdir(exist_ok=True)
    history_file = history_dir / "pixabay-history.json"
    if history_file.exists():
        try:
            used_ids = set(json.loads(history_file.read_text(encoding="utf-8")))
        except (json.JSONDecodeError, OSError):
            used_ids = set()
    else:
        used_ids = set()

    # Rotasi topik harian
    topic = TOPICS[date.today().timetuple().tm_yday % len(TOPICS)]
    audio = work_dir / "narration.mp3"
    asyncio.run(create_voice(topic["voice"], audio))

    probe = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", str(audio)],
        capture_output=True, text=True, check=True
    )
    total = float(probe.stdout.strip()) + 0.5
    print(f"DURASI NARASI: {total:.1f} detik")
    if total < 30 or total > 45:
        print("PERINGATAN: Durasi narasi di luar target AI PINTAR (30-45 detik).")
    else:
        print("DURASI SESUAI STANDAR AI PINTAR (30-45 detik).")
    duration = total / len(topic["scenes"])

    clips = []
    for i, ((heading, subtitle), query) in enumerate(zip(topic["scenes"], topic["queries"]), start=1):
        raw = work_dir / f"pixabay_{i}.mp4"
        overlay = work_dir / f"overlay_{i}.png"
        rendered = work_dir / f"scene_{i}.mp4"
        print(f"Mengambil footage {i}/5: {query}")
        pixabay_video(api_key, query, raw, used_ids)
        make_overlay(i, heading, subtitle, overlay)
        run_cmd([
            "ffmpeg", "-y", "-stream_loop", "-1", "-i", str(raw), "-loop", "1", "-i", str(overlay),
            "-t", f"{duration:.3f}",
            "-filter_complex",
            "[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,fps=30,setsar=1[bg];[1:v]format=rgba[ov];[bg][ov]overlay=0:0,format=yuv420p[v]",
            "-map", "[v]", "-an", "-c:v", "libx264", "-preset", "ultrafast", "-crf", "24",
            "-movflags", "+faststart", str(rendered)
        ])
        clips.append(rendered)

    concat = work_dir / "clips.txt"
    with concat.open("w", encoding="utf-8") as f:
        for clip in clips:
            f.write(f"file '{clip.resolve()}'\n")

    output = output_dir / "ai_pintar_video.mp4"
    run_cmd([
        "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(concat), "-i", str(audio),
        "-map", "0:v:0", "-map", "1:a:0", "-c:v", "copy", "-c:a", "aac", "-b:a", "128k",
        "-shortest", "-movflags", "+faststart", str(output)
    ])
    quality_control_video(output)
    history_file.write_text(
        json.dumps(sorted(used_ids), ensure_ascii=False, indent=2),
        encoding="utf-8"
    )
    print(f"RIWAYAT FOOTAGE: {len(used_ids)} ID tersimpan.")
    (output_dir / "caption.txt").write_text(topic["caption"], encoding="utf-8")
    print(f"BERHASIL: {output}")
    print(f"TOPIK: {topic['title']}")

if __name__ == "__main__":
    main()
