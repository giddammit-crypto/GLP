from PIL import Image

BRAIN = "/home/astra/.gemini/antigravity/brain/cbfb705e-7ae6-4c0e-9385-273c0ec0cce5"
im_multi_path = f"{BRAIN}/glp_armored_trains_sideview_1788889371637.jpg"

im_multi = Image.open(im_multi_path)
w_m, h_m = im_multi.size
# Let's crop train 3 carefully to avoid the upper wheels
# The train 3 itself: y from 520 to 730
im3 = im_multi.crop((0, 520, w_m, 735))

# Isolate white background
im3_rgba = im3.convert("RGBA")
datas = im3_rgba.getdata()
new_data = []
for item in datas:
    if item[0] > 235 and item[1] > 235 and item[2] > 235:
        max_diff = max(abs(item[0]-item[1]), abs(item[1]-item[2]), abs(item[0]-item[2]))
        if max_diff < 15:
            new_data.append((255, 255, 255, 0))
            continue
    new_data.append(item)
im3_rgba.putdata(new_data)

bbox = im3_rgba.getbbox()
if bbox:
    im3_cropped = im3_rgba.crop(bbox)
else:
    im3_cropped = im3_rgba

# Fit to 180x80 canvas
canvas = Image.new("RGBA", (180, 80), (0, 0, 0, 0))
cw, ch = (180, 80)
target_w = cw - 16
target_h = ch - 14

ratio = min(target_w / im3_cropped.width, target_h / im3_cropped.height)
new_w = int(im3_cropped.width * ratio)
new_h = int(im3_cropped.height * ratio)

scaled = im3_cropped.resize((new_w, new_h), Image.Resampling.LANCZOS)
pos_x = (cw - new_w) // 2
pos_y = (ch - new_h) // 2 + 4
canvas.paste(scaled, (pos_x, pos_y), scaled)

canvas.save(f"{BRAIN}/GLP_train_groza_sprite.png")
canvas.save("gfx/interface/technologies/GLP_train_tech_3.png")
print("Cleaned train 3 sprite generated successfully!")
