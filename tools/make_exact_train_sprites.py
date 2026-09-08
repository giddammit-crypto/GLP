import os
import subprocess
from PIL import Image, ImageDraw, ImageEnhance

ROOT = "/home/astra/.gemini/antigravity/scratch/hoi4_gulyaypole_mod_release"
BRAIN = "/home/astra/.gemini/antigravity/brain/cbfb705e-7ae6-4c0e-9385-273c0ec0cce5"
TECH_DIR = os.path.join(ROOT, "gfx/interface/technologies")
os.makedirs(TECH_DIR, exist_ok=True)

FLAG_IMG = os.path.join(ROOT, "mod_page/assets/flag.png")
flag_base = Image.open(FLAG_IMG).convert("RGBA")

# 1. Base Train 1: «Свобода или Смерть» (from glp_train_svoboda_sprite_1788889390914.jpg)
im1 = Image.open(os.path.join(BRAIN, "glp_train_svoboda_sprite_1788889390914.jpg")).convert("RGBA")

# Isolate transparent background
def isolate_pure_white(im, thresh=240):
    im_rgba = im.convert("RGBA")
    datas = im_rgba.getdata()
    new_data = []
    for item in datas:
        if item[0] > thresh and item[1] > thresh and item[2] > thresh:
            diff = max(abs(item[0]-item[1]), abs(item[1]-item[2]), abs(item[0]-item[2]))
            if diff < 15:
                new_data.append((0, 0, 0, 0))
                continue
        new_data.append(item)
    im_rgba.putdata(new_data)
    return im_rgba

im1_iso = isolate_pure_white(im1)

# In train 1, replace the pirate skull flag with the official Gulyaypole flag!
# Let's locate the flag area on im1 (around x: 530..700, y: 140..250 in 1376x768)
w1, h1 = im1_iso.size

# Erase the existing skull flag cloth
draw1 = ImageDraw.Draw(im1_iso)
# Erase old flag area with transparent pixels
for y in range(140, 245):
    for x in range(540, 710):
        im1_iso.putpixel((x, y), (0, 0, 0, 0))

# Resize official flag to fit flag pole
flag_resized_1 = flag_base.resize((150, 95), Image.Resampling.LANCZOS)
im1_iso.paste(flag_resized_1, (550, 145), flag_resized_1)

bbox1 = im1_iso.getbbox()
im1_cropped = im1_iso.crop(bbox1)

# 2. Base Train 2: «Батько Махно» (from glp_train_batko_sprite_1788889408118.jpg)
im2 = Image.open(os.path.join(BRAIN, "glp_train_batko_sprite_1788889408118.jpg")).convert("RGBA")
# Erase bottom text completely
w2, h2 = im2.size
# crop strictly above the text
im2 = im2.crop((0, 0, w2, int(h2 * 0.78)))
im2_iso = isolate_pure_white(im2)

# Add a flagpole with official Gulyaypole flag on the command locomotive cab!
# Command locomotive roof is around x=480..520, y=280..320
draw2 = ImageDraw.Draw(im2_iso)
# Draw dark metallic flagpole
flagpole_x = 490
draw2.line([(flagpole_x, 190), (flagpole_x, 340)], fill=(35, 35, 38, 255), width=4)
# Paste Gulyaypole flag
flag_resized_2 = flag_base.resize((140, 88), Image.Resampling.LANCZOS)
im2_iso.paste(flag_resized_2, (flagpole_x + 4, 195), flag_resized_2)

bbox2 = im2_iso.getbbox()
im2_cropped = im2_iso.crop(bbox2)

# 3. Base Train 3: «Гроза Степей» (from multi image)
im_multi = Image.open(os.path.join(BRAIN, "glp_armored_trains_sideview_1788889371637.jpg")).convert("RGBA")
# middle train or bottom train without upper wheels
# Middle train: y from 370 to 650
im3 = im_multi.crop((0, 365, im_multi.width, 640))
im3_iso = isolate_pure_white(im3)

# Add Gulyaypole flag onto the middle train's turret
draw3 = ImageDraw.Draw(im3_iso)
flagpole3_x = 720
draw3.line([(flagpole3_x, 20), (flagpole3_x, 150)], fill=(35, 35, 38, 255), width=4)
flag_resized_3 = flag_base.resize((130, 82), Image.Resampling.LANCZOS)
im3_iso.paste(flag_resized_3, (flagpole3_x + 4, 25), flag_resized_3)

# Remove any text on wagons if present
bbox3 = im3_iso.getbbox()
im3_cropped = im3_iso.crop(bbox3)

# Canvas fitting for standard HOI4 equipment format: 180x80 pixels
def fit_sprite(cropped_im):
    canvas = Image.new("RGBA", (180, 80), (0, 0, 0, 0))
    cw, ch = 180, 80
    target_w = cw - 12
    target_h = ch - 10
    ratio = min(target_w / cropped_im.width, target_h / cropped_im.height)
    new_w = int(cropped_im.width * ratio)
    new_h = int(cropped_im.height * ratio)
    scaled = cropped_im.resize((new_w, new_h), Image.Resampling.LANCZOS)
    pos_x = (cw - new_w) // 2
    pos_y = (ch - new_h) // 2 + 1
    canvas.paste(scaled, (pos_x, pos_y), scaled)
    return canvas

sp1 = fit_sprite(im1_cropped)
sp2 = fit_sprite(im2_cropped)
sp3 = fit_sprite(im3_cropped)

# Save transparent PNGs
sp1.save(os.path.join(BRAIN, "GLP_train_svoboda_sprite_final.png"))
sp2.save(os.path.join(BRAIN, "GLP_train_batko_sprite_final.png"))
sp3.save(os.path.join(BRAIN, "GLP_train_groza_sprite_final.png"))

sp1.save(os.path.join(TECH_DIR, "GLP_train_tech_1.png"))
sp2.save(os.path.join(TECH_DIR, "GLP_train_tech_2.png"))
sp3.save(os.path.join(TECH_DIR, "GLP_train_tech_3.png"))

# Convert to HOI4 DXT5 / ARGB DDS
for i, name in enumerate(["GLP_train_tech_1", "GLP_train_tech_2", "GLP_train_tech_3"], 1):
    png_path = os.path.join(TECH_DIR, f"{name}.png")
    dds_path = os.path.join(TECH_DIR, f"{name}.dds")
    # Use ImageMagick to produce DXT5 with full alpha
    cmd = ["magick", png_path, "-define", "dds:compression=dxt5", dds_path]
    subprocess.check_call(cmd)
    print(f"Generated {dds_path}")

print("All exact train sprites created successfully!")
