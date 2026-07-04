#!/usr/bin/env python3
"""
Downloads the daily OurAirports dataset and writes a trimmed airports.min.json
containing only real, quotable airfields (a proper ICAO code, an IATA code, or
scheduled service), with each airport mapped to a Levare region bucket.

Run by the GitHub Action weekly. No dependencies beyond the Python standard library.
Source: https://github.com/davidmegginson/ourairports-data  (public domain, CC0)
"""
import csv, re, json, io, urllib.request

SRC = "https://raw.githubusercontent.com/davidmegginson/ourairports-data/main/airports.csv"
ICAO = re.compile(r'^[A-Z]{4}$')

# --- Region buckets (edit these sets to re-map countries) --------------------
UK   = {'GB','IM','JE','GG'}
US   = {'US'}
ME   = {'AE','SA','QA','KW','BH','OM','IL','JO','LB','SY','IQ','IR','YE','PS'}
APAC = {'CN','HK','MO','TW','JP','KR','KP','MN','IN','PK','BD','LK','NP','BT','MV',
        'SG','MY','TH','VN','LA','KH','MM','PH','ID','BN','TL','AU','NZ','FJ','PG',
        'NC','PF','WS','TO','VU','SB','KI','FM','MH','PW','NR','TV','CK'}
EUR  = {'AL','AD','AT','BY','BE','BA','BG','HR','CY','CZ','DK','EE','FI','FR','DE',
        'GR','HU','IS','IE','IT','XK','LV','LI','LT','LU','MT','MD','MC','ME','NL',
        'MK','NO','PL','PT','RO','RU','SM','RS','SK','SI','ES','SE','CH','UA','VA',
        'TR','GI','FO'}

def region(c):
    if c in UK:   return 'UK'
    if c in US:   return 'US'
    if c in ME:   return 'Middle East'
    if c in APAC: return 'APAC'
    if c in EUR:  return 'Europe'
    return ''   # Africa, Canada, Latin America, Caribbean, etc. -> no region (never excluded)

def main():
    raw = urllib.request.urlopen(SRC, timeout=120).read().decode('utf-8')
    out = []
    for r in csv.DictReader(io.StringIO(raw)):
        t = r['type']
        if t in ('closed', 'seaplane_base', 'balloonport'):
            continue
        keep = (t in ('large_airport', 'medium_airport')
                or ICAO.match(r['ident'] or '')
                or (r['iata_code'] or '').strip()
                or r['scheduled_service'] == 'yes')
        if not keep:
            continue
        try:
            lat = round(float(r['latitude_deg']), 4)
            lon = round(float(r['longitude_deg']), 4)
        except (ValueError, TypeError):
            continue
        out.append([r['ident'], (r['iata_code'] or '').strip(), r['name'],
                    r['municipality'] or '', lat, lon, region(r['iso_country'])])
    out.sort(key=lambda x: x[0])
    with open('airports.min.json', 'w', encoding='utf-8') as f:
        json.dump(out, f, ensure_ascii=False, separators=(',', ':'))
    print(f"Wrote airports.min.json  records={len(out)}")

if __name__ == '__main__':
    main()
