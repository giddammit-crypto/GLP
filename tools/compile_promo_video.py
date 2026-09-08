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
    {"id": "slide_01", "dur": 5.0, "zoom": "in"},
    {"id": "slide_02", "dur": 4.5, "zoom": "out"},
    {"id": "slide_03", "dur": 4.5, "zoom": "in"},
    {"id": "slide_04", "dur": 4.5, "zoom": "out"},
    {"id": "slide_05", "dur": 4.5, "zoom": "in"},
    {"id": "slide_06", "dur": 4.5, "zoom": "out"},
    {"id": "slide_07", "dur": 5.0, "zoom": "in"},
    {"id": "slide_08", "dur": 5.5, "zoom": "out"},
]

clip_files = []

for idx, s in enumerate(slides):
    img_path = os.path.join(SLIDES_DIR, f"{s['id']}.png")
    out_clip = os.path.join(CLIPS_DIR, f"clip_{idx:02d}.mp4")
    clip_files.append(out_clip)
    
    dur = s["dur"]
    fps = 30
    total_frames = int(dur * fps)
    
    # Smooth Ken-Burns zoom effect
    if s["zoom"] == "in":
        vf = f"scale=8000x4500,zoompan=z='min(zoom+0.0007,1.15)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={total_frames}:s=1920x1080:fps={fps},fade=t=in:st=0:d=0.5,fade=t=out:st={dur-0.5}:d=0.5"
    else:
        vf = f"scale=8000x4500,zoompan=z='if(lte(on,1),1.15,max(1.0,zoom-0.0007))':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={total_frames}:s=1920x1080:fps={fps},fade=t=in:st=0:d=0.5,fade=t=out:st={dur-0.5}:d=0.5"
        
    cmd = [
        "ffmpeg", "-y",
        "-loop", "1",
        "-t", str(dur),
        "-i", img_path,
        "-vf", vf,
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        "-r", str(fps),
        out_clip
    ]
    print(f"Encoding {out_clip}...")
    subprocess.check_call(cmd)

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
subprocess.check_call(cmd_concat)

# Total duration calculation
total_dur = sum(s["dur"] for s in slides)
print(f"Total video duration: {total_dur}s")

# Mix video with Mongol Shuudan soundtrack (fade in/out audio)
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
subprocess.check_call(cmd_final)

print(f"SUCCESS! Official video trailer created at: {FINAL_VIDEO}")
