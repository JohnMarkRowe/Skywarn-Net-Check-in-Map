"""Clip the official NWS County Warning Area shapefile to the map area -> data/cwa.json
Usage: python scripts/build_cwa.py path/to/w_DDmmyy.shp   (pip install pyshp shapely)"""
import json, sys, shapefile
from shapely.geometry import shape, box
r = shapefile.Reader(sys.argv[1])
view = box(-94.9-3, 32.7-3, -89.4+3, 36.8+3)   # clip box well outside the visible frame so its edges never show
LABELBOX = {'MEG': box(-90.3, 33.8, -89.4, 35.0)}
out = []
for sr in r.shapeRecords():
    g = shape(sr.shape.__geo_interface__)
    if not g.intersects(view): continue
    c = g.intersection(view).simplify(0.004, preserve_topology=True)
    polys = [c] if c.geom_type == 'Polygon' else [p for p in getattr(c, 'geoms', []) if p.geom_type == 'Polygon']
    rings = [[[round(x, 3), round(y, 3)] for x, y in p.exterior.coords] for p in polys]
    wfo = sr.record['WFO']
    inner = g.intersection(LABELBOX.get(wfo, box(-94.9, 32.7, -89.4, 36.8)))
    lp = inner.representative_point() if not inner.is_empty else None
    out.append({'id': wfo, 'r': rings, 'lx': round(lp.x, 3) if lp else None, 'ly': round(lp.y, 3) if lp else None})
json.dump(out, open('data/cwa.json', 'w'))
