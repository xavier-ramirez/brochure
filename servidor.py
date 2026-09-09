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
import exportar_html

# Aqui se piden los archivos que baja la barra del editor. Cada ruta dice
# quien la atiende, con que argumentos y como se llama el archivo que sale;
# asi el manejador sigue siendo uno solo para las cuatro. Las versiones de
# carta son el mismo exportador con carta=True -tanto el PDF como el
# PowerPoint-: no hay un segundo modulo que mantener.
EXPORTADORES = {
    '/api/pdf':        (exportar_pdf,  {},              exportar_pdf.NOMBRE),
    '/api/pdf-carta':  (exportar_pdf,  {'carta': True}, exportar_pdf.NOMBRE_CARTA),
    '/api/pptx':       (exportar_pptx, {},              exportar_pptx.NOMBRE),
    '/api/pptx-carta': (exportar_pptx, {'carta': True}, exportar_pptx.NOMBRE_CARTA),
    # La presentacion en un solo archivo: no tiene version de carta -las hojas
    # impresas no tienen modo presentacion- asi que va sola.
    '/api/html':       (exportar_html, {},              exportar_html.NOMBRE),
}

BASE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(BASE, 'img')
ANTERIORES = os.path.join(IMG, '_anteriores')
# El encuadre de las fotos se guarda por HOJA. La panoramica y la carta
# comparten uno -son la misma maqueta, y el usuario quiere encuadrar una vez
# para las dos-; la hoja de pie tiene el SUYO, porque alli los marcos son de
# otra forma y el trozo que se ve no puede ser el mismo.
# vertical.html carga los dos ficheros, el comun primero: una foto que no se
# haya tocado en la vertical sigue saliendo con el encuadre de la panoramica, y
# en cuanto se mueve alli se queda con el suyo sin tocar el de la otra.
ENCUADRES = {
    '':         (os.path.join(BASE, 'encuadre.json'),
                 os.path.join(BASE, 'encuadre.css')),
    'vertical': (os.path.join(BASE, 'encuadre_vertical.json'),
                 os.path.join(BASE, 'encuadre_vertical.css')),
}
PUERTO = 8787
MAX_BYTES = 40 * 1024 * 1024

# Ancho al que se guarda cada foto segun donde va. Es el DOBLE de lo mas ancho que
# esa foto llega a pintarse -medido en las dos maquetas, contando el zoom del
# encuadre-, y ese doble no es un margen de seguridad cualquiera:
#
#   · En pantalla: Windows suele estar al 125 o 150 %, asi que el navegador pinta mas
#     puntos de los que dice el CSS. Una foto guardada justo a su medida se ve blanda
#     ahi, que es exactamente lo que se noto el 2026-09-07 con empresa_sede.
#   · En papel: la lamina es de 96 dpi, asi que al doble la foto imprime a 192 dpi.
#     No es calidad de imprenta -harian falta 3,125x, o sea 4000 px en las grandes-,
#     pero cuadruplicar el peso de las fotos por eso dejaria un PDF que no se puede
#     enviar por correo (hoy pesa 13,6 MB con 14 MB de fotos).
#
# Los valores de antes eran MENORES que lo pintado en dos huecos: las miniaturas se
# guardaban a 700 px y la ficha que va sola las pinta a 983, o sea que el navegador
# tenia que INVENTAR pixeles. Por eso se veian borrosas dentro del brochure y nitidas
# al abrirlas por fuera.
#
# Si algun dia se cambia el tamano de una foto en el CSS, hay que volver a medir esto,
# y medir las TRES maquetas: vertical.html, index.html y carta.html. Cada hueco se
# guarda una sola vez en img/, asi que el ancho tiene que servir para la que mas grande
# la pinte de las tres.
ANCHOS = [
    ('_1', 2600),                    # foto grande de proyecto (pinta hasta 1280)
    ('_2', 2000), ('_3', 2000),      # miniaturas (pintan hasta 983 en la ficha que va sola)
    ('servicio_', 900),              # pintan hasta 431
    ('portada_', 2600),
    ('flota_equipo', 2600),
    ('portafolio_', 2600),
    ('clientes_', 2600),
]

