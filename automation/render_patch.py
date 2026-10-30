from __future__ import annotations
import json, re, subprocess
from PIL import Image, ImageDraw, ImageFont
import daily_short as pipeline

OUT = pipeline.OUT

def render(data):
    script = data["script"].strip()
    title = data["title"].strip()
    (OUT/"script.txt").write_text(script, encoding="utf-8")
    (OUT/"metadata.json").write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    voices = subprocess.run(["espeak-ng", "--voices"], capture_output=True, text=True, check=True).stdout
    voice = "en-in" if re.search(r"\\ben-in\\b", voices) else "en"
    subprocess.run(["espeak-ng", "-v", voice, "-s", "148", "-w", str(OUT/"voice.wav"), script], check=True)

    W, H = 720, 1280
    img = Image.new("RGB", (W,H), (11,22,42))
    draw = ImageDraw.Draw(img)
    for y in range(H):
        t = y/H
        draw.line((0,y,W,y), fill=(int(11+10*t), int(22+25*t), int(42+48*t)))
    regular = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    bold = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
    small = ImageFont.truetype(regular, 24)
    title_font = ImageFont.truetype(bold, 42)
    brand = ImageFont.truetype(bold, 22)
    draw.rounded_rectangle((44,54,300,104), radius=18, fill=(34,76,128))
    draw.text((62,66), "DAILY AI NEWS", font=brand, fill="white")
    draw.text((48,190), "TODAY'S UPDATE", font=small, fill=(140,190,245))
    title_lines = pipeline.wrap_lines(title[:72], title_font, draw, 610)[:3]
    y = 270
    for line in title_lines:
        draw.text((48,y), line, font=title_font, fill="white", stroke_width=1)
        y += 58
    draw.rounded_rectangle((48,760,672,1010), radius=24, outline=(91,145,205), width=3)
    draw.text((78,800), "WHAT YOU NEED TO KNOW", font=brand, fill=(143,195,250))
    draw.text((78,865), "AI • TECHNOLOGY • EXPLAINED", font=small, fill=(230,238,248))
    draw.text((48,1160), "Follow for clear, source-linked AI updates", font=small, fill=(205,220,240))
    img.save(OUT/"background.png")

    # Keep captions compact and split long sentences into short readable lines.
    chunks = [c.strip() for c in re.split(r'(?<=[.!?])\\s+', script) if c.strip()]
    probe = subprocess.run(["ffprobe","-v","error","-show_entries","format=duration","-of","default=noprint_wrappers=1:nokey=1",str(OUT/"voice.wav")], capture_output=True, text=True, check=True)
    duration = float(probe.stdout.strip())
    weights = [max(1,len(c.split())) for c in chunks]
    total = sum(weights)
    cursor = 0.0
    def stamp(sec):
        ms = int(round(sec*1000)); h=ms//3600000; ms%=3600000; m=ms//60000; ms%=60000; s=ms//1000; ms%=1000
        return f"{h:02}:{m:02}:{s:02},{ms:03}"
    with (OUT/"captions.srt").open("w", encoding="utf-8") as f:
        for i,(chunk,weight) in enumerate(zip(chunks,weights),1):
            start = cursor
            cursor += duration*weight/total
            lines = pipeline.textwrap.wrap(chunk, width=34, break_long_words=False, break_on_hyphens=False)
            f.write(f"{i}\\n{stamp(start)} --> {stamp(cursor)}\\n" + "\\n".join(lines) + "\\n\\n")

    vf = "scale=720:1280,zoompan=z='min(zoom+0.00025,1.08)':d=1:s=720x1280:fps=30,subtitles=output/captions.srt:force_style='FontName=DejaVu Sans,FontSize=9,PrimaryColour=&H00FFFFFF,OutlineColour=&H00101010,BorderStyle=1,Outline=1,Shadow=0,Alignment=2,MarginV=145'"
    subprocess.run(["ffmpeg","-y","-loop","1","-i",str(OUT/"background.png"),"-i",str(OUT/"voice.wav"),"-vf",vf,"-t",str(duration),"-r","30","-c:v","libx264","-preset","veryfast","-pix_fmt","yuv420p","-c:a","aac","-b:a","128k","-shortest",str(OUT/"daily-short.mp4")], check=True)
    result = subprocess.run(["ffprobe","-v","error","-show_entries","stream=codec_type,width,height","-of","json",str(OUT/"daily-short.mp4")], capture_output=True, text=True, check=True)
    streams = json.loads(result.stdout)["streams"]
    if not any(s.get("codec_type")=="video" and s.get("width")==720 and s.get("height")==1280 for s in streams):
        raise RuntimeError("Rendered file failed vertical-video validation.")
    if not any(s.get("codec_type")=="audio" for s in streams):
        raise RuntimeError("Rendered file has no audio.")
