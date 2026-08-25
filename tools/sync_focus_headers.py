#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GLP: keep the branch banner comments in common/national_focus/GLP_focus.txt
honest.

The tree is organised into 27 documented branches, each introduced by

        # =============================================================
        # 7. ЧЕРНОМОРСКИЙ ФЛОТ И МОРСКАЯ МОЩЬ (10 фокусов, x = 2..6, y = 6..10)
        # =============================================================

Those numbers had drifted: the banners claimed 233 focuses in total while the
tree holds 190, and 21 of the 27 counts (plus several x/y ranges) were wrong.
A designer reading the header would plan against a tree that does not exist.

This tool recomputes every banner from the file itself:
  * a branch owns every `focus = { ... }` block between its banner and the next
    banner (source order -- the authoritative grouping, not a guessed x/y box);
  * the count and the x/y envelope are then written back verbatim.

USAGE
    tools/sync_focus_headers.py --check    # exit 1 if any banner is stale
    tools/sync_focus_headers.py --apply    # rewrite the banners (idempotent)
"""
import argparse
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FOCUS_FILE = os.path.join(ROOT, 'common', 'national_focus', 'GLP_focus.txt')

BANNER = re.compile(
    r'^(?P<indent>\t)# (?P<n>\d+)(?P<suffix>[a-z]?)\. (?P<name>.+?) '
    r'\((?P<rest>[^)]*)\)\s*$')


def plural_ru(n):
    """Russian plural for «фокус»."""
    if 11 <= n % 100 <= 14:
        return 'фокусов'
    return {1: 'фокус', 2: 'фокуса', 3: 'фокуса', 4: 'фокуса'}.get(n % 10, 'фокусов')


def parse(text):
    """Return [(line_index, banner_match, [focus_id, ...]), ...]."""
    lines = text.split('\n')
    branches = []
    cur = None
    pending = False
    for i, ln in enumerate(lines):
        m = BANNER.match(ln)
        if m:
            cur = {'i': i, 'm': m, 'focuses': []}
            branches.append(cur)
            continue
        if ln.startswith('\tfocus = {'):
            if cur is not None:
                cur['focuses'].append(None)
                pending = True
            continue
        if pending and cur is not None:
            mid = re.match(r'^\t\tid = (\S+)', ln)
            if mid:
                cur['focuses'][-1] = mid.group(1)
                pending = False
    return lines, branches


def coords_of(text):
    out = {}
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
        x = re.search(r'^\s*x\s*=\s*(-?\d+)', body, re.M)
        y = re.search(r'^\s*y\s*=\s*(-?\d+)', body, re.M)
        if fid and x and y:
            out[fid.group(1)] = (int(x.group(1)), int(y.group(1)))
    return out


def desired_banner(branch, coords):
    m = branch['m']
    n = len(branch['focuses'])
    xs = [coords[f][0] for f in branch['focuses'] if f in coords]
    ys = [coords[f][1] for f in branch['focuses'] if f in coords]
    if xs and ys:
        rng = 'x = %d..%d, y = %d..%d' % (min(xs), max(xs), min(ys), max(ys))
    else:
        rng = m.group('rest')
    return '%s# %s%s. %s (%d %s, %s)' % (m.group('indent'), m.group('n'),
                                         m.group('suffix'), m.group('name'),
                                         n, plural_ru(n), rng)


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--check', action='store_true')
    ap.add_argument('--apply', action='store_true')
    args = ap.parse_args()

    with open(FOCUS_FILE, encoding='utf-8-sig') as fh:
        text = fh.read()
    lines, branches = parse(text)
    coords = coords_of(text)

    if not branches:
        print('ERROR no branch banners found in %s' % FOCUS_FILE)
        return 1

    stale = []
    for br in branches:
        want = desired_banner(br, coords)
        have = lines[br['i']]
        if want != have:
            # Keep the exact replacement text (leading tab included); only the
            # console report is stripped.
            stale.append((br['i'], have, want))

    if args.apply and stale:
        for i, _have, want in stale:
            lines[i] = want
        with open(FOCUS_FILE, 'w', encoding='utf-8') as fh:
            fh.write('\n'.join(lines))
        # Guard against a rewrite that stops matching BANNER (e.g. one that
        # drops the leading tab) -- that would silently orphan the branch.
        for i, _have, want in stale:
            if not BANNER.match(want):
                print('ERROR rewritten banner no longer parses: %r' % want)
                return 1

    for i, have, want in stale:
        print('stale banner line %d:\n  was: %s\n  now: %s'
              % (i + 1, have.strip(), want.strip()))

    total = sum(len(br['focuses']) for br in branches)
    nfocus = text.count('\n\tfocus = {')
    if total != nfocus:
        print('ERROR branches account for %d focuses but the tree holds %d -- '
              'some focus blocks sit outside every banner' % (total, nfocus))
        return 1
    print('OK: %d branches, %d focuses, %d banner(s) rewritten'
          % (len(branches), total, len(stale) if args.apply else 0))
    return 1 if (stale and not args.apply) else 0


if __name__ == '__main__':
    sys.exit(main())
