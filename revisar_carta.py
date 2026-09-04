# -*- coding: utf-8 -*-
"""Compara el PDF de carta contra el panoramico, texto por texto.

    python revisar_carta.py

La hoja carta lleva EXACTAMENTE el mismo texto que la panoramica y con la
misma letra, del mismo tamano en puntos: lo unico que cambia es la forma de la
hoja. Aqui se comprueba justo eso, que a ojo no se ve:

  1. que no falte ni sobre una sola letra en ninguna hoja. Si un texto se sale
     de su caja, Chrome lo recorta y desaparece del PDF sin avisar: esta es la
     unica forma de cazarlo en las 19 hojas de una vez.
  2. que cada letra lleve el mismo cuerpo y la misma familia en las dos. Se
     cuenta por CARACTERES y no por lineas, porque en carta -mas angosta- los
     parrafos se parten en mas lineas y eso no es un fallo, es lo que se busca.
  3. que ningun texto se meta en las franjas del encabezado y del pie, ni se
     acerque al canto del papel mas de lo que ninguna lamina se acerca.

Hace falta el PDF de las dos versiones:
    python exportar_pdf.py  &&  python exportar_pdf.py carta
"""
import collections
import io, os, re, sys

# la consola de Windows va en cp1252 y se atraganta con las comillas de pulgada
# de los titulos; asi el aviso sale con un '?' en vez de reventar el script
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(errors='replace')

try:
    import fitz
except ImportError:
    sys.exit('Falta PyMuPDF:  pip install pymupdf')

BASE = os.path.dirname(os.path.abspath(__file__))
PANO = os.path.join(BASE, 'Brochure_Vidalsa27.pdf')
CARTA = os.path.join(BASE, 'Brochure_Vidalsa27_Carta.pdf')

PPP = 96.0            # pixeles del diseno por pulgada
PT = 72.0             # puntos del PDF por pulgada


def medida(nombre, css, respaldo):
    """Lee una variable de una hoja de estilos. Las medidas de la hoja carta
    no se copian aqui: se le preguntan a quien las decide, o al cambiarlas
    alli este control se quedaria comprobando otra cosa."""
    m = re.search(r'--%s\s*:\s*([0-9.]+)px' % nombre, css)
    return float(m.group(1)) if m else respaldo


_carta = io.open(os.path.join(BASE, 'carta.css'), encoding='utf-8').read()
_estilos = io.open(os.path.join(BASE, 'estilos.css'), encoding='utf-8').read()

ANCHO = medida('ancho-lamina', _carta, 1056)      # la hoja carta
DISENO = medida('alto-diseno', _estilos, 720)     # lo que ocupa la maqueta
ENC = medida('enc', _carta, 64)                   # franja del encabezado
# El margen mas apretado que usa el diseno es el de la rejilla de proyectos.
# Nada de texto deberia acercarse al canto mas que eso.
LADO_MIN = medida('lado-rejilla', _carta, 30)
# tolerancia: el antialias y los rebases de una fraccion de pixel no se ven
HOLGURA = 2.0


def px(v):
    """puntos del PDF -> pixeles del diseno"""
    return v * PPP / PT


def piezas(ruta):
    """Cada texto de cada pagina: (pagina, texto, cuerpo, fuente, caja)."""
    doc = fitz.open(ruta)
    fuera = []
    for n, pag in enumerate(doc, 1):
        for b in pag.get_text('dict')['blocks']:
            for l in b.get('lines', []):
                for s in l['spans']:
                    t = ' '.join(s['text'].split())
                    if t:
                        fuera.append((n, t, round(s['size'], 3), s['font'],
                                      [px(v) for v in s['bbox']]))
    return doc.page_count, fuera


def por_hoja(piezas_):
    d = collections.defaultdict(list)
    for p in piezas_:
        d[p[0]].append(p)
    return d


def letras(trozos):
    """Todas las letras de la hoja, seguidas y sin espacios: asi da igual
    donde se parta cada linea."""
    return ''.join(''.join(t[1].split()) for t in trozos)


def cuerpos(trozos):
    """Cuantos caracteres hay de cada (cuerpo, familia)."""
    c = collections.Counter()
    for _, t, cuerpo, fnt, _r in trozos:
        c[(cuerpo, fnt)] += len(''.join(t.split()))
    return c


def primera_diferencia(a, b):
    for i, (x, y) in enumerate(zip(a, b)):
        if x != y:
            return i
    return min(len(a), len(b))


