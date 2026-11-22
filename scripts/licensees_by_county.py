"""Tally FCC amateur licensees per Arkansas county from a ULS-style CSV.
Usage: python -I scripts/licensees_by_county.py licensees.csv path/to/zipcodes_lookup.json
Only county totals are written (data/licensees_by_county.json); no names or addresses are kept.
ZIP -> county: ZIP centre point tested against the county polygons in data/geo.json."""
import csv, json, sys, collections
src, zipjson = sys.argv[1], sys.argv[2]
geo = json.load(open('data/geo.json'))
zips = json.load(open(zipjson))            # {zip: [lat, lon]}
counties = [(c['n'], c['r']) for c in geo['counties'] if c['f'].startswith('05')]
def inring(x, y, ring):
    ins = False; j = len(ring) - 1
    for i in range(len(ring)):
        xi, yi = ring[i]; xj, yj = ring[j]
        if (yi > y) != (yj > y) and x < (xj - xi) * (y - yi) / (yj - yi) + xi: ins = not ins
        j = i
    return ins
def county_of(lat, lon):
    for n, rings in counties:
        if any(inring(lon, lat, r) for r in rings): return n
    return None
cache = {}
tot = collections.Counter(); byclass = collections.defaultdict(collections.Counter)
nozip = 0; n = 0
for row in csv.DictReader(open(src, encoding='utf-8', errors='replace')):
    n += 1; z = row['ZIP'].strip()[:5]
    if z not in cache: cache[z] = county_of(*zips[z]) if z in zips else None
    c = cache[z]
    if c is None: nozip += 1; continue
    tot[c] += 1; byclass[c][row['Operator Class'] or '?'] += 1
out = {'total': n, 'placed': sum(tot.values()), 'unplaced': nozip, 'counties': {c: tot.get(c, 0) for c, _ in counties},
       'byClass': {c: dict(v) for c, v in byclass.items()}}
json.dump(out, open('data/licensees_by_county.json', 'w'), indent=1, sort_keys=True)
print(n, out['placed'], nozip, len(counties))
