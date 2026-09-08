import os
import subprocess

ROOT = "/home/astra/.gemini/antigravity/scratch/hoi4_gulyaypole_mod_release"
OUTPUT_DIR = os.path.join(ROOT, "promo_video")
SLIDES_DIR = os.path.join(OUTPUT_DIR, "slides")
CLIPS_DIR = os.path.join(OUTPUT_DIR, "clips")
os.makedirs(CLIPS_DIR, exist_ok=True)

AUDIO_TRACK = os.path.join(ROOT, "music/mongol_shuudan_lyubo.ogg")
FINAL_VIDEO = os.path.join(OUTPUT_DIR, "gulyaypole_mod_official_trailer.mp4")

slides = [
    {"id": "slide_01", "dur": 5.0},
    {"id": "slide_02", "dur": 4.5},
    {"id": "slide_03", "dur": 4.5},
    {"id": "slide_04", "dur": 4.5},
    {"id": "slide_05", "dur": 4.5},
    {"id": "slide_06", "dur": 4.5},
    {"id": "slide_07", "dur": 5.0},
    {"id": "slide_08", "dur": 5.5},
]

clip_files = []

for idx, s in enumerate(slides):
    img_path = os.path.join(SLIDES_DIR, f"{s['id']}.png")
    out_clip = os.path.join(CLIPS_DIR, f"clip_{idx:02d}.mp4")
    clip_files.append(out_clip)
    
    dur = s["dur"]
    vf = f"fade=t=in:st=0:d=0.5,fade=t=out:st={dur-0.5}:d=0.5"
        
    cmd = [
        "ffmpeg", "-y",
        "-loop", "1",
        "-t", str(dur),
        "-i", img_path,
        "-vf", vf,
        "-c:v", "libx264",
        "-preset", "veryfast",
        "-pix_fmt", "yuv420p",
        "-r", "30",
        out_clip
    ]
    print(f"Encoding {out_clip}...")
    subprocess.check_call(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

# Write concat list
concat_list_path = os.path.join(CLIPS_DIR, "concat.txt")
with open(concat_list_path, "w") as f:
    for cf in clip_files:
        f.write(f"file '{cf}'\n")

raw_video = os.path.join(OUTPUT_DIR, "raw_video.mp4")
cmd_concat = [
    "ffmpeg", "-y",
    "-f", "concat",
    "-safe", "0",
    "-i", concat_list_path,
    "-c", "copy",
    raw_video
]
print("Concatenating clips...")
subprocess.check_call(cmd_concat, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

total_dur = sum(s["dur"] for s in slides)
print(f"Total video duration: {total_dur}s")

# Mix video with Mongol Shuudan soundtrack
cmd_final = [
    "ffmpeg", "-y",
    "-i", raw_video,
    "-ss", "0",
    "-t", str(total_dur),
    "-i", AUDIO_TRACK,
    "-map", "0:v",
    "-map", "1:a",
    "-af", f"afade=t=in:st=0:d=1.0,afade=t=out:st={total_dur-2.0}:d=2.0",
    "-c:v", "copy",
    "-c:a", "aac",
    "-b:a", "256k",
    "-shortest",
    FINAL_VIDEO
]
print("Mixing soundtrack and finalizing trailer...")
subprocess.check_call(cmd_final, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

# Also copy trailer to conversation brain directory so artifacts/links can access it
BRAIN_PROMO = "/home/astra/.gemini/antigravity/brain/cbfb705e-7ae6-4c0e-9385-273c0ec0cce5/gulyaypole_mod_official_trailer.mp4"
subprocess.check_call(["cp", FINAL_VIDEO, BRAIN_PROMO])

print(f"SUCCESS! Official video trailer created at: {FINAL_VIDEO} and {BRAIN_PROMO}")
