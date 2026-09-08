import os
import struct
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance

ROOT = "/home/astra/.gemini/antigravity/scratch/hoi4_gulyaypole_mod_release"
SRC_IMG = os.path.join(ROOT, "mod_page/assets/gallery/armored_train.jpg")

OUT_DIR = os.path.join(ROOT, "gfx/event_pictures")
os.makedirs(OUT_DIR, exist_ok=True)

# Helper to save uncompressed RGB888 DDS for 397x153 event pictures (identical to existing news_event_glp_armored_train.dds)
def save_dds_rgb888(image, out_path):
    # Ensure exact size 397x153
    im = image.resize((397, 153), Image.Resampling.LANCZOS).convert("RGB")
    width, height = im.size
    
    # DDS Header (128 bytes)
    magic = b'DDS '
    size = 124
    flags = 0x1007  # DDSD_CAPS | DDSD_HEIGHT | DDSD_WIDTH | DDSD_PIXELFORMAT
    pitch = width * 3
    depth = 0
    mipmaps = 0
    reserved1 = b'\x00' * 44
    
    # Pixel format: 32 bytes (DDPF_RGB)
    pf_size = 32
    pf_flags = 0x40  # DDPF_RGB
    fourcc = 0
    rgb_bits = 24
    r_mask = 0x00FF0000
    g_mask = 0x0000FF00
    b_mask = 0x000000FF
    a_mask = 0
    
    pf = struct.pack('<IIIIIIII', pf_size, pf_flags, fourcc, rgb_bits, r_mask, g_mask, b_mask, a_mask)
    caps = 0x1000  # DDSCAPS_TEXTURE
    caps2 = caps3 = caps4 = 0
    reserved2 = 0
    
    header = struct.pack('<4sIIIIII44s32sIIIII', magic, size, flags, height, width, pitch, depth, reserved1, pf, caps, caps2, caps3, caps4, reserved2)
    
    # Pixel data in BGR format
    pixels = bytearray()
    raw = im.tobytes()
    for i in range(0, len(raw), 3):
        r, g, b = raw[i], raw[i+1], raw[i+2]
        pixels.extend([b, g, r])
        
    with open(out_path, 'wb') as f:
        f.write(header)
        f.write(pixels)
    print(f"Wrote DDS RGB888 {out_path} ({width}x{height})")

base_im = Image.open(SRC_IMG).convert("RGB")

# 1. Поезд «Свобода или Смерть» (тяжёлый штурмовой бронепоезд, тёмно-стальной контрастный)
im1 = base_im.copy()
im1 = ImageEnhance.Contrast(im1).enhance(1.25)
im1 = ImageEnhance.Color(im1).enhance(0.7)
save_dds_rgb888(im1, os.path.join(OUT_DIR, "news_event_glp_train_svoboda.dds"))

# 2. Поезд «Батько Махно» (флагманский степной бронепоезд, с золотисто-медным тоном и прожекторами)
im2 = base_im.copy()
im2 = ImageEnhance.Contrast(im2).enhance(1.15)
im2 = ImageEnhance.Brightness(im2).enhance(1.1)
# Warm copper tint
overlay = Image.new("RGB", im2.size, (210, 160, 100))
im2 = Image.blend(im2, overlay, 0.12)
save_dds_rgb888(im2, os.path.join(OUT_DIR, "news_event_glp_train_batko.dds"))

# 3. Поезд «Гроза Степей» (маневренный рейдовый бронепоезд, ночной холодный синий тон)
im3 = base_im.copy()
im3 = ImageEnhance.Contrast(im3).enhance(1.3)
im3 = ImageEnhance.Brightness(im3).enhance(0.9)
# Cool night tint
overlay3 = Image.new("RGB", im3.size, (80, 110, 160))
im3 = Image.blend(im3, overlay3, 0.15)
save_dds_rgb888(im3, os.path.join(OUT_DIR, "news_event_glp_train_groza.dds"))

print("Train art assets generated successfully!")
