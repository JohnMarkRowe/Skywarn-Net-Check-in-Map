"""Export the town-coordinate table from resolve_locations.py to data/places.json (used by the page to place uploaded reports)."""
import ast, json, re
src = open('scripts/resolve_locations.py').read()
places = ast.literal_eval(re.search(r'PLACES = (\{.*?\n\})', src, re.S).group(1))
county = ast.literal_eval(re.search(r'COUNTY_LEVEL = (\{.*?\})', src).group(1))
gaz = json.load(open('data/ar_cities.json'))
merged = {**gaz, **places}          # hand-checked entries win
json.dump({'places': merged, 'countyLevel': sorted(county)}, open('data/places.json', 'w'))
print(len(places), 'hand-checked +', len(merged) - len(places), 'gazetteer =', len(merged))
