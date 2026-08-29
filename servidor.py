# -*- coding: utf-8 -*-
"""Servidor local para ver y editar el brochure.

    python servidor.py     ->    http://localhost:8787

Con la pagina abierta ahi:
  doble clic sobre una foto -> elegir otra imagen del PC
  arrastrar sobre la foto   -> mover el encuadre
  rueda del raton           -> acercar / alejar

Todo se guarda solo: las fotos en img/ y el encuadre en encuadre.css,
asi que "python exportar_pdf.py" saca el PDF igual a lo que ves.
"""
import datetime
import io, json, os, shutil, threading, webbrowser
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs
from PIL import Image

import exportar_pdf

BASE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(BASE, 'img')
ANTERIORES = os.path.join(IMG, '_anteriores')
ENCUADRE_JSON = os.path.join(BASE, 'encuadre.json')
ENCUADRE_CSS = os.path.join(BASE, 'encuadre.css')
PUERTO = 8787
MAX_BYTES = 40 * 1024 * 1024

# ancho al que se guarda cada foto segun donde va
ANCHOS = [
    ('_1', 1300),                    # foto grande de proyecto
    ('_2', 700), ('_3', 700),        # miniaturas
    ('servicio_', 700),
    ('portada_', 1300),
    ('flota_equipo', 2000),
    ('portafolio_', 2000),
    ('clientes_', 1500),
]


def ancho_para(nombre):
    for pista, w in ANCHOS:
        if nombre.startswith(pista) or nombre.endswith(pista):
            return w
    return 1300


def guardar_anterior(ruta, nombre):
    """Antes de pisar una foto, deja una copia en img/_anteriores/.
    Asi nunca se pierde nada, ni por un cambio mio ni por una equivocacion."""
    if not os.path.exists(ruta):
        return
    os.makedirs(ANTERIORES, exist_ok=True)
    sello = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    shutil.copy2(ruta, os.path.join(ANTERIORES, '%s_%s.jpg' % (nombre, sello)))


def escribir_css(datos):
    lineas = ['/* Encuadre de las fotos. Lo escribe el editor; no hace falta tocarlo. */']
    for nombre in sorted(datos):
        e = datos[nombre]
        x, y = float(e.get('x', 50)), float(e.get('y', 50))
        lineas.append(
            'img[data-foto="%s"]{object-position:%.1f%% %.1f%%;'
            '--org:%.1f%% %.1f%%;--zoom:%.3f}'
            % (nombre, x, y, x, y, float(e.get('zoom', 1))))
    io.open(ENCUADRE_CSS, 'w', encoding='utf-8').write('\n'.join(lineas) + '\n')


class Manejador(SimpleHTTPRequestHandler):
    def __init__(self, *a, **kw):
        super().__init__(*a, directory=BASE, **kw)

    def log_message(self, *a):
        pass                                   # sin ruido en la consola

    def end_headers(self):
        self.send_header('Cache-Control', 'no-store')
        if self.path.split('?')[0].lower().endswith('.pdf'):
            self.send_header('Content-Disposition',
                             'attachment; filename="%s"' % exportar_pdf.NOMBRE)
        super().end_headers()

    def responder(self, codigo, obj):
        cuerpo = json.dumps(obj).encode('utf-8')
        self.send_response(codigo)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(cuerpo)))
        self.end_headers()
        self.wfile.write(cuerpo)

    def do_POST(self):
        ruta = urlparse(self.path)
        largo = int(self.headers.get('Content-Length') or 0)
        if largo > MAX_BYTES:
            return self.responder(400, {'ok': False, 'error': 'Archivo demasiado grande'})
        cuerpo = self.rfile.read(largo) if largo else b''
        if ruta.path != '/api/pdf' and not cuerpo:
            return self.responder(400, {'ok': False, 'error': 'No llego nada'})

        if ruta.path == '/api/encuadre':
            try:
                datos = json.loads(cuerpo.decode('utf-8'))
                io.open(ENCUADRE_JSON, 'w', encoding='utf-8').write(
                    json.dumps(datos, indent=1, ensure_ascii=False))
                escribir_css(datos)
                return self.responder(200, {'ok': True})
            except Exception as err:
                return self.responder(500, {'ok': False, 'error': str(err)})

        if ruta.path == '/api/pdf':
            try:
                _, megas = exportar_pdf.generar()
                return self.responder(200, {'ok': True, 'archivo': exportar_pdf.NOMBRE,
                                            'megas': round(megas, 1)})
            except Exception as err:
                return self.responder(500, {'ok': False, 'error': str(err)})

        if ruta.path == '/api/foto':
            nombre = (parse_qs(ruta.query).get('nombre') or [''])[0]
            if not nombre or not all(c.isalnum() or c in '_-' for c in nombre):
                return self.responder(400, {'ok': False, 'error': 'Nombre de foto invalido'})
            destino = os.path.join(IMG, nombre + '.jpg')
            if not os.path.exists(destino):
                return self.responder(404, {'ok': False, 'error': 'Esa foto no existe en img/'})
            try:
                im = Image.open(io.BytesIO(cuerpo))
                im = im.convert('RGB')
                guardar_anterior(destino, nombre)
                w = ancho_para(nombre)
                if im.width > w:
                    im = im.resize((w, round(im.height * w / im.width)), Image.LANCZOS)
                im.save(destino, 'JPEG', quality=88, optimize=True, progressive=True)
                return self.responder(200, {'ok': True, 'ancho': im.width, 'alto': im.height})
            except Exception as err:
                return self.responder(500, {'ok': False, 'error': 'No es una imagen valida (%s)' % err})

        return self.responder(404, {'ok': False, 'error': 'Ruta desconocida'})


def main():
    if not os.path.exists(ENCUADRE_CSS):
        escribir_css({})
    servidor = ThreadingHTTPServer(('127.0.0.1', PUERTO), Manejador)
    url = 'http://localhost:%d/index.html' % PUERTO
    print('Brochure en:  ' + url)
    print('Ctrl+C para parar.')
    threading.Timer(1.0, lambda: webbrowser.open(url)).start()
    try:
        servidor.serve_forever()
    except KeyboardInterrupt:
        print('\nservidor detenido')
        servidor.server_close()


if __name__ == '__main__':
    main()
