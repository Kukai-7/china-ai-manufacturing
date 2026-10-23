"""Download the raw inputs used by build.py and viz.py into raw/ (World Bank API, Our World in Data, Wikipedia, Natural Earth). No key needed."""
import json, os, requests
import lxml.html
from shapely.geometry import shape, mapping

PEERS = 'CHN;USA;DEU;JPN;KOR;WLD'
INDICATORS = ['NV.IND.MANF.CD', 'NV.IND.MANF.ZS', 'TX.VAL.TECH.CD', 'TX.VAL.TECH.MF.ZS', 'GB.XPD.RSDV.GD.ZS', 'SP.POP.SCIE.RD.P6',
              'IP.PAT.RESD', 'SP.POP.1564.TO']
NE = 'https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/'


def wb(ind):
    url = f'https://api.worldbank.org/v2/country/{PEERS}/indicator/{ind}?format=json&per_page=4000&date=1990:2026'
    rows = requests.get(url, timeout=60).json()[1] or []
    return [[r['countryiso3code'], int(r['date']), float(f"{float(r['value']):.6g}")] for r in rows if r['value'] is not None]


def wiki_table(revision):
    """Cells of the provincial table in one pinned Wikipedia revision, as text, footnote markers removed."""
    r = requests.get('https://en.wikipedia.org/w/api.php', params=dict(action='parse', oldid=revision, prop='text|revid', format='json', formatversion=2), timeout=60).json()['parse']
    doc = lxml.html.fromstring(r['text'])
    for sup in doc.xpath('//sup'): sup.drop_tree()
    t = next(t for t in doc.xpath('//table') if '2025(p)' in t.xpath('.//tr')[0].text_content())
    return {'rev': r['revid'], 'table': [[c.text_content().strip() for c in tr.xpath('./th|./td')] for tr in t.xpath('.//tr')]}


if __name__ == '__main__':
    os.makedirs('raw', exist_ok=True)
    out = {f'wb_{i}': wb(i) for i in INDICATORS}
    out['owid_robots'] = requests.get('https://ourworldindata.org/grapher/annual-industrial-robots-installed.csv?useColumnShortNames=true', timeout=60).text
    out['wiki_gdp'] = wiki_table(1358609842)        # List of Chinese administrative divisions by GDP
    out['wiki_gdppc'] = wiki_table(1373819856)      # ... by GDP per capita
    json.dump(out, open('raw/bundle.json', 'w'))
    # provinces of mainland China, simplified (the South China Sea islets feature is dropped)
    a1 = requests.get(NE + 'ne_10m_admin_1_states_provinces.geojson', timeout=300).json()
    feats = [dict(type='Feature', properties=dict(name=f['properties']['name'], name_zh=f['properties']['name_zh']),
                  geometry=mapping(shape(f['geometry']).simplify(.02, preserve_topology=True)))
             for f in a1['features'] if f['properties']['adm0_a3'] == 'CHN' and f['properties']['name'] != 'Paracel Islands']
    json.dump(dict(type='FeatureCollection', features=feats), open('raw/china_provinces.geojson', 'w'))
    open('raw/ne_50m_admin_0_countries.geojson', 'wb').write(requests.get(NE + 'ne_50m_admin_0_countries.geojson', timeout=120).content)
