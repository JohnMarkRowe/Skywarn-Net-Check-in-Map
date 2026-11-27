# Skywarn Net Check-in Map

A map of amateur radio operators who check in to statewide Skywarn nets, with county outlines and NWS County Warning Area (CWA) outlines. Hovering a pin shows the callsign, town, and check-in time.

**Status: prototype.** It replays a completed net from a Ham.Live end-of-net report. Live updating is not built yet.

## What works

- **Mode toggle: Historical report or Live net.**
  - *Historical report:* replays the bundled sample net, or any Ham.Live end-of-net CSV you load from your computer (play, pause, speed, timeline). New check-ins pulse as they arrive.
  - *Live net:* accepts a Net ID or live net link and recognizes the ID, but is **not connected** to anything yet. The page exposes `addLiveCheckin({callsign, location, time})` as the single entry point a live feed will call.
- Hover a pin for callsign, town, and time.
- County outlines (US Census data via `us-atlas`), an optional county-names layer (off by default), and NWS CWA outlines (official NWS shapefile). Each layer has its own toggle.
- Locations that cannot be placed with confidence are listed under "Needs review" instead of being guessed.

## What is not built yet

- **Live feed.** Running-net check-ins are behind a login in Ham.Live. A proposed public, read-only endpoint is described in [docs/hamlive-checkin-feed-proposal.md](docs/hamlive-checkin-feed-proposal.md) and is awaiting review by the instance operator. The end-of-net CSV report is only available after the net closes.
- **Net discovery.** Each Ham.Live net has a stable Net ID, and the live page is `/views/livenet/<Net ID>`. The idea is to pick or detect the current net by ID, not by its name.
- **Geocoding.** Town coordinates in `scripts/resolve_locations.py` are approximate and entered by hand. A real build should geocode, with a manual override list.
- **Map tiles.** The prototype draws its own outline map. A deployed site would use proper tiles.

## Privacy

Pins are placed at city or county level only. The page shows callsigns, towns, and times, not names or street addresses. The raw report CSV is git-ignored because it contains names.

## Rebuild

```
node scripts/extract_counties.cjs          # needs: npm install us-atlas topojson-client
python scripts/resolve_locations.py report.csv
python scripts/build_cwa.py w_16ap26.shp   # needs: pip install pyshp shapely
python scripts/build_page.py               # writes docs/index.html
```

Open `docs/index.html` in a browser.

## Data sources

- County and state outlines: US Census Bureau, via the `us-atlas` npm package.
- County Warning Areas: National Weather Service shapefile (`w_16ap26`, valid 16 April 2026), https://www.weather.gov/gis/CWABounds

## Zoom and clustering

- Scroll wheel, pinch, the + / − buttons or double-click to zoom; drag to pan. **Fit** zooms to the check-ins, **All** shows the whole state.
- Stations close together merge into a numbered circle; hover it to list the callsigns, click to zoom in. From about 5× zoom, stations in the same town fan out so each callsign can be hovered.
- Boundary detail follows zoom: CWA lines are boldest zoomed out, county lines strengthen as you zoom in, and county names appear from 2× (if the County names box is ticked).
- Counties are Census 1:10M generalized boundaries, so edges look coarse near the 12× maximum zoom.

## County shading and participation gaps

Tick **County shading** to colour counties by check-ins per 100 licensed hams, raw check-ins, or licensed hams. A "Biggest participation gaps" list ranks counties with 50+ licensees by fewest check-ins per licensee. Licensee totals come from `data/licensees_by_county.json`, made by `scripts/licensees_by_county.py` from an FCC amateur licensee CSV (county totals only; the raw file is never committed).

## AUXCOMM-trained layer

Tick **AUXCOMM-trained** to show a square badge with the number of trained people in each county, and to add them to the shading options and the gap list. Counts come from `data/auxcomm_by_county.json`, made by `scripts/auxcomm_by_county.py` from the class roster (.xlsx, never committed). People are placed by home ZIP, or by the county in their organization name when no ZIP is listed; state-level groups are left unplaced.

## Net control: add a spotter not on Ham.Live

Open **Add a spotter not on Ham.Live** under the map. Enter a callsign and where the station is (a town, or "Pope County"). Recognized places are pinned at once with a dashed outline ("placed by net control"). If the place is not recognized, the map asks: pick a "Did you mean" suggestion, choose a known town or county, or click the spot on the map. Town or county choices are remembered in that browser. Adding the same callsign again moves the pin (for mobile stations). The same prompt is available from the **Place…** button on any "Needs review" entry. Spotters placed in Live mode are saved in that browser for 24 hours (a reload keeps them). A **Placed by net control** list has **Move…** (type a new place, or click the new spot on the map; map picks are labeled "Near <town>") and **Remove** for each. Placements made on a historical report are not saved.

Places come from a hand-checked table (`resolve_locations.py`) plus a statewide list of ~600 Arkansas post-office towns (`data/ar_cities.json`, built by `scripts/build_gazetteer.py` from ZIP centre points, accurate to a few miles).
