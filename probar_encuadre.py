# -*- coding: utf-8 -*-
"""Prueba de ida y vuelta del encuadre: guarda valores extremos, recarga la
pagina en el navegador y comprueba que el editor lee EXACTAMENTE lo guardado."""
import io, json, os, re, subprocess, urllib.request

BASE = os.path.dirname(os.path.abspath(__file__))
D = BASE.replace(chr(92), '/')
CHROME = os.path.join('C:' + chr(92) + 'Program Files', 'Google', 'Chrome', 'Application', 'chrome.exe')

CASOS = {
    'macolla15_2': {'x': 0, 'y': 0, 'zoom': 1},          # pegado a la esquina
    'macolla15_3': {'x': 100, 'y': 100, 'zoom': 2.5},    # esquina opuesta con zoom
    'chuto_2':     {'x': 0, 'y': 63.7, 'zoom': 1.8},     # borde izquierdo
}
previo = json.load(io.open(os.path.join(BASE, 'encuadre.json'), encoding='utf-8'))
respaldo = {k: previo.get(k) for k in CASOS}

req = urllib.request.Request('http://localhost:8787/api/encuadre',
                             data=json.dumps(CASOS).encode('utf-8'),
                             headers={'Content-Type': 'application/json'}, method='POST')
print('guardado ->', urllib.request.urlopen(req, timeout=15).read().decode())

sonda = ('<scr' + 'ipt>addEventListener("load",function(){setTimeout(function(){'
         'document.title="R|"+JSON.stringify(window.__encuadre||{});},400);});</scr' + 'ipt>')
h = io.open(os.path.join(BASE, 'index.html'), encoding='utf-8').read()
h = h.replace('<script src="editor.js" defer></script>',
              '<script src="editor.js" defer></script>' + sonda)
io.open(os.path.join(BASE, '_pe.html'), 'w', encoding='utf-8').write(h)

r = subprocess.run([CHROME, '--headless=new', '--disable-gpu', '--virtual-time-budget=9000',
                    '--window-size=1280,13000', '--dump-dom',
                    'http://localhost:8787/_pe.html'],
                   capture_output=True, text=True, encoding='utf-8', errors='replace')
m = re.search(r'<title>R\|(.*?)</title>', r.stdout or '', re.S)
leido = json.loads(m.group(1)) if m else {}

print('\n%-14s %-22s %-22s %s' % ('foto', 'guardado', 'leido al recargar', ''))
bien = True
for n, esperado in CASOS.items():
    real = leido.get(n)
    ok = real and all(abs(real[k] - esperado[k]) < 0.15 for k in ('x', 'y', 'zoom'))
    bien = bien and ok
    print('%-14s %-22s %-22s %s'
          % (n, '%g/%g z%g' % (esperado['x'], esperado['y'], esperado['zoom']),
             ('%g/%g z%g' % (real['x'], real['y'], real['zoom'])) if real else 'NO LEIDO',
             'ok' if ok else '<-- SE PERDIO'))
print('\nRESULTADO:', 'el encuadre se conserva' if bien else 'HAY PERDIDA')

# devolver los valores que tenian
vuelta = {k: (v if v else {'x': 50, 'y': 50, 'zoom': 1}) for k, v in respaldo.items()}
urllib.request.urlopen(urllib.request.Request(
    'http://localhost:8787/api/encuadre', data=json.dumps(vuelta).encode('utf-8'),
    headers={'Content-Type': 'application/json'}, method='POST'), timeout=15).read()
os.remove(os.path.join(BASE, '_pe.html'))
print('valores restaurados')
