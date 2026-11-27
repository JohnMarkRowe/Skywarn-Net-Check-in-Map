import csv, glob, json, re, sys

src = sys.argv[1]  # path to a Ham.Live end-of-net report CSV

# Approximate city-center coordinates (lat, lon). Level: city / county.
# Entries I'm not confident about are deliberately left out so they land in "needs review".
PLACES = {
 'magnolia': (33.267, -93.239), 'north little rock': (34.770, -92.267), 'little rock': (34.746, -92.290),
 'danville': (35.056, -93.394), 'conway': (35.089, -92.442),
 'conwayou': (35.089, -92.442),  # typo of Conway, fixed by hand
 'malvern': (34.363, -92.813), 'pearcy': (34.325, -93.010),
 'royal': (34.600, -93.100), 'el dorado': (33.208, -92.666),
 'waldo': (33.355, -93.293), 'cotter': (36.270, -92.542),
 'hot springs': (34.504, -93.055), 'flippin': (36.286, -92.593),
 'gassville': (36.288, -92.499), 'mountain home': (36.335, -92.386),
 'paragould': (36.058, -90.497), 'caddo gap': (34.380, -93.600),
 'morrilton': (35.150, -92.744), 'russellville': (35.278, -93.134),
 'west memphis': (35.147, -90.185), 'memphis': (35.150, -90.049),
 'brookland': (35.908, -90.556), 'forrest city': (35.008, -90.790),
 'benton': (34.565, -92.587), 'bryant': (34.596, -92.489),
 'pine bluff': (34.228, -92.003), 'sherwood': (34.815, -92.224),
 'jonesboro': (35.842, -90.704), 'beebe': (35.071, -91.879),
 'cabot': (34.975, -92.017), 'batesville': (35.770, -91.641),
 'southside': (35.730, -91.720), 'melbourne': (36.059, -91.908),
 'desha': (35.624, -91.630), 'searcy': (35.251, -91.736),
 'des arc': (34.976, -91.496), 'clinton': (35.592, -92.461),
 'walnut ridge': (36.069, -90.953), 'paris': (33.661, -95.556),
 'cleveland': (34.597, -83.763), 'alma': (35.478, -94.222),
 'dover': (35.398, -93.114), 'elkins': (35.995, -94.000),
 'monticello': (33.629, -91.791),
 'red oak': (34.580, -93.150),  # only "Garland County" was given: county-level, approximate
}
COUNTY_LEVEL = {'red oak'}
# statewide fallback (ZIP-centre average per city); the hand-checked table above always wins
import json as _json
PLACES = {**_json.load(open('data/ar_cities.json')), **PLACES}

def clean(loc):
    s = loc.lower().strip().split(' - ')[0]
    s = re.sub(r'\b(baxter|columbia|yell|garland) county\b', '', s)
    s = s.replace('- co', '').replace('-', ' ')
    s = re.sub(r'\barkansas\b', '', s)
    s = re.sub(r'[, ]+(ar|tn|tx|ga)\b\.?', '', s)
    s = re.sub(r'[,.]', ' ', s)
    s = re.sub(r'\s+', ' ', s).strip()
    # "Magnolia  Columbia Co" -> "magnolia"; "Baxter County-Cotter" -> "cotter"
    return s

OVERRIDE = {'magnolia columbia': 'magnolia', 'danville yell': 'danville'}

rows = list(csv.DictReader(open(src, newline='')))
pts, review = [], []
for r in rows:
    key = clean(r['Location'])
    key = OVERRIDE.get(key, key)
    # "Red Oak, Garland County" -> clean strips county word, leaves "red oak"
    if key in PLACES:
        lat, lon = PLACES[key]
        pts.append({'c': r['Callsign'], 'loc': r['Location'].strip(), 'lat': lat, 'lon': lon,
                    't': r['Check-In Date'], 'lvl': 'county' if key in COUNTY_LEVEL else 'city',
                    'role': r['Role']})
    else:
        review.append({'c': r['Callsign'], 'loc': r['Location'].strip(), 't': r['Check-In Date']})
pts.sort(key=lambda p: p['t'])
review.sort(key=lambda p: p['t'])
json.dump({'pts': pts, 'review': review, 'net': rows[0]['Net'], 'netId': rows[0]['Net ID']},
          open('data/sample_net.json', 'w'))
print(len(rows), 'rows,', len(pts), 'plotted,', len(review), 'need review')
print('REVIEW:', [(x['c'], x['loc']) for x in review])