# Las fotos de sede y de oficina -empresa_sede, empresa_tendido, oficina_*- NO tienen
# regla propia y caen aqui. Pintan hasta 1144 px -el maximo esta en carta.html-, asi que
# su doble son 2288 y se redondea a 2400 para dejar margen.
# El 2200 que hubo aqui salia de medir solo la vertical y la panoramica: al medir tambien
# la de carta el maximo subio, y por eso hay que mirar LAS TRES cada vez que se toque una
# medida del CSS.
ANCHO_POR_DEFECTO = 2400


def ancho_para(nombre):
    for pista, w in ANCHOS:
        if nombre.startswith(pista) or nombre.endswith(pista):
            return w
    return ANCHO_POR_DEFECTO


def que_llego(cuerpo):
    """Que es lo que se ha subido, cuando NO es una imagen que Pillow sepa leer.

    Devuelve una frase para el aviso, o None si el archivo no se reconoce como
    ninguno de los sospechosos habituales.

    Se mira la FIRMA de los primeros bytes, no la extension: el nombre puede
    mentir y aqui, ademas, el servidor no lo recibe.

    El caso que se dio de verdad -2026-09-08, montando una foto de proyecto- fue
    un .MOV: las Live Photos del iPhone se descargan como un .MOV al lado del
    .jpeg y con el MISMO nombre, asi que en el dialogo de Windows aparecen los
    dos seguidos y es facil pinchar el que no es. El error de Pillow que salia
    -"cannot identify image file <_io.BytesIO object at 0x...>"- no decia nada
    de eso; de ahi esta funcion.
    """
    cab = cuerpo[:16]
    if cab[4:8] == b'ftyp':
        # Contenedor ISO-BMFF: por la marca de dentro se sabe si es foto o video.
        marca = bytes(cab[8:12])
        if marca in (b'heic', b'heix', b'heim', b'heis', b'hevc', b'mif1', b'msf1'):
            return 'una foto HEIC del iPhone: pasala a JPG y subela'
        return 'un video: sube el .jpeg, no el .MOV de la Live Photo'
    if cab[:4] == b'%PDF':
        return 'un PDF'
    if cab[:2] == b'PK':
        return 'un ZIP (o un .docx / .xlsx / .pptx)'
    return None


def guardar_anterior(ruta, nombre):
    """Antes de pisar una foto, deja una copia en img/_anteriores/.
    Asi nunca se pierde nada, ni por un cambio mio ni por una equivocacion."""
    if not os.path.exists(ruta):
        return
    os.makedirs(ANTERIORES, exist_ok=True)
    sello = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    shutil.copy2(ruta, os.path.join(ANTERIORES, '%s_%s.jpg' % (nombre, sello)))


