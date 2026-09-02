#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Интерактивная раскладка ветки тачанок в древе технологий HOI4 (infantry_folder).

Запуск:

    python3 tools/tech_tree_layout.py [--port 8712] [--host 0.0.0.0]

Что делает:
  * рисует схему ванильного древа пехоты в реальных пиксельных координатах
    (gridbox'ы берутся из interface/countrytechtreeview.gui, позиции технологий —
    из common/technologies/infantry.txt);
  * ветку тачанок (GLP_tachanka_tech_1..4) можно перетащить мышью или задать
    строку/столбец/шаг числами. Сетка — 70 px (слот gridbox'а);
  * кнопка «Сохранить» переписывает только `position = { x = .. y = .. }`
    внутри блоков folder у четырёх технологий в
    common/technologies/GLP_technologies.txt и запускает tools/glp_audit.py.

Ничего, кроме позиций в этом файле, инструмент не трогает.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TECH_FILE = os.path.join(ROOT, "common", "technologies", "GLP_technologies.txt")
TECH_IDS = ["GLP_tachanka_tech_1", "GLP_tachanka_tech_2",
            "GLP_tachanka_tech_3", "GLP_tachanka_tech_4"]

# ---------------------------------------------------------------------------
# Ванильная геометрия древа пехоты (HOI4 1.19).
#
# interface/countrytechtreeview.gui, контейнер infantry_folder:
#   slotsize = { width = 70 height = 70 }, format = "LEFT"
#     -> x в folder.position = строка вниз, y = столбец вправо, шаг 70 px.
# Все gridbox'ы имеют origin x = 140 и свою вертикаль (ниже).
# ---------------------------------------------------------------------------
SLOT = 70
ORIGIN_X = 140

GRIDBOX_Y = {                       # имя gridbox'а -> вертикаль origin
    "support_weapons_tree": 210,
    "night_vision_tree": 210,
    "infantry_weapons_tree": 325,
    "tech_trucks_tree": 620,        # сюда же наследуются броневики и тачанки
    "marines_tree": 825,
    "tech_mountaineers_tree": 925,
    "paratroopers_tree": 1025,
    "rangers_tech_tree": 1125,
    "tech_special_forces_tree": 1140,
}

# Заголовки секций (instantTextBoxType внутри techtree_stripes).
SECTIONS = [
    # x, y, ширина (оценка по длине текста), подпись
    (30, 100, 330, "INFANTRY_TITLE_WEAPONS — «Вооружение пехоты»"),
    (30, 510, 360, "INFANTRY_TITLE_MOTORISED — «Моторизованные войска»"),
    (40, 950, 330, "INFANTRY_TITLE_SPECIAL — «Специальные войска»"),
]

# Шапка лет: x подписи -> столбец (подпись стоит на 10 px левее ячейки).
YEAR_COLUMN = {
    1918: 0, 1924: 1, 1936: 2, 1938: 4, 1939: 6, 1940: 8,
    1941: 10, 1942: 12, 1943: 14, 1944: 16, 1945: 18, 1946: 20,
}


def year_to_column(year: int, fallback: int = 0) -> int:
    """Столбец для записи `y = @year` из ванильных файлов технологий."""
    if year <= 1918:
        return 0
    if year <= 1924:
        return 1
    if year <= 1938:
        return 2 + (year - 1936)
    return 6 + 2 * (year - 1939)


# Ванильные технологии: (gridbox, подпись, строка x, столбец y)
# Для столбцов вида @year указан год, для «до 1918» — явный столбец -1.
VANILLA_TECHS = [
    # --- моторизованная ветка + броневики (один gridbox) ---
    ("tech_trucks_tree", "Грузовики", 0, "col", -1),
    ("tech_trucks_tree", "Мотопехота", 0, "year", 1936),
    ("tech_trucks_tree", "Механизация 1", 0, "year", 1940),
    ("tech_trucks_tree", "Механизация 2", 0, "year", 1942),
    ("tech_trucks_tree", "Механизация 3", 0, "year", 1944),
    ("tech_trucks_tree", "Амфибии 1", 2, "year", 1941),
    ("tech_trucks_tree", "Амфибии 2", 2, "year", 1943),
    ("tech_trucks_tree", "Бронеавтомобиль 1", 4, "year", 1924),
    ("tech_trucks_tree", "Бронеавтомобиль 2", 4, "year", 1940),
    ("tech_trucks_tree", "Бронеавтомобиль 3", 4, "year", 1942),
    # --- спецвойска ---
    ("marines_tree", "Морская пехота 1", 3, "year", 1936),
    ("marines_tree", "Морская пехота 2", 3, "year", 1939),
    ("marines_tree", "Морская пехота 3", 3, "year", 1943),
    ("tech_mountaineers_tree", "Горные стрелки 1", 5, "year", 1936),
    ("tech_mountaineers_tree", "Горные стрелки 2", 5, "year", 1939),
    ("tech_mountaineers_tree", "Горные стрелки 3", 5, "year", 1943),
    ("paratroopers_tree", "Парашютисты 1", 2, "year", 1936),
    ("paratroopers_tree", "Парашютисты 2", 2, "year", 1939),
    ("paratroopers_tree", "Парашютисты 3", 2, "year", 1943),
    ("rangers_tech_tree", "Рейнджеры 1", 4, "year", 1936),
    ("rangers_tech_tree", "Рейнджеры 2", 4, "year", 1939),
    ("rangers_tech_tree", "Рейнджеры 3", 4, "year", 1943),
    ("tech_special_forces_tree", "Спецназ", 6, "year", 1938),
    ("tech_special_forces_tree", "Улучш. спецназ", 5, "year", 1940),
    ("tech_special_forces_tree", "Спецназ: выживание", 7, "year", 1940),
    ("tech_special_forces_tree", "Экстрим-подготовка", 5, "year", 1942),
    ("tech_special_forces_tree", "Выживание", 7, "year", 1942),
    ("tech_special_forces_tree", "Элитные войска", 6, "year", 1944),
    # --- вооружение (верх древа, для ориентира) ---
    ("infantry_weapons_tree", "Стрелковое оружие", 0, "col", -1),
    ("infantry_weapons_tree", "Стрелковое оружие II", 0, "year", 1938),
    ("infantry_weapons_tree", "Стрелковое оружие III", 0, "year", 1942),
    ("support_weapons_tree", "Поддержка 1918", 0, "year", 1918),
    ("support_weapons_tree", "Поддержка II", 0, "year", 1938),
]


def vanilla_boxes() -> list[dict]:
    boxes = []
    for tree, label, row, kind, value in VANILLA_TECHS:
        col = value if kind == "col" else year_to_column(value)
        boxes.append({
            "label": label,
            "x": ORIGIN_X + col * SLOT,
            "y": GRIDBOX_Y[tree] + row * SLOT,
        })
    return boxes


def section_boxes() -> list[dict]:
    return [{"label": label, "x": x, "y": y, "w": w, "h": 40}
            for x, y, w, label in SECTIONS]


# ---------------------------------------------------------------------------
# Чтение/запись позиций ветки тачанок
# ---------------------------------------------------------------------------
POS_RE = re.compile(r"position\s*=\s*\{\s*x\s*=\s*(-?\d+)\s+y\s*=\s*(-?\d+)\s*\}")


def read_positions() -> dict:
    """Текущие (строка, столбец первой технологии, шаг) из файла технологий."""
    text = open(TECH_FILE, encoding="utf-8").read()
    rows, cols = [], []
    for tech_id in TECH_IDS:
        start = text.find("\n\t" + tech_id + " = {")
        if start < 0:
            raise SystemExit(f"не найдено определение технологии {tech_id}")
        match = POS_RE.search(text, start)
        if not match:
            raise SystemExit(f"у {tech_id} нет position в блоке folder")
        rows.append(int(match.group(1)))
        cols.append(int(match.group(2)))
    return {"row": rows[0], "col": cols[0], "step": cols[1] - cols[0]}


def write_positions(row: int, col: int, step: int) -> str:
    text = open(TECH_FILE, encoding="utf-8").read()
    for index, tech_id in enumerate(TECH_IDS):
        start = text.find("\n\t" + tech_id + " = {")
        if start < 0:
            raise SystemExit(f"не найдено определение технологии {tech_id}")
        match = POS_RE.search(text, start)
        if not match:
            raise SystemExit(f"у {tech_id} нет position в блоке folder")
        new = "position = { x = %d y = %d }" % (row, col + index * step)
        text = text[:match.start()] + new + text[match.end():]
    with open(TECH_FILE, "w", encoding="utf-8") as handle:
        handle.write(text)
    return text


def branch_boxes(row: int, col: int, step: int) -> list[dict]:
    names = ["Тачанка РПА", "Тачанка прорыва", "Броневик «Воля»", "Броневик «Батько»"]
    return [{"label": names[i],
             "x": ORIGIN_X + (col + i * step) * SLOT,
             "y": GRIDBOX_Y["tech_trucks_tree"] + row * SLOT}
            for i in range(len(TECH_IDS))]


def collisions(row: int, col: int, step: int, pad: int = 6) -> list[str]:
    rects = branch_boxes(row, col, step)
    for rect in rects:
        rect["w"] = rect["h"] = SLOT
    others = vanilla_boxes() + section_boxes()
    for other in others:
        other.setdefault("w", SLOT)
        other.setdefault("h", SLOT)
    problems = []
    for rect in rects:
        for other in others:
            if (rect["x"] - pad < other["x"] + other["w"] and
                    other["x"] - pad < rect["x"] + rect["w"] and
                    rect["y"] - pad < other["y"] + other["h"] and
                    other["y"] - pad < rect["y"] + rect["h"]):
                problems.append(f"«{rect['label']}» пересекается с «{other['label']}»")
    return sorted(set(problems))


def run_audit() -> str:
    try:
        done = subprocess.run([sys.executable, os.path.join("tools", "glp_audit.py")],
                              cwd=ROOT, capture_output=True, text=True, timeout=600)
    except Exception as exc:                                   # pragma: no cover
        return f"аудит не запустился: {exc}"
    output = (done.stdout or "") + (done.stderr or "")
    lines = [line for line in output.splitlines() if line.strip()]
    return "\n".join(lines[-12:])


# ---------------------------------------------------------------------------
# Веб-интерфейс
# ---------------------------------------------------------------------------
PAGE = r"""<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="utf-8">
<title>Раскладка ветки тачанок — infantry_folder</title>
<style>
  :root { --bg:#14161a; --panel:#1d2127; --line:#2b313a; --txt:#dfe4ea; --muted:#9aa4b2; --glp:#e0a53f; }
  * { box-sizing: border-box; }
  body { margin:0; background:var(--bg); color:var(--txt); font:14px/1.45 "Segoe UI", system-ui, sans-serif; }
  header { padding:14px 18px; border-bottom:1px solid var(--line); background:var(--panel); }
  header h1 { margin:0 0 4px; font-size:17px; }
  header p { margin:0; color:var(--muted); font-size:12.5px; }
  main { display:flex; gap:16px; padding:16px; align-items:flex-start; }
  aside { width:330px; flex:0 0 330px; background:var(--panel); border:1px solid var(--line);
          border-radius:10px; padding:14px; }
  aside h2 { font-size:14px; margin:0 0 10px; text-transform:uppercase; letter-spacing:.04em; color:var(--muted); }
  .field { display:flex; align-items:center; justify-content:space-between; margin-bottom:8px; gap:8px; }
  .field label { font-size:13px; }
  .field input { width:78px; padding:4px 6px; background:#12151a; color:var(--txt);
                 border:1px solid var(--line); border-radius:6px; text-align:right; }
  .presets button, .actions button { display:block; width:100%; margin-bottom:6px; padding:8px 10px;
      background:#232a33; color:var(--txt); border:1px solid var(--line); border-radius:7px;
      cursor:pointer; text-align:left; font-size:13px; }
  .presets button:hover, .actions button:hover { border-color:var(--glp); }
  .actions button.primary { background:#3a2f14; border-color:var(--glp); color:#ffd98a; font-weight:600; }
  pre { background:#12151a; border:1px solid var(--line); border-radius:8px; padding:10px;
        font-size:12px; white-space:pre-wrap; margin:10px 0 0; }
  #warn { margin-top:10px; font-size:12.5px; color:#ff8f6b; min-height:18px; }
  #status { margin-top:8px; font-size:12.5px; color:#8fd18a; white-space:pre-wrap; min-height:18px; }
  .canvas-wrap { flex:1 1 auto; overflow:auto; max-height:82vh; background:#0f1115;
                 border:1px solid var(--line); border-radius:10px; }
  svg { display:block; }
  .hint { color:var(--muted); font-size:12px; margin-top:10px; }
  .legend { display:flex; gap:14px; flex-wrap:wrap; color:var(--muted); font-size:12px; margin-bottom:10px; }
  .legend i { display:inline-block; width:12px; height:12px; border-radius:3px; margin-right:5px; vertical-align:-1px; }
</style>
</head>
<body>
<header>
  <h1>Ветка тачанок в древе пехоты — раскладка</h1>
  <p>Сетка 70 px (слот gridbox'а <code>tech_trucks_tree</code>, origin 140×620). Перетащите жёлтую ветку мышью или задайте строку/столбец вручную, затем сохраните.</p>
</header>
<main>
  <aside>
    <h2>Позиция</h2>
    <div class="field"><label>Строка (x)</label><input id="row" type="number" step="1"></div>
    <div class="field"><label>Столбец 1-й тех. (y)</label><input id="col" type="number" step="1"></div>
    <div class="field"><label>Шаг между технологиями</label><input id="step" type="number" step="1" min="1" max="8"></div>
    <div class="legend">
      <span><i style="background:#e0a53f"></i>тачанки</span>
      <span><i style="background:#3b434f"></i>ванильные техи</span>
      <span><i style="background:#5b5320"></i>заголовки секций</span>
    </div>
    <h2>Быстрый выбор</h2>
    <div class="presets">
      <button data-row="4"  data-col="24" data-step="3">Текущая: строка броневиков (4)</button>
      <button data-row="6"  data-col="24" data-step="3">Под броневиками, ниже «Спецвойск» (6)</button>
      <button data-row="16" data-col="2"  data-step="3">Под всем блоком спецвойск (16)</button>
      <button data-row="6"  data-col="16" data-step="3">Под броневиками, в видимой зоне (6)</button>
    </div>
    <h2>Сохранение</h2>
    <div class="actions">
      <button class="primary" id="save">Сохранить в GLP_technologies.txt</button>
      <button id="reset">Сбросить к сохранённому</button>
    </div>
    <pre id="code"></pre>
    <div id="warn"></div>
    <div id="status"></div>
    <p class="hint">Сервер пишет только блоки <code>position = {…}</code> четырёх технологий
    <code>GLP_tachanka_tech_1..4</code>, затем запускает <code>tools/glp_audit.py</code>.</p>
  </aside>
  <div class="canvas-wrap"><svg id="canvas" xmlns="http://www.w3.org/2000/svg"></svg></div>
</main>
<script>
const SLOT = 70, OX = 140, OY = 620;
const VANILLA = __VANILLA__;
const SECTIONS = __SECTIONS__;
const YEAR_COLUMN = __YEARS__;
const CANVAS_W = 2700, CANVAS_H = 1950;
const START = __START__;

let state = { row: START.row, col: START.col, step: START.step };

const svg = document.getElementById('canvas');
const rowIn = document.getElementById('row');
const colIn = document.getElementById('col');
const stepIn = document.getElementById('step');
const codeEl = document.getElementById('code');
const warnEl = document.getElementById('warn');
const statusEl = document.getElementById('status');

function box(i) {
  const col = state.col + i * state.step;
  return { x: OX + col * SLOT, y: OY + state.row * SLOT };
}
function rectHit(a, b, pad) {
  const aw = a.w || SLOT, ah = a.h || SLOT, bw = b.w || SLOT, bh = b.h || SLOT;
  return a.x - pad < b.x + bw && b.x - pad < a.x + aw && a.y - pad < b.y + bh && b.y - pad < a.y + ah;
}

function background() {
  let out = '';
  for (let y = 0; y <= CANVAS_H; y += SLOT) {
    out += `<line x1="0" y1="${y}" x2="${CANVAS_W}" y2="${y}" stroke="#1b2027" stroke-width="1"/>`;
  }
  for (let x = OX; x <= CANVAS_W; x += SLOT) {
    out += `<line x1="${x}" y1="0" x2="${x}" y2="${CANVAS_H}" stroke="#191d24" stroke-width="1"/>`;
  }
  for (const [year, col] of Object.entries(YEAR_COLUMN)) {
    const x = OX + col * SLOT;
    out += `<line x1="${x}" y1="0" x2="${x}" y2="${CANVAS_H}" stroke="#2a3340" stroke-width="1.5" stroke-dasharray="6 8"/>`;
    out += `<text x="${x + 6}" y="26" fill="#7f8b9c" font-size="22">${year}</text>`;
  }
  // зона фоновой картинки древа (1400x1275)
  out += `<rect x="0" y="0" width="1400" height="1275" fill="none" stroke="#39424f" stroke-width="2" stroke-dasharray="4 6"/>`;
  out += `<text x="8" y="1265" fill="#4d5766" font-size="18">фон древа 1400×1275</text>`;
  return out;
}

function drawVanilla() {
  let out = '';
  for (const b of VANILLA) {
    out += `<rect x="${b.x + 3}" y="${b.y + 3}" width="${SLOT - 6}" height="${SLOT - 6}" rx="8"
             fill="#3b434f" stroke="#4a5563" stroke-width="1"/>`;
    out += `<text x="${b.x + SLOT / 2}" y="${b.y + SLOT / 2 + 4}" fill="#c3ccd8" font-size="12"
             text-anchor="middle">${b.label}</text>`;
  }
  for (const s of SECTIONS) {
    out += `<rect x="${s.x}" y="${s.y}" width="${s.w}" height="${s.h}" rx="6" fill="#5b5320"
             fill-opacity="0.35" stroke="#8f8430" stroke-width="1.5" stroke-dasharray="5 4"/>`;
    out += `<text x="${s.x + 6}" y="${s.y + 26}" fill="#e3d08a" font-size="17">${s.label}</text>`;
  }
  return out;
}

function drawBranch() {
  const boxes = [0, 1, 2, 3].map(i => box(i));
  const names = ['Тачанка РПА', 'Тачанка прорыва', 'Броневик «Воля»', 'Броневик «Батько»'];
  let out = '';
  // связь от «Грузовиков» (строка 0, столбец -1) к первой тачанке
  const trucks = { x: OX - SLOT, y: OY };
  out += `<polyline points="${trucks.x + SLOT},${trucks.y + SLOT / 2} ${boxes[0].x + SLOT / 2},${boxes[0].y + SLOT / 2}"
           fill="none" stroke="#7a6a3a" stroke-width="3" stroke-dasharray="10 7"/>`;
  for (let i = 0; i < 3; i++) {
    const a = boxes[i], b = boxes[i + 1];
    out += `<line x1="${a.x + SLOT}" y1="${a.y + SLOT / 2}" x2="${b.x}" y2="${b.y + SLOT / 2}"
             stroke="#e0a53f" stroke-width="4"/>`;
  }
  boxes.forEach((b, i) => {
    out += `<g class="node" data-i="${i}">
      <rect x="${b.x + 2}" y="${b.y + 2}" width="${SLOT - 4}" height="${SLOT - 4}" rx="9"
            fill="#e0a53f" fill-opacity="0.28" stroke="#e0a53f" stroke-width="2.5"/>
      <text x="${b.x + SLOT / 2}" y="${b.y + SLOT / 2 - 2}" fill="#ffd98a" font-size="12"
            text-anchor="middle">${names[i]}</text>
      <text x="${b.x + SLOT / 2}" y="${b.y + SLOT / 2 + 14}" fill="#c9a45c" font-size="11"
            text-anchor="middle">x=${state.row} y=${state.col + i * state.step}</text>
    </g>`;
  });
  return out;
}

function update() {
  rowIn.value = state.row; colIn.value = state.col; stepIn.value = state.step;
  svg.setAttribute('viewBox', `0 0 ${CANVAS_W} ${CANVAS_H}`);
  svg.setAttribute('width', CANVAS_W * 0.62);
  svg.setAttribute('height', CANVAS_H * 0.62);
  svg.innerHTML = background() + drawVanilla() + `<g id="branch">${drawBranch()}</g>`;

  const boxes = [0, 1, 2, 3].map(i => ({ ...box(i), label: 'тачанка ' + (i + 1) }));
  const problems = [];
  for (const b of boxes) {
    for (const other of [...VANILLA, ...SECTIONS]) {
      if (rectHit(b, other, 6)) problems.push(`«${b.label}» накладывается на «${other.label}»`);
    }
  }
  warnEl.textContent = problems.length ? '⚠ ' + [...new Set(problems)].join('; ') : '';
  codeEl.textContent = ['GLP_tachanka_tech_1', 'GLP_tachanka_tech_2', 'GLP_tachanka_tech_3', 'GLP_tachanka_tech_4']
    .map((id, i) => `${id}\n\tfolder = {\n\t\tname = infantry_folder\n\t\tposition = { x = ${state.row} y = ${state.col + i * state.step} }\n\t}`)
    .join('\n\n');
  bindDrag();
}

const drag = { active: false, pt: null, start: null };

function toSvg(evt) {
  const pt = svg.createSVGPoint();
  pt.x = evt.clientX; pt.y = evt.clientY;
  return pt.matrixTransform(svg.getScreenCTM().inverse());
}

// Слушатели на window вешаются один раз, иначе они копятся при каждой
// перерисовке ветки.
window.addEventListener('mousemove', evt => {
  if (!drag.active) return;
  const pt = toSvg(evt);
  const dRow = Math.round((pt.y - drag.pt.y) / SLOT);
  const dCol = Math.round((pt.x - drag.pt.x) / SLOT);
  state.row = Math.max(0, Math.min(40, drag.start.row + dRow));
  state.col = drag.start.col + dCol;
  update();
});
window.addEventListener('mouseup', () => { drag.active = false; });

function bindDrag() {
  const group = document.getElementById('branch');
  if (!group) return;
  group.style.cursor = 'grab';
  group.addEventListener('mousedown', evt => {
    drag.active = true; drag.pt = toSvg(evt); drag.start = { ...state };
    evt.preventDefault();
  });
}

[rowIn, colIn, stepIn].forEach(el => el.addEventListener('input', () => {
  state.row = parseInt(rowIn.value || '0', 10);
  state.col = parseInt(colIn.value || '0', 10);
  state.step = Math.min(8, Math.max(1, parseInt(stepIn.value || '1', 10)));
  update();
}));
document.querySelectorAll('.presets button').forEach(btn => btn.addEventListener('click', () => {
  state = { row: +btn.dataset.row, col: +btn.dataset.col, step: +btn.dataset.step };
  update();
  statusEl.textContent = '';
}));
document.getElementById('reset').addEventListener('click', async () => {
  const res = await fetch('/api/state').then(r => r.json());
  state = { row: res.row, col: res.col, step: res.step };
  statusEl.textContent = 'Загружено сохранённое значение.';
  update();
});
document.getElementById('save').addEventListener('click', async () => {
  statusEl.textContent = 'Сохраняю…';
  const res = await fetch('/api/save', {
    method: 'POST', headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(state),
  }).then(r => r.json());
  statusEl.textContent = res.ok
    ? `Сохранено: строка ${state.row}, столбцы ${[0, 1, 2, 3].map(i => state.col + i * state.step).join('/')}\n\nАудит:\n${res.audit}`
    : 'Ошибка: ' + res.error;
});
update();
</script>
</body>
</html>
"""


class Handler(BaseHTTPRequestHandler):
    server_version = "GLPTechTreeLayout/1.0"

    def _send(self, body: bytes, ctype: str, code: int = 200) -> None:
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def _json(self, payload: dict, code: int = 200) -> None:
        self._send(json.dumps(payload).encode("utf-8"), "application/json; charset=utf-8", code)

    def do_GET(self) -> None:                                  # noqa: N802
        if self.path.startswith("/api/state"):
            self._json(read_positions())
            return
        years = {str(year): col for year, col in YEAR_COLUMN.items()}
        page = (PAGE
                .replace("__VANILLA__", json.dumps(vanilla_boxes(), ensure_ascii=False))
                .replace("__SECTIONS__", json.dumps(section_boxes(), ensure_ascii=False))
                .replace("__YEARS__", json.dumps(years))
                .replace("__START__", json.dumps(read_positions())))
        self._send(page.encode("utf-8"), "text/html; charset=utf-8")

    def do_POST(self) -> None:                                 # noqa: N802
        if not self.path.startswith("/api/save"):
            self._json({"ok": False, "error": "unknown endpoint"}, 404)
            return
        length = int(self.headers.get("Content-Length", "0"))
        try:
            data = json.loads(self.rfile.read(length) or b"{}")
            row = int(data.get("row"))
            col = int(data.get("col"))
            step = int(data.get("step"))
        except Exception as exc:
            self._json({"ok": False, "error": f"плохие данные: {exc}"})
            return
        if not (0 <= row <= 40 and -2 <= col <= 60 and 1 <= step <= 8):
            self._json({"ok": False, "error": "значения вне диапазона"})
            return
        try:
            write_positions(row, col, step)
        except Exception as exc:
            self._json({"ok": False, "error": str(exc)})
            return
        self._json({"ok": True, "audit": run_audit()})

    def log_message(self, fmt: str, *args) -> None:
        sys.stderr.write("[tech_tree_layout] " + (fmt % args) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=8712)
    args = parser.parse_args()

    server = ThreadingHTTPServer((args.host, args.port), Handler)
    print(f"раскладка ветки тачанок: http://{args.host}:{args.port}/")
    print(f"файл технологий: {TECH_FILE}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
