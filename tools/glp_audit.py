#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GLP mod audit  -- HOI4 1.19.2 compliance checker.

Checks performed:
  1. Brace balance / basic syntax of every .txt / .gfx script.
  2. Localisation: UTF-8 BOM, "l_<lang>:" header, duplicate keys,
     key parity between russian and english, and balanced quotes in every
     value (an unescaped " inside a value truncates the string and the game
     prints ???????).
  3. Missing localisation for characters, custom leader traits, ideas,
     idea tokens (advisors), national focuses, events.
  4. Duplicate definitions: character ids, advisor idea_token, idea names,
     focus ids, leader trait names, sprite names  (a classic 1.19.2
     "scenario fails to load / checksum" crash source).
  5. Sprite integrity: every GFX_* referenced by script is defined,
     every texturefile on a spriteType exists on disk.
  6. Portrait/event/idea/loading-panel DDS geometry, compression and alpha.
  7. Every national spirit uses a thematic GFX_idea_GLP_* icon and exactly
     matches tools/idea_pictures.tsv.
  8. Loading quote geometry/font (vanilla tip window 1024x200, CENTER_DOWN,
     loadscreen_tip) and continuous-focus palette centring/safe gap below the focus tree.
  9. Custom cavalry/cossack models from Rise of Russia must be present
     (GLP_units.*, DON_cavalry -- Don Cossack rider --, sabre, sabre anims) and
     wired as tag-specific GLP_cavalry_entity / GLP_cavalry_2_entity without
     cloning vanilla cavalry entities; every mesh's embedded .dds deps resolve.
 10. Character traits that are neither vanilla nor defined by the mod.
 11. Anti-pattern `check_variable = { random ... }` in common/events/history.
 12. Every focus carries generic `search_filters` matching
     tools/focus_search_filters.tsv, so the whole tree stays visible in the
     in-game focus search/filter panel.
 13. Branch banner comments in GLP_focus.txt state the real focus count and
     the real x/y envelope (tools/sync_focus_headers.py keeps them honest).
 14. Idea modifier keys are spelled with real 1.19 static-modifier names
    (an unknown key is silently ignored by the engine, so the buff just
    never happens).
 15. Crisis-event integrity: every glp_crisis.* id is actually triggered
    (referenced in some focus / on_action / event), every retire/retire_char
    call sits behind a has_character guard (silent error otherwise), and
    step-1/2/3 chains clean their set_country_flag / clr_country_flag pairs.
 16. Division template icons match the branch the template name (and its
     division_names_group) promises: every template_counter is registered in
     tools/division_icons.tsv, and the icon the engine would draw (highest
     priority line battalion, per vanilla `priority`) equals the branch of the
     name.  Cavalry divisions that carry a light_armor battalion otherwise
     show a TANK silhouette (priority 2501 vs 599) -- hence template_counter
     92 and tools/division_icons.tsv.  A branch tile must be BASE GAME art
     (gfx/interface/counters/divisions_{large,small}/unit_<branch>_icon.dds);
     only `depicts = flag` may ship its own 76x42 / 30x12 dds.
     Also: each entry of a division-names group must mention a branch its own
     division_types allow.
 17. Advisors are complete: every idea_token of common/characters resolves to
     an idea in common/ideas whose category equals the advisor slot (an idea
     that does not exist == an advisor with zero bonuses), the slot is a real
     vanilla High Command slot, traits resolve to vanilla-or-mod traits, the
     idea grants at least one modifier, and hiring gates in the characters
     block and in the idea agree.
 18. The custom tachanka technology contract uses current 1.19 keys, is
     restricted to GLP, creates valid GLP-only division templates, has a real
     incoming path/gridbox anchor, uses a transport equipment archetype, and
     resolves cavalry designer/map icons and equipment combat stats.
