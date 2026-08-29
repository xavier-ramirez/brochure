# -*- coding: utf-8 -*-
"""Genera index.html con el diseno de la pagina, cortado en laminas panoramicas
16:9 (1280 x 720 px = 13,333 x 7,5 pulg, igual que PowerPoint).
Cada lamina es una pagina del PDF.

    python generar.py         -> index.html
    python servidor.py        -> http://localhost:8787   (para cambiar fotos)
    python exportar_pdf.py    -> Brochure_Vidalsa27.pdf
"""
import datetime
import io, json, os
from contenido import (EMPRESA, CONTACTO, PILARES, SERVICIOS, GERENCIAS, CARTERA,
                       AREAS, PROYECTOS, FLOTA, PORTAFOLIO)

MESES = ('enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio',
         'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre')

BASE = os.path.dirname(os.path.abspath(__file__))

# Comparativa de degradados debajo de la portada. Ponlo en False cuando decidas
# cual te gusta. NO sale en el PDF ni cuenta como lamina: es solo para mirar.
PRUEBA_PORTADA = False
PRUEBAS = [
    ('pr-b', 'B — desvanecido recto en el borde izquierdo de la foto'),
    ('pr-c', 'C — desvanecido siguiendo la diagonal del corte'),
    ('pr-d', 'D — velo claro encima, el corte se mantiene'),
]


def fecha_portafolio():
    if PORTAFOLIO.get('fecha'):
        return PORTAFOLIO['fecha']
    hoy = datetime.date.today()
    return '%d de %s de %d' % (hoy.day, MESES[hoy.month - 1], hoy.year)


def miles(n):
    return '{:,}'.format(int(n)).replace(',', '.')


def datos_flota():
    """Cifras de equipos, generadas por preparar_flota.py desde el sistema."""
    ruta = os.path.join(BASE, 'flota.json')
    if not os.path.exists(ruta):
        raise SystemExit('Falta flota.json: corre primero  python preparar_flota.py')
    return json.load(io.open(ruta, encoding='utf-8'))

AREA_NOMBRE = dict(AREAS)


# ---------------------------------------------------------------- piezas ---
def espaciada(txt):
    return txt.upper()


def foto(nombre, alt='', ext='jpg'):
    """<img> editable: data-foto lo enlaza con el editor y con encuadre.css"""
    return '<img src="img/%s.%s" data-foto="%s" alt="%s">' % (nombre, ext, nombre, alt)


def epigrafe(txt, clase=''):
    return '<div class="epigrafe %s">%s</div>' % (clase, espaciada(txt))


def chip(txt):
    return '<span class="chip"><b>%s</b></span>' % espaciada(txt)


def pildora(estado):
    clase = 'marcha' if estado.lower().startswith('en ') else 'lista'
    return '<span class="estado %s"><b>%s</b></span>' % (clase, espaciada(estado))


def rieles(clase):
    return ('<div class="%s"><i style="left:0;width:9px;background:#4966AD"></i>'
            '<i style="left:24px;width:5px;background:rgba(124,139,186,.5)"></i></div>' % clase)


def banda(nombre, epi, titulo, alto, pie=''):
    return '''<div class="banda" style="height:%dpx">
    %s
    <span class="velo"></span>
    %s
    <div class="banda-txt">%s<h2>%s</h2></div>
    %s
  </div>''' % (alto, foto(nombre), rieles('rieles-banda'), epigrafe(epi, 'claro'),
               titulo, pie)


# --------------------------------------------------------------- laminas ---
def lamina_portada():
    tag = '<i>·</i>'.join('<span>%s</span>' % espaciada(t) for t in EMPRESA['tagline_portada'])
    return '''<section class="lamina l-portada">
  <div class="pt-izq">
    <span class="cuna-ice"></span><span class="esquina-navy"></span>
    <div class="pt-cuerpo">
      <img class="logo" src="img/logo.png" alt="Constructora Vidalsa 27, C.A.">
      <div class="linea"></div>
      <div class="tagline">%s</div>
      <h1>%s</h1>
      <div class="guion"></div>
      <p class="entrada">%s</p>
      <div class="barras"><i></i><i></i><i></i><i></i></div>
    </div>
  </div>
  <div class="pt-der">
    <div class="rieles-portada"><i style="left:0;width:5px;background:#C3CAD9"></i><i style="left:18px;width:9px;background:#2A3C78"></i><i style="left:40px;width:4px;background:#8FA0CB"></i></div>
    <figure class="pt-f1">%s</figure>
    <figure class="pt-f2">%s</figure>
  </div>
</section>''' % (tag, EMPRESA['titular_portada'], EMPRESA['entrada_portada'],
                 foto('portada_valvulas'), foto('portada_bombeo'))


