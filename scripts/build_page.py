"""Inline the data files into the page template -> docs/index.html"""
t = open('scripts/template.html').read()
t = (t.replace('__DATA__', open('data/sample_net.json').read())
      .replace('__GEO__', open('data/geo.json').read())
      .replace('__CWA__', open('data/cwa.json').read()))
open('docs/index.html', 'w').write(t)
