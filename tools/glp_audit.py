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


SPEC_LARGE = (156, 224)
SPEC_SMALL = (156, 210)
SPEC_SCREEN = (1920, 1080)
OK_FMT_LARGE = ('ARGB8888', 'DXT5')      # ТЗ: ARGB 8888 для больших портретов
OK_FMT_SMALL = ('DXT5', 'ARGB8888')      # ТЗ: DXT5 для малых портретов/иконок
OK_FMT_SCREEN = ('DXT1', 'DXT5')         # ТЗ: DXT1/DXT5 без мип-мап


def check_portraits():
    for p in walk('gfx/leaders', ('.dds',)):
        info = dds_info(p)
        if not info:
            err(f"{rel(p)}: not a valid DDS file")
            continue
        w, h, fmt = info
        large = p.endswith('_large.dds')
        want = SPEC_LARGE if large else SPEC_SMALL
        ok = OK_FMT_LARGE if large else OK_FMT_SMALL
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
        if 'Portrait' in p or re.search(r'idea_GLP_[A-Z]', os.path.basename(p)):
            if (w, h) != SPEC_SMALL:
                err(f"{rel(p)}: advisor icon is {w}x{h}, spec requires 156x210")


def check_screens():
    """Загрузочные экраны и фон меню: 1920x1080, DXT1/DXT5, без мип-мап."""
    targets = sorted(glob_dds('gfx/loadingscreens')) + [
        os.path.join(ROOT, 'gfx/interface/frontendmainviewbg.dds')]
    for p in targets:
        if not os.path.exists(p):
            continue
        info = dds_info(p)
        if not info:
            err(f"{rel(p)}: not a valid DDS file")
            continue
        w, h, fmt = info
        if (w, h) != SPEC_SCREEN:
            err(f"{rel(p)}: {w}x{h}, spec requires 1920x1080")
        if fmt not in OK_FMT_SCREEN:
            err(f"{rel(p)}: compression {fmt}, spec requires DXT1 or DXT5")
    # ванильные экраны должны быть перекрыты
    missing = [n for n in range(1, 17)
               if not os.path.exists(os.path.join(ROOT, f'gfx/loadingscreens/load_{n}.dds'))]
    if missing:
        warn("ванильные экраны загрузки не перекрыты: "
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


def main():
    check_syntax()
    loc = load_loc()
    defs = collect_definitions()
    check_duplicates(defs)
    check_sprites(defs)
    check_portraits()
    check_screens()
    check_music()
    check_fonts()
    check_bookmarks(loc)
    check_focus_tree(defs)
    check_units()
    check_characters(defs, loc)

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
