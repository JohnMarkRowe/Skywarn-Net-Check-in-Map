"""Arkansas highways with mile values -> data/highways.json
Source: TravelMapping/HighwayData (open data), folders hwy_data/AR/{usai,usaus,usaar}.
Usage: python -I scripts/build_highways.py path/to/HighwayData/hwy_data/AR
Each route: {id, cls: 'I'|'US'|'AR', ex: true|false, p: [[lon, lat, mile], ...]}
 - Interstates: mile = exit-number anchored (exit numbers follow mileage in Arkansas), interpolated between exits. ex=true.
 - US / state routes: mile = distance along the route from its first point (approximate). ex=false.
Business routes, spurs and loops with letter suffixes are skipped."""
import sys, re, json, math, os
base = sys.argv[1]
def hav(a, b):
    R = 3958.8; la1, lo1, la2, lo2 = map(math.radians, (a[1], a[0], b[1], b[0]))
    h = math.sin((la2-la1)/2)**2 + math.cos(la1)*math.cos(la2)*math.sin((lo2-lo1)/2)**2
    return 2*R*math.asin(math.sqrt(h))
def read(path):
    out = []
    for line in open(path):
        t = line.split()
        if len(t) < 2: continue
        m = re.search(r'lat=(-?[\d.]+)&lon=(-?[\d.]+)', t[-1])
        if m: out.append((t[0], (float(m.group(2)), float(m.group(1)))))
    return out
def build(folder, pat, cls, fmt):
    routes = []
    for fn in sorted(os.listdir(os.path.join(base, folder))):
        m = re.fullmatch(pat, fn)
        if not m: continue
        wps = read(os.path.join(base, folder, fn)); 
        if len(wps) < 2: continue
        coords = [c for _, c in wps]
        dist = [0.0]
        for i in range(1, len(coords)): dist.append(dist[-1] + hav(coords[i-1], coords[i]))
        miles, exact = dist[:], False
        if cls == 'I':
            anch = []
            for i, (lab, _) in enumerate(wps):
                if i == 0 and not re.match(r'\d', lab): anch.append((i, 0.0)); continue
                mm = re.fullmatch(r'(\d{1,3})[A-Za-z]?', lab)
                if mm: anch.append((i, float(mm.group(1))))
            vals = [v for _, v in anch]
            if len(anch) >= 3 and all(b >= a for a, b in zip(vals, vals[1:])):
                exact = True; miles = []
                for i in range(len(wps)):
                    lo = max((a for a in anch if a[0] <= i), key=lambda a: a[0], default=None)
                    hi = min((a for a in anch if a[0] >= i), key=lambda a: a[0], default=None)
                    if lo and hi and lo[0] != hi[0]:
                        f = (dist[i]-dist[lo[0]]) / max(1e-9, dist[hi[0]]-dist[lo[0]]); miles.append(lo[1] + f*(hi[1]-lo[1]))
                    elif lo and lo[0] == i: miles.append(lo[1])
                    elif lo: miles.append(lo[1] + dist[i]-dist[lo[0]])
                    else: miles.append(hi[1] - (dist[hi[0]]-dist[i]))
        num = int(m.group(1))
        routes.append({'id': fmt(num), 'cls': cls, 'ex': exact,
                       'p': [[round(c[0], 4), round(c[1], 4), round(mi, 2)] for c, mi in zip(coords, miles)]})
    return routes
R = build('usai', r'ar\.i(\d{3})\.wpt', 'I', lambda n: 'I-%d' % n) \
  + build('usaus', r'ar\.us(\d{3})\.wpt', 'US', lambda n: 'US %d' % n) \
  + build('usaar', r'ar\.ar(\d{3})\.wpt', 'AR', lambda n: 'AR %d' % n)
json.dump({'routes': R}, open('data/highways.json', 'w'), separators=(',', ':'))
import collections
print(collections.Counter(r['cls'] for r in R), sum(len(r['p']) for r in R), os.path.getsize('data/highways.json')//1024, 'KB')
for r in R:
    if r['cls'] == 'I': print(r['id'], 'exact' if r['ex'] else 'est', r['p'][0][2], r['p'][-1][2], len(r['p']))