Exit code 0 = clean, 1 = errors found.  Warnings never fail the build.
"""
import hashlib
import os
import re
import struct
import sys
from collections import defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Paths that live in the base game, not in the mod -- referencing them is fine.
VANILLA_TEXTURES = {
    'gfx/interface/goals/shine_overlay.dds',
    # Ванильные силуэты родов войск для контр-фишек дивизий. Мод намеренно
    # НЕ рисует свою иконку кавалерии: template_counter 92 указывает на эти
    # файлы базовой игры (см. tools/division_icons.tsv и раздел 16).
    'gfx/interface/counters/divisions_large/unit_cavalry_icon.dds',
    'gfx/interface/counters/divisions_small/onmap_unit_cavalry_icon.dds',
    'gfx/FX/buttonstate.lua',
    'gfx//interface//thisisdog.dds',
    'gfx/interface/pdx_dev_logo_s.dds',
    'gfx/interface/Loadingscreen_loadingstatus.dds',
    'gfx/interface/Loadingscreen_loadingtip.dds',
    'gfx/interface/pdx_int_logo.dds',
    'gfx/interface/clausewitz_logo.dds',
    'gfx//interface//LoadingScreen_Progress_2.dds',
    'gfx//interface//LoadingScreen_Progress_1.dds',
    'gfx//FX//progress.lua',
}

ERRORS = []
WARNINGS = []


def err(msg):
    ERRORS.append(msg)


def warn(msg):
    WARNINGS.append(msg)


def walk(subdir, exts):
    base = os.path.join(ROOT, subdir)
    for dirpath, _dirs, files in os.walk(base):
        for f in sorted(files):
            if f.lower().endswith(exts):
                yield os.path.join(dirpath, f)


def rel(p):
    return os.path.relpath(p, ROOT)


def read(p):
    with open(p, 'rb') as fh:
        raw = fh.read()
    if raw.startswith(b'\xef\xbb\xbf'):
        raw = raw[3:]
    return raw.decode('utf-8', 'replace')


def strip_comments(text):
    out = []
    for line in text.split('\n'):
        res = []
        in_str = False
        for ch in line:
            if ch == '"':
                in_str = not in_str
            if ch == '#' and not in_str:
                break
            res.append(ch)
        out.append(''.join(res))
    return '\n'.join(out)


# ---------------------------------------------------------------- 1. syntax
SCRIPT_DIRS = (
    ('common', ('.txt', '.gfx', '.gui')),
    ('events', ('.txt', '.gfx', '.gui')),
    ('history', ('.txt', '.gfx', '.gui')),
    ('interface', ('.txt', '.gfx', '.gui')),
    # 3D unit declarations are Clausewitz script too.  A missing brace in
    # either directory silently prevents models from loading in HOI4.
    ('gfx/entities', ('.gfx', '.asset')),
    ('gfx/models/units', ('.asset',)),
)


def check_syntax():
    for d, exts in SCRIPT_DIRS:
        for p in walk(d, exts):
            body = strip_comments(read(p))
            depth = 0
            for i, line in enumerate(body.split('\n'), 1):
                depth += line.count('{') - line.count('}')
                if depth < 0:
                    err(f"{rel(p)}:{i}: unbalanced '}}' (depth < 0)")
                    break
            if depth > 0:
                err(f"{rel(p)}: {depth} unclosed '{{' at end of file")
            if '\ufffd' in body:
                warn(f"{rel(p)}: contains invalid UTF-8 bytes")

            # Clausewitz не всегда сообщает понятную ошибку для опечатки
            # вроде `position = { y = 1s }`: окно просто получает неверную
            # геометрию. Координаты и размеры допускают число, процент или
            # выражение, но не число с буквенным суффиксом.
            for i, line in enumerate(body.split('\n'), 1):
                if ('position' in line or 'size' in line) and re.search(
                        r'\b[xy]\s*=\s*-?\d+(?:\.\d+)?[A-Za-z_]+\b', line):
                    err(f"{rel(p)}:{i}: malformed UI coordinate or size value")


# --------------------------------------------------------- 2/3. localisation
LOC_LINE = re.compile(r'^\s*([A-Za-z0-9_.\-]+):\s*\d+\s*"')
# Похоже на ключ локализации, но БЕЗ номера версии («key: "..."» вместо
# «key:0 "..."») — HOI4 такие строки молча игнорирует, в игре будет ???????.
LOC_NOVER = re.compile(r'^\s*([A-Za-z0-9_.\-]+):\s*(?!\d)(?!=)\s*"')


def load_loc():
    langs = {}
    for p in walk('localisation', ('.yml',)):
        parts = rel(p).split(os.sep)
        lang = parts[1] if len(parts) > 1 and parts[1] in ('russian', 'english') else os.path.basename(os.path.dirname(p))
        is_replace = 'replace' in parts
        with open(p, 'rb') as fh:
            raw = fh.read()
        if not raw.startswith(b'\xef\xbb\xbf'):
            err(f"{rel(p)}: missing UTF-8 BOM (HOI4 will not load this file)")
        text = raw.decode('utf-8-sig', 'replace')
        lines = text.split('\n')
        if not lines or not lines[0].strip().startswith(f'l_{lang}:'):
            err(f"{rel(p)}: first line must be 'l_{lang}:'")
        seen = {}
        for i, line in enumerate(lines, 1):
            if LOC_NOVER.match(line):
                err(f"{rel(p)}:{i}: строка локализации без номера версии "
                    f"(HOI4 её не загрузит, в игре будет ???????): {line.strip()[:60]}")
                continue
            m = LOC_LINE.match(line)
            if not m:
                continue
            k = m.group(1)
            if k in seen and not is_replace:
                err(f"{rel(p)}:{i}: duplicate localisation key '{k}' "
                    f"(first at line {seen[k]})")
            seen[k] = i
            # Значение обязано быть одной целой строкой: неэкранированная "
            # внутри обрывает строку, и движок покажет ??????? вместо текста
            # (класс поломки из итерации 6; аудит поймал её на новых
            # *_advisor_desc, где кавычки стояли внутри значения).
            # m заканчивается на открывающей кавычке значения
            value = line[m.end():].replace('\\"', '')
            if value.count('"') != 1:
                err(f"{rel(p)}:{i}: локализация «{k}» — кавычки значения не "
                    "сбалансированы: движок оборвёт строку и покажет ??????? "
                    "вместо текста; внутренние кавычки нужно экранировать "
                    "или убрать из значения")
            langs.setdefault(lang, {})[k] = rel(p)
    return langs


# ------------------------------------------------------------- script parses
def all_script_text(subdir):
    chunks = {}
    for p in walk(subdir, ('.txt',)):
        chunks[p] = strip_comments(read(p))
    return chunks


def collect_definitions():
    defs = defaultdict(lambda: defaultdict(list))  # kind -> name -> [where]

    # characters + advisors
    for p, body in all_script_text('common/characters').items():
        for m in re.finditer(r'^\t([A-Za-z0-9_]+)\s*=\s*\{', body, re.M):
            defs['character'][m.group(1)].append(rel(p))
        for m in re.finditer(r'idea_token\s*=\s*([A-Za-z0-9_]+)', body):
            defs['idea_token'][m.group(1)].append(rel(p))
        for m in re.finditer(r'\bid\s*=\s*(-?\d+)', body):
            if m.group(1) != '-1':
                defs['character_id'][m.group(1)].append(rel(p))

    # leader / unit traits
    for p, body in all_script_text('common/country_leader').items():
        for m in re.finditer(r'^\t([A-Za-z0-9_]+)\s*=\s*\{', body, re.M):
            defs['trait'][m.group(1)].append(rel(p))
    for p, body in all_script_text('common/unit_leader').items():
        for m in re.finditer(r'^\t([A-Za-z0-9_]+)\s*=\s*\{', body, re.M):
            defs['trait'][m.group(1)].append(rel(p))

    # ideas (country / advisor slots)
    for p, body in all_script_text('common/ideas').items():
        for m in re.finditer(r'^\t\t([A-Za-z0-9_]+)\s*=\s*\{', body, re.M):
            defs['idea'][m.group(1)].append(rel(p))

    # focuses (skip the tree id itself and event ids such as glp_news.3)
    for p, body in all_script_text('common/national_focus').items():
        tree_ids = set(re.findall(r'focus_tree\s*=\s*\{\s*id\s*=\s*([A-Za-z0-9_]+)', body))
        for m in re.finditer(r'\bid\s*=\s*([A-Za-z0-9_]+)(?![\w.])', body):
            fid = m.group(1)
            if fid in tree_ids:
                continue
            defs['focus'][fid].append(rel(p))

    # events
    for p in walk('events', ('.txt',)):
        body = strip_comments(read(p))
        for m in re.finditer(r'^\s*id\s*=\s*([A-Za-z0-9_]+\.\d+)', body, re.M):
            defs['event'][m.group(1)].append(rel(p))

    # sprites
    for p in walk('interface', ('.gfx',)):
        body = strip_comments(read(p))
        for m in re.finditer(r'name\s*=\s*"?(GFX_[A-Za-z0-9_]+)"?', body):
            defs['sprite'][m.group(1)].append(rel(p))
    return defs


def check_duplicates(defs):
    human = {
        'character': 'character',
        'idea_token': 'advisor idea_token',
        'character_id': 'hard-coded character id',
        'trait': 'leader trait',
        'idea': 'idea / national spirit',
        'focus': 'national focus id',
        'event': 'event id',
        'sprite': 'sprite (spriteType name)',
    }
    for kind, table in defs.items():
        for name, places in table.items():
            if len(places) > 1:
                err(f"duplicate {human.get(kind, kind)} '{name}' defined "
                    f"{len(places)}x in: {', '.join(sorted(set(places)))}")


# -------------------------------------------------------------- 5. sprites
def check_sprites(defs):
    defined = set(defs['sprite'])
    # texture files exist?
    for p in walk('interface', ('.gfx',)):
        body = strip_comments(read(p))
        for m in re.finditer(r'texturefile\s*=\s*"?([^"\s]+)"?', body):
            tex = m.group(1).replace('\\', '/')
            if tex in VANILLA_TEXTURES:
                continue
            if not os.path.exists(os.path.join(ROOT, tex)):
                err(f"{rel(p)}: texturefile not found on disk -> {tex}")
    # referenced sprites exist?  (only GFX_ names our mod owns: GLP)
    refs = defaultdict(set)
    for d in ('common', 'events', 'interface'):
        for p in walk(d, ('.txt', '.gfx')):
            body = strip_comments(read(p))
            for m in re.finditer(r'"?(GFX_[A-Za-z0-9_]*GLP[A-Za-z0-9_]*)"?', body):
                refs[m.group(1)].add(rel(p))
    for name, places in sorted(refs.items()):
        if name not in defined:
            err(f"sprite '{name}' referenced by {', '.join(sorted(places))} "
                f"but never defined in interface/*.gfx")
    for name in sorted(defined):
        if 'GLP' in name and name not in refs:
            warn(f"sprite '{name}' defined but never referenced")


# ------------------------------------------------------------ 6. dds geometry
def dds_info(path):
    with open(path, 'rb') as fh:
        head = fh.read(128)
    if head[:4] != b'DDS ':
        return None
    h = struct.unpack('<I', head[12:16])[0]
    w = struct.unpack('<I', head[16:20])[0]
    fourcc = head[84:88].decode('ascii', 'replace').strip('\x00') or 'ARGB8888'
    return w, h, fourcc


SPEC_LARGE = (156, 210)   # оффиціальный размѣръ портрета лидера/генерала
SPEC_MEDIUM = (88, 119)   # списокъ генераловъ (оффиціальный размѣръ)
SPEC_SMALL = (65, 67)     # ячейка совѣтника/идеи (квадратная)
SPEC_SCREEN = (1920, 1080)
OK_FMT_LARGE = ('ARGB8888', 'DXT5')
OK_FMT_SMALL = ('DXT5', 'ARGB8888')
OK_FMT_SCREEN = ('DXT1', 'DXT5')


def check_portraits():
    for p in walk('gfx/leaders', ('.dds',)):
        info = dds_info(p)
        if not info:
            err(f"{rel(p)}: not a valid DDS file")
            continue
        w, h, fmt = info
        base = os.path.basename(p)
        if base.endswith('_large.dds'):
            want, ok = SPEC_LARGE, OK_FMT_LARGE
        else:
            want, ok = SPEC_MEDIUM, OK_FMT_SMALL   # Portrait_GLP_<Name>.dds = medium
        if (w, h) != want:
            err(f"{rel(p)}: {w}x{h}, spec requires {want[0]}x{want[1]}")
        if fmt not in ok:
            err(f"{rel(p)}: compression {fmt}, spec requires {' or '.join(ok)}")
    for p in walk('gfx/interface/ideas', ('.dds',)):
        info = dds_info(p)
        if not info:
            err(f"{rel(p)}: not a valid DDS file")
            continue
        w, h, _fmt = info
        if re.search(r'idea_GLP_[A-Z]', os.path.basename(p)):
            if (w, h) != SPEC_SMALL:
                err(f"{rel(p)}: advisor icon is {w}x{h}, spec requires 65x67")


def check_screens():
    """Загрузочные экраны: 1920x1080. Фон меню: 1920x1440 (эталон UI 4:3)."""
    # Фон меню — спрайт въ эталонномъ разрѣшеніи интерфейса HOI4 (1920x1440),
    # чтобы не «тянулся» по вертикали. Загрузочные экраны — 1920x1080.
    menu_bg = os.path.join(ROOT, 'gfx/interface/frontendmainviewbg.dds')
    for p in sorted(glob_dds('gfx/loadingscreens')):
        info = dds_info(p)
        if not info:
            err(f"{rel(p)}: not a valid DDS file")
            continue
        w, h, fmt = info
        if (w, h) != SPEC_SCREEN:
            err(f"{rel(p)}: {w}x{h}, spec requires 1920x1080")
        if fmt not in OK_FMT_SCREEN:
            err(f"{rel(p)}: compression {fmt}, spec requires DXT1 or DXT5")
    if os.path.exists(menu_bg):
        info = dds_info(menu_bg)
        if not info:
            err(f"{rel(menu_bg)}: not a valid DDS file")
        else:
            w, h, fmt = info
            if (w, h) != (1920, 1440):
                err(f"{rel(menu_bg)}: {w}x{h}, фон меню должен быть 1920x1440 "
                    f"(эталонное 4:3 разрѣшеніе UI, иначе тянется по высоте)")
            if fmt not in OK_FMT_SCREEN:
                err(f"{rel(menu_bg)}: compression {fmt}, spec requires DXT1 or DXT5")
    # replace_path="gfx/loadingscreens" въ descriptor.mod полностью исключаетъ
    # ваниль и DLC; наши 16 load_N.dds ссылаются на шесть экрановъ мода.
    desc = os.path.join(ROOT, 'descriptor.mod')
    if os.path.exists(desc):
        body = read(desc)
        if 'gfx/loadingscreens' not in body:
            warn("descriptor.mod: нет replace_path=\"gfx/loadingscreens\" — "
                 "ванильные/DLC экраны загрузки могут подмешиваться")
    missing = [n for n in range(1, 7)
               if not os.path.exists(os.path.join(ROOT, f'gfx/loadingscreens/load_{n}.dds'))]
    if missing:
        warn("экраны загрузки мода не выставлены: "
             + ', '.join(f'load_{n}.dds' for n in missing))


def check_focus_tree(defs):
    """Целостность дерева фокусов: ссылки, идеи, события, персонажи."""
    focus_ids = set(defs['focus'])
    idea_ids = set(defs['idea'])
    event_ids = set(defs['event'])
    char_ids = set(defs['character'])
    token_ids = set(defs['idea_token'])

    files = dict(all_script_text('common/national_focus'))
    files.update(all_script_text('common/decisions'))
    files.update(all_script_text('common/on_actions'))
    files.update(all_script_text('history/countries'))
    for p in walk('events', ('.txt',)):
        files[p] = strip_comments(read(p))

    positions = defaultdict(list)
    for p, body in files.items():
        # ссылки на другие фокусы
        for kw in ('prerequisite', 'mutually_exclusive'):
            for m in re.finditer(kw + r'\s*=\s*\{([^}]*)\}', body):
                for f in re.findall(r'focus\s*=\s*([A-Za-z0-9_]+)', m.group(1)):
                    if f not in focus_ids:
                        err(f"{rel(p)}: {kw} ссылается на несуществующий фокус '{f}'")
        for m in re.finditer(r'relative_position_id\s*=\s*([A-Za-z0-9_]+)', body):
            if m.group(1) not in focus_ids:
                err(f"{rel(p)}: relative_position_id -> нет фокуса '{m.group(1)}'")
        # идеи
        for kw in ('add_ideas', 'remove_ideas'):
            for m in re.finditer(kw + r'\s*=\s*(?:\{([^{}]*)\}|([A-Za-z0-9_]+))', body):
                names = (m.group(1) or m.group(2) or '').split()
                for n in names:
                    if n.startswith('GLP_') and n not in idea_ids and n not in token_ids:
                        err(f"{rel(p)}: {kw} -> нет идеи '{n}'")
        for m in re.finditer(r'swap_ideas\s*=\s*\{([^{}]*)\}', body):
            for n in re.findall(r'(?:add|remove)_idea\s*=\s*([A-Za-z0-9_]+)', m.group(1)):
                if n.startswith('GLP_') and n not in idea_ids and n not in token_ids:
                    err(f"{rel(p)}: swap_ideas -> нет идеи '{n}'")
        # события
        for m in re.finditer(r'(?:country_event|news_event)\s*=\s*\{[^}]*?id\s*=\s*([A-Za-z0-9_.]+)', body):
            e = m.group(1)
            if e.startswith('glp') and e not in event_ids:
                err(f"{rel(p)}: ссылка на несуществующее событие '{e}'")
        # персонажи
        for m in re.finditer(r'(?:recruit_character|promote_character|retire_character)\s*=\s*([A-Za-z0-9_]+)', body):
            c = m.group(1)
            if c.startswith('GLP_generic_'):
                continue          # ванильные generic-советники (history/general/generic_advisors.txt)
            if c.startswith('GLP_') and c not in char_ids:
                err(f"{rel(p)}: нет персонажа '{c}'")

    # коллизии координат внутри дерева
    for p, body in all_script_text('common/national_focus').items():
        for blk in re.finditer(r'focus\s*=\s*\{(.*?)\n\t\}', body, re.S):
            b = blk.group(1)
            fid = re.search(r'id\s*=\s*([A-Za-z0-9_]+)', b)
            x = re.search(r'\bx\s*=\s*(-?\d+)', b)
            y = re.search(r'\by\s*=\s*(-?\d+)', b)
            rel_to = re.search(r'relative_position_id\s*=\s*([A-Za-z0-9_]+)', b)
            if fid and x and y and not rel_to:
                positions[(x.group(1), y.group(1))].append(fid.group(1))
    for (x, y), names in sorted(positions.items()):
        if len(names) > 1:
            warn(f"фокусы в одной клетке x={x} y={y}: {', '.join(names)}")


def check_events(loc):
    """У каждого события должны быть title/desc и подписи всех опций."""
    ru = loc.get('russian', {})
    en = loc.get('english', {})
    for p in walk('events', ('.txt',)):
        body = strip_comments(read(p))
        for blk in re.finditer(r'(?:country_event|news_event|state_event|unit_leader_event)\s*=\s*\{(.*?)\n\}', body, re.S):
            b = blk.group(1)
            eid = re.search(r'\bid\s*=\s*([A-Za-z0-9_.]+)', b)
            if not eid:
                continue
            keys = []
            for kw in ('title', 'desc'):
                for m in re.finditer(kw + r'\s*=\s*([A-Za-z0-9_.]+)', b):
                    keys.append(m.group(1))
            for m in re.finditer(r'\bname\s*=\s*([A-Za-z0-9_.]+)', b):
                keys.append(m.group(1))
            for k in keys:
                if k not in ru:
                    err(f"{rel(p)}: событие {eid.group(1)} — нет русской локализации '{k}'")
                elif k not in en:
                    warn(f"{rel(p)}: событие {eid.group(1)} — нет английской локализации '{k}'")


def check_crisis_events():
    """Целостность цепочки кризисных событий glp_crisis.* (Спринт 6).

    Три инварианта, выявленные при итерации 20:
      (1) каждый glp_crisis.* должен запускаться (иначе событие лежит
          мёртвым грузом); проверяем country_event / news_event со ссылкой
          на glp_crisis.* в фокусах, on_actions, других событиях;
      (2) каждая казнь персонажа (retire / retire_character) обязана
          быть обёрнута в `if = { limit = { has_character = X } ... }` --
          1.19 молча роняет ошибку на retire без guard'а, если персонаж
          погиб ранее (что вполне реально для Григорьева / Махно /
          Скоблина -- они в зоне боевых действий);
      (3) в ступенчатых цепочках glp_crisis.40/41/42 флаги ступеней
          должны очищаться в финальной опции (clr_country_flag), иначе
          повторный запуск ступени даст ложный «branch already chosen»;
          для цепочки Махно -- наоборот, GLP_makhno_* ставится только
          как маркер пути и не требует clr.
    """
    # ----- (1) каждый glp_crisis.* запускается -----
    crisis_ids = set()
    for p in walk('events', ('.txt',)):
        body = strip_comments(read(p))
        for m in re.finditer(r'^\s*id\s*=\s*(glp_crisis\.\d+)', body, re.M):
            crisis_ids.add(m.group(1))

    # Какие crisis-ids фактически ВЫЗЫВАЮТСЯ (а не только объявляются).
    # Простая и надёжная эвристика:
    #   * В common/ и events/ — каждое вхождение `id = X` либо объявление
    #     (X-блок = country_event = { id = X ... }), либо вызов.
    #   * В common/national_focus/ и common/on_actions/ объявлений быть
    #     не может — только вызовы.
    # Считаем по файлам: для каждого crisis-id в каждом файле events/ если
    # `id = X` встречается >= 2 раз, значит есть вызов. В common/* — каждое
    # упоминание = вызов.
    referenced = defaultdict(set)
    for d in ('common/national_focus', 'common/on_actions', 'common/decisions',
              'events'):
        for p in walk(d, ('.txt',)):
            body = strip_comments(read(p))
            for cid in sorted(crisis_ids):
                if d != 'events':
                    if re.search(rf'\bid\s*=\s*{re.escape(cid)}\b', body):
                        referenced[cid].add(rel(p))
                else:
                    # в events/ 1 вхождение = только объявление; > 1 = есть вызов
                    if len(re.findall(rf'\bid\s*=\s*{re.escape(cid)}\b', body)) > 1:
                        referenced[cid].add(rel(p))

    for cid in sorted(crisis_ids):
        if cid not in referenced:
            err(f"crisis: событие {cid} не запускается ни из on_actions, "
                f"ни из фокусов, ни из других событий — мёртвый груз")

    # ----- (2) retire только под has_character guard -----
    for d in ('common', 'events', 'history'):
        for p in walk(d, ('.txt',)):
            body = strip_comments(read(p))
            # ищем вызовы retire / retire_character в character scope:
            # <TOK> = { retire = yes } ИЛИ retire_character = <TOK>
            for m in re.finditer(
                    r'([A-Za-z_][A-Za-z0-9_]*)\s*=\s*\{\s*retire\s*=\s*yes\s*\}',
                    body):
                tok = m.group(1)
                # контекст 200 символов до — есть ли has_character guard?
                start = max(0, m.start() - 200)
                ctx = body[start:m.start()]
                if not re.search(rf'has_character\s*=\s*{re.escape(tok)}\b', ctx):
                    err(f"{rel(p)}: '{tok} = {{ retire = yes }}' без "
                        f"if = {{ limit = {{ has_character = {tok} }} }} guard'а -- "
                        f"1.19 роняет silent error, если персонаж погиб ранее")
            for m in re.finditer(r'\bretire_character\s*=\s*([A-Za-z_][A-Za-z0-9_]*)', body):
                tok = m.group(1)
                # skip generic-советников (они всегда есть)
                if tok.startswith('GLP_generic_'):
                    continue
                start = max(0, m.start() - 200)
                ctx = body[start:m.start()]
                if not re.search(rf'has_character\s*=\s*{re.escape(tok)}\b', ctx):
                    err(f"{rel(p)}: retire_character = {tok} без "
                        f"if = {{ limit = {{ has_character = {tok} }} }} guard'а")

    # ----- (3) ступени 40/41/42: флаги очищаются -----
    # Берём только финальные опции ступени 3 (glp_crisis.42) и проверяем,
    # что в каждой опции срабатывает хотя бы один clr_country_flag из
    # {GLP_white_step_2_*, GLP_white_step_3_*}.
    p = os.path.join(ROOT, 'events/GLP_diplomacy.txt')
    if not os.path.exists(p):
        return
    body = strip_comments(read(p))
    m_step3 = re.search(
        r'country_event\s*=\s*\{\s*\n\s*id\s*=\s*glp_crisis\.42', body)
    if not m_step3:
        return
    open_pos = body.find('{', m_step3.start())
    depth = 1
    j = open_pos + 1
    while j < len(body) and depth:
        if body[j] == '{':
            depth += 1
        elif body[j] == '}':
            depth -= 1
        j += 1
    body42 = body[open_pos + 1:j - 1]
    # триггеры ступени 3: для каждой опции с trigger = has_country_flag
    # ожидаем соответствующий clr_country_flag в её теле.
    for opt in re.finditer(r'option\s*=\s*\{(.*?)\n\t\}', body42, re.S):
        b = opt.group(1)
        trig = re.search(r'trigger\s*=\s*\{\s*has_country_flag\s*=\s*([A-Za-z0-9_]+)', b)
        if not trig:
            continue
        flag = trig.group(1)
        if not re.search(rf'clr_country_flag\s*=\s*{re.escape(flag)}', b):
            err(f"{rel(p)}: glp_crisis.42 — опция с trigger на {flag!r} "
                f"не очищает этот флаг; повторный запуск цепочки даст "
                f"«branch already chosen»")
        # также требуем очистку «парного» флага ступени 2
        if flag == 'GLP_white_step_3_dispersed':
            if not re.search(r'clr_country_flag\s*=\s*GLP_white_step_2_sidelined', b):
                err(f"{rel(p)}: glp_crisis.42 — финал ветки 'dispersed' "
                    f"не очищает GLP_white_step_2_sidelined")
        elif flag == 'GLP_white_step_3_parallel':
            if not re.search(r'clr_country_flag\s*=\s*GLP_white_step_2_favored', b):
                err(f"{rel(p)}: glp_crisis.42 — финал ветки 'parallel' "
                    f"не очищает GLP_white_step_2_favored")


def check_units():
    """Ни одной дивизии РПАУ за предѣлами Вольной территоріи."""
    prov2state = {}
    owners = {}
    for p in walk('history/states', ('.txt',)):
        body = strip_comments(read(p))
        sid = re.search(r'id\s*=\s*(\d+)', body)
        own = re.search(r'owner\s*=\s*([A-Z]{3})', body)
        pr = re.search(r'provinces\s*=\s*\{([^}]*)\}', body)
        if not (sid and pr):
            continue
        owners[sid.group(1)] = own.group(1) if own else '???'
        for prov in pr.group(1).split():
            prov2state[prov] = sid.group(1)
    for p in walk('history/units', ('.txt',)):
        body = strip_comments(read(p))
        templates = set(re.findall(r'division_template\s*=\s*\{\s*\n?\s*name\s*=\s*"([^"]+)"', body))
        for m in re.finditer(r'location\s*=\s*(\d+)', body):
            prov = m.group(1)
            state = prov2state.get(prov)
            if state is None:
                err(f"{rel(p)}: дивизия в провинции {prov} — она не входит "
                    f"ни в один стейт Вольной территории (армия «в изгнании»)")
            elif owners.get(state) != 'GLP':
                err(f"{rel(p)}: дивизия в провинции {prov} (стейт {state}) — "
                    f"владелец {owners.get(state)}, а не GLP")
        # шаблоны, которых нет в этом же файле
        used = set(re.findall(r'division_template\s*=\s*"([^"]+)"', body))
        for t in sorted(used - templates):
            err(f"{rel(p)}: используется шаблон дивизии \"{t}\", "
                f"не определённый в этом OOB")


def check_bookmarks(loc):
    """Ключи закладок (history = "KEY") обязаны иметь локализацию."""
    ru = loc.get('russian', {})
    en = loc.get('english', {})
    for p in walk('common/bookmarks', ('.txt',)):
        body = strip_comments(read(p))
        for m in re.finditer(r'history\s*=\s*"([A-Za-z0-9_]+)"', body):
            key = m.group(1)
            if not key.startswith('GLP'):
                continue          # ванильные ключи берутся из базовой игры
            if key not in ru:
                err(f"{rel(p)}: нет русской локализации закладки '{key}'")
            if key not in en:
                warn(f"{rel(p)}: нет английской локализации закладки '{key}'")


def check_fonts():
    """Шрифты для запекания титров должны лежать в репозитории вместе с OFL."""
    need = ['tools/fonts/SourceSerifPro-Black.ttf',
            'tools/fonts/SourceSerifPro-Bold.ttf',
            'tools/fonts/SourceSerifPro-Regular.ttf',
            'tools/fonts/OFL-SourceSerifPro.txt']
    for f in need:
        path = os.path.join(ROOT, f)
        if not os.path.exists(path):
            err(f"{f} отсутствует — tools/build_screens.sh не соберёт титры")
        elif f.endswith('.ttf'):
            with open(path, 'rb') as fh:
                magic = fh.read(4)
            if magic not in (b'\x00\x01\x00\x00', b'true', b'OTTO', b'ttcf'):
                err(f"{f}: это не TrueType/OpenType шрифт")


def check_loading_tips():
    """Ванильные цитаты загрузки должны быть полностью перекрыты.

    Базовая игра использует ключи LOADING_TIP_0..~90, DLC добавляют свои;
    чтобы ванильная цитата никогда не появилась, мы перекрываем 0..500.
    При этом в файле не должно остаться ни одной ванильной цитаты: только
    авторские цитаты мода (Прудон, Бакунин, Кропоткин, Махно, Волин и т.д.).
    """
    ALLOWED_SIGNS = ('М. А. Бакунинъ', 'П. А. Кропоткинъ', 'П.-Ж. Прудонъ',
                     'Э. Гольдманъ', 'Н. И. Махно', 'В. М. Волинъ',
                     'П. А. Аршиновъ', 'Декларація РПА', 'Девизъ тачанки',
                     'Девизъ анархистовъ', 'Mikhail Bakunin', 'Peter Kropotkin',
                     'Pierre-Joseph Proudhon', 'Emma Goldman', 'Nestor Makhno',
                     'V. M. Voline', 'Peter Arshinov', 'RIAU Declaration',
                     'Tachanka motto', 'Anarchist motto')
    for lang in ('russian', 'english'):
        p = os.path.join(ROOT, f'localisation/{lang}/loading_tips_l_{lang}.yml')
        if not os.path.exists(p):
            err(f"{rel(p)} отсутствует — ванильные цитаты загрузки не перекрыты")
            continue
        text = read(p)
        nums = sorted(int(m.group(1))
                      for m in re.finditer(r'^\s*LOADING_TIP_(\d+):', text, re.M))
        if not nums:
            err(f"{rel(p)}: не найдено ни одного ключа LOADING_TIP_<n>")
            continue
        gaps = [n for n in range(0, 501) if n not in nums]
        if gaps:
            err(f"{rel(p)}: не перекрыты ванильные цитаты "
                f"(нет ключей для {len(gaps)} номеров, первый: LOADING_TIP_{gaps[0]})")
        # Никаких ванильных цитат: каждый текст обязан ссылаться на автора мода.
        for m in re.finditer(r'^LOADING_TIP_\d+:0 .*$', text, re.M):
            line = m.group(0)
            if not any(sign in line for sign in ALLOWED_SIGNS):
                err(f"{rel(p)}: ванильная цитата не перекрыта -> {line[:80]}...")


def check_music():
    """Ванильный саундтрек активирован по запросу (без принудительного перекрытия)."""
    return
    if os.path.exists(os.path.join(ROOT, 'music/music.asset')):
        body = read(os.path.join(ROOT, 'music/music.asset'))
        if 'name = "maintheme"' not in body:
            warn('music/music.asset: нет песни "maintheme" — '
                 'в главном меню зазвучит ванильная тема')
        # плейлист должен содержать не один трек
        tracks = re.findall(r'name\s*=\s*"([^"]+)"', body)
        if len(tracks) < 10:
            warn(f'music/music.asset: в плейлисте только {len(tracks)} '
                 f'треков (ожидается 10–11 композиций Монгол Шуудан)')
        # Предупреждаем о заглушке: если все .ogg байт-в-байт одинаковые,
        # в игре все "дорожки" звучат как один трек (сейчас это так и есть).
        oggs = sorted(p for p in walk('music', ('.ogg',)))
        hashes = defaultdict(set)
        for p in oggs:
            with open(p, 'rb') as fh:
                hashes[hashlib.md5(fh.read()).hexdigest()].add(rel(p))
        dup = {h: sorted(v) for h, v in hashes.items() if len(v) > 1}
        if dup and len(hashes) == 1:
            warn(f'music: все {len(oggs)} .ogg файлов идентичны (md5 '
                 f'{list(hashes)[0]}) — это плейсхолдеры. Замените их реальными '
                 f'дорожками Монгол Шуудан (OGG Vorbis) с теми же именами.')
        elif dup:
            for h, v in dup.items():
                warn(f'music: одинаковые .ogg ({len(v)} шт.): {", ".join(v)}')


def check_opinions(loc):
    """Все модификаторы мнений должны быть локализованы."""
    for p, body in all_script_text('common/opinion_modifiers').items():
        for m in re.finditer(r'^\t([A-Za-z0-9_]+)\s*=\s*\{', body, re.M):
            op = m.group(1)
            for lang in ('russian', 'english'):
                if op not in loc.get(lang, {}):
                    err(f"{rel(p)}: модификатор мнения '{op}' не локализован ({lang})")


def glob_dds(subdir):
    base = os.path.join(ROOT, subdir)
    for dirpath, _d, files in os.walk(base):
        for f in files:
            if f.lower().endswith('.dds'):
                yield os.path.join(dirpath, f)


# ------------------------------------------------- 7. traits & loc coverage
# Словарь имён черт базовой игры.  У каждой существующей черты есть
# локализационный ключ, поэтому полный снимок имён лежит в
# tools/vanilla_trait_names.txt (собран из localisation/english/
# traits_l_english.yml; зеркало ванили cbrzeczysz/hoi4-history @ 1.14.1).
# Рукой этот список не вести: прошлая версия словаря содержала выдуманные
# army_cavalry_speed_2 и army_morale_2, из-за чего советники Щусь и Григорьев
# прошли аудит и в игре не дали ни одного модификатора.
ADVISOR_TRAIT_FAMILIES = {
    'army': ('armored', 'artillery', 'cavalry', 'commando', 'concealment',
             'entrenchment', 'infantry', 'logistics', 'regrouping',
             'CombinedArms',
             'chief_defensive', 'chief_drill', 'chief_entrenchment',
             'chief_maneuver', 'chief_morale', 'chief_offensive',
             'chief_organizational', 'chief_planning', 'chief_reform'),
    'navy': ('amphibious_assault', 'anti_submarine', 'battleship',
             'capital_ship', 'carrier', 'cruiser', 'destroyer',
             'fleet_logistics', 'naval_air_defense', 'screen', 'submarine',
             'chief_commerce_raiding', 'chief_decisive_battle',
             'chief_maneuver', 'chief_naval_aviation', 'chief_reform'),
    'air': ('air_combat_training', 'air_superiority', 'airborne',
            'bomber_interception', 'close_air_support', 'naval_strike',
            'pilot_training', 'strategic_bombing', 'tactical_bombing',
            'chief_all_weather', 'chief_ground_support',
            'chief_night_operations', 'chief_reform', 'chief_safety'),
}


def _advisor_trait_names():
    """Черты ставки/министров ванили: семейства x уровни 1..3 (сверено со
    снимком локализации -- количества совпадают: 54 army, 48 navy, 42 air)."""
    out = set()
    for ledger, fams in ADVISOR_TRAIT_FAMILIES.items():
        for fam in fams:
            for lvl in (1, 2, 3):
                out.add(f'{ledger}_{fam}_{lvl}')
    return out


def load_vanilla_traits():
    """Имена ванильных черт: снимок локализации + семейства ставки."""
    names = _advisor_trait_names()
    snap = os.path.join(ROOT, 'tools/vanilla_trait_names.txt')
    if not os.path.exists(snap):
        warn('tools/vanilla_trait_names.txt: нет снимка ванильных черт -- '
             'проверка имён видит только семейства army_*/navy_*/air_*')
        return names
    for line in read(snap).split('\n'):
        line = line.strip()
        if line and not line.startswith('#'):
            names.add(line)
    return names


VANILLA_TRAITS = load_vanilla_traits()

# Законные advisor-слоты (High Command / правительство) базовой игры:
# common/characters/NZL.txt, common/ideas/belarus.txt, 1.14.1.
ADVISOR_SLOTS = {
    'theorist', 'army_chief', 'navy_chief', 'air_chief', 'high_command',
    'political_advisor', 'chief_of_armament', 'tank_designer',
    'aircraft_designer', 'naval_designer', 'high_commission', 'secretary',
}



def check_characters(defs, loc):
    defined_traits = set(defs['trait'])
    ru = loc.get('russian', {})
    en = loc.get('english', {})
    for p, body in all_script_text('common/characters').items():
        for m in re.finditer(r'(?<![A-Za-z_])traits\s*=\s*\{([^}]*)\}', body):
            for t in m.group(1).split():
                if t not in defined_traits and t not in VANILLA_TRAITS:
                    warn(f"{rel(p)}: trait '{t}' is not defined by the mod and "
                         f"is not in the known vanilla list -- verify it exists")
    # loc coverage
    need = []
    need += [(k, 'character') for k in defs['character']]
    need += [(k, 'advisor token') for k in defs['idea_token']]
    need += [(k, 'leader trait') for k in defs['trait']]
    need += [(k, 'idea') for k in defs['idea']]
    need += [(k, 'focus') for k in defs['focus']]
    for key, kind in need:
        if key not in ru:
            err(f"missing russian localisation for {kind} '{key}'")
        if key not in en:
            warn(f"missing english localisation for {kind} '{key}'")
    for key, kind in need:
        if kind in ('leader trait', 'idea', 'focus', 'advisor token'):
            d = key + '_desc'
            if key in ru and d not in ru and kind != 'advisor token':
                warn(f"missing russian description '{d}'")
    # parity
    for k in sorted(set(ru) - set(en)):
        if k.startswith('GLP'):
            warn(f"key '{k}' exists in russian but not english")
    for k in sorted(set(en) - set(ru)):
        if k.startswith('GLP'):
            err(f"key '{k}' exists in english but not russian")


# ------------------------------------------------- 8. vanilla sprite whitelists
# Спрайты базовой игры (без DLC): дампы interface/goals.gfx версий 1.7.1 и
# interface/ideas.gfx версии 1.7.1: Paradox не удаляет имена спрайтов,
# поэтому список валиден и для 1.19. Ссылка на спрайт вне списка --
# риск "красной иконки" без соответствующего DLC.
VANILLA_FOCUS_ICONS = set(['GFX_goal_generic_CAS', 'GFX_goal_generic_air_bomber', 'GFX_goal_generic_air_doctrine', 'GFX_goal_generic_air_fighter', 'GFX_goal_generic_air_fighter2', 'GFX_goal_generic_air_naval_bomber', 'GFX_goal_generic_air_production', 'GFX_goal_generic_alliance', 'GFX_goal_generic_allies_build_infantry', 'GFX_goal_generic_amphibious_assault', 'GFX_goal_generic_army_artillery', 'GFX_goal_generic_army_artillery2', 'GFX_goal_generic_army_doctrines', 'GFX_goal_generic_army_motorized', 'GFX_goal_generic_army_tanks', 'GFX_goal_generic_attack_allies', 'GFX_goal_generic_axis_build_infantry', 'GFX_goal_generic_build_airforce', 'GFX_goal_generic_build_navy', 'GFX_goal_generic_build_tank', 'GFX_goal_generic_cavalry', 'GFX_goal_generic_construct_civ_factory', 'GFX_goal_generic_construct_civilian', 'GFX_goal_generic_construct_infrastructure', 'GFX_goal_generic_construct_mil_factory', 'GFX_goal_generic_construct_military', 'GFX_goal_generic_construct_naval_dockyard', 'GFX_goal_generic_construction', 'GFX_goal_generic_construction2', 'GFX_goal_generic_consumer_goods', 'GFX_goal_generic_dangerous_deal', 'GFX_goal_generic_defence', 'GFX_goal_generic_demand_territory', 'GFX_goal_generic_forceful_treaty', 'GFX_goal_generic_fortify_city', 'GFX_goal_generic_improve_relations', 'GFX_goal_generic_intelligence_exchange', 'GFX_goal_generic_major_alliance', 'GFX_goal_generic_major_war', 'GFX_goal_generic_military_deal', 'GFX_goal_generic_military_sphere', 'GFX_goal_generic_more_territorial_claims', 'GFX_goal_generic_national_unity', 'GFX_goal_generic_navy_anti_submarine', 'GFX_goal_generic_navy_battleship', 'GFX_goal_generic_navy_carrier', 'GFX_goal_generic_navy_cruiser', 'GFX_goal_generic_navy_doctrines_tactics', 'GFX_goal_generic_navy_submarine', 'GFX_goal_generic_neutrality_focus', 'GFX_goal_generic_occupy_start_war', 'GFX_goal_generic_occupy_states_coastal', 'GFX_goal_generic_occupy_states_ongoing_war', 'GFX_goal_generic_oil_refinery', 'GFX_goal_generic_political_pressure', 'GFX_goal_generic_position_armies', 'GFX_goal_generic_positive_trade_relations', 'GFX_goal_generic_production', 'GFX_goal_generic_production2', 'GFX_goal_generic_propaganda', 'GFX_goal_generic_radar', 'GFX_goal_generic_scientific_exchange', 'GFX_goal_generic_secret_weapon', 'GFX_goal_generic_small_arms', 'GFX_goal_generic_soviet_construction', 'GFX_goal_generic_special_forces', 'GFX_goal_generic_territory_or_war', 'GFX_goal_generic_trade', 'GFX_goal_generic_war_with_comintern', 'GFX_goal_generic_wolf_pack', 'GFX_focus_generic_adriatic_sea_focus', 'GFX_focus_generic_advanced_military_studies', 'GFX_focus_generic_aegean_sea_focus', 'GFX_focus_generic_africa_defense', 'GFX_focus_generic_africa_factory', 'GFX_focus_generic_africa_infrastructure', 'GFX_focus_generic_africa_liberation', 'GFX_focus_generic_africa_naval', 'GFX_focus_generic_africa_production', 'GFX_focus_generic_agricultural_subsidies', 'GFX_focus_generic_air_bases', 'GFX_focus_generic_air_carrier', 'GFX_focus_generic_air_defense', 'GFX_focus_generic_air_partners', 'GFX_focus_generic_air_research_boost', 'GFX_focus_generic_aircraft_production', 'GFX_focus_generic_aluminum', 'GFX_focus_generic_american_investments', 'GFX_focus_generic_annex_country', 'GFX_focus_generic_annex_country_2', 'GFX_focus_generic_anti_fascist_diplomacy', 'GFX_focus_generic_anti_tank_guns', 'GFX_focus_generic_armored_air_support', 'GFX_focus_generic_army_doctrines_2', 'GFX_focus_generic_army_tanks2', 'GFX_focus_generic_atlantic_coast', 'GFX_focus_generic_attack_argentina', 'GFX_focus_generic_attack_austria', 'GFX_focus_generic_attack_baltics', 'GFX_focus_generic_attack_bolivia', 'GFX_focus_generic_attack_brazil', 'GFX_focus_generic_attack_bulgaria', 'GFX_focus_generic_attack_chile', 'GFX_focus_generic_attack_colombia', 'GFX_focus_generic_attack_communist_spain', 'GFX_focus_generic_attack_cyprus', 'GFX_focus_generic_attack_czechoslovakia', 'GFX_focus_generic_attack_denmark', 'GFX_focus_generic_attack_ecuador', 'GFX_focus_generic_attack_ethiopia', 'GFX_focus_generic_attack_finland', 'GFX_focus_generic_attack_greece', 'GFX_focus_generic_attack_haiti', 'GFX_focus_generic_attack_hungary', 'GFX_focus_generic_attack_iran', 'GFX_focus_generic_attack_katanga', 'GFX_focus_generic_attack_kurdistan', 'GFX_focus_generic_attack_mongolia', 'GFX_focus_generic_attack_nationalist_spain_focus', 'GFX_focus_generic_attack_nordic_territory', 'GFX_focus_generic_attack_norway', 'GFX_focus_generic_attack_paraguay', 'GFX_focus_generic_attack_peru', 'GFX_focus_generic_attack_poland', 'GFX_focus_generic_attack_portugal', 'GFX_focus_generic_attack_republican_spain', 'GFX_focus_generic_attack_romania', 'GFX_focus_generic_attack_slovakia', 'GFX_focus_generic_attack_sweden', 'GFX_focus_generic_attack_the_guyanas', 'GFX_focus_generic_attack_turkey', 'GFX_focus_generic_attack_uruguay', 'GFX_focus_generic_attack_usa', 'GFX_focus_generic_attack_venezuela', 'GFX_focus_generic_attack_vichy_france', 'GFX_focus_generic_attack_yugoslavia', 'GFX_focus_generic_bad_medical', 'GFX_focus_generic_balkan_diplomacy', 'GFX_focus_generic_balkans_focus', 'GFX_focus_generic_baltic_entente', 'GFX_focus_generic_baltic_sea_empire', 'GFX_focus_generic_baltic_sea_fleet', 'GFX_focus_generic_befriend_afghanistan', 'GFX_focus_generic_befriend_albania', 'GFX_focus_generic_befriend_austria', 'GFX_focus_generic_befriend_barotseland', 'GFX_focus_generic_befriend_bohemia', 'GFX_focus_generic_befriend_bulgaria', 'GFX_focus_generic_befriend_chile', 'GFX_focus_generic_befriend_communist_spain_focus', 'GFX_focus_generic_befriend_cyprus', 'GFX_focus_generic_befriend_czechoslovakia', 'GFX_focus_generic_befriend_denmark', 'GFX_focus_generic_befriend_greece', 'GFX_focus_generic_befriend_hungary', 'GFX_focus_generic_befriend_iceland', 'GFX_focus_generic_befriend_katanga', 'GFX_focus_generic_befriend_kurdistan', 'GFX_focus_generic_befriend_mapuche', 'GFX_focus_generic_befriend_monarchist_georgia', 'GFX_focus_generic_befriend_nationalist_spain_focus', 'GFX_focus_generic_befriend_norway', 'GFX_focus_generic_befriend_portugal', 'GFX_focus_generic_befriend_republican_spain_focus', 'GFX_focus_generic_befriend_rwanda', 'GFX_focus_generic_befriend_saudi_arabia', 'GFX_focus_generic_befriend_sinkiang', 'GFX_focus_generic_befriend_slovakia', 'GFX_focus_generic_befriend_sweden', 'GFX_focus_generic_befriend_switzerland', 'GFX_focus_generic_befriend_szekelys', 'GFX_focus_generic_befriend_teschen', 'GFX_focus_generic_befriend_turkey', 'GFX_focus_generic_befriend_usa', 'GFX_focus_generic_befriend_wiedist_albania', 'GFX_focus_generic_black_sea_focus', 'GFX_focus_generic_blue_flags', 'GFX_focus_generic_british_trade', 'GFX_focus_generic_camel_corps', 'GFX_focus_generic_cas_aircraft', 'GFX_focus_generic_catholic_dominion', 'GFX_focus_generic_central_planning', 'GFX_focus_generic_china1', 'GFX_focus_generic_chromium', 'GFX_focus_generic_coal_mining', 'GFX_focus_generic_coastal_fort', 'GFX_focus_generic_coffee', 'GFX_focus_generic_combined_arms', 'GFX_focus_generic_commonwealth_build_infantry', 'GFX_focus_generic_communism_anti_fascism', 'GFX_focus_generic_communist', 'GFX_focus_generic_communist_attack_czechoslovakia', 'GFX_focus_generic_communist_attack_hungary', 'GFX_focus_generic_communist_attack_poland', 'GFX_focus_generic_communist_industry', 'GFX_focus_generic_concessions', 'GFX_focus_generic_conspiracy', 'GFX_focus_generic_copy_plane_designs', 'GFX_focus_generic_court', 'GFX_focus_generic_cruiser2', 'GFX_focus_generic_cruiser_submarines', 'GFX_focus_generic_cryptologic_bomb', 'GFX_focus_generic_currency_reforms', 'GFX_focus_generic_defensive_reorganization', 'GFX_focus_generic_democratic_europe', 'GFX_focus_generic_destroyer', 'GFX_focus_generic_devaluation', 'GFX_focus_generic_develop_denmark_silhouette', 'GFX_focus_generic_develop_eritrea', 'GFX_focus_generic_develop_ethiopia', 'GFX_focus_generic_develop_finland_silhouette', 'GFX_focus_generic_develop_iceland_silhouette', 'GFX_focus_generic_develop_libya', 'GFX_focus_generic_develop_norway_silhouette', 'GFX_focus_generic_develop_somaliland', 'GFX_focus_generic_develop_sweden_silhouette', 'GFX_focus_generic_diplomatic_treaty', 'GFX_focus_generic_early_helicopter', 'GFX_focus_generic_economic_recovery', 'GFX_focus_generic_energy', 'GFX_focus_generic_farmland', 'GFX_focus_generic_fascist_propaganda', 'GFX_focus_generic_fascist_troops', 'GFX_focus_generic_fiat', 'GFX_focus_generic_field_hostpital', 'GFX_focus_generic_forest_brothers', 'GFX_focus_generic_fortify_denmark', 'GFX_focus_generic_fortify_finland', 'GFX_focus_generic_fortify_iceland', 'GFX_focus_generic_fortify_norway', 'GFX_focus_generic_fortify_sweden', 'GFX_focus_generic_free_iberia', 'GFX_focus_generic_freedom_council', 'GFX_focus_generic_full_employment', 'GFX_focus_generic_full_social_mobilization', 'GFX_focus_generic_german_trade', 'GFX_focus_generic_government_in_exile', 'GFX_focus_generic_heavy_tank', 'GFX_focus_generic_home_defense', 'GFX_focus_generic_horse_studs', 'GFX_focus_generic_hydroelectric_energy', 'GFX_focus_generic_improve_roads', 'GFX_focus_generic_improve_the_administration', 'GFX_focus_generic_industrialists', 'GFX_focus_generic_industry_1', 'GFX_focus_generic_industry_2', 'GFX_focus_generic_industry_3', 'GFX_focus_generic_infiltration', 'GFX_focus_generic_influence_benelux', 'GFX_focus_generic_influence_middle_east', 'GFX_focus_generic_invade_denmark', 'GFX_focus_generic_invade_finland', 'GFX_focus_generic_invade_iceland', 'GFX_focus_generic_invade_norway', 'GFX_focus_generic_invade_sweden', 'GFX_focus_generic_invite_republican_spanish_exiles', 'GFX_focus_generic_italy_first', 'GFX_focus_generic_italy_propaganda', 'GFX_focus_generic_japanese_imperial_glory', 'GFX_focus_generic_jet_planes', 'GFX_focus_generic_join_comintern', 'GFX_focus_generic_land_reclamation', 'GFX_focus_generic_league_of_nations', 'GFX_focus_generic_license_production', 'GFX_focus_generic_liechtenstein_coa', 'GFX_focus_generic_limited_social_mobilization', 'GFX_focus_generic_little_entente', 'GFX_focus_generic_long_range_aircraft', 'GFX_focus_generic_low_cost_housing', 'GFX_focus_generic_manpower', 'GFX_focus_generic_mass_production', 'GFX_focus_generic_mechanized', 'GFX_focus_generic_mediterranean_sea_focus', 'GFX_focus_generic_merchant_fleet', 'GFX_focus_generic_midget_submarines', 'GFX_focus_generic_military_academy', 'GFX_focus_generic_military_dictatorship', 'GFX_focus_generic_military_industry', 'GFX_focus_generic_military_mission', 'GFX_focus_generic_mine_warfare', 'GFX_focus_generic_mining_industry', 'GFX_focus_generic_modernize_industry', 'GFX_focus_generic_monarchist_sentiment', 'GFX_focus_generic_monarchist_workers', 'GFX_focus_generic_monarchy_1', 'GFX_focus_generic_monarchy_2', 'GFX_focus_generic_monetary_union', 'GFX_focus_generic_motor_cycle', 'GFX_focus_generic_mountain_fortification', 'GFX_focus_generic_multi_role_aircraft', 'GFX_focus_generic_national_security', 'GFX_focus_generic_naval_discipline', 'GFX_focus_generic_naval_invasion', 'GFX_focus_generic_naval_invasion_tank', 'GFX_focus_generic_navy_battleship2', 'GFX_focus_generic_nordic_territory', 'GFX_focus_generic_north_atlantic_fleet', 'GFX_focus_generic_nuclear_development', 'GFX_focus_generic_offshore_oil_rig', 'GFX_focus_generic_pan_scandinavism', 'GFX_focus_generic_paratrooper', 'GFX_focus_generic_polish_deal', 'GFX_focus_generic_pope', 'GFX_focus_generic_population_growth', 'GFX_focus_generic_price_controls', 'GFX_focus_generic_printing_press', 'GFX_focus_generic_promote_SA_immigration', 'GFX_focus_generic_provoke_border_clashes', 'GFX_focus_generic_public_works', 'GFX_focus_generic_radio_communication', 'GFX_focus_generic_railroad', 'GFX_focus_generic_railway_gun', 'GFX_focus_generic_red_flags', 'GFX_focus_generic_refit_civilian_ships', 'GFX_focus_generic_reinforcing_the_supply_network', 'GFX_focus_generic_reorient_production', 'GFX_focus_generic_resource_extraction', 'GFX_focus_generic_road_investment', 'GFX_focus_generic_royal_wedding', 'GFX_focus_generic_rubber', 'GFX_focus_generic_rubber_plantations', 'GFX_focus_generic_scandinavia_flags', 'GFX_focus_generic_scandinavian_alliance', 'GFX_focus_generic_secret_service_agency', 'GFX_focus_generic_self_management', 'GFX_focus_generic_self_propelled_gun', 'GFX_focus_generic_social_democracy', 'GFX_focus_generic_socialist_science', 'GFX_focus_generic_south_america', 'GFX_focus_generic_soviet_politics', 'GFX_focus_generic_spread_fascism', 'GFX_focus_generic_spur_communist_revolutions', 'GFX_focus_generic_steel', 'GFX_focus_generic_stockpile_fuel', 'GFX_focus_generic_strike_at_democracy1', 'GFX_focus_generic_strike_at_democracy2', 'GFX_focus_generic_strike_at_democracy3', 'GFX_focus_generic_subjugation', 'GFX_focus_generic_supply_line', 'GFX_focus_generic_support_the_left_right', 'GFX_focus_generic_surrender', 'GFX_focus_generic_tank_air_support', 'GFX_focus_generic_tank_assault', 'GFX_focus_generic_tank_assembly', 'GFX_focus_generic_tank_production', 'GFX_focus_generic_tankette', 'GFX_focus_generic_the_council_of_europe', 'GFX_focus_generic_the_giant_wakes', 'GFX_focus_generic_the_suez', 'GFX_focus_generic_torpedo_production', 'GFX_focus_generic_total_war', 'GFX_focus_generic_trade_interdiction', 'GFX_focus_generic_treaty', 'GFX_focus_generic_truck', 'GFX_focus_generic_tungsten', 'GFX_focus_generic_universal_suffrage', 'GFX_focus_generic_university_1', 'GFX_focus_generic_university_2', 'GFX_focus_generic_university_3', 'GFX_focus_generic_uranium_extraction', 'GFX_focus_generic_vatican_agents', 'GFX_focus_generic_vatican_state', 'GFX_focus_generic_vichy_france_triumphant_focus', 'GFX_focus_generic_welfare', 'GFX_focus_generic_whispers', 'GFX_focus_generic_winter_warfare', 'GFX_focus_generic_women_in_military', 'GFX_focus_generic_workers', 'GFX_focus_generic_workers_and_farmers_rise', 'GFX_focus_rocketry'])

VANILLA_IDEA_SPRITES = set(['GFX_idea_generic_acquire_tanks', 'GFX_idea_generic_agrarian_reform', 'GFX_idea_generic_agrarian_society', 'GFX_idea_generic_air_african_1', 'GFX_idea_generic_air_african_2', 'GFX_idea_generic_air_african_3', 'GFX_idea_generic_air_air_combat_trainer_african_2d', 'GFX_idea_generic_air_air_combat_trainer_asian_2d', 'GFX_idea_generic_air_air_combat_trainer_commonwealth_2d', 'GFX_idea_generic_air_air_combat_trainer_eastern_european_2d', 'GFX_idea_generic_air_air_combat_trainer_middle_eastern_2d', 'GFX_idea_generic_air_air_combat_trainer_south_american_2d', 'GFX_idea_generic_air_air_combat_trainer_western_european_2d', 'GFX_idea_generic_air_arab_1', 'GFX_idea_generic_air_arab_2', 'GFX_idea_generic_air_arab_3', 'GFX_idea_generic_air_asia_1', 'GFX_idea_generic_air_asia_2', 'GFX_idea_generic_air_asia_3', 'GFX_idea_generic_air_bonus', 'GFX_idea_generic_air_chief_all_weather_asian_2d', 'GFX_idea_generic_air_chief_all_weather_commonwealth_2d', 'GFX_idea_generic_air_chief_all_weather_eastern_european_2d', 'GFX_idea_generic_air_chief_all_weather_middle_eastern_2d', 'GFX_idea_generic_air_chief_all_weather_south_american_2d', 'GFX_idea_generic_air_chief_all_weather_western_european_2d', 'GFX_idea_generic_air_close_air_sup_african_2d', 'GFX_idea_generic_air_close_air_sup_asian_2d', 'GFX_idea_generic_air_close_air_sup_commonwealth_2d', 'GFX_idea_generic_air_close_air_sup_eastern_european_2d', 'GFX_idea_generic_air_close_air_sup_middle_eastern_2d', 'GFX_idea_generic_air_close_air_sup_south_american_2d', 'GFX_idea_generic_air_close_air_sup_western_european_2d', 'GFX_idea_generic_air_europe_1', 'GFX_idea_generic_air_europe_2', 'GFX_idea_generic_air_europe_3', 'GFX_idea_generic_air_manufacturer_1', 'GFX_idea_generic_air_manufacturer_2', 'GFX_idea_generic_air_manufacturer_3', 'GFX_idea_generic_air_payment', 'GFX_idea_generic_air_research', 'GFX_idea_generic_air_south_america_1', 'GFX_idea_generic_air_south_america_2', 'GFX_idea_generic_air_south_america_3', 'GFX_idea_generic_air_warfare_theorist_african_2d', 'GFX_idea_generic_air_warfare_theorist_asian_2d', 'GFX_idea_generic_air_warfare_theorist_commonwealth_2d', 'GFX_idea_generic_air_warfare_theorist_eastern_european_2d', 'GFX_idea_generic_air_warfare_theorist_middle_eastern_2d', 'GFX_idea_generic_air_warfare_theorist_south_american_2d', 'GFX_idea_generic_air_warfare_theorist_western_european_2d', 'GFX_idea_generic_armor', 'GFX_idea_generic_army_african_1', 'GFX_idea_generic_army_african_2', 'GFX_idea_generic_army_african_3', 'GFX_idea_generic_army_african_4', 'GFX_idea_generic_army_african_5', 'GFX_idea_generic_army_african_6', 'GFX_idea_generic_army_arab_1', 'GFX_idea_generic_army_arab_2', 'GFX_idea_generic_army_arab_3', 'GFX_idea_generic_army_art_african_2d', 'GFX_idea_generic_army_art_asian_2d', 'GFX_idea_generic_army_art_commonwealth_2d', 'GFX_idea_generic_army_art_eastern_european_2d', 'GFX_idea_generic_army_art_middle_eastern_2d', 'GFX_idea_generic_army_art_south_american_2d', 'GFX_idea_generic_army_art_western_european_2d', 'GFX_idea_generic_army_asia_1', 'GFX_idea_generic_army_asia_2', 'GFX_idea_generic_army_asia_3', 'GFX_idea_generic_army_asia_4', 'GFX_idea_generic_army_asia_5', 'GFX_idea_generic_army_asia_6', 'GFX_idea_generic_army_asia_7', 'GFX_idea_generic_army_chief_def_african_2d', 'GFX_idea_generic_army_chief_def_asian_2d', 'GFX_idea_generic_army_chief_def_commonwealth_2d', 'GFX_idea_generic_army_chief_def_eastern_european_2d', 'GFX_idea_generic_army_chief_def_middle_eastern_2d', 'GFX_idea_generic_army_chief_def_south_american_2d', 'GFX_idea_generic_army_chief_def_western_european_2d', 'GFX_idea_generic_army_chief_off_african_2d', 'GFX_idea_generic_army_chief_off_asian_2d', 'GFX_idea_generic_army_chief_off_commonwealth_2d', 'GFX_idea_generic_army_chief_off_eastern_european_2d', 'GFX_idea_generic_army_chief_off_middle_eastern_2d', 'GFX_idea_generic_army_chief_off_south_american_2d', 'GFX_idea_generic_army_chief_off_western_european_2d', 'GFX_idea_generic_army_europe_1', 'GFX_idea_generic_army_europe_2', 'GFX_idea_generic_army_europe_3', 'GFX_idea_generic_army_europe_4', 'GFX_idea_generic_army_europe_5', 'GFX_idea_generic_army_europe_6', 'GFX_idea_generic_army_log_african_2d', 'GFX_idea_generic_army_log_asian_2d', 'GFX_idea_generic_army_log_commonwealth_2d', 'GFX_idea_generic_army_log_eastern_european_2d', 'GFX_idea_generic_army_log_middle_eastern_2d', 'GFX_idea_generic_army_log_south_american_2d', 'GFX_idea_generic_army_log_western_european_2d', 'GFX_idea_generic_army_problems', 'GFX_idea_generic_army_south_america_1', 'GFX_idea_generic_army_south_america_2', 'GFX_idea_generic_army_south_america_3', 'GFX_idea_generic_army_south_america_4', 'GFX_idea_generic_army_south_america_5', 'GFX_idea_generic_army_war_college', 'GFX_idea_generic_artillery_manufacturer_1', 'GFX_idea_generic_artillery_manufacturer_2', 'GFX_idea_generic_artillery_manufacturer_3', 'GFX_idea_generic_artillery_regiments', 'GFX_idea_generic_bomber_production_diverted', 'GFX_idea_generic_build_infrastructure', 'GFX_idea_generic_captain_of_industry_african_2d', 'GFX_idea_generic_captain_of_industry_asian_2d', 'GFX_idea_generic_captain_of_industry_commonwealth_2d', 'GFX_idea_generic_captain_of_industry_eastern_european_2d', 'GFX_idea_generic_captain_of_industry_middle_eastern_2d', 'GFX_idea_generic_captain_of_industry_south_american_2d', 'GFX_idea_generic_captain_of_industry_western_european_2d', 'GFX_idea_generic_central_management', 'GFX_idea_generic_coastal_defense_ships', 'GFX_idea_generic_coastal_defense_ships2', 'GFX_idea_generic_coastal_navy', 'GFX_idea_generic_communism_drift_bonus', 'GFX_idea_generic_communist_army', 'GFX_idea_generic_communist_revolutionary_african_2d', 'GFX_idea_generic_communist_revolutionary_asian_2d', 'GFX_idea_generic_communist_revolutionary_commonwealth_2d', 'GFX_idea_generic_communist_revolutionary_eastern_european_2d', 'GFX_idea_generic_communist_revolutionary_middle_eastern_2d', 'GFX_idea_generic_communist_revolutionary_southamerican_2d', 'GFX_idea_generic_communist_revolutionary_western_european_2d', 'GFX_idea_generic_constitutional_guarantees', 'GFX_idea_generic_deal_with_the_devil', 'GFX_idea_generic_deal_with_the_devil2', 'GFX_idea_generic_degauss_ship_hulls', 'GFX_idea_generic_democratic_drift_bonus', 'GFX_idea_generic_democratic_reformer_african_2d', 'GFX_idea_generic_democratic_reformer_asian_2d', 'GFX_idea_generic_democratic_reformer_commonwealth_2d', 'GFX_idea_generic_democratic_reformer_eastern_european_2d', 'GFX_idea_generic_democratic_reformer_middle_eastern_2d', 'GFX_idea_generic_democratic_reformer_southamerican_2d', 'GFX_idea_generic_democratic_reformer_western_european_2d', 'GFX_idea_generic_disjointed_gov', 'GFX_idea_generic_electronics_concern_1', 'GFX_idea_generic_electronics_concern_2', 'GFX_idea_generic_electronics_concern_3', 'GFX_idea_generic_exploit_mines', 'GFX_idea_generic_fascism_banned', 'GFX_idea_generic_fascism_drift_2', 'GFX_idea_generic_fascism_drift_bonus', 'GFX_idea_generic_fascist_demagogue_african_2d', 'GFX_idea_generic_fascist_demagogue_asian_2d', 'GFX_idea_generic_fascist_demagogue_commonwealth_2d', 'GFX_idea_generic_fascist_demagogue_eastern_european_2d', 'GFX_idea_generic_fascist_demagogue_middle_eastern_2d', 'GFX_idea_generic_fascist_demagogue_southamerican_2d', 'GFX_idea_generic_fascist_demagogue_western_european_2d', 'GFX_idea_generic_fighter_production_diverted', 'GFX_idea_generic_flexible_foreign_policy', 'GFX_idea_generic_flexible_foreign_policy2', 'GFX_idea_generic_foreign_capital', 'GFX_idea_generic_fortification_engineer_african_2d', 'GFX_idea_generic_fortification_engineer_asian_2d', 'GFX_idea_generic_fortification_engineer_commonwealth_2d', 'GFX_idea_generic_fortification_engineer_eastern_european_2d', 'GFX_idea_generic_fortification_engineer_middle_eastern_2d', 'GFX_idea_generic_fortification_engineer_south_american_2d', 'GFX_idea_generic_fortification_engineer_western_european_2d', 'GFX_idea_generic_fortify_the_borders', 'GFX_idea_generic_goods_red_bonus', 'GFX_idea_generic_industrial_concern_1', 'GFX_idea_generic_industrial_concern_2', 'GFX_idea_generic_industrial_concern_3', 'GFX_idea_generic_infantry_bonus', 'GFX_idea_generic_infantry_equipment_manufacturer_1', 'GFX_idea_generic_infantry_equipment_manufacturer_2', 'GFX_idea_generic_infantry_equipment_manufacturer_3', 'GFX_idea_generic_intel_bonus', 'GFX_idea_generic_king_handled', 'GFX_idea_generic_license_production', 'GFX_idea_generic_local_self_management', 'GFX_idea_generic_manpower_bonus', 'GFX_idea_generic_military_theorist_african_2d', 'GFX_idea_generic_military_theorist_asian_2d', 'GFX_idea_generic_military_theorist_commonwealth_2d', 'GFX_idea_generic_military_theorist_eastern_european_2d', 'GFX_idea_generic_military_theorist_middle_eastern_2d', 'GFX_idea_generic_military_theorist_south_american_2d', 'GFX_idea_generic_military_theorist_western_european_2d', 'GFX_idea_generic_morale_bonus', 'GFX_idea_generic_motorized_equipment_manufacturer_1', 'GFX_idea_generic_motorized_equipment_manufacturer_2', 'GFX_idea_generic_motorized_equipment_manufacturer_3', 'GFX_idea_generic_naval_manufacturer_1', 'GFX_idea_generic_naval_manufacturer_2', 'GFX_idea_generic_naval_manufacturer_3', 'GFX_idea_generic_naval_theorist_african_2d', 'GFX_idea_generic_naval_theorist_asian_2d', 'GFX_idea_generic_naval_theorist_commonwealth_2d', 'GFX_idea_generic_naval_theorist_eastern_european_2d', 'GFX_idea_generic_naval_theorist_middle_eastern_2d', 'GFX_idea_generic_naval_theorist_south_american_2d', 'GFX_idea_generic_naval_theorist_western_european_2d', 'GFX_idea_generic_navy_african_1', 'GFX_idea_generic_navy_african_2', 'GFX_idea_generic_navy_african_3', 'GFX_idea_generic_navy_anti_submarine_african_2d', 'GFX_idea_generic_navy_anti_submarine_asian_2d', 'GFX_idea_generic_navy_anti_submarine_commonwealth_2d', 'GFX_idea_generic_navy_anti_submarine_eastern_european_2d', 'GFX_idea_generic_navy_anti_submarine_middle_eastern_2d', 'GFX_idea_generic_navy_anti_submarine_south_american_2d', 'GFX_idea_generic_navy_anti_submarine_western_european_2d', 'GFX_idea_generic_navy_arab_1', 'GFX_idea_generic_navy_arab_2', 'GFX_idea_generic_navy_arab_3', 'GFX_idea_generic_navy_asia_1', 'GFX_idea_generic_navy_asia_2', 'GFX_idea_generic_navy_asia_3', 'GFX_idea_generic_navy_bonus', 'GFX_idea_generic_navy_carrier_bonus', 'GFX_idea_generic_navy_chief_decisive_bat_african_2d', 'GFX_idea_generic_navy_chief_decisive_bat_asian_2d', 'GFX_idea_generic_navy_chief_decisive_bat_commonwealth_2d', 'GFX_idea_generic_navy_chief_decisive_bat_eastern_european_2d', 'GFX_idea_generic_navy_chief_decisive_bat_middle_eastern_2d', 'GFX_idea_generic_navy_chief_decisive_bat_south_american_2d', 'GFX_idea_generic_navy_chief_decisive_bat_western_european_2d', 'GFX_idea_generic_navy_europe_1', 'GFX_idea_generic_navy_europe_2', 'GFX_idea_generic_navy_europe_3', 'GFX_idea_generic_navy_fleet_log_african_2d', 'GFX_idea_generic_navy_fleet_log_asian_2d', 'GFX_idea_generic_navy_fleet_log_commonwealth_2d', 'GFX_idea_generic_navy_fleet_log_eastern_european_2d', 'GFX_idea_generic_navy_fleet_log_middle_eastern_2d', 'GFX_idea_generic_navy_fleet_log_south_american_2d', 'GFX_idea_generic_navy_fleet_log_western_european_2d', 'GFX_idea_generic_navy_south_america_1', 'GFX_idea_generic_navy_south_america_2', 'GFX_idea_generic_navy_south_america_3', 'GFX_idea_generic_neutrality_drift_bonus', 'GFX_idea_generic_oppression', 'GFX_idea_generic_political_advisor_african_1', 'GFX_idea_generic_political_advisor_african_2', 'GFX_idea_generic_political_advisor_african_3', 'GFX_idea_generic_political_advisor_arab_1', 'GFX_idea_generic_political_advisor_arab_2', 'GFX_idea_generic_political_advisor_arab_3', 'GFX_idea_generic_political_advisor_asia_1', 'GFX_idea_generic_political_advisor_asia_2', 'GFX_idea_generic_political_advisor_asia_3', 'GFX_idea_generic_political_advisor_europe_1', 'GFX_idea_generic_political_advisor_europe_2', 'GFX_idea_generic_political_advisor_europe_3', 'GFX_idea_generic_political_advisor_europe_4', 'GFX_idea_generic_political_advisor_europe_5', 'GFX_idea_generic_political_advisor_europe_6', 'GFX_idea_generic_political_advisor_india_1', 'GFX_idea_generic_political_advisor_india_2', 'GFX_idea_generic_political_advisor_south_america_1', 'GFX_idea_generic_political_advisor_south_america_2', 'GFX_idea_generic_political_advisor_south_america_3', 'GFX_idea_generic_political_support', 'GFX_idea_generic_pp_unity_bonus', 'GFX_idea_generic_production_bonus', 'GFX_idea_generic_purge', 'GFX_idea_generic_refining_concern_1', 'GFX_idea_generic_research_bonus', 'GFX_idea_generic_reserve_divisions', 'GFX_idea_generic_sea_focused_navy', 'GFX_idea_generic_secret_police', 'GFX_idea_generic_spy_coup', 'GFX_idea_generic_spy_intel', 'GFX_idea_generic_spy_political', 'GFX_idea_generic_tank_manufacturer_1', 'GFX_idea_generic_tank_manufacturer_2', 'GFX_idea_generic_tank_manufacturer_3', 'GFX_idea_generic_the_london_naval_treaty', 'GFX_idea_generic_victors_of_ww1', 'GFX_idea_generic_volunteer_expedition_bonus', 'GFX_idea_generic_wall_line', 'GFX_idea_generic_war_industrialist_african_2d', 'GFX_idea_generic_war_industrialist_asian_2d', 'GFX_idea_generic_war_industrialist_commonwealth_2d', 'GFX_idea_generic_war_industrialist_eastern_european_2d', 'GFX_idea_generic_war_industrialist_middle_eastern_2d', 'GFX_idea_generic_war_industrialist_south_american_2d', 'GFX_idea_generic_war_industrialist_western_european_2d', 'GFX_idea_generic_war_preparation', 'GFX_idea_german_advisors'])

STATS = {}


def check_continuous_focus_layout():
    """Палитра вечных фокусов должна стоять по центру ниже всего дерева."""
    focus_spacing = (96, 130)       # interface/nationalfocusview.gui
    focus_item = (165, 128)
    palette_size = (770, 380)
    safe_gap = 100

    paths = list(walk('common/national_focus', ('.txt',)))
    target = next((p for p in paths if os.path.basename(p) == 'GLP_focus.txt'), None)
    if target is None:
        err("common/national_focus/GLP_focus.txt отсутствует")
        return
    body = strip_comments(read(target))
    pos = re.search(
        r'continuous_focus_position\s*=\s*\{\s*x\s*=\s*(-?\d+)\s+y\s*=\s*(-?\d+)\s*\}',
        body)
    if not pos:
        err(f"{rel(target)}: нет continuous_focus_position")
        return
    palette_x, palette_y = map(int, pos.groups())

    coordinates = []
    for block in re.finditer(r'\bfocus\s*=\s*\{(.*?)\n\t\}', body, re.S):
        b = block.group(1)
        if re.search(r'\brelative_position_id\s*=', b):
            # В GLP сейчас абсолютная сетка; не делаем неверных вычислений,
            # если будущая ветка перейдёт на относительные координаты.
            continue
        x = re.search(r'^\s*x\s*=\s*(-?\d+)', b, re.M)
        y = re.search(r'^\s*y\s*=\s*(-?\d+)', b, re.M)
        if x and y:
            coordinates.append((int(x.group(1)), int(y.group(1))))
    if not coordinates:
        err(f"{rel(target)}: не удалось определить координаты фокусов")
        return

    left = min(x for x, _ in coordinates) * focus_spacing[0]
    right = max(x for x, _ in coordinates) * focus_spacing[0] + focus_item[0]
    bottom = max(y for _, y in coordinates) * focus_spacing[1] + focus_item[1]
    tree_center = (left + right) / 2
    palette_center = palette_x + palette_size[0] / 2

    if abs(tree_center - palette_center) > 1:
        err(f"{rel(target)}: панель вечных фокусов не по центру "
            f"(центр дерева {tree_center:.1f}, центр панели {palette_center:.1f})")
    if palette_y < bottom + safe_gap:
        err(f"{rel(target)}: панель вечных фокусов наезжает на дерево "
            f"(y={palette_y}, нужно не меньше {bottom + safe_gap})")

    STATS['continuous_focus_position'] = (palette_x, palette_y)


def check_focus_icons():
    """Каждый фокус: иконка есть и это ванильный base-game спрайт."""
    for p, body in all_script_text('common/national_focus').items():
        for blk in re.finditer(r'\tfocus\s*=\s*\{(.*?)\n\t\}', body, re.S):
            b = blk.group(1)
            fid = re.search(r'id\s*=\s*([A-Za-z0-9_]+)', b)
            ic = re.search(r'icon\s*=\s*(GFX_\w+)', b)
            if not ic:
                err(f"{rel(p)}: фокус '{fid.group(1) if fid else '?'}' без иконки")
                continue
            if ic.group(1) not in VANILLA_FOCUS_ICONS:
                err(f"{rel(p)}: фокус '{fid.group(1)}' использует неванильную "
                    f"или DLC-зависимую иконку '{ic.group(1)}'")
    icons = [m.group(1) for p, b in all_script_text('common/national_focus').items()
             for m in re.finditer(r'icon\s*=\s*(GFX_\w+)', b)]
    STATS['focus_icons'] = (len(icons), len(set(icons)))


def check_idea_pictures():
    """Каждый национальный дух использует тематическую валидную иконку."""
    actual = {}
    for p, body in all_script_text('common/ideas').items():
        for m in re.finditer(r'^\t\t(GLP_\w+)\s*=\s*\{(.*?)^\t\t\}', body, re.M | re.S):
            iid, blk = m.group(1), m.group(2)
            pic = re.search(r'picture\s*=\s*([^\s#}\"]+)', blk)
            if not pic:
                err(f"{rel(p)}: идея '{iid}' без picture")
                continue
            name = pic.group(1)
            actual[iid] = name

    mapping_path = os.path.join(ROOT, 'tools/idea_pictures.tsv')
    expected = {}
    if os.path.exists(mapping_path):
        for line_no, line in enumerate(read(mapping_path).splitlines(), 1):
            if not line or line.startswith('#') or line == 'idea\tpicture':
                continue
            cols = line.split('\t')
            if len(cols) == 2:
                expected[cols[0]] = cols[1]

    for iid in sorted(set(actual) - set(expected)):
        err(f"tools/idea_pictures.tsv: нет строки для идеи '{iid}'")
    for iid in sorted(set(expected) - set(actual)):
        err(f"tools/idea_pictures.tsv: лишняя/неизвестная идея '{iid}'")
    for iid in sorted(set(actual) & set(expected)):
        if actual[iid] != expected[iid]:
            err(f"tools/idea_pictures.tsv: '{iid}' -> {expected[iid]}, "
                f"но в идеях указано {actual[iid]}")

    pics = list(actual.values())
    STATS['idea_pictures'] = (len(pics), len(pics), len(set(pics)))



def check_event_pictures():
    """Все картинки событий -- ванильный формат 397x153 (как news_event_001.dds)."""
    for p in glob_dds('gfx/event_pictures'):
        info = dds_info(p)
        if not info:
            err(f"{rel(p)}: not a valid DDS file")
            continue
        w, h, fmt = info
        if (w, h) != (397, 153):
            err(f"{rel(p)}: {w}x{h} -- ванильный формат картинок событий 397x153 "
                f"(иначе окно новости растягивает картинку)")
        if fmt not in ('ARGB8888', 'DXT5', 'DXT1'):
            err(f"{rel(p)}: compression {fmt} unsupported")


def check_idea_icon_geometry():
    """Кастомные иконки идей 60x68 (как ванильные generic_*.dds), советники 65x67."""
    for p in walk('gfx/interface/ideas', ('.dds',)):
        info = dds_info(p)
        if not info:
            continue
        w, h, _ = info
        base = os.path.basename(p)
        if re.match(r'idea_GLP_[a-z]', base) and (w, h) != (60, 68):
            err(f"{rel(p)}: иконка идеи {w}x{h}, ванильный формат 60x68")


def check_gui_overrides():
    """Проверяет окно загрузки и полноту ванильных event windows."""
    p = os.path.join(ROOT, 'interface/load_screen.gui')
    if not os.path.exists(p):
        err("interface/load_screen.gui отсутствует -- цитаты не будут оформлены")
    else:
        body = strip_comments(read(p))
        for token in ('"load_screen"', '"status"', '"tip"', '"text"', '"progressbar"'):
            if token not in body:
                err(f"interface/load_screen.gui: отсутствует элемент {token}")
        if 'GFX_loadingtip_bg' not in body or 'bg_load_screen' not in body:
            err("interface/load_screen.gui: нет ванильной плашки bg_load_screen / GFX_loadingtip_bg")

        # Окно "tip" повторяет ванильный layout: 1024x200 (CENTER_DOWN),
        # плашка на x=-700/y=-147, текст loadscreen_tip на x=-450/y=-157.
        # Кастомная подложка-карточка не используется.
        required = (
            'position = { x = 0 y = 0 }',
            'size = { x = 1024 y = 200 }',
            'Orientation = "CENTER_DOWN"',
            'position = { x = -700 y = -147 }',
            'position = { x = -450 y = -157 }',
            'font = "loadscreen_tip"',
            'maxWidth = 900',
            'maxHeight = 200',
        )
        for token in required:
            if token not in body:
                err(f"interface/load_screen.gui: нарушена ванильная спецификация цитаты -> {token}")

        if 'GFX_GLP_loading_tip_journal_bg' in body:
            err("interface/load_screen.gui: кастомная подложка GFX_GLP_loading_tip_journal_bg "
                "не должна использоваться — блок цитаты должен выглядеть как в ваниле")

    gfx = os.path.join(ROOT, 'interface/load_screen.gfx')
    if os.path.exists(gfx):
        gbody = strip_comments(read(gfx))
        if 'GFX_GLP_loading_tip_journal_bg' in gbody:
            err("interface/load_screen.gfx: кастомная подложка GFX_GLP_loading_tip_journal_bg "
                "не должна определяться")
        m = re.search(r'name\s*=\s*"GFX_loadingtip_bg"[^{}]*?texturefile\s*=\s*"([^"]+)"', gbody)
        if not m:
            err("interface/load_screen.gfx: GFX_loadingtip_bg не определён")
        elif m.group(1) != 'gfx/interface/Loadingscreen_loadingtip.dds':
            err("interface/load_screen.gfx: GFX_loadingtip_bg -> " + m.group(1) +
                ", ожидается ванильная gfx/interface/Loadingscreen_loadingtip.dds")

    if os.path.exists(os.path.join(ROOT, 'interface/loadingscreen.gui')):
        err("interface/loadingscreen.gui: пустой файл с неванильным именем -- удалить")
    p = os.path.join(ROOT, 'interface/eventwindow.gui')
    if os.path.exists(p):
        body = read(p)
        for token in ('"EventWindow"', '"EventWindow_Operative"', '"EventWindow_leader"',
                      '"EventWindow_News"', '"event_option_entry"'):
            if token not in body:
                err(f"interface/eventwindow.gui: отсутствует ванильное окно {token}")
        # Шрифты окон событий обязаны быть ванильными: hoi4_typewriter22 (заголовки),
        # hoi4_typewriter16 (описания), hoi_20bs (кнопки выборов).
        for want_font in ('hoi4_typewriter22', 'hoi4_typewriter16', 'hoi_20bs'):
            if f'font = "{want_font}"' not in body:
                err(f"interface/eventwindow.gui: нет ванильного шрифта {want_font} "
                    "-- окна событий должны использовать стандартные шрифты")

    # ------------------------------------------------------------------
    #  Оверрайды «чистых портретов»: из списков командиров и карточек
    #  советников убраны значки, которые движок рисует поверх/у портрета
    #  (HQ-бейдж, иконки черт, иконки типа соединения, полоски ролей).
    # ------------------------------------------------------------------
    #  Проверка целостности контейнеров в unitleaderwindow, countrypoliticsview,
    #  countryofficercorpview.
    # ------------------------------------------------------------------
    required_containers = {
        'interface/unitleaderwindow.gui': ('"armyleaderentry"', '"divisionleaderentry"'),
        'interface/countrypoliticsview.gui': ('"political_idea_entry"', '"political_selectable_idea_entry_grid"',
                                              '"political_selectable_idea_entry_list"'),
        'interface/countryofficercorpview.gui': ('"country_view_advisor_entry"', '"high_command_entry"',
                                                 '"army_chief_entry"', '"navy_chief_entry"', '"air_chief_entry"',
                                                 '"theorist_entry"')
    }
    for rel, required in required_containers.items():
        p = os.path.join(ROOT, rel)
        if not os.path.exists(p):
            err(f"{rel} отсутствует")
            continue
        body = strip_comments(read(p))
        for token in required:
            if token not in body:
                err(f"{rel}: отсутствует ванильный контейнер {token}")


def check_event_window_stress_and_adaptiveness():
    """Стресс-тест и проверка адаптивности окон новостей и ивентов (русский текст, скроллбары, современные окна)."""
    p = os.path.join(ROOT, 'interface/eventwindow.gui')
    if os.path.exists(p):
        body = read(p)
        # Проверяем, что все типы окон событий имеют скроллбары для длинного текста (адаптивность под русский язык)
        windows = ['EventWindow', 'EventWindow_Operative', 'EventWindow_leader', 'EventWindow_News']
        for w in windows:
            if w not in body:
                err(f"interface/eventwindow.gui: окно {w} отсутствует")
        
        # Проверяем наличие standardtext_slider для адаптивного скролла описаний
        if body.count('scrollbarType = standardtext_slider') < 2:
            err("interface/eventwindow.gui: описания событий должны поддерживать скролл (standardtext_slider) для адаптивности длинных текстов")

    # Убеждаемся, что окно загрузки (О несторе махно в начале игры) НЕ затронуто и не изменено
    load_gui = os.path.join(ROOT, 'interface/load_screen.gui')
    if os.path.exists(load_gui):
        lbody = strip_comments(read(load_gui))
        if 'tip' not in lbody or 'loadscreen_tip' not in lbody:
            err("interface/load_screen.gui: окно загрузки (нестор махно) не должно повреждаться")


def check_advisor_portraits(defs):
    """Каждый персонаж с ролью advisor обязан иметь portraits."""
    sprites = set(defs['sprite'])
    for p, body in all_script_text('common/characters').items():
        for m in re.finditer(r'^\t(GLP_\w+)\s*=\s*\{(.*?)^\t\}', body, re.M | re.S):
            cid, blk = m.group(1), m.group(2)
            has_portraits = re.search(r'portraits\s*=\s*\{', blk)
            if not has_portraits:
                err(f"{rel(p)}: персонаж '{cid}' без portraits")
                continue
            for s in re.findall(r'(GFX_portrait_\w+)', blk):
                if s not in sprites:
                    err(f"{rel(p)}: персонаж '{cid}' -> спрайт '{s}' не объявлен")
    STATS['characters'] = len(re.findall(r'^\tGLP_\w+\s*=\s*\{',
                                          list(all_script_text('common/characters').values())[0], re.M))


# Каталог gfx/models/units/ хранит импортированные бинарники Revolution or
# Reaction: Rise of Russia: всадник-донской казак DON_cavalry (модель конницы
# Гуляйполя) и пехота-матрос RSR_marine. Краш итерации 4-6 был вызван не
# самими моделями, а сборкой кавалерийских сущностей через clone ванильных
# cavalry-сущностей; после перехода на явные определения (паттерн DON_*-блока
# из YR_units_cavalry.asset) импорт работает. Список обязателен для
# check_unit_models, а граф сущностей целиком проверяет check_entity_graph.


EXPECTED_UNIT_MODEL_FILES = (
    'gfx/entities/GLP_units.asset',
    'gfx/entities/GLP_units.gfx',
    'gfx/models/units/GLP_cavalry_animations.asset',
    'gfx/models/units/RSR_marine.mesh',
    'gfx/models/units/RSR_marine_diffuse.dds',
    'gfx/models/units/RSR_marine_normal.dds',
    'gfx/models/units/RSR_marine_spec.dds',
    'gfx/models/units/DON_cavalry.mesh',
    'gfx/models/units/DON_cavalry_diffuse.dds',
    'gfx/models/units/DON_cavalry_normal.dds',
    'gfx/models/units/DON_cavalry_specular.dds',
    'gfx/models/units/russian_sword_sabre.mesh',
    'gfx/models/units/russian_sword_sabre_holder.mesh',
    'gfx/models/units/russian_sword_sabre_diffuse.dds',
    'gfx/models/units/russian_sword_sabre_normal.dds',
    'gfx/models/units/russian_sword_sabre_spec.dds',
    'gfx/models/units/CHI_sword_sabre_diffuse.dds',
    'gfx/models/units/CHI_sword_sabre_normal.dds',
    'gfx/models/units/CHI_sword_sabre_spec.dds',
    'gfx/models/units/russian_infantry_cavalry_rider_attack_sabre.anim',
    'gfx/models/units/russian_infantry_cavalry_rider_attack_sabre_idle.anim',
    'gfx/models/units/russian_infantry_cavalry_rider_idle_sabre.anim',
    'gfx/models/units/russian_infantry_cavalry_rider_moving_sabre.anim',
    'gfx/models/units/russian_infantry_cavalry_rider_retreat_sabre.anim',
)


# ------------------------------------------------------ 16. иконки дивизий
# Род войск, который «рисует» иконку шаблона. HOI4 берёт иконку под-юнита с
# НАИБОЛЬШИМ priority среди линейных батальонов (колонки combat_support --
# артполки, ПТО, ПВО -- род войск не определяют). Поэтому конница с танковым
# батальоном без template_counter показывает ТАНК, а не коня.
# Приоритеты -- дамп ванили 1.14.1, common/units/*.txt.
SUBUNIT_ICON = {
    # name: (priority, группа, семья-иконка)
    'infantry':                  (600,  'infantry',              'foot'),
    'bicycle_battalion':         (600,  'infantry',              'foot'),
    'marine':                    (601,  'infantry',              'marine'),
    'marine_commando':           (601,  'infantry',              'marine'),
    'mountaineers':              (601,  'infantry',              'mountain'),
    'paratrooper':               (2,    'infantry',              'para'),
    'militia':                   (400,  'infantry',              'foot'),
    'irregular_infantry':        (400,  'infantry',              'foot'),
    'penal_battalion':           (400,  'infantry',              'foot'),
    'cavalry':                   (599,  'mobile',                'horse'),
    'camelry':                   (599,  'mobile',                'horse'),
    'motorized':                 (599,  'mobile',                'truck'),
    'bus':                       (1000, 'mobile',                'truck'),
    'mechanized':                (610,  'mobile',                'truck'),
    'amphibious_mechanized':     (610,  'mobile',                'truck'),
    'armored_car':               (501,  'mobile',                'truck'),
    'light_armor':               (2501, 'armor',                 'tank'),
    'medium_armor':              (2502, 'armor',                 'tank'),
    'heavy_armor':               (2503, 'armor',                 'tank'),
    'modern_armor':              (2510, 'armor',                 'tank'),
    'super_heavy_armor':         (2510, 'armor',                 'tank'),
    'amphibious_armor':          (2501, 'armor',                 'tank'),
    'artillery_brigade':         (1198, 'combat_support',        'foot'),
    'mot_artillery_brigade':     (1198, 'mobile_combat_support', 'foot'),
    'rocket_artillery_brigade':  (1199, 'combat_support',        'foot'),
    'mot_rocket_artillery_brigade': (1199, 'mobile_combat_support', 'foot'),
    'anti_tank_brigade':         (1197, 'combat_support',        'foot'),
    'mot_anti_tank_brigade':     (1197, 'mobile_combat_support', 'foot'),
    'anti_air_brigade':          (301,  'combat_support',        'foot'),
    'mot_anti_air_brigade':      (301,  'mobile_combat_support', 'foot'),
    'light_sp_artillery_brigade':  (1795, 'armor_combat_support', 'tank'),
    'medium_sp_artillery_brigade': (1796, 'armor_combat_support', 'tank'),
    'heavy_sp_artillery_brigade':  (1797, 'armor_combat_support', 'tank'),
    'light_tank_destroyer_brigade':  (1795, 'armor_combat_support', 'tank'),
    'medium_tank_destroyer_brigade': (1796, 'armor_combat_support', 'tank'),
    'heavy_tank_destroyer_brigade':  (1797, 'armor_combat_support', 'tank'),
    'blackshirt_assault_battalion':  (0,   'support',              'foot'),
}
ICON_FAMILIES = ('foot', 'horse', 'truck', 'tank', 'marine', 'mountain', 'para')
# Словарь колонки depicts в tools/division_icons.tsv -> семья иконки
BRANCH_TO_FAMILY = {
    'cavalry': 'horse', 'infantry': 'foot', 'garrison': 'foot', 'militia': 'foot',
    'motorized': 'truck', 'mechanized': 'truck', 'armor': 'tank', 'marine': 'marine',
    'mountaineers': 'mountain', 'paratrooper': 'para',
    # GLP-тачанки: собственные силуэты (ванильного силуэта тачанки нет), но по
    # названию и по группе имён это та же «конная» семья, что у конницы.
    'tachanka': 'horse', 'armored_tachanka': 'horse',
}
# Собственные силуэты родов войск разрешены только для этих колонок depicts:
#  * flag            -- знамёна добровольцев (90/91);
#  * tachanka/armored_tachanka -- тачанки GLP (93/94), ванильного силуэта нет.
CUSTOM_TILE_DEPICTS = {'flag', 'tachanka', 'armored_tachanka'}
# Род войск по названию дивизии (ищет ВСЕ совпадения: «моторизованная
# тачаночная» = truck + horse, и этого достаточно, чтобы имя не противоречило
# группе имён).
NAME_FAMILIES = (
    (('конн', 'кавалер', 'тачан', 'казач', 'улан', 'драгун'),          'horse'),
    (('танк', 'бронетанк', 'бронеполк', 'автоброн'),                   'tank'),
    (('моториз', 'мото', 'автомоб', 'механизац'),                      'truck'),
    (('морск', 'матрос', 'черномор', 'флот'),                           'marine'),
    (('горн', 'альп'),                                                  'mountain'),
    (('параш', 'вдв', 'воздушно'),                                      'para'),
    (('стрелк', 'пехот', 'дружин', 'ополчен', 'самооборо', 'гарнизон',
      'охран', 'караул', 'страж', 'заслон'),                            'foot'),
)
SUPPORT_GROUPS = ('support', 'combat_support', 'mobile_combat_support',
                  'armor_combat_support')


def _block_body(text, start):
    """Тело {...}, открывающегося на text[start] == '{'; None при разъезде."""
    if start >= len(text) or text[start] != '{':
        return None
    i, depth = start, 0
    while i < len(text):
        if text[i] == '{':
            depth += 1
        elif text[i] == '}':
            depth -= 1
            if depth == 0:
                return text[start + 1:i]
        i += 1
    return None


def name_families(title):
    low = title.lower()
    fams = {fam for keys, fam in NAME_FAMILIES if any(k in low for k in keys)}
    # «десантная» сама по себе не род войск (высадка бывает морская и
    # воздушная) — уточняем только по морскому контексту, иначе молчим
    if 'десант' in low and any(k in low for k in ('морск', 'матрос', 'черномор',
                                                   'флот', 'керчен', 'одесс',
                                                   'севастоп')):
        fams.add('marine')
    return fams


def load_custom_subunits():
    """Свои sub_units мода: имя -> (priority, группа, семья-иконка)."""
    out = {}
    for p in walk('common/units', ('.txt',)):
        body = strip_comments(read(p))
        m = re.search(r'sub_units\s*=\s*\{', body)
        if not m:
            continue
        inner = _block_body(body, body.index('{', m.start()))
        if inner is None:
            continue
        for mm in re.finditer(r'^\s*(\w+)\s*=\s*\{', inner, re.MULTILINE):
            blk = _block_body(inner, inner.index('{', mm.start()))
            if not blk:
                continue
            prio = re.search(r'\bpriority\s*=\s*(\d+)', blk)
            grp = re.search(r'\bgroup\s*=\s*(\w+)', blk)
            if not prio or not grp:
                continue          # type = {...}, categories = {...}, террейн
            name = mm.group(1)
            if re.search(r'\bcavalry\s*=\s*yes', blk):
                fam = 'horse'
            elif grp.group(1) == 'armor':
                fam = 'tank'
            elif name in SUBUNIT_ICON:
                fam = SUBUNIT_ICON[name][2]
            else:
                fam = {'infantry': 'foot', 'mobile': 'truck',
                       'support': 'foot'}.get(grp.group(1), 'foot')
            out[name] = (int(prio.group(1)), grp.group(1), fam)
    return out


def load_name_groups():
    """Группы имён дивизий: имя -> (роды из division_types, список названий)."""
    groups = {}
    for p in walk('common/units/names_divisions', ('.txt',)):
        body = strip_comments(read(p))
        for m in re.finditer(r'^\s*(\w+)\s*=\s*\{', body, re.MULTILINE):
            blk = _block_body(body, body.index('{', m.start()))
            if not blk:
                continue
            dt = re.search(r'division_types\s*=\s*\{([^}]*)\}', blk)
            types = {t.strip('"') for t in dt.group(1).split()} if dt else set()
            fams = {SUBUNIT_ICON[t][2] for t in types if t in SUBUNIT_ICON}
            names = re.findall(r'\d+\s*=\s*\{\s*"([^"]+)"', blk)
            groups[m.group(1)] = (fams, names)
    return groups


def check_division_icons():
    """Иконка каждого шаблона дивизии обязана соответствовать его названию.

    Правила (реестр -- tools/division_icons.tsv):
      * template_counter обязан быть в реестре, его плитки -- определены как
        спрайты GFX_div_templ_N_large/_small;
      * род войск (depicts != flag) рисуется ГРАФИКОЙ БАЗОВОЙ ИГРЫ:
        gfx/interface/counters/divisions_large/unit_<depicts>_icon.dds и
        .../divisions_small/onmap_unit_<depicts>_icon.dds, noOfFrames = 2,
        путь зарегистрирован в VANILLA_TEXTURES. Собственный силуэт рода войск
        мод не рисует (он расходится с ванильным при каждом патче игры);
      * своя плитка 76x42 / 30x12 допустима только для depicts = flag;
      * counter с depicts != flag утверждает род войск -- он обязан совпасть
        с родом, который следует из названия шаблона и его группы имён;
      * без counter иконка = семья линейного батальона с максимальным
        priority -- она обязана совпасть с названием/группой имён;
      * каждое имя в группе имён обязано упоминать род своей группы.
    """
    registry = {}
    tsv = os.path.join(ROOT, 'tools/division_icons.tsv')
    if not os.path.exists(tsv):
        err('tools/division_icons.tsv: нет реестра иконок шаблонов дивизий')
        return
    for line in read(tsv).split('\n'):
        if not line.strip() or line.startswith('#') or line.startswith('counter\t'):
            continue
        parts = [x.strip() for x in line.split('\t')]
        if len(parts) < 4 or not parts[0].isdigit():
            err('tools/division_icons.tsv: строка не «counter\tlarge\tsmall'
                f'\tdepicts\t...»: {line}')
            continue
        registry[parts[0]] = dict(large=parts[1], small=parts[2],
                                  depicts=parts[3], used=0)

    sprites = {}
    for p in walk('interface', ('.gfx',)):
        body = strip_comments(read(p))
        for m in re.finditer(r'spriteType\s*=\s*\{([^}]*)\}', body, re.S):
            blk = m.group(1)
            nm = re.search(r'name\s*=\s*"(GFX_div_templ_\d+_(?:large|small))"',
                           blk)
            if not nm:
                continue
            tex = re.search(r'texturefile\s*=\s*"?([^"\s]+)"?', blk, re.I)
            frames = re.search(r'noOfFrames\s*=\s*(\d+)', blk, re.I)
            sprites[nm.group(1)] = (tex.group(1) if tex else '',
                                    int(frames.group(1)) if frames else 1)

    for n, row in sorted(registry.items()):
        if row['depicts'] != 'flag' and row['depicts'] not in BRANCH_TO_FAMILY:
            err(f'tools/division_icons.tsv: counter {n}: неизвестный depicts '
                f'«{row["depicts"]}» (можно семья иконки из {"/".join(ICON_FAMILIES)} '
                f'или flag)')
        for key, want in (('large', (76, 42)), ('small', (30, 12))):
            sprite = row[key]
            if sprite not in sprites:
                err(f'tools/division_icons.tsv: counter {n}: спрайт «{sprite}» '
                    f'не определён ни в одном interface/*.gfx')
                continue
            tex, frames = sprites[sprite]
            path = os.path.join(ROOT, tex)
            if not os.path.exists(path):
                # Иконка из базовой игры: единственный способ показать род
                # войск, не клонируя ванильные ассеты мода.
                mv = re.fullmatch(r'gfx/interface/counters/divisions_'
                                  r'(large|small)/(onmap_)?unit_([a-z_]+)_icon'
                                  r'\.dds', tex)
                if not mv:
                    err(f'tools/division_icons.tsv: counter {n}: {sprite} -> {tex} '
                        '— такой текстуры нет в моде, и это не ванильный силуэт '
                        'рода войск (gfx/interface/counters/divisions_'
                        '{large,small}/[onmap_]unit_<род>_icon.dds)')
                    continue
                if mv.group(1) != key:
                    err(f'counter {n}: {sprite} -> {tex}: плитку «{key}» берёт из '
                        f'папки divisions_{mv.group(1)}, а надо divisions_{key}')
                if (mv.group(2) is not None) != (key == 'small'):
                    err(f'counter {n}: {tex}: onmap_-силуэт принадлежит мелким '
                        'фишкам на карте (divisions_small); большую плитку '
                        'дизайнера им рисовать нельзя')
                if row['depicts'] in CUSTOM_TILE_DEPICTS:
                    err(f'counter {n}: {row["depicts"]} обязан использовать '
                        f'собственную плитку мода, а не ванильный силуэт '
                        f'«{mv.group(3)}» — {tex}')
                    continue
                if (BRANCH_TO_FAMILY.get(mv.group(3))
                        != BRANCH_TO_FAMILY.get(row['depicts'])):
                    err(f'counter {n}: {tex} — силуэт «{mv.group(3)}», а в '
                        f'tools/division_icons.tsv обещан род «{row["depicts"]}»')
                if tex not in VANILLA_TEXTURES:
                    err(f'counter {n}: {tex} — ссылка на графику базовой игры без '
                        'записи в VANILLA_TEXTURES (список «легально живёт в игре, '
                        'а не в моде»); добавь путь туда и укажи источник')
                if frames != 2:
                    err(f'counter {n}: {sprite} — ванильный атлас силуэтов идёт в '
                        '2 кадра, нужно noOfFrames = 2 (иначе движок сожмёт обе '
                        'иконки в одну плитку)')
                continue
            if row['depicts'] not in CUSTOM_TILE_DEPICTS:
                err(f'counter {n}: {tex} — собственный силуэт рода войск в моде '
                    'запрещён: для depicts != flag берётся графика базовой игры '
                    '(см. tools/division_icons.tsv)')
                continue
            info = dds_info(path)
            if not info:
                err(f'{tex}: не является DDS')
                continue
            w, h, fmt = info
            if (w, h) != want:
                err(f'{tex}: counter {n} — плитка {w}x{h}, движок ждёт плитку '
                    f'шаблона дивизии {want[0]}x{want[1]}')
            if fmt not in ('ARGB8888', 'DXT5'):
                err(f'{tex}: counter {n} — сжатие {fmt}, нужно ARGB8888 или DXT5')

    groups = load_name_groups()
    custom = load_custom_subunits()

    for grp, (fams, names) in sorted(groups.items()):
        if not fams:
            continue
        for div_name in names:
            nf = name_families(div_name)
            if nf and not (nf & fams):
                warn(f'группа имён {grp}: «{div_name}» называет другой род войск '
                     f'({"|".join(sorted(nf))}), чем сама группа '
                     f'({"|".join(sorted(fams))})')

    for d in ('history/units', 'common/on_actions', 'events', 'common/national_focus'):
        for p in walk(d, ('.txt',)):
            body = strip_comments(read(p))
            for m in re.finditer(r'division_template\s*=\s*\{', body):
                blk = _block_body(body, body.index('{', m.start()))
                if not blk:
                    continue
                nm = re.search(r'\bname\s*=\s*"([^"]+)"', blk)
                if not nm:
                    continue          # это ссылка division_template = "..."
                title = nm.group(1)
                regs = re.search(r'\bregiments\s*=\s*\{', blk)
                reg_body = _block_body(blk, regs.end() - 1) if regs else ''
                battalions = re.findall(r'(\w+)\s*=\s*\{\s*x\s*=\s*\d+\s+y\s*=\s*\d+\s*\}',
                                        reg_body or '')
                c = re.search(r'template_counter\s*=\s*(\d+)', blk)
                counter = c.group(1) if c else None
                g = re.search(r'division_names_group\s*=\s*(\w+)', blk)
                grp = g.group(1) if g else None

                if grp and grp not in groups:
                    err(f'{rel(p)}: шаблон «{title}» ссылается на группу имён '
                        f'{grp}, которой нет в common/units/names_divisions/')
                    continue

                nf = name_families(title)
                gf = groups[grp][0] if grp else set()
                if nf and gf and not (nf & gf):
                    warn(f'{rel(p)}: шаблон «{title}» называется как '
                         f'{"|".join(sorted(nf))}, но имена берёт из группы {grp} '
                         f'({"|".join(sorted(gf))})')
                want = (nf & gf) or gf or nf
                if not want:
                    continue

                if counter:
                    if counter not in registry:
                        err(f'{rel(p)}: шаблон «{title}»: template_counter = {counter} '
                            'нет в tools/division_icons.tsv — движок не найдёт '
                            f'спрайты GFX_div_templ_{counter}_large/_small, и у '
                            'дивизии не будет иконки')
                        continue
                    registry[counter]['used'] += 1
                    dep = registry[counter]['depicts']
                    if dep in CUSTOM_TILE_DEPICTS:
                        continue      # знамя/тачанка род войск не утверждает
                    got = BRANCH_TO_FAMILY.get(dep)
                    if got not in want:
                        err(f'{rel(p)}: шаблон «{title}» — иконка counter {counter} '
                            f'(«{dep}») не соответствует названию/группе имён '
                            f'(ожидается {"|".join(sorted(want))})')
                    continue

                scored = []
                for b in sorted(set(battalions)):
                    prio, grp_name, fam = (custom.get(b) or SUBUNIT_ICON.get(b)
                                           or (0, 'infantry', 'foot'))
                    if grp_name in SUPPORT_GROUPS:
                        continue      # колонки поддержки иконку не задают
                    scored.append((prio, fam, b))
                if not scored:
                    continue
                top = max(scored)
                if top[1] not in want:
                    others = [x for x in scored if x[1] in want]
                    hint = ''
                    if others:
                        hint = (f' — например, у «{others[0][2]}» priority '
                                f'{others[0][0]}, он проигрывает; нужен '
                                f'template_counter из tools/division_icons.tsv '
                                f'с плиткой «{sorted(want)[0]}»')
                    err(f'{rel(p)}: шаблон «{title}» — иконка не по названию: '
                        f'движок возьмёт силуэт «{top[2]}» (priority {top[0]} → '
                        f'{top[1]}), а ожидается {"|".join(sorted(want))}{hint}')

    for n, row in sorted(registry.items()):
        if not row['used']:
            warn(f'tools/division_icons.tsv: counter {n} («{row["depicts"]}») не '
                 f'используется ни одним шаблоном дивизии')


def _idea_defs_by_category():
    """common/ideas/*.txt -> {имя идеи: (категория, блок, «файл:строка»)}."""
    out = {}
    for p in walk('common/ideas', ('.txt',)):
        body = strip_comments(read(p))
        m = re.search(r'\bideas\s*=\s*\{', body)
        if not m:
            continue
        root = _block_body(body, m.end() - 1)
        if not root:
            continue
        for cm in re.finditer(r'^\t([a-z_][a-z_0-9]*)\s*=\s*\{', root, re.M):
            cat_body = _block_body(root, root.index('{', cm.start()))
            if not cat_body:
                continue
            for im in re.finditer(r'^\t\t([A-Za-z_][A-Za-z_0-9]*)\s*=\s*\{',
                                  cat_body, re.M):
                blk = _block_body(cat_body, cat_body.index('{', im.start()))
                out[im.group(1)] = (cm.group(1), blk or '',
                                    f'{os.path.basename(p)}:{cat_body.count(chr(10), 0, im.start())}')
    return out


def check_advisor_ideas(defs):
    """Советник без advisor-идеи = советник без бонусов (раздел 17).

    common/characters задаёт только КАДРА (слот, цена, черта для списка
    кандидатов); сами модификаторы живут в идее из common/ideas, объявленной в
    категории, имя которой равны слоту. Этот аудит уже ловил выдуманные имена
    черт, но не ловил отсутствующие идеи -- так «Щусь и Григорьев» имели
    советников без единого бонуса.
    """
    ideas = _idea_defs_by_category()
    known_traits = set(defs['trait']) | VANILLA_TRAITS
    foci = set(defs['focus'])
    seen = set()

    for p in sorted(walk('common/characters', ('.txt',))):
        body = strip_comments(read(p))
        for m in re.finditer(r'\badvisor\s*=\s*\{', body):
            blk = _block_body(body, body.index('{', m.start()))
            if not blk:
                continue
            line_no = body.count('\n', 0, m.start()) + 1
            who = f'{rel(p)}:{line_no}'
            slot = re.search(r'\bslot\s*=\s*(\S+)', blk)
            tok = re.search(r'\bidea_token\s*=\s*(\S+)', blk)
            if not slot:
                err(f'{who}: advisor-блок без slot')
                continue
            slot = slot.group(1)
            if slot not in ADVISOR_SLOTS:
                err(f'{who}: slot = {slot} — такого advisor-слота в базовой '
                    f'игре нет (законны: {", ".join(sorted(ADVISOR_SLOTS))}); '
                    'советник не встанет ни в одну ячейку ставки')
            traits = ' '.join(re.findall(r'traits\s*=\s*\{([^}]*)\}', blk, re.S))
            adv_traits = set(re.findall(r'[A-Za-z_][A-Za-z_0-9]*', traits))
            bad = sorted(t for t in adv_traits if t not in known_traits)
            if bad:
                err(f'{who}: advisor-черты {bad} не определены ни модом, ни в '
                    'базовой игре (см. tools/vanilla_trait_names.txt) — '
                    'советник наймётся без бонусов')
            if slot == 'high_command' and 'ledger' not in blk:
                warn(f'{who}: slot = high_command без ledger — советник '
                     'попадёт не во вкладку учёта')
            if not tok:
                continue
            token = tok.group(1)
            seen.add(token)
            if token not in ideas:
                err(f'{who}: idea_token = {token} — такой идеи нет ни в одном '
                    'common/ideas/*.txt; советник существует, но не даёт '
                    'ровно ничего (описать её нужно в категории, равной slot)')
                continue
            cat, iblk, where = ideas[token]
            if cat != slot:
                err(f'common/ideas: идея {token} объявлена в категории '
                    f'«{cat}», а персонаж ждёт её в слоте «{slot}» — '
                    'движок не свяжет советника с бонусами')
            if not re.search(r'\ballowed\s*=\s*\{', iblk):
                err(f'common/ideas: идея {token} без allowed — она будет '
                    'предложена всем странам, а не только GLP')
            i_traits = set(re.findall(
                r'[A-Za-z_][A-Za-z_0-9]*',
                ' '.join(re.findall(r'traits\s*=\s*\{([^}]*)\}', iblk, re.S))))
            if not i_traits and not re.search(r'\bmodifier\s*=\s*\{', iblk):
                err(f'common/ideas: идея {token} не даёт ни traits, ни '
                    'modifier — нанимать её не за что')
            if adv_traits - i_traits:
                err(f'common/ideas: идея {token} не даёт {sorted(adv_traits - i_traits)}, '
                    f'хотя персонаж ({who}) обещает эти черты в списке кандидатов')
            for t_ in sorted(i_traits - adv_traits):
                warn(f'common/ideas: идея {token} даёт черту «{t_}», которой нет '
                     f'у кандидата ({who}) — tooltip и реальные бонусы разойдутся')
            pic = re.search(r'\bpicture\s*=\s*([^\s#}\"]+)', iblk)
            if pic:
                pname = pic.group(1)
                if (f'GFX_idea_{pname}' not in VANILLA_IDEA_SPRITES
                        and not pname.startswith('SPR_')
                        and f'GFX_idea_{pname}' not in defs.get('sprite', set())):
                    err(f'common/ideas: идея {token}: picture = {pname} — '
                        'нет ни ванильного GFX_idea_*, ни спрайта мода')
            for fm in re.finditer(r'has_completed_focus\s*=\s*(\S+)', iblk):
                if fm.group(1) not in foci:
                    err(f'common/ideas: идея {token} требует фокус '
                        f'{fm.group(1)}, которого нет в common/national_focus — '
                        'советник нельзя будет нанять никогда')

    for token in sorted(set(ideas) - seen):
        cat = ideas[token][0]
        if cat in ADVISOR_SLOTS and token.startswith('GLP_'):
            warn(f'common/ideas: advisor-идея {token} (категория «{cat}») не '
                 'привязана ни к одному персонажу — мёртвый код')


def check_unit_models():
    """Донская казачья конница и пехота-матрос Rise of Russia должны быть на месте.

    Отдельно проверяется то, за чем пользователь приходил дважды: конные
    дивизии GLP обязаны стоять на модели ДОНСКИХ казаков (DON_cavalry), а не
    на ванильном всаднике, и каждый меш обязан находить свои .dds (иначе
    движок рисует белую болванку).
    """
    for fname in EXPECTED_UNIT_MODEL_FILES:
        p = os.path.join(ROOT, fname)
        if not os.path.exists(p):
            err(f"{fname}: отсутствует кастомная модель конницы/казаков")

    asset = os.path.join(ROOT, 'gfx/entities/GLP_units.asset')
    if os.path.exists(asset):
        body = strip_comments(read(asset))
        for name in ('GLP_infantry_entity', 'GLP_cavalry_entity', 'GLP_cavalry_2_entity'):
            if f'name = "{name}"' not in body:
                err(f"gfx/entities/GLP_units.asset: нет сущности '{name}'")
        if re.search(r'clone\s*=\s*"(cavalry_entity|cavalry_2_entity|generic_infantry_mg_rider_entity|infantry_rifle_entity)"', body):
            err("gfx/entities/GLP_units.asset: запрещён clone ванильной cavalry/infantry-сущности")

    # кавалерийские всадники мода = донские казаки
    gfx = os.path.join(ROOT, 'gfx/entities/GLP_units.gfx')
    if os.path.exists(gfx):
        gbody = strip_comments(read(gfx))
        for mesh in ('GLP_cavalry_mesh', 'GLP_cavalry_2_mesh'):
            m = re.search(r'pdxmesh\s*=\s*\{[^{}]*?name\s*=\s*"%s"[^{}]*?file\s*=\s*"([^"]+)"'
                          % re.escape(mesh), gbody, re.S)
            if not m:
                err(f"gfx/entities/GLP_units.gfx: pdxmesh '{mesh}' не найден — "
                    'у конных дивизий не будет модели донских казаков')
                continue
            if not m.group(1).endswith('DON_cavalry.mesh'):
                err(f"gfx/entities/GLP_units.gfx: '{mesh}' -> {m.group(1)}: "
                    'конница Гуляйполя обязана стоять на модели донских казаков '
                    'gfx/models/units/DON_cavalry.mesh')
        # каждый меш обязан находить текстуры, на которые ссылается изнутри
        for mm in re.finditer(r'pdxmesh\s*=\s*\{[^{}]*?file\s*=\s*"([^"]+)"', gbody, re.S):
            mp = os.path.join(ROOT, mm.group(1))
            if not os.path.exists(mp):
                continue
            deps = {d.decode() for d in
                    re.findall(rb'([A-Za-z0-9_]{4,60}\.dds)', open(mp, 'rb').read())}
            folder = os.path.dirname(mp)
            for dep in sorted(deps):
                if not os.path.exists(os.path.join(folder, dep)):
                    err(f"{rel(mp)}: меш ссылается на {dep}, которого нет в "
                        f"{rel(folder)}/ — текстуры импортированы под другим именем")


# ---------------------------------------------------------------- 11. entity graph
# Ванильные имена, разрешённые в сущностях мода (проверено по дампу базовой
# игры units_cavalry.asset/units_infantry.asset и RSR, 2026-08).
VANILLA_ENTITIES = set("""
    infantry_rifle_entity infantry_2_entity infantry_3_entity
    infantry_rider_entity generic_infantry_mg_rider_entity
    cavalry_entity cavalry_2_entity
    infantry_cavalry_horse_entity
    generic_cavalry_rifle_combined_entity generic_cavalry_mg_combined_entity
    camelry_entity
    GER_infantry_weapon_rifle_right_entity GER_infantry_weapon_rifle_left_entity
    GER_infantry_weapon_rifle_long_idle_entity
    GER_infantry_weapon_mg_right_entity GER_infantry_weapon_mg_left_entity
    GER_infantry_weapon_mg_long_idle_entity
""".split())

# Ванильные pdxmesh, используемые в attach/состояниях: известные id-анимации
# и ноды (по дампу infantry.gfx базовой игры).
VANILLA_MESH_ANIMS = {
    'infantry_cavalry_horse_mesh': {'cavalry_idle', 'cavalry_move',
                                    'cavalry_attack', 'cavalry_attack_2'},
    'infantry_cavalry_horse_frame_mesh': {'idle', 'move', 'attack'},
    'infantry_cavalry_camel_mesh': {'cavalry_idle', 'cavalry_move',
                                    'cavalry_attack', 'cavalry_attack_2'},
}
VANILLA_MESH_NODES = {
    'infantry_cavalry_horse_mesh': {'Saddle_Node'},
    'infantry_cavalry_horse_frame_mesh': set(),
    'infantry_cavalry_camel_mesh': {'Saddle_Node'},
}
# Минимальный набор id-анимаций для GLP-mesh пехоты: ванильный родительский
# entity (infantry_rifle_entity и др.) ссылається на эти стейты.
REQUIRED_INFANTRY_MESH_ANIMS = {
    'idle', 'attack', 'support_attack', 'move', 'march_move', 'retreat',
    'death', 'training', 'long_idle01',
}
_MESH_SECTION_KEYWORDS = {'pCubeShape4', 'mesh', 'aabb', 'material', 'skin',
                          'skeleton'}


def _mesh_bones(path):
    """Кости PDX-меша: строки вида [[Name внутри бинарника."""
    with open(path, 'rb') as fh:
        raw = fh.read()
    bones = set(re.findall(rb'\[\[([A-Za-z0-9_]+)', raw))
    return {b.decode() for b in bones} - _MESH_SECTION_KEYWORDS


def _parse_entity_blocks(body):
    """entity = { ... } -> {name: block} (вложенных entity не бывает)."""
    ents = {}
    for m in re.finditer(r'\bentity\s*=\s*\{', body):
        start = m.end()
        depth = 1
        i = start
        while i < len(body) and depth:
            if body[i] == '{':
                depth += 1
            elif body[i] == '}':
                depth -= 1
            i += 1
        blk = body[start:i - 1]
        nm = re.search(r'\bname\s*=\s*"([A-Za-z0-9_]+)"', blk)
        if nm:
            ents[nm.group(1)] = blk
    return ents


def check_entity_graph():
    """Глубокая проверка графа 3D-сущностей GLP (причина крашей рендера).

    Аудит ранее не проверял:
      * резолвится ли clone (GLP-entity или ванильный белый список);
      * резолвится ли pdxmesh (GLP-mesh или ванильный белый список);
      * каждая animation = "X" в state существует среди объявленных id
        данного pdxmesh (у ванильного меша -- по известному набору);
      * каждая attach-нода реально есть в бинарном .mesh (у ванильного
        меша -- по белому списку);
      * тип анимации в GLP_units.gfx -- GLP_* (собственный .asset) или
        GER_infantry_* (базовая игра).
    Плюс анти-паттерн `check_variable = { random ... }` во всех скриптах.
    """
    gfx_path = os.path.join(ROOT, 'gfx/entities/GLP_units.gfx')
    asset_path = os.path.join(ROOT, 'gfx/entities/GLP_units.asset')
    if not (os.path.exists(gfx_path) and os.path.exists(asset_path)):
        # Мод на ванильных моделях: gfx/entities/GLP_units.* удалены,
        # движок выбирает infantry_rifle_entity / cavalry_entity /
        # cavalry_2_entity по graphical_culture= eastern_european_gfx.
        # Граф сущностей ванили в дамп мода не входит и здесь не проверяется.
        return
    model_dir = os.path.join(ROOT, 'gfx/models/units')
    gfx_body = strip_comments(read(gfx_path))
    asset_body = strip_comments(read(asset_path))

    # mesh name -> {anims: set, file: path}
    meshes = {}
    for m in re.finditer(
            r'\bpdxmesh\s*=\s*\{[^{}]*?name\s*=\s*"(GLP_[A-Za-z0-9_]+)"(.*?)\n\t\}',
            gfx_body, re.S):
        name, blk = m.group(1), m.group(2)
        meshes[name] = {
            'anims': set(re.findall(r'animation\s*=\s*\{\s*id\s*=\s*"([A-Za-z0-9_]+)"', blk)),
            'file': (re.search(r'file\s*=\s*"([^"]+)"', blk) or [None, None])[1]
            if re.search(r'file\s*=\s*"([^"]+)"', blk) else None,
        }
    if not meshes:
        err(f"{rel(gfx_path)}: не найдено ни одной GLP pdxmesh")
        return

    # тип анимации в gfx: GLP_* (объявлен в GLP_cavalry_animations.asset)
    # или GER_infantry_* (базовая игра, проверено дампом generic mesh)
    anim_types = set(re.findall(r'type\s*=\s*"(GLP_[A-Za-z0-9_]+|GER_infantry_[A-Za-z0-9_]+)"', gfx_body))
    anim_decls = set(re.findall(
        r'animation\s*=\s*\{\s*name\s*=\s*"(GLP_[A-Za-z0-9_]+)"',
        strip_comments(read(os.path.join(model_dir, 'GLP_cavalry_animations.asset'))))) \
        if os.path.exists(os.path.join(model_dir, 'GLP_cavalry_animations.asset')) else set()
    for t in sorted(anim_types):
        if t.startswith('GLP_') and t not in anim_decls:
            err(f"{rel(gfx_path)}: animation type '{t}' не объявлен в GLP_cavalry_animations.asset")

    # бинарные ноды GLP-мешей
    mesh_nodes = {}
    for name, info in meshes.items():
        if info['file'] and os.path.exists(os.path.join(ROOT, info['file'])):
            mesh_nodes[name] = _mesh_bones(os.path.join(ROOT, info['file']))

    ents = _parse_entity_blocks(asset_body)
    glp_ents = set(ents)

    # Цепочка clone: кто наследует стейты ванильной пехоты
    # (infantry_rifle_entity / infantry_2_entity / infantry_3_entity) —
    # именно их меш обязан объявлять REQUIRED_INFANTRY_MESH_ANIMS.
    # (Кавалерийские "rider"-сущности не клонируют ванильную пехоту.)
    clone_map = {}
    for ename, blk in ents.items():
        cm = re.search(r'\bclone\s*=\s*"([A-Za-z0-9_]+)"', blk)
        clone_map[ename] = cm.group(1) if cm else None
    needs_infantry_anims = set()

    def _reaches_infantry_parent(name, depth=0):
        if depth > 8 or name in needs_infantry_anims:
            return name in needs_infantry_anims
        if name in ('infantry_rifle_entity', 'infantry_2_entity',
                    'infantry_3_entity'):
            needs_infantry_anims.add(name)
            return True
        parent = clone_map.get(name)
        return bool(parent and _reaches_infantry_parent(parent, depth + 1))
    for ename in list(ents):
        _reaches_infantry_parent(ename)

    for ename, blk in sorted(ents.items()):
        # 1) clone
        cm = re.search(r'\bclone\s*=\s*"([A-Za-z0-9_]+)"', blk)
        if cm:
            tgt = cm.group(1)
            if tgt not in glp_ents and tgt not in VANILLA_ENTITIES:
                err(f"{rel(asset_path)}: entity '{ename}': clone '{tgt}' — "
                    "нет ни среди сущностей мода, ни в ванильном белом списке "
                    "(кросс-файловые clone к cavalry-сущностям — источник краша)")
        # 2) pdxmesh
        pm = re.search(r'\bpdxmesh\s*=\s*"([A-Za-z0-9_]+)"', blk)
        mesh = pm.group(1) if pm else None
        if mesh and mesh not in meshes and mesh not in VANILLA_MESH_ANIMS:
            err(f"{rel(asset_path)}: entity '{ename}': pdxmesh '{mesh}' — "
                "не объявлен в GLP_units.gfx и не ванильный")
        # 3) анимации в явных state должны существовать у pdxmesh
        if mesh:
            allowed = (meshes.get(mesh, {}).get('anims')
                       if mesh in meshes else
                       VANILLA_MESH_ANIMS.get(mesh, set()))
            for am in re.finditer(r'\bstate\s*=\s*\{[^}]*?animation\s*=\s*"([A-Za-z0-9_]+)"', blk):
                if am.group(1) not in allowed:
                    err(f"{rel(asset_path)}: entity '{ename}': state "
                        f"animation '{am.group(1)}' не объявлен у меша '{mesh}'")
        # 4) attach: ноды в бинарном меше + цель attach
        for att in re.finditer(r'\battach\s*=\s*\{\s*name\s*=\s*"[A-Za-z0-9_]+"\s+'
                               r'([A-Za-z0-9_]+|infantry|cavalry|horse)\s*=\s*"(?P<t>[A-Za-z0-9_]+)"', blk):
            node, target = att.group(1), att.group('t')
            if node in ('infantry', 'cavalry', 'horse'):
                if target not in glp_ents and target not in VANILLA_ENTITIES:
                    err(f"{rel(asset_path)}: entity '{ename}': attach {node} "
                        f"-> '{target}' не определена")
                continue
            if mesh in mesh_nodes:
                if node not in mesh_nodes[mesh]:
                    err(f"{rel(asset_path)}: entity '{ename}': attach-нода "
                        f"'{node}' отсутствует в бинарном меше '{mesh}'")
            elif mesh in VANILLA_MESH_NODES:
                if node not in VANILLA_MESH_NODES[mesh]:
                    err(f"{rel(asset_path)}: entity '{ename}': attach-нода "
                        f"'{node}' не найдена у ванильного меша '{mesh}'")
            if target not in glp_ents and target not in VANILLA_ENTITIES:
                err(f"{rel(asset_path)}: entity '{ename}': attach -> "
                    f"'{target}' не определена")
        # 5) сущность, наследующая стейты ванильной пехоты (цепочка clone
        # до infantry_rifle_entity/infantry_2_entity), обязана стоять на
        # GLP-меше, объявляющем эти id-анимации
        if mesh in meshes and ename in needs_infantry_anims:
            missing = REQUIRED_INFANTRY_MESH_ANIMS - meshes[mesh]['anims']
            if missing:
                err(f"{rel(asset_path)}: entity '{ename}': меш '{mesh}' не "
                    f"объявляет {sorted(missing)} — унаследованные ванильные "
                    "стейты infantry_*_entity будут ссылаться на пустоту")

    STATS['entity_graph'] = (len(ents), len(meshes))

    # анти-паттерн: random не является переменной для check_variable
    for d in ('common', 'events', 'history'):
        for p in walk(d, ('.txt',)):
            body = strip_comments(read(p))
            for i, line in enumerate(body.split('\n'), 1):
                if re.search(r'check_variable\s*=\s*\{[^}]*\brandom\b', line):
                    err(f"{rel(p)}:{i}: check_variable сравнивает только "
                        f"set_variable-переменные; для шанса используйте "
                        f"'random = <процент>' как отдельный триггер")


def check_no_stray_art():
    """В gfx/ не должно быть мастер-файлов, кроме _src_* (источники сборки)."""
    for dirpath, _d, files in os.walk(os.path.join(ROOT, 'gfx')):
        for f in files:
            if f.lower().endswith(('.png', '.jpg', '.jpeg', '.tga')):
                relp = rel(os.path.join(dirpath, f))
                if relp.startswith('gfx/flags/'):
                    continue          # флаги HOI4 -- формат TGA by design
                if not f.startswith('_src_'):
                    err(f"{rel(os.path.join(dirpath, f))}: посторонний файл "
                        f"(мастеры называются _src_*.png/jpg)")


def check_loc_tech_names(loc):
    """В значениях локализации не должно быть технических имён."""
    for lang in ('russian', 'english'):
        p = os.path.join(ROOT, f'localisation/{lang}')
        for fp in walk(f'localisation/{lang}', ('.yml',)):
            for i, line in enumerate(read(fp).split('\n'), 1):
                m = re.match(r'^\s*[A-Za-z0-9_.\-]+:\d*\s*"(.*)"', line)
                if not m:
                    continue
                val = m.group(1)
                if re.search(r'GFX_\w+', val):
                    err(f"{rel(fp)}:{i}: в тексте видно техническое имя спрайта")
                if re.search(r'\b(GLP|GPL)_[a-z0-9_]+\b', val, re.IGNORECASE):
                    err(f"{rel(fp)}:{i}: в тексте видно техническое имя ключа GLP_*/GPL_*")


