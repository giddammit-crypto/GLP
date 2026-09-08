import os
import subprocess
from PIL import Image, ImageDraw

ROOT = "/home/astra/.gemini/antigravity/scratch/hoi4_gulyaypole_mod_release"
BRAIN = "/home/astra/.gemini/antigravity/brain/cbfb705e-7ae6-4c0e-9385-273c0ec0cce5"
TECH_DIR = os.path.join(ROOT, "gfx/interface/technologies")

FLAG_IMG = os.path.join(ROOT, "mod_page/assets/flag.png")
flag_base = Image.open(FLAG_IMG).convert("RGBA")

im_multi = Image.open(os.path.join(BRAIN, "glp_armored_trains_sideview_1788889371637.jpg")).convert("RGBA")
w_m, h_m = im_multi.size

# Middle train: y from 375 to 495 (pure middle train body and gun turret without top/bottom overlap!)
# Let's inspect coordinates:
# The middle train locomotive and gun wagon run across the middle:
im3 = im_multi.crop((0, 360, w_m, 500))

# Isolate pure white background
datas = im3.getdata()
new_data = []
for item in datas:
    if item[0] > 235 and item[1] > 235 and item[2] > 235:
        diff = max(abs(item[0]-item[1]), abs(item[1]-item[2]), abs(item[0]-item[2]))
        if diff < 15:
            new_data.append((0, 0, 0, 0))
            continue
    new_data.append(item)
im3.putdata(new_data)

bbox3 = im3.getbbox()
if bbox3:
    im3_cropped = im3.crop(bbox3)
else:
    im3_cropped = im3

# Also add the official Gulyaypole flag on top of the middle train!
flag_w = 120
flag_h = int(flag_w * flag_base.height / flag_base.width)
flag_resized = flag_base.resize((flag_w, flag_h), Image.Resampling.LANCZOS)

# Create an expanded height image to host the flag
comb = Image.new("RGBA", (im3_cropped.width, im3_cropped.height + flag_h + 10), (0, 0, 0, 0))
comb.paste(im3_cropped, (0, flag_h + 10), im3_cropped)

# Draw flagpole and paste flag on the locomotive cab / turret
draw = ImageDraw.Draw(comb)
fp_x = int(comb.width * 0.42)
draw.line([(fp_x, 8), (fp_x, flag_h + 20)], fill=(35, 35, 38, 255), width=4)
comb.paste(flag_resized, (fp_x + 4, 10), flag_resized)

# Now fit to HOI4 standard 180x80 canvas
bbox_comb = comb.getbbox()
comb_cropped = comb.crop(bbox_comb)

canvas = Image.new("RGBA", (180, 80), (0, 0, 0, 0))
cw, ch = 180, 80
target_w = cw - 12
target_h = ch - 10
ratio = min(target_w / comb_cropped.width, target_h / comb_cropped.height)
new_w = int(comb_cropped.width * ratio)
new_h = int(comb_cropped.height * ratio)
scaled = comb_cropped.resize((new_w, new_h), Image.Resampling.LANCZOS)
pos_x = (cw - new_w) // 2
pos_y = (ch - new_h) // 2 + 2
canvas.paste(scaled, (pos_x, pos_y), scaled)

canvas.save(os.path.join(BRAIN, "GLP_train_groza_sprite_final.png"))
canvas.save(os.path.join(TECH_DIR, "GLP_train_tech_3.png"))

# Convert to DDS DXT5
subprocess.check_call(["magick", os.path.join(TECH_DIR, "GLP_train_tech_3.png"), "-define", "dds:compression=dxt5", os.path.join(TECH_DIR, "GLP_train_tech_3.dds")])
print("Train 3 perfectly cleaned and generated!")
