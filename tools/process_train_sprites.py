import os
from PIL import Image, ImageChops, ImageFilter

ROOT = "/home/astra/.gemini/antigravity/scratch/hoi4_gulyaypole_mod_release"
BRAIN = "/home/astra/.gemini/antigravity/brain/cbfb705e-7ae6-4c0e-9385-273c0ec0cce5"
TECH_DIR = os.path.join(ROOT, "gfx/interface/technologies")

# Source images
im1_path = os.path.join(BRAIN, "glp_train_svoboda_sprite_1788889390914.jpg")
im2_path = os.path.join(BRAIN, "glp_train_batko_sprite_1788889408118.jpg")
im_multi_path = os.path.join(BRAIN, "glp_armored_trains_sideview_1788889371637.jpg")

def isolate_white_background(img, threshold=240):
    im = img.convert("RGBA")
    r, g, b, a = im.split()
    # Mask where all r,g,b > threshold
    datas = im.getdata()
    new_data = []
    for item in datas:
        # Check if nearly white
        if item[0] > threshold and item[1] > threshold and item[2] > threshold:
            # check saturation / difference
            max_diff = max(abs(item[0]-item[1]), abs(item[1]-item[2]), abs(item[0]-item[2]))
            if max_diff < 15:
                new_data.append((255, 255, 255, 0)) # transparent
                continue
        new_data.append(item)
    im.putdata(new_data)
    return im

def crop_to_content(im):
    bbox = im.getbbox()
    if bbox:
        return im.crop(bbox)
    return im

# 1. Train 1: «Свобода или Смерть»
im1 = Image.open(im1_path)
# Crop train area (exclude flag pole top if needed or keep)
im1_iso = isolate_white_background(im1, threshold=245)
im1_cropped = crop_to_content(im1_iso)
print("im1 cropped size:", im1_cropped.size)

# 2. Train 2: «Батько Махно»
im2 = Image.open(im2_path)
# Crop to remove bottom text "INSURGENT SUPER-HEAVY TRAIN..."
w, h = im2.size
im2 = im2.crop((0, 0, w, int(h * 0.82))) # cut bottom text
im2_iso = isolate_white_background(im2, threshold=245)
im2_cropped = crop_to_content(im2_iso)
print("im2 cropped size:", im2_cropped.size)

# 3. Train 3: «Гроза Степей» (from bottom of multi image)
im_multi = Image.open(im_multi_path)
w_m, h_m = im_multi.size
# The bottom train is roughly from y = 470 to y = 730
im3 = im_multi.crop((0, 480, w_m, 740))
im3_iso = isolate_white_background(im3, threshold=245)
im3_cropped = crop_to_content(im3_iso)
print("im3 cropped size:", im3_cropped.size)

# Function to fit into HOI4 equipment format: canvas 180x80 (or 240x96), centered with clean margins
def make_hoi4_tech_sprite(cropped_im, canvas_size=(180, 80)):
    canvas = Image.new("RGBA", canvas_size, (0, 0, 0, 0))
    cw, ch = canvas_size
    
    # Scale to fit with margins (padding: 8px horizontal, 6px vertical)
    target_w = cw - 16
    target_h = ch - 12
    
    ratio = min(target_w / cropped_im.width, target_h / cropped_im.height)
    new_w = int(cropped_im.width * ratio)
    new_h = int(cropped_im.height * ratio)
    
    scaled = cropped_im.resize((new_w, new_h), Image.Resampling.LANCZOS)
    
    # Paste centered horizontally, aligned toward bottom center
    pos_x = (cw - new_w) // 2
    pos_y = (ch - new_h) // 2 + 2
    canvas.paste(scaled, (pos_x, pos_y), scaled)
    return canvas

# Generate the 3 sprites
s1 = make_hoi4_tech_sprite(im1_cropped, (180, 80))
s2 = make_hoi4_tech_sprite(im2_cropped, (180, 80))
s3 = make_hoi4_tech_sprite(im3_cropped, (180, 80))

# Save PNG previews for brain / showcase
s1.save(os.path.join(BRAIN, "GLP_train_svoboda_sprite.png"))
s2.save(os.path.join(BRAIN, "GLP_train_batko_sprite.png"))
s3.save(os.path.join(BRAIN, "GLP_train_groza_sprite.png"))

# Also save transparent PNGs in mod technologies folder
s1.save(os.path.join(TECH_DIR, "GLP_train_tech_1.png"))
s2.save(os.path.join(TECH_DIR, "GLP_train_tech_2.png"))
s3.save(os.path.join(TECH_DIR, "GLP_train_tech_3.png"))

print("Exported transparent PNG sprites successfully!")
