#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GLP mod audit  -- HOI4 1.19.2 compliance checker.

Checks performed:
  1. Brace balance / basic syntax of every .txt / .gfx script.
  2. Localisation: UTF-8 BOM, "l_<lang>:" header, duplicate keys,
     key parity between russian and english.
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
     (GLP_units.*, NTC_cavalry in black papakha, sabre, sabre anims) and wired as
     tag-specific GLP_cavalry_entity / GLP_cavalry_2_entity without
     cloning vanilla cavalry entities.
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
 15. Idea slot model: swap_ideas upgrade lines keep exactly one spirit per
    slot in any focus completion order (guard coverage + prerequisite
    guarantees + no prereq cycles), and the worst-case permanent spirit
    stack stays under the design caps (GAMEPLAY_READINESS.md, phase A).
 16. Diplomacy mechanics (phase B): alliance focuses trigger partner
    events with give_guarantee + a refusal branch; the Moscow ultimatum is
    actually fired and refusal costs SOV a wargoal; pact refusal carries a
    timed isolation spirit; lend-lease and white volunteer waves are
    rate-limited (no farmland).
 17. Focus-tree pacing (phase C): top rows cheap (cost <= 5), middle
    bounded (cost <= 7), capstones gated by available and mutually
    exclusive; partner-dependent focuses must bypass dead partners;
    navy/air terminals bound to Crimea (137) / Donbass (227).
 18. Decisions (phase D): no farmland -- every resource grant carries
    fire_only_once / long cooldown / self-cost; the raid has a
    state_target; Spanish aid checks the stockpile, consumes it, and
    is visible on the SPR side; >= 4 occupation decisions gated by
    state control; the raid risk event exists.
 19. Equipment (phase E): every stockpile/has_equipment key is a real
    1.19 key (unknown keys are silently ignored by the engine); the
    RPA trophy loop starts active (tech_maintenance_company in the
    opening set_technology) and the "Tachanka Kurin" template exists.
 20. .gfx parser safety: exactly one top-level spriteTypes block per
    file and no effectFile/animation subblocks inside sprite blocks
    (a broken .gfx silently drops ALL its sprites in-game).
 21. "Iberian Fire and the Black International" module: event ->
    flags -> decisions -> Barcelona fork -> faction integrity.

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
LOC_LINE = re.compile(r'^\s*([A-Za-z0-9_.\-]+):\s*\d*\s*"')


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
            m = LOC_LINE.match(line)
            if not m:
                continue
            k = m.group(1)
            if k in seen and not is_replace:
                err(f"{rel(p)}:{i}: duplicate localisation key '{k}' "
                    f"(first at line {seen[k]})")
            seen[k] = i
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
    missing = [n for n in range(1, 17)
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
                     'П. А. Аршиновъ', 'Декларация РПА', 'Девизъ тачанки',
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
    """Ванильный саундтрек должен быть перекрыт файлами мода."""
    for f in ('music/music.asset', 'music/songs.txt', 'music/_songs.txt'):
        if not os.path.exists(os.path.join(ROOT, f)):
            err(f"{f} отсутствует — ванильный саундтрек не будет перекрыт")
            continue
        body = read(os.path.join(ROOT, f))
        if f.endswith('.txt') and 'music_station' not in body:
            err(f"{f}: отсутствует директива music_station — станция не зарегистрируется в радиоприёмнике")
        for m in re.finditer(r'file\s*=\s*"([^"]+)"', body):
            if not os.path.exists(os.path.join(ROOT, 'music', m.group(1))):
                err(f"{f}: аудиофайл не найден -> music/{m.group(1)}")
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
VANILLA_TRAITS = set("""
    inspirational_leader panic_leader dislikes_germany dislikes_russia
    war_hero collaborator communist_revolutionary anti_communist
    guerilla_fighter trickster organizer offensive_doctrine defensive_doctrine
    infantry_officer infantry_leader infantry_expert cavalry_officer
    cavalry_leader cavalry_expert armor_officer armor_leader panzer_expert
    artillery_officer artillery_leader artillery_expert commando
    ranger trait_mountaineer trait_engineer naval_invader paratrooper
    aggressive_assaulter skilled_staffer brilliant_strategist
    fast_planner careful_planner substance_abuser trait_reckless
    politically_connected media_personality thorough_planner
    hill_fighter desert_fox winter_specialist swamp_fox jungle_rat
    urban_assault_specialist old_guard harsh_leader war_hero_general
    logistics_wizard scavenger camouflage_expert bearer_of_artillery
    army_chief_organizational_2 army_chief_offensive_2 army_chief_defensive_2
    army_cavalry_2 army_cavalry_speed_2 army_morale_2 army_entrenchment_2
    army_infantry_2 army_regrouping_2 army_logistics_2 army_artillery_2
    silent_workhorse ideological_crusader captain_of_industry
    war_industrialist prince_of_terror fortification_engineer
    compassionate_gentleman quartermaster_general
""".split())


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
    """Каждый национальный дух использует тематическую иконку GLP-пака.

    tools/idea_pictures.tsv является человекочитаемой картой подбора. Аудит
    требует полного совпадения таблицы с common/ideas/GLP_ideas.txt, чтобы при
    добавлении нового духа нельзя было незаметно вернуть generic-иконку.
    """
    actual = {}
    for p, body in all_script_text('common/ideas').items():
        for m in re.finditer(r'^\t\t(GLP_\w+)\s*=\s*\{(.*?)^\t\t\}', body, re.M | re.S):
            iid, blk = m.group(1), m.group(2)
            pic = re.search(r'picture\s*=\s*(GFX_\w+)', blk)
            if not pic:
                err(f"{rel(p)}: идея '{iid}' без picture")
                continue
            name = pic.group(1)
            actual[iid] = name
            if not name.startswith('GFX_idea_GLP_'):
                err(f"{rel(p)}: идея '{iid}' использует '{name}', а должна "
                    "использовать тематическую иконку GFX_idea_GLP_* из пака")

    mapping_path = os.path.join(ROOT, 'tools/idea_pictures.tsv')
    expected = {}
    if not os.path.exists(mapping_path):
        err("tools/idea_pictures.tsv отсутствует")
    else:
        for line_no, line in enumerate(read(mapping_path).splitlines(), 1):
            if not line or line.startswith('#') or line == 'idea\tpicture':
                continue
            cols = line.split('\t')
            if len(cols) != 2:
                err(f"tools/idea_pictures.tsv:{line_no}: ожидаются 2 колонки")
                continue
            iid, picture = cols
            if iid in expected:
                err(f"tools/idea_pictures.tsv:{line_no}: дубль идеи '{iid}'")
            expected[iid] = picture

    for iid in sorted(set(actual) - set(expected)):
        err(f"tools/idea_pictures.tsv: нет строки для идеи '{iid}'")
    for iid in sorted(set(expected) - set(actual)):
        err(f"tools/idea_pictures.tsv: лишняя/неизвестная идея '{iid}'")
    for iid in sorted(set(actual) & set(expected)):
        if actual[iid] != expected[iid]:
            err(f"tools/idea_pictures.tsv: '{iid}' -> {expected[iid]}, "
                f"но в GLP_ideas.txt указано {actual[iid]}")

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
        for token in ('"EventWindow"', '"EventWindow_leader"', '"EventWindow_News"',
                      '"event_option_entry"'):
            if token not in body:
                err(f"interface/eventwindow.gui: отсутствует ванильное окно {token}")
        # Окно новостей стоит на тёмном фоне GLP_event_news_bg_wide, поэтому
        # заголовок и описание обязаны использовать «инверсные» (белые) шрифты;
        # обычные (чёрные) в этом окне = текст нечитаем.
        m = re.search(r'name\s*=\s*"EventWindow_News"(.*?)(?=\n\tcontainerWindowType|\n})', body, re.S)
        if not m:
            err("interface/eventwindow.gui: не найден блок EventWindow_News")
        else:
            news = m.group(1)
            for want in ('font = "hoi4_typewriter22_inverted"',
                         'font = "hoi4_typewriter16_inverted"'):
                if want not in news:
                    err(f"interface/eventwindow.gui: в новостях отсутствует {want} "
                        "-- текст рисуется чёрным на тёмном фоне")
            for bad in ('font = "hoi4_typewriter22"', 'font = "hoi4_typewriter16"'):
                if re.search(re.escape(bad) + r'(?![_A-Za-z])', news):
                    err(f"interface/eventwindow.gui: в EventWindow_News остался {bad} "
                        "-- чёрный текст на тёмном фоне")

    # ------------------------------------------------------------------
    #  Оверрайды «чистых портретов»: из списков командиров и карточек
    #  советников убраны значки, которые движок рисует поверх/у портрета
    #  (HQ-бейдж, иконки черт, иконки типа соединения, полоски ролей).
    #  Вероятность регрессии (кто-то вернёт элементы) ловится здесь.
    # ------------------------------------------------------------------
    no_badge = {
        'interface/unitleaderwindow.gui': (('army_hq_icon', 'template_button', 'ship_icon_button'),
           ('"armyleaderentry"', '"divisionleaderentry"')),
        'interface/countrypoliticsview.gui': (('idea_traits',),
           ('"political_idea_entry"', '"political_selectable_idea_entry_grid"',
            '"political_selectable_idea_entry_list"')),
    }
    for rel, (forbidden, required) in no_badge.items():
        p = os.path.join(ROOT, rel)
        if not os.path.exists(p):
            err(f"{rel} отсутствует -- значки на портретах вернутся")
            continue
        body = strip_comments(read(p))
        for token in required:
            if token not in body:
                err(f"{rel}: отсутствует ванильный контейнер {token}")
        for token in forbidden:
            if f'name = "{token}"' in body:
                err(f"{rel}: элемент {token} снова определён -- он рисуется поверх портрета")

    p = os.path.join(ROOT, 'interface/countryofficercorpview.gui')
    if not os.path.exists(p):
        err("interface/countryofficercorpview.gui отсутствует -- "
            "значки ролей/черт у штабных портретов вернутся")
    else:
        body = strip_comments(read(p))
        for token in ('"country_view_advisor_entry"', '"high_command_entry"',
                      '"army_chief_entry"', '"navy_chief_entry"', '"air_chief_entry"',
                      '"theorist_entry"'):
            if token not in body:
                err(f"interface/countryofficercorpview.gui: отсутствует контейнер {token}")
        if 'name = "advisor_type_icon"' in body:
            err("interface/countryofficercorpview.gui: advisor_type_icon снова определён "
                "-- полоска роли рисуется у штабного портрета")
        # idea_traits у командных entries быть не должно; блоки духов их сохраняют,
        # поэтому проверяем по расположению: ни одного idea_traits выше theorist_entry.
        ut = body.find('name = "theorist_entry"')
        head = body[:ut]
        if 'name = "idea_traits"' in head:
            err("interface/countryofficercorpview.gui: idea_traits в командных entries "
                "-- полоска черт рисуется у штабного портрета")


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


# В моде нет кастомных 3D-моделей. Раньше каталог gfx/models/units/
# содержал mesh-файлы из Revolution or Reaction: Rise of Russia, но их
# импорт провоцировал краш рендера, и теперь мод полностью на ванильных
# infantry_rifle_entity / cavalry_entity / cavalry_2_entity. Все следы
# импорта (GLP_units.gfx / .asset, GLP_cavalry_animations.asset,
# .mesh/.dds/.anim) удалены; в случае попытки вернуть их -- check_unit_models
# сообщит об этом.


EXPECTED_UNIT_MODEL_FILES = (
    'gfx/entities/GLP_units.asset',
    'gfx/entities/GLP_units.gfx',
    'gfx/models/units/GLP_cavalry_animations.asset',
    'gfx/models/units/RSR_marine.mesh',
    'gfx/models/units/RSR_marine_diffuse.dds',
    'gfx/models/units/RSR_marine_normal.dds',
    'gfx/models/units/RSR_marine_spec.dds',
    'gfx/models/units/NTC_cavalry.mesh',
    'gfx/models/units/NTC_cavalry_diffuse_.dds',
    'gfx/models/units/NTC_cavalry_normal.dds',
    'gfx/models/units/NTC_cavalry_spec.dds',
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


def check_unit_models():
    """Пехота-матрос RSR_marine и казачья конница Rise of Russia должны быть на месте."""
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


def _im_alpha_max(path):
    """Максимальная альфа пикселя через ImageMagick; None, если IM недоступен."""
    import shutil, subprocess
    if not shutil.which('convert'):
        return None
    try:
        o = subprocess.run(
            ['convert', path, '-alpha', 'extract',
             '-format', '%[fx:maxima*255]', 'info:'],
            capture_output=True, text=True, timeout=30)
        return float(o.stdout.strip())
    except Exception:
        return None


def check_dds_transparency():
    """Тематические иконки духов (60x68, idea_GLP_<категория>) обязаны иметь
    реальные прозрачные пиксели по углам — иначе иконка закроет слот
    непрозрачным квадратом. ПОРТРЕТНЫЕ иконки советников (idea_GLP_<Имя>,
    65x67) — исключение: по ТЗ это чистый непрозрачный кадр портрета
    без рамки-«бумажки» и значка специализации (рамку рисует слот движка)."""
    for p in sorted(walk('gfx/interface/ideas', ('.dds',))):
        if re.match(r'^idea_GLP_[A-Z]', os.path.basename(p)):
            continue  # портрет советника — намеренно сплошной кадр
        mn = _im_alpha_min(p)
        if mn is None:
            warn("ImageMagick недоступен -- пиксельная проверка прозрачности пропущена")
            return
        if mn >= 32.0:
            err(f"{rel(p)}: нет реальной прозрачности (min alpha = {mn:.0f}, "
                f"нужно < 32) -- иконка закроет слот непрозрачным квадратом")


def check_advisor_frames():
    """Советники — ЧИСТЫЕ портреты 65x67 (ТЗ: «без бумажки и иконки
    специализации»). Министерские шаблоны Ultimate-HOI4-GFX (Minister_Base.png
    с бумажной карточкой и Minister_Background.png с наклонной подложкой)
    запрещены: их композиция закрывала нижнюю половину портрета яркой
    «бумажкой». Проверяем размер, полную непрозрачность кадра и отсутствие
    ссылок на шаблоны в сборочном скрипте."""
    script = read(os.path.join(ROOT, 'tools/build_portraits.sh'))
    for tpl in ('Minister_Base.png', 'Minister_Background.png'):
        if tpl in script:
            err(f"tools/build_portraits.sh использует шаблон {tpl} -- "
                f"«бумажка»/значок роли вернётся на портреты советников")
    for p in sorted(walk('gfx/interface/ideas', ('.dds',))):
        base = os.path.basename(p)
        if not re.match(r'^idea_GLP_[A-Z]', base):
            continue
        info = dds_info(p)
        if info and (info[0], info[1]) != (65, 67):
            err(f"{rel(p)}: размер иконки советника {info[0]}x{info[1]}, ваниль 65x67")
        mx = _im_alpha_max(p)
        if mx is not None and mx <= 250.0:
            err(f"{rel(p)}: кадр портрета советника должен быть полностью "
                f"непрозрачным (max alpha = {mx:.0f}) -- не рамка, а чистый портрет")


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
    music_asset = read(os.path.join(ROOT, 'music/gulyaipole.asset'))
    if 'name = "gulyaipole_intro_voice"' in music_asset:
        err('intro voice: music и soundeffect используют одно имя gulyaipole_intro_voice')


# --------------------------------------------- cinematic intro regression guards
# Буквы дореволюционной/украинской кириллицы, которых НЕТ в атласе шрифтов
# HOI4: движок рисует вместо них «?» (классические «?????????» в текстах).
FORBIDDEN_FONT_CHARS = 'ѣѢіІїЇєЄґҐѳѲѵѴѣ́І́'


def check_loc_font_charset():
    """Значения локализации обязаны состоять из символов атласа шрифтов HOI4.

    Раньше в цитатах загрузки и текстах мода использовалась дореформенная
    орфография (ѣ, і) — в игре все такие буквы отображались знаками «?».
    Твёрдый знак «ъ» в атласе есть и сохранён ради колорита.
    """
    pat = re.compile('[' + re.escape(FORBIDDEN_FONT_CHARS) + ']')
    for lang in ('russian', 'english'):
        for fp in walk(f'localisation/{lang}', ('.yml',)):
            for i, line in enumerate(read(fp).split('\n'), 1):
                m = re.match(r'^\s*[A-Za-z0-9_.\-]+:\d*\s*"(.*)"', line)
                if m and pat.search(m.group(1)):
                    bad = sorted(set(pat.findall(m.group(1))))
                    err(f"{rel(fp)}:{i}: символы {' '.join(bad)} отсутствуют "
                        f"в атласе шрифтов HOI4 и покажутся «?»")
    # descriptor.mod рендерит только лаунчер (Chromium), но приводим к тому
    # же алфавиту для единообразия.
    dmod = read(os.path.join(ROOT, 'descriptor.mod'))
    if pat.search(dmod):
        warn('descriptor.mod: остались символы вне атласа HOI4 (ѣ/і) — '
             'приведите имя мода к современному алфавиту')


def check_intro_gui_keys(loc):
    """Каждый text=/buttonText= ключ окна заставки должен быть в RU и EN loc.

    Отсутствующий ключ движок печатает на элементе как есть — на заставке
    была видна «техническая» надпись GULYAIPOLE_TOGGLE_MODE_DYNAMIC.
    """
    gui_path = os.path.join(ROOT, 'interface/gulyaipole_intro_custom.gui')
    text = strip_comments(read(gui_path))
    keys = set()
    for m in re.finditer(r'^\s*text\s*=\s*"([^"]+)"', text, re.M):
        keys.add(m.group(1))
    for m in re.finditer(r'buttonText\s*=\s*"([^"]+)"', text):
        keys.add(m.group(1))
    for key in sorted(keys):
        if key.startswith(('[', '$')) or not re.match(r'^[A-Z0-9_]+$', key):
            continue  # динамические команды и литералы
        for lang in ('russian', 'english'):
            if key not in loc.get(lang, {}):
                err(f"interface/gulyaipole_intro_custom.gui: ключ '{key}' "
                    f"отсутствует в {lang} локализации — увидите техническое имя")
    # defined_text нельзя использовать как buttonText без записи в .yml
    for fp in walk('common/scripted_localisation', ('.txt',)):
        for m in re.finditer(r'name\s*=\s*([A-Za-z0-9_.]+)', read(fp)):
            name = m.group(1)
            if name in keys:
                err(f"defined_text '{name}' использован как прямой ключ GUI; "
                    f"нужна запись в .yml или две кнопки с обычными ключами")


def _im_mean(path, ops):
    import shutil, subprocess
    if not shutil.which('convert'):
        return None
    try:
        o = subprocess.run(['convert', path] + ops + ['-format', '%[fx:mean]', 'info:'],
                           capture_output=True, text=True, timeout=60)
        return float(o.stdout.strip())
    except Exception:
        return None


def check_intro_no_crawl():
    """Анимированная лента титров полностью удалена по ТЗ: история показывается
    обычным текстовым полем. Запрещены любые остатки — спрайт, текстуры,
    кнопки-переключатели и их ключи локализации (иначе на окне снова появятся
    технические имена или пустая колонка)."""
    for sub in ('interface', 'common', 'gfx', 'localisation'):
        for fp in walk(sub, ('.gui', '.gfx', '.txt', '.yml')):
            text = read(fp)
            for token in ('GFX_intro_text_crawl', 'gulyaipole_text_crawl',
                          'gulyaipole_text_mask', 'gulyaipole_text_base',
                          'GULYAIPOLE_TOGGLE_', 'glp_intro_crawl_mode'):
                # glp_intro_crawl_mode допустим только в clr_ (чистка старых сохранений)
                if token == 'glp_intro_crawl_mode':
                    for m in re.finditer(r'^.*glp_intro_crawl_mode.*$', text, re.M):
                        if 'clr_country_flag' not in m.group(0):
                            err(f"{rel(fp)}: остаток режима ленты '{m.group(0).strip()[:70]}'")
                elif token in text:
                    err(f"{rel(fp)}: остаток удалённой ленты титров -- '{token}'")
    for leftover in ('gfx/interface/intro/gulyaipole_text_crawl.dds',
                     'gfx/interface/intro/gulyaipole_text_mask.dds',
                     'gfx/interface/intro/gulyaipole_text_base.dds'):
        if os.path.exists(os.path.join(ROOT, leftover)):
            err(f"{leftover}: файл-остаток ленты титров удалите из мода")

# ------------------------------------------------- 15. слотовая модель духов
# Духи живут "слотами": линии апгрейда идут через swap_ideas (старый -> новый),
# поэтому в слоте одновременно держится один дух. Два класса сбоев:
#  1) фокус добавляет дух Y из линии C, но guard'ы has_idea не покрывают дух z
#     той же линии, который у игрока в этот момент держится (середина линии
#     уже заменена промежуточным фокусом), -- ветка else складывает z + Y
#     ("двойное накопление");
#  2) суммарные модификаторы стека духов превышают дизайн-капы
#     (GAMEPLAY_READINESS.md, фаза A): страна превращается в сверхдержаву.
# Оба класса ловятся симуляцией дерева фокусов (детерминированная).

JUNTA_LINE_IDEAS = {  # путь хунты -- самостоятельный обмен стаб <--> л/с;
    'GLP_idea_military_junta',       # в капе conscription не участвует
    'GLP_idea_total_militarization',
    'GLP_idea_continental_crusade',
}
BOUND_CAPS = {
    # Худший случай ПОСТОЯННОГО стека (все линии до конца, один капстон из
    # взаимных). Консрипция -- из GAMEPLAY_READINESS.md (фаза A, <= 0.35 без
    # хунты); кавалерия -- норма «финальный кав-атак +0.25..0.40». Фабрики:
    # глобального капа в ТЗ нет (только <= 0.15 на один дух -- это
    # SINGLE_IDEA_CAPS), 0.50 -- предельный потолок против исходного бага
    # (+1.35 при 111 add_ideas).
    'conscription_factor': 0.35,          # без линии хунты
    'cavalry_attack_factor': 0.40,
    'industrial_capacity_factory': 0.50,
    'research_speed_factor': 0.50,
}
SINGLE_IDEA_CAPS = {
    'cavalry_attack_factor': 0.30,
    'industrial_capacity_factory': 0.15,
}
MAX_RESEARCH_SLOTS = 2
STARTING_CORE_DEF_CAP = 0.10


def _idea_mods_map():
    """{дух: {ключ модификатора: значение}} по common/ideas."""
    mods = {}
    for p in walk('common/ideas', ('.txt',)):
        text = strip_comments(read(p))
        for m in re.finditer(r'^\t\t(GLP[A-Za-z0-9_]*)\s*=\s*\{\n', text, re.M):
            name = m.group(1)
            rest = text[m.end():]
            mm = re.search(r'modifier\s*=\s*\{', rest)
            if not mm:
                continue
            depth, j = 1, mm.end()
            while depth and j < len(rest):
                if rest[j] == '{':
                    depth += 1
                elif rest[j] == '}':
                    depth -= 1
                j += 1
            d = {}
            for k, v in re.findall(
                    r'^\s*([a-z_][a-z0-9_]*)\s*=\s*(-?[\d.]+)\s*$',
                    rest[mm.end():j - 1], re.M):
                d[k] = d.get(k, 0.0) + float(v)
            mods[name] = d
    return mods


def _focus_idea_effects(body):
    """Порядковые эффекты идей фокуса:
    ('add', идея) / ('timed', идея) / ('remove', идея) /
    ('swap', [guard-ы...], новый) -- guard пуст = «голый» swap_ideas.

    Ветку else = { add_ideas = Y } считаем безусловным add Y: если guard
    сработал, повторный add идемпотентен; если нет -- это ровно поведение
    else-ветки.
    """
    eff = []
    guarded_spans = []
    for m in re.finditer(
            r'has_idea\s*=\s*([A-Za-z0-9_]+)\s*\}\s*'
            r'swap_ideas\s*=\s*\{\s*remove_idea\s*=\s*([A-Za-z0-9_]+)\s*'
            r'add_idea\s*=\s*([A-Za-z0-9_]+)\s*\}', body, re.S):
        if m.group(1) != m.group(2):
            err(f"swap_ideas: guard has_idea = {m.group(1)} не совпадает с "
                f"remove_idea = {m.group(2)} -- возможна двойная замена")
        eff.append(('swap', [m.group(1)], m.group(3), m.start()))
        guarded_spans.append(m.span())
    for m in re.finditer(
            r'swap_ideas\s*=\s*\{\s*remove_idea\s*=\s*([A-Za-z0-9_]+)\s*'
            r'add_idea\s*=\s*([A-Za-z0-9_]+)\s*\}', body, re.S):
        if any(s <= m.start() < e for s, e in guarded_spans):
            continue
        eff.append(('swap', [], m.group(2), m.start()))
    for m in re.finditer(r'add_ideas\s*=\s*\{([^}]*)\}', body):
        for n in re.findall(r'([A-Za-z0-9_]+)', m.group(1)):
            eff.append(('add', n, None, m.start()))
    for m in re.finditer(r'add_ideas\s*=\s*([A-Za-z0-9_]+)\s*$', body, re.M):
        eff.append(('add', m.group(1), None, m.start()))
    for m in re.finditer(
            r'add_timed_idea\s*=\s*\{[^}]*?idea\s*=\s*([A-Za-z0-9_]+)', body):
        eff.append(('timed', m.group(1), None, m.start()))
    swap_spans = [s.span() for s in re.finditer(
        r'swap_ideas\s*=\s*\{.*?\}', body, re.S)]
    for m in re.finditer(r'remove_idea\s*=\s*([A-Za-z0-9_]+)', body):
        if any(s <= m.start() < e for s, e in swap_spans):
            continue
        eff.append(('remove', m.group(1), None, m.start()))
    eff.sort(key=lambda e: e[3])
    out = [(e[0], e[1], e[2]) for e in eff]
    merged = []
    for e in out:
        # if/else_if-цепочка с одним и тем же целью = один логический swap
        # с набором guard'ов (первый сработавший guard и срабатывает).
        if (merged and merged[-1][0] == 'swap' and e[0] == 'swap'
                and merged[-1][2] == e[2]):
            merged[-1][1] = merged[-1][1] + e[1]
            continue
        # else = { add_ideas = Y } за swap'ом с тем же Y -- часть того же
        # логического эффекта: если guard сработал, swap уже добавил Y
        # (повтор add идемпотентен); если нет -- в линии не держится ничего
        # (иначе swap-проверка уже бы поймала дыру в guard'ах).
        if (merged and merged[-1][0] == 'swap' and merged[-1][2] == e[1]
                and e[0] == 'add'):
            continue
        merged.append(list(e) if e[0] == 'swap' else e)
    return [(k, tuple(g) if k == 'swap' else g, t) for k, g, t in merged]


def _focus_data():
    data = {}
    for p in walk('common/national_focus', ('.txt',)):
        for fid, body in _focus_blocks(p):
            pre = re.findall(
                r'prerequisite\s*=\s*\{\s*focus\s*=\s*([A-Za-z0-9_]+)', body)
            me = []
            m = re.search(r'mutually_exclusive\s*=\s*\{([^}]*)\}', body, re.S)
            if m:
                me = re.findall(r'focus\s*=\s*([A-Za-z0-9_]+)', m.group(1))
            data[fid] = {'pre': pre, 'me': me,
                         'eff': _focus_idea_effects(body)}
    return data


def _starting_ideas():
    held = set()
    for p in walk('history/countries', ('.txt',)):
        text = strip_comments(read(p))
        for m in re.finditer(r'add_ideas\s*=\s*\{([^}]*)\}', text):
            held.update(re.findall(r'([A-Za-z0-9_]+)', m.group(1)))
    return held


def _me_components(data):
    """Связные компоненты взаимного исключения (>= 2 фокуса)."""
    parent = {}

    def find(x):
        parent.setdefault(x, x)
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a, b):
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[ra] = rb

    for fid, fd in data.items():
        for other in fd['me']:
            if other in data:
                union(fid, other)
    comps = defaultdict(set)
    for fid in data:
        comps[find(fid)].add(fid)
    return [c for c in comps.values() if len(c) >= 2]


def _closure(fid, data, memo=None, stack=None):
    """Транзитивные предшественники фокуса (без самого фокуса)."""
    if stack is None:
        stack = set()
    if fid in memo:
        return memo[fid]
    if fid in stack:
        return set()          # цикл -- не наш класс дефекта
    stack.add(fid)
    out = set()
    for p in data.get(fid, {}).get('pre', []):
        if p in data:
            out.add(p)
            out |= _closure(p, data, memo, stack)
    stack.discard(fid)
    memo[fid] = out
    return out


def _simulate(closure, skip, data, starting=None):
    """Возвращает (held, timed_held): все держимые идеи и те из них, что
    были добавлены как timed (в игре истекают -- для капов постоянного
    стека считаются только held - timed_held)."""
    if starting is None:
        starting = _starting_ideas()
    held = set(starting)
    timed_held = set()
    order = []
    seen = set()

    def visit(f):
        # seen отмечается до обхода детей: при цикле в prerequisite
        # повторный вход в ту же вершину просто пропускается (цикл
        # отдельным error'ом сообщает _prereq_cycle).
        if f in seen or f in skip or f not in closure:
            return
        seen.add(f)
        for p in data.get(f, {}).get('pre', []):
            if p in closure:
                visit(p)
        order.append(f)

    for f in sorted(closure):
        visit(f)
    for fid in order:
        for kind, payload, target in data[fid]['eff']:
            if kind in ('add', 'timed'):
                held.add(payload)
                if kind == 'timed':
                    timed_held.add(payload)
            elif kind == 'remove':
                held.discard(payload)
                timed_held.discard(payload)
            elif kind == 'swap':
                for g in payload:
                    if g in held:
                        held.discard(g)
                        timed_held.discard(g)
                        break
                held.add(target)
    return held, timed_held


def _prereq_cycle(data):
    """Цикл в prerequisite (фокус требует сам себя через цепочку) -- дерево
    не может быть пройдено; движок повиснет или спрячет ветку."""
    WHITE, GRAY, BLACK = 0, 1, 2
    color = {fid: WHITE for fid in data}

    def dfs(fid, trail):
        color[fid] = GRAY
        for p in data[fid]['pre']:
            if p not in data:
                continue
            if color[p] == GRAY:
                i = trail.index(p) if p in trail else -1
                return (trail[i:] + [fid]) if i >= 0 else [p, fid]
            if color[p] == WHITE:
                cyc = dfs(p, trail + [fid])
                if cyc:
                    return cyc
        color[fid] = BLACK
        return None

    for fid in sorted(data):
        if color[fid] == WHITE:
            cyc = dfs(fid, [])
            if cyc:
                return cyc
    return None


def check_idea_slot_model():
    """Симуляция стека духов: слоты, guard'ы и дизайн-капы.

    1. Линии духов = связные компоненты графа swap_ideas (в слоте
       одновременно держится один дух). Для каждого эффекта, добавляющего
       дух Y из линии C, симулируется состояние «всё до фокуса выполнено»
       (с перебором веток mutually_exclusive): если в этот момент держится
       другой дух z линии C, которого не покрывает guard -- двойное
       накопление (error).
    1b. Каждый guard обязан быть гарантирован: фокус, добавляющий guard-идею,
       должен быть предшественником swap-фокуса (иначе порядок выполнения
       фокусов -- за игроком -- даёт дыру в else-ветке). Цикл в
       prerequisite тоже ошибка.
    2. Капы: точный худший случай ПОСТОЯННОГО стека (перебор всех 112
       комбинаций mutually_exclusive; timed-духи исключены -- они истекают
       по дизайну): conscription <= 0.35 (без хунты), cavalry_attack <=
       0.40, factory <= 0.50, research_speed <= 0.50; на один дух:
       cavalry_attack <= 0.30, factory <= 0.15; слоты исследований <= 2;
       стартовый core-def <= 0.10.
    """
    mods = _idea_mods_map()
    data = _focus_data()
    if not data:
        err('слотовая модель: дерево фокусов не найдено')
        return

    cyc = _prereq_cycle(data)
    if cyc:
        err('дерево фокусов: цикл в prerequisite: ' + ' -> '.join(cyc))
        return          # дальше по циклическому дереву симуляция бессмысленна

    # --- граф линий (swap_ideas везде: фокусы + события + решения) ---
    edge = defaultdict(set)
    for p in walk('common/national_focus', ('.txt',)):
        for _fid, body in _focus_blocks(p):
            for m in re.finditer(
                    r'swap_ideas\s*=\s*\{\s*remove_idea\s*=\s*([A-Za-z0-9_]+)\s*'
                    r'add_idea\s*=\s*([A-Za-z0-9_]+)\s*\}', body, re.S):
                a, b = m.group(1), m.group(2)
                edge[a].add(b)
                edge[b].add(a)
    for sub in ('events', 'common/decisions'):
        for p in walk(sub, ('.txt',)):
            text = strip_comments(read(p))
            for m in re.finditer(
                    r'swap_ideas\s*=\s*\{\s*remove_idea\s*=\s*([A-Za-z0-9_]+)\s*'
                    r'add_idea\s*=\s*([A-Za-z0-9_]+)\s*\}', text, re.S):
                a, b = m.group(1), m.group(2)
                edge[a].add(b)
                edge[b].add(a)
    line_of = {}
    seen = set()
    lines = []
    for a in sorted(edge):
        if a in seen:
            continue
        comp, stack = set(), [a]
        while stack:
            n = stack.pop()
            if n in comp:
                continue
            comp.add(n)
            stack.extend(edge[n] - comp)
        seen |= comp
        if len(comp) >= 2:
            lines.append(comp)
            for n in comp:
                line_of[n] = comp
    STATS['idea_slot_lines'] = len(lines)
    STATS['idea_slot_ideas'] = len(line_of)

    # --- 1. двойное накопление: guard покрывает всё, что держится ---
    me_comps = _me_components(data)
    starting = _starting_ideas()
    memo = {}
    for fid in sorted(data):
        closure = _closure(fid, data, memo)
        local = [c & closure for c in me_comps if c & closure]
        selections = [()]
        for c in local:
            selections = [s + (one,) for s in selections for one in sorted(c)]
        for sel in selections:
            skip = set()
            for c, one in zip(local, sel):
                skip |= c - {one}
            held, _timed = _simulate(closure, skip, data, starting)
            for kind, payload, target in data[fid]['eff']:
                if kind == 'swap':
                    idea, guards = target, set(payload)
                else:
                    idea, guards = payload, set()
                if kind not in ('add', 'timed', 'swap'):
                    continue
                comp = line_of.get(idea)
                if not comp:
                    continue
                bad = (held & comp) - guards - {idea}
                if bad:
                    err(f"слот духов: фокус '{fid}' добавляет '{idea}', но в "
                        f"этот момент у игрока в той же линии держится "
                        f"'{sorted(bad)[0]}' -- guard не покрывает её, "
                        f"итог: двойное накопление")
                    break

    # --- 1b. guard должен быть гарантирован: фокус, добавляющий guard-идею,
    # обязан быть (транзитивным) предшественником swap-фокуса. Иначе игрок
    # может выполнить фокусы в порядке, при котором guard-идея ещё не
    # получена (параллельные ветки), а затем получить её -- и else-ветка
    # сложит духи в одном слоте. Порядок выполнения -- за игроком.
    idea_adders = defaultdict(set)
    for fid, fd in data.items():
        for kind, _payload, target in fd['eff']:
            if kind in ('swap', 'add', 'timed'):
                idea_adders[target].add(fid)
    for fid in sorted(data):
        for kind, payload, target in data[fid]['eff']:
            if kind != 'swap':
                continue
            for g in payload:
                if g in starting:
                    continue
                adders = {a for a in idea_adders.get(g, set()) if a != fid}
                if not adders:
                    continue
                if not any(a in memo.get(fid, _closure(fid, data, memo))
                           for a in adders):
                    err(f"слот духов: фокус '{fid}' guard'ит '{g}', но "
                        f"добавляющий её фокус {sorted(adders)[0]} не "
                        f"предшественник -- добавьте prerequisite, иначе "
                        f"порядок фокусов даёт двойное накопление")

    # --- 2. капы: точный худший случай постоянного стека. Игрок обязан
    # выбрать ровно ОДИН фокус из каждого компонента mutually_exclusive,
    # поэтому перебираем все допустимые комбинации (их немного: 112 на
    # текущем дереве) и берём максимум суммарного модификатора. Считаются
    # только ПЕРЕМАНЕНТНЫЕ духи: timed-духи по дизайну временные (480-730
    # дней) и истекают, поэтому в постоянный стек не входят.
    selections = [()]
    for c in me_comps:
        selections = [s + (one,) for s in selections for one in sorted(c)]
    worst = defaultdict(float)
    for sel in selections:
        skip = set()
        for c, one in zip(me_comps, sel):
            skip |= c - {one}
        held, timed_held = _simulate(set(data), skip, data, starting)
        perm = held - timed_held
        for k in BOUND_CAPS:
            s = 0.0
            for i in perm:
                if k == 'conscription_factor' and i in JUNTA_LINE_IDEAS:
                    continue
                s += mods.get(i, {}).get(k, 0.0)
            if s > worst[k]:
                worst[k] = s
    for k, cap in BOUND_CAPS.items():
        if worst[k] > cap + 1e-9:
            err(f"слот духов: худший случай постоянного стека {k} = "
                f"{worst[k]:.2f} превышает кап {cap:.2f}")
    STATS['idea_slot_worst_case'] = {k: round(v, 3)
                                     for k, v in worst.items()}

    for idea, dm in mods.items():
        for k, cap in SINGLE_IDEA_CAPS.items():
            if dm.get(k, 0.0) > cap + 1e-9:
                err(f"слот духов: дух '{idea}' даёт {k} = "
                    f"{dm[k]:.2f} > капа {cap:.2f} на один дух")

    slots = 0
    for p in walk('common/national_focus', ('.txt',)):
        text = strip_comments(read(p))
        slots += sum(int(n) for n in re.findall(
            r'add_research_slot\s*=\s*(\d+)', text))
    if slots > MAX_RESEARCH_SLOTS:
        err(f"слоты исследований: сумма add_research_slot = {slots} "
            f"> {MAX_RESEARCH_SLOTS}")
    STATS['research_slots_total'] = slots

    core = sum(mods.get(i, {}).get('army_core_defence_factor', 0.0)
               for i in starting)
    if core > STARTING_CORE_DEF_CAP + 1e-9:
        err(f"слот духов: стартовый army_core_defence_factor = {core:.2f} "
            f"> {STARTING_CORE_DEF_CAP}")


# ------------------------------------------------- 16. дипломатика: механика, а не бутафория
# Фаза B (Спринт 2): «союз» обязан давать реальную защиту (guarantee /
# access / faction), у партнёрского события должен быть путь отказа,
# ультиматум Москвы обязан реально запускаться, а его отказ -- стоить
# create_wargoal. Помощь по ленд-лизу и белые волонтёры ограничены
# кулдауном/лимитом (иначе фармабельны).

ALLIANCE_FOCUS = {
    'GLP_alliance_with_soviet_union': 'SOV',
    'GLP_alliance_with_germany': 'GER',
    'GLP_alliance_with_britain': 'ENG',
}
PACT_EVENTS = ('glp_diplo.1', 'glp_diplo.2', 'glp_diplo.3')


def check_diplomacy_mechanics(defs):
    """Фаза B: дипломатия -- механика, а не бутафория (см. GAMEPLAY_READINESS
    раздел 3.2). Четыре инварианта:
    1. каждый союзный фокус запускает событие партнёра, в котором есть
       give_guarantee (реальная защита) и не меньше двух опций (путь отказа);
    2. ультиматум Москвы запускается из on_actions, а его отказ несёт
       create_wargoal (иначе угроза бутафорская);
    3. отказ от пакта имеет механическую цену (timed-дух изоляции);
    4. ленд-лиз (кулдаун >= 360 дней) и волны белых добровольцев
       (кулдаун >= 90 дней + лимит числа волн) не фармабельны.
    """
    event_bodies = {}
    for p in walk('events', ('.txt',)):
        event_bodies[p] = strip_comments(read(p))

    def event_body(eid):
        # id события стоит в начале строки с одним табом; вхождения вида
        # `country_event = { id = X }` (вложенные ссылки) не должны
        # подходить -- иначе ловим хвост чужого события.
        pat = re.compile(r'^\tid = ' + re.escape(eid) + r'\s*(.*?)(?=^country_event|\Z)', re.S | re.M)
        for _p, b in event_bodies.items():
            m = pat.search(b)
            if m:
                return m.group(1)
        return None

    # 1. союзный фокус -> событие партнёра с реальными механиками
    for fid, tag in ALLIANCE_FOCUS.items():
        body = None
        for p in walk('common/national_focus', ('.txt',)):
            for f, b in _focus_blocks(p):
                if f == fid:
                    body = b
        if body is None:
            err(f"дипломатика: фокус '{fid}' не найден")
            continue
        m = re.search(
            re.escape(tag) + r'\s*=\s*\{\s*country_event\s*=\s*\{\s*id\s*=\s*(glp_diplo\.\d+)',
            body)
        if not m:
            err(f"дипломатика: фокус '{fid}' не запускает событие {tag} -- "
                "пакт остаётся бутафорией (только opinion)")
            continue
        eid = m.group(1)
        ebody = event_body(eid)
        if ebody is None:
            err(f"дипломатика: событие {eid} ({fid}) не найдено в events/")
            continue
        if 'give_guarantee' not in ebody:
            err(f"дипломатика: событие {eid} без give_guarantee -- пакт не "
                "даёт Гуляйполю реальной защиты")
        if len(re.findall(r'\boption = \{', ebody)) < 2:
            err(f"дипломатика: событие {eid} меньше двух опций -- нет пути "
                "отказа партнёра")

    # 2. ультиматум: запуск + wargoal за отказ
    on_actions = ''
    for p in walk('common/on_actions', ('.txt',)):
        on_actions += strip_comments(read(p))
    if not re.search(r'glp_crisis\.1(?!\d)', on_actions):
        err("дипломатика: ультиматум Москвы (glp_crisis.1) не запускается "
            "из on_actions -- война-якорь никогда не наступит")
    crisis2 = event_body('glp_crisis.2')
    if crisis2 is None:
        err('дипломатика: событие glp_crisis.2 (ультиматум: отказ) не найдено')
    elif 'create_wargoal' not in crisis2:
        err("дипломатика: glp_crisis.2 без create_wargoal -- отказ от "
            "ультиматума ничего не стоит Москве")

    # 3. отказ от пакта = механическая цена
    for eid in PACT_EVENTS:
        ebody = event_body(eid)
        if ebody is None:
            err(f"дипломатика: событие {eid} не найдено в events/")
            continue
        if 'GLP_idea_isolated_resistance' not in ebody:
            err(f"дипломатика: в событии {eid} отказ от пакта не несёт "
                "механической цены (GLP_idea_isolated_resistance)")

    # 4. ограниченность помощи
    dec_text = ''
    for p in walk('common/decisions', ('.txt',)):
        dec_text += strip_comments(read(p))
    m = re.search(r'GLP_receive_lend_lease = \{(.*?)\n\t\}', dec_text, re.S)
    if not m:
        err('дипломатика: решение ленд-лиза GLP_receive_lend_lease не найдено')
    else:
        dr = re.search(r'days_remove = (\d+)', m.group(1))
        if not dr or int(dr.group(1)) < 360:
            err("дипломатика: кулдаун ленд-лиза меньше года -- помощь "
                "не ограничена")
    m = re.search(r'GLP_white_volunteer_wave = \{(.*?)\n\t\}', dec_text, re.S)
    if not m:
        err('дипломатика: решение GLP_white_volunteer_wave не найдено')
    else:
        blk = m.group(1)
        dr = re.search(r'days_remove = (\d+)', blk)
        if not dr or int(dr.group(1)) < 90:
            err("дипломатика: кулдаун волны волонтёров меньше 90 дней -- "
                "фарм л/с")
        if 'check_variable' not in blk:
            err("дипломатика: у волны волонтёров нет лимита числа волн "
                "(check_variable) -- бесконечные л/с")


# ------------------------------------------------- 17. пейсинг дерева (Спринт 3)
CAPSTONE_Y = 18
FOREIGN_FOCUS_TAGS = re.compile(
    r'\b(SOV|GER|ENG|ROM|TUR|POL|SPR|ITA|FRA|USA|JAP|AUS|HUN|RUM|BUL|YUG|'
    r'PER|AFG|LIT|LAO|CZE|SER|DEN|NOR|SWE|FIN)\b')


def _brace_block(body, kw):
    """Текст внутри первого `kw = { ... }` с матчингом скобок."""
    m = re.search(r'\b' + kw + r'\s*=\s*\{', body)
    if not m:
        return None
    depth, j = 1, m.end()
    while depth and j < len(body):
        if body[j] == '{':
            depth += 1
        elif body[j] == '}':
            depth -= 1
        j += 1
    return body[m.end():j - 1]


def check_focus_pacing():
    """Фаза C (Спринт 3): пейсинг спроектирован, а не случаен.
    1. Верх (y <= 2): cost <= 5 — политический старт идёт быстро.
    2. Середина (3 <= y <= 17): cost <= 7 — никаких стен по 100 ПП.
    3. Капстоуны (y >= 18): cost <= 7 и осмысленный available
       (date/has_war/controls_state) — «чудо/наследие» не берётся сразу.
    4. Капстоуны попарно mutually_exclusive — нижний ряд это выбор,
       а не «собрать всё».
    5. available с foreign-tag обязан иметь bypass, покрывающий этот
       тег — мёртвый/вражеский партнёр не должен замораживать дерево.
    6. Флот-терминал (glory_of_the_sea) привязан к Крыму (стейт 137),
       воздух-терминал (mastery_of_the_skies) — к Донбассу (стейт 227).
    """
    capstones = []
    for p in walk('common/national_focus', ('.txt',)):
        for fid, body in _focus_blocks(p):
            y = re.search(r'^\s*y = (-?\d+)\s*$', body, re.M)
            c = re.search(r'^\s*cost = (\d+(?:\.\d+)?)\s*$', body, re.M)
            if not (y and c):
                err(f"пейсинг: фокус '{fid}' без парсеуемых y/cost "
                    "(проверьте формат строк)")
                continue
            yv, cv = int(y.group(1)), float(c.group(1))
            if yv <= 2 and cv > 5:
                err(f"пейсинг: верхний фокус '{fid}' (y={yv}) cost {cv:g} > 5 "
                    "-- старт слишком медленный")
            if 3 <= yv <= 17 and cv > 7:
                err(f"пейсинг: средний фокус '{fid}' (y={yv}) cost {cv:g} > 7 "
                    "-- стена по 100 ПП")
            if yv >= CAPSTONE_Y:
                capstones.append(fid)
                if cv > 7:
                    err(f"пейсинг: капстон '{fid}' cost {cv:g} > 7")
                av = _brace_block(body, 'available')
                if not av or not re.search(r'date|has_war|controls_state', av):
                    err(f"пейсинг: капстон '{fid}' без available-гейта "
                        "(date/has_war/controls_state) -- «чудо» доступно "
                        "с самого начала")
    # 4. попарный ME капстоунов
    for p in walk('common/national_focus', ('.txt',)):
        for fid, body in _focus_blocks(p):
            if fid not in capstones:
                continue
            me = _brace_block(body, 'mutually_exclusive') or ''
            missing = [f for f in capstones
                       if f != fid and not re.search(r'focus = %s\b' % f, me)]
            if missing:
                err(f"пейсинг: капстон '{fid}' не исключает {missing} -- "
                    "нижний ряд можно собрать весь")
    # 5. foreign-tag в available -> bypass
    for p in walk('common/national_focus', ('.txt',)):
        for fid, body in _focus_blocks(p):
            av = _brace_block(body, 'available')
            if av and FOREIGN_FOCUS_TAGS.search(av):
                bp = _brace_block(body, 'bypass')
                if not bp or not FOREIGN_FOCUS_TAGS.search(bp):
                    err(f"пейсинг: фокус '{fid}' ссылается на чужую страну в "
                        "available, но bypass не покрывает её -- мёртвый "
                        "партнёр заморозит дерево")
    # 6. гейты флота/воздуха
    for p in walk('common/national_focus', ('.txt',)):
        for fid, body in _focus_blocks(p):
            if fid == 'GLP_glory_of_the_sea' and 'controls_state = 137' not in body:
                err("пейсинг: флот-терминал (glory_of_the_sea) не привязан "
                    "к Крыму (controls_state = 137)")
            if fid == 'GLP_mastery_of_the_skies' and 'controls_state = 227' not in body:
                err("пейсинг: воздух-терминал (mastery_of_the_skies) не "
                    "привязан к Донбассу (controls_state = 227)")
    STATS['focus_pacing_capstones'] = len(capstones)


# ------------------------------------------------- 18. решения: рычаг с ценой, а не фарм
def _decision_blocks():
    """{decision_id: body} по common/decisions."""
    out = {}
    for p in walk('common/decisions', ('.txt',)):
        text = strip_comments(read(p))
        for m in re.finditer(r'\n\t(GLP_[A-Za-z0-9_]+) = \{', text):
            start, depth, j = m.end(), 1, m.end()
            while depth > 0 and j < len(text):
                if text[j] == '{':
                    depth += 1
                elif text[j] == '}':
                    depth -= 1
                j += 1
            out[m.group(1)] = text[start:j - 1]
    return out


def check_decision_economy():
    """Фаза D (Спринт 4): решения — рычаг с ценой, а не бесплатный
    генератор ресурсов.
    1. Решение с грантом (>= 1000 л/с или любое положительное
       снаряжение) должно быть ограничено: fire_only_once = yes,
       либо кулдаун >= 120, либо кулдаун >= 90 при цене >= 40, либо
       оно само стоит >= 1500 л/с (рейд-луп платит за себя).
    2. Рейд (GLP_conduct_cavalry_partisan_raid) имеет state_target и
       target_trigger — рейд не «в эфире».
    3. Испания (GLP_send_brigade_to_cnt_fai): проверка склада
       (has_equipment), честное списание (отрицательный amount) и
       испанская сторона видит бригаду (событие в скоупе SPR).
    4. Не меньше 4 оккупационных решений, гейтнутых контролем стейта
       (is_controlled_by = ROOT).
    5. Событие риска рейда glp_raid.1 существует.
    """
    decs = _decision_blocks()

    def cooldown(body):
        vals = []
        for kw in ('days_remove', 'days_re_enable'):
            m = re.search(r'\b' + kw + r'\s*=\s*(\d+)', body)
            if m:
                vals.append(int(m.group(1)))
        return max(vals) if vals else 0

    granted = 0
    for did, body in sorted(decs.items()):
        mp = [int(v) for v in re.findall(r'add_manpower = ([1-9]\d*)', body)]
        eq = re.findall(r'add_equipment_to_stockpile = \{[^}]*amount = ([1-9]\d*)', body)
        if not (any(v >= 1000 for v in mp) or eq):
            continue
        granted += 1
        cost = re.search(r'^\s*cost = (\d+)', body, re.M)
        cost = int(cost.group(1)) if cost else 0
        cd = cooldown(body)
        mp_cost = min((int(v) for v in
                       re.findall(r'add_manpower = -([1-9]\d*)', body)), default=0)
        if ('fire_only_once = yes' in body
                or cd >= 120
                or (cd >= 90 and cost >= 40)
                or mp_cost >= 1500):
            continue
        err(f"решение '{did}': грант л/с/снаряжения без ограничения "
            "(нет fire_only_once, кулдаун < 120, цена < 40, нет "
            "собственной цены в л/с) -- фарм")

    raid = decs.get('GLP_conduct_cavalry_partisan_raid')
    if raid is None:
        err('решения: рейд GLP_conduct_cavalry_partisan_raid отсутствует')
    else:
        if not re.search(r'target = \{\s*type = state', raid):
            err('решения: у рейда нет state_target (target = { type = state })')
        if 'target_trigger = {' not in raid:
            err('решения: у рейда нет target_trigger -- целятся в любой стейт')

    spain = decs.get('GLP_send_brigade_to_cnt_fai')
    if spain is None:
        err('решения: помощь Испании GLP_send_brigade_to_cnt_fai отсутствует')
    else:
        if not re.search(r'has_equipment = \{\s*[a-z_0-9]+ > \d+', spain):
            err("решения: у Испании нет проверки склада (has_equipment) -- "
                "винтовки можно списать в минус")
        if not re.search(r'amount = -\d+', spain):
            err("решения: Испания не списывает собственный склад "
                "(нет отрицательного amount) -- бригада бесплатная")
        # SPR-скоп ищем в complete_effect: в available тоже есть
        # `SPR = { ... }` (проверка гражданской войны), и это не то.
        ce = _brace_block(spain, 'complete_effect')
        spr_blk = _brace_block(ce, 'SPR') if ce else None
        if spr_blk is None or not re.search(r'\b(news_event|country_event)\s*=\s*\{', spr_blk):
            err('решения: испанская сторона не видит бригаду '
                '(нет события в скоупе SPR)')

    occ = [d for d, b in decs.items() if 'is_controlled_by = ROOT' in b]
    if len(occ) < 4:
        err(f"решения: оккупационных решений (гейт is_controlled_by) "
            f"только {len(occ)}, нужно >= 4")

    found = False
    for p in walk('events', ('.txt',)):
        if re.search(r'^\tid = glp_raid\.1$', strip_comments(read(p)), re.M):
            found = True
    if not found:
        err('события: событие риска рейда glp_raid.1 отсутствует')

    STATS['decisions_with_grants'] = granted


# ------------------------------------------------- 19. снаряжение: ключи 1.19
KNOWN_119_EQUIPMENT = {
    'small_arms_equipment_1', 'small_arms_equipment_2', 'small_arms_equipment_3',
    'support_equipment',
    'anti_tank_equipment_1', 'anti_tank_equipment_2',
    'artillery_equipment_1', 'artillery_equipment_2',
    'motorized_equipment', 'truck_equipment', 'train_equipment',
    # С 1.13 (T-A) танк = шасси + орудие; «*_tank_equipment_*» в 1.19
    # не существует.
    'light_tank_chassis_1', 'light_tank_chassis_2',
    'medium_tank_chassis_1', 'medium_tank_chassis_2',
    'heavy_tank_chassis_1',
    'light_tank_gun_1', 'light_tank_gun_2',
    'medium_tank_gun_1', 'medium_tank_gun_2',
    'heavy_tank_gun_1',
    'destroyer_hull_1', 'destroyer_hull_2',
    'light_cruiser_hull_1', 'light_cruiser_hull_2',
    'heavy_cruiser_hull_1', 'heavy_cruiser_hull_2',
    'battleship_hull_1', 'battleship_hull_2',
    'capital_ship_hull_1', 'capital_ship_hull_2',
    'carrier_hull_1', 'carrier_hull_2',
    'submarine_hull_1',
}


def check_equipment_keys():
    """1.19 (Спринт 5): ключ снаряжения обязан существовать.

    Движок не роняет ошибку на неизвестном type в
    add_equipment_to_stockpile -- он молча игнорирует эффект (трофеи и
    решения «не работают» без следа), а has_equipment с чужим ключом
    всегда ложь (решение навсегда недоступно). Сканируем common/,
    events/, history/. Плюс инварианты трофейного лупа:
    tech_maintenance_company в стартовом set_technology (луп активен с
    1936) и шаблон «Тачаночный курень» в OOB 1936.
    """
    seen = 0
    for subdir in ('common', 'events', 'history'):
        for p in walk(subdir, ('.txt',)):
            text = strip_comments(read(p))
            for m in re.finditer(
                    r'add_equipment_to_stockpile\s*=\s*\{\s*type\s*=\s*([A-Za-z0-9_]+)',
                    text):
                seen += 1
                if m.group(1) not in KNOWN_119_EQUIPMENT:
                    err(f"снаряжение: {rel(p)}: '{m.group(1)}' -- не ключ 1.19, "
                        "движок молча проигнорирует эффект")
            for m in re.finditer(r'has_equipment\s*=\s*\{\s*([A-Za-z0-9_]+)', text):
                seen += 1
                if m.group(1) not in KNOWN_119_EQUIPMENT:
                    err(f"снаряжение: {rel(p)}: has_equipment '{m.group(1)}' -- "
                        "не ключ 1.19, условие всегда ложно")
    found_tech = False
    for p in walk('history/countries', ('.txt',)):
        if 'tech_maintenance_company' in strip_comments(read(p)):
            found_tech = True
    if not found_tech:
        err("трофеи: нет tech_maintenance_company в стартовом set_technology -- "
            "трофейный луп РПА не будет активен с 1936")
    found_tpl = False
    for p in walk('history/units', ('.txt',)):
        if 'Тачаночный курень' in read(p):
            found_tpl = True
    if not found_tpl:
        err('трофеи: шаблон «Тачаночный курень» отсутствует в OOB 1936')
    STATS['equipment_refs'] = seen


# ------------------------------------------------- 20. .gfx: безопасность парсера
def check_gfx_parse_safety():
    """.gfx: парсер не прощает структуры (регрессия 2026-08-26).

    1. В файле ровно ОДИН топ-уровневый блок `spriteTypes = { ... }`:
       второй блок ломает разбор, и ВСЕ спрайты файла перестают
       грузиться (симптом в игре: пропал фон главного меню / фон и
       фотографии заставки, при этом тексты и ванильные кнопки на месте).
    2. Поля `effectFile` и подблок `animation = { ... }` внутри
       spriteType/corneredTileSpriteType/frameAnimatedSpriteType не
       поддерживаются парсером 1.19 — тот же симптом. (В progressbartype
       effectFile — валидное ванильное поле, оно не проверяется;
       frameAnimatedSpriteType с noOfFrames — валидный вид анимации.)
    """
    seen = 0
    sprite_kinds = ('spriteType = {', 'corneredTileSpriteType = {',
                    'frameAnimatedSpriteType = {')
    for p in walk('interface', ('.gfx',)):
        seen += 1
        text = strip_comments(read(p))
        n = len(re.findall(r'^spriteTypes\s*=\s*\{', text, re.M))
        if n == 0:
            err(f".gfx: {rel(p)}: нет блока spriteTypes")
        elif n > 1:
            err(f".gfx: {rel(p)}: {n} блока spriteTypes -- второй "
                "топ-уровневый блок ломает парсер, все спрайты файла "
                "перестают грузиться")
        for kind in sprite_kinds:
            for m in re.finditer(r'\b' + re.escape(kind), text):
                depth, j = 1, m.end()
                while depth and j < len(text):
                    if text[j] == '{':
                        depth += 1
                    elif text[j] == '}':
                        depth -= 1
                    j += 1
                body = text[m.end():j - 1]
                nm = re.search(r'name = "([^"]+)"', body)
                label = nm.group(1) if nm else '?'
                if 'effectFile' in body:
                    err(f".gfx: {rel(p)}: спрайт '{label}' содержит "
                        "effectFile -- неподдерживаемое парсером 1.19 "
                        "поле, файл не загрузится")
                if re.search(r'\banimation\s*=\s*\{', body):
                    err(f".gfx: {rel(p)}: спрайт '{label}' содержит "
                        "подблок animation = {{}} -- неподдерживаемый "
                        "парсером 1.19, файл не загрузится")
    if seen == 0:
        err('.gfx: в interface/ не найдено ни одного .gfx')
    STATS['gfx_files'] = seen


# ------------------------------------------------- 21. модуль «Иберийский пожар и Чёрный Интернационал»
def check_spain_module():
    """Модуль «Иберийский пожар и Чёрный Интернационал»: целостность
    связей событие -> флаги -> решения -> развилка -> фракция.
    1. glp_spain.1: три взаимоисключающих выбора, каждый ставит свой
       флаги маршрута + общий glp_spain_choice_made.
    2. Запуск — через on_actions (флаг glp_spain_war_active), а не
       через постоянный mean_time_to_happen-сканер.
    3. Три контрабандных маршрута: скриптовая проверка риска
       (random = N), честное списание (отрицательный amount),
       кулдаун >= 90.
    4. КРО-решение ставит glp_kro_barcelona; событие майских дней
       разветвляется по этому флагу.
    5. Пакт: create_faction + add_to_faction = SPR + оба нацдуха.
    6. Черта GLP_spanish_tempering в /common/unit_leader/; шаблон
       бригады в загружаемом OOB (GLP_1936).
    """
    ev = {}
    for p in walk('events', ('.txt',)):
        text = strip_comments(read(p))
        for m in re.finditer(r'(?:country_event|news_event)\s*=\s*\{', text):
            depth, j = 1, m.end()
            while depth and j < len(text):
                if text[j] == '{':
                    depth += 1
                elif text[j] == '}':
                    depth -= 1
                j += 1
            body = text[m.end():j - 1]
            eid = re.search(r'\bid = ([A-Za-z0-9_.]+)', body)
            if eid:
                ev[eid.group(1)] = (p, body)

    # 1. Иберийский пожар
    sp1 = ev.get('glp_spain.1')
    if sp1 is None:
        err('модуль Испании: событие glp_spain.1 отсутствует')
    else:
        _p, body = sp1
        if len(re.findall(r'\boption = \{', body)) < 3:
            err('модуль Испании: glp_spain.1 меньше трёх вариантов выбора')
        if 'glp_spain_choice_made' not in body:
            err('модуль Испании: glp_spain.1 не ставит glp_spain_choice_made '
                '(событие повторится)')
        for flag in ('glp_spain_open_route', 'glp_spain_secret_route',
                     'glp_spain_refused'):
            if flag not in body:
                err(f'модуль Испании: glp_spain.1 не ставит {flag}')

    # 2. Запуск через on_actions
    on_actions = ''
    for p in walk('common/on_actions', ('.txt',)):
        on_actions += strip_comments(read(p))
    if 'glp_spain_war_active' not in on_actions:
        err('модуль Испании: glp_spain_war_active не ставится в on_actions '
            '(событие не запустится)')

    # 3. Контрабандные коридора
    dec_text = ''
    for p in walk('common/decisions', ('.txt',)):
        dec_text += strip_comments(read(p))
    for did, min_cd in (('GLP_spain_black_sea_run', 90),
                        ('GLP_spain_balkan_underground_traffic', 90),
                        ('GLP_spain_french_syndicate_smuggling', 90)):
        m = re.search(r'\t' + did + r' = \{(.*?)\n\t\t\}', dec_text, re.S)
        if not m:
            err(f'модуль Испании: решение {did} отсутствует')
            continue
        body = m.group(1)
        if 'random = ' not in body:
            err(f'модуль Испании: {did} без скриптовой проверки риска '
                '(random = N)')
        if not re.search(r'amount = -\d+', body):
            err(f'модуль Испании: {did} не списывает собственный склад '
                '(нет отрицательного amount)')
        cd = re.search(r'days_remove = (\d+)', body)
        if not cd or int(cd.group(1)) < min_cd:
            err(f'модуль Испании: {did} без кулдауна >= {min_cd} дней '
                '(фарм-маршрут)')

    # 4. КРО + развилка майских дней
    kro = re.search(r'\tGLP_spain_send_kro_group = \{(.*?)\n\t\t\}',
                    dec_text, re.S)
    if not kro or 'glp_kro_barcelona' not in kro.group(1):
        err('модуль Испании: КРО-решение не ставит glp_kro_barcelona')
    bc1 = ev.get('glp_barcelona.1')
    if bc1 is None:
        err('модуль Испании: событие glp_barcelona.1 отсутствует')
    else:
        _p, body = bc1
        if 'glp_kro_barcelona' not in body:
            err('модуль Испании: glp_barcelona.1 не разветвляется по '
                'флагу КРО (glp_kro_barcelona)')
        if 'glp_spanish_programs_shut' not in body:
            err('модуль Испании: glp_barcelona.1 не сворачивает программы '
                'помощи (glp_spanish_programs_shut)')

    # 5. Пакт Чёрного Интернационала
    pact = re.search(r'\tGLP_spain_black_international_pact = \{(.*?)\n\t\t\}',
                     dec_text, re.S)
    if not pact:
        err('модуль Испании: решение GLP_spain_black_international_pact '
            'отсутствует')
    else:
        body = pact.group(1)
        if 'create_faction' not in body:
            err('модуль Испании: пакт не создаёт фракцию')
        if 'add_to_faction = SPR' not in body:
            err('модуль Испании: пакт не вводит SPR во фракцию')
        for idea in ('GLP_idea_catalan_wolfram_syndicate_workshops',
                     'GLP_idea_ukrainian_coal_and_grain'):
            if idea not in body:
                err(f'модуль Испании: пакт не выдаёт {idea}')

    # 6. Черта и шаблон бригады
    trait_found = False
    for p in walk('common/unit_leader', ('.txt',)):
        if 'GLP_spanish_tempering' in strip_comments(read(p)):
            trait_found = True
    if not trait_found:
        err('модуль Испании: черта GLP_spanish_tempering не найдена в '
            '/common/unit_leader/')
    oob = ''
    for p in walk('history/units', ('.txt',)):
        oob += read(p)
    if 'Бригада РПАУ добровольцев' not in oob:
        err('модуль Испании: шаблон «Бригада РПАУ добровольцев» не в OOB')
    home = re.search(r'\tGLP_spain_brigade_homecoming = \{(.*?)\n\t\t\}',
                     dec_text, re.S)
    if not home or 'GLP_spanish_tempering' not in home.group(1):
        err('модуль Испании: GLP_spain_brigade_homecoming не выдаёт черту')

    # Духи модуля в локализации покрывает check_characters (RU обяз.,
    # EN — паритет); локализация опций событий — check_events.
    STATS['spain_module_events'] = len(ev)


def main():
    check_syntax()
    loc = load_loc()
    defs = collect_definitions()
    check_duplicates(defs)
    check_sprites(defs)
    check_portraits()
    check_screens()
    check_loading_tips()
    check_music()
    check_cinematic_intro_voice()
    check_loc_font_charset()
    check_intro_gui_keys(loc)
    check_intro_no_crawl()
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
    check_advisor_portraits(defs)
    check_unit_models()
    check_entity_graph()
    check_no_stray_art()
    check_loc_tech_names(loc)
    check_dds_transparency()
    check_focus_search_filters()
    check_focus_branch_headers()
    check_idea_modifier_keys()
    check_advisor_frames()
    check_idea_slot_model()
    check_diplomacy_mechanics(defs)
    check_focus_pacing()
    check_decision_economy()
    check_equipment_keys()
    check_gfx_parse_safety()
    check_spain_module()

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
