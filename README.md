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

- **Live feed.** It still needs to be confirmed how a running Ham.Live net exposes its check-ins. The end-of-net CSV report is only available after the net closes.
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
