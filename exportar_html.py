# -*- coding: utf-8 -*-
"""Exporta la presentacion CON EFECTOS a UN SOLO archivo HTML.

    python exportar_html.py   -> Presentacion_Vidalsa27.html

Para que sirve, que es lo que ningun otro formato da:

  Los efectos del brochure -la entrada escalonada, el titulo palabra por
  palabra, la pila de fotos que gira, los reinicios de la portada y el cierre-
  estan escritos en CSS y en JavaScript. NO se pueden traducir a PowerPoint sin
  perderlos por el camino: alli no existe la entrada por desenfoque, ni las
  curvas de aceleracion a medida, y los bucles habria que escribirlos en XML a
  mano. La unica manera de que se vean EXACTAMENTE igual en otra computadora es
  entregar la cosa que los produce.

  Eso es este archivo: la pagina entera con todo dentro. Se abre con doble clic
  en cualquier PC -no hace falta instalar nada, ni internet, ni el servidor: un
  navegador lo tiene hasta la maquina mas pelada- y arranca sola en modo
  presentacion con los efectos puestos.

Que se mete dentro:

  - las dos hojas de estilo enlazadas (fuentes y encuadre); estilos.css ya va
    incrustado de fabrica, lo pone generar.py;
  - las fuentes Barlow y Barlow Condensed, en base64, para que se vean iguales
    aunque en esa computadora no esten instaladas;
  - las 85 fotos, tambien en base64;
  - encaje.js y presentacion.js.

Que se queda FUERA, y a proposito:

  - editor.js. La barra del editor no pinta nada en una presentacion suelta, y
    ademas habla con el servidor -guardar encuadres, generar el PDF- que ahi no
    existe. Sin ella el archivo abre limpio.

El peso sale de las fotos: base64 ocupa un tercio mas que el binario, asi que
17 MB de fotos son unos 24. El archivo entero ronda los 25 MB, menos que el
PowerPoint que ya se genera.
"""
import base64
import io
import mimetypes
import os
import re

BASE = os.path.dirname(os.path.abspath(__file__))
NOMBRE = 'Presentacion_Vidalsa27.html'
SALIDA = os.path.join(BASE, NOMBRE)

# La pagina de la que sale: la panoramica, que es la unica con modo
# presentacion. La hoja carta y la de pie son verticales y no llenan una
# pantalla (ver el comentario del boton en editor.js).
PAGINA = 'index.html'

# Lo que se incrusta y lo que no. editor.js queda fuera: ver la cabecera.
GUIONES = ('encaje.js', 'presentacion.js')
FUERA = ('editor.js',)


def _dato(ruta):
    """Un archivo como data: URI, con su tipo adivinado por la extension."""
    tipo, _ = mimetypes.guess_type(ruta)
    if not tipo:
        tipo = 'application/octet-stream'
    with open(ruta, 'rb') as f:
        return 'data:%s;base64,%s' % (tipo, base64.b64encode(f.read()).decode('ascii'))


def _css_con_fuentes(ruta):
    """El CSS de una hoja, con sus url(...) convertidos a data: URI.

    Hace falta para fuentes.css, que apunta a doce .woff2 en fonts/. Si se
    dejaran como rutas, el archivo suelto se abriria con las letras del sistema
    y no seria el mismo brochure."""
    carpeta = os.path.dirname(ruta)
    css = io.open(ruta, encoding='utf-8').read()

    def cambiar(m):
        rel = m.group(2)
        if rel.startswith('data:'):
            return m.group(0)
        archivo = os.path.join(carpeta, rel.replace('/', os.sep))
        if not os.path.exists(archivo):
            return m.group(0)
        return "url('%s')" % _dato(archivo)

    return re.sub(r"url\((['\"]?)([^'\")]+)\1\)", cambiar, css)


def generar():
    """Arma el archivo. Devuelve (ruta, megas) o lanza RuntimeError."""
    pagina = os.path.join(BASE, PAGINA)
    if not os.path.exists(pagina):
        raise RuntimeError('Falta %s. Ejecuta antes: python generar.py' % PAGINA)

    html = io.open(pagina, encoding='utf-8').read()

    # 1. las hojas enlazadas, dentro
    def meter_hoja(m):
        rel = m.group(1)
        ruta = os.path.join(BASE, rel.replace('/', os.sep))
        if not os.path.exists(ruta):
            return m.group(0)
        return '<style>\n%s\n</style>' % _css_con_fuentes(ruta)

    html = re.sub(r'<link rel="stylesheet" href="([^"]+)">', meter_hoja, html)

    # 2. los guiones, dentro; editor.js fuera
    def meter_guion(m):
        rel = m.group(1)
        if rel in FUERA:
            return ''
        if rel not in GUIONES:
            return m.group(0)
        ruta = os.path.join(BASE, rel.replace('/', os.sep))
        if not os.path.exists(ruta):
            return m.group(0)
        return '<script>\n%s\n</script>' % io.open(ruta, encoding='utf-8').read()

    html = re.sub(r'<script src="([^"]+)"[^>]*></script>', meter_guion, html)

    # 3. la marca que hace que arranque sola y con efectos. Va ANTES de
    #    presentacion.js, que la lee en su primera linea.
    html = html.replace('<script>\n' + io.open(
        os.path.join(BASE, 'presentacion.js'), encoding='utf-8').read() + '\n</script>',
        '<script>window.__presSuelta = true;</script>\n<script>\n' + io.open(
            os.path.join(BASE, 'presentacion.js'), encoding='utf-8').read() + '\n</script>', 1)

    # 4. las fotos, dentro
    faltan = []
    vistas = {}

    def meter_foto(m):
        rel = m.group(1)
        if rel.startswith('data:'):
            return m.group(0)
        if rel in vistas:
            return 'src="%s"' % vistas[rel]
        ruta = os.path.join(BASE, rel.replace('/', os.sep))
        if not os.path.exists(ruta):
            faltan.append(rel)
            return m.group(0)
        vistas[rel] = _dato(ruta)
        return 'src="%s"' % vistas[rel]

    html = re.sub(r'src="((?!data:)[^"]+)"', meter_foto, html)
    if faltan:
        raise RuntimeError('Faltan %d archivos: %s' % (len(faltan), ', '.join(faltan[:5])))

    io.open(SALIDA, 'w', encoding='utf-8').write(html)
    megas = os.path.getsize(SALIDA) / 1048576.0
    return SALIDA, megas


if __name__ == '__main__':
    ruta, megas = generar()
    print('%s listo -> %.1f MB' % (os.path.basename(ruta), megas))
    print('Se abre con doble clic en cualquier PC, sin instalar nada.')
