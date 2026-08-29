# -*- coding: utf-8 -*-
"""Revisa que nada se salga de la lamina y captura un PNG de cada una.

    python revisar.py            -> revision/lamina_NN.png + informe de desbordes
"""
import os, re, subprocess

BASE = os.path.dirname(os.path.abspath(__file__))
D = BASE.replace(chr(92), '/')
OUT = os.path.join(BASE, 'revision')
os.makedirs(OUT, exist_ok=True)
CHROME = os.path.join('C:' + chr(92) + 'Program Files', 'Google', 'Chrome', 'Application', 'chrome.exe')

SONDA = (
 '<scr' + 'ipt>addEventListener("load",function(){'
 'var out=[];'
 'document.querySelectorAll(".lamina").forEach(function(l,n){'
 ' var lb=l.getBoundingClientRect();'
 ' l.querySelectorAll("*").forEach(function(e){'
 '  var r=e.getBoundingClientRect();'
 '  if(r.width<1||r.height<1)return;'
 '  var d=Math.round(Math.max(r.bottom-lb.bottom,0)),'
 '      a=Math.round(Math.max(lb.top-r.top,0)),'
 '      x=Math.round(Math.max(r.right-lb.right,0));'
 '  if(d>1||(x>1&&!e.closest(".tira,.banda,.rieles-portada,.fotos-top,.pt-der,.cr-der")))'
 '   out.push("L"+(n+1)+" "+e.tagName+"."+(typeof e.className==="string"?e.className.split(" ")[0]:"")'
 '    +" abajo:"+d+" derecha:"+x);'
 ' });'
 '});'
 'document.querySelectorAll(".desc,.pilar p,.srv li,.gerencias li,.ct p,.entrada,.fl-cab p,.fl-familias li,.fl-familias,.cartera article").forEach(function(e){'
 ' if(e.scrollHeight>e.clientHeight+2)'
 '  out.push("TEXTO CORTADO en "+(e.closest(".lamina")?"L"+([].indexOf.call(document.querySelectorAll(".lamina"),e.closest(".lamina"))+1):"?")'
 '   +" -> "+e.textContent.slice(0,40));'
 '});'
 'document.title="CHK|"+(out.length?out.slice(0,40).join(" || "):"sin desbordes");'
 '});</scr' + 'ipt>')

fuente = open(os.path.join(BASE, 'index.html'), encoding='utf-8').read()
open(os.path.join(BASE, '_revision.html'), 'w', encoding='utf-8').write(
    fuente.replace('</body>',
        '<style>.lamina{opacity:1!important;transform:none!important}.lamina.prueba,.rotulo-prueba{display:none!important}</style>'
        + SONDA + '</body>'))

r = subprocess.run([CHROME, '--headless=new', '--disable-gpu', '--virtual-time-budget=9000',
                    '--window-size=1280,720', '--dump-dom', 'file:///' + D + '/_revision.html'],
                   capture_output=True, text=True, encoding='utf-8', errors='replace')
m = re.search(r'<title>(.*?)</title>', r.stdout or '', re.S)
informe = m.group(1) if m else 'no se pudo medir'
print('--- desbordes ---')
for linea in informe.replace('CHK|', '').split(' || '):
    print(' ', linea)

# una captura por lamina, desplazando el body
N = fuente.count('class="lamina') - fuente.count('prueba pr-')
for i in range(N):
    destino = OUT + '/lamina_%02d.png' % (i + 1)
    if os.path.exists(destino):
        os.remove(destino)
    marco = fuente.replace('</body>',
        '<style>body{margin-top:-%dpx}.lamina{margin-bottom:24px;'
        'opacity:1!important;transform:none!important}#ed-barra{display:none!important}'
        '.lamina.prueba,.rotulo-prueba{display:none!important}</style></body>' % (i * 744))
    tmp = os.path.join(BASE, '_shot.html')
    open(tmp, 'w', encoding='utf-8').write(marco)
    subprocess.run([CHROME, '--headless=new', '--disable-gpu', '--hide-scrollbars',
                    '--virtual-time-budget=7000', '--window-size=1280,720',
                    '--screenshot=' + destino.replace(chr(92), '/'),
                    'file:///' + D + '/_shot.html'], capture_output=True)
print('capturas ->', OUT)
for f in ('_revision.html', '_shot.html'):
    p = os.path.join(BASE, f)
    if os.path.exists(p):
        os.remove(p)
