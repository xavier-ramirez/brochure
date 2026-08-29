# -*- coding: utf-8 -*-
"""Baja Barlow y Barlow Condensed de Google Fonts a fonts/ para que las laminas
se vean igual sin internet y el PDF exporte siempre con la misma tipografia."""
import os, re, urllib.request

BASE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(BASE, 'fonts')
os.makedirs(OUT, exist_ok=True)

CSS = ('https://fonts.googleapis.com/css2'
       '?family=Barlow:wght@300;400;500;600'
       '&family=Barlow+Condensed:wght@600;700&display=swap')
# user-agent moderno -> Google devuelve woff2
UA = ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
      '(KHTML, like Gecko) Chrome/120.0 Safari/537.36')

req = urllib.request.Request(CSS, headers={'User-Agent': UA})
css = urllib.request.urlopen(req, timeout=30).read().decode('utf-8')

# nos quedamos solo con los bloques latin / latin-ext
bloques = re.findall(r'/\*\s*([\w-]+)\s*\*/\s*(@font-face\s*\{.*?\})', css, re.S)
locales = []
for subset, bloque in bloques:
    if subset not in ('latin', 'latin-ext'):
        continue
    fam = re.search(r"font-family:\s*'([^']+)'", bloque).group(1)
    peso = re.search(r'font-weight:\s*(\d+)', bloque).group(1)
    url = re.search(r'url\((https://[^)]+\.woff2)\)', bloque).group(1)
    nombre = '%s-%s-%s.woff2' % (fam.replace(' ', ''), peso, subset)
    destino = os.path.join(OUT, nombre)
    if not os.path.exists(destino):
        with urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': UA}),
                                    timeout=60) as r, open(destino, 'wb') as f:
            f.write(r.read())
    rango = re.search(r'unicode-range:\s*([^;]+);', bloque)
    locales.append("@font-face{font-family:'%s';font-style:normal;font-weight:%s;"
                   "font-display:block;src:url('fonts/%s') format('woff2');%s}"
                   % (fam, peso, nombre, ('unicode-range:%s;' % rango.group(1)) if rango else ''))

with open(os.path.join(BASE, 'fuentes.css'), 'w', encoding='utf-8') as f:
    f.write('\n'.join(locales) + '\n')

print(len(locales), 'font-face ->', OUT)
