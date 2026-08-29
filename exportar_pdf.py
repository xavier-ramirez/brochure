# -*- coding: utf-8 -*-
"""Exporta index.html a PDF panoramico 16:9 (13,333 x 7,5 pulgadas, igual que
una diapositiva de PowerPoint), una lamina por pagina.

    python exportar_pdf.py

El boton "Descargar PDF" de la barra del editor llama a este mismo codigo.
"""
import os, subprocess, sys

BASE = os.path.dirname(os.path.abspath(__file__))
D = BASE.replace(chr(92), '/')
NOMBRE = 'Brochure_Vidalsa27.pdf'
SALIDA = os.path.join(BASE, NOMBRE)

CANDIDATOS = [
    os.path.join('C:' + chr(92) + 'Program Files', 'Google', 'Chrome', 'Application', 'chrome.exe'),
    os.path.join('C:' + chr(92) + 'Program Files (x86)', 'Google', 'Chrome', 'Application', 'chrome.exe'),
    os.path.join('C:' + chr(92) + 'Program Files', 'Microsoft', 'Edge', 'Application', 'msedge.exe'),
    os.path.join('C:' + chr(92) + 'Program Files (x86)', 'Microsoft', 'Edge', 'Application', 'msedge.exe'),
]


def navegador():
    return next((c for c in CANDIDATOS if os.path.exists(c)), None)


def generar():
    """Genera el PDF. Devuelve (ruta, megas) o lanza RuntimeError."""
    nav = navegador()
    if not nav:
        raise RuntimeError('No se encontro Chrome ni Edge. Exporta con Ctrl+P desde la pagina.')
    if os.path.exists(SALIDA):
        try:
            os.remove(SALIDA)
        except PermissionError:
            raise RuntimeError('El PDF esta abierto en otro programa. Cierralo y vuelve a intentar.')
    subprocess.run([
        nav, '--headless=new', '--disable-gpu',
        '--virtual-time-budget=25000',
        '--no-pdf-header-footer',
        '--print-to-pdf-no-header',
        '--print-to-pdf=' + SALIDA.replace(chr(92), '/'),
        'file:///' + D + '/index.html',
    ], capture_output=True, timeout=300)
    if not os.path.exists(SALIDA):
        raise RuntimeError('No se genero el PDF. Prueba con Ctrl+P -> Guardar como PDF, '
                           'margenes "Ninguno" y "Graficos de fondo" activado.')
    return SALIDA, os.path.getsize(SALIDA) / 1024 / 1024


if __name__ == '__main__':
    try:
        ruta, megas = generar()
    except RuntimeError as err:
        sys.exit(str(err))
    print('PDF listo: %s  (%.1f MB)' % (ruta, megas))
