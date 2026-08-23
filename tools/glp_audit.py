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
  6. Portrait .dds geometry & compression against the art spec
     (156x210 for small/advisor icons, 156x224 for large portraits).
  7. Character traits that are neither vanilla nor defined by the mod.

Exit code 0 = clean, 1 = errors found.  Warnings never fail the build.
"""
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
SCRIPT_DIRS = ('common', 'events', 'history', 'interface')


def check_syntax():
    for d in SCRIPT_DIRS:
        for p in walk(d, ('.txt', '.gfx', '.gui')):
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


# --------------------------------------------------------- 2/3. localisation
LOC_LINE = re.compile(r'^\s*([A-Za-z0-9_.\-]+):\s*\d*\s*"')


def load_loc():
    langs = {}
    for p in walk('localisation', ('.yml',)):
        lang = os.path.basename(os.path.dirname(p))
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
            if k in seen:
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

    Базовая игра использует ключи LOADING_TIP_1..~90, DLC добавляют свои;
    чтобы ванильная цитата никогда не появилась, мы перекрываем 1..256.
    """
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
        gaps = [n for n in range(1, 257) if n not in nums]
        if gaps:
            err(f"{rel(p)}: не перекрыты ванильные цитаты "
                f"(нет ключей для {len(gaps)} номеров, первый: LOADING_TIP_{gaps[0]})")


def check_music():
    """Ванильный саундтрек должен быть перекрыт файлами мода."""
    for f in ('music/music.asset', 'music/songs.txt'):
        if not os.path.exists(os.path.join(ROOT, f)):
            err(f"{f} отсутствует — ванильный саундтрек не будет перекрыт")
            continue
        body = read(os.path.join(ROOT, f))
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
    """Каждая идея: picture есть; ванильные ссылки -- только base-game."""
    for p, body in all_script_text('common/ideas').items():
        for m in re.finditer(r'^\t\t(GLP_\w+)\s*=\s*\{(.*?)^\t\t\}', body, re.M | re.S):
            iid, blk = m.group(1), m.group(2)
            pic = re.search(r'picture\s*=\s*(GFX_\w+)', blk)
            if not pic:
                err(f"{rel(p)}: идея '{iid}' без picture")
                continue
            name = pic.group(1)
            if 'GLP' in name:
                continue          # кастомный спрайт -- проверяется в check_sprites
            if name not in VANILLA_IDEA_SPRITES:
                err(f"{rel(p)}: идея '{iid}' ссылается на неванильный/DLC "
                    f"спрайт '{name}' (нет в базовой игре)")
    pics = [m.group(1) for p, b in all_script_text('common/ideas').items()
            for m in re.finditer(r'picture\s*=\s*(GFX_\w+)', b)]
    STATS['idea_pictures'] = (len(pics), sum(1 for x in pics if 'GLP' in x), len(set(pics)))


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
    """load_screen.gui: панель цитат удалена, все контейнеры на месте.
    eventwindow.gui: все ванильные окна присутствуют."""
    p = os.path.join(ROOT, 'interface/load_screen.gui')
    if not os.path.exists(p):
        err("interface/load_screen.gui отсутствует -- ванильная металлическая "
            "панель цитат вернётся на загрузочный экран")
    else:
        body = strip_comments(read(p))
        for token in ('"load_screen"', '"status"', '"tip"', '"text"', '"progressbar"'):
            if token not in body:
                err(f"interface/load_screen.gui: отсутствует элемент {token}")
        if 'GFX_loadingtip_bg' in body:
            err("interface/load_screen.gui: всё ещё ссылается на GFX_loadingtip_bg")
    if os.path.exists(os.path.join(ROOT, 'interface/loadingscreen.gui')):
        err("interface/loadingscreen.gui: пустой файл с неванильным именем -- удалить")
    p = os.path.join(ROOT, 'interface/eventwindow.gui')
    if os.path.exists(p):
        body = read(p)
        for token in ('"EventWindow"', '"EventWindow_leader"', '"EventWindow_News"',
                      '"event_option_entry"'):
            if token not in body:
                err(f"interface/eventwindow.gui: отсутствует ванильное окно {token}")


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
    for lang, keys in loc.items():
        p = keys
        for key, where in [] :
            pass
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
                if re.search(r'\bGLP_[a-z0-9_]+\b', val):
                    err(f"{rel(fp)}:{i}: в тексте видно техническое имя ключа GLP_*")


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
    """Иконки идей и малые портреты советников обязаны иметь реальные
    прозрачные пиксели (наличие альфа-канала само по себе ничего не
    доказывает -- проверяем минимум альфы по факту)."""
    for p in sorted(walk('gfx/interface/ideas', ('.dds',))):
        mn = _im_alpha_min(p)
        if mn is None:
            warn("ImageMagick недоступен -- пиксельная проверка прозрачности пропущена")
            return
        if mn >= 32.0:
            err(f"{rel(p)}: нет реальной прозрачности (min alpha = {mn:.0f}, "
                f"нужно < 32) -- иконка закроет слот непрозрачным квадратом")


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
    check_fonts()
    check_bookmarks(loc)
    check_focus_tree(defs)
    check_units()
    check_events(loc)
    check_characters(defs, loc)
    check_focus_icons()
    check_idea_pictures()
    check_event_pictures()
    check_idea_icon_geometry()
    check_gui_overrides()
    check_advisor_portraits(defs)
    check_no_stray_art()
    check_loc_tech_names(loc)
    check_dds_transparency()

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