def escribir_css(datos, destino, hoja=''):
    rotulo = ('/* Encuadre de las fotos%s. Lo escribe el editor; no hace falta '
              'tocarlo. */' % (' en la HOJA DE PIE' if hoja else ''))
    lineas = [rotulo]
    for nombre in sorted(datos):
        e = datos[nombre]
        x, y = float(e.get('x', 50)), float(e.get('y', 50))
        lineas.append(
            'img[data-foto="%s"]{object-position:%.1f%% %.1f%%;'
            '--org:%.1f%% %.1f%%;--zoom:%.3f}'
            % (nombre, x, y, x, y, float(e.get('zoom', 1))))
    io.open(destino, 'w', encoding='utf-8').write('\n'.join(lineas) + '\n')


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
            return self.responder(400, {'ok': False, 'error':
                'Archivo demasiado grande: %s MB, y el tope son %s'
                % (largo // (1024 * 1024), MAX_BYTES // (1024 * 1024))})
        cuerpo = self.rfile.read(largo) if largo else b''
        if ruta.path not in EXPORTADORES and not cuerpo:
            return self.responder(400, {'ok': False, 'error': 'No llego nada'})

        if ruta.path == '/api/encuadre':
            try:
                # ?hoja=vertical -> el encuadre propio de la hoja de pie. Sin el
                # parametro, el comun de la panoramica y la carta. Un valor que
                # no conozcamos cae en el comun, que es el de siempre.
                hoja = (parse_qs(ruta.query).get('hoja') or [''])[0]
                if hoja not in ENCUADRES:
                    hoja = ''
                destino_json, destino_css = ENCUADRES[hoja]
                # El navegador solo manda las fotos que tocaste en ESTA sesion.
                # Hay que FUSIONAR con lo ya guardado; si se reemplazara, cada
                # visita borraria los encuadres de las anteriores.
                nuevos = json.loads(cuerpo.decode('utf-8'))
                datos = {}
                if os.path.exists(destino_json):
                    try:
                        datos = json.load(io.open(destino_json, encoding='utf-8'))
                    except ValueError:
                        datos = {}
                datos.update(nuevos)
                io.open(destino_json, 'w', encoding='utf-8').write(
                    json.dumps(datos, indent=1, ensure_ascii=False, sort_keys=True))
                escribir_css(datos, destino_css, hoja)
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
            # Lo que llega NO se abre a ciegas: primero se mira si es uno de los
            # archivos que se cuelan por el dialogo de "elegir foto". Asi el aviso
            # dice que paso -"es un video"- en vez del volcado de Pillow, que no
            # se entiende. El navegador hace este mismo filtro antes de subir
            # (ver editor.js); esto es la red de abajo, por si se sube de otra
            # forma -curl, o un navegador que no mande el tipo-.
            aviso = que_llego(cuerpo)
            if aviso:
                return self.responder(400, {'ok': False, 'error': 'Eso es ' + aviso})
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
            except Exception:
                # 400 y no 500: el archivo es el que esta mal, no el servidor.
                # El tamano va en el aviso porque distingue dos averias que se
                # parecen: un archivo que llego entero pero no es una imagen, y
                # uno que llego a medias. En KB solo si los hay; si no, sale
                # "0 KB", que se lee como si no hubiera llegado nada.
                peso = ('%s KB' % (len(cuerpo) // 1024) if len(cuerpo) >= 1024
                        else '%s bytes' % len(cuerpo))
                return self.responder(400, {'ok': False, 'error':
                    'No se pudo leer como imagen (%s). Prueba con un JPG o un PNG'
                    % peso})

        if ruta.path == '/api/borrar-foto':
            # Vacia el marco: la foto sale de img/ y el hueco se queda con su
            # fondo gris. No es un borrado a lo bruto -guardar_anterior() deja
            # antes una copia con fecha en img/_anteriores/, la misma red que
            # protege al cambio de foto-, asi que siempre se puede recuperar.
            #
            # El ENCUADRE de esa foto NO se toca. Es a proposito: casi siempre
            # se borra para poner otra en el mismo sitio, y al subirla vuelve
            # encuadrada como estaba. Una regla suelta en encuadre.css que no
            # apunte a ninguna foto no molesta a nadie.
            nombre = (parse_qs(ruta.query).get('nombre') or [''])[0]
            if not nombre or not all(c.isalnum() or c in '_-' for c in nombre):
                return self.responder(400, {'ok': False, 'error': 'Nombre de foto invalido'})
            destino = os.path.join(IMG, nombre + '.jpg')
            if not os.path.exists(destino):
                return self.responder(404, {'ok': False, 'error': 'Esa foto ya no esta en img/'})
            try:
                guardar_anterior(destino, nombre)
                os.remove(destino)
                return self.responder(200, {'ok': True, 'copia': os.path.basename(ANTERIORES)})
            except Exception as err:
                return self.responder(500, {'ok': False, 'error': str(err)})

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
    for hoja, (_, destino_css) in ENCUADRES.items():
        if not os.path.exists(destino_css):
            escribir_css({}, destino_css, hoja)
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
