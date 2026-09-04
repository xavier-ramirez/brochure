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
import io, json, os, shutil, sys, threading, webbrowser
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs
from PIL import Image, ImageOps

import exportar_pdf
import exportar_pptx

# Aqui se piden los archivos que baja la barra del editor. Cada ruta dice
# quien la atiende, con que argumentos y como se llama el archivo que sale;
# asi el manejador sigue siendo uno solo para las tres. El PDF de carta es
# el mismo exportador con carta=True: no hay un segundo modulo que mantener.
EXPORTADORES = {
    '/api/pdf':       (exportar_pdf,  {},              exportar_pdf.NOMBRE),
    '/api/pdf-carta': (exportar_pdf,  {'carta': True}, exportar_pdf.NOMBRE_CARTA),
    '/api/pptx':      (exportar_pptx, {},              exportar_pptx.NOMBRE),
}

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
        camino = self.path.split('?')[0].lower()
        for _, _, nombre in EXPORTADORES.values():
            # por nombre exacto, no por extension: hay dos archivos .pdf
            if camino.endswith('/' + nombre.lower()):
                self.send_header('Content-Disposition',
                                 'attachment; filename="%s"' % nombre)
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
        if ruta.path not in EXPORTADORES and not cuerpo:
            return self.responder(400, {'ok': False, 'error': 'No llego nada'})

        if ruta.path == '/api/encuadre':
            try:
                # El navegador solo manda las fotos que tocaste en ESTA sesion.
                # Hay que FUSIONAR con lo ya guardado; si se reemplazara, cada
                # visita borraria los encuadres de las anteriores.
                nuevos = json.loads(cuerpo.decode('utf-8'))
                datos = {}
                if os.path.exists(ENCUADRE_JSON):
                    try:
                        datos = json.load(io.open(ENCUADRE_JSON, encoding='utf-8'))
                    except ValueError:
                        datos = {}
                datos.update(nuevos)
                io.open(ENCUADRE_JSON, 'w', encoding='utf-8').write(
                    json.dumps(datos, indent=1, ensure_ascii=False, sort_keys=True))
                escribir_css(datos)
                return self.responder(200, {'ok': True, 'guardados': len(datos)})
            except Exception as err:
                return self.responder(500, {'ok': False, 'error': str(err)})

        trabajo = EXPORTADORES.get(ruta.path)
        if trabajo:
            modulo, argumentos, nombre = trabajo
            try:
                _, megas = modulo.generar(**argumentos)
                return self.responder(200, {'ok': True, 'archivo': nombre,
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
                # las fotos de telefono traen la orientacion en el EXIF; si no se
                # aplica antes de guardar, el JPEG sale girado
                im = ImageOps.exif_transpose(im).convert('RGB')
                guardar_anterior(destino, nombre)
                w = ancho_para(nombre)
                if im.width > w:
                    im = im.resize((w, round(im.height * w / im.width)), Image.LANCZOS)
                im.save(destino, 'JPEG', quality=88, optimize=True, progressive=True)
                return self.responder(200, {'ok': True, 'ancho': im.width, 'alto': im.height})
            except Exception as err:
                return self.responder(500, {'ok': False, 'error': 'No es una imagen valida (%s)' % err})

        return self.responder(404, {'ok': False, 'error': 'Ruta desconocida'})


def sin_freno():
    """Quita el freno de energia de Windows a este proceso.

    Windows ralentiza a proposito los programas que no estan en primer plano,
    y este servidor vive minimizado. Como los Chrome que lanza el exportador
    heredan ese freno, el PowerPoint tardaba el triple pedido desde el boton de
    la pagina que escribiendo  python exportar_pptx.py  en una consola.
    Si la llamada no existe (Windows viejo, o no es Windows), no pasa nada.
    """
    if os.name != 'nt':
        return
    import ctypes
    from ctypes import wintypes

    class Energia(ctypes.Structure):
        _fields_ = [('Version', wintypes.ULONG),
                    ('ControlMask', wintypes.ULONG),
                    ('StateMask', wintypes.ULONG)]

    # ControlMask = EXECUTION_SPEED, StateMask = 0 -> "no me frenes"
    estado = Energia(1, 1, 0)
    try:
        k = ctypes.windll.kernel32
        k.SetProcessInformation(k.GetCurrentProcess(), 4,
                                ctypes.byref(estado), ctypes.sizeof(estado))
    except (AttributeError, OSError):
        pass


def main():
    sin_freno()
    if not os.path.exists(ENCUADRE_CSS):
        escribir_css({})
    servidor = ThreadingHTTPServer(('127.0.0.1', PUERTO), Manejador)
    url = 'http://localhost:%d/index.html' % PUERTO
    print('Brochure en:  ' + url)
    print('Ctrl+C para parar.')
    # con --sin-navegador no abre pestana: lo usa mantener_servidor.bat, que
    # relanza el servidor si se cae y llenaria el navegador de pestanas
    if '--sin-navegador' not in sys.argv:
        threading.Timer(1.0, lambda: webbrowser.open(url)).start()
    try:
        servidor.serve_forever()
    except KeyboardInterrupt:
        print('\nservidor detenido')
        servidor.server_close()


if __name__ == '__main__':
    main()
