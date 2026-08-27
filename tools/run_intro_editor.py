#!/usr/bin/env python3
"""
Визуальный редактор заставки HOI4 — Гуляй-Поле.
Координаты в редакторе 1:1 совпадают с координатами в файле .gui и в игре.
"""

import http.server, socketserver, json, os, re, sys, urllib.parse

PORT = 8088
MOD_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GUI_PATH = os.path.join(MOD_DIR, "interface", "gulyaipole_intro_custom.gui")
ASSETS_DIR = os.path.join(MOD_DIR, "tools", "editor_assets")

# ─── Парсинг GUI → dict ────────────────────────────────────────────────────

def parse_pos(block):
    m = re.search(r'position\s*=\s*\{\s*x\s*=\s*(-?\d+)\s*y\s*=\s*(-?\d+)', block)
    return (int(m.group(1)), int(m.group(2))) if m else (0, 0)

def parse_size(block):
    m = re.search(r'size\s*=\s*\{\s*width\s*=\s*(\d+)\s*height\s*=\s*(\d+)', block)
    if m: return (int(m.group(1)), int(m.group(2)))
    mw = re.search(r'maxWidth\s*=\s*(\d+)', block)
    mh = re.search(r'maxHeight\s*=\s*(\d+)', block)
    if mw and mh: return (int(mw.group(1)), int(mh.group(1)))
    return (100, 20)

ELEMENT_PATTERNS = {
    "ukraine_military_map":  r'iconType\s*=\s*\{[^}]*name\s*=\s*"ukraine_military_map"[^}]*\}',
    "makhno_portrait_intro": r'iconType\s*=\s*\{[^}]*name\s*=\s*"makhno_portrait_intro"[^}]*\}',
    "makhno_caption":        r'instantTextBoxType\s*=\s*\{[^}]*name\s*=\s*"makhno_caption"[^}]*\}',
    "cavalry_photo":         r'iconType\s*=\s*\{[^}]*name\s*=\s*"cavalry_photo"[^}]*\}',
    "cavalry_caption":       r'instantTextBoxType\s*=\s*\{[^}]*name\s*=\s*"cavalry_caption"[^}]*\}',
    "text_panel_bg":         r'iconType\s*=\s*\{[^}]*name\s*=\s*"text_panel_bg"[^}]*\}',
    "cinematic_intro_text":  r'instantTextBoxType\s*=\s*\{[^}]*name\s*=\s*"cinematic_intro_text"[^}]*\}',
    "map_caption":           r'instantTextBoxType\s*=\s*\{[^}]*name\s*=\s*"map_caption"[^}]*\}',
    "start_campaign_button": r'buttonType\s*=\s*\{[^}]*name\s*=\s*"start_campaign_button"[^}]*\}',
}

def parse_gui():
    if not os.path.exists(GUI_PATH): return {}
    with open(GUI_PATH, encoding="utf-8", errors="replace") as f:
        txt = f.read()
    result = {}
    for name, pat in ELEMENT_PATTERNS.items():
        m = re.search(pat, txt, re.DOTALL)
        if m:
            block = m.group(0)
            x, y = parse_pos(block)
            w, h  = parse_size(block)
            result[name] = {"x": x, "y": y, "w": w, "h": h}
    return result

# ─── Генератор GUI-кода ────────────────────────────────────────────────────

def gen(el, name, defaults):
    d = {**defaults, **el.get(name, {})}
    return d