def main():
    for r in (PANO, CARTA):
        if not os.path.exists(r):
            sys.exit('Falta %s. Corre antes:  python exportar_pdf.py  y  '
                     'python exportar_pdf.py carta' % os.path.basename(r))

    # ---- lo primero: que los dos PDF sean de AHORA -----------------------
    # Comparar contra un PDF viejo es peor que no comparar: da por bueno algo
    # que ya no existe. Si alguna fuente es mas nueva que un PDF, se para.
    fuentes = ['generar.py', 'contenido.py', 'estilos.css', 'carta.css',
               'hoja.css', 'encuadre.css', 'fuentes.css']
    ultima = max(os.path.getmtime(os.path.join(BASE, f)) for f in fuentes
                 if os.path.exists(os.path.join(BASE, f)))
    viejos = [os.path.basename(r) for r in (PANO, CARTA)
              if os.path.getmtime(r) < ultima]
    if viejos:
        print('  !! %s no lleva los ultimos cambios.' % ' y '.join(viejos))
        print('     Vuelve a sacarlo con:  python exportar_pdf.py')
        return 1

    n_pano, p_pano = piezas(PANO)
    n_carta, todo_carta = piezas(CARTA)
    # El encabezado no lleva texto -solo el logo- pero el pie si: el numero de
    # hoja. Es de la hoja carta y solo de ella, asi que se aparta de la
    # comparacion; la parte de geometria si lo mira.
    p_carta = [x for x in todo_carta if x[4][1] < ENC + DISENO]

    print('panoramica  %2d hojas, %4d textos' % (n_pano, len(p_pano)))
    print('carta       %2d hojas, %4d textos (%d de ellos son el numero de hoja)'
          % (n_carta, len(todo_carta), len(todo_carta) - len(p_carta)))
    print()
    fallos = 0

    if n_pano != n_carta:
        print('  !! no tienen el mismo numero de hojas')
        fallos += 1

    # ---- 0: el encogido de Chrome ----------------------------------------
    # Si algo dentro de una lamina se sale de su caja, Chrome no avisa: encoge
    # el documento ENTERO para que quepa, y el PDF sale con toda la letra mas
    # pequena y el encabezado y el pie fuera de sitio. Se cazo dos veces -las
    # barras de la trama y la cuna de la portada-, asi que se mira primero:
    # si todos los cuerpos salen multiplicados por lo mismo, es esto.
    ta = sorted({p[2] for p in p_pano})
    tb = sorted({p[2] for p in p_carta})
    if ta and tb and ta != tb:
        f = tb[0] / ta[0]
        if all(abs(y / x - f) < .002 for x, y in zip(ta, tb)) and abs(f - 1) > .002:
            print('  !! EL PDF DE CARTA SALIO ENCOGIDO al %.1f %%.' % (f * 100))
            print('     No es la letra: es que algo se sale de su caja y Chrome')
            print('     achica la hoja entera para que quepa. Busca en carta.css')
            print('     la ultima regla que ensancha algo -un ancho mayor que su')
            print('     contenedor- y quitala.')
            return 1

    a, b = por_hoja(p_pano), por_hoja(p_carta)

    for hoja in sorted(set(a) | set(b)):
        ta, tb = letras(a.get(hoja, [])), letras(b.get(hoja, []))
        if ta != tb:
            i = primera_diferencia(ta, tb)
            print('  !! hoja %d  el texto NO es el mismo (%d letras en la '
                  'panoramica, %d en carta)' % (hoja, len(ta), len(tb)))
            print('     desde la letra %d:  panoramica ...%s' % (i, ta[i:i + 46]))
            print('                         carta      ...%s' % tb[i:i + 46])
            fallos += 1

        ca, cb = cuerpos(a.get(hoja, [])), cuerpos(b.get(hoja, []))
        for clave in sorted(set(ca) | set(cb)):
            if ca[clave] != cb[clave]:
                print('  !! hoja %d  %.2f pt %s: %d letras en la panoramica, '
                      '%d en carta' % (hoja, clave[0], clave[1],
                                       ca[clave], cb[clave]))
                fallos += 1

    # ---- geometria: nada fuera de sitio ----------------------------------
    for hoja, txt, cuerpo, fnt, (x0, y0, x1, y1) in todo_carta:
        en_pie = y0 > ENC + DISENO
        if not en_pie and y0 < ENC - HOLGURA:
            print('  !! hoja %d  texto metido en el encabezado: %r (y=%.0f)'
                  % (hoja, txt[:44], y0))
            fallos += 1
        if not en_pie and y1 > ENC + DISENO + HOLGURA:
            print('  !! hoja %d  texto que se sale de la maqueta: %r (y=%.0f)'
                  % (hoja, txt[:44], y1))
            fallos += 1
        if x0 < LADO_MIN - HOLGURA or x1 > ANCHO - LADO_MIN + HOLGURA:
            print('  !! hoja %d  texto pegado al canto: %r (x=%.0f..%.0f)'
                  % (hoja, txt[:44], x0, x1))
            fallos += 1

    print()
    if fallos:
        print('%d avisos' % fallos)
    else:
        print('Todo cuadra: las %d hojas llevan las mismas letras, con el mismo' % n_carta)
        print('cuerpo y la misma familia, y ninguna se sale de su sitio.')
    return 1 if fallos else 0


if __name__ == '__main__':
    sys.exit(main())
