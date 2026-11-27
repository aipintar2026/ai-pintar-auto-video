"""Automatic short-video cover generation and structural QC."""
from pathlib import Path
import subprocess
from PIL import Image, ImageDraw, ImageFont, ImageOps

WIDTH,HEIGHT=1080,1920
SAFE=(80,260,1000,1620)


def _font(size):
    for p in ("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf","C:/Windows/Fonts/arialbd.ttf"):
        try:
            return ImageFont.truetype(p,size)
        except OSError:
            pass
    return ImageFont.load_default()


def _wrap_title(title,font,max_width):
    words=str(title).strip().split()
    lines=[]; current=""
    for word in words:
        candidate=(current+" "+word).strip()
        if current and font.getbbox(candidate)[2]>max_width:
            lines.append(current); current=word
        else:
            current=candidate
    if current: lines.append(current)
    return lines


def generate_cover_from_frame(frame_path, output, title):
    src=Image.open(frame_path).convert("RGB")
    image=ImageOps.fit(src,(WIDTH,HEIGHT),method=Image.Resampling.LANCZOS)
    overlay=Image.new("RGBA",(WIDTH,HEIGHT),(0,0,0,0))
    draw=ImageDraw.Draw(overlay)
    font=_font(76)
    lines=_wrap_title(title,font,800)
    while len(lines)>5 and font.size>48:
        font=_font(font.size-4); lines=_wrap_title(title,font,800)
    if len(lines)>5:
        lines=lines[:5]
        lines[-1]=lines[-1].rstrip(" .") + "…"
    line_heights=[font.getbbox(line)[3]-font.getbbox(line)[1] for line in lines]
    total=sum(line_heights)+24*(len(lines)-1)
    box_top=max(500,min(HEIGHT-total-200,780))
    box_bottom=box_top+total+120
    draw.rounded_rectangle((100,box_top-60,980,box_bottom+60),radius=42,fill=(5,14,38,205),outline=(38,137,231,230),width=5)
    brand_font=_font(42)
    draw.text((150,box_top-10),"AI PINTAR",font=brand_font,fill=(110,205,255,255),stroke_width=1,stroke_fill=(0,0,0,180))
    y=box_top+60
    for line,height in zip(lines,line_heights):
        draw.text((150,y),line,font=font,fill=(255,255,255,255),stroke_width=2,stroke_fill=(0,0,0,180))
        y+=height+24
    image=Image.alpha_composite(image.convert("RGBA"),overlay).convert("RGB")
    out=Path(output); out.parent.mkdir(parents=True,exist_ok=True)
    image.save(out,"JPEG",quality=90,optimize=True)
    report=validate_cover(out,title,lines,box_top,box_bottom)
    return report


def create_cover_from_video(video_path, output, title, frame_time=1.0):
    frame=Path(output).with_suffix(".frame.jpg")
    frame.parent.mkdir(parents=True,exist_ok=True)
    subprocess.run(["ffmpeg","-y","-ss",str(frame_time),"-i",str(video_path),"-frames:v","1","-q:v","2",str(frame)],check=True,capture_output=True,timeout=60)
    try:
        return generate_cover_from_frame(frame,output,title)
    finally:
        frame.unlink(missing_ok=True)


def validate_cover(path,title,lines=None,box_top=None,box_bottom=None):
    p=Path(path)
    if not p.exists() or p.stat().st_size<10_000:
        raise RuntimeError("Cover QC: file hilang atau terlalu kecil.")
    with Image.open(p) as im:
        if im.size!=(WIDTH,HEIGHT):
            raise RuntimeError("Cover QC: resolusi harus 1080x1920.")
    if not str(title).strip():
        raise RuntimeError("Cover QC: judul kosong.")
    line_count=len(lines or _wrap_title(str(title),_font(76),800))
    if line_count>5:
        raise RuntimeError("Cover QC: judul melebihi 5 baris.")
    if box_top is not None and box_bottom is not None and (box_top<SAFE[1] or box_bottom>SAFE[3]):
        raise RuntimeError("Cover QC: teks keluar dari safe zone.")
    return {"cover_qc_status":"PASS","resolution":"1080x1920","title_lines":line_count,"safe_zone":"PASS","visual_review_required":True,"semantic_match":"NOT_AUTOMATED"}