def generate_gui(elements):
    MAP  = gen(elements, "ukraine_military_map",  {"x":35,  "y":85,  "w":285,"h":225})
    MAPC = gen(elements, "map_caption",            {"x":35,  "y":315, "w":285,"h":20})
    POR  = gen(elements, "makhno_portrait_intro",  {"x":380, "y":40,  "w":225,"h":325})
    PORC = gen(elements, "makhno_caption",         {"x":380, "y":372, "w":225,"h":20})
    CAV  = gen(elements, "cavalry_photo",          {"x":660, "y":120, "w":322,"h":166})
    CAVC = gen(elements, "cavalry_caption",        {"x":660, "y":292, "w":322,"h":20})
    TBG  = gen(elements, "text_panel_bg",          {"x":108, "y":428, "w":790,"h":200})
    TXT  = gen(elements, "cinematic_intro_text",   {"x":113, "y":435, "w":780,"h":182})
    BTN  = gen(elements, "start_campaign_button",  {"x":327, "y":696, "w":221,"h":34})

    # Метка кнопки — всегда на 7px ниже Y кнопки, по центру
    bl_x = BTN["x"]
    bl_y = BTN["y"] + 7
    bl_w = BTN["w"]

    return f"""# Гуляй-Поле — кинематографическая заставка (HOI4 1.19.2)
# Сгенерировано визуальным редактором. Координаты 1:1 совпадают с игрой.

guiTypes = {{
\tcontainerWindowType = {{
\t\tname = "gulyaipole_cinematic_intro_window"
\t\tposition = {{ x = 0 y = 0 }}
\t\tsize = {{ width = 1024 height = 768 }}
\t\torientation = center
\t\torigo = center
\t\tmoveable = no
\t\tclick_to_front = no

\t\tbackground = {{
\t\t\tname = "Background"
\t\t\tquadTextureSprite = "GFX_intro_bg"
\t\t}}

\t\ticonType = {{
\t\t\tname = "intro_window_frame"
\t\t\tposition = {{ x = 0 y = 0 }}
\t\t\tsize = {{ width = 1024 height = 768 }}
\t\t\tspriteType = "GFX_gold_inner_border"
\t\t\talwaystransparent = yes
\t\t}}

\t\t# ── КАРТА
\t\ticonType = {{
\t\t\tname = "ukraine_military_map"
\t\t\tposition = {{ x = {MAP['x']} y = {MAP['y']} }}
\t\t\tsize = {{ width = {MAP['w']} height = {MAP['h']} }}
\t\t\tspriteType = "GFX_intro_ukraine_map"
\t\t\talwaystransparent = yes
\t\t}}
\t\tinstantTextBoxType = {{
\t\t\tname = "map_caption"
\t\t\tposition = {{ x = {MAPC['x']} y = {MAPC['y']} }}
\t\t\tfont = "cg_16b"
\t\t\tborderSize = {{ x = 0 y = 0 }}
\t\t\ttext = "GULYAIPOLE_MAP_CAPTION"
\t\t\tmaxWidth = {MAPC['w']}
\t\t\tmaxHeight = {MAPC['h']}
\t\t\tfixedsize = yes
\t\t\tformat = center
\t\t}}

\t\t# ── ПОРТРЕТ МАХНО (без рамки)
\t\ticonType = {{
\t\t\tname = "makhno_portrait_intro"
\t\t\tposition = {{ x = {POR['x']} y = {POR['y']} }}
\t\t\tsize = {{ width = {POR['w']} height = {POR['h']} }}
\t\t\tspriteType = "GFX_portrait_nestor_makhno_intro"
\t\t\talwaystransparent = yes
\t\t}}
\t\tinstantTextBoxType = {{
\t\t\tname = "makhno_caption"
\t\t\tposition = {{ x = {PORC['x']} y = {PORC['y']} }}
\t\t\tfont = "cg_16b"
\t\t\tborderSize = {{ x = 0 y = 0 }}
\t\t\ttext = "GULYAIPOLE_MAKHNO_CAPTION"
\t\t\tmaxWidth = {PORC['w']}
\t\t\tmaxHeight = {PORC['h']}
\t\t\tfixedsize = yes
\t\t\tformat = center
\t\t}}

\t\t# ── КОННИЦА
\t\ticonType = {{
\t\t\tname = "cavalry_photo"
\t\t\tposition = {{ x = {CAV['x']} y = {CAV['y']} }}
\t\t\tsize = {{ width = {CAV['w']} height = {CAV['h']} }}
\t\t\tspriteType = "GFX_intro_makhno_cavalry"
\t\t\talwaystransparent = yes
\t\t}}
\t\tinstantTextBoxType = {{
\t\t\tname = "cavalry_caption"
\t\t\tposition = {{ x = {CAVC['x']} y = {CAVC['y']} }}
\t\t\tfont = "cg_16b"
\t\t\tborderSize = {{ x = 0 y = 0 }}
\t\t\ttext = "GULYAIPOLE_CAVALRY_CAPTION"
\t\t\tmaxWidth = {CAVC['w']}
\t\t\tmaxHeight = {CAVC['h']}
\t\t\tfixedsize = yes
\t\t\tformat = center
\t\t}}

\t\t# ── ТЕКСТ ИСТОРИИ
\t\ticonType = {{
\t\t\tname = "text_panel_bg"
\t\t\tposition = {{ x = {TBG['x']} y = {TBG['y']} }}
\t\t\tsize = {{ width = {TBG['w']} height = {TBG['h']} }}
\t\t\tspriteType = "GFX_tiled_bg_dark"
\t\t\talwaystransparent = yes
\t\t}}
\t\tinstantTextBoxType = {{
\t\t\tname = "cinematic_intro_text"
\t\t\tposition = {{ x = {TXT['x']} y = {TXT['y']} }}
\t\t\tfont = "cg_16b"
\t\t\tborderSize = {{ x = 4 y = 4 }}
\t\t\ttext = "GULYAIPOLE_EPIC_INTRO_TEXT"
\t\t\tmaxWidth = {TXT['w']}
\t\t\tmaxHeight = {TXT['h']}
\t\t\tformat = left
\t\t\tscrollbarType = standardtext_slider
\t\t}}

\t\t# ── КНОПКА (buttonType для click + textbox для кириллицы)
\t\tbuttonType = {{
\t\t\tname = "start_campaign_button"
\t\t\tposition = {{ x = {BTN['x']} y = {BTN['y']} }}
\t\t\tspriteType = "GFX_intro_start_button"
\t\t\tbuttonText = ""
\t\t\tclicksound = click_default
\t\t\tshortcut = "ENTER"
\t\t}}
\t\tinstantTextBoxType = {{
\t\t\tname = "start_campaign_button_label"
\t\t\tposition = {{ x = {bl_x} y = {bl_y} }}
\t\t\tfont = "cg_16b"
\t\t\tborderSize = {{ x = 0 y = 0 }}
\t\t\ttext = "GULYAIPOLE_START_BUTTON"
\t\t\tmaxWidth = {bl_w}
\t\t\tmaxHeight = 20
\t\t\tfixedsize = yes
\t\t\tformat = center
\t\t\tvertical_alignment = center
\t\t\talwaystransparent = yes
\t\t}}
\t}}
}}
"""

