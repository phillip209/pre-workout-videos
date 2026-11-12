"""Review helper: grab frames of a rendered episode at (line, word, offset) cues into a contact sheet."""
import json, subprocess, sys
import imageio_ffmpeg
from PIL import Image

ep = sys.argv[1]
keys = [k.split(":") for k in sys.argv[2:]]
ff = imageio_ffmpeg.get_ffmpeg_exe()
tl = json.load(open(f"out/{ep}/timeline.json", encoding="utf-8"))
Wd = {(l["id"], w[0].lower().strip(".,?¿!:")): w[1] for l in tl["lines"] for w in l["words"]}
ims = []
for lid, w, d in keys:
    t = Wd[(lid, w)] + float(d)
    raw = subprocess.run([ff, "-v", "error", "-ss", f"{t:.2f}", "-i", f"out/{ep}/{ep}.mp4", "-frames:v", "1", "-vf",
                          "scale=216:384:flags=neighbor", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True).stdout
    ims.append(Image.frombytes("RGB", (216, 384), raw))
cols = 8
rows = (len(ims) + cols - 1) // cols
sheet = Image.new("RGB", (cols * 219, rows * 387), (255, 255, 255))
for i, im in enumerate(ims):
    sheet.paste(im, ((i % cols) * 219, (i // cols) * 387))
sheet.save(f"out/{ep}/review.png")