def _im_alpha_min(path):
    """Минимальная альфа пикселя через ImageMagick; None, если IM недоступен."""
    import shutil, subprocess
    if not shutil.which('convert'):
        return None
    try:
        o = subprocess.run(
            ['convert', path, '-alpha', 'extract',
             '-format', '%[fx:minima*255]', 'info:'],
            capture_output=True, text=True, timeout=30)
        return float(o.stdout.strip())
    except Exception:
        return None


def check_dds_transparency():
    """Духи (национальные идеи) — иконки БЕЗ персонажей — обязаны иметь
    реальные прозрачные пиксели (угловые пиксели не должны быть непрозрачными).
    Иконки советников-персонажей (idea_GLP_[A-Z]*) намеренно полностью
    непрозрачны: в build_portraits.sh они строятся как plain-portrait (alpha=100%),
    а рамку министра и значок роли рисует сам движок HOI4 поверх иконки.
    Проверку прозрачности применяем только к духам (idea_GLP_[a-z]*)."""
    import re as _re
    for p in sorted(walk('gfx/interface/ideas', ('.dds',))):
        base = os.path.basename(p)
        # Пропускаем иконки советников-персонажей (idea_GLP_<Имя> с заглавной буквы)
        if _re.match(r'^idea_GLP_[A-Z]', base):
            continue
        mn = _im_alpha_min(p)
        if mn is None:
            warn("ImageMagick недоступен -- пиксельная проверка прозрачности пропущена")
            return
        if mn >= 32.0:
            err(f"{rel(p)}: нет реальной прозрачности (min alpha = {mn:.0f}, "
                f"нужно < 32) -- иконка закроет слот непрозрачным квадратом")


