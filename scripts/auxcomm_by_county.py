"""Tally AUXCOMM-trained people per Arkansas county from the class roster (.xlsx).
Usage: python -I scripts/auxcomm_by_county.py roster.xlsx ar_zips.json
Placement: home ZIP (ZIP centre inside a county polygon); if no ZIP, the county named in the
person's organization (e.g. 'Pope Co OEM'); otherwise unplaced (state-level groups).
Only county totals are written (data/auxcomm_by_county.json); no names, contacts or addresses."""
import json, re, sys, collections, openpyxl
src, zipjson = sys.argv[1], sys.argv[2]
geo = json.load(open('data/geo.json')); zips = json.load(open(zipjson))
counties = [(c['n'], c['r']) for c in geo['counties'] if c['f'].startswith('05')]
names = {n.lower(): n for n, _ in counties}
def inring(x, y, ring):
    ins = False; j = len(ring) - 1
    for i in range(len(ring)):
        xi, yi = ring[i]; xj, yj = ring[j]
        if (yi > y) != (yj > y) and x < (xj - xi) * (y - yi) / (yj - yi) + xi: ins = not ins
        j = i
    return ins
def by_zip(z):
    if z not in zips: return None
    lat, lon = zips[z]
    for n, rs in counties:
        if any(inring(lon, lat, r) for r in rs): return n
def by_org(org):
    hits = {names[m.lower()] for m in re.findall(r'([A-Za-z ]+?)\s*(?:Co\b\.?|County)', org or '') for m in [m.strip().split()[-1]] if m.lower() in names}
    return hits.pop() if len(hits) == 1 else None
ws = openpyxl.load_workbook(src, read_only=True).active
tot = collections.Counter(); tb = collections.Counter(); dep = collections.Counter(); how = collections.Counter(); n = 0
zre = re.compile(r'\b(7[12]\d{3})\b')
for r in ws.iter_rows(min_row=2, values_only=True):
    if not (r[2] or r[4]): continue
    n += 1
    m = zre.search(str(r[6] or '')); c = by_zip(m.group(1)) if m else None
    src_ = 'zip'
    if not c: c = by_org(str(r[5] or '')); src_ = 'org'
    if not c: how['unplaced'] += 1; continue
    how[src_] += 1; tot[c] += 1; tb[c] += bool(r[0]); dep[c] += bool(r[1])
out = {'people': n, 'placed': sum(tot.values()), 'method': dict(how),
       'counties': {c: tot.get(c, 0) for c, _ in counties},
       'taskbook': {c: v for c, v in tb.items() if v}, 'deployable': {c: v for c, v in dep.items() if v}}
json.dump(out, open('data/auxcomm_by_county.json', 'w'), indent=1, sort_keys=True)
print(n, out['placed'], dict(how))
print(sorted(((v, c) for c, v in tot.items()), reverse=True)[:12])
