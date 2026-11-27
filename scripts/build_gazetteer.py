"""Statewide Arkansas place list: city -> average of its ZIP-code centre points (data/ar_zip_cities.json,
[zip, city, lat, lon]).  Approximate (a few miles), but covers every post-office town.
The hand-checked table in resolve_locations.py always wins over these.   Writes data/ar_cities.json."""
import json, collections
agg = collections.defaultdict(list)
for z, city, lat, lon in json.load(open('data/ar_zip_cities.json')):
    agg[city.lower().strip()].append((lat, lon))
out = {c: [round(sum(a for a, _ in v) / len(v), 4), round(sum(b for _, b in v) / len(v), 4)] for c, v in agg.items()}
json.dump(out, open('data/ar_cities.json', 'w'), sort_keys=True)
print(len(out), 'cities')