def check_advisor_frames():
    """Совѣтники обязаны быть въ ванильной рамкѣ министра (тотъ же уголъ и
    размѣръ, что въ базовой игрѣ). Шаблоны -- изъ Ultimate-HOI4-GFX (Globvs):
    Minister_Base.png (рамка + карточка) и Minister_Background.png (наклонная
    подложка, задающая уголъ). Проверяем, что шаблоны на мѣстѣ (сборка
    воспроизводима: tools/build_portraits.sh) и что иконки совѣтниковъ
    обрѣзаны по наклонной маскѣ, а не сплошные."""
    for need in ('tools/_gfx_src/Minister_Base.png',
                 'tools/_gfx_src/Minister_Background.png'):
        if not os.path.exists(os.path.join(ROOT, need)):
            err(f"{need} отсутствует -- сборка рамок совѣтниковъ невоспроизводима")
    for p in sorted(walk('gfx/interface/ideas', ('.dds',))):
        base = os.path.basename(p)
        if not re.match(r'^idea_GLP_[A-Z]', base):
            continue
        info = dds_info(p)
        if info and (info[0], info[1]) != (65, 67):
            err(f"{rel(p)}: рамка совѣтника {info[0]}x{info[1]}, ваниль 65x67")


# ------------------------------------------------- 12. focus search filters
GENERIC_FOCUS_FILTERS = {
    'FOCUS_FILTER_POLITICAL', 'FOCUS_FILTER_RESEARCH', 'FOCUS_FILTER_INDUSTRY',
    'FOCUS_FILTER_STABILITY', 'FOCUS_FILTER_WAR_SUPPORT', 'FOCUS_FILTER_MANPOWER',
    'FOCUS_FILTER_ANNEXATION',
}


