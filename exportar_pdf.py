# -*- coding: utf-8 -*-
"""Exporta el brochure a PDF, una lamina por pagina.

    python exportar_pdf.py          -> Brochure_Vidalsa27.pdf
                                       panoramico 16:9, 13,333 x 7,5 pulgadas,
                                       igual que una diapositiva de PowerPoint

    python exportar_pdf.py carta    -> Brochure_Vidalsa27_Carta.pdf
                                       hoja carta apaisada, 11 x 8,5 pulgadas,
                                       con encabezado y pie de pagina

Las dos salen de las mismas laminas y con la misma letra, del mismo tamano en
milimetros: la de carta solo lee carta.html en vez de index.html, y quien la
coloca en el folio es carta.css. No se encoge ni se recompone nada.

El boton "Descargar PDF" de la barra del editor llama al panoramico.
"""
import os, subprocess, sys

BASE = os.path.dirname(os.path.abspath(__file__))
D = BASE.replace(chr(92), '/')
NOMBRE = 'Brochure_Vidalsa27.pdf'
SALIDA = os.path.join(BASE, NOMBRE)

# la variante de carta: misma maquinaria, otra pagina de entrada y otro nombre
NOMBRE_CARTA = 'Brochure_Vidalsa27_Carta.pdf'

# en Windows, Chrome abriria un parpadeo de consola negra al lanzarlo desde
# aqui; con esta bandera no se crea ninguna ventana
SIN_VENTANA = {'creationflags': subprocess.CREATE_NO_WINDOW} if os.name == 'nt' else {}

CANDIDATOS = [
    os.path.join('C:' + chr(92) + 'Program Files', 'Google', 'Chrome', 'Application', 'chrome.exe'),
    os.path.join('C:' + chr(92) + 'Program Files (x86)', 'Google', 'Chrome', 'Application', 'chrome.exe'),
    os.path.join('C:' + chr(92) + 'Program Files', 'Microsoft', 'Edge', 'Application', 'msedge.exe'),
    os.path.join('C:' + chr(92) + 'Program Files (x86)', 'Microsoft', 'Edge', 'Application', 'msedge.exe'),
]


def navegador():
    return next((c for c in CANDIDATOS if os.path.exists(c)), None)


def generar(carta=False):
    """Genera el PDF. Devuelve (ruta, megas) o lanza RuntimeError.
    Con carta=True saca la version de hoja carta a partir de carta.html."""
    pagina = 'carta.html' if carta else 'index.html'
    salida = os.path.join(BASE, NOMBRE_CARTA) if carta else SALIDA
    nav = navegador()
    if not nav:
        raise RuntimeError('No se encontro Chrome ni Edge. Exporta con Ctrl+P desde la pagina.')
    if not os.path.exists(os.path.join(BASE, pagina)):
        raise RuntimeError('Falta %s. Ejecuta antes: python generar.py' % pagina)
    if os.path.exists(salida):
        try:
            os.remove(salida)
        except PermissionError:
            raise RuntimeError('El PDF esta abierto en otro programa. Cierralo y vuelve a intentar.')
    subprocess.run([
        nav, '--headless=new', '--disable-gpu',
        '--virtual-time-budget=25000',
        '--no-pdf-header-footer',
        '--print-to-pdf-no-header',
        '--print-to-pdf=' + salida.replace(chr(92), '/'),
        'file:///' + D + '/' + pagina,
    ], capture_output=True, timeout=300, **SIN_VENTANA)
    if not os.path.exists(salida):
        raise RuntimeError('No se genero el PDF. Prueba con Ctrl+P -> Guardar como PDF, '
                           'margenes "Ninguno" y "Graficos de fondo" activado.')
    return salida, os.path.getsize(salida) / 1024 / 1024


if __name__ == '__main__':
    # Sin argumentos salen LOS DOS. Antes salia solo el panoramico y era muy
    # facil olvidar el segundo: el otro PDF se quedaba viejo sin avisar, y
    # revisar_carta.py -que compara los dos- daba por bueno lo que en realidad
    # comparaba contra un archivo caducado. Con un solo comando no se descuadran.
    pedido = [a.lower() for a in sys.argv[1:]]
    if 'carta' in pedido:
        cuales = [True]
    elif 'panoramico' in pedido or 'pano' in pedido:
        cuales = [False]
    else:
        cuales = [False, True]
    for es_carta in cuales:
        try:
            ruta, megas = generar(es_carta)
        except RuntimeError as err:
            sys.exit(str(err))
        print('PDF listo: %s  (%.1f MB)' % (ruta, megas))
