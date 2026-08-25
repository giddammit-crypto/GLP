#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GLP: `search_filters` assignment / verification for common/national_focus/GLP_focus.txt.

WHY THIS EXISTS
---------------
Since HoI4 1.9 the National Focus window has a search box and a row of filter
chips (Political / Research / Industry / Stability / War Support / Manpower /
Territorial Expansion).  A focus only shows up in those results if it declares

        search_filters = { FOCUS_FILTER_POLITICAL ... }

Vanilla ships that line on every single focus.  GLP had it on none of its 190
focuses, so the whole tree was invisible to the in-game focus search -- a
visible polish gap against any official DLC.

Only the seven GENERIC filter tokens are used here.  The rest of the vanilla
set (FOCUS_FILTER_CHI_INFLATION, FOCUS_FILTER_USA_CONGRESS,
FOCUS_FILTER_TFV_AUTONOMY, FOCUS_FILTER_MEX_*, FOCUS_FILTER_SPA_CIVIL_WAR,
FOCUS_FILTER_FRA_*) is tied to another country's/DLC's UI and would show a
meaningless chip on the GLP panel.

HOW FILTERS ARE CHOSEN
----------------------
Deterministically, from two signals only -- no hand-waving:
  1. the focus icon (a table of vanilla sprite -> category), and
  2. what the focus actually does in `completion_reward`
     (add_stability / add_war_support / conscription / factories /
      transfer_state / create_wargoal / add_tech_research ...).
`FOCUS_FILTER_POLITICAL` is the guaranteed fallback so no focus can ever end
up with an empty list.

USAGE
-----
    tools/assign_focus_filters.py --check      # verify tree == tsv  (exit 1 on drift)
    tools/assign_focus_filters.py --write-tsv  # regenerate tools/focus_search_filters.tsv
    tools/assign_focus_filters.py --apply      # insert/replace the line in GLP_focus.txt

