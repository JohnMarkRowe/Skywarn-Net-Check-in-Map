"""Inline the data files into the page template -> docs/index.html"""
import json
t = open('scripts/template.html').read()
t = (t.replace('__DATA__', open('data/sample_net.json').read())
      .replace('__GEO__', open('data/geo.json').read())
      .replace('__CWA__', open('data/cwa.json').read())
      .replace('__PLACES__', open('data/places.json').read())
      .replace('__HWY__', open('data/highways.json').read())
      .replace('__AUX__', json.dumps(json.load(open('data/auxcomm_by_county.json'))['counties']))
      .replace('__LIC__', json.dumps(json.load(open('data/licensees_by_county.json'))['counties'])))
open('docs/index.html', 'w').write(t)