def _focus_blocks(path):
    """(focus_id, body) for every `focus = { ... }` in a focus-tree file."""
    text = strip_comments(read(path))
    out = []
    for m in re.finditer(r'\n\tfocus = \{', text):
        start, depth, j = m.end(), 1, m.end()
        while depth > 0 and j < len(text):
            if text[j] == '{':
                depth += 1
            elif text[j] == '}':
                depth -= 1
            j += 1
        body = text[start:j - 1]
        fid = re.search(r'^\s*id\s*=\s*(\S+)', body, re.M)
        if fid:
            out.append((fid.group(1), body))
    return out


def check_focus_search_filters():
    """Каждый фокус обязан быть видимым в поиске/фильтре окна фокусов.

    С 1.9 в окне национальных фокусов есть строка поиска и чипы-фильтры.
    Фокус попадает в выдачу только если у него объявлен
    `search_filters = { FOCUS_FILTER_* }`; в ванили эта строка есть у каждого
    фокуса. Без неё всё дерево невидимо для поиска -- чисто полировочный, но
    видимый игроком дефект. Допускаются только семь GENERIC-токенов:
    страновые/DLC-токены (CHI_INFLATION, USA_CONGRESS, TFV_AUTONOMY, MEX_*,
    SPA_*, FRA_*) дали бы бессмысленный чип в панели Гуляйполя.
    Соответствие tools/focus_search_filters.tsv обязательно.
    """
    tsv_path = os.path.join(ROOT, 'tools', 'focus_search_filters.tsv')
    table = {}
    if os.path.exists(tsv_path):
        with open(tsv_path, encoding='utf-8') as fh:
            for line in fh:
                if line.startswith('#') or not line.strip():
                    continue
                parts = line.rstrip('\n').split('\t')
                if len(parts) >= 2:
                    table[parts[0]] = set(parts[1].split())
    else:
        err("tools/focus_search_filters.tsv отсутствует -- не с чем сверять "
            "search_filters (tools/assign_focus_filters.py --write-tsv)")

    seen = 0
    for p in walk('common/national_focus', ('.txt',)):
        for fid, body in _focus_blocks(p):
            seen += 1
            m = re.search(r'^\s*search_filters\s*=\s*\{([^\n]*)\}', body, re.M)
            tokens = m.group(1).split() if m else []
            if not tokens:
                err(f"{rel(p)}: фокус '{fid}' без search_filters -- он не "
                    f"попадёт в поиск/фильтр окна фокусов")
                continue
            for tok in tokens:
                if tok not in GENERIC_FOCUS_FILTERS:
                    err(f"{rel(p)}: фокус '{fid}' использует не-generic токен "
                        f"фильтра '{tok}'")
            if fid in table and set(tokens) != table[fid]:
                err(f"{rel(p)}: фокус '{fid}' — search_filters {sorted(tokens)} "
                    f"не совпадает с tools/focus_search_filters.tsv "
                    f"{sorted(table[fid])}")
    STATS['focus_search_filters'] = seen