# ─── HTTP сервер ────────────────────────────────────────────────────────────

class Handler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        p = urllib.parse.urlparse(self.path).path
        if p in ("/", "/index.html"):
            self.send_response(200)
            self.send_header("Content-type","text/html; charset=utf-8")
            self.end_headers()
            with open(os.path.join(MOD_DIR,"tools","intro_editor.html"),"rb") as f:
                self.wfile.write(f.read())
        elif p == "/api/get_data":
            self.send_response(200)
            self.send_header("Content-type","application/json")
            self.end_headers()
            self.wfile.write(json.dumps(parse_gui()).encode())
        elif p.startswith("/editor_assets/"):
            fp = os.path.join(ASSETS_DIR, p[len("/editor_assets/"):])
            if os.path.exists(fp):
                self.send_response(200)
                self.send_header("Content-type","image/png")
                self.end_headers()
                with open(fp,"rb") as f: self.wfile.write(f.read())
            else:
                self.send_response(404); self.end_headers()
        else:
            super().do_GET()

    def do_POST(self):
        if self.path == "/api/save":
            length = int(self.headers.get("Content-Length",0))
            data = json.loads(self.rfile.read(length).decode())
            code = generate_gui(data.get("elements",{}))
            with open(GUI_PATH,"w",encoding="utf-8") as f: f.write(code)
            self.send_response(200)
            self.send_header("Content-type","application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"status":"ok","message":"✅ gulyaipole_intro_custom.gui сохранён!"}).encode())
        else:
            self.send_response(404); self.end_headers()

    def log_message(self, fmt, *args):
        pass  # тихий режим

socketserver.TCPServer.allow_reuse_address = True
with socketserver.TCPServer(("", PORT), Handler) as srv:
    print(f"🚀 Редактор запущен → http://localhost:{PORT}")
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        print("Остановлен.")