def lamina_nosotros():
    cols = ''.join(
        '<article class="pilar"><div class="pilar-cab"><span class="num"><b>%s</b></span>'
        '<h3>%s</h3></div><p>%s</p></article>' % (n, espaciada(t), p)
        for n, t, p in PILARES)
    return '''<section class="lamina l-nosotros">
  %s
  <div class="panel" style="top:400px;height:320px">
    %s
    <div class="cols3">%s</div>
  </div>
</section>''' % (banda('flota_equipo', 'Quiénes somos', 'Misión, visión y objetivo', 400),
                 rieles('rieles-panel'), cols)


def lamina_servicios():
    cols = ''
    for n, t, items in SERVICIOS:
        li = ''.join('<li>%s</li>' % x for x in items)
        cols += ('<article class="srv"><div class="num">%s</div><h3>%s</h3>'
                 '<div class="regla"></div><ul>%s</ul></article>' % (espaciada(n), t, li))
    fotos = ''.join('<figure>%s</figure>' % foto('servicio_' + s)
                    for s in ('1_zanja', '2_tendido', '3_soldadura', '4_valvula', '5_maquinaria'))
    return '''<section class="lamina l-servicios">
  <div class="cabecera">%s<h2>Nuestros servicios</h2></div>
  <div class="panel" style="top:160px;height:280px">
    %s
    <div class="cols4">%s</div>
  </div>
  <div class="tira">%s</div>
</section>''' % (epigrafe('Qué hacemos'), rieles('rieles-panel'), cols, fotos)


def lamina_portafolio():
    cols = ''
    for clave, nombre in AREAS:
        items = [p for p in PROYECTOS if p['area'] == clave]
        li = ''.join(
            '<li><span class="nom">%s</span>'
            '<span class="pie">%s %s</span></li>' % (p['lista'], p['cliente'], pildora(p['estado']))
            for p in items)
        cols += ('<div class="pf-col"><header><h3>%s</h3><span class="cuenta">%02d</span></header>'
                 '<ol>%s</ol></div>' % (espaciada(nombre), len(items), li))
    return '''<section class="lamina l-portafolio">
  %s
  <div class="pf-cols">%s</div>
</section>''' % (banda('portafolio_oleoducto', 'Portafolio', 'Nuestros proyectos', 190,
                        '<div class="banda-fecha"><span>%s</span><b>%s</b></div>'
                        % (espaciada(PORTAFOLIO['rotulo']), fecha_portafolio())), cols)


def tarjeta(p):
    """Tarjeta de proyecto, igual que en la pagina."""
    minis = ''.join('<figure>%s</figure>' % foto('%s_%d' % (p['id'], i)) for i in (2, 3))
    return '''<article class="tarjeta">
      <div class="hero">%s<div class="marca">%s</div></div>
      <div class="insignias"><span class="anio">%s</span>%s</div>
      <h3>%s</h3>
      <div class="sub">%s</div>
      <p class="desc">%s</p>
      <div class="minis">%s</div>
      <div class="caja-cliente"><span class="rot">%s</span><b>%s</b></div>
    </article>''' % (foto(p['id'] + '_1'), chip(AREA_NOMBRE[p['area']]),
                     espaciada(p['anio']), pildora(p['estado']),
                     p['titulo'], p['sub'], p['texto'], minis,
                     espaciada('Cliente'), p['cliente'])


def lamina_proyectos(a, b):
    return ('<section class="lamina l-proyectos"><div class="rejilla">%s%s</div></section>'
            % (tarjeta(a), tarjeta(b)))