# ------------------------------------------------- 13. branch banner honesty
BRANCH_BANNER = re.compile(
    r'^\t# (?P<n>\d+)(?P<suffix>[a-z]?)\. (?P<name>.+?) '
    r'\((?P<count>\d+) фокус\w*, (?P<rest>[^)]*)\)\s*$')


def check_focus_branch_headers():
    """Баннеры веток в GLP_focus.txt обязаны говорить правду.

    Дерево разбито на 28 документированных веток; баннер каждой заявляет
    количество фокусов и диапазон координат. Эти числа разъезжались с
    реальностью (в сумме заявлялось 233 фокуса при 190 фактических, 21 счётчик
    и несколько диапазонов x/y были неверны) -- дизайнер, читающий шапку,
    планировал бы работу против несуществующего дерева.
    """
    for p in walk('common/national_focus', ('.txt',)):
        text = read(p)
        lines = text.split('\n')
        coords = {fid: (
            int(re.search(r'^\s*x\s*=\s*(-?\d+)', b, re.M).group(1)),
            int(re.search(r'^\s*y\s*=\s*(-?\d+)', b, re.M).group(1)))
            for fid, b in _focus_blocks(p)
            if re.search(r'^\s*x\s*=\s*-?\d+', b, re.M)
            and re.search(r'^\s*y\s*=\s*-?\d+', b, re.M)}

        branches, cur = [], None
        pending = False
        for i, ln in enumerate(lines):
            m = BRANCH_BANNER.match(ln)
            if m:
                cur = {'i': i, 'm': m, 'focuses': []}
                branches.append(cur)
                continue
            if ln.startswith('\tfocus = {') and cur is not None:
                cur['focuses'].append(None)
                pending = True
                continue
            if pending and cur is not None:
                mid = re.match(r'^\t\tid = (\S+)', ln)
                if mid:
                    cur['focuses'][-1] = mid.group(1)
                    pending = False
        if not branches:
            continue

        accounted = 0
        for br in branches:
            ids = [f for f in br['focuses'] if f]
            accounted += len(ids)
            declared = int(br['m'].group('count'))
            if declared != len(ids):
                err(f"{rel(p)}:{br['i'] + 1}: баннер ветки "
                    f"'{br['m'].group('n')}{br['m'].group('suffix')}' заявляет "
                    f"{declared} фокусов, фактически {len(ids)} "
                    f"(tools/sync_focus_headers.py --apply)")
            xs = [coords[f][0] for f in ids if f in coords]
            ys = [coords[f][1] for f in ids if f in coords]
            if xs and ys:
                want = 'x = %d..%d, y = %d..%d' % (min(xs), max(xs),
                                                  min(ys), max(ys))
                if br['m'].group('rest').strip() != want:
                    err(f"{rel(p)}:{br['i'] + 1}: баннер ветки "
                        f"'{br['m'].group('n')}{br['m'].group('suffix')}' "
                        f"заявляет диапазон '{br['m'].group('rest')}', "
                        f"фактически '{want}'")
        total = text.count('\n\tfocus = {')
        if accounted != total:
            err(f"{rel(p)}: баннеры покрывают {accounted} фокусов из {total} -- "
                f"часть фокусов лежит вне всех веток")
        STATS['focus_branches'] = (len(branches), accounted, total)
        if len(branches) < 6:
            warn(f"{rel(p)}: только {len(branches)} веток -- целевой стандарт "
                 f"DLC 6+")