`--apply` is idempotent: re-running it produces byte-identical output.
"""
import argparse
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FOCUS_FILE = os.path.join(ROOT, 'common', 'national_focus', 'GLP_focus.txt')
TSV_FILE = os.path.join(ROOT, 'tools', 'focus_search_filters.tsv')

POLITICAL = 'FOCUS_FILTER_POLITICAL'
RESEARCH = 'FOCUS_FILTER_RESEARCH'
INDUSTRY = 'FOCUS_FILTER_INDUSTRY'
STABILITY = 'FOCUS_FILTER_STABILITY'
WAR_SUPPORT = 'FOCUS_FILTER_WAR_SUPPORT'
MANPOWER = 'FOCUS_FILTER_MANPOWER'
ANNEXATION = 'FOCUS_FILTER_ANNEXATION'

VALID_FILTERS = (POLITICAL, RESEARCH, INDUSTRY, STABILITY,
                 WAR_SUPPORT, MANPOWER, ANNEXATION)

# ---------------------------------------------------------------------------
# icon -> categories.  Keys are bare sprite names (without the GFX_ prefix);
# matched by exact name first, then by substring as a fallback.
# ---------------------------------------------------------------------------
ICON_EXACT = {
    # --- army / manpower ---------------------------------------------------
    'GFX_goal_generic_army_doctrines': (MANPOWER,),
    'GFX_goal_generic_small_arms': (MANPOWER, INDUSTRY),
    'GFX_goal_generic_cavalry': (MANPOWER,),
    'GFX_goal_generic_army_motorized': (MANPOWER, RESEARCH),
    'GFX_goal_generic_army_tanks': (MANPOWER, RESEARCH),
    'GFX_goal_generic_build_tank': (MANPOWER, RESEARCH),
    'GFX_goal_generic_special_forces': (MANPOWER,),
    'GFX_goal_generic_defence': (MANPOWER,),
    'GFX_goal_generic_position_armies': (MANPOWER,),
    'GFX_goal_generic_allies_build_infantry': (MANPOWER,),
    'GFX_goal_generic_fortify_city': (MANPOWER, INDUSTRY),
    'GFX_focus_generic_anti_tank_guns': (MANPOWER, RESEARCH),
    'GFX_focus_generic_coastal_fort': (MANPOWER, INDUSTRY),
    'GFX_focus_generic_forest_brothers': (MANPOWER,),
    'GFX_focus_generic_military_academy': (MANPOWER, RESEARCH),
    'GFX_focus_generic_supply_line': (MANPOWER, INDUSTRY),
    'GFX_focus_generic_mechanized': (MANPOWER, RESEARCH),
    'GFX_focus_generic_military_mission': (MANPOWER, POLITICAL),
    # --- navy / air --------------------------------------------------------
    'GFX_goal_generic_navy_battleship': (MANPOWER, RESEARCH),
    'GFX_goal_generic_navy_submarine': (MANPOWER, RESEARCH),
    'GFX_goal_generic_construct_naval_dockyard': (INDUSTRY,),
    'GFX_goal_generic_build_airforce': (MANPOWER, RESEARCH),
    'GFX_goal_generic_air_doctrine': (RESEARCH,),
    'GFX_goal_generic_air_fighter': (RESEARCH,),
    'GFX_goal_generic_air_fighter2': (RESEARCH,),
    'GFX_goal_generic_air_bomber': (RESEARCH,),
    'GFX_goal_generic_air_naval_bomber': (RESEARCH,),
    'GFX_goal_generic_CAS': (RESEARCH,),
    'GFX_goal_generic_radar': (RESEARCH,),
    # --- industry ----------------------------------------------------------
    'GFX_focus_generic_mass_production': (INDUSTRY,),
    'GFX_focus_generic_industry_2': (INDUSTRY,),
    'GFX_focus_generic_military_industry': (INDUSTRY,),
    'GFX_focus_generic_steel': (INDUSTRY,),
    'GFX_focus_generic_railroad': (INDUSTRY,),
    'GFX_focus_generic_public_works': (INDUSTRY,),
    'GFX_focus_generic_license_production': (INDUSTRY, POLITICAL),
    'GFX_goal_generic_construct_civ_factory': (INDUSTRY,),
    'GFX_goal_generic_trade': (INDUSTRY, POLITICAL),
    'GFX_goal_generic_scientific_exchange': (RESEARCH, POLITICAL),
    # --- agriculture / welfare / society ----------------------------------
    'GFX_focus_generic_farmland': (INDUSTRY, STABILITY),
    'GFX_focus_generic_agricultural_subsidies': (INDUSTRY, STABILITY),
    'GFX_focus_generic_welfare': (STABILITY,),
    'GFX_focus_generic_field_hostpital': (STABILITY, MANPOWER),
    'GFX_focus_generic_self_management': (STABILITY, POLITICAL),
    'GFX_focus_generic_workers': (INDUSTRY, STABILITY),
    'GFX_focus_generic_workers_and_farmers_rise': (INDUSTRY, STABILITY),
    'GFX_focus_generic_universal_suffrage': (POLITICAL, STABILITY),
    # --- research ----------------------------------------------------------
    'GFX_focus_generic_university_1': (RESEARCH,),
    'GFX_focus_generic_socialist_science': (RESEARCH,),
    'GFX_focus_generic_cryptologic_bomb': (RESEARCH,),
    'GFX_focus_generic_radio_communication': (RESEARCH,),
    'GFX_focus_generic_printing_press': (RESEARCH, STABILITY),
    'GFX_focus_rocketry': (RESEARCH,),
    # --- politics / diplomacy / security ----------------------------------
    'GFX_goal_generic_political_pressure': (POLITICAL,),
    'GFX_goal_generic_improve_relations': (POLITICAL,),
    'GFX_goal_generic_alliance': (POLITICAL,),
    'GFX_goal_generic_major_alliance': (POLITICAL,),
    'GFX_goal_generic_military_deal': (POLITICAL, MANPOWER),
    'GFX_goal_generic_military_sphere': (POLITICAL, ANNEXATION),
    'GFX_goal_generic_neutrality_focus': (POLITICAL,),
    'GFX_goal_generic_national_unity': (POLITICAL, STABILITY),
    'GFX_goal_generic_propaganda': (WAR_SUPPORT, POLITICAL),
    'GFX_goal_generic_major_war': (WAR_SUPPORT, ANNEXATION),
    'GFX_goal_generic_occupy_states_ongoing_war': (ANNEXATION,),
    'GFX_goal_generic_occupy_states_coastal': (ANNEXATION,),
    'GFX_goal_generic_intelligence_exchange': (POLITICAL, RESEARCH),
    'GFX_focus_generic_red_flags': (POLITICAL, WAR_SUPPORT),
    'GFX_focus_generic_conspiracy': (POLITICAL, STABILITY),
    'GFX_focus_generic_secret_service_agency': (POLITICAL,),
    'GFX_focus_generic_national_security': (POLITICAL, STABILITY),
    'GFX_focus_generic_railway_gun': (MANPOWER, INDUSTRY),
    'GFX_focus_generic_air_defense': (RESEARCH, MANPOWER),
    'GFX_focus_generic_anti_fascist_diplomacy': (POLITICAL,),
    'GFX_focus_generic_army_doctrines_2': (MANPOWER, RESEARCH),
    'GFX_focus_generic_balkan_diplomacy': (POLITICAL,),
    'GFX_focus_generic_black_sea_focus': (MANPOWER, ANNEXATION),
    'GFX_focus_generic_coal_mining': (INDUSTRY,),
    'GFX_focus_generic_combined_arms': (MANPOWER, RESEARCH),
    'GFX_focus_generic_court': (POLITICAL, STABILITY),
    'GFX_focus_generic_defensive_reorganization': (MANPOWER,),
    'GFX_focus_generic_destroyer': (MANPOWER, RESEARCH),
    'GFX_focus_generic_economic_recovery': (INDUSTRY, STABILITY),
    'GFX_focus_generic_full_employment': (INDUSTRY, STABILITY),
    'GFX_focus_generic_full_social_mobilization': (MANPOWER, WAR_SUPPORT),
    'GFX_focus_generic_horse_studs': (MANPOWER,),
    'GFX_focus_generic_hydroelectric_energy': (INDUSTRY,),
    'GFX_focus_generic_improve_roads': (INDUSTRY,),
    'GFX_focus_generic_industry_3': (INDUSTRY,),
    'GFX_focus_generic_infiltration': (POLITICAL,),
    'GFX_focus_generic_invite_republican_spanish_exiles': (POLITICAL, MANPOWER),
    'GFX_focus_generic_jet_planes': (RESEARCH,),
    'GFX_focus_generic_join_comintern': (POLITICAL,),
    'GFX_focus_generic_land_reclamation': (INDUSTRY, STABILITY),
    'GFX_focus_generic_little_entente': (POLITICAL,),
    'GFX_focus_generic_merchant_fleet': (INDUSTRY,),
    'GFX_focus_generic_military_dictatorship': (POLITICAL, WAR_SUPPORT),
    'GFX_focus_generic_mining_industry': (INDUSTRY,),
    'GFX_focus_generic_modernize_industry': (INDUSTRY,),
    'GFX_focus_generic_naval_discipline': (MANPOWER, RESEARCH),
    'GFX_focus_generic_naval_invasion': (MANPOWER, ANNEXATION),
    'GFX_focus_generic_offshore_oil_rig': (INDUSTRY,),
    'GFX_focus_generic_population_growth': (STABILITY, MANPOWER),
    'GFX_focus_generic_refit_civilian_ships': (INDUSTRY,),
    'GFX_focus_generic_reinforcing_the_supply_network': (INDUSTRY, MANPOWER),
    'GFX_focus_generic_resource_extraction': (INDUSTRY,),
    'GFX_focus_generic_rubber': (INDUSTRY,),
    'GFX_focus_generic_self_propelled_gun': (RESEARCH, MANPOWER),
    'GFX_focus_generic_stockpile_fuel': (INDUSTRY, WAR_SUPPORT),
    'GFX_focus_generic_strike_at_democracy2': (POLITICAL, WAR_SUPPORT),
    'GFX_focus_generic_strike_at_democracy3': (POLITICAL, WAR_SUPPORT, ANNEXATION),
    'GFX_focus_generic_tank_assault': (MANPOWER, RESEARCH),
    'GFX_focus_generic_the_giant_wakes': (WAR_SUPPORT, MANPOWER),
    'GFX_focus_generic_total_war': (WAR_SUPPORT, MANPOWER),
    'GFX_focus_generic_truck': (INDUSTRY, MANPOWER),
    'GFX_focus_generic_university_2': (RESEARCH,),
    'GFX_focus_generic_university_3': (RESEARCH,),
    'GFX_focus_generic_whispers': (POLITICAL, STABILITY),
    'GFX_focus_generic_women_in_military': (MANPOWER, STABILITY),
}

ICON_SUBSTR = ()   # intentionally empty: the table above is exhaustive (118/118
                   # icons in GLP_focus.txt).  An unmapped icon is an ERROR, not
                   # a silent guess -- that is what keeps the .tsv reviewable.

# ---------------------------------------------------------------------------
# completion_reward signals -> categories.
#
# Deliberately narrow.  An earlier revision keyed STABILITY off
# `add_political_power` and MANPOWER off `add_command_power`, which put
# FOCUS_FILTER_STABILITY on 125 of 190 focuses -- a chip that fires on two
# thirds of the tree filters nothing.  Only effects that are the *point* of a
# focus contribute a chip here; everything else comes from the icon.
# ---------------------------------------------------------------------------
REWARD_SIGNALS = (
    # Territorial expansion: the one effect class the icon cannot show.
    (r'\btransfer_state\b|\bcreate_wargoal\b|\btake_state_focus\b'
     r'|\bannex_country\b', ANNEXATION),
    # A real conscription/division payoff, not just +25 command power.
    (r'\badd_manpower\b|\bload_oob\b|\bdivision_template\b'
     r'|\bset_division_template\b', MANPOWER),
    # Explicit tech unlock.
    (r'\badd_tech_research\b', RESEARCH),
    # A big, deliberate stability swing (>= 5%), not the usual +2%.
    (r'add_stability = -?0\.(?:0[5-9]|[1-9]\d)', STABILITY),
    (r'add_war_support = -?0\.(?:0[5-9]|[1-9]\d)', WAR_SUPPORT),
)

# A focus wears at most this many chips; vanilla rarely exceeds two.
MAX_FILTERS = 3

# Which chip survives when the cap bites.  Earlier = more specific.
FILTER_PRIORITY = (ANNEXATION, WAR_SUPPORT, RESEARCH, MANPOWER,
                   INDUSTRY, STABILITY, POLITICAL)


def parse_focuses(text):
    """Yield (focus_id, icon, full_block_body) for every focus in the tree."""
    out = []
    for m in re.finditer(r'\n\tfocus = \{', text):
        start = m.end()
        depth, j = 1, start
        while depth > 0 and j < len(text):
            if text[j] == '{':
                depth += 1
            elif text[j] == '}':
                depth -= 1
            j += 1
        body = text[start:j - 1]
        fid = re.search(r'^\s*id\s*=\s*(\S+)', body, re.M)
        icon = re.search(r'^\s*icon\s*=\s*(\S+)', body, re.M)
        if fid:
            out.append((fid.group(1), icon.group(1) if icon else '', body))
    return out


def reward_block(body):
    m = re.search(r'\n\t\tcompletion_reward\s*=\s*\{', body)
    if not m:
        return ''
    start = m.end()
    depth, j = 1, start
    while depth > 0 and j < len(body):
        if body[j] == '{':
            depth += 1
        elif body[j] == '}':
            depth -= 1
        j += 1
    return body[start:j - 1]


def filters_for(fid, icon, body):
    """Deterministic filter list for one focus.

    Raises KeyError for an icon that is not in ICON_EXACT -- the caller
    collects those so `--check` can fail loudly instead of guessing.
    """
    hits = []

    def add(f):
        if f not in hits:
            hits.append(f)

    for f in ICON_EXACT[icon]:
        add(f)

    rw = reward_block(body)
    for pattern, cat in REWARD_SIGNALS:
        if re.search(pattern, rw):
            add(cat)

    if not hits:
        add(POLITICAL)

    # Cap, keeping the most specific chips; then emit in canonical order so
    # the .tsv diff stays readable.
    rank = {f: i for i, f in enumerate(FILTER_PRIORITY)}
    hits = sorted(hits, key=lambda f: rank[f])[:MAX_FILTERS]
    order = {f: i for i, f in enumerate(VALID_FILTERS)}
    return sorted(hits, key=lambda f: order[f])


def build_mapping(focuses):
    """focus_id -> [filters], plus the list of unmapped icons found."""
    mapping, unmapped = {}, {}
    for fid, icon, body in focuses:
        if icon not in ICON_EXACT:
            unmapped.setdefault(icon, []).append(fid)
            mapping[fid] = [POLITICAL]
            continue
        mapping[fid] = filters_for(fid, icon, body)
    return mapping, unmapped


def load_tsv(path):
    data = {}
    if not os.path.exists(path):
        return data
    with open(path, encoding='utf-8') as fh:
        for line in fh:
            if line.startswith('#') or not line.strip():
                continue
            parts = line.rstrip('\n').split('\t')
            if len(parts) >= 2:
                data[parts[0]] = parts[1].split()
    return data


def write_tsv(mapping):
    lines = [
        '# GLP focus -> in-game focus-search chips (HOI4 1.19).',
        '#',
        '# `search_filters` in common/national_focus/GLP_focus.txt must match this',
        '# table exactly -- tools/glp_audit.py enforces it, so a newly added focus',
        '# cannot silently drop out of the focus search panel.',
        '#',
        '# Only the seven GENERIC vanilla tokens are used; the country/DLC-specific',
        '# ones (CHI_INFLATION, USA_CONGRESS, TFV_AUTONOMY, MEX_*, SPA_*, FRA_*)',
        '# belong to other nations\' UI and would render a meaningless chip here.',
        '#',
        '# Regenerate with:  tools/assign_focus_filters.py --write-tsv',
        '# Apply to the tree: tools/assign_focus_filters.py --apply',
        '#',
        '# focus_id\tFOCUS_FILTER_*',
    ]
    for fid in mapping:
        lines.append(fid + '\t' + ' '.join(mapping[fid]))
    with open(TSV_FILE, 'w', encoding='utf-8') as fh:
        fh.write('\n'.join(lines) + '\n')


def apply_to_tree(mapping):
    """Insert or replace `search_filters` on every focus. Idempotent."""
    with open(FOCUS_FILE, encoding='utf-8-sig') as fh:
        text = fh.read()

    out = []
    pos = 0
    changed = 0
    for m in re.finditer(r'\n\tfocus = \{', text):
        start = m.end()
        depth, j = 1, start
        while depth > 0 and j < len(text):
            if text[j] == '{':
                depth += 1
            elif text[j] == '}':
                depth -= 1
            j += 1
        block_end = j - 1
        body = text[start:block_end]
        fid_m = re.search(r'^\s*id\s*=\s*(\S+)', body, re.M)
        if not fid_m:
            continue
        fid = fid_m.group(1)
        if fid not in mapping:
            continue
        line = '\n\t\tsearch_filters = { %s }' % ' '.join(mapping[fid])

        existing = re.search(r'\n\t\tsearch_filters = \{[^\n]*\}', body)
        if existing:
            if existing.group(0) == line:
                continue
            new_body = body[:existing.start()] + line + body[existing.end():]
        else:
            anchor = re.search(r'\n\t\tcompletion_reward = \{', body)
            if anchor:
                new_body = body[:anchor.start()] + line + body[anchor.start():]
            else:
                new_body = body.rstrip() + line + '\n\t'
        out.append(text[pos:start])
        out.append(new_body)
        pos = block_end
        changed += 1
    out.append(text[pos:])

    if changed:
        with open(FOCUS_FILE, 'w', encoding='utf-8') as fh:
            fh.write(''.join(out))
    return changed


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--write-tsv', action='store_true')
    ap.add_argument('--apply', action='store_true')
    ap.add_argument('--check', action='store_true')
    ap.add_argument('--quiet', action='store_true')
    args = ap.parse_args()

    with open(FOCUS_FILE, encoding='utf-8-sig') as fh:
        text = fh.read()
    focuses = parse_focuses(text)
    mapping, unmapped = build_mapping(focuses)

    if unmapped:
        for icon in sorted(unmapped):
            print('ERROR unmapped focus icon %s (focuses: %s) -- add it to '
                  'ICON_EXACT in tools/assign_focus_filters.py'
                  % (icon, ', '.join(unmapped[icon][:4])))
        # Refuse to write a half-guessed table / tree.
        return 1

    if args.write_tsv:
        write_tsv(mapping)
        if not args.quiet:
            print('wrote %s (%d focuses)' % (os.path.relpath(TSV_FILE, ROOT), len(mapping)))

    if args.apply:
        n = apply_to_tree(mapping)
        if not args.quiet:
            print('search_filters updated on %d focus(es)' % n)

    if args.check:
        tsv = load_tsv(TSV_FILE)
        problems = []
        for fid, _icon, body in focuses:
            in_tree = re.search(r'^\s*search_filters = \{([^\n]*)\}', body, re.M)
            actual = in_tree.group(1).split() if in_tree else []
            want = mapping.get(fid, [])
            if not actual:
                problems.append('%s: no search_filters in the focus tree' % fid)
            elif sorted(actual) != sorted(tsv.get(fid, [])):
                problems.append('%s: tree %s != tsv %s'
                                % (fid, actual, tsv.get(fid, [])))
            for tok in actual:
                if tok not in VALID_FILTERS:
                    problems.append('%s: non-generic filter token %s' % (fid, tok))
        if problems:
            for p in problems:
                print('ERROR ' + p)
            return 1
        if not args.quiet:
            print('OK: %d focuses carry generic search_filters matching %s'
                  % (len(focuses), os.path.relpath(TSV_FILE, ROOT)))
    return 0


if __name__ == '__main__':
    sys.exit(main())