def lamina_proyecto_solo(p):
    """El proyecto impar ocupa la lamina entera: caben hasta 4 fotos.
    Basta con dejar en img/ los archivos <id>_2.jpg ... <id>_5.jpg."""
    hay = [i for i in (2, 3, 4, 5)
           if os.path.exists(os.path.join(BASE, 'img', '%s_%d.jpg' % (p['id'], i)))]
    minis = ''.join('<figure>%s</figure>' % foto('%s_%d' % (p['id'], i)) for i in hay)
    return '''<section class="lamina l-destacado">
  <div class="hero">%s<div class="marca">%s</div></div>
  <div class="cuerpo">
    <div class="izq">
      <div class="insignias"><span class="anio">%s</span>%s</div>
      <h3>%s</h3>
      <div class="sub">%s</div>
      <p class="desc">%s</p>
      <div class="caja-cliente"><span class="rot">%s</span><b>%s</b></div>
    </div>
    <div class="der">
      <div class="minis">%s</div>
    </div>
  </div>
</section>''' % (foto(p['id'] + '_1'), chip(AREA_NOMBRE[p['area']]),
                 espaciada(p['anio']), pildora(p['estado']), p['titulo'], p['sub'],
                 p['texto'], espaciada('Cliente'), p['cliente'], minis)


def lamina_flota():
    d = datos_flota()
    bloques = ''
    for b in d['bloques']:
        celdas = ''.join(
            '<li><b>%s</b><span>%s</span></li>' % (miles(t['cantidad']), t['nombre'])
            for t in b['tipos'])
        bloques += ('<section class="fl-bloque">'
                    '<header><h3>%s</h3><span class="fl-suma">%s equipos</span></header>'
                    '<ul>%s</ul></section>'
                    % (espaciada(b['titulo']), miles(b['total']), celdas))
    fotos = ''.join('<figure>%s</figure>' % foto('flota_%d' % i) for i in (1, 2, 3, 4))
    return '''<section class="lamina l-flota">
  <div class="panel" style="top:0;height:530px">
    %s
    <div class="fl-cab">
      %s
      <h2>%s</h2>
      <p>%s</p>
    </div>
    <div class="fl-total">
      <b>%s</b>
      <span>equipos propios</span>
      <div class="fl-sub"><span>%s tipos de equipo</span><span>%s marcas</span></div>
    </div>
    <div class="fl-bloques">%s</div>
  </div>
  <div class="tira tira-flota">%s</div>
</section>''' % (rieles('rieles-panel'), epigrafe(FLOTA['epigrafe'], 'claro'),
                 FLOTA['titulo'], FLOTA['texto'],
                 miles(d['total']), miles(d['tipos_distintos']), miles(d['marcas']),
                 bloques, fotos)


def lamina_clientes():
    ger = ''.join('<li>%s</li>' % g for g in GERENCIAS)
    cart = ''.join(
        '<article><img src="img/%s.png" alt="%s"><span>%s</span></article>'
        % (archivo, nombre, espaciada(sub)) for nombre, sub, archivo in CARTERA)
    return '''<section class="lamina l-clientes">
  %s
  <div class="panel" style="top:300px;height:420px">
    %s
    <div class="cl-cols">
      <div>%s<ul class="gerencias">%s</ul></div>
      <div>%s<div class="cartera">%s</div></div>
    </div>
  </div>
</section>''' % (banda('clientes_equipo', 'Clientes', 'Nuestros clientes', 300),
                 rieles('rieles-panel'),
                 epigrafe('Contratos directos con siete gerencias de la FPO', 'suave'), ger,
                 epigrafe('Toda la cartera', 'suave'), cart)


ICONOS = {
 'Sede corporativa': '<path d="M12 21s7-6.1 7-11a7 7 0 1 0-14 0c0 4.9 7 11 7 11z"/><circle cx="12" cy="10" r="2.6"/>',
 'Sede operativa':   '<path d="M12 21s7-6.1 7-11a7 7 0 1 0-14 0c0 4.9 7 11 7 11z"/><circle cx="12" cy="10" r="2.6"/>',
 'Teléfonos':        '<rect x="7" y="2.5" width="10" height="19" rx="2"/><path d="M11 18.6h2"/>',
 'Contacto':         '<rect x="3" y="5" width="18" height="14" rx="2"/><path d="M3.6 6.2 12 13l8.4-6.8"/>',
}