# ------------------------------------------------- 14. idea modifier spelling
KNOWN_IDEA_MODIFIERS = {
    'air_cas_present_factor', 'air_naval_strike_attack_factor',
    'air_superiority_efficiency', 'army_armor_attack_factor',
    'army_attack_factor', 'army_core_attack_factor', 'army_core_defence_factor',
    'army_defence_factor', 'army_infantry_attack_factor', 'army_morale_factor',
    'army_org_factor', 'army_speed_factor', 'attrition', 'breakthrough_factor',
    'casualty_trickleback', 'cavalry_attack_factor', 'cavalry_defence_factor',
    'cavalry_speed_factor', 'compliance_growth', 'conscription_factor',
    'consumer_goods_factor', 'convoy_raiding_efficiency_factor',
    'decryption_factor', 'dig_in_speed_factor', 'drift_defence_factor',
    'encryption_factor', 'enemy_operative_detection_chance_factor',
    'enemy_partisan_effect', 'equipment_capture_factor',
    'experience_gain_army_factor', 'experience_gain_navy_factor',
    'foreign_subversive_activites', 'generate_wargoal_tension',
    'industrial_capacity_dockyard', 'industrial_capacity_factory',
    'industry_repair_factor', 'intel_network_gain_factor',
    'justify_war_goal_time', 'land_reinforce_rate', 'license_purchase_cost',
    'max_dig_in', 'max_planning', 'mobilization_speed', 'monthly_population',
    'naval_coordination', 'naval_hit_chance', 'navy_capital_ship_attack_factor',
    'navy_max_range_factor', 'navy_org_factor', 'navy_screen_attack_factor',
    'navy_submarine_attack_factor', 'neutrality_drift', 'operative_slot',
    'org_loss_when_moving', 'out_of_supply_factor', 'planning_speed',
    'political_power_cost', 'political_power_factor', 'political_power_gain',
    'production_factory_efficiency_gain_factor',
    'production_factory_max_efficiency_factor',
    'production_lack_of_resource_penalty_factor',
    'production_speed_arms_factory_factor',
    'production_speed_industrial_complex_factor',
    'production_speed_rail_way_factor', 'production_speed_supply_node_factor',
    'railway_gun_bombardment_factor', 'recon_factor', 'research_speed_factor',
    'resistance_damage_to_garrison', 'resistance_growth',
    'resistance_growth_on_our_occupied_states', 'resistance_target',
    'send_volunteer_divisions_required', 'send_volunteer_size',
    'send_volunteers_tension', 'special_forces_attack_factor',
    'special_forces_cap', 'special_forces_defence_factor', 'stability_factor',
    'subversive_activites_upkeep', 'supply_consumption_factor', 'supply_factor',
    'supply_node_range', 'trade_laws_cost_factor', 'trade_opinion_factor',
    'training_time_factor', 'war_support_factor',
}


def check_idea_modifier_keys():
    """Опечатка в ключе модификатора идеи молча ничего не даёт игроку.

    Движок не роняет ошибку на неизвестном ключе статического модификатора --
    он просто игнорирует его, поэтому «+10% к чему-то» может бесследно
    исчезнуть. Все 88 ключей, используемых GLP, сверены со списком
    статических модификаторов 1.19; неизвестный ключ = предупреждение.
    """
    used = set()
    for p, body in all_script_text('common/ideas').items():
        i = 0
        while True:
            m = re.search(r'\bmodifier = \{', body[i:])
            if not m:
                break
            start, depth, j = i + m.end(), 1, i + m.end()
            while depth > 0 and j < len(body):
                if body[j] == '{':
                    depth += 1
                elif body[j] == '}':
                    depth -= 1
                j += 1
            inner = body[start:j - 1]
            for key in re.findall(
                    r'^\s*([A-Za-z_][A-Za-z0-9_]*)\s*=\s*-?[\d.]+\s*$',
                    inner, re.M):
                used.add(key)
                if key not in KNOWN_IDEA_MODIFIERS:
                    warn(f"{rel(p)}: неизвестный ключ модификатора '{key}' -- "
                         f"движок его молча проигнорирует")
            i = j
    STATS['idea_modifier_keys'] = len(used)


def check_cinematic_intro_voice():
    """Проверяет полную цепочку автоматической озвучки заставки GLP.

    Проверка намеренно идёт от события до файла: наличие одного voice.ogg
    недостаточно, если asset не зарегистрирован или событие не вызывает
    sound_effect. В таком случае заставка открывается молча.
    """
    required = {
        'sound/gulyaipole_sounds.asset': (
            'name = "gulyaipole_intro_voice_file"',
            'file = "voice.ogg"',
            'name = "gulyaipole_intro_voice"',
        ),
        'events/GulyaipoleCinematicIntro.txt': (
            'set_country_flag = glp_show_cinematic_intro',
            'sound_effect = gulyaipole_intro_voice',
        ),
        'common/on_actions/GLP_on_actions.txt': (
            'country_event = { id = glp_cinematic_intro.1 }',
        ),
    }
    for path, tokens in required.items():
        text = read(os.path.join(ROOT, path))
        for token in tokens:
            if token not in text:
                err(f"intro voice: {path} не содержит обязательную запись {token!r}")

    voice_path = os.path.join(ROOT, 'sound/voice.ogg')
    if not os.path.isfile(voice_path):
        err('intro voice: отсутствует sound/voice.ogg')
    elif not open(voice_path, 'rb').read(4) == b'OggS':
        err('intro voice: sound/voice.ogg не является OGG-контейнером')

    # Радио-версия не должна иметь имя soundeffect: одинаковое имя делает
    # диагностику и поведение движка неоднозначными.
    music_asset_path = os.path.join(ROOT, 'music/music.asset')
    if os.path.exists(music_asset_path):
        music_asset = read(music_asset_path)
        if 'name = "gulyaipole_intro_voice"' in music_asset:
            err('intro voice: music и soundeffect используют одно имя gulyaipole_intro_voice')


def check_tachanka_technology_contract():
    """Validate the custom infantry-technology branch as an engine contract.

    The generic audit intentionally does not know every Clausewitz database
    key.  This focused check catches the two failures that made the branch
    appear to be present on disk while being absent in-game: the old
    ``enable_sub_units`` spelling, a root technology without an incoming
    path/gridbox anchor, globally active custom battalions, and templates or
    icons that do not resolve to the intended cavalry family.
    """
    tech_path = os.path.join(ROOT, 'common/technologies/GLP_technologies.txt')
    anchor_path = os.path.join(ROOT, 'common/technologies/zzz_GLP_tachanka_anchor.txt')
    equipment_path = os.path.join(ROOT, 'common/units/equipment/GLP_tachanka_equipment.txt')
    units_path = os.path.join(ROOT, 'common/units/GLP_white_units.txt')

    if not all(os.path.isfile(p) for p in (tech_path, anchor_path, equipment_path, units_path)):
        err('tachanka: missing one of the technology, anchor, equipment, or unit files')
        return

    tech = strip_comments(read(tech_path))
    anchor = strip_comments(read(anchor_path))
    equipment = strip_comments(read(equipment_path))
    units = strip_comments(read(units_path))

    def extract_block(text, key):
        """Return the first Clausewitz block whose key is *key*."""
        match = re.search(
            r'(?m)^\s*' + re.escape(key) + r'\s*=\s*\{', text)
        if not match:
            return None
        opening = text.find('{', match.start())
        depth = 0
        for index in range(opening, len(text)):
            if text[index] == '{':
                depth += 1
            elif text[index] == '}':
                depth -= 1
                if depth == 0:
                    return text[opening + 1:index]
        return None

    if 'enable_sub_units' in tech:
        err('common/technologies/GLP_technologies.txt: use enable_subunits, not enable_sub_units')
    if re.search(r'(?m)^\s*prerequisites\s*=', tech):
        err('common/technologies/GLP_technologies.txt: prerequisites is not a HOI4 technology key; use path/dependencies')

    expected_chain = [
        'GLP_tachanka_tech_1',
        'GLP_tachanka_tech_2',
        'GLP_tachanka_tech_3',
        'GLP_tachanka_tech_4',
    ]
    if not re.search(r'leads_to_tech\s*=\s*GLP_tachanka_tech_1\b', anchor):
        err('tachanka: root tech has no incoming path from a vanilla gridbox anchor')
    for current, following in zip(expected_chain, expected_chain[1:]):
        if f'leads_to_tech = {following}' not in tech:
            err(f'tachanka: {current} does not lead to {following}')

    for tech_id in expected_chain:
        body = extract_block(tech, tech_id)
        if body is None:
            err(f'tachanka: missing technology definition {tech_id}')
            continue
        if not re.search(r'folder\s*=\s*\{[^}]*name\s*=\s*infantry_folder', body, re.S):
            err(f'tachanka: {tech_id} is not assigned to infantry_folder')
        if not re.search(r'position\s*=\s*\{[^}]*x\s*=\s*-?\d+[^}]*y\s*=\s*-?\d+', body, re.S):
            err(f'tachanka: {tech_id} has no literal infantry-folder position')
        if not re.search(r'allow\s*=\s*\{[^}]*tag\s*=\s*GLP', body, re.S):
            err(f'tachanka: {tech_id} can be researched by a country other than GLP')

    if not re.search(r'allow_branch\s*=\s*\{[^}]*tag\s*=\s*GLP', tech, re.S):
        err('tachanka: root branch is not restricted to GLP')

    tech2 = extract_block(tech, 'GLP_tachanka_tech_2') or ''
    if 'load_oob = "unlock_armored_tachankas"' not in tech2:
        err('tachanka: tech 2 does not create the armored-tachanka division template')
    armored_oob_path = os.path.join(ROOT, 'history/units/unlock_armored_tachankas.txt')
    if not os.path.isfile(armored_oob_path):
        err('tachanka: missing history/units/unlock_armored_tachankas.txt')
    else:
        armored_oob = strip_comments(read(armored_oob_path))
        if 'armored_tachanka' not in armored_oob:
            err('tachanka: armored template does not contain armored_tachanka regiments')
        if not re.search(r'template_counter\s*=\s*94', armored_oob):
            err('tachanka: armored template has no tachanka template_counter = 94')

    equipment_ids = set(re.findall(r'(?m)^\s*((?:armored_)?tachanka_equipment(?:_\d+)?)\s*=\s*\{', equipment))
    if 'tachanka_equipment' not in equipment_ids:
        err('tachanka: missing tachanka_equipment archetype')
    if 'armored_tachanka_equipment' not in equipment_ids:
        err('tachanka: missing armored_tachanka_equipment archetype')
    variant_bodies = {}
    for number, parent in zip(range(1, 5), ['tachanka_equipment', None,
                                             'tachanka_equipment_2', 'tachanka_equipment_3']):
        eid = f'tachanka_equipment_{number}'
        body = extract_block(equipment, eid)
        if body is None:
            err(f'tachanka: missing equipment variant {eid}')
            continue
        variant_bodies[eid] = body
        expected_arch = 'tachanka_equipment' if number == 1 else 'armored_tachanka_equipment'
        if not re.search(rf'(?m)^\s*archetype\s*=\s*{re.escape(expected_arch)}\s*$', body):
            err(f'tachanka: {eid} is not attached to {expected_arch} archetype')
        if number > 1 and parent is not None and not re.search(
                rf'(?m)^\s*parent\s*=\s*{re.escape(parent)}\s*$', body):
            err(f'tachanka: {eid} must inherit from {parent}')

    # Combat values belong to equipment, as they do for vanilla tanks.  Check
    # effective inherited values as well as the monotonic progression of the
    # four variants, so a future edit cannot silently remove armor/attack.
    # The armored archetype must carry armor_value/hardness: the division
    # designer reads the battalion armor from the equipment family archetype,
    # so a numeric zero there is what caused "no armor in division".
    archetype_body = extract_block(equipment, 'tachanka_equipment') or ''
    armored_archetype_body = extract_block(equipment, 'armored_tachanka_equipment') or ''
    combat_stats = (
        'maximum_speed', 'reliability', 'hardness', 'soft_attack', 'hard_attack',
        'defense', 'breakthrough', 'ap_attack', 'armor_value',
        'fuel_consumption', 'build_cost_ic',
    )

    def flat_stat(body, key):
        match = re.search(r'(?m)^\s*' + re.escape(key) + r'\s*=\s*(-?[0-9]+(?:\.[0-9]+)?)', body)
        if match:
            return float(match.group(1))
        return None

    if not armored_archetype_body:
        err('tachanka: armored_tachanka_equipment archetype is empty')
    else:
        armor_arch = flat_stat(armored_archetype_body, 'armor_value')
        if armor_arch is None or armor_arch < 6:
            err('tachanka: armored_tachanka_equipment archetype has armor_value below 6')
        hardness_arch = flat_stat(armored_archetype_body, 'hardness')
        if hardness_arch is None or hardness_arch <= 0:
            err('tachanka: armored_tachanka_equipment archetype has non-positive hardness')
        if flat_stat(archetype_body, 'armor_value') not in (0, None):
            err('tachanka: plain tachanka_equipment archetype must stay unarmored (armor_value 0)')

    def stat_value(body, key):
        if body in (archetype_body, armored_archetype_body):
            return flat_stat(body, key)
        match = re.search(r'(?m)^\s*' + re.escape(key) + r'\s*=\s*(-?[0-9]+(?:\.[0-9]+)?)', body)
        if match:
            return float(match.group(1))
        # Fall back to the archetype the variant declares.
        fallback = armored_archetype_body if re.search(
            r'(?m)^\s*archetype\s*=\s*armored_tachanka_equipment\s*$', body) else archetype_body
        return flat_stat(fallback, key)

    effective = {}
    for number in range(1, 5):
        eid = f'tachanka_equipment_{number}'
        body = variant_bodies.get(eid)
        if body is None:
            continue
        effective[eid] = {}
        for key in combat_stats:
            value = stat_value(body, key)
            if value is None:
                err(f'tachanka: {eid} has no effective equipment stat {key}')
            else:
                effective[eid][key] = value
        for key in ('maximum_speed', 'build_cost_ic'):
            if key in effective[eid] and effective[eid][key] <= 0:
                err(f'tachanka: {eid} has non-positive {key}')
        for key in ('reliability', 'hardness'):
            if key in effective[eid] and not 0 <= effective[eid][key] <= 1:
                err(f'tachanka: {eid} has invalid {key} outside 0..1')
        for key in ('soft_attack', 'hard_attack', 'defense', 'breakthrough',
                    'ap_attack', 'armor_value', 'fuel_consumption'):
            if key in effective[eid] and effective[eid][key] < 0:
                err(f'tachanka: {eid} has negative {key}')

    for key in ('soft_attack', 'hard_attack', 'ap_attack', 'armor_value', 'hardness'):
        values = [effective[f'tachanka_equipment_{n}'][key]
                  for n in range(1, 5)
                  if f'tachanka_equipment_{n}' in effective and key in effective[f'tachanka_equipment_{n}']]
        if len(values) == 4:
            # armor_value and hardness jump from the plain family (0) to the
            # armored family (6 / 0.2) at variant 2, so allow that one step.
            if key in ('armor_value', 'hardness'):
                if values[0] > values[1] or any(values[i] > values[i + 1] for i in range(1, 3)):
                    err(f'tachanka: {key} regresses after the family switch to armored')
            elif values != sorted(values):
                err(f'tachanka: {key} does not progress monotonically across equipment variants')

    for unit_id in ('tachanka', 'armored_tachanka'):
        body = extract_block(units, unit_id)
        if body is None:
            err(f'tachanka: missing sub-unit definition {unit_id}')
            continue
        if not re.search(r'(?m)^\s*active\s*=\s*no\s*$', body):
            err(f'tachanka: {unit_id} is globally active; it must be enabled by GLP technology')
        family = 'armored_tachanka_equipment' if unit_id == 'armored_tachanka' else 'tachanka_equipment'
        if not re.search(rf'(?m)^\s*transport\s*=\s*{re.escape(family)}\s*$', body):
            err(f'tachanka: {unit_id} does not inherit speed from {family}')
        if not re.search(rf'(?m)^\s*{re.escape(family)}\s*=\s*20\s*$', body):
            err(f'tachanka: {unit_id} does not consume the {family} archetype')
        if unit_id == 'armored_tachanka' and re.search(
                r'(?m)^\s*(?:maximum_speed|armor_value|ap_attack)\s*=', body):
            err('tachanka: armored_tachanka duplicates equipment combat stats in the sub-unit')
        if not re.search(r'(?m)^\s*sprite\s*=\s*cavalry\s*$', body):
            err(f'tachanka: {unit_id} does not use the vanilla cavalry designer icon')
        if not re.search(r'(?m)^\s*map_icon_category\s*=\s*other\s*$', body):
            err(f'tachanka: {unit_id} does not use the vanilla cavalry map icon category')

    history_path = os.path.join(ROOT, 'history/units/GLP_1936.txt')
    if os.path.isfile(history_path):
        history = strip_comments(read(history_path))
        tachanka_template = extract_block(history, 'division_template') or ''
        # The first template is the starting GLP tachanka formation.
        if 'tachanka = {' not in tachanka_template:
            err('tachanka: GLP starting tachanka template does not use the custom battalion')
        if not re.search(r'template_counter\s*=\s*93', tachanka_template):
            err('tachanka: GLP starting tachanka template has no tachanka template_counter = 93')

    # GFX-объявления иконок тачанок (под-юнит + плитки 93/94).
    gfx = strip_comments(read(os.path.join(ROOT, 'interface/GLP_subunit_icons.gfx')))
    if not gfx:
        err('tachanka: missing subunit-icon declarations (interface/GLP_subunit_icons.gfx)')
    else:
        # Атласы под-юнитов идут в 2 кадрах (как ванильный subuniticons.gfx).
        two_frame = {
            'GFX_unit_tachanka_icon_medium': 'gfx/interface/counters/divisions_large/unit_tachanka_icon.dds',
            'GFX_unit_tachanka_icon_medium_white': 'gfx/interface/counters/divisions_small/onmap_unit_tachanka_icon.dds',
            'GFX_unit_tachanka_icon_small': 'gfx/texticons/unit_tachanka_icon_small.dds',
            'GFX_unit_armored_tachanka_icon_medium': 'gfx/interface/counters/divisions_large/unit_armored_tachanka_icon.dds',
            'GFX_unit_armored_tachanka_icon_medium_white': 'gfx/interface/counters/divisions_small/onmap_unit_armored_tachanka_icon.dds',
            'GFX_unit_armored_tachanka_icon_small': 'gfx/texticons/unit_armored_tachanka_icon_small.dds',
        }
        for sprite, texture in two_frame.items():
            pattern = (rf'name\s*=\s*"{re.escape(sprite)}"'
                       rf'.{{0,600}}?texturefile\s*=\s*"{re.escape(texture)}"'
                       rf'.{{0,200}}?noOfFrames\s*=\s*2')
            if not re.search(pattern, gfx, re.S | re.I):
                err(f'tachanka: {sprite} is not declared with two-frame atlas -> {texture}')
        # Плитки шаблонов 93/94 -- одиночные (как знамёна 90/91), noOfFrames нет.
        single = {
            'GFX_div_templ_93_large': 'gfx/interface/counters/division_templates_large/GLP_tachanka_large.dds',
            'GFX_div_templ_93_small': 'gfx/interface/counters/division_templates_small/GLP_tachanka_small.dds',
            'GFX_div_templ_94_large': 'gfx/interface/counters/division_templates_large/GLP_armored_tachanka_large.dds',
            'GFX_div_templ_94_small': 'gfx/interface/counters/division_templates_small/GLP_armored_tachanka_small.dds',
        }
        for sprite, texture in single.items():
            pattern = rf'name\s*=\s*"{re.escape(sprite)}".{{0,600}}?texturefile\s*=\s*"{re.escape(texture)}"'
            if not re.search(pattern, gfx, re.S | re.I):
                err(f'tachanka: {sprite} is not declared -> {texture}')


def main():
    check_syntax()
    check_tachanka_technology_contract()
    loc = load_loc()
    defs = collect_definitions()
    check_duplicates(defs)
    check_sprites(defs)
    check_portraits()
    check_screens()
    check_loading_tips()
    check_music()
    check_cinematic_intro_voice()
    check_fonts()
    check_bookmarks(loc)
    check_opinions(loc)
    check_focus_tree(defs)
    check_continuous_focus_layout()
    check_units()
    check_events(loc)
    check_characters(defs, loc)
    check_focus_icons()
    check_idea_pictures()
    check_event_pictures()
    check_idea_icon_geometry()
    check_gui_overrides()
    check_event_window_stress_and_adaptiveness()
    check_advisor_portraits(defs)
    check_advisor_ideas(defs)
    check_unit_models()
    check_division_icons()
    check_entity_graph()
    check_no_stray_art()
    check_loc_tech_names(loc)
    check_dds_transparency()
    check_focus_search_filters()
    check_focus_branch_headers()
    check_idea_modifier_keys()
    check_advisor_frames()
    check_crisis_events()

    print("=" * 72)
    print(f" GLP AUDIT  --  {len(ERRORS)} error(s), {len(WARNINGS)} warning(s)")
    print("=" * 72)
    for e in ERRORS:
        print("  [ERROR]  " + e)
    for w in WARNINGS:
        print("  [warn ]  " + w)
    return 1 if ERRORS else 0


if __name__ == '__main__':
    sys.exit(main())