def lamina_cierre():
    tag = '<i>·</i>'.join('<span>%s</span>' % espaciada(t) for t in EMPRESA['tagline_cierre'])
    cols = ''.join('<div class="ct"><h4><svg viewBox="0 0 24 24">%s</svg>%s</h4><p>%s</p></div>'
                   % (ICONOS[t], espaciada(t), v) for t, v in CONTACTO)
    return '''<section class="lamina l-cierre">
  <div class="cr-izq">
    <span class="cuna-ice"></span>
    <div class="pt-cuerpo">
      <img class="logo" src="img/logo.png" alt="Constructora Vidalsa 27, C.A.">
      <div class="linea"></div>
      <div class="tagline">%s</div>
      <h2>%s</h2>
      <div class="barras"><i></i><i></i><i></i><i></i></div>
    </div>
  </div>
  <div class="cr-der">
    <div class="rieles-portada"><i style="left:0;width:5px;background:#C3CAD9"></i><i style="left:18px;width:9px;background:#2A3C78"></i><i style="left:40px;width:4px;background:#8FA0CB"></i></div>
    <figure>%s</figure>
  </div>
  <div class="pie-navy">
    %s
    <div class="contacto">%s</div>
    <div class="sello"><span>%s</span><span>%s</span></div>
  </div>
</section>''' % (tag, EMPRESA['titular_cierre'], foto('flota_equipo_cierre'),
                 rieles('rieles-panel'), cols,
                 espaciada(EMPRESA['elaborado']), espaciada(EMPRESA['sello']))


# ------------------------------------------------------------------ armado ---
def construir():
    portada = lamina_portada()
    laminas = [portada]
    if PRUEBA_PORTADA:
        laminas.append('<div class="rotulo-prueba">A — como esta ahora (arriba) · '
                       'debajo, las opciones con degradado</div>')
        for clase, rotulo in PRUEBAS:
            laminas.append('<div class="rotulo-prueba">%s</div>' % rotulo)
            laminas.append(portada.replace('class="lamina l-portada"',
                                           'class="lamina l-portada prueba %s"' % clase))
    laminas += [lamina_nosotros(), lamina_servicios(), lamina_portafolio()]
    pares = len(PROYECTOS) // 2 * 2
    for i in range(0, pares, 2):
        laminas.append(lamina_proyectos(PROYECTOS[i], PROYECTOS[i + 1]))
    if len(PROYECTOS) % 2:
        laminas.append(lamina_proyecto_solo(PROYECTOS[-1]))
    laminas.append(lamina_flota())
    laminas.append(lamina_clientes())
    laminas.append(lamina_cierre())

    css = io.open(os.path.join(BASE, 'estilos.css'), encoding='utf-8').read()
    html = ('<!doctype html>\n<html lang="es">\n<head>\n<meta charset="utf-8">\n'
            '<title>Brochure — Constructora Vidalsa 27</title>\n'
            '<link rel="stylesheet" href="fuentes.css">\n'
            '<style>\n%s</style>\n'
            '<link rel="stylesheet" href="encuadre.css">\n'
            '</head>\n<body>\n%s\n'
            '<script src="editor.js" defer></script>\n'
            '</body>\n</html>\n' % (css, '\n'.join(laminas)))
    io.open(os.path.join(BASE, 'index.html'), 'w', encoding='utf-8').write(html)
    reales = sum(1 for l in laminas if 'class="lamina' in l and 'prueba' not in l)
    print('index.html listo -> %d laminas (1280 x 720 px cada una)' % reales)
    if PRUEBA_PORTADA:
        print('   + %d clones de portada para comparar degradados '
              '(no salen en el PDF; se quitan con PRUEBA_PORTADA = False)' % len(PRUEBAS))


if __name__ == '__main__':
    construir()
